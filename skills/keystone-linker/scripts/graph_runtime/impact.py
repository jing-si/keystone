"""Typed-relation impact traversal and bounded candidate presentation."""

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable, Sequence, Tuple

from .lifecycle_policy import (
    EXCLUDED_IMPACT_LIFECYCLES,
    observed_evidence_attested,
)
from .model import Evidence, GraphSnapshot, Lifecycle, Node
from .relation_policy import RELATION_POLICY


class ImpactGrade(str, Enum):
    REQUIRED = "required"
    STRONG_CANDIDATE = "strong_candidate"
    WEAK_CANDIDATE = "weak_candidate"
    INFORMATIONAL = "informational"


@dataclass(frozen=True)
class TraversalCandidate:
    node: Node
    grade: ImpactGrade
    via: Tuple[str, ...]


_GRADE_RANK = {
    ImpactGrade.INFORMATIONAL: 1,
    ImpactGrade.WEAK_CANDIDATE: 2,
    ImpactGrade.STRONG_CANDIDATE: 3,
    ImpactGrade.REQUIRED: 4,
}


_BUDGET_LABEL = {
    ImpactGrade.REQUIRED: "required",
    ImpactGrade.STRONG_CANDIDATE: "strong_candidates",
    ImpactGrade.WEAK_CANDIDATE: "weak_candidates",
    ImpactGrade.INFORMATIONAL: "informational",
}


_FORWARD_GRADE = {
    name: ImpactGrade(rule["forward_grade"])
    for name, rule in RELATION_POLICY.items()
}


_REVERSE_GRADE = {
    name: ImpactGrade(rule["reverse_grade"])
    for name, rule in RELATION_POLICY.items()
}


def _locator_key(locator):
    return (
        locator.path,
        locator.heading or "",
        locator.symbol or "",
        locator.test_name or "",
        locator.config_key or "",
        locator.schema_name or "",
    )


def _candidate_sort_key(candidate: TraversalCandidate):
    return (
        -_GRADE_RANK[candidate.grade],
        candidate.node.id,
        _locator_key(candidate.node.locator),
        candidate.via,
    )


def _cap_grade(grade: ImpactGrade, cap: ImpactGrade) -> ImpactGrade:
    return grade if _GRADE_RANK[grade] <= _GRADE_RANK[cap] else cap


def _admitted_grade(relation, node: Node, grade: ImpactGrade):
    if relation.lifecycle in EXCLUDED_IMPACT_LIFECYCLES:
        return None
    if relation.lifecycle in {Lifecycle.DRAFT, Lifecycle.DEPRECATED}:
        grade = _cap_grade(grade, ImpactGrade.INFORMATIONAL)
    elif relation.evidence == Evidence.INFERRED:
        grade = _cap_grade(grade, ImpactGrade.WEAK_CANDIDATE)
    elif relation.evidence == Evidence.OBSERVED:
        cap = (
            ImpactGrade.STRONG_CANDIDATE
            if observed_evidence_attested(relation)
            else ImpactGrade.WEAK_CANDIDATE
        )
        grade = _cap_grade(grade, cap)

    if node.lifecycle in EXCLUDED_IMPACT_LIFECYCLES:
        return None
    if node.lifecycle in {Lifecycle.DRAFT, Lifecycle.DEPRECATED}:
        grade = _cap_grade(grade, ImpactGrade.INFORMATIONAL)
    return grade


def _candidate_wire(candidate: TraversalCandidate):
    locator = {
        key: value
        for key, value in asdict(candidate.node.locator).items()
        if value is not None
    }
    return {
        "id": candidate.node.id,
        "kind": candidate.node.kind.value,
        "artifact_kind": candidate.node.artifact_kind.value,
        "grade": candidate.grade.value,
        "via": list(candidate.via),
        "locator": locator,
    }


