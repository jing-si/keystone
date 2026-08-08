"""Transaction lifecycle and verified reconstruction closure validation."""

from typing import Any, Dict, Optional, Tuple

from .model import Diagnostic, GraphSnapshot
from .relation_policy import policy_for, relation_direction_allowed
from .transaction_evidence import TransactionEvidence
from .transaction_input import TransactionInput
from .transaction_wire_validation import (
    apply_mutation_delta,
    is_mechanical_envelope,
    is_snapshot_wire,
    mechanical_envelope_passes,
    normalized_wire,
)
from .validation_support import diagnostic
from .wire import graph_snapshot_wire


def validate_transaction_lifecycle(
    value: Dict[str, Any],
    transaction_input: TransactionInput,
    evidence: TransactionEvidence,
    source_snapshot: Optional[GraphSnapshot] = None,
    baseline_source_snapshot: Optional[GraphSnapshot] = None,
) -> Tuple[Diagnostic, ...]:
    findings = list(_validate_state_evidence(value, transaction_input, evidence))
    mechanical = value.get("mechanical_validation")
    if mechanical is not None and not is_mechanical_envelope(mechanical):
        findings.append(diagnostic(
            "mechanical_validation_invalid",
            "mechanical_validation must be a structurally valid diagnostic envelope",
        ))
    if value.get("schema_version") == 2:
        findings.extend(_validate_mutation_semantics(
            value,
            transaction_input,
            source_snapshot,
            baseline_source_snapshot,
        ))
    if transaction_input.state == "verified":
        findings.extend(_validate_verified_closure(
            value,
            transaction_input,
            evidence,
            source_snapshot,
            baseline_source_snapshot,
        ))
    return tuple(findings)


def _node_context(
    value: Dict[str, Any],
    transaction_input: TransactionInput,
    source_snapshot: Optional[GraphSnapshot],
) -> Dict[str, Tuple[str, str]]:
    node_wires: Dict[str, Dict[str, Any]] = {}
    reconstruction = value.get("reconstruction")
    if (
        source_snapshot is None
        and transaction_input.state in {"verified", "conflicted"}
        and isinstance(reconstruction, dict)
    ):
        for key in ("result", "baseline"):
            snapshot = reconstruction.get(key)
            if not isinstance(snapshot, dict):
                continue
            for node in snapshot.get("nodes", []):
                if not isinstance(node, dict):
                    continue
                identity = node.get("id")
                kind = node.get("kind")
                artifact_kind = node.get("artifact_kind")
                if all(isinstance(item, str) for item in (
                    identity, kind, artifact_kind
                )):
                    node_wires[identity] = node
            if node_wires:
                break
    if source_snapshot is not None:
        source_wire = graph_snapshot_wire(
            source_snapshot,
            schema_version=value.get("schema_version", 1),
        )
        node_wires = {
            node["id"]: node for node in source_wire["nodes"]
        }
    if transaction_input.state != "verified":
        for mutation in transaction_input.mutations:
            if not isinstance(mutation, dict) or mutation.get("entity") != "node":
                continue
            operation = mutation.get("operation")
            before = mutation.get("before")
            after = mutation.get("after")
            entity = after or before
            if not isinstance(entity, dict) or not isinstance(entity.get("id"), str):
                continue
            identity = entity["id"]
            current = node_wires.get(identity)
            if operation == "add" and current is None and isinstance(after, dict):
                node_wires[identity] = after
            elif (
                operation == "update"
                and normalized_wire(current) == normalized_wire(before)
                and isinstance(after, dict)
            ):
                node_wires[identity] = after
            elif (
                operation == "remove"
                and normalized_wire(current) == normalized_wire(before)
            ):
                node_wires.pop(identity, None)
    return {
        identity: (node["kind"], node["artifact_kind"])
        for identity, node in node_wires.items()
        if isinstance(node.get("kind"), str)
        and isinstance(node.get("artifact_kind"), str)
    }


