"""Independent manifest-section validators for acceptance finalization."""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from finalization_support import (
    diagnostic,
    finalization_scalar,
    read_scoped_file,
    resolve_scoped_path,
)


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
FINALIZATION_STATES = {"pending", "in_progress", "complete", "waived"}
LEGACY_DISPOSITIONS = {
    "updated",
    "no_change_required",
    "historical",
    "out_of_scope",
    "clarification_required",
    "integration_gate",
}
DISPOSITIONS = {
    "updated",
    "no_change",
    "historical",
    "out_of_scope",
    "clarification_required",
    "integration_gate",
}
LEGACY_PATH_REQUIRED_DISPOSITIONS = {"updated", "no_change_required", "historical"}
PATH_REQUIRED_DISPOSITIONS = {"updated", "no_change", "historical"}
SINGULAR_CURRENT_STEP_PATTERNS = (
    re.compile(
        r"(?im)^\s*(?:[-*]\s*)?(?:현재\s*단계|current(?:\s+step|_step))\s*(?::|은|는)"
    ),
    re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:현재\s+작업|실행\s+상태)\s*(?::|은|는)\s*S\d+"),
    re.compile(r"(?im)^\s*(?:[-*]\s*)?S\d+\s*부터\s*진행"),
    re.compile(r"(?im)^\s*(?:[-*]\s*)?Worker\s+S\d+(?:-[A-Z0-9]+)*\b"),
)


