"""Canonical transaction wire and lifecycle validation."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

from .model import Diagnostic, GraphSnapshot
from .transaction_evidence import validate_transaction_evidence
from .transaction_input import validate_transaction_input
from .transaction_lifecycle import validate_transaction_lifecycle
from .validation_support import diagnostic
from .wire import graph_snapshot_wire


def snapshot_wire(snapshot: GraphSnapshot) -> Dict[str, Any]:
    return graph_snapshot_wire(snapshot)


# keystone: id=key.code.linker.graph-transaction-validator kind=output_artifact artifact_kind=code refs=key.standard.artifact.graph.transaction-wire locator.symbol=validate_transaction
def validate_transaction(
    value: Any,
    root: Path = None,
    source_snapshot: GraphSnapshot = None,
    baseline_source_snapshot: GraphSnapshot = None,
) -> Tuple[Diagnostic, ...]:
    if not isinstance(value, dict):
        return (diagnostic("transaction_shape_invalid", "transaction must be a JSON object"),)
    findings: List[Diagnostic] = []
    input_result = validate_transaction_input(value)
    findings.extend(input_result.diagnostics)
    transaction_input = input_result.transaction_input

    evidence_result = validate_transaction_evidence(
        value, root, transaction_input.mutations
    )
    findings.extend(evidence_result.diagnostics)
    if evidence_result.evidence is None:
        return tuple(findings)
    findings.extend(validate_transaction_lifecycle(
        value,
        transaction_input,
        evidence_result.evidence,
        source_snapshot,
        baseline_source_snapshot,
    ))
    return tuple(findings)
