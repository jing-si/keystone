"""Canonical JSON-wire serialization for Artifact Graph domain values."""

from typing import Any, Dict, Optional, Sequence

from .model import (
    Diagnostic,
    GraphRelevance,
    GraphSnapshot,
    GraphTransaction,
    Locator,
    Node,
    Provenance,
    Relation,
    SCHEMA_VERSION,
)


def _locator_wire(locator: Locator) -> Dict[str, Any]:
    return {
        name: getattr(locator, name)
        for name in (
            "path", "heading", "symbol", "test_name", "config_key", "schema_name",
        )
        if getattr(locator, name) is not None
    }


def _provenance_wire(provenance: Provenance) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "produced_from": list(provenance.produced_from),
        "governed_by": list(provenance.governed_by),
    }
    if provenance.surface is not None:
        result["surface"] = provenance.surface
    if provenance.locator is not None:
        result["locator"] = _locator_wire(provenance.locator)
    if provenance.attested_by is not None:
        result["attested_by"] = provenance.attested_by
    return result


def _node_wire(node: Node) -> Dict[str, Any]:
    result = {
        "id": node.id,
        "kind": node.kind.value,
        "artifact_kind": node.artifact_kind.value,
        "locator": _locator_wire(node.locator),
        "lifecycle": node.lifecycle.value,
        "provenance": _provenance_wire(node.provenance),
    }
    if any((
        node.declared_lifecycle is not None,
        node.declared_approval_state is not None,
        node.declared_governed_by,
        node.declared_source_authority,
        node.parent_id,
        node.approval_state is not None,
        node.source_authority,
    )):
        result["declared_metadata"] = {
            "document_lifecycle": (
                node.declared_lifecycle.value
                if node.declared_lifecycle is not None
                else None
            ),
            "approval_state": (
                node.declared_approval_state.value
                if node.declared_approval_state is not None
                else None
            ),
            "governed_by": list(node.declared_governed_by),
            "source_authority": [list(item) for item in node.declared_source_authority],
        }
        result["effective_metadata"] = {
            "document_lifecycle": node.lifecycle.value,
            "approval_state": (
                node.approval_state.value if node.approval_state is not None else None
            ),
            "governed_by": list(node.provenance.governed_by),
            "source_authority": [list(item) for item in node.source_authority],
        }
        result["parent_id"] = node.parent_id
    return result


def _relation_wire(relation: Relation) -> Dict[str, Any]:
    return {
        "source": relation.source,
        "relation": relation.relation.value,
        "target": relation.target,
        "evidence": relation.evidence.value,
        "provenance": _provenance_wire(relation.provenance),
        "lifecycle": relation.lifecycle.value,
    }


def graph_snapshot_wire(snapshot: GraphSnapshot) -> Dict[str, Any]:
    """Serialize a source-derived graph snapshot to its canonical wire."""
    return {
        "schema_version": snapshot.schema_version,
        "nodes": [_node_wire(node) for node in snapshot.nodes],
        "relations": [_relation_wire(relation) for relation in snapshot.relations],
    }


def _entity_wire(value: Any) -> Optional[Dict[str, Any]]:
    if value is None:
        return None
    if isinstance(value, Node):
        return _node_wire(value)
    if isinstance(value, Relation):
        return _relation_wire(value)
    raise TypeError("canonical mutation entity must be Node or Relation")


def _diagnostic_wire(item: Diagnostic) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "code": item.code,
        "message": item.message,
        "severity": item.severity.value,
    }
    if item.path is not None:
        result["path"] = item.path
    if item.locator is not None:
        result["locator"] = _locator_wire(item.locator)
    return result


def _mechanical_envelope(diagnostics: Sequence[Diagnostic]) -> Dict[str, Any]:
    items = [_diagnostic_wire(item) for item in diagnostics]
    errors = sum(item["severity"] == "error" for item in items)
    warnings = sum(item["severity"] == "warning" for item in items)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "fail" if errors else "pass",
        "diagnostics": items,
        "summary": {"errors": errors, "warnings": warnings},
    }


def transaction_wire(
        transaction: GraphTransaction, *,
        baseline_snapshot: Optional[GraphSnapshot] = None,
) -> Dict[str, Any]:
    """Serialize exactly the accepted canonical transaction wire."""
    if transaction.reconstruction is not None and baseline_snapshot is None:
        raise ValueError("reconstruction serialization requires its baseline snapshot")
    reconstruction = (
        None
        if transaction.reconstruction is None
        else {
            "baseline": graph_snapshot_wire(baseline_snapshot),
            "result": graph_snapshot_wire(transaction.reconstruction),
        }
    )
    return {
        "schema_version": transaction.schema_version,
        "transaction_id": transaction.transaction_id,
        "scope_ref": transaction.scope_ref,
        "input_deltas": [{
            "kind": delta.kind.value,
            "source_surface": delta.source_surface,
            "changed_locators": [
                _locator_wire(locator) for locator in delta.changed_locators
            ],
            "semantic_summary": delta.semantic_summary,
            "baseline_digest": delta.baseline_digest,
            "graph_relevant": delta.graph_relevant,
        } for delta in transaction.input_deltas],
        "canonical_mutations": [{
            "operation": mutation.operation.value,
            "entity": mutation.entity.value,
            "before": _entity_wire(mutation.before),
            "after": _entity_wire(mutation.after),
            "evidence": mutation.evidence.value,
            "direct_relation_reason": mutation.direct_relation_reason,
        } for mutation in transaction.canonical_mutations],
        "surface_patches": [{
            "patch_id": patch.patch_id,
            "owner": patch.owner.value,
            "surface": patch.surface.value,
            "target_path": patch.target_path,
            "baseline_digest": patch.baseline_digest,
            "exact_patch": patch.exact_patch,
            "required": patch.required,
        } for patch in transaction.surface_patches],
        "attestations": [{
            "patch_id": item.patch_id,
            "owner": item.owner.value,
            "decision": item.decision.value,
            "evidence": item.evidence,
        } for item in transaction.attestations],
        "apply_results": [{
            "patch_id": item.patch_id,
            "result": item.result.value,
            "resulting_digest": item.resulting_digest,
            "evidence": item.evidence,
        } for item in transaction.apply_results],
        "state": transaction.state.value,
        "conflict_reason": (
            transaction.conflict_reason.value
            if transaction.conflict_reason is not None
            else None
        ),
        "reconstruction": reconstruction,
        "mechanical_validation": _mechanical_envelope(
            transaction.mechanical_validation
        ),
        "coverage_debt": list(transaction.coverage_debt),
    }


def attempt_history_wire(
        history: Any, graph_relevance: GraphRelevance, *,
        current_baseline: Optional[GraphSnapshot] = None,
        prior_baselines: Sequence[Optional[GraphSnapshot]] = (),
) -> Dict[str, Any]:
    """Serialize report-level relevance and retry history outside the transaction."""
    prior_attempts = tuple(history.prior_attempts)
    if len(prior_baselines) != len(prior_attempts):
        raise ValueError("each prior attempt requires a corresponding baseline entry")
    return {
        "schema_version": SCHEMA_VERSION,
        "graph_relevance": {
            "relevant": graph_relevance.relevant,
            "disposition": graph_relevance.disposition.value,
            "reason": graph_relevance.reason,
        },
        "transaction": transaction_wire(
            history.current, baseline_snapshot=current_baseline
        ),
        "prior_attempts": [
            transaction_wire(transaction, baseline_snapshot=baseline)
            for transaction, baseline in zip(prior_attempts, prior_baselines)
        ],
    }
