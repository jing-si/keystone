"""Structured dependency parsing, registry validation, and event-graph evaluation."""

from dataclasses import dataclass, replace
from enum import Enum
from typing import Dict, Mapping, Optional, Sequence, Set, Tuple


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
    gate_id: str = ""
    source_id: str = ""
    origin: str = "structured"
    invalid_codes: Tuple[str, ...] = ()


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
    gate_id: str = ""
    source_id: str = ""
    steps: Tuple[str, ...] = ()
    work_completion: bool = False
    optional: bool = False
    origin: str = "structured"
    target_work_status: str = ""
    target_approval_state: str = ""
    cycle_events: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DependencyDiagnostic:
    code: str
    message: str
    gate_id: str = ""


@dataclass(frozen=True)
class DependencyCycle:
    events: Tuple[str, ...]
    gate_ids: Tuple[str, ...]


@dataclass(frozen=True)
class DependencyGraphResult:
    evaluations: Tuple[DependencyEvaluation, ...] = ()
    diagnostics: Tuple[DependencyDiagnostic, ...] = ()
    cycles: Tuple[DependencyCycle, ...] = ()


@dataclass(frozen=True)
class DependencySource:
    source_id: str
    path: str
    work_status: str = ""
    approval_state: str = ""
    step_ref: str = ""
    work_ref: str = ""
    structured_dependencies: Tuple[str, ...] = ()
    legacy_dependencies: Tuple[str, ...] = ()
    gates: Tuple[WorkGate, ...] = ()
    is_work: bool = False


