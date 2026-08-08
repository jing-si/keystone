"""Pure synchronization transaction state transitions and verification."""

from dataclasses import dataclass, replace
from typing import Mapping, Optional, Sequence, Tuple

from .model import (
    ApplicationResult,
    ApplicationStatus,
    AttestationDecision,
    ConflictReason,
    Diagnostic,
    FailureReason,
    GraphSnapshot,
    GraphTransaction,
    MutationEntity,
    MutationOperation,
    Severity,
    SurfaceAttestation,
    TransactionState,
    patch_owner_matches_surface,
    patch_source_identity,
)
from .lifecycle_policy import (
    node_lifecycle_admitted,
    relation_lifecycle_admitted,
)
from .patch_replay import PATCH_FORMATS, digest_bytes, replay_patch
from .relation_policy import policy_for, relation_direction_allowed
from .transaction_wire_validation import is_digest_wire
from .validation_support import canonical_relative_path


@dataclass(frozen=True)
class AttemptHistory:
    current: GraphTransaction
    prior_attempts: Tuple[GraphTransaction, ...] = ()


_BASELINE_CHECK_ISSUER = object()


@dataclass(frozen=True)
class _BaselineCheck:
    patch_id: str
    baseline_digest: str
    issuer: object


def _baseline_check(patch) -> _BaselineCheck:
    return _BaselineCheck(
        patch.patch_id,
        patch.baseline_digest,
        _BASELINE_CHECK_ISSUER,
    )


def _has_baseline_check(transaction: GraphTransaction, patch) -> bool:
    return any(
        isinstance(check, _BaselineCheck)
        and check.issuer is _BASELINE_CHECK_ISSUER
        and check.patch_id == patch.patch_id
        and check.baseline_digest == patch.baseline_digest
        for check in transaction._baseline_checks
    )


def _require_schema_version(transaction: GraphTransaction) -> None:
    if (type(transaction.schema_version) is not int
            or transaction.schema_version not in {1, 2}):
        raise ValueError("transaction schema_version must be 1 or 2")


def _require(transaction: GraphTransaction, *states: TransactionState) -> None:
    _require_schema_version(transaction)
    if transaction.state not in states:
        allowed = ", ".join(state.value for state in states)
        raise ValueError("transaction must be %s" % allowed)


def _required_patches(transaction: GraphTransaction):
    return tuple(patch for patch in transaction.surface_patches if patch.required)


def _require_patch_invariants(transaction: GraphTransaction) -> None:
    _require_schema_version(transaction)
    target_paths = [
        canonical_relative_path(patch.target_path)
        for patch in transaction.surface_patches
    ]
    if len(set(target_paths)) != len(target_paths):
        raise ValueError("each physical target may have only one patch")
    if any(not patch_owner_matches_surface(patch.owner, patch.surface, patch.target_path)
           for patch in transaction.surface_patches):
        raise ValueError("patch owner does not own the described surface")
    if transaction.canonical_mutations and not _required_patches(transaction):
        raise ValueError("graph-changing transaction requires at least one required patch")
    for patch in transaction.surface_patches:
        executable_fields = (
            patch.patch_format,
            patch.patch_body,
            patch.expected_after_digest,
            patch.baseline_content,
        )
        if transaction.schema_version == 1:
            if any(value is not None for value in executable_fields):
                raise ValueError("schema-v1 patch cannot contain schema-v2 executable fields")
            continue
        if (
            patch.patch_format not in PATCH_FORMATS
            or not isinstance(patch.patch_body, str)
            or patch.exact_patch != patch.patch_body
            or not is_digest_wire(patch.expected_after_digest or "")
            or patch.expected_after_digest == "absent"
        ):
            raise ValueError("schema-v2 requires every patch to be executable")
        if patch.baseline_digest == "absent":
            if patch.baseline_content is not None:
                raise ValueError("absent baseline requires null baseline_content")
            baseline = b""
        elif not isinstance(patch.baseline_content, str):
            raise ValueError("schema-v2 patch requires baseline_content")
        else:
            baseline = patch.baseline_content.encode("utf-8")
            if digest_bytes(baseline) != patch.baseline_digest:
                raise ValueError("baseline_content does not match baseline_digest")
        try:
            replayed = replay_patch(baseline, patch.patch_format, patch.patch_body)
        except ValueError as error:
            raise ValueError("schema-v2 patch cannot be replayed: %s" % error) from error
        if digest_bytes(replayed) != patch.expected_after_digest:
            raise ValueError("schema-v2 patch does not produce expected_after_digest")
    if transaction.schema_version == 2:
        if not isinstance(transaction.scope_ref, str) or not transaction.scope_ref.strip():
            raise ValueError("schema-v2 transaction requires a non-empty scope_ref")
        relevant_deltas = {
            delta.source_surface: delta
            for delta in transaction.input_deltas
            if delta.graph_relevant
        }
        for patch in transaction.surface_patches:
            delta = relevant_deltas.get(patch.target_path)
            if delta is None:
                raise ValueError(
                    "schema-v2 patch requires a graph-relevant input delta"
                )
            if delta.baseline_digest != patch.baseline_digest:
                raise ValueError(
                    "schema-v2 patch baseline must match its input delta"
                )
        for mutation in transaction.canonical_mutations:
            for surface in _mutation_surfaces(mutation):
                linked = tuple(
                    patch for patch in transaction.surface_patches
                    if _patch_links_surface(surface, patch)
                )
                if any(not patch.required for patch in linked):
                    raise ValueError(
                        "schema-v2 forbids a mutation-bearing optional patch"
                    )
                if not any(patch.required for patch in linked):
                    raise ValueError(
                        "every schema-v2 mutation surface requires a required owning patch"
                    )


