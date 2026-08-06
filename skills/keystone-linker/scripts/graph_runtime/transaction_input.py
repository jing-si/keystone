"""Transaction header, input delta, and canonical mutation validation."""

from dataclasses import dataclass
from typing import Any, Dict, Sequence, Tuple

from .model import Diagnostic
from .transaction_wire_validation import (
    entity_identity,
    is_digest_wire,
    is_locator_wire,
    is_node_wire,
    is_relation_wire,
)
from .validation_support import diagnostic


TRANSACTION_STATES = {
    "proposed",
    "awaiting_attestation",
    "ready_to_apply",
    "applying",
    "partially_applied",
    "verified",
    "conflicted",
    "failed",
}
CONFLICT_REASONS = {
    "stale_baseline",
    "reject",
    "needs_revision",
    "reconstruction_mismatch",
}
TRANSACTION_FIELDS = {
    "schema_version",
    "transaction_id",
    "scope_ref",
    "input_deltas",
    "canonical_mutations",
    "surface_patches",
    "attestations",
    "apply_results",
    "state",
    "conflict_reason",
    "reconstruction",
    "mechanical_validation",
    "coverage_debt",
}


@dataclass(frozen=True)
class TransactionInput:
    state: Any
    conflict_reason: Any
    mutations: Tuple[Any, ...]


@dataclass(frozen=True)
class TransactionInputValidationResult:
    diagnostics: Tuple[Diagnostic, ...]
    transaction_input: TransactionInput


def validate_transaction_input(
    value: Dict[str, Any],
) -> TransactionInputValidationResult:
    findings = []
    for field in sorted(set(value) - TRANSACTION_FIELDS):
        findings.append(diagnostic(
            "transaction_unknown_field",
            "unknown transaction field: %s" % field,
        ))

    state = value.get("state")
    if state not in TRANSACTION_STATES:
        findings.append(diagnostic(
            "transaction_state_invalid",
            "unsupported transaction state: %s" % state,
        ))
    if value.get("schema_version") != 1:
        findings.append(diagnostic(
            "transaction_schema_invalid",
            "transaction schema_version must be 1",
        ))

    conflict_reason = value.get("conflict_reason")
    if conflict_reason is not None and conflict_reason not in CONFLICT_REASONS:
        findings.append(diagnostic(
            "conflict_reason_invalid",
            "transaction conflict_reason is invalid",
        ))
    if state != "conflicted" and conflict_reason is not None:
        findings.append(diagnostic(
            "conflict_reason_unexpected",
            "only conflicted transactions may declare conflict_reason",
        ))
    for field in ("transaction_id", "scope_ref"):
        if not isinstance(value.get(field), str) or not value[field]:
            findings.append(diagnostic(
                "transaction_field_missing", "%s is required" % field
            ))

    input_deltas = value.get("input_deltas", [])
    if not isinstance(input_deltas, list):
        findings.append(diagnostic(
            "input_deltas_invalid", "input_deltas must be an array"
        ))
        input_deltas = []
    for delta in input_deltas:
        if not _is_input_delta(delta):
            findings.append(diagnostic(
                "input_delta_invalid",
                "input delta does not match change_delta wire",
            ))

    coverage_debt = value.get("coverage_debt", [])
    if not (
        isinstance(coverage_debt, list)
        and all(isinstance(item, str) for item in coverage_debt)
    ):
        findings.append(diagnostic(
            "coverage_debt_invalid",
            "coverage_debt must be an array of strings",
        ))

    mutations = value.get("canonical_mutations", [])
    if not isinstance(mutations, list):
        findings.append(diagnostic(
            "transaction_mutations_invalid",
            "canonical_mutations must be an array",
        ))
        mutations = []
    findings.extend(_validate_mutations(mutations))

    return TransactionInputValidationResult(
        diagnostics=tuple(findings),
        transaction_input=TransactionInput(
            state=state,
            conflict_reason=conflict_reason,
            mutations=tuple(mutations),
        ),
    )


def _is_input_delta(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {
            "kind",
            "source_surface",
            "changed_locators",
            "semantic_summary",
            "baseline_digest",
            "graph_relevant",
        }
        and value.get("kind") in {"document_delta", "artifact_delta"}
        and isinstance(value.get("source_surface"), str)
        and bool(value["source_surface"])
        and isinstance(value.get("changed_locators"), list)
        and all(
            is_locator_wire(locator)
            for locator in value.get("changed_locators", [])
        )
        and isinstance(value.get("semantic_summary"), str)
        and is_digest_wire(value.get("baseline_digest", ""))
        and isinstance(value.get("graph_relevant"), bool)
    )


def _validate_mutations(mutations: Sequence[Any]) -> Tuple[Diagnostic, ...]:
    findings = []
    mutation_identities = set()
    for index, mutation in enumerate(mutations):
        if not isinstance(mutation, dict):
            findings.append(diagnostic(
                "transaction_mutation_invalid",
                "canonical_mutations[%d] must be an object" % index,
            ))
        elif mutation.get("operation") not in {"add", "update", "remove"}:
            findings.append(diagnostic(
                "mutation_operation_invalid", "mutation operation is invalid"
            ))
        elif mutation.get("entity") not in {"node", "relation"}:
            findings.append(diagnostic(
                "mutation_entity_invalid", "mutation entity is invalid"
            ))
        elif mutation.get("evidence") == "inferred":
            findings.append(diagnostic(
                "inferred_mutation_forbidden",
                "inferred evidence cannot be a canonical mutation",
            ))
        elif mutation.get("evidence") not in {"declared", "observed"}:
            findings.append(diagnostic(
                "mutation_evidence_invalid",
                "mutation evidence must be declared or observed",
            ))
        else:
            findings.extend(
                _validate_canonical_mutation(mutation, mutation_identities)
            )
    return tuple(findings)


def _validate_canonical_mutation(
    mutation: Dict[str, Any],
    mutation_identities: set,
) -> Tuple[Diagnostic, ...]:
    findings = []
    operation = mutation["operation"]
    before = mutation.get("before")
    after = mutation.get("after")
    if (
        (operation == "add" and (before is not None or not isinstance(after, dict)))
        or (
            operation == "remove"
            and (not isinstance(before, dict) or after is not None)
        )
        or (
            operation == "update"
            and (not isinstance(before, dict) or not isinstance(after, dict))
        )
    ):
        findings.append(diagnostic(
            "mutation_shape_invalid",
            "mutation before/after values do not match operation",
        ))

    entity_values = [item for item in (before, after) if item is not None]
    validator = is_node_wire if mutation["entity"] == "node" else is_relation_wire
    if any(not validator(item) for item in entity_values):
        findings.append(diagnostic(
            "mutation_%s_invalid" % mutation["entity"],
            "canonical mutation entity does not match the canonical wire",
        ))
    identities = {
        entity_identity(mutation["entity"], item)
        for item in entity_values
    }
    if len(identities) > 1:
        findings.append(diagnostic(
            "mutation_identity_changed",
            "update/remove mutation identity must remain stable",
        ))
    identity = next(iter(identities), None)
    key = (mutation["entity"], identity)
    if identity is not None and key in mutation_identities:
        findings.append(diagnostic(
            "mutation_identity_duplicate",
            "multiple canonical mutations target the same identity",
        ))
    mutation_identities.add(key)
    return tuple(findings)
