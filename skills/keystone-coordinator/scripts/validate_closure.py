#!/usr/bin/env python3
"""Validate a lean current-state Coordinator closure report."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from work_state_runtime import evaluate_repository


SCHEMA_VERSION = 1
EXECUTION_MODES = {"direct_execution", "orchestration"}
REPORT_STATUSES = {"DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "NEEDS_SCOPE_CHANGE", "BLOCKED"}
PRE_ACCEPTANCE_DECISIONS = {"accept_candidate", "repair", "review", "verify", "escalate", "block"}
POST_ACCEPTANCE_DECISIONS = {"closure_complete", "repair", "escalate", "block"}
SYNC_DISPOSITIONS = {"required", "not_applicable", "deferred"}


class DuplicateJsonKey(ValueError):
    pass


class NonfiniteJsonValue(ValueError):
    pass


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKey("duplicate JSON key: %s" % key)
        result[key] = value
    return result


def _reject_nonfinite(value):
    raise NonfiniteJsonValue("non-finite JSON number is forbidden: %s" % value)


def _loads_json_strict(value):
    return json.loads(
        value, object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite,
    )


def _diagnostic(code, message, path, severity="error"):
    return {"code": code, "message": message, "path": path, "severity": severity}


def _mapping(value):
    return value if isinstance(value, Mapping) else {}


def _sequence(value):
    return value if isinstance(value, list) else []


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _evidence(value):
    return bool(_sequence(value)) and all(_text(item) for item in value)


def _validate_historical_structure(manifest, diagnostics):
    schema = manifest.get("schema_version")
    required = (
        {"closure_phase", "closure_target", "worker_report", "keystone_closure", "coordinator_review"}
        if schema == 2 else
        {"closure_stage", "closure_target", "worker_report", "keystone_closure", "coordinator_review"}
    )
    for field in sorted(required - set(manifest)):
        diagnostics.append(_diagnostic(
            "historical_field_missing",
            "Historical schema-v%d structure is missing %s." % (schema, field),
            field,
        ))
    diagnostics.append(_diagnostic(
        "historical_structure_only",
        "Historical schema-v%d was inspected structurally; retired trust material and producers are not current authority." % schema,
        "schema_version",
        "warning",
    ))


def _validate_execution(manifest, diagnostics):
    mode = manifest.get("execution_mode")
    if mode not in EXECUTION_MODES:
        diagnostics.append(_diagnostic(
            "execution_mode_invalid",
            "execution_mode must be direct_execution or orchestration.",
            "execution_mode",
        ))
        return
    skill_ids = [
        item.get("skill_id") for item in _sequence(manifest.get("injected_skills"))
        if isinstance(item, Mapping) and _text(item.get("skill_id"))
    ]
    if mode == "orchestration" and not skill_ids:
        diagnostics.append(_diagnostic(
            "orchestration_skill_missing",
            "orchestration requires the selected external implementation skill.",
            "injected_skills",
        ))


def _validate_report(manifest, diagnostics):
    report = _mapping(manifest.get("worker_report"))
    if not report:
        diagnostics.append(_diagnostic(
            "worker_report_missing", "worker_report must be an object.", "worker_report"
        ))
        return False
    if report.get("status") not in REPORT_STATUSES:
        diagnostics.append(_diagnostic(
            "worker_status_invalid", "worker_report.status is invalid.", "worker_report.status"
        ))
    changed_files = report.get("changed_files")
    if not isinstance(changed_files, list) or not all(_text(item) for item in changed_files):
        diagnostics.append(_diagnostic(
            "changed_files_invalid", "changed_files must be a list of paths.", "worker_report.changed_files"
        ))
    if report.get("scope_check") != "within_scope":
        diagnostics.append(_diagnostic(
            "scope_check_failed", "The current diff must be within the approved scope.", "worker_report.scope_check"
        ))
    if report.get("forbidden_change_check") != "none":
        diagnostics.append(_diagnostic(
            "forbidden_change_check_failed", "Forbidden or unrelated changes must be absent.",
            "worker_report.forbidden_change_check",
        ))
    verification = _mapping(report.get("verification"))
    if verification.get("status") not in {"pass", "fail", "not_run"}:
        diagnostics.append(_diagnostic(
            "verification_status_invalid", "verification.status must be pass, fail, or not_run.",
            "worker_report.verification.status",
        ))
    if verification.get("status") == "pass" and not _evidence(verification.get("evidence")):
        diagnostics.append(_diagnostic(
            "verification_evidence_missing", "Passing verification requires observed evidence.",
            "worker_report.verification.evidence",
        ))
    for index, delta in enumerate(_sequence(report.get("artifact_deltas"))):
        if not isinstance(delta, Mapping) or not _text(delta.get("source_surface")):
            diagnostics.append(_diagnostic(
                "artifact_delta_invalid", "Each supplied artifact delta needs source_surface.",
                "worker_report.artifact_deltas[%d]" % index,
            ))
    return (
        report.get("status") == "DONE"
        and verification.get("status") == "pass"
        and report.get("scope_check") == "within_scope"
        and report.get("forbidden_change_check") == "none"
    )


def _validate_sync(name, value, diagnostics):
    if not isinstance(value, Mapping):
        diagnostics.append(_diagnostic(
            "sync_invalid", "%s must be an object when supplied." % name,
            "keystone_closure.%s" % name,
        ))
        return
    disposition = value.get("disposition")
    if disposition not in SYNC_DISPOSITIONS:
        diagnostics.append(_diagnostic(
            "sync_disposition_invalid", "%s disposition is invalid." % name,
            "keystone_closure.%s.disposition" % name,
        ))
    if not _text(value.get("reason")):
        diagnostics.append(_diagnostic(
            "sync_reason_missing", "%s needs a concise reason." % name,
            "keystone_closure.%s.reason" % name,
        ))
    if disposition == "required" and not _evidence(value.get("evidence")):
        diagnostics.append(_diagnostic(
            "sync_evidence_missing", "Required %s needs current-state evidence." % name,
            "keystone_closure.%s.evidence" % name,
        ))


def _validate_review(manifest, report_ready, diagnostics):
    phase = manifest.get("closure_phase")
    if phase not in {"pre_acceptance", "post_acceptance"}:
        diagnostics.append(_diagnostic(
            "closure_phase_invalid", "closure_phase must be pre_acceptance or post_acceptance.",
            "closure_phase",
        ))
        return
    review = _mapping(manifest.get("coordinator_review"))
    decision = review.get("decision")
    allowed = PRE_ACCEPTANCE_DECISIONS if phase == "pre_acceptance" else POST_ACCEPTANCE_DECISIONS
    if decision not in allowed:
        diagnostics.append(_diagnostic(
            "review_decision_invalid", "Coordinator review decision is invalid for this phase.",
            "coordinator_review.decision",
        ))
        return
    if decision in {"accept_candidate", "closure_complete"} and not report_ready:
        diagnostics.append(_diagnostic(
            "acceptance_candidate_not_ready", "Acceptance readiness requires a DONE, verified, in-scope result.",
            "coordinator_review.decision",
        ))
    if decision == "closure_complete":
        if not _text(review.get("acceptance_ref")):
            diagnostics.append(_diagnostic(
                "acceptance_ref_missing", "closure_complete requires Main's acceptance_ref.",
                "coordinator_review.acceptance_ref",
            ))
        progress = _mapping(_mapping(manifest.get("keystone_closure")).get("progress"))
        if progress.get("state") != "updated" or not _evidence(progress.get("evidence")):
            diagnostics.append(_diagnostic(
                "progress_sync_incomplete", "closure_complete requires durable updated Progress evidence.",
                "keystone_closure.progress",
            ))


def validate_manifest(manifest: Any, **_historical_context) -> Dict[str, Any]:
    diagnostics: List[Dict[str, str]] = []
    if not isinstance(manifest, Mapping):
        diagnostics.append(_diagnostic("manifest_invalid", "Manifest root must be an object.", "$"))
    elif manifest.get("schema_version") in {2, 3}:
        _validate_historical_structure(manifest, diagnostics)
    else:
        if manifest.get("schema_version") != SCHEMA_VERSION:
            diagnostics.append(_diagnostic(
                "schema_version_invalid", "Current closure schema_version must be 1.", "schema_version"
            ))
        _validate_execution(manifest, diagnostics)
        report_ready = _validate_report(manifest, diagnostics)
        closure = manifest.get("keystone_closure")
        if not isinstance(closure, Mapping):
            diagnostics.append(_diagnostic(
                "keystone_closure_missing", "keystone_closure must be an object.", "keystone_closure"
            ))
        else:
            for name in ("document_sync", "metadata_sync", "graph_sync", "work_state_sync"):
                if name in closure:
                    _validate_sync(name, closure[name], diagnostics)
        _validate_review(manifest, report_ready, diagnostics)

    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "fail" if errors else "pass",
        "diagnostics": diagnostics,
        "summary": {"errors": errors, "warnings": warnings},
    }


def _error_result(code, message):
    diagnostic = _diagnostic(code, message, "manifest")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "error",
        "diagnostics": [diagnostic],
        "summary": {"errors": 1, "warnings": 0},
    }


def derive_repository_work_state(root: Path) -> Dict[str, Any]:
    return evaluate_repository(Path(root))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--root", type=Path)
    # Historical flags stay parseable but do not restore retired authority.
    parser.add_argument("--assignment", type=Path)
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--linker-runner", type=Path)
    parser.add_argument("--author-runner", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--capture-authority-key", type=Path)
    parser.add_argument("--trusted-capture-authority-key-sha256")
    parser.add_argument("--acceptance-authority-key", type=Path)
    parser.add_argument("--trusted-acceptance-authority-key-sha256")
    parser.add_argument("--owner-key", action="append", default=[])
    parser.add_argument("--owner-key-sha256", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        manifest = _loads_json_strict(args.manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        result = _error_result("manifest_unreadable", str(error))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2
    except (json.JSONDecodeError, DuplicateJsonKey, NonfiniteJsonValue) as error:
        result = _error_result("manifest_json_invalid", str(error))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2
    result = validate_manifest(manifest)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
