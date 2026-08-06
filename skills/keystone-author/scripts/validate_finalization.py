#!/usr/bin/env python3
"""Validate Keystone acceptance-finalization evidence without editing sources."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from finalization_sections import (
    validate_finalization_closure,
    validate_impact_candidates,
    validate_namespace_entries,
)
from finalization_steps import (
    validate_early_work,
    validate_steps_and_transitions,
)
from finalization_support import (
    active_steps_from_text,
    approval_scalar,
    diagnostic,
    finalization_scalar,
    inline_mapping_scalar,
    read_scoped_file,
    resolve_scoped_path,
    scalar_from_text,
)


DIAGNOSTIC_SCHEMA_VERSION = 1


def output(status: str, diagnostics: List[Dict[str, str]]) -> None:
    payload = {
        "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
        "status": status,
        "diagnostics": diagnostics,
        "summary": {
            "errors": sum(item["severity"] == "error" for item in diagnostics),
            "warnings": sum(item["severity"] == "warning" for item in diagnostics),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def invocation_error(code: str, message: str, path: Optional[str] = None) -> int:
    output("error", [diagnostic(code, message, path)])
    return 2


def validate_manifest(root: Path, manifest: Dict[str, Any]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []

    schema_version = manifest.get("schema_version")
    if schema_version not in {1, 2, 3}:
        findings.append(diagnostic("schema_version_unsupported", "schema_version must be 1, 2, or 3."))

    if not isinstance(manifest.get("acceptance_ref"), str) or not manifest["acceptance_ref"].strip():
        findings.append(diagnostic("acceptance_ref_missing", "acceptance_ref must be a non-empty string."))

    step_findings, steps = validate_steps_and_transitions(root, manifest, schema_version)
    findings.extend(step_findings)

    findings.extend(validate_finalization_closure(root, manifest, schema_version))

    findings.extend(validate_early_work(manifest.get("early_work"), steps))

    findings.extend(validate_impact_candidates(
        root, manifest.get("impact_candidates"), schema_version
    ))
    findings.extend(validate_namespace_entries(manifest.get("namespace_entries")))

    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Keystone document root or repository root")
    parser.add_argument("--manifest", required=True, help="Acceptance-finalization manifest JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        return invocation_error("root_unavailable", "--root must resolve to an existing directory.", args.root)
    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file():
        return invocation_error("manifest_unavailable", "--manifest must resolve to an existing file.", args.manifest)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return invocation_error("manifest_invalid_json", f"Manifest is not valid JSON: {error.msg}.", args.manifest)
    except (OSError, UnicodeError) as error:
        return invocation_error("manifest_unreadable", f"Cannot read manifest: {error}.", args.manifest)
    if not isinstance(manifest, dict):
        return invocation_error("manifest_invalid_shape", "Manifest root must be a JSON object.", args.manifest)

    findings = validate_manifest(root, manifest)
    output("fail" if findings else "pass", findings)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
