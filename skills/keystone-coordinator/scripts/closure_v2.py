"""Strict actual-state validation for Coordinator closure manifest schema v2."""

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from closure_actual_state import (
    changed_paths,
    digest_bytes,
    digest_json,
    normalize_relative_path,
    path_in_scope,
    path_overlaps_scope,
    repository_snapshot,
    repository_symlinks,
    resolved_repository_root,
)


Diagnostic = Dict[str, str]
DIGEST_PREFIX_LENGTH = len("sha256:")
EXECUTION_MODES = {"direct_execution", "orchestration"}
PURPOSES = {"investigate", "document_edit", "implement", "review", "verify"}
AUTHORITIES = {"read_only", "bounded_edit", "review_only", "verification"}
REPORT_STATUSES = {
    "DONE",
    "DONE_WITH_CONCERNS",
    "NEEDS_CONTEXT",
    "NEEDS_SCOPE_CHANGE",
    "BLOCKED",
}
DEPENDENCY_STATUSES = {"satisfied", "waiting", "unresolvable", "invalid", "unknown"}
SYNC_DISPOSITIONS = {"required", "not_applicable", "deferred"}
RUNNER_ENVELOPE_FIELDS = {
    "schema_version", "status", "diagnostics", "summary",
}
RUNNER_DIAGNOSTIC_FIELDS = {"severity", "code", "message"}
LINKER_COVERAGE_LIST_FIELDS = (
    "discovered_sources",
    "parsed_sources",
    "omitted_sources",
    "declared_only_sources",
    "skipped_sources",
)
LINKER_COVERAGE_FIELDS = {
    "mode", "complete", "path_digest", "counts",
} | set(LINKER_COVERAGE_LIST_FIELDS)
LOCATOR_FIELDS = {
    "path", "heading", "symbol", "test_name", "config_key", "schema_name",
}
WORK_STATE_RUNTIME_FIELDS = {
    "policy_digest", "result_digest", "source_generation",
    "path_set_digest", "complete",
}


class DuplicateJsonKey(ValueError):
    pass


class NonfiniteJsonValue(ValueError):
    pass


def _reject_duplicate_keys(pairs: Sequence[Any]) -> Dict[str, Any]:
    value: Dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJsonKey("duplicate JSON key: %s" % key)
        value[key] = item
    return value


def _reject_nonfinite_json(value: str) -> None:
    raise NonfiniteJsonValue("non-finite JSON number is forbidden: %s" % value)


def _loads_json_strict(value: str) -> Any:
    return json.loads(
        value,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite_json,
    )


def package_runner_paths() -> Tuple[Path, Path]:
    """Return the resolved Linker and Author runners owned by this package set."""
    package_skills = Path(__file__).resolve().parents[2]
    return (
        (
            package_skills / "keystone-linker" / "scripts"
            / "run_graph_validation.py"
        ).resolve(),
        (
            package_skills / "keystone-author" / "scripts"
            / "run_finalization_validation.py"
        ).resolve(),
    )


def diagnostic(code: str, message: str, path: str) -> Diagnostic:
    return {"code": code, "message": message, "path": path, "severity": "error"}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _evidence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_text(item) for item in value)


def _locator(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) <= LOCATOR_FIELDS
        and isinstance(value.get("path"), str)
        and bool(value["path"])
        and all(item is None or isinstance(item, str) for item in value.values())
    )


def _locators(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        _locator(item) for item in value
    )