def _validate_mutation_semantics(
    value: Dict[str, Any],
    transaction_input: TransactionInput,
    source_snapshot: Optional[GraphSnapshot],
    baseline_source_snapshot: Optional[GraphSnapshot],
) -> Tuple[Diagnostic, ...]:
    mutation_baseline = None
    if transaction_input.state in {
        "proposed", "awaiting_attestation", "ready_to_apply"
    }:
        mutation_baseline = source_snapshot
    elif transaction_input.state == "verified":
        mutation_baseline = baseline_source_snapshot
    findings = list(_validate_mutation_baselines(
        value,
        transaction_input,
        mutation_baseline,
    ))
    nodes = _node_context(value, transaction_input, source_snapshot)
    for index, mutation in enumerate(transaction_input.mutations):
        if not isinstance(mutation, dict):
            continue
        if mutation.get("entity") != "relation":
            if mutation.get("direct_relation_reason") is not None:
                findings.append(diagnostic(
                    "direct_relation_reason_unexpected",
                    "node mutation %d cannot declare direct_relation_reason" % index,
                ))
            continue
        if mutation.get("operation") == "remove":
            if mutation.get("direct_relation_reason") is not None:
                findings.append(diagnostic(
                    "direct_relation_reason_unexpected",
                    "relation removal cannot declare a direct reason",
                ))
            continue
        relation = mutation.get("after") or mutation.get("before")
        if not isinstance(relation, dict):
            continue
        source_id = relation.get("source")
        target_id = relation.get("target")
        relation_name = relation.get("relation")
        if not all(isinstance(item, str) for item in (
            source_id, target_id, relation_name
        )):
            continue
        source = nodes.get(source_id)
        target = nodes.get(target_id)
        if source is None or target is None:
            findings.append(diagnostic(
                "mutation_relation_context_missing",
                "relation mutation %d lacks source or target node context" % index,
            ))
            continue
        if not relation_direction_allowed(
            source[0],
            source[1],
            relation_name,
            target[0],
            target[1],
        ):
            findings.append(diagnostic(
                "mutation_relation_direction_invalid",
                "relation mutation %d violates canonical direction policy" % index,
            ))
        direct_item_artifact = (
            source[0] == "document_item" and target[0] == "output_artifact"
        )
        if not direct_item_artifact:
            if mutation.get("direct_relation_reason") is not None:
                findings.append(diagnostic(
                    "direct_relation_reason_unexpected",
                    "non-direct relation mutation %d cannot declare a direct reason" % index,
                ))
            continue
        try:
            direct_policy = policy_for(relation_name)["direct_item_artifact"]
        except ValueError:
            continue
        if direct_policy == "bounded":
            reason = mutation.get("direct_relation_reason")
            if not isinstance(reason, str) or not reason.strip():
                findings.append(diagnostic(
                    "direct_relation_reason_missing",
                    "bounded direct relation mutation %d requires a reason" % index,
                ))
            if target[1] not in {"schema", "code", "config"}:
                findings.append(diagnostic(
                    "direct_relation_case_invalid",
                    "bounded direct relation mutation %d has an unsupported artifact kind"
                    % index,
                ))
        elif direct_policy == "forbidden":
            findings.append(diagnostic(
                "direct_relation_forbidden",
                "direct item-to-artifact relation mutation %d is forbidden" % index,
            ))
        elif mutation.get("direct_relation_reason") is not None:
            findings.append(diagnostic(
                "direct_relation_reason_unexpected",
                "unbounded direct relation mutation %d cannot declare a direct reason" % index,
            ))
    return tuple(findings)


def _validate_mutation_baselines(
    value: Dict[str, Any],
    transaction_input: TransactionInput,
    source_snapshot: Optional[GraphSnapshot],
) -> Tuple[Diagnostic, ...]:
    """Apply each mutation against the exact source-derived baseline in order."""
    if source_snapshot is None:
        return ()
    current = graph_snapshot_wire(
        source_snapshot,
        schema_version=value.get("schema_version", 1),
    )
    findings = []
    for index, mutation in enumerate(transaction_input.mutations):
        if not isinstance(mutation, dict):
            continue
        applied = apply_mutation_delta(current, (mutation,))
        if applied is None:
            entity = mutation.get("entity")
            findings.append(diagnostic(
                "mutation_baseline_context_mismatch",
                "%s mutation %d before-state differs from source snapshot"
                % (entity, index),
            ))
            continue
        current = applied
    return tuple(findings)


