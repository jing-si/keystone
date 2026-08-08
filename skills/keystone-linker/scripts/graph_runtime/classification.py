"""Strict source-bound classification for graph synchronization deltas."""

import hashlib
import json
import os
import shlex
import stat
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .adapters import adapter_for_path
from .companion import load_authoritative_json
from .index_model import ScanScope
from .scanner import ReferenceScanner
from .snapshot_validation import reconstruct
from .source_unit import COMPANION_SUFFIX
from .validation_support import canonical_relative_path
from .yaml_subset import MetadataError, parse_yaml_subset


Diagnostic = Dict[str, Any]
DIGEST_PREFIX = "sha256:"
ABSENT = "absent"
INPUT_FIELDS = {
    "schema_version",
    "delta_set_digest",
    "deltas",
    "source_context",
}
SOURCE_CONTEXT_FIELDS = {
    "repository_root_digest",
    "coverage",
    "sources",
}
COVERAGE_FIELDS = {
    "mode",
    "complete",
    "source_count",
    "source_path_digest",
}
DELTA_FIELDS = {
    "kind",
    "source_surface",
    "change_kind",
    "changed_locators",
    "semantic_summary",
    "baseline_digest",
    "resulting_digest",
    "graph_relevant",
}
LOCATOR_FIELDS = {
    "path",
    "heading",
    "symbol",
    "test_name",
    "config_key",
    "schema_name",
}
CHANGE_KINDS = {"added", "modified", "deleted", "type_replaced"}
DELTA_KINDS = {"artifact_delta", "document_delta"}


class ClassificationInputError(ValueError):
    """Raised when authority-bearing classification input is not canonical."""


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize a JSON value using the package canonical byte representation."""

    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return DIGEST_PREFIX + hashlib.sha256(value).hexdigest()


def digest_json(value: Any) -> str:
    return digest_bytes(canonical_json_bytes(value))


def repository_root_digest(root: Path) -> str:
    return digest_json(str(root.resolve()))


def source_coverage_context(root: Path, sources: Sequence[str]) -> Dict[str, Any]:
    """Build the strict delta-source coverage projection for a repository root."""

    canonical = sorted({_canonical_path(item, "source_context.sources") for item in sources})
    return {
        "repository_root_digest": repository_root_digest(root),
        "coverage": {
            "mode": "delta_set",
            "complete": True,
            "source_count": len(canonical),
            "source_path_digest": digest_json(canonical),
        },
        "sources": canonical,
    }


def classification_input(root: Path, deltas: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Build canonical classification input from the complete ordered delta set."""

    projected = [dict(item) for item in deltas]
    sources = [str(item.get("source_surface", "")) for item in projected]
    return {
        "schema_version": 1,
        "delta_set_digest": digest_json(projected),
        "deltas": projected,
        "source_context": source_coverage_context(root, sources),
    }


def diagnostic(code: str, message: str, path: str) -> Diagnostic:
    return {
        "code": code,
        "message": message,
        "severity": "error",
        "path": path,
    }


def result_envelope(
    *,
    status: str,
    disposition: str,
    delta_set_digest: str,
    source_generation_digest: str,
    inspected_sources: Sequence[Mapping[str, Any]],
    exclusion_evidence: Sequence[Mapping[str, Any]],
    reason_codes: Sequence[str],
    diagnostics: Sequence[Diagnostic],
) -> Dict[str, Any]:
    serialized = [dict(item) for item in diagnostics]
    errors = sum(item.get("severity") == "error" for item in serialized)
    warnings = sum(item.get("severity") == "warning" for item in serialized)
    return {
        "schema_version": 1,
        "status": status,
        "disposition": disposition,
        "delta_set_digest": delta_set_digest,
        "source_generation_digest": source_generation_digest,
        "inspected_sources": [dict(item) for item in inspected_sources],
        "exclusion_evidence": [dict(item) for item in exclusion_evidence],
        "reason_codes": list(reason_codes),
        "diagnostics": serialized,
        "summary": {"errors": errors, "warnings": warnings},
    }


def error_envelope(code: str, message: str, path: str) -> Dict[str, Any]:
    item = diagnostic(code, message, path)
    return result_envelope(
        status="error",
        disposition="deferred",
        delta_set_digest=ABSENT,
        source_generation_digest=ABSENT,
        inspected_sources=[],
        exclusion_evidence=[],
        reason_codes=[code],
        diagnostics=[item],
    )


