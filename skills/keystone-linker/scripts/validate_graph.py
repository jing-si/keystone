#!/usr/bin/env python3
"""Reconstruct and mechanically validate a Keystone Artifact Graph."""

import argparse
import json
import sys
from pathlib import Path

from graph_runtime.validator import (
    diagnostic, envelope, reconstruct, validate_snapshot, validate_transaction,
)
from graph_runtime.model import Severity
from graph_runtime.scanner import ReferenceScanner, ScanScope


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
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
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
    try:
        if args.manifest:
            manifest = load_json(args.manifest, "manifest_invalid")
            if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or not isinstance(manifest.get("sources"), list):
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
        duplicates = sorted({source for source in sources if sources.count(source) > 1})
        for source in duplicates:
            findings.append(diagnostic("duplicate_manifest_source",
                                       "source is declared more than once: %s" % source))
        declared_sources = set(sources)
        if scope == "repository":
            discovery = ReferenceScanner(root).discover(ScanScope.REPOSITORY)
            discovered_sources = {
                item.relative[:-len(".keystone.json")]
                if item.relative.endswith(".keystone.json") else item.relative
                for item in discovery.sources
            }
            for item in discovery.diagnostics:
                findings.append(diagnostic(item.code, item.message, item.path,
                                           severity=Severity(item.severity)))
            omitted = sorted(discovered_sources - declared_sources) if declared_sources else []
            if omitted:
                omitted_severity = Severity.WARNING if coverage == "subset" else Severity.ERROR
                for source in omitted:
                    findings.append(diagnostic(
                        "repository_coverage_debt" if coverage == "subset" else "repository_source_omitted",
                        "repository source is omitted from manifest: %s" % source,
                        source, severity=omitted_severity))
            sources = sorted(discovered_sources)
        elif transaction is not None:
            patch_targets = {
                item.get("target_path") for item in transaction.get("surface_patches", [])
                if isinstance(item, dict) and isinstance(item.get("target_path"), str)
            } if isinstance(transaction, dict) else set()
            for target in sorted(patch_targets - declared_sources):
                findings.append(diagnostic(
                    "transaction_source_omission",
                    "transaction patch target is omitted from validation sources: %s" % target,
                    target))
        snapshot, parse_findings = reconstruct(root, sources)
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
    payload = envelope(findings)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 1 if payload["summary"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