def parse_work_gates(raw, declared_dependencies: Sequence[str], source_id: str):
    """Parse canonical work_gates and return gates plus stable diagnostic tuples."""
    if raw is None:
        return (), ()
    if not isinstance(raw, list):
        return (), (("work_gates_invalid", "work_gates must be an array"),)
    declared = set(declared_dependencies)
    gates = []
    diagnostics = []
    seen: Dict[Tuple[str, Tuple[str, ...], bool], int] = {}
    seen_ids: Dict[str, int] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            diagnostics.append(("work_gate_invalid", "work_gates[%d] must be a mapping" % index))
            continue
        dependency = item.get("dependency")
        if not isinstance(dependency, str) or not dependency:
            diagnostics.append(("work_gate_dependency_invalid",
                                "work_gates[%d] requires dependency" % index))
            continue
        generated_id = "%s#gate-%03d" % (source_id, index + 1)
        gate_id = item.get("id", generated_id)
        invalid_codes = []
        for field in sorted(
            set(item) - {"id", "dependency", "applies_to", "condition", "optional"}
        ):
            diagnostics.append((
                "work_gate_field_unknown",
                "work_gates[%d] field is unknown: %s" % (index, field),
            ))
            invalid_codes.append("work_gate_schema_invalid")
        if not isinstance(gate_id, str) or not gate_id.strip():
            diagnostics.append(("work_gate_id_invalid",
                                "work_gates[%d] id must be a non-empty string" % index))
            gate_id = generated_id
            invalid_codes.append("work_gate_id_invalid")
        applies = item.get("applies_to", {})
        condition = item.get("condition", {})
        if isinstance(applies, dict):
            for field in sorted(set(applies) - {"steps", "work_completion"}):
                diagnostics.append((
                    "work_gate_scope_field_unknown",
                    "work_gates[%d] applies_to field is unknown: %s"
                    % (index, field),
                ))
                invalid_codes.append("work_gate_schema_invalid")
        else:
            diagnostics.append((
                "work_gate_scope_invalid",
                "work_gates[%d] applies_to must be a mapping" % index,
            ))
            invalid_codes.append("work_gate_scope_invalid")
        steps = applies.get("steps", ()) if isinstance(applies, dict) else ()
        work_completion = applies.get("work_completion", False) if isinstance(applies, dict) else False
        optional = item.get("optional", False)
        if not isinstance(steps, list) or not all(isinstance(step, str) and step for step in steps):
            diagnostics.append(("work_gate_steps_invalid",
                                "work_gates[%d] steps must be strings" % index))
            continue
        if not isinstance(work_completion, bool) or (not steps and not work_completion):
            diagnostics.append(("work_gate_scope_invalid",
                                "work_gates[%d] requires steps or work_completion" % index))
            continue
        if not isinstance(optional, bool):
            diagnostics.append(("work_gate_optional_invalid",
                                "work_gates[%d] optional must be boolean" % index))
            continue

        work_status = condition.get("work_status") if isinstance(condition, dict) else None
        approval_state = condition.get("approval_state") if isinstance(condition, dict) else None
        legacy_present = isinstance(condition, dict) and "approval" in condition
        legacy_approval = condition.get("approval", {}) if legacy_present else {}
        legacy_approval_state = (legacy_approval.get("state")
                                 if isinstance(legacy_approval, dict) else None)
        if not isinstance(condition, dict):
            diagnostics.append(("work_gate_condition_invalid",
                                "work_gates[%d] condition must be a mapping" % index))
            invalid_codes.append("work_gate_condition_invalid")
        else:
            unknown_condition_fields = set(condition) - {"work_status", "approval_state", "approval"}
            for field in sorted(unknown_condition_fields):
                diagnostics.append(("work_gate_condition_field_unknown",
                                    "work_gates[%d] condition field is unknown: %s"
                                    % (index, field)))
                invalid_codes.append("work_gate_condition_invalid")
        if legacy_present:
            diagnostics.append(("work_gate_approval_schema_legacy",
                                "work_gates[%d] must use condition.approval_state" % index))
            invalid_codes.append("work_gate_condition_invalid")
        if (approval_state is not None and legacy_approval_state is not None
                and legacy_approval_state != approval_state):
            diagnostics.append(("work_gate_condition_conflict",
                                "work_gates[%d] approval conditions conflict" % index))
            invalid_codes.append("work_gate_condition_conflict")
        if work_status != "complete" or approval_state != "accepted":
            diagnostics.append(("work_gate_condition_invalid",
                                "work_gates[%d] requires complete and accepted" % index))
            invalid_codes.append("work_gate_condition_invalid")
        if dependency == source_id:
            diagnostics.append(("work_gate_self_reference", "work gate cannot depend on its source"))
            invalid_codes.append("work_gate_self_reference")
        if dependency not in declared:
            diagnostics.append(("work_gate_dependency_undeclared",
                                "work gate dependency is not declared by depends_on: %s" % dependency))
            invalid_codes.append("work_gate_dependency_undeclared")

        if gate_id in seen_ids:
            diagnostics.append(("work_gate_id_duplicate", "work gate id is duplicated: %s" % gate_id))
            invalid_codes.append("work_gate_id_duplicate")
            prior = seen_ids[gate_id]
            gates[prior] = replace(
                gates[prior],
                invalid_codes=tuple(sorted(set(gates[prior].invalid_codes +
                                               ("work_gate_id_duplicate",)))),
            )
        else:
            seen_ids[gate_id] = len(gates)

        identity = (dependency, tuple(steps), work_completion)
        if identity in seen:
            diagnostics.append(("work_gate_duplicate", "work gate is duplicated: %s" % dependency))
            invalid_codes.append("work_gate_duplicate")
            prior = seen[identity]
            gates[prior] = replace(
                gates[prior],
                invalid_codes=tuple(sorted(set(gates[prior].invalid_codes +
                                               ("work_gate_duplicate",)))),
            )
        else:
            seen[identity] = len(gates)
        gates.append(WorkGate(
            dependency,
            tuple(steps),
            work_completion,
            work_status or "",
            approval_state or "",
            optional,
            gate_id,
            source_id,
            "structured",
            tuple(sorted(set(invalid_codes))),
        ))
    return tuple(gates), tuple(diagnostics)


def evaluate_work_gates(gates: Sequence[WorkGate],
                        targets: Mapping[str, DependencyTargetState]):
    """Evaluate target state without registry or cycle validation (compatibility API)."""
    return tuple(_evaluate_gate(gate, targets.get(gate.dependency)) for gate in gates)