def _digest(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    suffix = value[DIGEST_PREFIX_LENGTH:]
    return len(suffix) == 64 and all(character in "0123456789abcdef" for character in suffix)


def _unknown_fields(
    value: Mapping[str, Any], allowed: Set[str], path: str, diagnostics: List[Diagnostic]
) -> None:
    for field in sorted(set(value) - allowed):
        diagnostics.append(
            diagnostic(
                "unknown_field",
                f"Unknown authority-bearing field {field!r} is not allowed in schema v2.",
                f"{path}.{field}" if path else field,
            )
        )


def _missing_fields(
    value: Mapping[str, Any], required: Set[str], path: str,
    diagnostics: List[Diagnostic],
) -> None:
    for field in sorted(required - set(value)):
        diagnostics.append(diagnostic(
            "required_field_missing",
            "Authoritative schema v2 field %r is required." % field,
            "%s.%s" % (path, field) if path else field,
        ))


def _require_text_fields(
    value: Mapping[str, Any], fields: Iterable[str], path: str, diagnostics: List[Diagnostic]
) -> None:
    for field in fields:
        if not _text(value.get(field)):
            diagnostics.append(
                diagnostic("required_field_missing", f"{field} is required.", f"{path}.{field}")
            )


def _validate_paths(
    values: Any, path: str, diagnostics: List[Diagnostic]
) -> List[str]:
    if not isinstance(values, list):
        diagnostics.append(diagnostic("path_list_invalid", "Expected an explicit path array.", path))
        return []
    result: List[str] = []
    for index, raw in enumerate(values):
        normalized = normalize_relative_path(raw)
        if normalized is None:
            diagnostics.append(
                diagnostic(
                    "path_invalid",
                    "Paths must be normalized repository-relative POSIX paths without traversal.",
                    f"{path}[{index}]",
                )
            )
            continue
        if normalized in result:
            diagnostics.append(
                diagnostic("path_duplicate", "Path entries must be unique.", f"{path}[{index}]")
            )
            continue
        result.append(normalized)
    return result


def _validate_gate(
    raw: Any, path: str, diagnostics: List[Diagnostic]
) -> Optional[Mapping[str, Any]]:
    gate = _mapping(raw)
    allowed = {"gate_id", "source", "dependency", "scope", "result", "blocking"}
    _unknown_fields(gate, allowed, path, diagnostics)
    scope = _mapping(gate.get("scope"))
    _unknown_fields(scope, {"steps", "work_completion"}, f"{path}.scope", diagnostics)
    if (
        not all(_text(gate.get(field)) for field in ("gate_id", "source", "dependency"))
        or gate.get("result") not in DEPENDENCY_STATUSES
        or not isinstance(gate.get("blocking"), bool)
        or not isinstance(scope.get("steps"), list)
        or not all(_text(item) for item in _list(scope.get("steps")))
        or not isinstance(scope.get("work_completion"), bool)
    ):
        diagnostics.append(
            diagnostic(
                "dependency_gate_invalid",
                "Dependency gates require identity, target, scope, result, and blocking evidence.",
                path,
            )
        )
        return None
    if gate["result"] in {"invalid", "unresolvable", "unknown"}:
        diagnostics.append(
            diagnostic(
                "dependency_gate_unresolved",
                "Invalid, unresolvable, or unknown dependency evidence is fail-closed.",
                path,
            )
        )
    if gate["result"] == "satisfied" and gate["blocking"]:
        diagnostics.append(
            diagnostic(
                "dependency_gate_blocking_inconsistent",
                "A satisfied dependency cannot remain blocking.",
                path,
            )
        )
    return gate


def _validate_context(
    context: Mapping[str, Any], closure_target: Any, closure_step_ref: Any,
    diagnostics: List[Diagnostic]
) -> None:
    allowed = {
        "main_context_checkpoint",
        "work_context",
        "source_documents",
        "applicable_standards",
        "accepted_decisions",
        "completion_criteria",
        "scope_boundaries",
        "forbidden_changes",
        "verification_expectations",
        "artifact_context",
        "reader_context",
        "author_context",
        "work_state_runtime",
        "dependency_status",
        "active_step_gates",
        "work_completion_gates",
    }
    _unknown_fields(context, allowed, "assignment.context_pack", diagnostics)
    if not _text(context.get("main_context_checkpoint")):
        diagnostics.append(
            diagnostic(
                "main_context_checkpoint_missing",
                "The immutable assignment must preserve Main context.",
                "assignment.context_pack.main_context_checkpoint",
            )
        )
    work = _mapping(context.get("work_context"))
    _unknown_fields(work, {"round_ref", "work_ref", "step_refs"},
                    "assignment.context_pack.work_context", diagnostics)
    _require_text_fields(work, ("round_ref", "work_ref"),
                         "assignment.context_pack.work_context", diagnostics)
    if not _evidence(work.get("step_refs")):
        diagnostics.append(
            diagnostic(
                "work_context_missing",
                "work_context.step_refs must be a non-empty array.",
                "assignment.context_pack.work_context.step_refs",
            )
        )
    for field in (
        "source_documents",
        "applicable_standards",
        "completion_criteria",
        "forbidden_changes",
        "verification_expectations",
    ):
        if not _evidence(context.get(field)):
            diagnostics.append(
                diagnostic(
                    "context_evidence_missing",
                    f"{field} must be a non-empty evidence array.",
                    f"assignment.context_pack.{field}",
                )
            )
    if not isinstance(context.get("accepted_decisions"), list):
        diagnostics.append(
            diagnostic(
                "accepted_decisions_missing",
                "accepted_decisions must be an explicit array.",
                "assignment.context_pack.accepted_decisions",
            )
        )
    for name in ("artifact_context", "reader_context", "author_context"):
        item = _mapping(context.get(name))
        _unknown_fields(item, {"status", "evidence"},
                        f"assignment.context_pack.{name}", diagnostics)
        if item.get("status") not in {"ready", "not_applicable", "blocked"}:
            diagnostics.append(
                diagnostic("context_status_invalid", f"{name}.status is invalid.",
                           f"assignment.context_pack.{name}.status")
            )
        elif item["status"] == "blocked":
            diagnostics.append(
                diagnostic("context_blocked", f"{name} is blocked.",
                           f"assignment.context_pack.{name}.status")
            )
        elif not _evidence(item.get("evidence")):
            diagnostics.append(
                diagnostic("context_evidence_missing", f"{name} requires evidence.",
                           f"assignment.context_pack.{name}.evidence")
            )
    work_state = _mapping(context.get("work_state_runtime"))
    if "work_state_runtime" in context:
        path = "assignment.context_pack.work_state_runtime"
        _unknown_fields(work_state, WORK_STATE_RUNTIME_FIELDS, path, diagnostics)
        _missing_fields(work_state, WORK_STATE_RUNTIME_FIELDS, path, diagnostics)
        for field in (
            "policy_digest", "result_digest", "source_generation", "path_set_digest",
        ):
            if not _digest(work_state.get(field)):
                diagnostics.append(diagnostic(
                    "work_state_runtime_digest_invalid",
                    "%s must be a canonical SHA-256 digest." % field,
                    "%s.%s" % (path, field),
                ))
        if work_state.get("complete") is not True:
            diagnostics.append(diagnostic(
                "work_state_runtime_incomplete",
                "Context Pack Work State Runtime must bind a complete generation.",
                path + ".complete",
            ))
    if context.get("dependency_status") not in DEPENDENCY_STATUSES:
        diagnostics.append(
            diagnostic(
                "dependency_status_invalid",
                "dependency_status must use the canonical vocabulary.",
                "assignment.context_pack.dependency_status",
            )
        )
    assignment_steps = _list(work.get("step_refs"))
    gate_groups: Dict[str, List[Mapping[str, Any]]] = {}
    gate_ids: Set[str] = set()
    for name in ("active_step_gates", "work_completion_gates"):
        raw_gates = context.get(name)
        if not isinstance(raw_gates, list):
            diagnostics.append(
                diagnostic("dependency_gates_missing", f"{name} must be an explicit array.",
                           f"assignment.context_pack.{name}")
            )
            gate_groups[name] = []
            continue
        gate_groups[name] = []
        for index, raw in enumerate(raw_gates):
            gate = _validate_gate(
                raw, f"assignment.context_pack.{name}[{index}]", diagnostics
            )
            if gate:
                gate_path = f"assignment.context_pack.{name}[{index}]"
                gate_id = gate["gate_id"]
                if gate_id in gate_ids:
                    diagnostics.append(diagnostic(
                        "dependency_gate_duplicate",
                        "Dependency gate IDs must be unique across gate groups.",
                        gate_path,
                    ))
                gate_ids.add(gate_id)
                scope = _mapping(gate.get("scope"))
                steps = _list(scope.get("steps"))
                if any(step not in assignment_steps for step in steps):
                    diagnostics.append(diagnostic(
                        "dependency_gate_step_scope_invalid",
                        "Dependency gate Steps must remain inside assignment work context.",
                        f"{gate_path}.scope.steps",
                    ))
                if name == "active_step_gates" and (
                    not steps or scope.get("work_completion") is not False
                ):
                    diagnostics.append(diagnostic(
                        "dependency_gate_group_mismatch",
                        "active_step_gates require Step-only scope.",
                        gate_path,
                    ))
                if name == "active_step_gates" and closure_target == "step" and (
                    not _text(closure_step_ref) or closure_step_ref not in steps
                ):
                    diagnostics.append(diagnostic(
                        "dependency_gate_closure_step_mismatch",
                        "Active-Step gates must apply to the concrete closure Step.",
                        gate_path,
                    ))
                if name == "work_completion_gates" and (
                    scope.get("work_completion") is not True or steps
                ):
                    diagnostics.append(diagnostic(
                        "dependency_gate_group_mismatch",
                        "work_completion_gates require Work-only scope.",
                        gate_path,
                    ))
                gate_groups[name].append(gate)
    if context.get("dependency_status") != "satisfied" and not any(gate_groups.values()):
        diagnostics.append(diagnostic(
            "dependency_status_gate_mismatch",
            "A non-satisfied dependency summary requires canonical gate evidence.",
            "assignment.context_pack.dependency_status",
        ))
    selected_groups = (
        ("active_step_gates", "work_completion_gates")
        if closure_target == "work"
        else ("active_step_gates",)
    )
    for selected in selected_groups:
        code = (
            "work_completion_dependency_blocking"
            if selected == "work_completion_gates"
            else "active_step_dependency_blocking"
        )
        for index, gate in enumerate(gate_groups.get(selected, [])):
            if gate["blocking"] and gate["result"] != "satisfied":
                diagnostics.append(
                    diagnostic(
                        code,
                        f"A blocking {selected} dependency prevents this closure target.",
                        f"assignment.context_pack.{selected}[{index}]",
                    )
                )


def _validate_assignment(
    assignment: Mapping[str, Any], closure_target: Any, closure_step_ref: Any,
    diagnostics: List[Diagnostic]
) -> Tuple[Mapping[str, Any], Mapping[str, Any], Dict[str, str]]:
    allowed = {
        "schema_version",
        "assignment_id",
        "execution_mode",
        "purpose",
        "authority",
        "goal",
        "context_pack",
        "injected_skills",
        "scope",
        "baseline_snapshot",
    }
    _unknown_fields(assignment, allowed, "assignment", diagnostics)
    _missing_fields(assignment, allowed, "assignment", diagnostics)
    assignment_schema = assignment.get("schema_version")
    if type(assignment_schema) is not int or assignment_schema != 2:
        diagnostics.append(
            diagnostic("assignment_schema_invalid", "Assignment schema_version must be 2.",
                       "assignment.schema_version")
        )
    _require_text_fields(assignment, ("assignment_id", "goal"), "assignment", diagnostics)
    if assignment.get("execution_mode") not in EXECUTION_MODES:
        diagnostics.append(diagnostic("execution_mode_invalid", "Invalid execution mode.",
                                      "assignment.execution_mode"))
    if assignment.get("purpose") not in PURPOSES:
        diagnostics.append(diagnostic("purpose_invalid", "Invalid assignment purpose.",
                                      "assignment.purpose"))
    if assignment.get("authority") not in AUTHORITIES:
        diagnostics.append(diagnostic("authority_invalid", "Invalid assignment authority.",
                                      "assignment.authority"))

    context = _mapping(assignment.get("context_pack"))
    if not isinstance(assignment.get("context_pack"), Mapping):
        diagnostics.append(diagnostic(
            "authoritative_field_type_invalid",
            "assignment.context_pack must be an object.",
            "assignment.context_pack",
        ))
    _validate_context(context, closure_target, closure_step_ref, diagnostics)
    scope = _mapping(assignment.get("scope"))
    if not isinstance(assignment.get("scope"), Mapping):
        diagnostics.append(diagnostic(
            "authoritative_field_type_invalid",
            "assignment.scope must be an object.",
            "assignment.scope",
        ))
    _unknown_fields(scope, {"read_scope", "allowed_edit_scope", "excluded_scope"},
                    "assignment.scope", diagnostics)
    normalized_scope = {
        name: _validate_paths(scope.get(name), f"assignment.scope.{name}", diagnostics)
        for name in ("read_scope", "allowed_edit_scope", "excluded_scope")
    }
    context_scope = _mapping(context.get("scope_boundaries"))
    _unknown_fields(context_scope, {"read_scope", "allowed_edit_scope", "excluded_scope"},
                    "assignment.context_pack.scope_boundaries", diagnostics)
    if scope != context_scope:
        diagnostics.append(
            diagnostic(
                "assignment_scope_context_mismatch",
                "Assignment scope must exactly match Context Pack scope boundaries.",
                "assignment.scope",
            )
        )

    skills = assignment.get("injected_skills")
    if not isinstance(skills, list) or not skills:
        diagnostics.append(
            diagnostic("injected_skills_missing", "At least one injected skill is required.",
                       "assignment.injected_skills")
        )
    skill_keys: Set[Tuple[str, str]] = set()
    for index, raw in enumerate(_list(skills)):
        item = _mapping(raw)
        path = f"assignment.injected_skills[{index}]"
        _unknown_fields(item, {"skill_id", "mode"}, path, diagnostics)
        if not _text(item.get("skill_id")) or not _text(item.get("mode")):
            diagnostics.append(diagnostic("injected_skill_invalid", "Skill ID and mode are required.", path))
            continue
        key = (item["skill_id"], item["mode"])
        if key in skill_keys:
            diagnostics.append(diagnostic("injected_skill_duplicate", "Injected skills must be unique.", path))
        skill_keys.add(key)
    external = {item for item in skill_keys if item[0] != "keystone-default-bounded-worker"}
    if assignment.get("execution_mode") == "orchestration" and not external:
        diagnostics.append(diagnostic("orchestration_external_skill_missing",
                                      "Orchestration requires an external skill.",
                                      "assignment.injected_skills"))
    if assignment.get("execution_mode") == "direct_execution" and (
        external or ("keystone-default-bounded-worker", "default") not in skill_keys
    ):
        diagnostics.append(diagnostic("direct_execution_skill_invalid",
                                      "Direct execution requires only the default worker contract.",
                                      "assignment.injected_skills"))

    baseline: Dict[str, str] = {}
    raw_snapshot = assignment.get("baseline_snapshot")
    if not isinstance(raw_snapshot, list):
        diagnostics.append(diagnostic("baseline_snapshot_invalid",
                                      "baseline_snapshot must be an explicit array.",
                                      "assignment.baseline_snapshot"))
    for index, raw in enumerate(_list(raw_snapshot)):
        item = _mapping(raw)
        path = f"assignment.baseline_snapshot[{index}]"
        _unknown_fields(item, {"path", "digest"}, path, diagnostics)
        normalized = normalize_relative_path(item.get("path"))
        if normalized is None:
            diagnostics.append(diagnostic("path_invalid", "Snapshot path is invalid.", f"{path}.path"))
            continue
        if normalized in baseline:
            diagnostics.append(diagnostic("baseline_path_duplicate", "Snapshot paths must be unique.", path))
        if not _digest(item.get("digest")):
            diagnostics.append(diagnostic("baseline_digest_invalid", "Snapshot digest is invalid.",
                                          f"{path}.digest"))
            continue
        baseline[normalized] = item["digest"]
    return context, normalized_scope, baseline


def _validate_report(
    report: Mapping[str, Any],
    assignment: Mapping[str, Any],
    assignment_digest: str,
    context: Mapping[str, Any],
    scope: Mapping[str, Any],
    baseline: Mapping[str, str],
    current: Mapping[str, str],
    diagnostics: List[Diagnostic],
) -> List[Mapping[str, Any]]:
    allowed = {
        "assignment_id", "assignment_digest", "context_digest", "execution_mode",
        "status", "purpose", "authority", "goal", "skill_usage", "changed_files",
        "artifact_deltas", "scope_check", "forbidden_change_check", "verification",
    }
    _unknown_fields(report, allowed, "worker_report", diagnostics)
    bindings = {
        "assignment_id": assignment.get("assignment_id"),
        "assignment_digest": assignment_digest,
        "context_digest": digest_json(context),
        "execution_mode": assignment.get("execution_mode"),
        "purpose": assignment.get("purpose"),
        "authority": assignment.get("authority"),
        "goal": assignment.get("goal"),
    }
    for field, expected in bindings.items():
        if report.get(field) != expected:
            diagnostics.append(
                diagnostic(f"{field}_mismatch", f"Report {field} is not bound to the assignment.",
                           f"worker_report.{field}")
            )
    if report.get("status") not in REPORT_STATUSES:
        diagnostics.append(diagnostic("worker_report_status_invalid", "Invalid report status.",
                                      "worker_report.status"))

    expected_skills = sorted(
        (item["skill_id"], item["mode"])
        for item in _list(assignment.get("injected_skills"))
        if isinstance(item, Mapping)
        and _text(item.get("skill_id"))
        and _text(item.get("mode"))
    )
    actual_skills: List[Tuple[str, str]] = []
    for index, raw in enumerate(_list(report.get("skill_usage"))):
        item = _mapping(raw)
        path = f"worker_report.skill_usage[{index}]"
        _unknown_fields(item, {"skill_id", "mode", "outputs_used", "limits_hit"}, path, diagnostics)
        if not _text(item.get("skill_id")) or not _text(item.get("mode")):
            diagnostics.append(diagnostic("skill_usage_invalid", "Skill ID and mode are required.", path))
        else:
            actual_skills.append((item["skill_id"], item["mode"]))
        if not _evidence(item.get("outputs_used")):
            diagnostics.append(diagnostic("skill_usage_outputs_missing", "outputs_used requires evidence.", path))
        if not isinstance(item.get("limits_hit"), list):
            diagnostics.append(diagnostic("skill_usage_limits_invalid", "limits_hit must be an array.", path))
    if sorted(actual_skills) != expected_skills:
        diagnostics.append(diagnostic("skill_usage_mismatch",
                                      "worker_report.skill_usage must exactly match injected skills.",
                                      "worker_report.skill_usage"))

    actual_changes = changed_paths(baseline, current)
    reported_files = report.get("changed_files")
    if not isinstance(reported_files, list) or reported_files != sorted(actual_changes):
        diagnostics.append(diagnostic("actual_changed_files_mismatch",
                                      "changed_files must exactly equal the derived actual change set.",
                                      "worker_report.changed_files"))
    for changed in actual_changes:
        if not path_in_scope(changed, scope.get("allowed_edit_scope", [])) or path_in_scope(
            changed, scope.get("excluded_scope", [])
        ):
            diagnostics.append(diagnostic("actual_change_out_of_scope",
                                          f"Actual changed path {changed} is outside allowed scope.",
                                          "worker_report.changed_files"))
    if actual_changes and assignment.get("authority") in {"read_only", "review_only", "verification"}:
        diagnostics.append(diagnostic("authority_change_forbidden",
                                      "This assignment authority does not allow repository changes.",
                                      "assignment.authority"))

    deltas: List[Mapping[str, Any]] = []
    raw_deltas = report.get("artifact_deltas")
    if not isinstance(raw_deltas, list):
        diagnostics.append(diagnostic("artifact_deltas_invalid", "artifact_deltas must be an array.",
                                      "worker_report.artifact_deltas"))
    by_path: Dict[str, List[Mapping[str, Any]]] = {}
    delta_allowed = {
        "kind", "source_surface", "change_kind", "changed_locators", "semantic_summary",
        "baseline_digest", "resulting_digest", "graph_relevant",
    }
    for index, raw in enumerate(_list(raw_deltas)):
        delta = _mapping(raw)
        path = f"worker_report.artifact_deltas[{index}]"
        _unknown_fields(delta, delta_allowed, path, diagnostics)
        surface = normalize_relative_path(delta.get("source_surface"))
        if surface is None:
            diagnostics.append(diagnostic("artifact_delta_surface_invalid", "Invalid delta surface.", path))
            continue
        if delta.get("kind") != "artifact_delta":
            diagnostics.append(diagnostic("artifact_delta_kind_invalid", "kind must be artifact_delta.", path))
        if delta.get("change_kind") not in {"added", "modified", "deleted"}:
            diagnostics.append(diagnostic("artifact_delta_change_kind_invalid", "Invalid change_kind.", path))
        if (
            not _locators(delta.get("changed_locators"))
            or not _text(delta.get("semantic_summary"))
        ):
            diagnostics.append(diagnostic("artifact_delta_evidence_missing",
                                          "Delta requires canonical locator objects and a summary.",
                                          path))
        if not isinstance(delta.get("graph_relevant"), bool):
            diagnostics.append(diagnostic("artifact_delta_graph_relevance_invalid",
                                          "graph_relevant must be boolean.", path))
        before = baseline.get(surface, "absent")
        after = current.get(surface, "absent")
        if delta.get("baseline_digest") != before:
            diagnostics.append(diagnostic("artifact_baseline_digest_mismatch",
                                          "Delta baseline digest does not match assignment snapshot.",
                                          f"{path}.baseline_digest"))
        if delta.get("resulting_digest") != after:
            diagnostics.append(diagnostic("artifact_resulting_digest_mismatch",
                                          "Delta resulting digest does not match current bytes.",
                                          f"{path}.resulting_digest"))
        if delta.get("change_kind") != actual_changes.get(surface):
            diagnostics.append(diagnostic("artifact_change_kind_mismatch",
                                          "Delta change_kind does not match actual state.",
                                          f"{path}.change_kind"))
        by_path.setdefault(surface, []).append(delta)
        deltas.append(delta)
    for changed in actual_changes:
        if len(by_path.get(changed, [])) != 1:
            diagnostics.append(diagnostic("artifact_delta_cardinality_invalid",
                                          f"Actual changed path {changed} requires exactly one delta.",
                                          "worker_report.artifact_deltas"))
    for surface in set(by_path) - set(actual_changes):
        diagnostics.append(diagnostic("artifact_delta_unexpected",
                                      f"Delta {surface} is not an actual changed path.",
                                      "worker_report.artifact_deltas"))

    actual_scope_claim = "within_scope" if not any(
        not path_in_scope(path, scope.get("allowed_edit_scope", []))
        or path_in_scope(path, scope.get("excluded_scope", []))
        for path in actual_changes
    ) else "out_of_scope"
    if report.get("scope_check") != actual_scope_claim:
        diagnostics.append(diagnostic("scope_check_mismatch", "scope_check disagrees with actual state.",
                                      "worker_report.scope_check"))
    if report.get("forbidden_change_check") != "none":
        diagnostics.append(diagnostic("forbidden_change_claim_invalid",
                                      "Unresolved forbidden changes prevent closure.",
                                      "worker_report.forbidden_change_check"))
    verification = _mapping(report.get("verification"))
    _unknown_fields(verification, {"status", "evidence"}, "worker_report.verification", diagnostics)
    if verification.get("status") != "pass" or not _evidence(verification.get("evidence")):
        diagnostics.append(diagnostic("verification_incomplete", "Verification must pass with evidence.",
                                      "worker_report.verification"))
    return deltas


def _safe_evidence_path(evidence_root: Path, value: Any) -> Optional[Path]:
    normalized = normalize_relative_path(value)
    if normalized is None:
        return None
    root = evidence_root.resolve()
    candidate = root.joinpath(*Path(normalized).parts)
    try:
        candidate.resolve().relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    return candidate


def _evidence_file_identity(value: os.stat_result) -> Tuple[int, ...]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
        value.st_nlink,
        stat.S_IFMT(value.st_mode),
    )


