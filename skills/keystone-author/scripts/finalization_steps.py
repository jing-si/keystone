"""Step, active-source, transition, and early-work finalization validation."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

from finalization_support import (
    active_steps_from_text,
    approval_scalar,
    diagnostic,
    read_scoped_file,
    resolve_scoped_path,
    scalar_from_text,
)


LEGACY_ACTIVE_STATUSES = {
    "ready", "in_progress", "assigned", "reported", "reviewing", "verifying",
}
WORK_STATUSES = {
    "planned", "in_progress", "blocked", "complete", "cancelled", "superseded",
}
ACTIVE_WORK_STATUSES = {"in_progress", "blocked"}
APPROVAL_STATES = {"pending", "accepted", "rejected"}
ACTIVE_SOURCE_CATEGORIES = {"work_index", "round_index", "context_map"}


def validate_steps_and_transitions(
        root: Path, manifest: Dict[str, Any], schema_version: Any,
) -> Tuple[List[Dict[str, str]], Dict[str, Dict[str, Any]]]:
    """Validate Step sources and transitions, returning declared Steps for later gates."""
    findings: List[Dict[str, str]] = []
    raw_steps = manifest.get("steps")
    steps: Dict[str, Dict[str, Any]] = {}
    if not isinstance(raw_steps, list):
        findings.append(diagnostic("steps_invalid", "steps must be an array."))
        raw_steps = []
    for index, step in enumerate(raw_steps):
        if not isinstance(step, dict) or not isinstance(step.get("ref"), str):
            findings.append(diagnostic(
                "step_ref_missing", f"steps[{index}] requires ref."
            ))
            continue
        ref = step["ref"]
        if ref in steps:
            findings.append(diagnostic(
                "step_ref_duplicate", f"Step ref is duplicated: {ref}."
            ))
        steps[ref] = step
        path, path_error = resolve_scoped_path(root, step.get("progress_path"))
        if path_error == "missing":
            findings.append(diagnostic(
                "step_progress_path_missing", f"Step {ref} requires progress_path."
            ))
        elif path_error == "outside":
            findings.append(diagnostic(
                "step_progress_path_outside_root", f"Step {ref} path escapes root."
            ))
        elif path is not None and not path.is_file():
            findings.append(diagnostic(
                "step_progress_path_unavailable",
                f"Step {ref} progress_path is unavailable.",
                step.get("progress_path"),
            ))
        elif path is not None:
            try:
                progress_content = path.read_text(encoding="utf-8")
                source_status = scalar_from_text(progress_content, "work_status")
            except (OSError, UnicodeError):
                progress_content = ""
                source_status = None
            if source_status is None:
                findings.append(diagnostic(
                    "step_status_source_missing",
                    f"Step {ref} progress has no work_status.",
                    step.get("progress_path"),
                ))
            elif source_status != step.get("status"):
                findings.append(diagnostic(
                    "step_status_source_mismatch",
                    f"Step {ref} manifest status {step.get('status')} differs "
                    f"from source {source_status}.",
                    step.get("progress_path"),
                ))
            if schema_version == 3:
                if step.get("status") not in WORK_STATUSES:
                    findings.append(diagnostic(
                        "step_work_status_invalid",
                        f"Step {ref} has unsupported work status: {step.get('status')}.",
                    ))
                source_approval = approval_scalar(progress_content, "state")
                manifest_approval = step.get("approval_state")
                if manifest_approval not in APPROVAL_STATES:
                    findings.append(diagnostic(
                        "step_approval_state_invalid",
                        f"Step {ref} requires a valid approval_state.",
                    ))
                elif source_approval != manifest_approval:
                    findings.append(diagnostic(
                        "step_approval_source_mismatch",
                        f"Step {ref} manifest approval {manifest_approval} differs "
                        f"from source {source_approval}.",
                        step.get("progress_path"),
                    ))
            source_step_ref = scalar_from_text(progress_content, "step_ref")
            source_work_ref = scalar_from_text(progress_content, "work_ref")
            if source_step_ref != ref:
                findings.append(diagnostic(
                    "step_ref_source_mismatch",
                    f"Step ref {ref} differs from source {source_step_ref}.",
                    step.get("progress_path"),
                ))
            if source_work_ref != step.get("work_ref"):
                findings.append(diagnostic(
                    "step_work_ref_source_mismatch",
                    f"Step work_ref {step.get('work_ref')} differs from source "
                    f"{source_work_ref}.",
                    step.get("progress_path"),
                ))

    raw_active = manifest.get("active_steps")
    if not isinstance(raw_active, list):
        findings.append(diagnostic("active_steps_invalid", "active_steps must be an array."))
        raw_active = []
    seen_active = set()
    for ref in raw_active:
        if not isinstance(ref, str):
            findings.append(diagnostic(
                "active_step_ref_invalid",
                "Each active_steps entry must be a step ref string.",
            ))
            continue
        if ref in seen_active:
            findings.append(diagnostic(
                "active_step_duplicate", f"Active step is duplicated: {ref}."
            ))
        seen_active.add(ref)
        step = steps.get(ref)
        if step is None:
            findings.append(diagnostic(
                "active_step_unresolved",
                f"Active step is not declared in steps: {ref}.",
            ))
        elif step.get("status") not in (
                ACTIVE_WORK_STATUSES if schema_version == 3 else LEGACY_ACTIVE_STATUSES):
            findings.append(diagnostic(
                "active_step_status_invalid",
                f"Active step {ref} has non-active status: {step.get('status')}.",
            ))

    raw_active_sources = manifest.get("active_step_sources")
    if not isinstance(raw_active_sources, list) or not raw_active_sources:
        findings.append(diagnostic(
            "active_step_sources_missing",
            "active_step_sources must contain at least one source path.",
        ))
    else:
        expected_active = sorted(ref for ref in raw_active if isinstance(ref, str))
        observed_source_categories = set()
        for source in raw_active_sources:
            if not isinstance(source, dict):
                findings.append(diagnostic(
                    "active_step_source_invalid",
                    "Each active_step_sources entry must be an object.",
                ))
                continue
            category = source.get("category")
            if isinstance(category, str):
                observed_source_categories.add(category)
            content, error, source_path = read_scoped_file(root, source.get("path"))
            if error:
                findings.append(diagnostic(
                    "active_steps_source_unavailable",
                    f"Cannot read active-step source: {error}.",
                    str(source.get("path")),
                ))
                continue
            actual_active = active_steps_from_text(content or "")
            if actual_active is None:
                findings.append(diagnostic(
                    "active_steps_source_missing",
                    "Source has no active_steps representation.",
                    source_path,
                ))
            elif sorted(actual_active) != expected_active:
                findings.append(diagnostic(
                    "active_steps_source_mismatch",
                    f"Source active_steps {actual_active} differs from manifest "
                    f"{expected_active}.",
                    source_path,
                ))
        for missing in sorted(ACTIVE_SOURCE_CATEGORIES - observed_source_categories):
            findings.append(diagnostic(
                "active_step_source_category_missing",
                f"Required active-step source category is missing: {missing}.",
            ))

    for ref, step in steps.items():
        active_statuses = (
            ACTIVE_WORK_STATUSES if schema_version == 3 else LEGACY_ACTIVE_STATUSES
        )
        if step.get("status") in active_statuses and ref not in seen_active:
            findings.append(diagnostic(
                "active_step_omitted",
                f"Declared active-status Step is omitted from active_steps: {ref}.",
            ))

    raw_accepted = manifest.get("accepted_steps")
    if not isinstance(raw_accepted, list) or not raw_accepted:
        findings.append(diagnostic(
            "accepted_steps_missing",
            "accepted_steps must contain the Steps accepted by Main.",
        ))
        raw_accepted = []
    accepted_steps = {ref for ref in raw_accepted if isinstance(ref, str)}
    for ref in accepted_steps:
        if ref not in steps:
            findings.append(diagnostic(
                "accepted_step_unresolved", f"Accepted Step is not declared: {ref}."
            ))

    if schema_version == 3:
        _validate_schema_v3_transitions(manifest, accepted_steps, steps, findings)
    else:
        _validate_legacy_transitions(manifest, accepted_steps, findings)
    return findings, steps


def _validate_schema_v3_transitions(
        manifest: Dict[str, Any], accepted_steps: set,
        steps: Dict[str, Dict[str, Any]], findings: List[Dict[str, str]],
) -> None:
    if "status_transitions" in manifest:
        findings.append(diagnostic(
            "legacy_status_transitions_forbidden",
            "schema_version 3 separates execution_transitions and approval_transitions.",
        ))
    execution_transitions = manifest.get("execution_transitions")
    approval_transitions = manifest.get("approval_transitions")
    if not isinstance(execution_transitions, list):
        findings.append(diagnostic(
            "execution_transitions_invalid", "execution_transitions must be an array."
        ))
        execution_transitions = []
    if not isinstance(approval_transitions, list):
        findings.append(diagnostic(
            "approval_transitions_invalid", "approval_transitions must be an array."
        ))
        approval_transitions = []
    for index, transition in enumerate(execution_transitions):
        if not isinstance(transition, dict) or set(transition) != {"ref", "from", "to"}:
            findings.append(diagnostic(
                "execution_transition_invalid",
                f"execution_transitions[{index}] has an invalid shape.",
            ))
            continue
        if transition.get("ref") not in accepted_steps:
            findings.append(diagnostic(
                "execution_transition_not_accepted",
                "Execution transition is not backed by Main acceptance: "
                f"{transition.get('ref')}.",
            ))
        if transition.get("from") != "in_progress" or transition.get("to") != "complete":
            findings.append(diagnostic(
                "execution_transition_invalid",
                "Accepted Step execution must transition in_progress -> complete: "
                f"{transition.get('ref')}.",
            ))
    for index, transition in enumerate(approval_transitions):
        required_fields = {"ref", "from", "to", "evidence"}
        if not isinstance(transition, dict) or set(transition) != required_fields:
            findings.append(diagnostic(
                "approval_transition_invalid",
                f"approval_transitions[{index}] has an invalid shape.",
            ))
            continue
        if transition.get("ref") not in accepted_steps:
            findings.append(diagnostic(
                "approval_transition_not_accepted",
                "Approval transition is not backed by Main acceptance: "
                f"{transition.get('ref')}.",
            ))
        if transition.get("from") != "pending" or transition.get("to") != "accepted":
            findings.append(diagnostic(
                "approval_transition_invalid",
                "Accepted Step approval must transition pending -> accepted: "
                f"{transition.get('ref')}.",
            ))
        if not isinstance(transition.get("evidence"), str) or not transition["evidence"].strip():
            findings.append(diagnostic(
                "approval_transition_evidence_missing",
                f"Approval transition requires evidence: {transition.get('ref')}.",
            ))
    execution_refs = [
        item.get("ref") for item in execution_transitions if isinstance(item, dict)
    ]
    approval_refs = [
        item.get("ref") for item in approval_transitions if isinstance(item, dict)
    ]
    for ref in accepted_steps:
        step = steps.get(ref, {})
        if step.get("status") != "complete":
            findings.append(diagnostic(
                "accepted_step_not_complete",
                f"Accepted Step {ref} must have work_status complete.",
            ))
        if step.get("approval_state") != "accepted":
            findings.append(diagnostic(
                "accepted_step_approval_missing",
                f"Accepted Step {ref} must have approval_state accepted.",
            ))
        if execution_refs.count(ref) != 1:
            findings.append(diagnostic(
                "accepted_step_execution_transition_count_invalid",
                f"Accepted Step {ref} requires exactly one execution transition.",
            ))
        if approval_refs.count(ref) != 1:
            findings.append(diagnostic(
                "accepted_step_approval_transition_count_invalid",
                f"Accepted Step {ref} requires exactly one approval transition.",
            ))


def _validate_legacy_transitions(
        manifest: Dict[str, Any], accepted_steps: set,
        findings: List[Dict[str, str]],
) -> None:
    transitions = manifest.get("status_transitions")
    if not isinstance(transitions, list):
        findings.append(diagnostic(
            "status_transitions_invalid", "status_transitions must be an array."
        ))
        transitions = []
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict):
            findings.append(diagnostic(
                "status_transition_invalid",
                f"status_transitions[{index}] must be an object.",
            ))
            continue
        if transition.get("kind") != "step":
            findings.append(diagnostic(
                "status_transition_kind_invalid",
                f"status_transitions[{index}] kind must be 'step'.",
            ))
            continue
        if transition.get("ref") not in accepted_steps:
            findings.append(diagnostic(
                "direct_step_transition_not_accepted",
                "Direct Step transition is not backed by Main acceptance: "
                f"{transition.get('ref')}.",
            ))
        if transition.get("from") != "in_progress" or transition.get("to") != "accepted":
            findings.append(diagnostic(
                "direct_step_transition_invalid",
                "Accepted Step transition must be in_progress -> accepted: "
                f"{transition.get('ref')}.",
            ))
    transition_refs = [
        item.get("ref") for item in transitions
        if isinstance(item, dict) and item.get("kind") == "step"
    ]
    for ref in accepted_steps:
        if transition_refs.count(ref) != 1:
            findings.append(diagnostic(
                "accepted_step_transition_count_invalid",
                f"Accepted Step {ref} requires exactly one direct transition.",
            ))


def validate_early_work(raw_early_work: Any,
                        steps: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    """Validate early-work trace without changing the target Step status."""
    findings: List[Dict[str, str]] = []
    if not isinstance(raw_early_work, list):
        findings.append(diagnostic("early_work_invalid", "early_work must be an array."))
        raw_early_work = []
    for index, entry in enumerate(raw_early_work):
        if not isinstance(entry, dict):
            findings.append(diagnostic(
                "early_work_entry_invalid", f"early_work[{index}] must be an object."
            ))
            continue
        target = entry.get("target_step")
        if target not in steps:
            findings.append(diagnostic(
                "early_work_target_unresolved",
                f"early_work[{index}] target_step is unresolved: {target}.",
            ))
        if entry.get("status_effect") != "none":
            findings.append(diagnostic(
                "early_work_status_effect_invalid",
                f"early_work[{index}] must use status_effect 'none'.",
            ))
        for field in ("cause", "completed_scope", "remaining_scope"):
            value = entry.get(field)
            valid = (
                isinstance(value, str) and bool(value.strip())
                if field == "cause"
                else isinstance(value, list) and bool(value)
            )
            if not valid:
                findings.append(diagnostic(
                    "early_work_trace_missing",
                    f"early_work[{index}] requires non-empty {field}.",
                ))
    return findings
