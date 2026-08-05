#!/usr/bin/env python3
"""Reconstruct and mechanically validate a Keystone Artifact Graph."""

import argparse
import json
import sys
from pathlib import Path

from graph_runtime.validator import (
    diagnostic, envelope, reconstruct, validate_snapshot, validate_transaction,
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Repository root")
    parser.add_argument("--source", action="append", default=[], help="Repeatable repository-relative source")
    parser.add_argument("--manifest", help="JSON manifest containing a sources array and optional transaction")
    parser.add_argument("--transaction", help="JSON graph transaction")
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
    try:
        if args.manifest:
            manifest = load_json(args.manifest, "manifest_invalid")
            if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or not isinstance(manifest.get("sources"), list):
                raise RuntimeError(("manifest_invalid", "manifest requires schema_version 1 and sources array"))
            if any(not isinstance(source, str) or not source or Path(source).is_absolute()
                   or ".." in Path(source).parts for source in manifest["sources"]):
                raise RuntimeError(("manifest_source_invalid",
                                    "each manifest source must be a non-empty repository-relative string"))
            sources.extend(manifest["sources"])
            transaction = manifest.get("transaction")
        if args.transaction:
            transaction = load_json(args.transaction, "transaction_invalid")
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
    findings = list(validate_snapshot(root, snapshot, parse_findings))
    if transaction is not None:
        findings.extend(validate_transaction(transaction, root, snapshot))
    payload = envelope(findings)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 1 if payload["summary"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