def _require_application_digest(transaction: GraphTransaction,
                                result: ApplicationResult) -> None:
    if transaction.schema_version != 2 or result.result != ApplicationStatus.APPLIED:
        return
    patches = {patch.patch_id: patch for patch in transaction.surface_patches}
    patch = patches.get(result.patch_id)
    if patch is not None and result.resulting_digest != patch.expected_after_digest:
        raise ValueError("applied resulting_digest must equal expected_after_digest")


def _mutation_surfaces(mutation):
    surfaces = []
    for value in (mutation.before, mutation.after):
        if value is None:
            continue
        if mutation.entity == MutationEntity.NODE:
            candidate = value.locator.path, value.provenance.surface
        else:
            locator = value.provenance.locator
            candidate = (
                locator.path if locator else None,
                value.provenance.surface,
            )
        if candidate not in surfaces:
            surfaces.append(candidate)
    return tuple(surfaces)


def _patch_links_surface(surface, patch) -> bool:
    path, expected_surface = surface
    source_identity = patch_source_identity(patch.surface, patch.target_path)
    return bool(
        path
        and source_identity == path
        and (
            expected_surface is None
            or patch.surface.value == expected_surface
        )
    )


def _patch_links_mutation(mutation, patch) -> bool:
    return any(
        _patch_links_surface(surface, patch)
        for surface in _mutation_surfaces(mutation)
    )


def _legacy_patch_links_mutation(mutation, patch) -> bool:
    value = mutation.after if mutation.after is not None else mutation.before
    if mutation.entity == MutationEntity.NODE:
        surface = value.locator.path, value.provenance.surface
    else:
        locator = value.provenance.locator
        surface = (
            locator.path if locator else None,
            value.provenance.surface,
        )
    return _patch_links_surface(surface, patch)


def _observed_link_sets(transaction: GraphTransaction):
    link_sets = []
    for mutation in transaction.canonical_mutations:
        if mutation.evidence.value != "observed":
            continue
        link_predicate = (
            _legacy_patch_links_mutation
            if transaction.schema_version == 1 else _patch_links_mutation
        )
        matches = frozenset(
            patch.patch_id for patch in transaction.surface_patches
            if link_predicate(mutation, patch)
        )
        link_sets.append(matches)
    return tuple(link_sets)


def begin_attestation(transaction: GraphTransaction) -> GraphTransaction:
    _require(transaction, TransactionState.PROPOSED)
    _require_patch_invariants(transaction)
    return replace(transaction, state=TransactionState.AWAITING_ATTESTATION)