def validate_finalization_closure(root: Path, manifest: Dict[str, Any],
                                  schema_version: Any) -> List[Dict[str, str]]:
    """Validate finalization state, legacy compatibility, and graph closure."""
    findings: List[Dict[str, str]] = []
    finalization = manifest.get("finalization")
    if not isinstance(finalization, dict) or finalization.get("required") is not True:
        findings.append(diagnostic(
            "finalization_required_missing",
            "finalization.required must be true for acceptance finalization.",
        ))
    else:
        if finalization.get("state") not in FINALIZATION_STATES:
            findings.append(diagnostic(
                "finalization_state_invalid",
                f"Unsupported finalization state: {finalization.get('state')}.",
            ))
        evidence = finalization.get("evidence")
        evidence_set = set(evidence) if isinstance(evidence, list) else set()
        for missing in sorted(REQUIRED_FINALIZATION_EVIDENCE - evidence_set):
            findings.append(diagnostic(
                "finalization_evidence_missing",
                f"Required finalization evidence is missing: {missing}.",
            ))
        if (finalization.get("state") == "complete"
                and "post_edit_verification" not in evidence_set):
            findings.append(diagnostic(
                "finalization_evidence_missing",
                "Complete finalization requires post_edit_verification.",
            ))
        content, error, source_path = read_scoped_file(
            root, finalization.get("progress_path")
        )
        if error:
            findings.append(diagnostic(
                "finalization_source_unavailable",
                f"Cannot read finalization progress: {error}.",
                str(finalization.get("progress_path")),
            ))
        else:
            source_state = finalization_scalar(content or "", "state")
            source_acceptance = finalization_scalar(content or "", "acceptance_ref")
            if source_state != finalization.get("state"):
                findings.append(diagnostic(
                    "finalization_state_source_mismatch",
                    f"Source finalization state {source_state} differs from manifest "
                    f"{finalization.get('state')}.",
                    source_path,
                ))
            if source_acceptance != manifest.get("acceptance_ref"):
                findings.append(diagnostic(
                    "finalization_acceptance_source_mismatch",
                    "Source finalization acceptance_ref differs from manifest.",
                    source_path,
                ))

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
                "schema_version 1 cannot approve complete finalization; use schema_version 3.",
            ))

    if (schema_version == 2 and isinstance(finalization, dict)
            and finalization.get("state") == "complete"):
        findings.append(diagnostic(
            "legacy_schema_complete_forbidden",
            "schema_version 2 cannot approve complete finalization; use schema_version 3.",
        ))

    if schema_version in {2, 3}:
        graph_sync = manifest.get("graph_sync")
        if not isinstance(graph_sync, dict):
            findings.append(diagnostic(
                "graph_sync_missing",
                "schema_version 2 or 3 requires graph_sync assessment.",
            ))
        else:
            disposition = graph_sync.get("disposition")
            required = graph_sync.get("required")
            if disposition not in {"required", "not_applicable", "deferred"}:
                findings.append(diagnostic(
                    "graph_sync_disposition_invalid", "graph_sync disposition is invalid."
                ))
            if (not isinstance(graph_sync.get("reason"), str)
                    or not graph_sync["reason"].strip()):
                findings.append(diagnostic(
                    "graph_sync_reason_missing", "graph_sync requires a non-empty reason."
                ))
            expected_required = disposition in {"required", "deferred"}
            if not isinstance(required, bool) or required is not expected_required:
                findings.append(diagnostic(
                    "graph_sync_required_mismatch",
                    "graph_sync.required does not match its disposition.",
                ))
            state = finalization.get("state") if isinstance(finalization, dict) else None
            graph_path = graph_sync.get("validation_manifest_path")
            transaction_id = graph_sync.get("transaction_id")
            if (graph_path is not None
                    and (not isinstance(graph_path, str) or not graph_path.strip())):
                findings.append(diagnostic(
                    "graph_sync_evidence_malformed",
                    "graph_sync validation_manifest_path must be a non-empty string.",
                ))
            if (transaction_id is not None
                    and (not isinstance(transaction_id, str) or not transaction_id.strip())):
                findings.append(diagnostic(
                    "graph_sync_evidence_malformed",
                    "graph_sync transaction_id must be a non-empty string.",
                ))
            if (disposition == "not_applicable"
                    and (graph_path is not None or transaction_id is not None)):
                findings.append(diagnostic(
                    "graph_sync_evidence_unexpected",
                    "not_applicable graph synchronization must not declare transaction evidence.",
                ))
            if state == "complete" and disposition == "deferred":
                findings.append(diagnostic(
                    "graph_sync_deferred",
                    "Deferred graph synchronization blocks complete finalization.",
                ))
            if state == "complete" and disposition == "required":
                graph_path_valid = isinstance(graph_path, str) and bool(graph_path.strip())
                transaction_id_valid = (
                    isinstance(transaction_id, str) and bool(transaction_id.strip())
                )
                if not graph_path_valid or not transaction_id_valid:
                    findings.append(diagnostic(
                        "graph_sync_evidence_missing",
                        "Complete finalization requires a graph validation manifest "
                        "and transaction_id.",
                    ))
                else:
                    content, error, source_path = read_scoped_file(root, graph_path)
                    if error:
                        findings.append(diagnostic(
                            "graph_sync_evidence_unavailable",
                            f"Cannot read graph validation manifest: {error}.",
                            graph_path,
                        ))
                    else:
                        try:
                            graph_manifest = json.loads(content or "")
                        except json.JSONDecodeError:
                            graph_manifest = None
                        graph_transaction = (
                            graph_manifest.get("transaction")
                            if isinstance(graph_manifest, dict)
                            else None
                        )
                        if not isinstance(graph_transaction, dict):
                            findings.append(diagnostic(
                                "graph_sync_evidence_malformed",
                                "Graph validation manifest requires an inline transaction.",
                                source_path,
                            ))
                        elif graph_transaction.get("transaction_id") != transaction_id:
                            findings.append(diagnostic(
                                "graph_sync_transaction_mismatch",
                                "graph_sync transaction_id differs from the graph "
                                "validation manifest.",
                                source_path,
                            ))
                        elif graph_transaction.get("state") != "verified":
                            findings.append(diagnostic(
                                "graph_sync_transaction_not_verified",
                                "Complete finalization requires the bound graph transaction "
                                "state to be verified.",
                                source_path,
                            ))
    return findings