def classify(root: Path, manifest: Any) -> Dict[str, Any]:
    """Validate and classify one complete source-bound delta set."""

    deltas, sources, delta_digest, complete = parse_input(root, manifest)
    inspected, source_bytes, diagnostics = inspect_sources(root, sources)
    diagnostics.extend(_validate_current_generation(deltas, inspected))
    graph_generation_digest, graph_reasons, graph_diagnostics = (
        _repository_graph_relevance(root, sources)
    )
    diagnostics.extend(graph_diagnostics)
    if not complete:
        diagnostics.append(diagnostic(
            "source_coverage_incomplete",
            "Authoritative graph classification requires complete delta-source coverage.",
            "source_context.coverage.complete",
        ))
    generation_digest = digest_json({
        "delta_sources": inspected,
        "repository_graph_generation_digest": graph_generation_digest,
    })
    if diagnostics:
        reason_codes = sorted({item["code"] for item in diagnostics})
        return result_envelope(
            status="fail",
            disposition="deferred",
            delta_set_digest=delta_digest,
            source_generation_digest=generation_digest,
            inspected_sources=inspected,
            exclusion_evidence=[],
            reason_codes=reason_codes,
            diagnostics=diagnostics,
        )
    reason_codes = sorted(set(
        _derive_relevance(deltas, inspected, source_bytes) + graph_reasons
    ))
    disposition = "required" if reason_codes else "not_applicable"
    exclusion_evidence = []
    if not reason_codes:
        if deltas:
            reason_codes = ["added_plain_unowned_source"]
            exclusion_evidence = _not_applicable_exclusion_evidence(
                deltas, inspected,
            )
        else:
            reason_codes = ["empty_delta_set"]
    return result_envelope(
        status="pass",
        disposition=disposition,
        delta_set_digest=delta_digest,
        source_generation_digest=generation_digest,
        inspected_sources=inspected,
        exclusion_evidence=exclusion_evidence,
        reason_codes=reason_codes,
        diagnostics=[],
    )


