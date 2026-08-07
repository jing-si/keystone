#!/usr/bin/env python3
"""Reconstruct and mechanically validate a Keystone Artifact Graph."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from graph_runtime.validator import (
    diagnostic, envelope, reconstruct, validate_snapshot, validate_transaction,
)
from graph_runtime.model import Severity, patch_source_identity
from graph_runtime.companion import load_authoritative_json
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
    return parser.parse_args()


def load_json(path, code):
    try:
        return load_authoritative_json(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise RuntimeError((code, str(error))) from error


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        payload = envelope((diagnostic("root_unavailable", "root is not a directory", args.root),), execution_error=True)
        print(json.dumps(payload, sort_keys=True))
        return 2
    sources = list(args.source)
    transaction = None
    findings = []
    scope = args.scope or "transaction"
    coverage = None
    coverage_payload = None
    captured_sources = None
    absent_sources = set()
    try:
        if args.manifest:
            manifest = load_json(args.manifest, "manifest_invalid")
            if (not isinstance(manifest, dict)
                    or type(manifest.get("schema_version")) is not int
                    or manifest.get("schema_version") != 1
                    or not isinstance(manifest.get("sources"), list)):
                raise RuntimeError(("manifest_invalid", "manifest requires schema_version 1 and sources array"))
            allowed_manifest = {"schema_version", "sources", "transaction", "scope", "coverage"}
            unknown_manifest = sorted(set(manifest) - allowed_manifest)
            if unknown_manifest:
                raise RuntimeError(("manifest_invalid", "unknown manifest fields: %s" % unknown_manifest))
            if any(not isinstance(source, str) or not source or Path(source).is_absolute()
                   or ".." in Path(source).parts for source in manifest["sources"]):
                raise RuntimeError(("manifest_source_invalid",
                                    "each manifest source must be a non-empty repository-relative string"))
            sources.extend(manifest["sources"])
            transaction = manifest.get("transaction")
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
            transaction = load_json(args.transaction, "transaction_invalid")
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
    if transaction is not None:
        findings.extend(validate_transaction(transaction, root, snapshot))
    findings.extend(generation_findings(root, captured_sources, absent_sources))
    payload = envelope(findings, coverage=coverage_payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 1 if payload["summary"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
