"""Deterministic session views derived from one immutable GraphSnapshot."""

# keystone: id=key.code.linker.source-views kind=output_artifact artifact_kind=code refs=key.standard.project.source-derived-semantic-views key.standard.skill.linker.source-derived-semantic-views locator.symbol=source_views_from_snapshot

from dataclasses import dataclass
import re
from typing import Dict, Set, Tuple

from .lifecycle_policy import replacement_evidence_admitted
from .model import (
    ApprovalState,
    ArtifactKind,
    GraphSnapshot,
    Lifecycle,
    Node,
    NodeKind,
    Relation,
    RelationType,
)
from .relation_policy import relation_direction_allowed


_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class CriterionTargetView:
    target_id: str
    verifier_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class CriterionVerificationView:
    criterion_id: str
    path: str
    approval_state: str
    status: str
    targets: Tuple[CriterionTargetView, ...] = ()


@dataclass(frozen=True)
class DecisionView:
    decision_id: str
    path: str
    approval_state: str
    replaces: Tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkArtifactView:
    work_id: str
    path: str
    output_ids: Tuple[str, ...] = ()
    test_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceViews:
    source_generation: str
    criteria: Tuple[CriterionVerificationView, ...] = ()
    effective_decisions: Tuple[DecisionView, ...] = ()
    pending_decisions: Tuple[DecisionView, ...] = ()
    work_artifacts: Tuple[WorkArtifactView, ...] = ()


def _approval(node: Node) -> str:
    return node.approval_state.value if node.approval_state is not None else "unknown"


def _is_decision(node: Node) -> bool:
    if node.id.startswith("key.acceptance."):
        return False
    return bool(
        node.kind in {NodeKind.DECISION, NodeKind.CLAIM}
        or node.id.startswith("key.claim.")
        or node.id.startswith("key.decision.")
        or node.id.startswith("key.work.decisions.")
    )


def _is_work_order(node: Node) -> bool:
    return bool(
        node.kind == NodeKind.WORK_ORDER
        or (node.id.startswith("key.work.") and node.id.endswith(".order"))
    )


def _direction_admitted(relation: Relation, by_id: Dict[str, Node]) -> bool:
    source = by_id.get(relation.source)
    target = by_id.get(relation.target)
    if source is None or target is None:
        return False
    return relation_direction_allowed(
        source.kind.value,
        source.artifact_kind.value,
        relation.relation.value,
        target.kind.value,
        target.artifact_kind.value,
    )


def _criterion_status(targets: Tuple[CriterionTargetView, ...], unresolved: bool) -> str:
    if not targets:
        return "unbound"
    if unresolved:
        return "unknown"
    verified = sum(bool(item.verifier_ids) for item in targets)
    if verified == len(targets):
        return "verified"
    if verified:
        return "partial"
    return "pending"


def _criterion_views(
    snapshot: GraphSnapshot,
    by_id: Dict[str, Node],
    active_relations: Tuple[Relation, ...],
) -> Tuple[CriterionVerificationView, ...]:
    verifiers_by_target: Dict[str, Set[str]] = {}
    for relation in active_relations:
        verifier = by_id.get(relation.source)
        if (
            relation.relation == RelationType.VERIFIES
            and verifier is not None
            and verifier.lifecycle == Lifecycle.ACTIVE
            and by_id.get(relation.target) is not None
            and by_id[relation.target].lifecycle == Lifecycle.ACTIVE
            and _direction_admitted(relation, by_id)
            and (
                verifier.kind == NodeKind.VERIFICATION_RESULT
                or (
                    verifier.kind == NodeKind.OUTPUT_ARTIFACT
                    and verifier.artifact_kind == ArtifactKind.TEST
                )
            )
        ):
            verifiers_by_target.setdefault(relation.target, set()).add(verifier.id)

    criteria = []
    for criterion in sorted(snapshot.nodes, key=lambda item: item.id):
        if not criterion.id.startswith("key.acceptance."):
            continue
        if criterion.lifecycle != Lifecycle.ACTIVE:
            continue
        target_ids = tuple(sorted({
            relation.target for relation in active_relations
            if relation.source == criterion.id
            and relation.relation == RelationType.REQUIRES_VERIFICATION_OF
        }))
        unresolved = any(
            target_id not in by_id
            or by_id[target_id].lifecycle != Lifecycle.ACTIVE
            or not all(
                _direction_admitted(relation, by_id)
                for relation in active_relations
                if relation.source == criterion.id
                and relation.relation == RelationType.REQUIRES_VERIFICATION_OF
                and relation.target == target_id
            )
            for target_id in target_ids
        )
        targets = tuple(
            CriterionTargetView(
                target_id,
                tuple(sorted(verifiers_by_target.get(target_id, ()))),
            )
            for target_id in target_ids
        )
        criteria.append(CriterionVerificationView(
            criterion.id,
            criterion.locator.path,
            _approval(criterion),
            _criterion_status(
                targets,
                unresolved,
            ),
            targets,
        ))
    return tuple(criteria)


