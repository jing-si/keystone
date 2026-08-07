"""Source reconstruction and source-derived snapshot validation."""

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .adapters import adapter_for_path
from .metadata import parse_source
from .lifecycle_policy import RETIRED_LIFECYCLES, replacement_evidence_admitted
from .model import (
    Diagnostic,
    Evidence,
    GraphSnapshot,
    Lifecycle,
    Node,
    Relation,
    RelationType,
)
from .relation_policy import relation_direction_allowed
from .validation_support import diagnostic, safe_path


RELATION_NAMES = {item.value for item in RelationType}


def _companion_relation_vocabulary(text: str, path: str) -> Tuple[Diagnostic, ...]:
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return ()
    relations = value.get("relations") if isinstance(value, dict) else None
    if not isinstance(relations, list):
        return ()
    findings = []
    for index, relation in enumerate(relations):
        if not isinstance(relation, dict):
            findings.append(diagnostic(
                "invalid_relation_format", "relations[%d] must be an object" % index, path
            ))
        elif relation.get("relation") not in RELATION_NAMES:
            findings.append(diagnostic(
                "invalid_relation_vocabulary",
                "relations[%d] uses an unsupported relation: %s" % (
                    index, relation.get("relation")
                ),
                path,
            ))
    return tuple(findings)


def reconstruct(
    root: Path,
    sources: Sequence[str],
    source_bytes: Optional[Mapping[str, bytes]] = None,
) -> Tuple[GraphSnapshot, Tuple[Diagnostic, ...]]:
    """Reconstruct deterministically from source surfaces, never from a cache."""
    nodes: List[Node] = []
    relations: Dict[Tuple[str, RelationType, str], Relation] = {}
    findings: List[Diagnostic] = []
    for relative in sorted(set(sources)):
        source_path = safe_path(root, relative)
        adapter = adapter_for_path(relative)
        if adapter is not None:
            if source_bytes is not None:
                raw_source = source_bytes.get(relative)
            else:
                raw_source = source_path.read_bytes() if source_path.is_file() else None
            if raw_source is None:
                raise FileNotFoundError(relative)
            result = parse_source(raw_source.decode("utf-8"), relative, adapter)
        else:
            companion_relative = relative + ".keystone.json"
            companion_path = safe_path(root, companion_relative)
            if source_bytes is not None:
                raw_companion = source_bytes.get(companion_relative)
            else:
                raw_companion = (
                    companion_path.read_bytes() if companion_path.is_file() else None
                )
            if raw_companion is None:
                raise FileNotFoundError(relative)
            companion_text = raw_companion.decode("utf-8")
            findings.extend(_companion_relation_vocabulary(companion_text, companion_relative))
            if source_bytes is not None:
                raw_source = source_bytes.get(relative)
                exists = relative in source_bytes
            else:
                exists = source_path.is_file()
                raw_source = source_path.read_bytes() if exists else None
            result = parse_source(
                "",
                relative,
                None,
                companion_text=companion_text,
                companion_path=companion_relative,
                companion_source_exists=exists,
                companion_source_bytes=raw_source,
            )
        nodes.extend(result.snapshot.nodes)
        for relation in result.snapshot.relations:
            identity = (relation.source, relation.relation, relation.target)
            existing = relations.get(identity)
            if existing is None:
                relations[identity] = relation
                continue
            rank = {Evidence.INFERRED: 1, Evidence.OBSERVED: 2, Evidence.DECLARED: 3}
            generated_mirror = "derived_produced_from" in {
                existing.provenance.surface, relation.provenance.surface,
            }
            if existing != relation and not generated_mirror:
                findings.append(diagnostic(
                    "relation_identity_conflict",
                    "relation identity has conflicting metadata: %s %s %s" % (
                        relation.source, relation.relation.value, relation.target
                    ),
                    relation.provenance.locator.path if relation.provenance.locator else None,
                ))
            if rank[relation.evidence] > rank[existing.evidence]:
                relations[identity] = relation
        findings.extend(result.diagnostics)
    snapshot = GraphSnapshot(
        nodes=tuple(sorted(nodes, key=lambda item: (item.id, item.locator.path))),
        relations=tuple(sorted(relations.values(), key=lambda item: (
            item.source, item.relation.value, item.target, item.evidence.value,
            item.lifecycle.value,
        ))),
        schema_version=2,
    )
    return snapshot, tuple(findings)


def _direction_valid(relation: Relation, nodes: Mapping[str, Node]) -> bool:
    source = nodes.get(relation.source)
    target = nodes.get(relation.target)
    if source is None or target is None:
        return True
    return relation_direction_allowed(
        source.kind.value,
        source.artifact_kind.value,
        relation.relation.value,
        target.kind.value,
        target.artifact_kind.value,
    )


def _supersession_cycles(relations: Iterable[Relation]) -> Tuple[Tuple[str, ...], ...]:
    edges: Dict[str, List[str]] = {}
    for relation in relations:
        if relation.relation.value == "supersedes" and relation.lifecycle == Lifecycle.ACTIVE:
            edges.setdefault(relation.source, []).append(relation.target)
    cycles = set()

    def visit(node: str, trail: Tuple[str, ...]) -> None:
        if node in trail:
            cycle = trail[trail.index(node):] + (node,)
            rotations = [cycle[index:-1] + cycle[:index] for index in range(len(cycle) - 1)]
            cycles.add(min(rotations))
            return
        for target in edges.get(node, ()):
            visit(target, trail + (node,))

    for source in sorted(edges):
        visit(source, ())
    return tuple(sorted(cycles))