def candidate_budget_projection(
        candidates: Sequence[TraversalCandidate], max_candidates: int,
):
    """Project traversal candidates without ever hiding a required candidate."""
    if (isinstance(max_candidates, bool) or not isinstance(max_candidates, int)
            or max_candidates < 0):
        raise ValueError("candidate budget must be a non-negative integer")
    ordered = tuple(sorted(candidates, key=_candidate_sort_key))
    grouped = {
        grade: tuple(item for item in ordered if item.grade == grade)
        for grade in ImpactGrade
    }
    required = grouped[ImpactGrade.REQUIRED]
    capacity = max(0, max_candidates - len(required))
    selected = list(required)
    for grade in (
        ImpactGrade.STRONG_CANDIDATE,
        ImpactGrade.WEAK_CANDIDATE,
        ImpactGrade.INFORMATIONAL,
    ):
        available = grouped[grade]
        selected.extend(available[:capacity])
        capacity = max(0, capacity - len(available))
    selected_ids = {item.node.id for item in selected}
    omitted_by_grade = {
        grade: tuple(
            item for item in grouped[grade] if item.node.id not in selected_ids
        )
        for grade in ImpactGrade
    }
    counts = {"total": len(ordered), "returned": len(selected)}
    counts.update({
        _BUDGET_LABEL[grade]: len(grouped[grade]) for grade in ImpactGrade
    })
    truncated = {
        _BUDGET_LABEL[grade]: len(omitted_by_grade[grade])
        for grade in ImpactGrade
    }
    omitted_summary = []
    for grade in (
        ImpactGrade.STRONG_CANDIDATE,
        ImpactGrade.WEAK_CANDIDATE,
        ImpactGrade.INFORMATIONAL,
    ):
        omitted = omitted_by_grade[grade]
        if not omitted:
            continue
        ids = sorted(item.node.id for item in omitted)
        paths = sorted(item.node.locator.path for item in omitted)
        omitted_summary.append({
            "grade": grade.value,
            "count": len(omitted),
            "evidence_type": "typed_relation_traversal",
            "keyword_range": {"first": ids[0], "last": ids[-1]},
            "path_range": {"first": paths[0], "last": paths[-1]},
            "reason": "candidate_budget",
        })
    return {
        "candidates": [_candidate_wire(item) for item in selected],
        "candidate_budget": {
            "applied": bool(omitted_summary),
            "limit": max_candidates,
            "counts": counts,
            "truncated": truncated,
            "omitted_summary": omitted_summary,
        },
    }


def changed_seed_candidates(
        snapshot: GraphSnapshot, seed_ids: Iterable[str],
) -> Tuple[TraversalCandidate, ...]:
    """Traverse typed direction rules and recursively retain required candidates."""
    seeds = frozenset(seed_ids)
    by_id = {node.id: node for node in snapshot.nodes}
    relations = tuple(sorted(
        snapshot.relations,
        key=lambda item: (item.source, item.relation.value, item.target),
    ))
    queue = [(seed_id, (seed_id,)) for seed_id in sorted(seeds)]
    expanded = set()
    found = {}
    while queue:
        current, path = queue.pop(0)
        if current in expanded:
            continue
        expanded.add(current)
        for relation in relations:
            if relation.source == current:
                neighbor = relation.target
                grade = _FORWARD_GRADE[relation.relation.value]
            elif relation.target == current:
                neighbor = relation.source
                grade = _REVERSE_GRADE[relation.relation.value]
            else:
                continue
            if neighbor in seeds or neighbor not in by_id:
                continue
            grade = _admitted_grade(relation, by_id[neighbor], grade)
            if grade is None:
                continue
            candidate_path = path
            prior = found.get(neighbor)
            if (prior is None
                    or _GRADE_RANK[grade] > _GRADE_RANK[prior.grade]
                    or (_GRADE_RANK[grade] == _GRADE_RANK[prior.grade]
                        and candidate_path < prior.via)):
                found[neighbor] = TraversalCandidate(
                    by_id[neighbor], grade, candidate_path
                )
            if grade == ImpactGrade.REQUIRED and neighbor not in expanded:
                queue.append((neighbor, path + (neighbor,)))
        queue.sort(key=lambda item: (item[0], item[1]))
    return tuple(found[node_id] for node_id in sorted(found))