def validate_impact_candidates(root: Path, raw_candidates: Any,
                               schema_version: Any) -> List[Dict[str, str]]:
    """Validate impact dispositions and return diagnostics in source order."""
    findings: List[Dict[str, str]] = []
    if not isinstance(raw_candidates, list):
        findings.append(diagnostic(
            "impact_candidates_invalid", "impact_candidates must be an array."
        ))
        raw_candidates = []
    observed_categories = set()
    for index, candidate in enumerate(raw_candidates):
        if not isinstance(candidate, dict):
            findings.append(diagnostic(
                "candidate_invalid", f"impact_candidates[{index}] must be an object."
            ))
            continue
        disposition = candidate.get("disposition")
        category = candidate.get("category")
        if isinstance(category, str):
            observed_categories.add(category)
        else:
            findings.append(diagnostic(
                "candidate_category_missing",
                f"impact_candidates[{index}] requires a category.",
            ))
        allowed_dispositions = DISPOSITIONS if schema_version == 3 else LEGACY_DISPOSITIONS
        path_required_dispositions = (
            PATH_REQUIRED_DISPOSITIONS
            if schema_version == 3
            else LEGACY_PATH_REQUIRED_DISPOSITIONS
        )
        if disposition not in allowed_dispositions:
            findings.append(diagnostic(
                "candidate_disposition_invalid",
                f"impact_candidates[{index}] has an invalid disposition.",
            ))
        reason = candidate.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            findings.append(diagnostic(
                "candidate_reason_missing",
                f"impact_candidates[{index}] requires a reason.",
            ))
        if category == "implementation_gate":
            gate_state = candidate.get("gate_state")
            gate_scope = candidate.get("gate_scope")
            if (gate_state not in {"resolved", "residual", "not_applicable"}
                    or not isinstance(gate_scope, str) or not gate_scope.strip()):
                findings.append(diagnostic(
                    "implementation_gate_assessment_invalid",
                    "implementation_gate requires gate_state and gate_scope.",
                ))
        elif category == "residual_risk":
            risk_items = candidate.get("risk_items")
            risk_state = candidate.get("risk_state")
            if (risk_state not in {"none", "recorded"}
                    or not isinstance(risk_items, list)
                    or (risk_state == "recorded" and not risk_items)):
                findings.append(diagnostic(
                    "residual_risk_assessment_invalid",
                    "residual_risk requires risk_state and risk_items.",
                ))
        elif category == "namespace":
            if candidate.get("namespace_state") not in {
                    "checked", "conflict", "not_applicable"}:
                findings.append(diagnostic(
                    "namespace_assessment_invalid",
                    "namespace requires namespace_state.",
                ))

        path_value = candidate.get("path")
        if disposition not in path_required_dispositions and path_value is None:
            continue
        path, path_error = resolve_scoped_path(root, path_value)
        if path_error == "missing":
            findings.append(diagnostic(
                "candidate_path_missing",
                f"impact_candidates[{index}] requires a path.",
            ))
            continue
        if path_error == "outside":
            findings.append(diagnostic(
                "candidate_path_outside_root",
                f"impact_candidates[{index}] path escapes root.",
            ))
            continue
        if path is None or not path.is_file():
            findings.append(diagnostic(
                "candidate_path_unavailable",
                f"impact_candidates[{index}] path is unavailable.",
                path_value,
            ))
            continue
        if disposition == "historical" or path.suffix.lower() != ".md":
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            findings.append(diagnostic(
                "candidate_path_unreadable", f"Cannot read candidate: {error}", path_value
            ))
            continue
        if any(pattern.search(content) for pattern in SINGULAR_CURRENT_STEP_PATTERNS):
            findings.append(diagnostic(
                "singular_current_step_claim",
                "Live candidate contains a singular current-step claim; use active_steps.",
                path_value,
            ))
    for missing in sorted(REQUIRED_IMPACT_CATEGORIES - observed_categories):
        findings.append(diagnostic(
            "impact_category_missing", f"Required impact category is missing: {missing}."
        ))
    return findings


def validate_namespace_entries(raw_namespaces: Any) -> List[Dict[str, str]]:
    """Validate namespace ownership and deterministic collision reporting."""
    findings: List[Dict[str, str]] = []
    if not isinstance(raw_namespaces, list):
        findings.append(diagnostic(
            "namespace_entries_invalid", "namespace_entries must be an array."
        ))
        raw_namespaces = []
    owners_by_name: Dict[Tuple[str, str], set] = defaultdict(set)
    for index, entry in enumerate(raw_namespaces):
        required_fields = ("namespace", "value", "owner")
        if (not isinstance(entry, dict)
                or not all(isinstance(entry.get(field), str) and entry[field].strip()
                           for field in required_fields)):
            findings.append(diagnostic(
                "namespace_entry_invalid",
                f"namespace_entries[{index}] requires namespace, value, and owner.",
            ))
            continue
        owners_by_name[(entry["namespace"], entry["value"])].add(entry["owner"])
    for (namespace, value), owners in sorted(owners_by_name.items()):
        if len(owners) > 1:
            findings.append(diagnostic(
                "namespace_collision",
                f"{namespace}:{value} is claimed by multiple owners: "
                f"{', '.join(sorted(owners))}.",
            ))
    return findings
