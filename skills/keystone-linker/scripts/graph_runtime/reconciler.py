"""Pure synchronization transaction state transitions and verification."""

from dataclasses import dataclass, replace
from typing import Mapping, Sequence, Tuple

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
from .patch_replay import PATCH_FORMATS, digest_bytes, replay_patch
from .transaction_wire_validation import is_digest_wire
from .validation_support import canonical_relative_path


@dataclass(frozen=True)
class AttemptHistory:
    current: GraphTransaction
    prior_attempts: Tuple[GraphTransaction, ...] = ()


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


def _require_application_digest(transaction: GraphTransaction,
                                result: ApplicationResult) -> None:
    if transaction.schema_version != 2 or result.result != ApplicationStatus.APPLIED:
        return
    patches = {patch.patch_id: patch for patch in transaction.surface_patches}
    patch = patches.get(result.patch_id)
    if patch is not None and result.resulting_digest != patch.expected_after_digest:
        raise ValueError("applied resulting_digest must equal expected_after_digest")


def _mutation_surface(mutation):
    value = mutation.after if mutation.after is not None else mutation.before
    if mutation.entity == MutationEntity.NODE:
        return value.locator.path, value.provenance.surface
    locator = value.provenance.locator
    return (locator.path if locator else None), value.provenance.surface


def _observed_link_sets(transaction: GraphTransaction):
    links = []
    for mutation in transaction.canonical_mutations:
        if mutation.evidence.value != "observed":
            continue
        path, surface = _mutation_surface(mutation)
        matches = frozenset(
            patch.patch_id for patch in transaction.surface_patches
            if path and patch_source_identity(patch.surface, patch.target_path) == path
            and (surface is None or patch.surface.value == surface)
        )
        links.append(matches)
    return tuple(links)


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
    stale = []
    for patch in _required_patches(transaction):
        if current_digests.get(patch.patch_id) != patch.baseline_digest:
            stale.append(ApplicationResult(patch.patch_id, ApplicationStatus.STALE_BASELINE,
                                           evidence="current digest differs from patch baseline"))
    if stale:
        return replace(transaction, apply_results=transaction.apply_results + tuple(stale),
                       state=TransactionState.CONFLICTED,
                       conflict_reason=ConflictReason.STALE_BASELINE)
    return replace(transaction, state=TransactionState.APPLYING)


def record_application(transaction: GraphTransaction,
                       result: ApplicationResult,
                       failure_reason: FailureReason = None) -> GraphTransaction:
    _require(transaction, TransactionState.APPLYING)
    _require_patch_invariants(transaction)
    patches = {patch.patch_id: patch for patch in transaction.surface_patches}
    if result.patch_id not in patches:
        raise ValueError("application result references unknown patch")
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
    state = (TransactionState.APPLYING if required_ids <= applied_ids
             else TransactionState.PARTIALLY_APPLIED)
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
    return replace(transaction, state=TransactionState.APPLYING)


def _intended_snapshot(transaction: GraphTransaction, baseline: GraphSnapshot) -> GraphSnapshot:
    nodes = {node.id: node for node in baseline.nodes}
    relations = {(relation.source, relation.relation, relation.target): relation
                 for relation in baseline.relations}
    for mutation in transaction.canonical_mutations:
        if mutation.entity == MutationEntity.NODE:
            identity = (mutation.after or mutation.before).id
            if mutation.operation == MutationOperation.REMOVE:
                nodes.pop(identity, None)
            else:
                nodes[identity] = mutation.after
        else:
            value = mutation.after or mutation.before
            identity = (value.source, value.relation, value.target)
            if mutation.operation == MutationOperation.REMOVE:
                relations.pop(identity, None)
            else:
                relations[identity] = mutation.after
    ordered_nodes = tuple(sorted(nodes.values(), key=lambda node: (node.id, node.locator.path)))
    ordered_relations = tuple(sorted(
        relations.values(),
        key=lambda relation: (relation.source, relation.relation.value, relation.target,
                              relation.evidence.value, relation.lifecycle.value),
    ))
    return GraphSnapshot(ordered_nodes, ordered_relations, baseline.schema_version)


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
    for patch_id in required:
        if current_digests.get(patch_id) != applied[patch_id].resulting_digest:
            return replace(transaction, reconstruction=reconstruction,
                           mechanical_validation=tuple(mechanical_validation),
                           state=TransactionState.CONFLICTED,
                           conflict_reason=ConflictReason.RECONSTRUCTION_MISMATCH)
    intended = _intended_snapshot(transaction, baseline_snapshot)
    if _normalized_snapshot(reconstruction) != intended:
        return replace(transaction, reconstruction=reconstruction,
                       mechanical_validation=tuple(mechanical_validation),
                       state=TransactionState.CONFLICTED,
                       conflict_reason=ConflictReason.RECONSTRUCTION_MISMATCH)
    if any(item.severity == Severity.ERROR for item in mechanical_validation):
        return replace(transaction, reconstruction=reconstruction,
                       mechanical_validation=tuple(mechanical_validation),
                       state=TransactionState.FAILED,
                       failure_reason=FailureReason.VALIDATION_FAILED)
    return replace(transaction, reconstruction=reconstruction,
                   mechanical_validation=tuple(mechanical_validation),
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
                    conflict_reason=None, failure_reason=None)
    return AttemptHistory(clean, history.prior_attempts + (history.current,))
