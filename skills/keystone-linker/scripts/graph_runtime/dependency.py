"""Structured dependency and work-gate parsing and evaluation."""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence, Tuple


class DependencyStatus(str, Enum):
    SATISFIED = "satisfied"
    WAITING = "waiting"
    UNRESOLVABLE = "unresolvable"
    INVALID = "invalid"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class WorkGate:
    dependency: str
    steps: Tuple[str, ...] = ()
    work_completion: bool = False
    required_work_status: str = "complete"
    required_approval_state: str = "accepted"
    optional: bool = False


@dataclass(frozen=True)
class DependencyTargetState:
    work_status: str = ""
    approval_state: str = ""
    exists: bool = True


@dataclass(frozen=True)
class DependencyEvaluation:
    dependency: str
    status: DependencyStatus
    blocking: bool
    reason: str


def parse_work_gates(raw, declared_dependencies: Sequence[str], source_id: str):
    """Parse canonical work_gates and return gates plus stable diagnostic tuples."""
    if raw in (None, {}):
        return (), ()
    if not isinstance(raw, list):
        return (), (("work_gates_invalid", "work_gates must be an array"),)
    declared = set(declared_dependencies)
    gates = []
    diagnostics = []
    seen = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            diagnostics.append(("work_gate_invalid", "work_gates[%d] must be a mapping" % index))
            continue
        dependency = item.get("dependency")
        applies = item.get("applies_to", {})
        condition = item.get("condition", {})
        steps = applies.get("steps", ()) if isinstance(applies, dict) else ()
        work_completion = applies.get("work_completion", False) if isinstance(applies, dict) else False
        optional = item.get("optional", False)
        if not isinstance(steps, list) or not all(isinstance(step, str) and step for step in steps):
            diagnostics.append(("work_gate_steps_invalid", "work_gates[%d] steps must be strings" % index))
            continue
        if not isinstance(work_completion, bool) or (not steps and not work_completion):
            diagnostics.append(("work_gate_scope_invalid", "work_gates[%d] requires steps or work_completion" % index))
            continue
        if not isinstance(optional, bool):
            diagnostics.append(("work_gate_optional_invalid", "work_gates[%d] optional must be boolean" % index))
            continue
        work_status = condition.get("work_status") if isinstance(condition, dict) else None
        approval_state = condition.get("approval_state") if isinstance(condition, dict) else None
        legacy_approval = condition.get("approval", {}) if isinstance(condition, dict) else {}
        legacy_approval_state = (legacy_approval.get("state")
                                 if isinstance(legacy_approval, dict) else None)
        if approval_state is None:
            approval_state = legacy_approval_state
        elif legacy_approval_state is not None and legacy_approval_state != approval_state:
            diagnostics.append(("work_gate_condition_conflict",
                                "work_gates[%d] approval conditions conflict" % index))
        if work_status != "complete" or approval_state != "accepted":
            diagnostics.append(("work_gate_condition_invalid",
                                "work_gates[%d] requires complete and accepted" % index))
            continue
        if not isinstance(dependency, str) or not dependency:
            diagnostics.append(("work_gate_dependency_invalid", "work_gates[%d] requires dependency" % index))
            continue
        if dependency == source_id:
            diagnostics.append(("work_gate_self_reference", "work gate cannot depend on its source"))
        if dependency not in declared:
            diagnostics.append(("work_gate_dependency_undeclared",
                                "work gate dependency is not declared by depends_on: %s" % dependency))
        identity = (dependency, tuple(steps), work_completion)
        if identity in seen:
            diagnostics.append(("work_gate_duplicate", "work gate is duplicated: %s" % dependency))
            continue
        seen.add(identity)
        gates.append(WorkGate(dependency, tuple(steps), work_completion,
                              work_status, approval_state, optional))
    return tuple(gates), tuple(diagnostics)


def evaluate_work_gates(gates: Sequence[WorkGate],
                        targets: Mapping[str, DependencyTargetState]):
    evaluations = []
    for gate in gates:
        target = targets.get(gate.dependency)
        if target is None or not target.exists:
            status, reason = DependencyStatus.UNRESOLVABLE, "dependency target is unavailable"
        elif not target.work_status or not target.approval_state:
            status, reason = DependencyStatus.UNKNOWN, "dependency target state is incomplete"
        elif (target.work_status == gate.required_work_status
              and target.approval_state == gate.required_approval_state):
            status, reason = DependencyStatus.SATISFIED, "dependency is complete and accepted"
        elif target.work_status in {"cancelled", "superseded"}:
            status, reason = DependencyStatus.UNRESOLVABLE, "terminal dependency needs an accepted exception"
        else:
            status, reason = DependencyStatus.WAITING, "dependency is not complete and accepted"
        evaluations.append(DependencyEvaluation(
            gate.dependency, status,
            not gate.optional and status != DependencyStatus.SATISFIED,
            reason,
        ))
    return tuple(evaluations)