def _validate_state_evidence(
    value: Dict[str, Any],
    transaction_input: TransactionInput,
    evidence: TransactionEvidence,
) -> Tuple[Diagnostic, ...]:
    findings = []
    state = transaction_input.state
    required = evidence.required_patch_ids
    confirmed = evidence.confirmed_patch_ids
    applied = evidence.applied_patch_ids
    result_statuses = {
        item.get("result") for item in evidence.results
        if isinstance(item, dict)
    }
    attestation_decisions = {
        item.get("decision") for item in evidence.attestations
        if isinstance(item, dict)
    }
    strict_v2 = value.get("schema_version") == 2

    if state == "proposed" and (evidence.attestations or evidence.results):
        findings.append(diagnostic(
            "proposed_evidence_forbidden",
            "proposed transaction cannot contain attestation or apply evidence",
        ))
    if state == "awaiting_attestation" and evidence.results:
        findings.append(diagnostic(
            "preapply_result_forbidden",
            "awaiting_attestation transaction cannot contain apply results",
        ))
    if strict_v2 and state == "ready_to_apply" and evidence.results:
        findings.append(diagnostic(
            "ready_apply_result_forbidden",
            "ready_to_apply transaction cannot contain apply results",
        ))
    if (
        strict_v2
        and state not in {"verified", "conflicted"}
        and value.get("reconstruction") is not None
    ):
        findings.append(diagnostic(
            "preverification_reconstruction_forbidden",
            "%s transaction cannot contain reconstruction evidence" % state,
        ))
    if strict_v2 and state in {
        "ready_to_apply", "applying", "partially_applied", "verified"
    }:
        if attestation_decisions & {"reject", "needs_revision"}:
            findings.append(diagnostic(
                "state_rejection_evidence_forbidden",
                "%s cannot contain reject or revision attestations" % state,
            ))
    if strict_v2 and state in {"applying", "partially_applied", "verified"} and (
        result_statuses & {"failed", "stale_baseline"}
    ):
        findings.append(diagnostic(
            "state_apply_result_invalid",
            "%s can contain only applied results" % state,
        ))
    if state in {"ready_to_apply", "applying", "partially_applied", "verified"}:
        if not required <= confirmed:
            findings.append(diagnostic(
                "state_attestation_incomplete",
                "%s requires all required patch confirmations" % state,
            ))
    if state == "partially_applied":
        invalid_partial = (
            not applied or not (required - applied)
            if strict_v2
            else not (applied & required) or not (required - applied)
        )
        if invalid_partial:
            findings.append(diagnostic(
                "partial_application_missing",
                "partially_applied requires applied work and pending required patches",
            ))
    if state == "conflicted" and not _conflict_has_evidence(
        value, transaction_input, evidence
    ):
        findings.append(diagnostic(
            "conflict_evidence_missing",
            "conflicted reason requires matching evidence",
        ))
    if state == "failed":
        mechanical = value.get("mechanical_validation")
        failed_validation = (
            is_mechanical_envelope(mechanical)
            and mechanical["status"] == "fail"
        )
        if not (evidence.failed_patch_ids or failed_validation):
            findings.append(diagnostic(
                "failure_evidence_missing",
                "failed requires failed application or mechanical error evidence",
            ))
    return tuple(findings)


def _conflict_has_evidence(
    value: Dict[str, Any],
    transaction_input: TransactionInput,
    evidence: TransactionEvidence,
) -> bool:
    rejected = evidence.rejected_patch_ids
    needs_revision = evidence.revision_patch_ids
    stale_baselines = evidence.stale_baseline_patch_ids
    return {
        "reject": bool(rejected),
        "needs_revision": bool(needs_revision),
        "stale_baseline": bool(stale_baselines),
        "reconstruction_mismatch": isinstance(value.get("reconstruction"), dict),
        None: bool(rejected or needs_revision or stale_baselines),
    }.get(transaction_input.conflict_reason, False)