def _decision_views(
    snapshot: GraphSnapshot,
    active_relations: Tuple[Relation, ...],
) -> Tuple[Tuple[DecisionView, ...], Tuple[DecisionView, ...]]:
    accepted_active_ids = {
        node.id for node in snapshot.nodes
        if _is_decision(node)
        and node.lifecycle == Lifecycle.ACTIVE
        and node.approval_state == ApprovalState.ACCEPTED
    }
    replaced_by_accepted = {
        relation.target for relation in active_relations
        if relation.relation == RelationType.SUPERSEDES
        and relation.source in accepted_active_ids
        and replacement_evidence_admitted(relation)
    }
    replacements = {
        node_id: tuple(sorted({
            relation.target for relation in active_relations
            if relation.source == node_id
            and relation.relation == RelationType.SUPERSEDES
            and replacement_evidence_admitted(relation)
        }))
        for node_id in accepted_active_ids
    }

    def decision_view(node: Node) -> DecisionView:
        return DecisionView(
            node.id,
            node.locator.path,
            _approval(node),
            replacements.get(node.id, ()),
        )

    effective_decisions = tuple(
        decision_view(node)
        for node in sorted(snapshot.nodes, key=lambda item: item.id)
        if node.id in accepted_active_ids and node.id not in replaced_by_accepted
    )
    pending_decisions = tuple(
        decision_view(node)
        for node in sorted(snapshot.nodes, key=lambda item: item.id)
        if _is_decision(node)
        and node.lifecycle == Lifecycle.ACTIVE
        and node.approval_state == ApprovalState.PENDING
    )
    return effective_decisions, pending_decisions


def _work_artifact_views(
    snapshot: GraphSnapshot,
    by_id: Dict[str, Node],
    active_relations: Tuple[Relation, ...],
) -> Tuple[WorkArtifactView, ...]:
    work_artifacts = []
    for work in sorted(snapshot.nodes, key=lambda item: item.id):
        if not _is_work_order(work) or work.lifecycle != Lifecycle.ACTIVE:
            continue
        output_ids = tuple(sorted({
            relation.target for relation in active_relations
            if relation.source == work.id
            and relation.relation == RelationType.PRODUCES
            and relation.target in by_id
            and _direction_admitted(relation, by_id)
            and by_id[relation.target].kind == NodeKind.OUTPUT_ARTIFACT
            and by_id[relation.target].lifecycle
            not in {Lifecycle.DEPRECATED, Lifecycle.REMOVED}
        }))
        if not output_ids:
            continue
        test_ids = tuple(
            output_id for output_id in output_ids
            if by_id[output_id].artifact_kind == ArtifactKind.TEST
        )
        work_artifacts.append(WorkArtifactView(
            work.id,
            work.locator.path,
            output_ids,
            test_ids,
        ))
    return tuple(work_artifacts)


def source_views_from_snapshot(
    snapshot: GraphSnapshot,
    source_generation: str,
) -> SourceViews:
    """Join current criteria, decisions, and Work artifacts without mutating sources."""
    if (
        not isinstance(source_generation, str)
        or _DIGEST.fullmatch(source_generation) is None
    ):
        raise ValueError("source_generation must be a canonical sha256 digest")
    by_id: Dict[str, Node] = {node.id: node for node in snapshot.nodes}
    active_relations = tuple(
        relation for relation in snapshot.relations
        if relation.lifecycle == Lifecycle.ACTIVE
    )
    effective_decisions, pending_decisions = _decision_views(
        snapshot, active_relations
    )

    return SourceViews(
        source_generation,
        _criterion_views(snapshot, by_id, active_relations),
        effective_decisions,
        pending_decisions,
        _work_artifact_views(snapshot, by_id, active_relations),
    )


def source_views_wire(views: SourceViews) -> Dict[str, object]:
    """Return the stable JSON-ready source-view wire."""
    return {
        "source_generation": views.source_generation,
        "criteria": [{
            "criterion_id": item.criterion_id,
            "path": item.path,
            "approval_state": item.approval_state,
            "status": item.status,
            "targets": [{
                "target_id": target.target_id,
                "verifier_ids": list(target.verifier_ids),
            } for target in item.targets],
        } for item in views.criteria],
        "effective_decisions": [{
            "decision_id": item.decision_id,
            "path": item.path,
            "approval_state": item.approval_state,
            "replaces": list(item.replaces),
        } for item in views.effective_decisions],
        "pending_decisions": [{
            "decision_id": item.decision_id,
            "path": item.path,
            "approval_state": item.approval_state,
            "replaces": list(item.replaces),
        } for item in views.pending_decisions],
        "work_artifacts": [{
            "work_id": item.work_id,
            "path": item.path,
            "output_ids": list(item.output_ids),
            "test_ids": list(item.test_ids),
        } for item in views.work_artifacts],
    }