def record_attestation(transaction: GraphTransaction,
                       attestation: SurfaceAttestation) -> GraphTransaction:
    _require(transaction, TransactionState.AWAITING_ATTESTATION)
    _require_patch_invariants(transaction)
    patches = {patch.patch_id: patch for patch in transaction.surface_patches}
    patch = patches.get(attestation.patch_id)
    if patch is None:
        raise ValueError("attestation references unknown patch")
    if patch.owner != attestation.owner:
        raise ValueError("attestation owner does not own patch surface")
    if any(item.patch_id == attestation.patch_id for item in transaction.attestations):
        raise ValueError("patch already attested")
    attestations = transaction.attestations + (attestation,)
    if attestation.decision in (AttestationDecision.REJECT, AttestationDecision.NEEDS_REVISION):
        reason = (ConflictReason.REJECT if attestation.decision == AttestationDecision.REJECT
                  else ConflictReason.NEEDS_REVISION)
        return replace(transaction, attestations=attestations, state=TransactionState.CONFLICTED,
                       conflict_reason=reason)
    confirmed = {item.patch_id for item in attestations
                 if item.decision == AttestationDecision.CONFIRM}
    required = {patch.patch_id for patch in _required_patches(transaction)}
    observed_admitted = all(bool(options & confirmed)
                            for options in _observed_link_sets(transaction))
    state = (TransactionState.READY_TO_APPLY if required <= confirmed and observed_admitted
             else TransactionState.AWAITING_ATTESTATION)
    return replace(transaction, attestations=attestations, state=state)


def begin_application(transaction: GraphTransaction,
                      current_digests: Mapping[str, str]) -> GraphTransaction:
    _require(transaction, TransactionState.READY_TO_APPLY)
    _require_patch_invariants(transaction)
    confirmed = {
        item.patch_id for item in transaction.attestations
        if item.decision == AttestationDecision.CONFIRM
    }
    candidates = (
        transaction.surface_patches
        if transaction.schema_version == 2
        else _required_patches(transaction)
    )
    patches = tuple(
        patch for patch in candidates
        if patch.required or patch.patch_id in confirmed
    )
    stale = []
    for patch in patches:
        if current_digests.get(patch.patch_id) != patch.baseline_digest:
            stale.append(ApplicationResult(patch.patch_id, ApplicationStatus.STALE_BASELINE,
                                           evidence="current digest differs from patch baseline"))
    if stale:
        return replace(transaction, apply_results=transaction.apply_results + tuple(stale),
                       state=TransactionState.CONFLICTED,
                       conflict_reason=ConflictReason.STALE_BASELINE)
    checks = tuple(_baseline_check(patch) for patch in patches)
    return replace(
        transaction,
        state=TransactionState.APPLYING,
        _baseline_checks=checks,
    )


def record_application(transaction: GraphTransaction,
                       result: ApplicationResult,
                       failure_reason: FailureReason = None) -> GraphTransaction:
    _require(transaction, TransactionState.APPLYING)
    _require_patch_invariants(transaction)
    patches = {patch.patch_id: patch for patch in transaction.surface_patches}
    if result.patch_id not in patches:
        raise ValueError("application result references unknown patch")
    confirmed = {
        item.patch_id for item in transaction.attestations
        if item.decision == AttestationDecision.CONFIRM
    }
    if transaction.schema_version == 2 and result.patch_id not in confirmed:
        raise ValueError("application requires a confirmed patch")
    if (
        transaction.schema_version == 2
        and not _has_baseline_check(transaction, patches[result.patch_id])
    ):
        raise ValueError("application requires a runtime-issued baseline check")
    if any(item.patch_id == result.patch_id for item in transaction.apply_results):
        raise ValueError("patch is already applied or already has a result")
    if result.result == ApplicationStatus.APPLIED and not result.resulting_digest:
        raise ValueError("applied result requires resulting_digest")
    _require_application_digest(transaction, result)
    results = transaction.apply_results + (result,)
    if result.result == ApplicationStatus.FAILED:
        reason = FailureReason.UNKNOWN if failure_reason is None else FailureReason(failure_reason)
        return replace(
            transaction,
            apply_results=results,
            state=TransactionState.FAILED,
            failure_reason=reason,
        )
    if failure_reason is not None:
        raise ValueError("failure_reason is only valid for failed application")
    if result.result == ApplicationStatus.STALE_BASELINE:
        return replace(transaction, apply_results=results, state=TransactionState.CONFLICTED,
                       conflict_reason=ConflictReason.STALE_BASELINE)
    applied_ids = {item.patch_id for item in results if item.result == ApplicationStatus.APPLIED}
    required_ids = {patch.patch_id for patch in _required_patches(transaction)}
    if transaction.schema_version == 1:
        state = (
            TransactionState.APPLYING
            if required_ids <= applied_ids
            else TransactionState.PARTIALLY_APPLIED
        )
    else:
        state = (
            TransactionState.PARTIALLY_APPLIED
            if applied_ids and not required_ids <= applied_ids
            else TransactionState.APPLYING
        )
    return replace(transaction, apply_results=results, state=state)