def _read_evidence_bytes(evidence_root: Path, relative: Any) -> bytes:
    normalized = normalize_relative_path(relative)
    if normalized is None:
        raise ValueError("evidence path is not normalized")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise OSError("evidence reads require no-follow descriptor APIs")
    root = evidence_root.resolve(strict=True)
    directory_flags = (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    directory_fd = os.open(str(root), directory_flags)
    try:
        parts = PurePosixPath(normalized).parts
        for component in parts[:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        before = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise OSError("evidence must be a single-link regular file")
        file_fd = os.open(parts[-1], file_flags, dir_fd=directory_fd)
        try:
            opened = os.fstat(file_fd)
            if _evidence_file_identity(opened) != _evidence_file_identity(before):
                raise OSError("evidence identity changed before read")
            chunks: List[bytes] = []
            while True:
                chunk = os.read(file_fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_fd = os.fstat(file_fd)
            if _evidence_file_identity(after_fd) != _evidence_file_identity(opened):
                raise OSError("evidence changed during read")
        finally:
            os.close(file_fd)
        after_path = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if _evidence_file_identity(after_path) != _evidence_file_identity(before):
            raise OSError("evidence changed after read")
        raw = b"".join(chunks)
        if len(raw) != before.st_size:
            raise OSError("evidence size changed during read")
        return raw
    finally:
        os.close(directory_fd)


def _read_evidence_json(
    evidence_root: Path,
    relative: Any,
    expected_digest: Any,
    path: str,
    diagnostics: List[Diagnostic],
) -> Tuple[Optional[Path], Optional[Mapping[str, Any]], Optional[bytes]]:
    evidence_path = _safe_evidence_path(evidence_root, relative)
    if evidence_path is None:
        diagnostics.append(diagnostic("evidence_path_invalid", "Evidence path is invalid.", path))
        return None, None, None
    try:
        raw = _read_evidence_bytes(evidence_root, relative)
        actual_digest = digest_bytes(raw)
        payload = _loads_json_strict(raw.decode("utf-8"))
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        DuplicateJsonKey,
        NonfiniteJsonValue,
    ) as error:
        diagnostics.append(diagnostic("evidence_unreadable", str(error), path))
        return evidence_path, None, None
    if actual_digest != expected_digest:
        diagnostics.append(diagnostic("evidence_digest_mismatch",
                                      "Evidence raw-byte digest does not match the manifest.", path))
    if not isinstance(payload, Mapping):
        diagnostics.append(diagnostic("evidence_invalid", "Evidence JSON must be an object.", path))
        return evidence_path, None, None
    return evidence_path, payload, raw


def _run_captured_manifest(
    runner: Path,
    root: Path,
    raw_manifest: bytes,
    timeout_seconds: float,
    expected_digest: Any,
    path: str,
    diagnostics: List[Diagnostic],
    runner_kind: str,
    *,
    runner_arguments: Sequence[str] = (),
    isolated: bool = False,
) -> Optional[Mapping[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="keystone-coordinator-evidence-") as directory:
        manifest_path = Path(directory) / "manifest.json"
        manifest_path.write_bytes(raw_manifest)
        command = [sys.executable]
        if isolated:
            command.append("-I")
        command.extend((
            str(runner),
            "--root",
            str(root),
            "--manifest",
            str(manifest_path),
            *runner_arguments,
        ))
        if isolated:
            return _run_evidence(
                command,
                timeout_seconds,
                expected_digest,
                path,
                diagnostics,
                runner_kind,
                isolated=True,
            )
        return _run_evidence(
            command,
            timeout_seconds,
            expected_digest,
            path,
            diagnostics,
            runner_kind,
        )


def _valid_linker_coverage(value: Any) -> bool:
    if not isinstance(value, Mapping) or set(value) != LINKER_COVERAGE_FIELDS:
        return False
    if (value.get("mode") not in {"discovered", "full", "subset"}
            or type(value.get("complete")) is not bool
            or not _digest(value.get("path_digest"))):
        return False
    lists = {}
    for field in LINKER_COVERAGE_LIST_FIELDS:
        items = value.get(field)
        if (not isinstance(items, list)
                or not all(_text(item) for item in items)
                or items != sorted(set(items))):
            return False
        lists[field] = items
    counts = value.get("counts")
    count_fields = {
        "discovered", "parsed", "omitted", "declared_only", "skipped",
    }
    if (not isinstance(counts, Mapping) or set(counts) != count_fields
            or any(type(counts.get(field)) is not int or counts[field] < 0
                   for field in count_fields)):
        return False
    for field in count_fields:
        if counts[field] != len(lists[field + "_sources"]):
            return False
    discovered = set(lists["discovered_sources"])
    parsed = set(lists["parsed_sources"])
    omitted = set(lists["omitted_sources"])
    declared_only = set(lists["declared_only_sources"])
    skipped = set(lists["skipped_sources"])
    if (not parsed <= discovered
            or not omitted <= parsed
            or not skipped <= discovered
            or parsed & skipped
            or declared_only & discovered):
        return False
    if value["complete"] and (
        discovered != parsed or omitted or declared_only or skipped
    ):
        return False
    return True


def _valid_runner_envelope(
    payload: Any, returncode: int, runner_kind: str
) -> bool:
    schema_version = payload.get("schema_version") if isinstance(payload, Mapping) else None
    if (not isinstance(payload, Mapping) or type(schema_version) is not int
            or schema_version != 1):
        return False
    expected_fields = set(RUNNER_ENVELOPE_FIELDS)
    if runner_kind == "linker" and "coverage" in payload:
        if not _valid_linker_coverage(payload["coverage"]):
            return False
        expected_fields.add("coverage")
    elif runner_kind != "author" and runner_kind != "linker":
        return False
    if set(payload) != expected_fields:
        return False
    diagnostics = payload.get("diagnostics")
    summary = payload.get("summary")
    if not isinstance(diagnostics, list) or not isinstance(summary, Mapping):
        return False
    if not all(
        isinstance(item, Mapping)
        and frozenset(item) in {
            frozenset(RUNNER_DIAGNOSTIC_FIELDS),
            frozenset(RUNNER_DIAGNOSTIC_FIELDS | {"path"}),
        }
        and item.get("severity") in {"error", "warning"}
        and _text(item.get("code"))
        and _text(item.get("message"))
        and ("path" not in item or _text(item.get("path")))
        for item in diagnostics
    ):
        return False
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    expected_status = {0: "pass", 1: "fail", 2: "error"}.get(returncode)
    return (
        expected_status is not None
        and payload.get("status") == expected_status
        and set(summary) == {"errors", "warnings"}
        and type(summary.get("errors")) is int
        and type(summary.get("warnings")) is int
        and summary == {"errors": errors, "warnings": warnings}
    )


def _run_evidence(
    command: Sequence[str], timeout_seconds: float, expected_digest: Any,
    path: str, diagnostics: List[Diagnostic], runner_kind: str,
    *, isolated: bool = False,
) -> Optional[Mapping[str, Any]]:
    run_options: Dict[str, Any] = {}
    if isolated:
        environment = {"PATH": os.defpath}
        for name in ("SYSTEMROOT", "WINDIR"):
            if name in os.environ:
                environment[name] = os.environ[name]
        run_options["env"] = environment
    try:
        process = subprocess.run(
            list(command), check=False, capture_output=True, text=True,
            timeout=timeout_seconds, **run_options,
        )
    except subprocess.TimeoutExpired:
        diagnostics.append(diagnostic("runner_timeout", "Evidence runner timed out.", path))
        return None
    except (OSError, subprocess.SubprocessError) as error:
        diagnostics.append(diagnostic("runner_execution_failed", str(error), path))
        return None
    try:
        payload = _loads_json_strict(process.stdout)
    except (json.JSONDecodeError, TypeError, DuplicateJsonKey, NonfiniteJsonValue):
        diagnostics.append(diagnostic("runner_output_malformed", "Runner output is not JSON.", path))
        return None
    if not _valid_runner_envelope(payload, process.returncode, runner_kind):
        diagnostics.append(diagnostic("runner_output_malformed",
                                      "Runner envelope and exit code are inconsistent.", path))
        return None
    if digest_json(payload) != expected_digest:
        diagnostics.append(diagnostic("runner_envelope_digest_mismatch",
                                      "Runner output is not bound to the recorded envelope digest.", path))
    if payload.get("status") == "error":
        diagnostics.append(diagnostic(
            "runner_reported_error",
            "The package-owned evidence runner reported an execution error.",
            path,
        ))
    return payload


def _generic_sync(
    name: str, value: Mapping[str, Any], diagnostics: List[Diagnostic]
) -> None:
    _unknown_fields(value, {"disposition", "state", "reason", "evidence"},
                    f"keystone_closure.{name}", diagnostics)
    disposition = value.get("disposition")
    state = value.get("state")
    if disposition not in SYNC_DISPOSITIONS:
        diagnostics.append(diagnostic(f"{name}_disposition_invalid", "Invalid sync disposition.",
                                      f"keystone_closure.{name}.disposition"))
        return
    expected = {
        "required": {"complete"},
        "not_applicable": {"not_applicable"},
        "deferred": {"pending", "blocked"},
    }
    if state not in expected[disposition]:
        diagnostics.append(diagnostic(f"{name}_incomplete", "Sync state is not closed.",
                                      f"keystone_closure.{name}.state"))
    if not _text(value.get("reason")) or not _evidence(value.get("evidence")):
        diagnostics.append(diagnostic(f"{name}_evidence_missing",
                                      "Sync disposition requires reason and evidence.",
                                      f"keystone_closure.{name}"))
    if disposition == "deferred":
        diagnostics.append(diagnostic(f"{name}_deferred", "Deferred sync prevents closure.",
                                      f"keystone_closure.{name}"))


def _delta_projection(delta: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "kind": delta.get("kind"),
        "source_surface": delta.get("source_surface"),
        "changed_locators": delta.get("changed_locators"),
        "semantic_summary": delta.get("semantic_summary"),
        "baseline_digest": delta.get("baseline_digest"),
        "graph_relevant": delta.get("graph_relevant"),
    }


def _validate_graph_sync(
    value: Mapping[str, Any], deltas: List[Mapping[str, Any]], root: Path,
    evidence_root: Path, linker_runner: Path, timeout_seconds: float,
    diagnostics: List[Diagnostic]
) -> None:
    disposition = value.get("disposition")
    if disposition == "required":
        allowed = {
            "disposition", "state", "reason", "validation_manifest_path",
            "validation_manifest_digest", "transaction_id", "delta_set_digest",
            "envelope_digest",
        }
    elif disposition == "not_applicable":
        allowed = {
            "disposition", "state", "reason", "classification_path",
            "classification_digest", "delta_set_digest",
        }
    else:
        allowed = {"disposition", "state", "reason", "evidence"}
    _unknown_fields(value, allowed, "keystone_closure.graph_sync", diagnostics)
    if disposition not in SYNC_DISPOSITIONS:
        diagnostics.append(diagnostic("graph_sync_disposition_invalid", "Invalid graph disposition.",
                                      "keystone_closure.graph_sync.disposition"))
        return
    if not _text(value.get("reason")):
        diagnostics.append(diagnostic("graph_sync_reason_missing", "Graph sync requires a reason.",
                                      "keystone_closure.graph_sync.reason"))
    expected_delta_digest = digest_json(deltas)
    if value.get("delta_set_digest") != expected_delta_digest:
        diagnostics.append(diagnostic("graph_delta_set_mismatch",
                                      "Graph evidence is not bound to the exact artifact delta set.",
                                      "keystone_closure.graph_sync.delta_set_digest"))
    if disposition == "deferred":
        diagnostics.append(diagnostic("graph_sync_deferred", "Deferred graph sync prevents closure.",
                                      "keystone_closure.graph_sync"))
        return
    if disposition == "not_applicable":
        if value.get("state") != "not_applicable":
            diagnostics.append(diagnostic("graph_sync_incomplete", "Graph state is not closed.",
                                          "keystone_closure.graph_sync.state"))
        _, classification, _ = _read_evidence_json(
            evidence_root, value.get("classification_path"),
            value.get("classification_digest"),
            "keystone_closure.graph_sync.classification_path", diagnostics,
        )
        if classification is not None:
            _unknown_fields(classification,
                            {"schema_version", "disposition", "delta_set_digest", "reason"},
                            "graph_classification", diagnostics)
            if (
                type(classification.get("schema_version")) is not int
                or classification.get("schema_version") != 1
                or classification.get("disposition") != "not_applicable"
                or classification.get("delta_set_digest") != expected_delta_digest
                or classification.get("reason") != value.get("reason")
            ):
                diagnostics.append(diagnostic("graph_classification_mismatch",
                                              "Linker classification does not match closure evidence.",
                                              "keystone_closure.graph_sync"))
        return

    if value.get("state") != "verified":
        diagnostics.append(diagnostic("graph_sync_incomplete", "Required graph sync must be verified.",
                                      "keystone_closure.graph_sync.state"))
    graph_path, graph_manifest, graph_manifest_bytes = _read_evidence_json(
        evidence_root, value.get("validation_manifest_path"),
        value.get("validation_manifest_digest"),
        "keystone_closure.graph_sync.validation_manifest_path", diagnostics,
    )
    if graph_manifest is None or graph_path is None or graph_manifest_bytes is None:
        return
    transaction = _mapping(graph_manifest.get("transaction"))
    transaction_schema = transaction.get("schema_version")
    if type(transaction_schema) is not int or transaction_schema != 2:
        diagnostics.append(diagnostic(
            "graph_transaction_schema_not_authoritative",
            "New Coordinator closure requires a canonical schema-v2 graph transaction.",
            "keystone_closure.graph_sync.validation_manifest_path",
        ))
    if (
        transaction.get("transaction_id") != value.get("transaction_id")
        or transaction.get("state") != "verified"
    ):
        diagnostics.append(diagnostic("graph_transaction_mismatch",
                                      "Graph evidence must reference the same verified transaction.",
                                      "keystone_closure.graph_sync.transaction_id"))
    expected_inputs = sorted(
        (_delta_projection(delta) for delta in deltas),
        key=lambda item: str(item.get("source_surface")),
    )
    actual_inputs = sorted(
        _list(transaction.get("input_deltas")),
        key=lambda item: str(_mapping(item).get("source_surface")),
    )
    if actual_inputs != expected_inputs:
        diagnostics.append(diagnostic("graph_transaction_delta_mismatch",
                                      "Graph transaction inputs must equal worker artifact deltas.",
                                      "keystone_closure.graph_sync.validation_manifest_path"))
    if not linker_runner.is_file():
        diagnostics.append(diagnostic("linker_runner_unavailable", "Linker runner is unavailable.",
                                      "keystone_closure.graph_sync"))
        return
    payload = _run_captured_manifest(
        linker_runner, root, graph_manifest_bytes, timeout_seconds,
        value.get("envelope_digest"),
        "keystone_closure.graph_sync.envelope_digest", diagnostics, "linker",
    )
    if payload is not None and payload.get("status") != "pass":
        diagnostics.append(diagnostic("linker_runner_failed",
                                      "Required Linker validation did not pass.",
                                      "keystone_closure.graph_sync"))


def _validate_finalization(
    phase: Any, closure: Mapping[str, Any], value: Mapping[str, Any],
    assignment_steps: List[str], evidence_root: Path, root: Path,
    author_runner: Path, timeout_seconds: float, diagnostics: List[Diagnostic],
    *, runner_arguments: Sequence[str] = (), isolated: bool = False,
) -> Optional[str]:
    if phase == "pre_acceptance":
        _unknown_fields(value, {"state", "evidence"},
                        "keystone_closure.finalization", diagnostics)
        if value.get("state") not in {"not_started", "in_progress"}:
            diagnostics.append(diagnostic("pre_acceptance_finalization_invalid",
                                          "Pre-acceptance finalization is not complete authority.",
                                          "keystone_closure.finalization.state"))
        if not isinstance(value.get("evidence"), list):
            diagnostics.append(diagnostic("finalization_evidence_invalid",
                                          "Finalization evidence must be an array.",
                                          "keystone_closure.finalization.evidence"))
        return None

    allowed = {
        "state", "acceptance_ref", "evidence", "manifest_path", "manifest_digest",
        "envelope_digest", "runner_status", "waiver_reason",
    }
    _unknown_fields(value, allowed, "keystone_closure.finalization", diagnostics)
    _require_text_fields(value, ("state", "acceptance_ref", "manifest_path", "manifest_digest",
                                 "envelope_digest", "runner_status"),
                         "keystone_closure.finalization", diagnostics)
    if not _evidence(value.get("evidence")):
        diagnostics.append(diagnostic("finalization_evidence_missing",
                                      "Post-acceptance finalization requires evidence.",
                                      "keystone_closure.finalization.evidence"))
    manifest_path, finalization_manifest, finalization_manifest_bytes = _read_evidence_json(
        evidence_root, value.get("manifest_path"), value.get("manifest_digest"),
        "keystone_closure.finalization.manifest_path", diagnostics,
    )
    if (
        finalization_manifest is None
        or manifest_path is None
        or finalization_manifest_bytes is None
    ):
        return None
    author_schema = finalization_manifest.get("schema_version")
    if type(author_schema) is not int or author_schema not in {5, 6}:
        diagnostics.append(diagnostic("author_manifest_schema_invalid",
                                      "Coordinator v2 requires canonical Author schema 5 or 6 evidence.",
                                      "keystone_closure.finalization.manifest_path"))
    acceptance_ref = closure.get("acceptance_ref")
    refs = {
        acceptance_ref,
        value.get("acceptance_ref"),
        finalization_manifest.get("acceptance_ref"),
    }
    if len(refs) != 1 or None in refs or "" in refs:
        diagnostics.append(diagnostic("acceptance_ref_mismatch",
                                      "Closure, finalization, and Author acceptance refs must match.",
                                      "keystone_closure.acceptance_ref"))
    accepted_steps = closure.get("accepted_steps")
    accepted_steps_valid = bool(
        isinstance(accepted_steps, list)
        and accepted_steps
        and all(_text(step) for step in accepted_steps)
        and len(set(accepted_steps)) == len(accepted_steps)
    )
    raw_author_steps = finalization_manifest.get("steps")
    author_step_refs = [
        item.get("ref") for item in raw_author_steps
        if isinstance(item, Mapping)
    ] if isinstance(raw_author_steps, list) else []
    raw_author_active_steps = finalization_manifest.get("active_steps", [])
    author_active_steps = (
        list(raw_author_active_steps)
        if isinstance(raw_author_active_steps, list)
        else []
    )
    author_steps_valid = bool(
        isinstance(raw_author_steps, list)
        and len(author_step_refs) == len(raw_author_steps)
        and all(_text(step) for step in author_step_refs)
        and len(set(author_step_refs)) == len(author_step_refs)
    )
    author_active_steps_valid = bool(
        isinstance(raw_author_active_steps, list)
        and all(_text(step) for step in author_active_steps)
        and len(set(author_active_steps)) == len(author_active_steps)
    )
    expected_author_steps = set(accepted_steps if accepted_steps_valid else ())
    expected_author_steps.update(
        author_active_steps if author_active_steps_valid else ()
    )
    if (
        not accepted_steps_valid
        or not author_steps_valid
        or not author_active_steps_valid
        or set(accepted_steps) & set(author_active_steps)
        or set(author_step_refs) != expected_author_steps
        or accepted_steps != finalization_manifest.get("accepted_steps")
        or any(step not in assignment_steps for step in accepted_steps)
    ):
        diagnostics.append(diagnostic("accepted_steps_mismatch",
                                      "Accepted Steps must match Author evidence and assignment "
                                      "scope; additional Author Steps must be exact active siblings.",
                                      "keystone_closure.accepted_steps"))
    author_state = _mapping(finalization_manifest.get("finalization")).get("state")
    if value.get("state") != author_state:
        diagnostics.append(diagnostic("finalization_state_mismatch",
                                      "Coordinator finalization state must match Author evidence.",
                                      "keystone_closure.finalization.state"))
    if value.get("state") == "waived" and not _text(value.get("waiver_reason")):
        diagnostics.append(diagnostic("finalization_waiver_reason_missing",
                                      "A waived finalization requires a reason.",
                                      "keystone_closure.finalization.waiver_reason"))
    if not author_runner.is_file():
        diagnostics.append(diagnostic("author_runner_unavailable", "Author runner is unavailable.",
                                      "keystone_closure.finalization"))
        return None
    payload = _run_captured_manifest(
        author_runner, root, finalization_manifest_bytes, timeout_seconds,
        value.get("envelope_digest"),
        "keystone_closure.finalization.envelope_digest", diagnostics, "author",
        runner_arguments=runner_arguments,
        isolated=isolated,
    )
    if payload is not None and payload.get("status") != value.get("runner_status"):
        diagnostics.append(diagnostic("author_runner_status_mismatch",
                                      "Author runner status differs from recorded evidence.",
                                      "keystone_closure.finalization.runner_status"))
    return payload.get("status") if payload else None


def validate_sync_evidence(
    name: str, value: Mapping[str, Any], diagnostics: List[Diagnostic]
) -> None:
    """Validate one document/metadata sync result for closure schema consumers."""

    _generic_sync(name, value, diagnostics)


def validate_assignment_context_evidence(
    context: Mapping[str, Any],
    closure_target: Any,
    closure_step_ref: Any,
    diagnostics: List[Diagnostic],
) -> None:
    """Validate the shared immutable Context Pack and dependency-gate projection."""

    _validate_context(context, closure_target, closure_step_ref, diagnostics)


def validate_graph_sync_evidence(
    value: Mapping[str, Any],
    deltas: List[Mapping[str, Any]],
    root: Path,
    evidence_root: Path,
    linker_runner: Path,
    timeout_seconds: float,
    diagnostics: List[Diagnostic],
) -> None:
    """Validate Linker evidence without exposing schema-v2 private helpers."""

    _validate_graph_sync(
        value,
        deltas,
        root,
        evidence_root,
        linker_runner,
        timeout_seconds,
        diagnostics,
    )


def validate_finalization_evidence(
    phase: Any,
    closure: Mapping[str, Any],
    value: Mapping[str, Any],
    assignment_steps: List[str],
    evidence_root: Path,
    root: Path,
    author_runner: Path,
    timeout_seconds: float,
    diagnostics: List[Diagnostic],
    *,
    runner_arguments: Sequence[str] = (),
    isolated: bool = False,
) -> Optional[str]:
    """Validate Author finalization evidence for a closure schema consumer."""

    return _validate_finalization(
        phase,
        closure,
        value,
        assignment_steps,
        evidence_root,
        root,
        author_runner,
        timeout_seconds,
        diagnostics,
        runner_arguments=runner_arguments,
        isolated=isolated,
    )


def validate_v2(
    manifest: Mapping[str, Any], *, root: Path, assignment: Mapping[str, Any],
    assignment_digest: str, evidence_root: Path, linker_runner: Path,
    author_runner: Path, timeout_seconds: float
) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []
    canonical_linker, canonical_author = package_runner_paths()
    for name, supplied, canonical in (
        ("linker_runner", linker_runner, canonical_linker),
        ("author_runner", author_runner, canonical_author),
    ):
        try:
            resolved = Path(supplied).resolve()
        except (OSError, TypeError, ValueError):
            resolved = None
        if resolved != canonical:
            diagnostics.append(diagnostic(
                "v2_runner_override_forbidden",
                "Schema v2 evidence runners must be package-owned sibling runners.",
                name,
            ))
    linker_runner = canonical_linker
    author_runner = canonical_author
    _unknown_fields(
        manifest,
        {"schema_version", "closure_phase", "closure_target", "worker_report",
         "closure_step_ref", "keystone_closure", "coordinator_review"},
        "", diagnostics,
    )
    manifest_fields = {
        "schema_version", "closure_phase", "closure_target", "worker_report",
        "keystone_closure", "coordinator_review",
    }
    _missing_fields(manifest, manifest_fields, "", diagnostics)
    manifest_schema = manifest.get("schema_version")
    if type(manifest_schema) is not int or manifest_schema != 2:
        diagnostics.append(diagnostic("schema_version_invalid", "Manifest schema_version must be 2.",
                                      "schema_version"))
    phase = manifest.get("closure_phase")
    if phase not in {"pre_acceptance", "post_acceptance"}:
        diagnostics.append(diagnostic("closure_phase_invalid", "Invalid closure phase.", "closure_phase"))
    target = manifest.get("closure_target")
    if target not in {"step", "work"}:
        diagnostics.append(diagnostic("closure_target_invalid", "closure_target must be step or work.",
                                      "closure_target"))
    closure_step_ref = manifest.get("closure_step_ref")
    if target == "step" and not _text(closure_step_ref):
        diagnostics.append(diagnostic(
            "closure_step_ref_missing",
            "Step closure requires one concrete closure_step_ref.",
            "closure_step_ref",
        ))
    elif target == "work" and closure_step_ref is not None:
        diagnostics.append(diagnostic(
            "closure_step_ref_unexpected",
            "Work closure must not declare closure_step_ref.",
            "closure_step_ref",
        ))
    if not _digest(assignment_digest):
        diagnostics.append(diagnostic(
            "assignment_digest_invalid",
            "Assignment digest must be a canonical SHA-256 value supplied by the host.",
            "worker_report.assignment_digest",
        ))

    for field in ("worker_report", "keystone_closure", "coordinator_review"):
        if not isinstance(manifest.get(field), Mapping):
            diagnostics.append(diagnostic(
                "authoritative_field_type_invalid",
                "%s must be an object in schema v2." % field,
                field,
            ))

    context, scope, baseline = _validate_assignment(
        assignment, target, closure_step_ref, diagnostics
    )
    assignment_steps = _list(_mapping(context.get("work_context")).get("step_refs"))
    if target == "step" and _text(closure_step_ref) and closure_step_ref not in assignment_steps:
        diagnostics.append(diagnostic(
            "closure_step_ref_out_of_scope",
            "closure_step_ref must be present in assignment work context.",
            "closure_step_ref",
        ))
    try:
        root = resolved_repository_root(root)
    except (OSError, RuntimeError) as error:
        diagnostics.append(diagnostic("repository_root_unavailable", str(error), "--root"))
        return diagnostics
    try:
        evidence_root = evidence_root.resolve(strict=True)
        if not evidence_root.is_dir():
            raise NotADirectoryError(str(evidence_root))
    except (OSError, RuntimeError) as error:
        diagnostics.append(diagnostic("evidence_root_unavailable", str(error), "--evidence-root"))
        return diagnostics
    try:
        evidence_root.relative_to(root)
    except ValueError:
        pass
    else:
        diagnostics.append(diagnostic(
            "evidence_root_inside_repository",
            "Authority evidence must be stored outside the repository snapshot.",
            "--evidence-root",
        ))
    try:
        root.relative_to(evidence_root)
    except ValueError:
        pass
    else:
        diagnostics.append(diagnostic(
            "evidence_root_contains_repository",
            "Authority evidence root must not contain the repository tree.",
            "--evidence-root",
        ))
    try:
        current = repository_snapshot(root)
    except (OSError, RuntimeError, UnicodeError) as error:
        diagnostics.append(diagnostic("repository_snapshot_failed", str(error), "--root"))
        return diagnostics
    try:
        symlinks = repository_symlinks(root)
    except (OSError, RuntimeError) as error:
        diagnostics.append(diagnostic("repository_symlink_scan_failed", str(error), "--root"))
        return diagnostics
    for path, (_, escapes) in symlinks.items():
        if escapes and path_overlaps_scope(path, scope.get("allowed_edit_scope", [])):
            diagnostics.append(
                diagnostic(
                    "symlink_scope_escape",
                    f"Allowed edit scope contains a symlink that escapes the repository: {path}.",
                    "assignment.scope.allowed_edit_scope",
                )
            )
    report = _mapping(manifest.get("worker_report"))
    deltas = _validate_report(
        report, assignment, assignment_digest, context, scope, baseline, current, diagnostics
    )

    closure = _mapping(manifest.get("keystone_closure"))
    closure_allowed = {"document_sync", "metadata_sync", "graph_sync", "finalization"}
    if phase == "post_acceptance":
        closure_allowed |= {"acceptance_ref", "acceptance_evidence", "accepted_steps"}
    _unknown_fields(closure, closure_allowed, "keystone_closure", diagnostics)
    for name in ("document_sync", "metadata_sync"):
        _generic_sync(name, _mapping(closure.get(name)), diagnostics)
    _validate_graph_sync(
        _mapping(closure.get("graph_sync")), deltas, root, evidence_root,
        linker_runner, timeout_seconds, diagnostics,
    )
    author_status = _validate_finalization(
        phase, closure, _mapping(closure.get("finalization")), assignment_steps,
        evidence_root, root, author_runner, timeout_seconds, diagnostics,
    )

    if phase == "post_acceptance":
        if not _text(closure.get("acceptance_ref")) or not _evidence(closure.get("acceptance_evidence")):
            diagnostics.append(diagnostic("acceptance_evidence_missing",
                                          "Post-acceptance closure requires acceptance evidence.",
                                          "keystone_closure.acceptance_ref"))

    review = _mapping(manifest.get("coordinator_review"))
    _unknown_fields(review,
                    {"assignment_id", "assignment_digest", "decision",
                     "main_acceptance_allowed", "evidence"},
                    "coordinator_review", diagnostics)
    if review.get("assignment_id") != assignment.get("assignment_id"):
        diagnostics.append(diagnostic("review_assignment_id_mismatch",
                                      "Review is not bound to the assignment.",
                                      "coordinator_review.assignment_id"))
    if review.get("assignment_digest") != assignment_digest:
        diagnostics.append(diagnostic("review_assignment_digest_mismatch",
                                      "Review is not bound to immutable assignment bytes.",
                                      "coordinator_review.assignment_digest"))
    if not _evidence(review.get("evidence")):
        diagnostics.append(diagnostic("coordinator_review_evidence_missing",
                                      "Coordinator review requires evidence.",
                                      "coordinator_review.evidence"))
    decision = review.get("decision")
    if phase == "pre_acceptance":
        if decision not in {"accept_candidate", "repair", "review", "verify", "escalate", "block"}:
            diagnostics.append(diagnostic("coordinator_decision_invalid", "Invalid pre-acceptance decision.",
                                          "coordinator_review.decision"))
        if decision == "accept_candidate" and (
            report.get("status") != "DONE" or review.get("main_acceptance_allowed") is not True
        ):
            diagnostics.append(diagnostic("accept_candidate_not_ready",
                                          "accept_candidate requires DONE and an explicit Main gate.",
                                          "coordinator_review.decision"))
        if decision != "accept_candidate" and review.get("main_acceptance_allowed") is not False:
            diagnostics.append(diagnostic("main_acceptance_gate_invalid",
                                          "Non-candidate decisions cannot allow Main acceptance.",
                                          "coordinator_review.main_acceptance_allowed"))
    else:
        if decision not in {"closure_complete", "repair", "escalate", "block"}:
            diagnostics.append(diagnostic("coordinator_decision_invalid", "Invalid post-acceptance decision.",
                                          "coordinator_review.decision"))
        if review.get("main_acceptance_allowed") is not False:
            diagnostics.append(diagnostic("main_acceptance_gate_invalid",
                                          "Post-acceptance closure cannot reopen Main acceptance.",
                                          "coordinator_review.main_acceptance_allowed"))
        if decision == "closure_complete" and (
            report.get("status") != "DONE"
            or _mapping(closure.get("finalization")).get("state") not in {"complete", "waived"}
            or author_status != "pass"
        ):
            diagnostics.append(diagnostic("post_acceptance_closure_incomplete",
                                          "closure_complete requires passing Author evidence.",
                                          "coordinator_review.decision"))
    if decision in {"accept_candidate", "closure_complete"}:
        diagnostics.append(diagnostic(
            "legacy_schema_not_authoritative",
            "Coordinator closure schema v2 is historical diagnostic compatibility only; "
            "authority-bearing success requires schema v3.",
            "schema_version",
        ))
    return diagnostics
