#!/usr/bin/env python3
"""Reconstruct and mechanically validate a Keystone Artifact Graph."""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Mapping

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from graph_runtime.validator import (
    diagnostic, envelope, reconstruct, validate_snapshot, validate_transaction,
)
from graph_runtime.model import Severity, patch_source_identity
from graph_runtime.companion import load_authoritative_json
from graph_runtime.application_evidence import (
    VerifiedApplicationEvidence,
    digest_bytes,
    normalize_evidence_path,
    validate_application_evidence,
)
from graph_runtime.scanner import ReferenceScanner, ScanScope
from graph_runtime.source_unit import COMPANION_SUFFIX, resolve_source_unit
from graph_runtime.validation_support import safe_path


_COMPANION_SUFFIX = COMPANION_SUFFIX
_INCOMPLETE_DISCOVERY_CODES = {
    "scan_truncated", "source_too_large", "source_unreadable",
}


def logical_source(path):
    return path[:-len(_COMPANION_SUFFIX)] if path.endswith(_COMPANION_SUFFIX) else path


def coverage_severity(code, requested_coverage, default):
    if code not in _INCOMPLETE_DISCOVERY_CODES:
        return default
    if requested_coverage == "full":
        return Severity.ERROR
    if requested_coverage == "subset":
        return Severity.WARNING
    return default


def capture_sources(root, sources):
    captured = {}
    absent = set()
    for relative in sorted(set(sources)):
        source_path = safe_path(root, relative)
        companion_relative = relative + _COMPANION_SUFFIX
        companion_path = safe_path(root, companion_relative)
        raw_source = source_path.read_bytes() if source_path.is_file() else None
        raw_companion = (
            companion_path.read_bytes() if companion_path.is_file() else None
        )
        unit = resolve_source_unit(relative, raw_source, raw_companion)
        if unit.surface is None and not unit.diagnostics:
            raise FileNotFoundError(relative)
        captured.update(unit.generation_items)
        if raw_source is None:
            absent.add(relative)
    return captured, absent


def generation_findings(root, captured, absent):
    findings = []
    for relative, expected in sorted(captured.items()):
        path = safe_path(root, relative)
        try:
            actual = path.read_bytes()
        except OSError:
            actual = None
        if actual != expected:
            findings.append(diagnostic(
                "source_generation_changed",
                "source bytes changed during validation",
                relative,
            ))
    for relative in sorted(absent):
        if safe_path(root, relative).exists():
            findings.append(diagnostic(
                "source_generation_changed",
                "previously absent source appeared during validation",
                relative,
            ))
    return findings


def application_baseline_sources(
    captured: Mapping[str, bytes],
    evidence: VerifiedApplicationEvidence,
) -> Dict[str, bytes]:
    """Restore authenticated pre-application bytes for every applied target."""
    baseline = dict(captured)
    for verified_receipt in evidence.receipts:
        try:
            patch = verified_receipt.envelope["receipt"]["patch_receipt"]["patch"]
            target = normalize_evidence_path(patch.get("target_path"))
            baseline_digest = patch.get("baseline_digest")
            baseline_content = patch.get("baseline_content")
        except (KeyError, TypeError) as error:
            raise ValueError("verified receipt has no canonical patch") from error
        if target is None:
            raise ValueError("verified receipt target path is invalid")
        if target not in baseline:
            raise ValueError(
                "applied target is absent from captured source generation: %s"
                % target
            )
        if baseline_digest == "absent":
            if baseline_content is not None:
                raise ValueError("absent patch baseline must have null content")
            baseline.pop(target)
            continue
        if not isinstance(baseline_content, str):
            raise ValueError("patch baseline content must be UTF-8 text")
        raw_baseline = baseline_content.encode("utf-8")
        if digest_bytes(raw_baseline) != baseline_digest:
            raise ValueError("patch baseline content digest is invalid")
        baseline[target] = raw_baseline
    return baseline