def _canonical_replacement_targets_retired(relation: Relation,
                                           nodes: Mapping[str, Node]) -> bool:
    """Admit only the canonical active new -> supersedes -> retired-old exception."""
    source = nodes.get(relation.source)
    target = nodes.get(relation.target)
    return bool(
        source is not None and target is not None
        and relation.relation == RelationType.SUPERSEDES
        and relation.lifecycle == Lifecycle.ACTIVE
        and replacement_evidence_admitted(relation)
        and source.lifecycle == Lifecycle.ACTIVE
        and target.lifecycle in {Lifecycle.DEPRECATED, Lifecycle.REMOVED}
    )


def validate_snapshot(root: Path, snapshot: GraphSnapshot,
                      parse_diagnostics: Iterable[Diagnostic] = ()) -> Tuple[Diagnostic, ...]:
    findings = list(parse_diagnostics)
    by_id: Dict[str, Node] = {}
    duplicate_ids = set()
    for node in snapshot.nodes:
        if node.id in by_id:
            duplicate_ids.add(node.id)
        else:
            by_id[node.id] = node
        try:
            locator_path = safe_path(root, node.locator.path)
        except ValueError as error:
            findings.append(diagnostic("locator_path_invalid", str(error), node.locator.path))
        else:
            if not locator_path.exists():
                findings.append(diagnostic(
                    "locator_path_missing", "locator path does not exist", node.locator.path
                ))
            elif locator_path.is_file():
                try:
                    text = locator_path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    text = None
                if text is not None:
                    observable_text = text
                    if node.locator.path.lower().endswith((".md", ".markdown")):
                        observable_text = re.sub(
                            r"\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)",
                            "",
                            observable_text,
                            flags=re.DOTALL,
                        )
                        observable_text = re.sub(
                            r"<!--.*?-->", "", observable_text, flags=re.DOTALL
                        )
                    else:
                        observable_text = "\n".join(
                            line for line in observable_text.splitlines()
                            if not re.search(r"(?:keystone|key)\s*:", line)
                        )
                    locator_checks = (
                        ("heading", "locator_heading_stale", lambda value: bool(re.search(
                            r"^\s*#{1,6}\s+" + re.escape(value) + r"\s*$",
                            observable_text,
                            re.MULTILINE,
                        ))),
                        ("symbol", "locator_symbol_stale", lambda value: value in observable_text),
                        ("test_name", "locator_test_name_stale",
                         lambda value: value in observable_text),
                        ("config_key", "locator_config_key_stale",
                         lambda value: value in observable_text),
                        ("schema_name", "locator_schema_name_stale",
                         lambda value: value in observable_text),
                    )
                    for field, code, predicate in locator_checks:
                        value = getattr(node.locator, field)
                        if value and not predicate(value):
                            findings.append(diagnostic(
                                code,
                                "declared %s was not found in source text" % field,
                                node.locator.path,
                            ))
    for node_id in sorted(duplicate_ids):
        findings.append(diagnostic(
            "duplicate_id", "duplicate node id across sources: %s" % node_id
        ))

    for relation in snapshot.relations:
        if relation.source not in by_id:
            if (relation.relation == RelationType.PRODUCES
                    and relation.evidence == Evidence.INFERRED
                    and relation.provenance.surface == "derived_produced_from"):
                findings.append(diagnostic(
                    "produced_from_target_missing",
                    "produced_from target is unresolved: %s" % relation.source,
                    relation.provenance.locator.path if relation.provenance.locator else None,
                ))
            else:
                findings.append(diagnostic(
                    "active_orphan",
                    "active relation source is missing: %s" % relation.source,
                    relation.provenance.locator.path if relation.provenance.locator else None,
                ))
        source_node = by_id.get(relation.source)
        target_node = by_id.get(relation.target)
        if (relation.lifecycle == Lifecycle.ACTIVE
                and source_node is not None
                and source_node.lifecycle in RETIRED_LIFECYCLES):
            findings.append(diagnostic(
                "active_relation_from_retired",
                "active semantic relation starts from a retired node: %s" % relation.source,
                relation.provenance.locator.path if relation.provenance.locator else None,
            ))
        if relation.target not in by_id:
            findings.append(diagnostic(
                "missing_target",
                "relation target is missing: %s" % relation.target,
                relation.provenance.locator.path if relation.provenance.locator else None,
            ))
        elif (relation.lifecycle == Lifecycle.ACTIVE
              and target_node.lifecycle in RETIRED_LIFECYCLES
              and not _canonical_replacement_targets_retired(relation, by_id)):
            findings.append(diagnostic(
                "active_relation_to_retired",
                "active semantic relation targets a retired node: %s" % relation.target,
                relation.provenance.locator.path if relation.provenance.locator else None,
            ))
        if not _direction_valid(relation, by_id):
            findings.append(diagnostic(
                "invalid_relation_direction",
                "relation direction is invalid for %s" % relation.relation.value,
                relation.provenance.locator.path if relation.provenance.locator else None,
            ))
    for cycle in _supersession_cycles(snapshot.relations):
        findings.append(diagnostic(
            "supersession_cycle", "supersession cycle: %s" % " -> ".join(cycle)
        ))
    return tuple(sorted(findings, key=lambda item: (item.path or "", item.code, item.message)))