def resume_application(transaction: GraphTransaction,
                       current_digests: Mapping[str, str]) -> GraphTransaction:
    _require(transaction, TransactionState.PARTIALLY_APPLIED)
    _require_patch_invariants(transaction)
    applied = {result.patch_id: result for result in transaction.apply_results
               if result.result == ApplicationStatus.APPLIED}
    for patch_id, result in applied.items():
        if current_digests.get(patch_id) != result.resulting_digest:
            return replace(transaction, state=TransactionState.CONFLICTED,
                           conflict_reason=ConflictReason.RECONSTRUCTION_MISMATCH)
    for patch in _required_patches(transaction):
        if patch.patch_id not in applied and current_digests.get(patch.patch_id) != patch.baseline_digest:
            stale = ApplicationResult(patch.patch_id, ApplicationStatus.STALE_BASELINE,
                                      evidence="remaining patch baseline is stale")
            return replace(transaction, apply_results=transaction.apply_results + (stale,),
                           state=TransactionState.CONFLICTED,
                           conflict_reason=ConflictReason.STALE_BASELINE)
    refreshed_checks = list(transaction._baseline_checks)
    if transaction.schema_version == 2:
        confirmed = {
            item.patch_id for item in transaction.attestations
            if item.decision == AttestationDecision.CONFIRM
        }
        for patch in transaction.surface_patches:
            if patch.patch_id in applied:
                continue
            if not patch.required and patch.patch_id not in confirmed:
                continue
            if current_digests.get(patch.patch_id) != patch.baseline_digest:
                stale = ApplicationResult(
                    patch.patch_id,
                    ApplicationStatus.STALE_BASELINE,
                    evidence="remaining confirmed patch baseline is stale",
                )
                return replace(
                    transaction,
                    apply_results=transaction.apply_results + (stale,),
                    state=TransactionState.CONFLICTED,
                    conflict_reason=ConflictReason.STALE_BASELINE,
                )
            refreshed_checks = [
                check for check in refreshed_checks
                if not (
                    isinstance(check, _BaselineCheck)
                    and check.patch_id == patch.patch_id
                )
            ]
            refreshed_checks.append(_baseline_check(patch))
    return replace(
        transaction,
        state=TransactionState.APPLYING,
        _baseline_checks=tuple(refreshed_checks),
    )


def _intended_snapshot(
    transaction: GraphTransaction,
    baseline: GraphSnapshot,
) -> Optional[GraphSnapshot]:
    nodes = {node.id: node for node in baseline.nodes}
    relations = {(relation.source, relation.relation, relation.target): relation
                 for relation in baseline.relations}
    for mutation in transaction.canonical_mutations:
        if mutation.entity == MutationEntity.NODE:
            identity = (mutation.after or mutation.before).id
            current = nodes.get(identity)
            if mutation.operation == MutationOperation.ADD:
                if mutation.before is not None or current is not None:
                    return None
                nodes[identity] = mutation.after
            elif mutation.operation == MutationOperation.UPDATE:
                if current != mutation.before or mutation.after is None:
                    return None
                nodes[identity] = mutation.after
            elif mutation.operation == MutationOperation.REMOVE:
                if current != mutation.before or mutation.after is not None:
                    return None
                nodes.pop(identity)
            else:
                return None
        else:
            value = mutation.after or mutation.before
            identity = (value.source, value.relation, value.target)
            current = relations.get(identity)
            if mutation.operation == MutationOperation.ADD:
                if mutation.before is not None or current is not None:
                    return None
                relations[identity] = mutation.after
            elif mutation.operation == MutationOperation.UPDATE:
                if current != mutation.before or mutation.after is None:
                    return None
                relations[identity] = mutation.after
            elif mutation.operation == MutationOperation.REMOVE:
                if current != mutation.before or mutation.after is not None:
                    return None
                relations.pop(identity)
            else:
                return None
    ordered_nodes = tuple(sorted(nodes.values(), key=lambda node: (node.id, node.locator.path)))
    ordered_relations = tuple(sorted(
        relations.values(),
        key=lambda relation: (relation.source, relation.relation.value, relation.target,
                              relation.evidence.value, relation.lifecycle.value),
    ))
    return GraphSnapshot(ordered_nodes, ordered_relations, baseline.schema_version)