def _not_applicable_exclusion_evidence(
    deltas: Sequence[Mapping[str, Any]],
    inspected: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Map every excluded locator to the exact source observations used."""

    inspected_indexes: Dict[str, int] = {
        str(item["path"]): index
        for index, item in enumerate(inspected)
    }
    evidence: List[Dict[str, Any]] = []
    for delta_index, delta in enumerate(deltas):
        source = str(delta["source_surface"])
        source_indexes = sorted({
            inspected_indexes[path]
            for path in (source, source + COMPANION_SUFFIX)
            if path in inspected_indexes
        })
        for locator_index, locator in enumerate(delta["changed_locators"]):
            evidence.append({
                "delta_index": delta_index,
                "locator_index": locator_index,
                "locator": dict(locator),
                "reason_code": "added_plain_unowned_source",
                "inspected_source_indexes": source_indexes,
            })
    return evidence


def parse_input(
    root: Path, manifest: Any
) -> Tuple[List[Mapping[str, Any]], List[str], str, bool]:
    if not isinstance(manifest, Mapping):
        raise ClassificationInputError("classification manifest must be an object")
    _exact_fields(manifest, INPUT_FIELDS, "classification manifest")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ClassificationInputError("schema_version must be the integer 1")
    raw_deltas = manifest.get("deltas")
    if not isinstance(raw_deltas, list):
        raise ClassificationInputError("deltas must be an array")
    deltas = [_validate_delta(item, index) for index, item in enumerate(raw_deltas)]
    if manifest.get("delta_set_digest") != digest_json(deltas):
        raise ClassificationInputError("delta_set_digest does not match the exact ordered deltas")
    if not _digest(manifest.get("delta_set_digest")):
        raise ClassificationInputError("delta_set_digest must be lowercase sha256")

    context = manifest.get("source_context")
    if not isinstance(context, Mapping):
        raise ClassificationInputError("source_context must be an object")
    _exact_fields(context, SOURCE_CONTEXT_FIELDS, "source_context")
    if context.get("repository_root_digest") != repository_root_digest(root):
        raise ClassificationInputError("repository_root_digest does not match --root")
    raw_sources = context.get("sources")
    if not isinstance(raw_sources, list):
        raise ClassificationInputError("source_context.sources must be an array")
    sources = [
        _canonical_path(item, "source_context.sources[%d]" % index)
        for index, item in enumerate(raw_sources)
    ]
    if sources != sorted(set(sources)):
        raise ClassificationInputError(
            "source_context.sources must be unique and lexicographically sorted"
        )
    expected_sources = sorted({str(item["source_surface"]) for item in deltas})
    if sources != expected_sources:
        raise ClassificationInputError(
            "source_coverage_delta_omitted: sources must equal the complete delta surface set"
        )

    coverage = context.get("coverage")
    if not isinstance(coverage, Mapping):
        raise ClassificationInputError("source_context.coverage must be an object")
    _exact_fields(coverage, COVERAGE_FIELDS, "source_context.coverage")
    if coverage.get("mode") != "delta_set":
        raise ClassificationInputError("source_context.coverage.mode must be delta_set")
    if not isinstance(coverage.get("complete"), bool):
        raise ClassificationInputError("source_context.coverage.complete must be boolean")
    if type(coverage.get("source_count")) is not int:
        raise ClassificationInputError("source_context.coverage.source_count must be an integer")
    if coverage.get("source_count") != len(sources):
        raise ClassificationInputError("source_context.coverage.source_count is stale")
    if coverage.get("source_path_digest") != digest_json(sources):
        raise ClassificationInputError("source_context.coverage.source_path_digest is stale")
    return deltas, sources, str(manifest["delta_set_digest"]), coverage["complete"]


def inspect_sources(
    root: Path, sources: Sequence[str]
) -> Tuple[List[Dict[str, Any]], Dict[str, Optional[bytes]], List[Diagnostic]]:
    inspected: List[Dict[str, Any]] = []
    source_bytes: Dict[str, Optional[bytes]] = {}
    diagnostics: List[Diagnostic] = []
    physical_paths = set(sources)
    physical_paths.update(
        source + COMPANION_SUFFIX
        for source in sources
        if not source.endswith(COMPANION_SUFFIX)
    )
    source_set = set(sources)
    for relative in sorted(physical_paths):
        try:
            entry, raw = _inspect_source(root, relative)
        except (OSError, RuntimeError, ValueError) as error:
            inspected.append({"path": relative, "type": "unreadable"})
            source_bytes[relative] = None
            diagnostics.append(diagnostic(
                "source_inspection_failed", str(error), relative,
            ))
            continue
        inspected.append(entry)
        source_bytes[relative] = raw
        if (
            relative in source_set
            and entry["type"] not in {"regular_file", "absent"}
        ) or (
            relative.endswith(COMPANION_SUFFIX)
            and entry["type"] not in {"regular_file", "absent"}
        ):
            diagnostics.append(diagnostic(
                "source_surface_not_regular",
                "Graph classification supports regular-file and absent source surfaces only.",
                relative,
            ))
    return inspected, source_bytes, diagnostics


def _inspect_source(
    root: Path, relative: str,
) -> Tuple[Dict[str, Any], Optional[bytes]]:
    root = root.resolve()
    candidate = root.joinpath(*Path(relative).parts)
    try:
        candidate.parent.resolve().relative_to(root)
    except ValueError as error:
        raise ValueError("source parent escapes repository root") from error
    try:
        before = candidate.lstat()
    except FileNotFoundError:
        return {"path": relative, "type": "absent"}, None
    if stat.S_ISLNK(before.st_mode):
        target = os.readlink(str(candidate))
        after = candidate.lstat()
        if _stat_identity(before) != _stat_identity(after):
            raise RuntimeError("source generation changed during symlink inspection")
        return {
            "path": relative,
            "type": "symlink",
            "symlink_target": target,
        }, None
    if stat.S_ISDIR(before.st_mode):
        after = candidate.lstat()
        if _stat_identity(before) != _stat_identity(after):
            raise RuntimeError("source generation changed during directory inspection")
        return {"path": relative, "type": "directory"}, None
    if not stat.S_ISREG(before.st_mode):
        return {"path": relative, "type": "special"}, None

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(str(candidate), flags)
    try:
        opened_before = os.fstat(descriptor)
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        opened_after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = candidate.lstat()
    identities = {
        _stat_identity(before),
        _stat_identity(opened_before),
        _stat_identity(opened_after),
        _stat_identity(after),
    }
    if len(identities) != 1:
        raise RuntimeError("source generation changed during regular-file inspection")
    raw = b"".join(chunks)
    return {
        "path": relative,
        "type": "regular_file",
        "raw_byte_digest": digest_bytes(raw),
        "executable": bool(after.st_mode & 0o111),
    }, raw


def _derive_relevance(
    deltas: Sequence[Mapping[str, Any]],
    inspected: Sequence[Mapping[str, Any]],
    source_bytes: Mapping[str, Optional[bytes]],
) -> List[str]:
    """Derive conservative relevance without trusting the caller's boolean alone."""

    inspected_by_path = {str(item.get("path")): item for item in inspected}
    reasons = set()
    for delta in deltas:
        path = str(delta["source_surface"])
        if delta["graph_relevant"]:
            reasons.add("graph_relevant_delta")
        if delta["kind"] == "document_delta":
            reasons.add("document_delta_requires_graph_review")
        if delta["change_kind"] in {"modified", "type_replaced"}:
            reasons.add("baseline_graph_state_unavailable")
        if delta["change_kind"] == "deleted":
            reasons.add("deleted_source_requires_graph_review")
        if path.endswith(COMPANION_SUFFIX):
            reasons.add("companion_metadata_changed")
            continue
        companion = inspected_by_path.get(path + COMPANION_SUFFIX, {})
        if companion.get("type") == "regular_file":
            reasons.add("companion_metadata_present")
        source = inspected_by_path.get(path, {})
        raw = source_bytes.get(path)
        if source.get("type") != "regular_file" or raw is None:
            continue
        adapter = adapter_for_path(path)
        if adapter is None:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            reasons.add("source_metadata_indeterminate")
            continue
        try:
            has_metadata = any(adapter.metadata_blocks(text))
        except (TypeError, ValueError):
            reasons.add("source_metadata_indeterminate")
        else:
            if has_metadata:
                reasons.add("declared_graph_metadata_present")
    return sorted(reasons)


def _repository_graph_relevance(
    root: Path, changed_sources: Sequence[str],
) -> Tuple[str, List[str], List[Diagnostic]]:
    """Bind repository graph sources and derive cross-surface locator ownership."""

    reasons = set()
    diagnostics: List[Diagnostic] = []
    scanner = ReferenceScanner(root)
    try:
        before = scanner.discover(ScanScope.REPOSITORY)
        raw_by_path = {
            source.relative: source.raw_bytes for source in before.sources
        }
        logical_sources = sorted({
            (
                path[:-len(COMPANION_SUFFIX)]
                if path.endswith(COMPANION_SUFFIX)
                else path
            )
            for path in raw_by_path
        })
        snapshot, findings = reconstruct(
            root, logical_sources, source_bytes=raw_by_path,
        )
        after = scanner.discover(ScanScope.REPOSITORY)
    except (OSError, RuntimeError, TypeError, UnicodeError, ValueError) as error:
        reasons.add("graph_ownership_indeterminate")
        generation = digest_json({
            "status": "unavailable",
            "reason": type(error).__name__,
        })
        return generation, sorted(reasons), diagnostics
    if before.freshness.digest != after.freshness.digest:
        diagnostics.append(diagnostic(
            "source_generation_changed",
            "Repository graph sources changed during classification.",
            "source_context",
        ))
    if not before.freshness.complete or not after.freshness.complete:
        reasons.add("graph_source_coverage_incomplete")
    if any(
        getattr(item.severity, "value", item.severity) == "error"
        for item in findings
    ):
        reasons.add("graph_reconstruction_diagnostic")
    changed = set(changed_sources)
    declared_locator_paths = {node.locator.path for node in snapshot.nodes}
    declared_locator_paths.update(_raw_declared_locator_paths(raw_by_path))
    if declared_locator_paths & changed:
        reasons.add("declared_locator_ownership")
    generation = digest_json({
        "scope": "repository",
        "freshness_digest": before.freshness.digest,
        "discovered_paths": list(before.freshness.discovered_paths),
        "complete": before.freshness.complete,
    })
    return generation, sorted(reasons), diagnostics


def _raw_declared_locator_paths(
    raw_by_path: Mapping[str, bytes],
) -> List[str]:
    """Recover explicitly declared locator paths even when ownership is cross-surface."""

    declared = set()
    logical_paths = sorted({
        (
            path[:-len(COMPANION_SUFFIX)]
            if path.endswith(COMPANION_SUFFIX)
            else path
        )
        for path in raw_by_path
    })
    for logical in logical_paths:
        companion_path = logical + COMPANION_SUFFIX
        companion = raw_by_path.get(companion_path)
        if companion is not None:
            try:
                value = load_authoritative_json(companion.decode("utf-8"))
            except (UnicodeError, TypeError, ValueError):
                pass
            else:
                nodes = value.get("nodes") if isinstance(value, Mapping) else None
                if isinstance(nodes, list):
                    for node in nodes:
                        locator = node.get("locator") if isinstance(node, Mapping) else None
                        if isinstance(locator, Mapping):
                            path = locator.get("path")
                            if isinstance(path, str) and path:
                                declared.add(path)
        raw = raw_by_path.get(logical)
        adapter = adapter_for_path(logical)
        if raw is None or adapter is None:
            continue
        try:
            text = raw.decode("utf-8")
            blocks = adapter.metadata_blocks(text)
            for block, _construct, _label in blocks:
                declared.update(_locator_paths_from_metadata_block(block))
        except (UnicodeError, MetadataError, TypeError, ValueError):
            continue
    return sorted(declared)


def _locator_paths_from_metadata_block(block: str) -> List[str]:
    if "=" in block and not any(
        line.lstrip().startswith(("key:", "locator:"))
        for line in block.splitlines()
    ):
        result = []
        for token in shlex.split(block.replace(", ", ",")):
            if token.startswith("locator.path="):
                value = token.split("=", 1)[1].rstrip(",")
                if value:
                    result.append(value)
        return result
    value = parse_yaml_subset(block.strip())
    candidates = []
    if isinstance(value, Mapping):
        candidates.append(value.get("locator"))
        key = value.get("key")
        if isinstance(key, Mapping):
            candidates.append(key.get("locator"))
    result = []
    for locator in candidates:
        if isinstance(locator, Mapping):
            path = locator.get("path")
            if isinstance(path, str) and path:
                result.append(path)
    return result


def _validate_current_generation(
    deltas: Sequence[Mapping[str, Any]],
    inspected: Sequence[Mapping[str, Any]],
) -> List[Diagnostic]:
    by_path = {str(item.get("path")): item for item in inspected}
    diagnostics: List[Diagnostic] = []
    deltas_by_path: Dict[str, List[Tuple[int, Mapping[str, Any]]]] = {}
    for index, delta in enumerate(deltas):
        deltas_by_path.setdefault(str(delta["source_surface"]), []).append(
            (index, delta)
        )
    for path, path_deltas in deltas_by_path.items():
        for position in range(1, len(path_deltas)):
            _previous_index, previous = path_deltas[position - 1]
            index, current_delta = path_deltas[position]
            if previous["resulting_digest"] != current_delta["baseline_digest"]:
                diagnostics.append(diagnostic(
                    "delta_generation_chain_invalid",
                    "A repeated source surface must chain each resulting digest "
                    "to the next phase baseline digest.",
                    "deltas[%d].baseline_digest" % index,
                ))
        index, delta = path_deltas[-1]
        current = by_path.get(path, {})
        change_kind = delta["change_kind"]
        expected = delta["resulting_digest"]
        current_digest = (
            current.get("raw_byte_digest")
            if current.get("type") == "regular_file"
            else ABSENT if current.get("type") == "absent" else None
        )
        if change_kind == "deleted":
            generation_matches = expected == ABSENT and current_digest == ABSENT
        else:
            generation_matches = _digest(expected) and current_digest == expected
        if not generation_matches:
            diagnostics.append(diagnostic(
                "source_generation_stale",
                "Current source bytes do not match the delta resulting digest.",
                "deltas[%d].resulting_digest" % index,
            ))
    return diagnostics


def _validate_delta(value: Any, index: int) -> Mapping[str, Any]:
    path = "deltas[%d]" % index
    if not isinstance(value, Mapping):
        raise ClassificationInputError("%s must be an object" % path)
    _exact_fields(value, DELTA_FIELDS, path)
    if value.get("kind") not in DELTA_KINDS:
        raise ClassificationInputError("%s.kind is invalid" % path)
    source_surface = _canonical_path(value.get("source_surface"), path + ".source_surface")
    if value.get("change_kind") not in CHANGE_KINDS:
        raise ClassificationInputError("%s.change_kind is invalid" % path)
    if not _text(value.get("semantic_summary")):
        raise ClassificationInputError("%s.semantic_summary is required" % path)
    if not isinstance(value.get("graph_relevant"), bool):
        raise ClassificationInputError("%s.graph_relevant must be boolean" % path)
    baseline = value.get("baseline_digest")
    resulting = value.get("resulting_digest")
    if baseline != ABSENT and not _digest(baseline):
        raise ClassificationInputError("%s.baseline_digest is invalid" % path)
    if resulting != ABSENT and not _digest(resulting):
        raise ClassificationInputError("%s.resulting_digest is invalid" % path)
    if value["change_kind"] == "added" and baseline != ABSENT:
        raise ClassificationInputError("%s added delta requires absent baseline" % path)
    if value["change_kind"] == "deleted" and resulting != ABSENT:
        raise ClassificationInputError("%s deleted delta requires absent result" % path)
    if value["change_kind"] in {"modified", "type_replaced"} and (
        baseline == ABSENT or resulting == ABSENT
    ):
        raise ClassificationInputError(
            "%s modified/type-replaced delta requires both digests" % path
        )
    raw_locators = value.get("changed_locators")
    if not isinstance(raw_locators, list) or not raw_locators:
        raise ClassificationInputError("%s.changed_locators must be non-empty" % path)
    locators = [
        _validate_locator(item, source_surface, "%s.changed_locators[%d]" % (path, position))
        for position, item in enumerate(raw_locators)
    ]
    if locators != sorted(locators, key=canonical_json_bytes):
        raise ClassificationInputError("%s.changed_locators must be canonically sorted" % path)
    if len({canonical_json_bytes(item) for item in locators}) != len(locators):
        raise ClassificationInputError("%s.changed_locators must be unique" % path)
    return {
        "kind": value["kind"],
        "source_surface": source_surface,
        "change_kind": value["change_kind"],
        "changed_locators": locators,
        "semantic_summary": value["semantic_summary"],
        "baseline_digest": baseline,
        "resulting_digest": resulting,
        "graph_relevant": value["graph_relevant"],
    }


def _validate_locator(value: Any, source_surface: str, path: str) -> Dict[str, str]:
    if not isinstance(value, Mapping):
        raise ClassificationInputError("%s must be an object" % path)
    if "path" not in value or set(value) - LOCATOR_FIELDS:
        raise ClassificationInputError("%s has invalid locator fields" % path)
    result: Dict[str, str] = {}
    for field, item in value.items():
        if not _text(item):
            raise ClassificationInputError("%s.%s must be non-empty text" % (path, field))
        result[field] = (
            _canonical_path(item, path + ".path") if field == "path" else item
        )
    if result["path"] != source_surface:
        raise ClassificationInputError(
            "%s.path must equal the delta source_surface" % path
        )
    return result


def _exact_fields(value: Mapping[str, Any], expected: set, path: str) -> None:
    if set(value) != expected:
        missing = sorted(expected - set(value))
        unknown = sorted(set(value) - expected)
        raise ClassificationInputError(
            "%s fields are not canonical (missing=%s, unknown=%s)"
            % (path, missing, unknown)
        )


def _canonical_path(value: Any, path: str) -> str:
    try:
        result = canonical_relative_path(value)
    except (TypeError, ValueError) as error:
        raise ClassificationInputError("%s is not canonical: %s" % (path, error)) from error
    if unicodedata.normalize("NFC", result) != result:
        raise ClassificationInputError("%s must use NFC normalization" % path)
    return result


def _digest(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith(DIGEST_PREFIX):
        return False
    suffix = value[len(DIGEST_PREFIX):]
    return len(suffix) == 64 and all(character in "0123456789abcdef" for character in suffix)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _stat_identity(value: os.stat_result) -> Tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )
