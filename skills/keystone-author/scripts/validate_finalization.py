#!/usr/bin/env python3
"""Validate Keystone acceptance-finalization evidence without editing sources."""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ACTIVE_STATUSES = {"ready", "in_progress", "assigned", "reported", "reviewing", "verifying"}
REQUIRED_IMPACT_CATEGORIES = {
    "progress",
    "work_order_change_set",
    "work_index",
    "round_index",
    "root_index",
    "context_map",
    "standard_decision_plan",
    "recovery",
    "implementation_gate",
    "residual_risk",
    "namespace",
}
REQUIRED_FINALIZATION_EVIDENCE = {
    "main_acceptance",
    "impact_dispositions",
    "source_updates",
    "semantic_review",
}
ACTIVE_SOURCE_CATEGORIES = {"work_index", "round_index", "context_map"}
FINALIZATION_STATES = {"pending", "in_progress", "complete", "waived"}
DISPOSITIONS = {
    "updated",
    "no_change_required",
    "historical",
    "out_of_scope",
    "clarification_required",
    "integration_gate",
}
PATH_REQUIRED_DISPOSITIONS = {"updated", "no_change_required", "historical"}
SINGULAR_CURRENT_STEP_PATTERNS = (
    re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:현재\s*단계|current(?:\s+step|_step))\s*(?::|은|는)"),
    re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:현재\s+작업|실행\s+상태)\s*(?::|은|는)\s*S\d+"),
    re.compile(r"(?im)^\s*(?:[-*]\s*)?S\d+\s*부터\s*진행"),
    re.compile(r"(?im)^\s*(?:[-*]\s*)?Worker\s+S\d+(?:-[A-Z0-9]+)*\b"),
)
STEP_REF_PATTERN = r"R\d+/S\d+(?:-[A-Z0-9]+)*"


def diagnostic(code: str, message: str, path: Optional[str] = None) -> Dict[str, str]:
    item = {"severity": "error", "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def output(status: str, diagnostics: List[Dict[str, str]]) -> None:
    payload = {
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


def resolve_scoped_path(root: Path, value: Any) -> Tuple[Optional[Path], Optional[str]]:
    if not isinstance(value, str) or not value.strip():
        return None, "missing"
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, "outside"
    return candidate, None


def read_scoped_file(root: Path, value: Any) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    path, path_error = resolve_scoped_path(root, value)
    if path_error:
        return None, path_error, None
    if path is None or not path.is_file():
        return None, "unavailable", None
    try:
        return path.read_text(encoding="utf-8"), None, str(value)
    except (OSError, UnicodeError):
        return None, "unreadable", str(value)


def scalar_from_text(content: str, field: str) -> Optional[str]:
    match = re.search(rf"(?m)^\s*{re.escape(field)}\s*:\s*['\"]?([^\n'\"]+)['\"]?\s*$", content)
    return match.group(1).strip() if match else None


def finalization_scalar(content: str, field: str) -> Optional[str]:
    block = re.search(r"(?ms)^finalization:\s*\n((?:^[ \t]+.*\n?)*)", content)
    return scalar_from_text(block.group(1), field) if block else None


def active_steps_from_text(content: str) -> Optional[List[str]]:
    match = re.search(r"(?im)^\s*(?:[-*]\s*)?(?:active[_ ]steps|현재\s*active[_ ]steps)\s*:\s*([^\n]+)$", content)
    if not match:
        return None
    return re.findall(STEP_REF_PATTERN, match.group(1))


def validate_manifest(root: Path, manifest: Dict[str, Any]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []

    schema_version = manifest.get("schema_version")
    if schema_version not in {1, 2}:
        findings.append(diagnostic("schema_version_unsupported", "schema_version must be 1 or 2."))

    if not isinstance(manifest.get("acceptance_ref"), str) or not manifest["acceptance_ref"].strip():
        findings.append(diagnostic("acceptance_ref_missing", "acceptance_ref must be a non-empty string."))

    raw_steps = manifest.get("steps")
    steps: Dict[str, Dict[str, Any]] = {}
    if not isinstance(raw_steps, list):
        findings.append(diagnostic("steps_invalid", "steps must be an array."))
        raw_steps = []
    for index, step in enumerate(raw_steps):
        if not isinstance(step, dict) or not isinstance(step.get("ref"), str):
            findings.append(diagnostic("step_ref_missing", f"steps[{index}] requires ref."))
            continue
        ref = step["ref"]
        if ref in steps:
            findings.append(diagnostic("step_ref_duplicate", f"Step ref is duplicated: {ref}."))
        steps[ref] = step
        path, path_error = resolve_scoped_path(root, step.get("progress_path"))
        if path_error == "missing":
            findings.append(diagnostic("step_progress_path_missing", f"Step {ref} requires progress_path."))
        elif path_error == "outside":
            findings.append(diagnostic("step_progress_path_outside_root", f"Step {ref} path escapes root."))
        elif path is not None and not path.is_file():
            findings.append(diagnostic("step_progress_path_unavailable", f"Step {ref} progress_path is unavailable.", step.get("progress_path")))
        elif path is not None:
            try:
                source_status = scalar_from_text(path.read_text(encoding="utf-8"), "work_status")
            except (OSError, UnicodeError):
                source_status = None
            if source_status is None:
                findings.append(diagnostic("step_status_source_missing", f"Step {ref} progress has no work_status.", step.get("progress_path")))
            elif source_status != step.get("status"):
                findings.append(diagnostic("step_status_source_mismatch", f"Step {ref} manifest status {step.get('status')} differs from source {source_status}.", step.get("progress_path")))
            source_step_ref = scalar_from_text(path.read_text(encoding="utf-8"), "step_ref")
            source_work_ref = scalar_from_text(path.read_text(encoding="utf-8"), "work_ref")
            if source_step_ref != ref:
                findings.append(diagnostic("step_ref_source_mismatch", f"Step ref {ref} differs from source {source_step_ref}.", step.get("progress_path")))
            if source_work_ref != step.get("work_ref"):
                findings.append(diagnostic("step_work_ref_source_mismatch", f"Step work_ref {step.get('work_ref')} differs from source {source_work_ref}.", step.get("progress_path")))

    raw_active = manifest.get("active_steps")
    if not isinstance(raw_active, list):
        findings.append(diagnostic("active_steps_invalid", "active_steps must be an array."))
        raw_active = []
    seen_active = set()
    for ref in raw_active:
        if not isinstance(ref, str):
            findings.append(diagnostic("active_step_ref_invalid", "Each active_steps entry must be a step ref string."))
            continue
        if ref in seen_active:
            findings.append(diagnostic("active_step_duplicate", f"Active step is duplicated: {ref}."))
        seen_active.add(ref)
        step = steps.get(ref)
        if step is None:
            findings.append(diagnostic("active_step_unresolved", f"Active step is not declared in steps: {ref}."))
        elif step.get("status") not in ACTIVE_STATUSES:
            findings.append(diagnostic("active_step_status_invalid", f"Active step {ref} has non-active status: {step.get('status')}."))

    raw_active_sources = manifest.get("active_step_sources")
    if not isinstance(raw_active_sources, list) or not raw_active_sources:
        findings.append(diagnostic("active_step_sources_missing", "active_step_sources must contain at least one source path."))
    else:
        expected_active = sorted(ref for ref in raw_active if isinstance(ref, str))
        observed_source_categories = set()
        for source in raw_active_sources:
            if not isinstance(source, dict):
                findings.append(diagnostic("active_step_source_invalid", "Each active_step_sources entry must be an object."))
                continue
            category = source.get("category")
            if isinstance(category, str):
                observed_source_categories.add(category)
            content, error, source_path = read_scoped_file(root, source.get("path"))
            if error:
                findings.append(diagnostic("active_steps_source_unavailable", f"Cannot read active-step source: {error}.", str(source.get("path"))))
                continue
            actual_active = active_steps_from_text(content or "")
            if actual_active is None:
                findings.append(diagnostic("active_steps_source_missing", "Source has no active_steps representation.", source_path))
            elif sorted(actual_active) != expected_active:
                findings.append(diagnostic("active_steps_source_mismatch", f"Source active_steps {actual_active} differs from manifest {expected_active}.", source_path))
        for missing in sorted(ACTIVE_SOURCE_CATEGORIES - observed_source_categories):
            findings.append(diagnostic("active_step_source_category_missing", f"Required active-step source category is missing: {missing}."))

    for ref, step in steps.items():
        if step.get("status") in ACTIVE_STATUSES and ref not in seen_active:
            findings.append(diagnostic("active_step_omitted", f"Declared active-status Step is omitted from active_steps: {ref}."))

    raw_accepted = manifest.get("accepted_steps")
    if not isinstance(raw_accepted, list) or not raw_accepted:
        findings.append(diagnostic("accepted_steps_missing", "accepted_steps must contain the Steps accepted by Main."))
        raw_accepted = []
    accepted_steps = {ref for ref in raw_accepted if isinstance(ref, str)}
    for ref in accepted_steps:
        if ref not in steps:
            findings.append(diagnostic("accepted_step_unresolved", f"Accepted Step is not declared: {ref}."))

    transitions = manifest.get("status_transitions")
    if not isinstance(transitions, list):
        findings.append(diagnostic("status_transitions_invalid", "status_transitions must be an array."))
        transitions = []
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict):
            findings.append(diagnostic("status_transition_invalid", f"status_transitions[{index}] must be an object."))
            continue
        if transition.get("kind") != "step":
            findings.append(diagnostic("status_transition_kind_invalid", f"status_transitions[{index}] kind must be 'step'."))
            continue
        if transition.get("ref") not in accepted_steps:
            findings.append(diagnostic("direct_step_transition_not_accepted", f"Direct Step transition is not backed by Main acceptance: {transition.get('ref')}."))
        if transition.get("from") != "in_progress" or transition.get("to") != "accepted":
            findings.append(diagnostic("direct_step_transition_invalid", f"Accepted Step transition must be in_progress -> accepted: {transition.get('ref')}."))
    transition_refs = [item.get("ref") for item in transitions if isinstance(item, dict) and item.get("kind") == "step"]
    for ref in accepted_steps:
        if transition_refs.count(ref) != 1:
            findings.append(diagnostic("accepted_step_transition_count_invalid", f"Accepted Step {ref} requires exactly one direct transition."))

    finalization = manifest.get("finalization")
    if not isinstance(finalization, dict) or finalization.get("required") is not True:
        findings.append(diagnostic("finalization_required_missing", "finalization.required must be true for acceptance finalization."))
    else:
        if finalization.get("state") not in FINALIZATION_STATES:
            findings.append(diagnostic("finalization_state_invalid", f"Unsupported finalization state: {finalization.get('state')}."))
        evidence = finalization.get("evidence")
        evidence_set = set(evidence) if isinstance(evidence, list) else set()
        for missing in sorted(REQUIRED_FINALIZATION_EVIDENCE - evidence_set):
            findings.append(diagnostic("finalization_evidence_missing", f"Required finalization evidence is missing: {missing}."))
        if finalization.get("state") == "complete" and "post_edit_verification" not in evidence_set:
            findings.append(diagnostic("finalization_evidence_missing", "Complete finalization requires post_edit_verification."))
        content, error, source_path = read_scoped_file(root, finalization.get("progress_path"))
        if error:
            findings.append(diagnostic("finalization_source_unavailable", f"Cannot read finalization progress: {error}.", str(finalization.get("progress_path"))))
        else:
            source_state = finalization_scalar(content or "", "state")
            source_acceptance = finalization_scalar(content or "", "acceptance_ref")
            if source_state != finalization.get("state"):
                findings.append(diagnostic("finalization_state_source_mismatch", f"Source finalization state {source_state} differs from manifest {finalization.get('state')}.", source_path))
            if source_acceptance != manifest.get("acceptance_ref"):
                findings.append(diagnostic("finalization_acceptance_source_mismatch", "Source finalization acceptance_ref differs from manifest.", source_path))

    if schema_version == 1:
        if "graph_sync" in manifest:
            findings.append(diagnostic(
                "legacy_schema_graph_sync_forbidden",
                "schema_version 1 cannot declare graph synchronization; use schema_version 2.",
            ))
        state = finalization.get("state") if isinstance(finalization, dict) else None
        if state == "complete":
            findings.append(diagnostic(
                "legacy_schema_complete_forbidden",
                "schema_version 1 cannot approve complete finalization; use schema_version 2.",
            ))

    if schema_version == 2:
        graph_sync = manifest.get("graph_sync")
        if not isinstance(graph_sync, dict):
            findings.append(diagnostic("graph_sync_missing", "schema_version 2 requires graph_sync assessment."))
        else:
            disposition = graph_sync.get("disposition")
            required = graph_sync.get("required")
            if disposition not in {"required", "not_applicable", "deferred"}:
                findings.append(diagnostic("graph_sync_disposition_invalid", "graph_sync disposition is invalid."))
            if not isinstance(graph_sync.get("reason"), str) or not graph_sync["reason"].strip():
                findings.append(diagnostic("graph_sync_reason_missing", "graph_sync requires a non-empty reason."))
            expected_required = disposition in {"required", "deferred"}
            if not isinstance(required, bool) or required is not expected_required:
                findings.append(diagnostic("graph_sync_required_mismatch", "graph_sync.required does not match its disposition."))
            state = finalization.get("state") if isinstance(finalization, dict) else None
            graph_path = graph_sync.get("validation_manifest_path")
            transaction_id = graph_sync.get("transaction_id")
            if graph_path is not None and (not isinstance(graph_path, str) or not graph_path.strip()):
                findings.append(diagnostic("graph_sync_evidence_malformed", "graph_sync validation_manifest_path must be a non-empty string."))
            if transaction_id is not None and (not isinstance(transaction_id, str) or not transaction_id.strip()):
                findings.append(diagnostic("graph_sync_evidence_malformed", "graph_sync transaction_id must be a non-empty string."))
            if disposition == "not_applicable" and (graph_path is not None or transaction_id is not None):
                findings.append(diagnostic("graph_sync_evidence_unexpected", "not_applicable graph synchronization must not declare transaction evidence."))
            if state == "complete" and disposition == "deferred":
                findings.append(diagnostic("graph_sync_deferred", "Deferred graph synchronization blocks complete finalization."))
            if state == "complete" and disposition == "required":
                if not isinstance(graph_path, str) or not graph_path.strip() or not isinstance(transaction_id, str) or not transaction_id.strip():
                    findings.append(diagnostic("graph_sync_evidence_missing", "Complete finalization requires a graph validation manifest and transaction_id."))
                else:
                    content, error, source_path = read_scoped_file(root, graph_path)
                    if error:
                        findings.append(diagnostic("graph_sync_evidence_unavailable", f"Cannot read graph validation manifest: {error}.", graph_path))
                    else:
                        try:
                            graph_manifest = json.loads(content or "")
                        except json.JSONDecodeError:
                            graph_manifest = None
                        graph_transaction = graph_manifest.get("transaction") if isinstance(graph_manifest, dict) else None
                        if not isinstance(graph_transaction, dict):
                            findings.append(diagnostic("graph_sync_evidence_malformed", "Graph validation manifest requires an inline transaction.", source_path))
                        elif graph_transaction.get("transaction_id") != transaction_id:
                            findings.append(diagnostic("graph_sync_transaction_mismatch", "graph_sync transaction_id differs from the graph validation manifest.", source_path))
                        elif graph_transaction.get("state") != "verified":
                            findings.append(diagnostic(
                                "graph_sync_transaction_not_verified",
                                "Complete finalization requires the bound graph transaction state to be verified.",
                                source_path,
                            ))

    raw_early_work = manifest.get("early_work")
    if not isinstance(raw_early_work, list):
        findings.append(diagnostic("early_work_invalid", "early_work must be an array."))
        raw_early_work = []
    for index, entry in enumerate(raw_early_work):
        if not isinstance(entry, dict):
            findings.append(diagnostic("early_work_entry_invalid", f"early_work[{index}] must be an object."))
            continue
        target = entry.get("target_step")
        if target not in steps:
            findings.append(diagnostic("early_work_target_unresolved", f"early_work[{index}] target_step is unresolved: {target}."))
        if entry.get("status_effect") != "none":
            findings.append(diagnostic("early_work_status_effect_invalid", f"early_work[{index}] must use status_effect 'none'."))
        for field in ("cause", "completed_scope", "remaining_scope"):
            value = entry.get(field)
            valid = isinstance(value, str) and bool(value.strip()) if field == "cause" else isinstance(value, list) and bool(value)
            if not valid:
                findings.append(diagnostic("early_work_trace_missing", f"early_work[{index}] requires non-empty {field}."))

    raw_candidates = manifest.get("impact_candidates")
    if not isinstance(raw_candidates, list):
        findings.append(diagnostic("impact_candidates_invalid", "impact_candidates must be an array."))
        raw_candidates = []
    observed_categories = set()
    for index, candidate in enumerate(raw_candidates):
        if not isinstance(candidate, dict):
            findings.append(diagnostic("candidate_invalid", f"impact_candidates[{index}] must be an object."))
            continue
        disposition = candidate.get("disposition")
        category = candidate.get("category")
        if isinstance(category, str):
            observed_categories.add(category)
        else:
            findings.append(diagnostic("candidate_category_missing", f"impact_candidates[{index}] requires a category."))
        if disposition not in DISPOSITIONS:
            findings.append(diagnostic("candidate_disposition_invalid", f"impact_candidates[{index}] has an invalid disposition."))
        reason = candidate.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            findings.append(diagnostic("candidate_reason_missing", f"impact_candidates[{index}] requires a reason."))
        if category == "implementation_gate":
            if candidate.get("gate_state") not in {"resolved", "residual", "not_applicable"} or not isinstance(candidate.get("gate_scope"), str) or not candidate["gate_scope"].strip():
                findings.append(diagnostic("implementation_gate_assessment_invalid", "implementation_gate requires gate_state and gate_scope."))
        elif category == "residual_risk":
            risk_items = candidate.get("risk_items")
            if candidate.get("risk_state") not in {"none", "recorded"} or not isinstance(risk_items, list) or (candidate.get("risk_state") == "recorded" and not risk_items):
                findings.append(diagnostic("residual_risk_assessment_invalid", "residual_risk requires risk_state and risk_items."))
        elif category == "namespace":
            if candidate.get("namespace_state") not in {"checked", "conflict", "not_applicable"}:
                findings.append(diagnostic("namespace_assessment_invalid", "namespace requires namespace_state."))

        path_value = candidate.get("path")
        if disposition not in PATH_REQUIRED_DISPOSITIONS and path_value is None:
            continue
        path, path_error = resolve_scoped_path(root, path_value)
        if path_error == "missing":
            findings.append(diagnostic("candidate_path_missing", f"impact_candidates[{index}] requires a path."))
            continue
        if path_error == "outside":
            findings.append(diagnostic("candidate_path_outside_root", f"impact_candidates[{index}] path escapes root."))
            continue
        if path is None or not path.is_file():
            findings.append(diagnostic("candidate_path_unavailable", f"impact_candidates[{index}] path is unavailable.", path_value))
            continue
        if disposition == "historical" or path.suffix.lower() != ".md":
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            findings.append(diagnostic("candidate_path_unreadable", f"Cannot read candidate: {error}", path_value))
            continue
        if any(pattern.search(content) for pattern in SINGULAR_CURRENT_STEP_PATTERNS):
            findings.append(diagnostic("singular_current_step_claim", "Live candidate contains a singular current-step claim; use active_steps.", path_value))
    for missing in sorted(REQUIRED_IMPACT_CATEGORIES - observed_categories):
        findings.append(diagnostic("impact_category_missing", f"Required impact category is missing: {missing}."))

    raw_namespaces = manifest.get("namespace_entries")
    if not isinstance(raw_namespaces, list):
        findings.append(diagnostic("namespace_entries_invalid", "namespace_entries must be an array."))
        raw_namespaces = []
    owners_by_name: Dict[Tuple[str, str], set] = defaultdict(set)
    for index, entry in enumerate(raw_namespaces):
        if not isinstance(entry, dict) or not all(isinstance(entry.get(field), str) and entry[field].strip() for field in ("namespace", "value", "owner")):
            findings.append(diagnostic("namespace_entry_invalid", f"namespace_entries[{index}] requires namespace, value, and owner."))
            continue
        owners_by_name[(entry["namespace"], entry["value"])].add(entry["owner"])
    for (namespace, value), owners in sorted(owners_by_name.items()):
        if len(owners) > 1:
            findings.append(diagnostic("namespace_collision", f"{namespace}:{value} is claimed by multiple owners: {', '.join(sorted(owners))}."))

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