def _semantic_diagnostics(
    transaction: GraphTransaction,
    snapshot: GraphSnapshot,
) -> Tuple[Diagnostic, ...]:
    findings = []
    nodes = {node.id: node for node in snapshot.nodes}
    for node in snapshot.nodes:
        if not node_lifecycle_admitted(node.kind, node.lifecycle):
            findings.append(Diagnostic(
                "node_lifecycle_domain_invalid",
                "node lifecycle is invalid for its domain",
                path=node.locator.path,
                locator=node.locator,
            ))
    for relation in snapshot.relations:
        path = (
            relation.provenance.locator.path
            if relation.provenance.locator is not None else None
        )
        if not relation_lifecycle_admitted(relation.lifecycle):
            findings.append(Diagnostic(
                "relation_lifecycle_domain_invalid",
                "relation lifecycle is invalid for its domain",
                path=path,
            ))
        source = nodes.get(relation.source)
        target = nodes.get(relation.target)
        if source is None:
            findings.append(Diagnostic(
                "active_orphan",
                "relation source is missing: %s" % relation.source,
                path=path,
            ))
        if target is None:
            findings.append(Diagnostic(
                "missing_target",
                "relation target is missing: %s" % relation.target,
                path=path,
            ))
        if source is not None and target is not None and not relation_direction_allowed(
            source.kind.value,
            source.artifact_kind.value,
            relation.relation.value,
            target.kind.value,
            target.artifact_kind.value,
        ):
            findings.append(Diagnostic(
                "invalid_relation_direction",
                "relation direction is invalid for %s" % relation.relation.value,
                path=path,
            ))
    for mutation in transaction.canonical_mutations:
        if mutation.entity != MutationEntity.RELATION:
            if mutation.direct_relation_reason is not None:
                findings.append(Diagnostic(
                    "direct_relation_reason_unexpected",
                    "node mutation cannot declare direct_relation_reason",
                ))
            continue
        if mutation.operation == MutationOperation.REMOVE:
            if mutation.direct_relation_reason is not None:
                findings.append(Diagnostic(
                    "direct_relation_reason_unexpected",
                    "relation removal cannot declare a direct reason",
                ))
            continue
        relation = mutation.after or mutation.before
        source = nodes.get(relation.source)
        target = nodes.get(relation.target)
        if (
            source is None
            or target is None
            or source.kind.value != "document_item"
            or target.kind.value != "output_artifact"
        ):
            if mutation.direct_relation_reason is not None:
                findings.append(Diagnostic(
                    "direct_relation_reason_unexpected",
                    "non-direct relation cannot declare a direct reason",
                ))
            continue
        direct_policy = policy_for(
            relation.relation.value
        )["direct_item_artifact"]
        if direct_policy == "bounded":
            if (
                not isinstance(mutation.direct_relation_reason, str)
                or not mutation.direct_relation_reason.strip()
            ):
                findings.append(Diagnostic(
                    "direct_relation_reason_missing",
                    "bounded direct relation requires a reason",
                ))
            if target.artifact_kind.value not in {"schema", "code", "config"}:
                findings.append(Diagnostic(
                    "direct_relation_case_invalid",
                    "bounded direct relation has an unsupported artifact kind",
                ))
        elif direct_policy == "forbidden":
            findings.append(Diagnostic(
                "direct_relation_forbidden",
                "direct item-to-artifact relation is forbidden",
            ))
        elif mutation.direct_relation_reason is not None:
            findings.append(Diagnostic(
                "direct_relation_reason_unexpected",
                "unbounded direct relation cannot declare a direct reason",
            ))
    return tuple(findings)


def _normalized_snapshot(snapshot: GraphSnapshot) -> GraphSnapshot:
    return GraphSnapshot(
        tuple(sorted(snapshot.nodes, key=lambda node: (node.id, node.locator.path))),
        tuple(sorted(snapshot.relations,
                     key=lambda relation: (relation.source, relation.relation.value,
                                           relation.target, relation.evidence.value,
                                           relation.lifecycle.value))),
        snapshot.schema_version,
    )