def coverage_envelope(discovery, declared_sources, manifest_declared, coverage_mode):
    discovered_paths = set(discovery.freshness.discovered_paths)
    parsed_paths = {item.relative for item in discovery.sources}
    discovered_sources = {logical_source(path) for path in discovered_paths}
    skipped_sources = {
        logical_source(path) for path in discovered_paths - parsed_paths
    }
    parsed_sources = {
        logical_source(path) for path in parsed_paths
    } - skipped_sources
    omitted_sources = (
        discovered_sources - declared_sources - skipped_sources
        if manifest_declared else set()
    )
    declared_only_sources = (
        declared_sources - discovered_sources if manifest_declared else set()
    )
    path_body = json.dumps(
        sorted(discovered_paths), separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    payload = {
        "mode": coverage_mode or "discovered",
        "complete": bool(
            discovery.freshness.complete
            and not skipped_sources
            and not omitted_sources
            and not declared_only_sources
        ),
        "path_digest": "sha256:" + hashlib.sha256(path_body).hexdigest(),
        "discovered_sources": sorted(discovered_sources),
        "parsed_sources": sorted(parsed_sources),
        "omitted_sources": sorted(omitted_sources),
        "declared_only_sources": sorted(declared_only_sources),
        "skipped_sources": sorted(skipped_sources),
        "counts": {
            "discovered": len(discovered_sources),
            "parsed": len(parsed_sources),
            "omitted": len(omitted_sources),
            "declared_only": len(declared_only_sources),
            "skipped": len(skipped_sources),
        },
    }
    return payload, parsed_sources, omitted_sources, declared_only_sources


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Repository root")
    parser.add_argument("--source", action="append", default=[], help="Repeatable repository-relative source")
    parser.add_argument("--manifest", help="JSON manifest containing a sources array and optional transaction")
    parser.add_argument("--transaction", help="JSON graph transaction")
    parser.add_argument("--scope", choices=("transaction", "repository"),
                        help="Validation discovery scope (default: transaction)")
    parser.add_argument(
        "--evidence-root",
        help="External root containing aggregate application evidence and receipts",
    )
    parser.add_argument(
        "--owner-key",
        action="append",
        default=[],
        metavar="OWNER=PATH",
        help="Repeatable applied-owner authority key binding",
    )
    parser.add_argument(
        "--owner-key-sha256",
        action="append",
        default=[],
        metavar="OWNER=sha256:...",
        help="Repeatable applied-owner pinned key digest",
    )
    return parser.parse_args()


def load_json_bytes(path, code):
    try:
        raw = Path(path).read_bytes()
        return load_authoritative_json(raw.decode("utf-8")), raw
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        raise RuntimeError((code, str(error))) from error


def load_json(path, code):
    return load_json_bytes(path, code)[0]


def parse_owner_bindings(values, flag):
    bindings = {}
    for value in values:
        if not isinstance(value, str) or "=" not in value:
            raise RuntimeError((
                "owner_key_argument_invalid",
                "%s requires OWNER=VALUE" % flag,
            ))
        owner, bound = value.split("=", 1)
        if owner not in {"author", "main", "coordinator"} or not bound:
            raise RuntimeError((
                "owner_key_argument_invalid",
                "%s owner must be author, main, or coordinator" % flag,
            ))
        if owner in bindings:
            raise RuntimeError((
                "owner_key_argument_invalid",
                "%s owner binding is duplicated: %s" % (flag, owner),
            ))
        bindings[owner] = bound
    return bindings


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        payload = envelope((diagnostic("root_unavailable", "root is not a directory", args.root),), execution_error=True)
        print(json.dumps(payload, sort_keys=True))
        return 2
    sources = list(args.source)
    transaction = None
    manifest_schema = None
    application_reference = None
    findings = []
    scope = args.scope or "transaction"
    coverage = None
    coverage_payload = None
    captured_sources = None
    absent_sources = set()
    historical_full_context = False
    try:
        if args.manifest:
            manifest, manifest_raw = load_json_bytes(
                args.manifest, "manifest_invalid"
            )
            if (not isinstance(manifest, dict)
                    or type(manifest.get("schema_version")) is not int
                    or manifest.get("schema_version") not in {1, 2}
                    or not isinstance(manifest.get("sources"), list)):
                raise RuntimeError((
                    "manifest_invalid",
                    "manifest requires schema_version 1 or 2 and a sources array",
                ))
            manifest_schema = manifest["schema_version"]
            if manifest_schema == 2:
                try:
                    canonical_manifest = json.dumps(
                        manifest,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                except (UnicodeError, ValueError, RecursionError) as error:
                    raise RuntimeError((
                        "manifest_invalid",
                        "schema-v2 manifest cannot be canonicalized: %s" % error,
                    )) from error
                if manifest_raw != canonical_manifest:
                    raise RuntimeError((
                        "manifest_noncanonical",
                        "schema-v2 manifest bytes must equal canonical JSON serialization",
                    ))
            allowed_manifest = {
                "schema_version", "sources", "transaction", "scope", "coverage",
            }
            if manifest_schema == 2:
                allowed_manifest.add("application_evidence")
            unknown_manifest = sorted(set(manifest) - allowed_manifest)
            if unknown_manifest:
                raise RuntimeError(("manifest_invalid", "unknown manifest fields: %s" % unknown_manifest))
            if manifest_schema == 2 and (
                "transaction" not in manifest
                or "application_evidence" not in manifest
                or not isinstance(manifest.get("transaction"), dict)
                or not isinstance(manifest.get("application_evidence"), dict)
                or set(manifest["application_evidence"]) != {"path", "digest"}
            ):
                raise RuntimeError((
                    "manifest_invalid",
                    "schema_version 2 requires transaction and exact application_evidence reference",
                ))
            if any(not isinstance(source, str) or not source or Path(source).is_absolute()
                   or ".." in Path(source).parts for source in manifest["sources"]):
                raise RuntimeError(("manifest_source_invalid",
                                    "each manifest source must be a non-empty repository-relative string"))
            sources.extend(manifest["sources"])
            transaction = manifest.get("transaction")
            application_reference = manifest.get("application_evidence")
            manifest_scope = manifest.get("scope")
            if manifest_scope is not None and manifest_scope not in {"transaction", "repository"}:
                raise RuntimeError(("manifest_scope_invalid", "manifest scope must be transaction or repository"))
            if args.scope and manifest_scope and args.scope != manifest_scope:
                raise RuntimeError(("manifest_scope_conflict", "CLI and manifest scopes disagree"))
            scope = args.scope or manifest_scope or "transaction"
            coverage = manifest.get("coverage")
            if coverage is not None and coverage not in {"full", "subset"}:
                raise RuntimeError(("manifest_coverage_invalid", "manifest coverage must be full or subset"))
        if args.transaction:
            supplied_transaction = load_json(args.transaction, "transaction_invalid")
            if (
                manifest_schema == 2
                and transaction is not None
                and supplied_transaction != transaction
            ):
                raise RuntimeError((
                    "transaction_manifest_conflict",
                    "schema-v2 manifest transaction and --transaction disagree",
                ))
            transaction = supplied_transaction
        owner_keys = parse_owner_bindings(args.owner_key, "--owner-key")
        owner_key_digests = parse_owner_bindings(
            args.owner_key_sha256, "--owner-key-sha256"
        )
        authority_options_present = bool(
            args.evidence_root or args.owner_key or args.owner_key_sha256
        )
        if authority_options_present and manifest_schema != 2:
            raise RuntimeError((
                "application_evidence_context_unexpected",
                "application-evidence options require manifest schema_version 2",
            ))
        historical_producers = (
            SCRIPT_ROOT.parents[1] / "keystone-author" / "scripts" / "run_owned_surface_apply.py",
            SCRIPT_ROOT.parents[1] / "keystone-author" / "scripts" / "owned_surface_apply_runtime.py",
            SCRIPT_ROOT.parents[1] / "keystone-coordinator" / "scripts" / "run_owned_surface_apply.py",
            SCRIPT_ROOT.parents[1] / "keystone-coordinator" / "scripts" / "owned_surface_apply_runtime.py",
        )
        historical_full_context = bool(
            manifest_schema == 2
            and args.evidence_root
            and owner_keys
            and set(owner_keys) == set(owner_key_digests)
            and all(path.is_file() for path in historical_producers)
        )
        if manifest_schema == 2 and not historical_full_context:
            findings.append(diagnostic(
                "historical_structure_only",
                "Historical schema-v2 application evidence was validated only against "
                "readable structure and current source; retired external trust material "
                "was not required.",
                severity=Severity.WARNING,
            ))
        if (isinstance(transaction, dict)
                and type(transaction.get("schema_version")) is not int
                and transaction.get("schema_version") in (1, 2)):
            findings.append(diagnostic(
                "transaction_schema_invalid",
                "transaction schema_version must be the integer 1 or 2",
            ))
        duplicates = sorted({source for source in sources if sources.count(source) > 1})
        for source in duplicates:
            findings.append(diagnostic("duplicate_manifest_source",
                                       "source is declared more than once: %s" % source))
        declared_sources = set(sources)
        if scope == "repository":
            discovery = ReferenceScanner(root).discover(ScanScope.REPOSITORY)
            (coverage_payload, parsed_sources, omitted,
             declared_only) = coverage_envelope(
                discovery, declared_sources, bool(args.manifest), coverage
            )
            for item in discovery.diagnostics:
                severity = coverage_severity(
                    item.code, coverage, Severity(item.severity)
                )
                findings.append(diagnostic(item.code, item.message, item.path,
                                           severity=severity))
            if omitted:
                omitted_severity = Severity.WARNING if coverage == "subset" else Severity.ERROR
                for source in sorted(omitted):
                    findings.append(diagnostic(
                        "repository_coverage_debt" if coverage == "subset" else "repository_source_omitted",
                        "repository source is omitted from manifest: %s" % source,
                        source, severity=omitted_severity))
            if declared_only:
                declared_only_severity = (
                    Severity.WARNING if coverage == "subset" else Severity.ERROR
                )
                for source in sorted(declared_only):
                    findings.append(diagnostic(
                        "repository_coverage_debt" if coverage == "subset"
                        else "repository_declared_source_missing",
                        "manifest source was not discovered in repository scope: %s" % source,
                        source,
                        severity=declared_only_severity,
                    ))
            sources = sorted(parsed_sources)
            all_captured = {
                item.relative: item.raw_bytes for item in discovery.sources
            }
            required_paths = set(sources) | {
                source + _COMPANION_SUFFIX for source in sources
            }
            captured_sources = {
                path: value for path, value in all_captured.items()
                if path in required_paths
            }
            discovered_paths = set(discovery.freshness.discovered_paths)
            absent_sources = {
                source for source in sources
                if source not in discovered_paths
                and source + _COMPANION_SUFFIX in discovered_paths
            }
        elif transaction is not None:
            patch_targets = {
                patch_source_identity(
                    item.get("surface"), item.get("target_path")
                ) for item in transaction.get("surface_patches", [])
                if isinstance(item, dict) and isinstance(item.get("target_path"), str)
            } if isinstance(transaction, dict) else set()
            for target in sorted(patch_targets - declared_sources):
                findings.append(diagnostic(
                    "transaction_source_omission",
                    "transaction patch target is omitted from validation sources: %s" % target,
                    target))
        if captured_sources is None:
            captured_sources, absent_sources = capture_sources(root, sources)
        snapshot, parse_findings = reconstruct(root, sources, captured_sources)
    except FileNotFoundError as error:
        payload = envelope((diagnostic("source_unavailable", "source or companion is unavailable: %s" % error.args[0]),), execution_error=True)
        print(json.dumps(payload, sort_keys=True))
        return 2
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        detail = error.args[0]
        code, message = detail if isinstance(detail, tuple) else ("validation_execution_failed", str(error))
        payload = envelope((diagnostic(code, message),), execution_error=True)
        print(json.dumps(payload, sort_keys=True))
        return 2
    findings.extend(validate_snapshot(root, snapshot, parse_findings))
    baseline_snapshot = None
    if (
        manifest_schema == 2
        and isinstance(transaction, dict)
        and historical_full_context
    ):
        application_result = validate_application_evidence(
            transaction=transaction,
            application_evidence=application_reference,
            root=root,
            evidence_root=Path(args.evidence_root),
            owner_keys={owner: Path(path) for owner, path in owner_keys.items()},
            owner_key_digests=owner_key_digests,
        )
        findings.extend(application_result.diagnostics)
        if application_result.evidence is not None:
            try:
                baseline_sources = application_baseline_sources(
                    captured_sources, application_result.evidence
                )
                baseline_logical_sources = [
                    source for source in sources
                    if source in baseline_sources
                    or source + _COMPANION_SUFFIX in baseline_sources
                ]
                baseline_snapshot, baseline_parse_findings = reconstruct(
                    root, baseline_logical_sources, baseline_sources
                )
            except (KeyError, TypeError, UnicodeError, ValueError) as error:
                findings.append(diagnostic(
                    "application_baseline_reconstruction_invalid",
                    str(error),
                ))
            else:
                findings.extend(baseline_parse_findings)
    if transaction is not None:
        findings.extend(validate_transaction(
            transaction,
            root,
            snapshot,
            baseline_source_snapshot=baseline_snapshot,
        ))
    findings.extend(generation_findings(root, captured_sources, absent_sources))
    execution_error_codes = {
        "application_evidence_context_invalid",
        "application_evidence_unreadable",
        "application_owner_key_invalid",
        "application_owner_key_mismatch",
        "application_owner_key_separation_required",
        "application_receipt_package_unavailable",
    }
    execution_error = any(
        item.code in execution_error_codes for item in findings
    )
    payload = envelope(
        findings, execution_error=execution_error, coverage=coverage_payload
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    if execution_error:
        return 2
    return 1 if payload["summary"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
