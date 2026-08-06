#!/usr/bin/env python3
"""Validate Coordinator context and Keystone closure evidence."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence


SCHEMA_VERSION = 1
EXECUTION_MODES = {"direct_execution", "orchestration"}
CLOSURE_PHASES = {"pre_acceptance", "post_acceptance"}
REPORT_STATUSES = {
    "DONE",
    "DONE_WITH_CONCERNS",
    "NEEDS_CONTEXT",
    "NEEDS_SCOPE_CHANGE",
    "BLOCKED",
}
ACCEPT_CANDIDATE_REPORT_STATUS = "DONE"
CONTEXT_STATUSES = {"ready", "not_applicable", "blocked"}
SYNC_DISPOSITIONS = {"required", "not_applicable", "deferred"}
PRE_ACCEPTANCE_DECISIONS = {"accept_candidate", "repair", "review", "verify", "escalate", "block"}
POST_ACCEPTANCE_DECISIONS = {"closure_complete", "repair", "escalate", "block"}
DEFAULT_WORKER_SKILL = "keystone-default-bounded-worker"
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


Diagnostic = Dict[str, str]
Payload = Mapping[str, Any]


def _diagnostic(code: str, message: str, path: str) -> Diagnostic:
    return {"code": code, "message": message, "path": path, "severity": "error"}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, list):
        return value
    return []


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_evidence(value: Any) -> bool:
    return bool(_sequence(value)) and all(_has_text(item) for item in _sequence(value))


def _is_list(value: Any) -> bool:
    return isinstance(value, list)


def _validate_schema(manifest: Payload, diagnostics: List[Diagnostic]) -> None:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        diagnostics.append(
            _diagnostic(
                "schema_version_invalid",
                "Coordinator closure manifest schema_version must be 1.",
                "schema_version",
            )
        )


def _validate_execution_mode(manifest: Payload, diagnostics: List[Diagnostic]) -> None:
    mode = manifest.get("execution_mode")
    if mode not in EXECUTION_MODES:
        diagnostics.append(
            _diagnostic(
                "execution_mode_invalid",
                "execution_mode must be direct_execution or orchestration.",
                "execution_mode",
            )
        )
        return

    skills = [_mapping(item) for item in _sequence(manifest.get("injected_skills"))]
    skill_ids = [item.get("skill_id") for item in skills if _has_text(item.get("skill_id"))]
    external_skills = [skill_id for skill_id in skill_ids if skill_id != DEFAULT_WORKER_SKILL]

    if mode == "orchestration" and not external_skills:
        diagnostics.append(
            _diagnostic(
                "orchestration_external_skill_missing",
                "orchestration mode requires at least one external injected skill.",
                "injected_skills",
            )
        )
    if mode == "direct_execution" and DEFAULT_WORKER_SKILL not in skill_ids:
        diagnostics.append(
            _diagnostic(
                "direct_execution_default_skill_missing",
                "direct_execution requires the default bounded-worker contract.",
                "injected_skills",
            )
        )
    if mode == "direct_execution" and external_skills:
        diagnostics.append(
            _diagnostic(
                "direct_execution_external_skill_forbidden",
                "direct_execution may use only the default bounded-worker contract.",
                "injected_skills",
            )
        )


def _validate_context_pack(manifest: Payload, diagnostics: List[Diagnostic]) -> bool:
    context = _mapping(manifest.get("context_pack"))
    valid = True
    if not context:
        diagnostics.append(
            _diagnostic("context_pack_missing", "context_pack is required.", "context_pack")
        )
        return False

    if not _has_text(context.get("main_context_checkpoint")):
        diagnostics.append(
            _diagnostic(
                "main_context_checkpoint_missing",
                "Context Pack must preserve Main intent and accepted decisions.",
                "context_pack.main_context_checkpoint",
            )
        )
        valid = False

    work = _mapping(context.get("work_context"))
    for field in ("round_ref", "work_ref"):
        if not _has_text(work.get(field)):
            diagnostics.append(
                _diagnostic(
                    "work_context_missing",
                    f"work_context.{field} is required.",
                    f"context_pack.work_context.{field}",
                )
            )
            valid = False
    if not _has_evidence(work.get("step_refs")):
        diagnostics.append(
            _diagnostic(
                "work_context_missing",
                "work_context.step_refs must contain at least one Step reference.",
                "context_pack.work_context.step_refs",
            )
        )
        valid = False

    for field, code in (
        ("source_documents", "source_documents_missing"),
        ("applicable_standards", "applicable_standards_missing"),
    ):
        if not _has_evidence(context.get(field)):
            diagnostics.append(
                _diagnostic(
                    code,
                    f"context_pack.{field} must not be empty.",
                    f"context_pack.{field}",
                )
            )
            valid = False

    if not _is_list(context.get("accepted_decisions")):
        diagnostics.append(
            _diagnostic(
                "accepted_decisions_missing",
                "context_pack.accepted_decisions must be an explicit array; it may be empty.",
                "context_pack.accepted_decisions",
            )
        )
        valid = False
    for field, code in (
        ("completion_criteria", "completion_criteria_missing"),
        ("forbidden_changes", "forbidden_changes_missing"),
        ("verification_expectations", "verification_expectations_missing"),
    ):
        if not _has_evidence(context.get(field)):
            diagnostics.append(
                _diagnostic(
                    code,
                    f"context_pack.{field} must be a non-empty array of bounded evidence.",
                    f"context_pack.{field}",
                )
            )
            valid = False

    scope_boundaries = _mapping(context.get("scope_boundaries"))
    if not scope_boundaries or any(
        not _is_list(scope_boundaries.get(field))
        for field in ("read_scope", "allowed_edit_scope", "excluded_scope")
    ):
        diagnostics.append(
            _diagnostic(
                "scope_boundaries_missing",
                "context_pack.scope_boundaries must explicitly declare read, allowed-edit, and excluded scope.",
                "context_pack.scope_boundaries",
            )
        )
        valid = False

    for name in ("artifact_context", "reader_context", "author_context"):
        item = _mapping(context.get(name))
        status = item.get("status")
        if status not in CONTEXT_STATUSES:
            diagnostics.append(
                _diagnostic(
                    f"{name}_status_invalid",
                    f"{name}.status must be ready, not_applicable, or blocked.",
                    f"context_pack.{name}.status",
                )
            )
            valid = False
        if status in {"ready", "not_applicable"} and not _has_evidence(item.get("evidence")):
            diagnostics.append(
                _diagnostic(
                    f"{name}_evidence_missing",
                    f"Ready or not-applicable {name} requires evidence.",
                    f"context_pack.{name}.evidence",
                )
            )
            valid = False
        if status == "blocked":
            valid = False
    return valid


def _validate_artifact_deltas(report: Payload, diagnostics: List[Diagnostic]) -> bool:
    valid = True
    if not _is_list(report.get("changed_files")):
        diagnostics.append(
            _diagnostic(
                "worker_report_changed_files_missing",
                "worker_report.changed_files must be an explicit array; use [] for no change.",
                "worker_report.changed_files",
            )
        )
        valid = False
    if not _is_list(report.get("artifact_deltas")):
        diagnostics.append(
            _diagnostic(
                "worker_report_artifact_deltas_missing",
                "worker_report.artifact_deltas must be an explicit array; use [] for no change.",
                "worker_report.artifact_deltas",
            )
        )
        valid = False

    changed_files: List[str] = []
    for index, item in enumerate(_sequence(report.get("changed_files"))):
        path = f"worker_report.changed_files[{index}]"
        if not _has_text(item):
            diagnostics.append(
                _diagnostic(
                    "worker_report_changed_file_invalid",
                    "Each changed_files entry must be a non-blank string.",
                    path,
                )
            )
            valid = False
        elif item in changed_files:
            diagnostics.append(
                _diagnostic(
                    "worker_report_changed_file_duplicate",
                    "Each changed_files entry must be unique.",
                    path,
                )
            )
            valid = False
        else:
            changed_files.append(item)
    deltas = [_mapping(item) for item in _sequence(report.get("artifact_deltas"))]
    delta_counts: Dict[str, int] = {}
    for item in deltas:
        surface = item.get("source_surface")
        if _has_text(surface):
            delta_counts[surface] = delta_counts.get(surface, 0) + 1

    for changed_file in changed_files:
        if delta_counts.get(changed_file, 0) == 0:
            diagnostics.append(
                _diagnostic(
                    "artifact_delta_missing",
                    f"Changed file {changed_file} has no artifact delta.",
                    "worker_report.artifact_deltas",
                )
            )
            valid = False
        elif delta_counts[changed_file] > 1:
            diagnostics.append(
                _diagnostic(
                    "artifact_delta_duplicate",
                    f"Changed file {changed_file} must have exactly one artifact delta.",
                    "worker_report.artifact_deltas",
                )
            )
            valid = False

    for index, delta in enumerate(deltas):
        path = f"worker_report.artifact_deltas[{index}]"
        if delta.get("kind") != "artifact_delta":
            diagnostics.append(
                _diagnostic(
                    "artifact_delta_kind_invalid",
                    "kind must be artifact_delta.",
                    f"{path}.kind",
                )
            )
            valid = False
        if not _has_text(delta.get("source_surface")):
            diagnostics.append(
                _diagnostic("artifact_delta_surface_missing", "source_surface is required.", path)
            )
            valid = False
        elif delta.get("source_surface") not in changed_files:
            diagnostics.append(
                _diagnostic(
                    "artifact_delta_unexpected",
                    "artifact_delta.source_surface must identify a changed file.",
                    f"{path}.source_surface",
                )
            )
            valid = False
        if not _has_evidence(delta.get("changed_locators")):
            diagnostics.append(
                _diagnostic(
                    "artifact_delta_locators_missing",
                    "changed_locators must not be empty.",
                    f"{path}.changed_locators",
                )
            )
            valid = False
        if not _has_text(delta.get("semantic_summary")):
            diagnostics.append(
                _diagnostic(
                    "artifact_delta_summary_missing",
                    "semantic_summary is required.",
                    f"{path}.semantic_summary",
                )
            )
            valid = False
        digest = delta.get("baseline_digest")
        if digest != "absent" and not (_has_text(digest) and DIGEST_PATTERN.fullmatch(digest)):
            diagnostics.append(
                _diagnostic(
                    "artifact_delta_digest_invalid",
                    "baseline_digest must be absent or sha256:<64 lowercase hex>.",
                    f"{path}.baseline_digest",
                )
            )
            valid = False
    return valid


def _validate_worker_report(manifest: Payload, diagnostics: List[Diagnostic]) -> bool:
    report = _mapping(manifest.get("worker_report"))
    valid = True
    if report.get("status") not in REPORT_STATUSES:
        diagnostics.append(
            _diagnostic(
                "worker_report_status_invalid",
                "worker_report.status is missing or invalid.",
                "worker_report.status",
            )
        )
        valid = False
    if report.get("execution_mode") != manifest.get("execution_mode"):
        diagnostics.append(
            _diagnostic(
                "worker_report_execution_mode_invalid",
                "worker_report.execution_mode must match manifest.execution_mode.",
                "worker_report.execution_mode",
            )
        )
        valid = False
    if report.get("scope_check") != "within_scope":
        valid = False
    if report.get("forbidden_change_check") != "none":
        valid = False
    verification = _mapping(report.get("verification"))
    if verification.get("status") != "pass" or not _has_evidence(verification.get("evidence")):
        valid = False
    return _validate_artifact_deltas(report, diagnostics) and valid


def _validate_sync(
    name: str,
    payload: Payload,
    diagnostics: List[Diagnostic],
) -> bool:
    disposition = payload.get("disposition")
    state = payload.get("state")
    path = f"keystone_closure.{name}"
    valid = True
    if disposition not in SYNC_DISPOSITIONS:
        diagnostics.append(
            _diagnostic(
                f"{name}_disposition_invalid",
                "Sync disposition must be required, not_applicable, or deferred.",
                f"{path}.disposition",
            )
        )
        return False
    if not _has_text(payload.get("reason")):
        diagnostics.append(
            _diagnostic(
                f"{name}_reason_missing",
                "Every sync disposition requires a concrete reason.",
                f"{path}.reason",
            )
        )
        valid = False
    if not _has_evidence(payload.get("evidence")):
        diagnostics.append(
            _diagnostic(
                f"{name}_evidence_missing",
                "Every sync disposition requires evidence.",
                f"{path}.evidence",
            )
        )
        valid = False

    complete_state = "verified" if name == "graph_sync" else "complete"
    expected_states = {
        "required": {complete_state},
        "not_applicable": {"not_applicable"},
        "deferred": {"pending", "blocked"},
    }
    if state not in expected_states[disposition]:
        diagnostics.append(
            _diagnostic(
                f"{name}_incomplete",
                f"{name} disposition {disposition} is incompatible with state {state!r}.",
                f"{path}.state",
            )
        )
        valid = False
    return valid and disposition != "deferred"


def _validate_closure(manifest: Payload, diagnostics: List[Diagnostic]) -> bool:
    closure = _mapping(manifest.get("keystone_closure"))
    results = []
    for name in ("document_sync", "metadata_sync", "graph_sync"):
        results.append(_validate_sync(name, _mapping(closure.get(name)), diagnostics))
    return all(results)


def _validate_review(
    manifest: Payload,
    context_ready: bool,
    report_ready: bool,
    closure_ready: bool,
    diagnostics: List[Diagnostic],
) -> None:
    phase = manifest.get("closure_phase")
    review = _mapping(manifest.get("coordinator_review"))
    decision = review.get("decision")
    closure = _mapping(manifest.get("keystone_closure"))
    finalization = _mapping(closure.get("finalization"))
    report = _mapping(manifest.get("worker_report"))
    report_ready_for_acceptance = (
        report_ready and report.get("status") == ACCEPT_CANDIDATE_REPORT_STATUS
    )

    if phase not in CLOSURE_PHASES:
        diagnostics.append(
            _diagnostic(
                "closure_phase_invalid",
                "closure_phase must be pre_acceptance or post_acceptance.",
                "closure_phase",
            )
        )
        return

    if not _has_evidence(review.get("evidence")):
        diagnostics.append(
            _diagnostic(
                "coordinator_review_evidence_missing",
                "Coordinator review requires evidence.",
                "coordinator_review.evidence",
            )
        )

    if phase == "pre_acceptance":
        if decision not in PRE_ACCEPTANCE_DECISIONS:
            diagnostics.append(
                _diagnostic(
                    "coordinator_decision_invalid",
                    "Invalid pre-acceptance Coordinator decision.",
                    "coordinator_review.decision",
                )
            )
            return
        ready = context_ready and report_ready_for_acceptance and closure_ready
        if decision == "accept_candidate" and report.get("status") != ACCEPT_CANDIDATE_REPORT_STATUS:
            diagnostics.append(
                _diagnostic(
                    "worker_report_not_ready_for_acceptance",
                    "accept_candidate requires worker_report.status DONE without unresolved concerns.",
                    "worker_report.status",
                )
            )
        if decision == "accept_candidate" and not ready:
            diagnostics.append(
                _diagnostic(
                    "accept_candidate_not_ready",
                    "accept_candidate requires complete context, report, verification, "
                    "and sync closure.",
                    "coordinator_review.decision",
                )
            )
        if review.get("main_acceptance_allowed") is True and decision != "accept_candidate":
            diagnostics.append(
                _diagnostic(
                    "main_acceptance_gate_invalid",
                    "Main acceptance may be allowed only for an accept candidate.",
                    "coordinator_review.main_acceptance_allowed",
                )
            )
        if decision == "accept_candidate" and review.get("main_acceptance_allowed") is not True:
            diagnostics.append(
                _diagnostic(
                    "main_acceptance_gate_invalid",
                    "An accept candidate must explicitly allow Main acceptance.",
                    "coordinator_review.main_acceptance_allowed",
                )
            )
        if finalization.get("state") not in {"not_started", "in_progress"}:
            diagnostics.append(
                _diagnostic(
                    "pre_acceptance_finalization_invalid",
                    "Pre-acceptance finalization must be not_started or in_progress.",
                    "keystone_closure.finalization.state",
                )
            )
        return

    if decision not in POST_ACCEPTANCE_DECISIONS:
        diagnostics.append(
            _diagnostic(
                "coordinator_decision_invalid",
                "Invalid post-acceptance Coordinator decision.",
                "coordinator_review.decision",
            )
        )
        return
    if not _has_text(closure.get("acceptance_ref")):
        diagnostics.append(
            _diagnostic(
                "acceptance_ref_missing",
                "Every post-acceptance closure record requires an acceptance_ref.",
                "keystone_closure.acceptance_ref",
            )
        )
    if not _has_evidence(closure.get("acceptance_evidence")):
        diagnostics.append(
            _diagnostic(
                "acceptance_evidence_missing",
                "Every post-acceptance closure record requires acceptance evidence.",
                "keystone_closure.acceptance_evidence",
            )
        )
    if decision == "closure_complete":
        if (
            not context_ready
            or not report_ready_for_acceptance
            or not closure_ready
            or finalization.get("state") not in {"complete", "waived"}
        ):
            diagnostics.append(
                _diagnostic(
                    "post_acceptance_closure_incomplete",
                    "closure_complete requires closed sync and complete or waived finalization.",
                    "coordinator_review.decision",
                )
            )
        if not _has_evidence(finalization.get("evidence")):
            diagnostics.append(
                _diagnostic(
                    "finalization_evidence_missing",
                    "Completed finalization requires evidence.",
                    "keystone_closure.finalization.evidence",
                )
            )
        if not _has_text(finalization.get("acceptance_ref")):
            diagnostics.append(
                _diagnostic(
                    "finalization_acceptance_ref_missing",
                    "Post-acceptance finalization requires an acceptance_ref.",
                    "keystone_closure.finalization.acceptance_ref",
                )
            )
        if finalization.get("state") == "waived" and not _has_text(finalization.get("waiver_reason")):
            diagnostics.append(
                _diagnostic(
                    "finalization_waiver_reason_missing",
                    "Waived finalization requires a concrete waiver_reason.",
                    "keystone_closure.finalization.waiver_reason",
                )
            )
        if review.get("main_acceptance_allowed") is not False:
            diagnostics.append(
                _diagnostic(
                    "main_acceptance_gate_invalid",
                    "Post-acceptance closure must not reopen Main acceptance.",
                    "coordinator_review.main_acceptance_allowed",
                )
            )


def validate_manifest(manifest: Any) -> Dict[str, Any]:
    diagnostics: List[Diagnostic] = []
    if not isinstance(manifest, Mapping):
        diagnostics.append(
            _diagnostic("manifest_invalid", "Manifest root must be an object.", "$")
        )
    else:
        _validate_schema(manifest, diagnostics)
        _validate_execution_mode(manifest, diagnostics)
        context_ready = _validate_context_pack(manifest, diagnostics)
        report_ready = _validate_worker_report(manifest, diagnostics)
        closure_ready = _validate_closure(manifest, diagnostics)
        _validate_review(manifest, context_ready, report_ready, closure_ready, diagnostics)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not diagnostics else "fail",
        "diagnostics": diagnostics,
        "summary": {"errors": len(diagnostics), "warnings": 0},
    }


def _error_result(code: str, message: str) -> Dict[str, Any]:
    diagnostic = _diagnostic(code, message, "manifest")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "error",
        "diagnostics": [diagnostic],
        "summary": {"errors": 1, "warnings": 0},
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        result = _error_result("manifest_unreadable", str(exc))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2
    except json.JSONDecodeError as exc:
        result = _error_result("manifest_json_invalid", str(exc))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2

    result = validate_manifest(manifest)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