def finalize_transaction(transaction: GraphTransaction,
                         reconstruction: GraphSnapshot,
                         mechanical_validation: Sequence[Diagnostic],
                         current_digests: Mapping[str, str],
                         *, baseline_snapshot: GraphSnapshot) -> GraphTransaction:
    _require(transaction, TransactionState.APPLYING)
    _require_patch_invariants(transaction)
    required = {patch.patch_id for patch in _required_patches(transaction)}
    confirms = {item.patch_id for item in transaction.attestations
                if item.decision == AttestationDecision.CONFIRM}
    applied = {item.patch_id: item for item in transaction.apply_results
               if item.result == ApplicationStatus.APPLIED}
    for result in applied.values():
        _require_application_digest(transaction, result)
    if not required <= confirms or not required <= set(applied):
        raise ValueError("all required patches must be confirmed and applied before verification")
    if transaction.schema_version == 2 and not set(applied) <= confirms:
        raise ValueError("every applied patch must be confirmed before verification")
    if transaction.schema_version == 2:
        patches = {patch.patch_id: patch for patch in transaction.surface_patches}
        if any(
            not _has_baseline_check(transaction, patches[patch_id])
            for patch_id in applied
        ):
            raise ValueError(
                "verification requires runtime-issued baseline checks"
            )
    verified_patch_ids = set(applied) if transaction.schema_version == 2 else required
    for patch_id in verified_patch_ids:
        if current_digests.get(patch_id) != applied[patch_id].resulting_digest:
            return replace(transaction, reconstruction=reconstruction,
                           mechanical_validation=tuple(mechanical_validation),
                           state=TransactionState.CONFLICTED,
                           conflict_reason=ConflictReason.RECONSTRUCTION_MISMATCH)
    intended = _intended_snapshot(transaction, baseline_snapshot)
    if intended is None or _normalized_snapshot(reconstruction) != intended:
        return replace(transaction, reconstruction=reconstruction,
                       mechanical_validation=tuple(mechanical_validation),
                       state=TransactionState.CONFLICTED,
                       conflict_reason=ConflictReason.RECONSTRUCTION_MISMATCH)
    validations = tuple(mechanical_validation) + _semantic_diagnostics(
        transaction, reconstruction
    )
    if any(item.severity == Severity.ERROR for item in validations):
        return replace(transaction, reconstruction=reconstruction,
                       mechanical_validation=validations,
                       state=TransactionState.FAILED,
                       failure_reason=FailureReason.VALIDATION_FAILED)
    return replace(transaction, reconstruction=reconstruction,
                   mechanical_validation=validations,
                   state=TransactionState.VERIFIED)


def new_attempt(history: AttemptHistory, revised: GraphTransaction) -> AttemptHistory:
    _require(history.current, TransactionState.CONFLICTED, TransactionState.FAILED)
    _require_schema_version(revised)
    if revised.state != TransactionState.PROPOSED:
        raise ValueError("new attempt must start proposed")
    if revised.transaction_id == history.current.transaction_id:
        raise ValueError("new attempt requires a new transaction ID")
    prior_baselines = {patch.target_path: patch.baseline_digest
                       for patch in history.current.surface_patches}
    new_baselines = {patch.target_path: patch.baseline_digest for patch in revised.surface_patches}
    if history.current.state == TransactionState.CONFLICTED:
        reason = history.current.conflict_reason
        baseline_changed = prior_baselines != new_baselines
        mutation_changed = history.current.canonical_mutations != revised.canonical_mutations
        patch_changed = history.current.surface_patches != revised.surface_patches
        if reason == ConflictReason.STALE_BASELINE and not baseline_changed:
            raise ValueError("stale-baseline attempt requires at least one new baseline")
        if reason in {ConflictReason.REJECT, ConflictReason.NEEDS_REVISION} and not (
                mutation_changed or patch_changed):
            raise ValueError("rejected or revised attempt requires a changed mutation or patch")
        if reason == ConflictReason.RECONSTRUCTION_MISMATCH and not (
                baseline_changed or mutation_changed or patch_changed):
            raise ValueError("reconstruction-mismatch attempt requires changed input")
        if reason is None and not baseline_changed:
            raise ValueError("legacy conflicted attempt requires at least one new baseline")
    elif history.current.failure_reason != FailureReason.TRANSIENT_IO:
        if (
            history.current.canonical_mutations == revised.canonical_mutations
            and history.current.surface_patches == revised.surface_patches
            and prior_baselines == new_baselines
        ):
            raise ValueError("non-transient failed attempt requires changed input")
    clean = replace(revised, attestations=(), apply_results=(), reconstruction=None,
                    mechanical_validation=(), state=TransactionState.PROPOSED,
                    conflict_reason=None, failure_reason=None, _baseline_checks=())
    return AttemptHistory(clean, history.prior_attempts + (history.current,))
