"""Transaction lifecycle and verified reconstruction closure validation."""

from typing import Any, Dict, Optional, Tuple

from .model import Diagnostic, GraphSnapshot
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
) -> Tuple[Diagnostic, ...]:
    findings = list(_validate_state_evidence(value, transaction_input, evidence))
    mechanical = value.get("mechanical_validation")
    if mechanical is not None and not is_mechanical_envelope(mechanical):
        findings.append(diagnostic(
            "mechanical_validation_invalid",
            "mechanical_validation must be a structurally valid diagnostic envelope",
        ))
    if transaction_input.state == "verified":
        findings.extend(_validate_verified_closure(
            value,
            transaction_input,
            evidence,
            source_snapshot,
        ))
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
    if state in {"ready_to_apply", "applying", "partially_applied", "verified"}:
        if not required <= confirmed:
            findings.append(diagnostic(
                "state_attestation_incomplete",
                "%s requires all required patch confirmations" % state,
            ))
    if state == "partially_applied":
        if not (applied & required) or not (required - applied):
            findings.append(diagnostic(
                "partial_application_missing",
                "partially_applied requires both applied and pending required patches",
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
) -> Tuple[Diagnostic, ...]:
    findings = []
    required = evidence.required_patch_ids
    confirmed = evidence.confirmed_patch_ids
    applied = evidence.applied_patch_ids
    mutations = transaction_input.mutations

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
