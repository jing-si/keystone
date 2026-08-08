#!/usr/bin/env python3
"""Validate Keystone acceptance-finalization evidence without editing sources."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from finalization_sections import (
    validate_finalization_closure,
    validate_impact_candidates,
    validate_namespace_entries,
)
from finalization_global import validate_global_state
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
V5_MANIFEST_FIELDS = {
    "schema_version",
    "acceptance_ref",
    "steps",
    "accepted_steps",
    "execution_transitions",
    "approval_transitions",
    "active_steps",
    "active_step_sources",
    "global_state",
    "early_work",
    "finalization",
    "graph_sync",
    "impact_candidates",
    "namespace_entries",
}


class DuplicateJsonKey(ValueError):
    pass


def reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJsonKey("duplicate JSON key: %s" % key)
        value[key] = item
    return value


def loads_json_strict(value: str) -> Any:
    return json.loads(value, object_pairs_hook=reject_duplicate_keys)


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


# keystone: id=key.code.author.finalization-validator kind=output_artifact artifact_kind=code refs=key.standard.skill.author.acceptance-finalization locator.symbol=validate_manifest
def validate_manifest(root: Path, manifest: Dict[str, Any]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []

    schema_version = manifest.get("schema_version")
    if type(schema_version) is not int or schema_version not in {1, 2, 3, 4, 5}:
        findings.append(diagnostic(
            "schema_version_unsupported",
            "schema_version must be 1, 2, 3, 4, or 5.",
        ))
    elif schema_version == 5:
        for field in sorted(set(manifest) - V5_MANIFEST_FIELDS):
            findings.append(diagnostic(
                "manifest_field_unknown",
                "schema_version 5 does not allow unknown top-level field: %s." % field,
            ))

    compatibility_version = 4 if schema_version == 5 else schema_version

    if not isinstance(manifest.get("acceptance_ref"), str) or not manifest["acceptance_ref"].strip():
        findings.append(diagnostic("acceptance_ref_missing", "acceptance_ref must be a non-empty string."))

    step_findings, steps = validate_steps_and_transitions(
        root, manifest, compatibility_version
    )
    findings.extend(step_findings)

    findings.extend(validate_finalization_closure(
        root, manifest, compatibility_version
    ))

    findings.extend(validate_early_work(manifest.get("early_work"), steps))

    findings.extend(validate_global_state(root, manifest, schema_version))

    findings.extend(validate_impact_candidates(
        root, manifest.get("impact_candidates"), compatibility_version
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
        manifest = loads_json_strict(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, DuplicateJsonKey) as error:
        message = getattr(error, "msg", str(error))
        return invocation_error("manifest_invalid_json", f"Manifest is not valid JSON: {message}.", args.manifest)
    except (OSError, UnicodeError) as error:
        return invocation_error("manifest_unreadable", f"Cannot read manifest: {error}.", args.manifest)
    if not isinstance(manifest, dict):
        return invocation_error("manifest_invalid_shape", "Manifest root must be a JSON object.", args.manifest)

    findings = validate_manifest(root, manifest)
    output("fail" if findings else "pass", findings)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
