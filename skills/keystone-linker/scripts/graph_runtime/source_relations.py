"""Declared source relations, work gates, and inferred production edges."""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Tuple

from .dependency import WorkGate, parse_work_gates
from .metadata_support import metadata_strings
from .model import (
    Diagnostic,
    Evidence,
    Locator,
    Node,
    NodeKind,
    Provenance,
    Relation,
    RelationType,
)


RELATION_TYPES = {member.value: member for member in RelationType}


@dataclass(frozen=True)
class SourceRelationResult:
    relations: Tuple[Relation, ...]
    diagnostics: Tuple[Diagnostic, ...]
    work_gates: Optional[Tuple[WorkGate, ...]] = None


def build_source_relations(
    data: Mapping[str, Any],
    node: Node,
    construct: Optional[str],
    surface: str,
    path: str,
    locator: Locator,
) -> SourceRelationResult:
    diagnostics = []
    conflicts = data.get("_relation_conflicts")
    if conflicts:
        diagnostics.append(Diagnostic(
            "structured_legacy_relation_conflict",
            "structured relation conflicts with legacy field: %s"
            % ", ".join(conflicts),
            path=path,
            locator=locator,
        ))

    relation_values = tuple(iter_relation_values(data))
    work_gates = None
    if construct == "document" and data.get("_work_gates") is not None:
        declared_dependencies = [
            target
            for relation_type, target in relation_values
            if relation_type == RelationType.DEPENDS_ON
        ]
        work_gates, gate_diagnostics = parse_work_gates(
            data.get("_work_gates"),
            declared_dependencies,
            node.id,
        )
        diagnostics.extend(
            Diagnostic(code, message, path=path, locator=locator)
            for code, message in gate_diagnostics
        )

    relations = {
        (node.id, relation_type.value, target): Relation(
            node.id,
            relation_type,
            target,
            Evidence.DECLARED,
            Provenance(surface=surface, locator=locator),
            node.lifecycle,
        )
        for relation_type, target in relation_values
    }
    if node.kind == NodeKind.OUTPUT_ARTIFACT:
        for source_id in node.provenance.produced_from:
            key = (source_id, RelationType.PRODUCES.value, node.id)
            if key not in relations:
                relations[key] = Relation(
                    source_id,
                    RelationType.PRODUCES,
                    node.id,
                    Evidence.INFERRED,
                    Provenance(
                        surface="derived_produced_from",
                        locator=locator,
                    ),
                    node.lifecycle,
                )
    return SourceRelationResult(
        relations=tuple(relations.values()),
        diagnostics=tuple(diagnostics),
        work_gates=work_gates,
    )


def iter_relation_values(
    data: Mapping[str, Any],
) -> Iterable[Tuple[RelationType, str]]:
    for name, relation in RELATION_TYPES.items():
        for target in metadata_strings(data.get(name)):
            yield relation, target