def _validate_verified_closure(
    value: Dict[str, Any],
    transaction_input: TransactionInput,
    evidence: TransactionEvidence,
    source_snapshot: Optional[GraphSnapshot],
    baseline_source_snapshot: Optional[GraphSnapshot],
) -> Tuple[Diagnostic, ...]:
    findings = []
    required = evidence.required_patch_ids
    confirmed = evidence.confirmed_patch_ids
    applied = evidence.applied_patch_ids
    mutations = transaction_input.mutations

    if value.get("schema_version") == 2:
        if not evidence.actual_state_root_available:
            findings.append(diagnostic(
                "verified_actual_state_root_missing",
                "schema-v2 verified closure requires repository actual-state root",
            ))
        if source_snapshot is None:
            findings.append(diagnostic(
                "verified_source_snapshot_missing",
                "schema-v2 verified closure requires source-only reconstruction",
            ))

    if not required or not mutations:
        findings.append(diagnostic(
            "verified_closure_vacuous",
            "verified requires required patches and canonical mutations",
        ))
    for patch_id in sorted(required):
        if patch_id not in confirmed:
            findings.append(diagnostic(
                "verified_attestation_missing",
                "verified patch lacks confirm: %s" % patch_id,
            ))
        if patch_id not in applied:
            findings.append(diagnostic(
                "verified_apply_missing",
                "verified patch lacks applied result: %s" % patch_id,
            ))

    reconstruction_evidence = value.get("reconstruction")
    schema_version = value.get("schema_version", 1)
    if not (
        isinstance(reconstruction_evidence, dict)
        and set(reconstruction_evidence) == {"baseline", "result"}
        and isinstance(reconstruction_evidence.get("baseline"), dict)
        and isinstance(reconstruction_evidence.get("result"), dict)
    ):
        findings.append(diagnostic(
            "verified_reconstruction_missing",
            "verified transaction requires reconstruction",
        ))
    elif not (
        is_snapshot_wire(reconstruction_evidence["baseline"], schema_version)
        and is_snapshot_wire(reconstruction_evidence["result"], schema_version)
    ):
        findings.append(diagnostic(
            "verified_reconstruction_wire_invalid",
            "verified reconstruction must match the transaction graph wire version",
        ))
    elif source_snapshot is not None and normalized_wire(
        reconstruction_evidence["result"]
    ) != normalized_wire(graph_snapshot_wire(
        source_snapshot, schema_version=schema_version
    )):
        findings.append(diagnostic(
            "verified_reconstruction_mismatch",
            "verified reconstruction differs from source-only reconstruction",
        ))
    if (
        schema_version == 2
        and baseline_source_snapshot is not None
        and isinstance(reconstruction_evidence, dict)
        and isinstance(reconstruction_evidence.get("baseline"), dict)
        and normalized_wire(reconstruction_evidence["baseline"])
        != normalized_wire(graph_snapshot_wire(
            baseline_source_snapshot, schema_version=schema_version
        ))
    ):
        findings.append(diagnostic(
            "verified_baseline_snapshot_mismatch",
            "verified reconstruction baseline differs from authenticated "
            "pre-application source reconstruction",
        ))

    mechanical = value.get("mechanical_validation")
    if not isinstance(mechanical, dict):
        findings.append(diagnostic(
            "verified_validation_missing",
            "verified transaction requires mechanical_validation",
        ))
        if mechanical == []:
            findings.append(diagnostic(
                "verified_validation_empty",
                "verified transaction requires explicit passing mechanical evidence",
            ))
    elif not mechanical_envelope_passes(mechanical):
        findings.append(diagnostic(
            "verified_validation_failed",
            "verified mechanical envelope does not pass",
        ))

    baseline = (
        reconstruction_evidence.get("baseline")
        if isinstance(reconstruction_evidence, dict)
        else None
    )
    reconstruction = (
        reconstruction_evidence.get("result")
        if isinstance(reconstruction_evidence, dict)
        else None
    )
    applied_snapshot = apply_mutation_delta(baseline, mutations)
    if (
        applied_snapshot is None
        or not isinstance(reconstruction, dict)
        or normalized_wire(applied_snapshot) != normalized_wire(reconstruction)
    ):
        findings.append(diagnostic(
            "mutation_baseline_closure_mismatch",
            "baseline plus canonical mutations must exactly equal reconstruction",
        ))
        findings.append(diagnostic(
            "mutation_reconstruction_mismatch",
            "canonical mutation delta differs from reconstruction",
        ))
    return tuple(findings)