def evaluate_dependency_graph(
    gates: Sequence[WorkGate],
    targets: Mapping[str, DependencyTargetState],
    *,
    source_steps: Mapping[str, Sequence[str]],
    legacy_dependencies: Optional[Mapping[str, Sequence[str]]] = None,
    structured_dependencies: Optional[Mapping[str, Sequence[str]]] = None,
) -> DependencyGraphResult:
    """Validate gates against the Work/Step registry and detect expanded-event cycles."""
    legacy_dependencies = legacy_dependencies or {}
    structured_dependencies = structured_dependencies or {}
    normalized = list(gates)
    diagnostics = []
    explicit_sources = {gate.source_id for gate in gates}
    for source in sorted(legacy_dependencies):
        legacy = tuple(dict.fromkeys(legacy_dependencies[source]))
        structured = tuple(dict.fromkeys(structured_dependencies.get(source, ())))
        if structured and set(legacy) != set(structured):
            diagnostics.append(DependencyDiagnostic(
                "structured_legacy_dependency_conflict",
                "structured dependency targets conflict with legacy targets: %s" % source,
            ))
            normalized = [
                replace(gate, invalid_codes=tuple(sorted(set(
                    gate.invalid_codes + ("structured_legacy_dependency_conflict",)))))
                if gate.source_id == source else gate
                for gate in normalized
            ]
            continue
        if structured or source in explicit_sources:
            continue
        for index, dependency in enumerate(legacy):
            normalized.append(WorkGate(
                dependency=dependency,
                work_completion=True,
                gate_id="%s#legacy-completion-%03d" % (source, index + 1),
                source_id=source,
                origin="legacy_completion_candidate",
            ))

    validated = []
    for gate in normalized:
        invalid_codes = set(gate.invalid_codes)
        if gate.source_id not in source_steps:
            invalid_codes.add("work_gate_source_missing")
            diagnostics.append(DependencyDiagnostic(
                "work_gate_source_missing",
                "work gate source is absent from the Work registry: %s" % gate.source_id,
                gate.gate_id,
            ))
        else:
            known_steps = set(source_steps[gate.source_id])
            for step in gate.steps:
                if step not in known_steps:
                    invalid_codes.add("work_gate_step_invalid")
                    diagnostics.append(DependencyDiagnostic(
                        "work_gate_step_invalid",
                        "work gate source step does not exist: %s/%s" % (gate.source_id, step),
                        gate.gate_id,
                    ))
        validated.append(replace(gate, invalid_codes=tuple(sorted(invalid_codes))))

    evaluations = [_evaluate_gate(gate, targets.get(gate.dependency)) for gate in validated]
    cycles, cycle_gate_ids = _expanded_event_cycles(validated, source_steps)
    if cycle_gate_ids:
        cycle_events = {
            gate_id: cycle.events
            for cycle in cycles
            for gate_id in cycle.gate_ids
        }
        evaluations = [
            replace(
                evaluation,
                status=DependencyStatus.INVALID,
                blocking=not evaluation.optional,
                reason="dependency gate participates in an expanded-event cycle",
                cycle_events=cycle_events.get(evaluation.gate_id, ()),
            )
            if evaluation.gate_id in cycle_gate_ids else evaluation
            for evaluation in evaluations
        ]
        for cycle in cycles:
            diagnostics.append(DependencyDiagnostic(
                "dependency_cycle",
                "expanded dependency event cycle: %s" % " -> ".join(cycle.events),
                ",".join(cycle.gate_ids),
            ))

    return DependencyGraphResult(
        tuple(sorted(evaluations, key=lambda item: (
            item.source_id, item.gate_id, item.dependency))),
        tuple(sorted(diagnostics, key=lambda item: (item.code, item.gate_id, item.message))),
        cycles,
    )


def evaluate_dependency_sources(sources: Sequence[DependencySource]) -> DependencyGraphResult:
    """Build the document-backed Work/Step registry and evaluate every recovered gate."""
    ordered = tuple(sorted(sources, key=lambda item: (item.path, item.source_id)))
    steps_by_directory: Dict[str, Set[str]] = {}
    for source in ordered:
        if source.step_ref:
            directory = source.path.rpartition("/")[0]
            steps_by_directory.setdefault(directory, set()).add(
                source.step_ref.rsplit("/", 1)[-1]
            )

    source_steps: Dict[str, Tuple[str, ...]] = {}
    targets: Dict[str, DependencyTargetState] = {}
    legacy_dependencies = {}
    structured_dependencies = {}
    gates = []
    for source in ordered:
        directory = source.path.rpartition("/")[0]
        if source.is_work:
            source_steps[source.source_id] = tuple(sorted(steps_by_directory.get(directory, ())))
            current = targets.get(source.source_id)
            candidate = DependencyTargetState(source.work_status, source.approval_state)
            if current is None or (not current.work_status and candidate.work_status):
                targets[source.source_id] = candidate
        if source.is_work and source.legacy_dependencies:
            legacy_dependencies[source.source_id] = source.legacy_dependencies
        if source.structured_dependencies:
            structured_dependencies[source.source_id] = source.structured_dependencies
        gates.extend(source.gates)
    return evaluate_dependency_graph(
        gates,
        targets,
        source_steps=source_steps,
        legacy_dependencies=legacy_dependencies,
        structured_dependencies=structured_dependencies,
    )


