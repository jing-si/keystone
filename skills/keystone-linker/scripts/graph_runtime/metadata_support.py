"""Shared normalization and ordering for source metadata parsers."""

from typing import Any, Iterable, Tuple

from .model import GraphSnapshot, Node, Relation


def metadata_strings(value: Any) -> Tuple[str, ...]:
    if value is None or value == "":
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return (str(value),)


def sorted_snapshot(
    nodes: Iterable[Node],
    relations: Iterable[Relation],
) -> GraphSnapshot:
    ordered_nodes = tuple(sorted(
        nodes,
        key=lambda node: (node.id, node.locator.path),
    ))
    ordered_relations = tuple(sorted(
        relations,
        key=lambda relation: (
            relation.source,
            relation.relation.value,
            relation.target,
            relation.evidence.value,
            relation.lifecycle.value,
        ),
    ))
    return GraphSnapshot(nodes=ordered_nodes, relations=ordered_relations)
