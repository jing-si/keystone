"""Deterministic, source-write-free Artifact Graph synchronization planning."""

import hashlib
import json
import re
from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Iterable, Mapping, Optional, Sequence, Tuple

from .model import (
    CanonicalMutation,
    Delta,
    Evidence,
    GraphSnapshot,
    GraphTransaction,
    MutationEntity,
    MutationEvidence,
    MutationOperation,
    Node,
    NodeKind,
    PatchOwner,
    PatchSurface,
    Relation,
    SurfacePatch,
    patch_owner_matches_surface,
)


_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


class DirectRelationCase(str, Enum):
    SINGLE_SCHEMA_CONSTRAINT = "single_schema_constraint"
    SINGLE_POLICY_IMPLEMENTATION = "single_policy_implementation"


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


@dataclass(frozen=True)
class PatchSpec:
    owner: PatchOwner
    surface: PatchSurface
    target_path: str
    baseline_digest: str
    exact_patch: str
    required: bool = True


def _wire(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_wire(item) for item in value]
    if isinstance(value, dict):
        return {key: _wire(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _wire(asdict(value))
    return value


def _stable_id(prefix: str, value) -> str:
    body = json.dumps(_wire(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "%s-%s" % (prefix, hashlib.sha256(body.encode("utf-8")).hexdigest()[:20])


def _mutation_sort_key(mutation: CanonicalMutation):
    value = mutation.after if mutation.after is not None else mutation.before
    if isinstance(value, Node):
        identity = value.id
    else:
        identity = "%s:%s:%s" % (value.source, value.relation.value, value.target)
    return mutation.entity.value, identity, mutation.operation.value


def _validate_digest(value: str) -> None:
    if value != "absent" and not _DIGEST.fullmatch(value):
        raise ValueError("baseline digest must be sha256:<64-lowercase-hex> or absent")


def _relation_key(relation: Relation):
    return relation.source, relation.relation, relation.target


def _locator_key(locator):
    return (locator.path, locator.heading or "", locator.symbol or "", locator.test_name or "",
            locator.config_key or "", locator.schema_name or "")


def _normalize_deltas(deltas: Sequence[Delta]) -> Tuple[Delta, ...]:
    normalized = []
    seen_sources = set()
    for delta in deltas:
        _validate_digest(delta.baseline_digest)
        if delta.source_surface in seen_sources:
            raise ValueError("each source surface must have exactly one delta baseline")
        seen_sources.add(delta.source_surface)
        normalized.append(replace(delta, changed_locators=tuple(
            sorted(delta.changed_locators, key=_locator_key))))
    return tuple(sorted(normalized, key=lambda delta: (
        delta.kind.value, delta.source_surface, delta.baseline_digest,
        delta.semantic_summary, delta.graph_relevant,
    )))


def _direct_item_artifact(snapshot: GraphSnapshot, relation: Relation,
                          requested_nodes: Mapping[str, Node]) -> bool:
    nodes = {node.id: node for node in snapshot.nodes}
    nodes.update(requested_nodes)
    source = nodes.get(relation.source)
    target = nodes.get(relation.target)
    return bool(source and target and source.kind == NodeKind.DOCUMENT_ITEM
                and target.kind == NodeKind.OUTPUT_ARTIFACT)


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


def _candidate_sort_key(candidate: TraversalCandidate):
    return (-_GRADE_RANK[candidate.grade], candidate.node.id,
            _locator_key(candidate.node.locator), candidate.via)


def _candidate_wire(candidate: TraversalCandidate):
    locator = {key: value for key, value in asdict(candidate.node.locator).items()
               if value is not None}
    return {"id": candidate.node.id, "kind": candidate.node.kind.value,
            "artifact_kind": candidate.node.artifact_kind.value,
            "grade": candidate.grade.value, "via": list(candidate.via), "locator": locator}


def candidate_budget_projection(candidates: Sequence[TraversalCandidate],
                                max_candidates: int):
    """Project traversal candidates without ever hiding a required candidate."""
    if isinstance(max_candidates, bool) or not isinstance(max_candidates, int) or max_candidates < 0:
        raise ValueError("candidate budget must be a non-negative integer")
    ordered = tuple(sorted(candidates, key=_candidate_sort_key))
    grouped = {grade: tuple(item for item in ordered if item.grade == grade)
               for grade in ImpactGrade}
    required = grouped[ImpactGrade.REQUIRED]
    capacity = max(0, max_candidates - len(required))
    selected = list(required)
    for grade in (ImpactGrade.STRONG_CANDIDATE, ImpactGrade.WEAK_CANDIDATE,
                  ImpactGrade.INFORMATIONAL):
        available = grouped[grade]
        selected.extend(available[:capacity])
        capacity = max(0, capacity - len(available))
    selected_ids = {item.node.id for item in selected}
    omitted_by_grade = {
        grade: tuple(item for item in grouped[grade] if item.node.id not in selected_ids)
        for grade in ImpactGrade
    }
    counts = {"total": len(ordered), "returned": len(selected)}
    counts.update({_BUDGET_LABEL[grade]: len(grouped[grade]) for grade in ImpactGrade})
    truncated = {_BUDGET_LABEL[grade]: len(omitted_by_grade[grade]) for grade in ImpactGrade}
    omitted_summary = []
    for grade in (ImpactGrade.STRONG_CANDIDATE, ImpactGrade.WEAK_CANDIDATE,
                  ImpactGrade.INFORMATIONAL):
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


_FORWARD_GRADE = {
    "produces": ImpactGrade.REQUIRED,
    "provides": ImpactGrade.STRONG_CANDIDATE,
    "uses": ImpactGrade.INFORMATIONAL,
    "implements": ImpactGrade.INFORMATIONAL,
    "verifies": ImpactGrade.INFORMATIONAL,
    "governed_by": ImpactGrade.INFORMATIONAL,
    "documents": ImpactGrade.INFORMATIONAL,
    "supersedes": ImpactGrade.INFORMATIONAL,
    "derived_from": ImpactGrade.INFORMATIONAL,
    "depends_on": ImpactGrade.INFORMATIONAL,
}


_REVERSE_GRADE = {
    "produces": ImpactGrade.STRONG_CANDIDATE,
    "provides": ImpactGrade.REQUIRED,
    "uses": ImpactGrade.STRONG_CANDIDATE,
    "implements": ImpactGrade.REQUIRED,
    "verifies": ImpactGrade.REQUIRED,
    "governed_by": ImpactGrade.REQUIRED,
    "documents": ImpactGrade.STRONG_CANDIDATE,
    "supersedes": ImpactGrade.REQUIRED,
    "derived_from": ImpactGrade.STRONG_CANDIDATE,
    "depends_on": ImpactGrade.REQUIRED,
}


def changed_seed_candidates(snapshot: GraphSnapshot,
                            seed_ids: Iterable[str]) -> Tuple[TraversalCandidate, ...]:
    """Traverse typed direction rules and recursively retain every required candidate."""
    seeds = frozenset(seed_ids)
    by_id = {node.id: node for node in snapshot.nodes}
    relations = tuple(sorted(snapshot.relations, key=lambda item: (
        item.source, item.relation.value, item.target)))
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
            candidate_path = path
            prior = found.get(neighbor)
            if (prior is None or _GRADE_RANK[grade] > _GRADE_RANK[prior.grade]
                    or (_GRADE_RANK[grade] == _GRADE_RANK[prior.grade]
                        and candidate_path < prior.via)):
                found[neighbor] = TraversalCandidate(by_id[neighbor], grade, candidate_path)
            if grade == ImpactGrade.REQUIRED and neighbor not in expanded:
                queue.append((neighbor, path + (neighbor,)))
        queue.sort(key=lambda item: (item[0], item[1]))
    return tuple(found[node_id] for node_id in sorted(found))


def _mutation_surface(mutation: CanonicalMutation):
    value = mutation.after if mutation.after is not None else mutation.before
    if isinstance(value, Node):
        return value.locator.path, value.provenance.surface
    locator = value.provenance.locator
    return (locator.path if locator else None), value.provenance.surface


def _patch_links_observed(mutation: CanonicalMutation, patch: SurfacePatch) -> bool:
    path, surface = _mutation_surface(mutation)
    return bool(path and patch.target_path == path
                and (surface is None or patch.surface.value == surface))


def plan_graph_sync(
        snapshot: GraphSnapshot,
        deltas: Sequence[Delta],
        scope_ref: str,
        *,
        requested_nodes_after: Sequence[Node] = (),
        requested_relations_after: Sequence[Relation] = (),
        requested_node_removals: Sequence[str] = (),
        requested_relation_removals: Sequence[Tuple[str, object, str]] = (),
        patch_specs: Sequence[PatchSpec] = (),
        evidence: Evidence = Evidence.DECLARED,
        direct_relation_case: Optional[DirectRelationCase] = None,
        direct_relation_reason: Optional[str] = None,
) -> GraphTransaction:
    """Plan exact requested after-states; never infer semantics or write sources."""
    try:
        admitted = Evidence(evidence)
    except ValueError as error:
        raise ValueError("unknown mutation evidence") from error
    if admitted == Evidence.INFERRED:
        raise ValueError("inferred evidence is not admissible for canonical mutation")
    mutation_evidence = MutationEvidence(admitted.value)
    normalized_deltas = _normalize_deltas(deltas)

    existing_nodes = {node.id: node for node in snapshot.nodes}
    after_nodes = {node.id: node for node in requested_nodes_after}
    if len(after_nodes) != len(requested_nodes_after):
        raise ValueError("requested node after-state IDs must be unique")
    existing_relations = {_relation_key(relation): relation for relation in snapshot.relations}
    after_relations = {_relation_key(relation): relation for relation in requested_relations_after}
    if len(after_relations) != len(requested_relations_after):
        raise ValueError("requested relation after-states must be unique")
    if any(relation.evidence == Evidence.INFERRED for relation in requested_relations_after):
        raise ValueError("inferred relation evidence is not admissible for canonical mutation")
    node_removals = tuple(requested_node_removals)
    relation_removals = tuple(tuple(key) for key in requested_relation_removals)
    if set(after_nodes) & set(node_removals):
        raise ValueError("node cannot have both after-state and removal")
    if set(after_relations) & set(relation_removals):
        raise ValueError("relation cannot have both after-state and removal")

    direct = [relation for relation in requested_relations_after
              if _direct_item_artifact(snapshot, relation, after_nodes)]
    if direct:
        if direct_relation_case is None:
            raise ValueError("capability-first planning forbids an unclassified direct item-to-artifact relation")
        try:
            DirectRelationCase(direct_relation_case)
        except ValueError as error:
            raise ValueError("direct item-to-artifact relation is not an allowed bounded case") from error
        if not direct_relation_reason or not direct_relation_reason.strip():
            raise ValueError("direct_relation_reason is required for a bounded direct relation")
        target_nodes = {node.id: node for node in snapshot.nodes}
        target_nodes.update(after_nodes)
        for relation in direct:
            artifact = target_nodes[relation.target]
            if direct_relation_case == DirectRelationCase.SINGLE_SCHEMA_CONSTRAINT:
                if artifact.artifact_kind.value != "schema":
                    raise ValueError("single schema constraint requires a schema artifact")
            elif artifact.artifact_kind.value not in {"code", "config"}:
                raise ValueError("single policy implementation requires a code or config artifact")

    mutations = []
    for node_id, after in after_nodes.items():
        before = existing_nodes.get(node_id)
        if before == after:
            continue
        operation = MutationOperation.ADD if before is None else MutationOperation.UPDATE
        mutations.append(CanonicalMutation(operation, MutationEntity.NODE, before, after,
                                            mutation_evidence))
    for node_id in node_removals:
        if node_id not in existing_nodes:
            raise ValueError("cannot remove unknown node: %s" % node_id)
        mutations.append(CanonicalMutation(MutationOperation.REMOVE, MutationEntity.NODE,
                                            existing_nodes[node_id], None, mutation_evidence))
    for key, after in after_relations.items():
        before = existing_relations.get(key)
        if before == after:
            continue
        if before is not None and before.evidence == Evidence.INFERRED:
            raise ValueError("inferred relation evidence is not admissible for canonical mutation")
        operation = MutationOperation.ADD if before is None else MutationOperation.UPDATE
        reason = direct_relation_reason.strip() if after in direct else None
        relation_evidence = MutationEvidence(after.evidence.value)
        mutations.append(CanonicalMutation(operation, MutationEntity.RELATION, before, after,
                                            relation_evidence, reason))
    for raw_key in relation_removals:
        key = tuple(raw_key)
        before = existing_relations.get(key)
        if before is None:
            raise ValueError("cannot remove unknown relation: %r" % (key,))
        if before.evidence == Evidence.INFERRED:
            raise ValueError("inferred relation evidence is not admissible for canonical mutation")
        mutations.append(CanonicalMutation(MutationOperation.REMOVE, MutationEntity.RELATION,
                                            before, None, MutationEvidence(before.evidence.value)))
    mutations = tuple(sorted(mutations, key=_mutation_sort_key))

    delta_by_path = {delta.source_surface: delta for delta in normalized_deltas}
    patches = []
    if len(set(patch_specs)) != len(patch_specs):
        raise ValueError("duplicate patch specs are not allowed")
    for spec in patch_specs:
        _validate_digest(spec.baseline_digest)
        if not patch_owner_matches_surface(spec.owner, spec.surface, spec.target_path):
            raise ValueError("patch owner does not own the described surface")
        matching_delta = delta_by_path.get(spec.target_path)
        if matching_delta is not None and matching_delta.baseline_digest != spec.baseline_digest:
            raise ValueError("patch baseline must exactly match its source delta baseline")
        patch_id = _stable_id("patch", spec)
        patches.append(SurfacePatch(patch_id, spec.owner, spec.surface, spec.target_path,
                                    spec.baseline_digest, spec.exact_patch, spec.required))
    patches = tuple(sorted(patches, key=lambda patch: (patch.target_path, patch.patch_id)))
    if len({patch.patch_id for patch in patches}) != len(patches):
        raise ValueError("duplicate patch IDs are not allowed")
    if mutations and not any(patch.required for patch in patches):
        raise ValueError("graph-changing transaction requires at least one required patch")
    for mutation in mutations:
        if mutation.evidence == MutationEvidence.OBSERVED and not any(
                _patch_links_observed(mutation, patch) for patch in patches):
            raise ValueError("observed mutation requires an exact owning surface patch")
    transaction_material = {
        "scope_ref": scope_ref,
        "deltas": normalized_deltas,
        "mutations": mutations,
        "patches": patches,
    }
    return GraphTransaction(
        transaction_id=_stable_id("graph-tx", transaction_material),
        scope_ref=scope_ref,
        input_deltas=normalized_deltas,
        canonical_mutations=mutations,
        surface_patches=patches,
    )