def _evaluate_gate(gate: WorkGate, target: DependencyTargetState) -> DependencyEvaluation:
    if gate.invalid_codes:
        status = DependencyStatus.INVALID
        reason = "invalid gate: %s" % ", ".join(gate.invalid_codes)
    elif target is None or not target.exists:
        status = DependencyStatus.UNRESOLVABLE
        reason = "dependency target is unavailable"
    elif not target.work_status or not target.approval_state:
        status = DependencyStatus.UNKNOWN
        reason = "dependency target state is incomplete"
    elif (target.work_status == gate.required_work_status
          and target.approval_state == gate.required_approval_state):
        status = DependencyStatus.SATISFIED
        reason = "dependency is complete and accepted"
    elif target.work_status in {"cancelled", "superseded"}:
        status = DependencyStatus.UNRESOLVABLE
        reason = "terminal dependency needs an accepted exception"
    else:
        status = DependencyStatus.WAITING
        reason = "dependency is not complete and accepted"
    return DependencyEvaluation(
        gate.dependency,
        status,
        not gate.optional and status != DependencyStatus.SATISFIED,
        reason,
        gate.gate_id,
        gate.source_id,
        gate.steps,
        gate.work_completion,
        gate.optional,
        gate.origin,
        target.work_status if target is not None else "",
        target.approval_state if target is not None else "",
    )


def _expanded_event_cycles(gates, source_steps):
    edges: Dict[str, Set[str]] = {}
    gate_edges = {}

    def add(source, target):
        edges.setdefault(source, set()).add(target)
        edges.setdefault(target, set())

    all_works = set(source_steps)
    all_works.update(gate.dependency for gate in gates)
    for work in sorted(all_works):
        complete = "%s::work_complete" % work
        accepted = "%s::approval_accepted" % work
        add(complete, accepted)
        for step in sorted(source_steps.get(work, ())):
            start = "%s::%s_start" % (work, step)
            step_complete = "%s::%s_complete" % (work, step)
            add(start, step_complete)
            add(step_complete, complete)

    for gate in gates:
        if gate.invalid_codes or gate.optional:
            continue
        target = "%s::approval_accepted" % gate.dependency
        destinations = ["%s::%s_start" % (gate.source_id, step) for step in gate.steps]
        if gate.work_completion:
            destinations.append("%s::work_complete" % gate.source_id)
        for destination in destinations:
            add(target, destination)
            gate_edges.setdefault(gate.gate_id, []).append((target, destination))

    components = _strongly_connected_components(edges)
    cycles = []
    cycle_gate_ids = set()
    for component in components:
        members = set(component)
        gate_ids = tuple(sorted(
            gate_id
            for gate_id, values in gate_edges.items()
            if any(source in members and target in members for source, target in values)
        ))
        if len(component) < 2 or not gate_ids:
            continue
        cycles.append(DependencyCycle(tuple(sorted(component)), gate_ids))
        cycle_gate_ids.update(gate_ids)
    return tuple(sorted(cycles, key=lambda item: (item.events, item.gate_ids))), cycle_gate_ids


def _strongly_connected_components(edges: Mapping[str, Set[str]]):
    index = 0
    indexes = {}
    lowlinks = {}
    stack = []
    on_stack = set()
    components = []

    def visit(node):
        nonlocal index
        indexes[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in sorted(edges.get(node, ())):
            if target not in indexes:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indexes[target])
        if lowlinks[node] != indexes[node]:
            return
        component = []
        while True:
            member = stack.pop()
            on_stack.remove(member)
            component.append(member)
            if member == node:
                break
        components.append(tuple(sorted(component)))

    for node in sorted(edges):
        if node not in indexes:
            visit(node)
    return tuple(sorted(components))
