"""Source-derived Artifact Graph mechanical validation.

This module diagnoses wire and repository facts.  It never edits a source,
chooses semantic relations, expands scope, or decides acceptance.
"""

import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .adapters import adapter_for_path
from .metadata import parse_source
from .model import (
    Diagnostic, Evidence, GraphSnapshot, Lifecycle, Node, PatchOwner, PatchSurface,
    Relation, RelationType, Severity, patch_owner_matches_surface,
)


TRANSACTION_STATES = {
    "proposed", "awaiting_attestation", "ready_to_apply", "applying",
    "partially_applied", "verified", "conflicted", "failed",
}
RELATION_NAMES = {
    "produces", "provides", "uses", "implements", "verifies", "depends_on",
    "governed_by", "documents", "supersedes", "derived_from",
}
NODE_KINDS = {"source_document", "document_section", "document_item", "claim", "decision",
              "work_order", "work_step", "capability", "output_artifact", "verification_result"}
ARTIFACT_KINDS = {"skill_source", "code", "config", "schema", "api", "test", "generated_file",
                  "doc_artifact", "none"}
_DIGEST = re.compile(r"(?:absent|sha256:[0-9a-f]{64})\Z")


def diagnostic(code: str, message: str, path: str = None, *, severity=Severity.ERROR) -> Diagnostic:
    return Diagnostic(code=code, message=message, severity=severity, path=path)


def _safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("source path must be a non-empty string")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError("source path escapes root: %s" % relative) from error
    return candidate


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
                "relations[%d] uses an unsupported relation: %s" % (index, relation.get("relation")),
                path,
            ))
    return tuple(findings)


def reconstruct(root: Path, sources: Sequence[str]) -> Tuple[GraphSnapshot, Tuple[Diagnostic, ...]]:
    """Reconstruct deterministically from source surfaces, never from a cache."""
    nodes: List[Node] = []
    relations: Dict[Tuple[str, RelationType, str], Relation] = {}
    findings: List[Diagnostic] = []
    for relative in sorted(set(sources)):
        source_path = _safe_path(root, relative)
        adapter = adapter_for_path(relative)
        if adapter is not None:
            if not source_path.is_file():
                raise FileNotFoundError(relative)
            result = parse_source(source_path.read_text(encoding="utf-8"), relative, adapter)
        else:
            companion_relative = relative + ".keystone.json"
            companion_path = _safe_path(root, companion_relative)
            if not companion_path.is_file():
                raise FileNotFoundError(relative)
            companion_text = companion_path.read_text(encoding="utf-8")
            findings.extend(_companion_relation_vocabulary(companion_text, companion_relative))
            exists = source_path.is_file()
            result = parse_source(
                source_path.read_text(encoding="utf-8") if exists else "",
                relative,
                None,
                companion_text=companion_text,
                companion_path=companion_relative,
                companion_source_exists=exists,
                companion_source_bytes=source_path.read_bytes() if exists else None,
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
                        relation.source, relation.relation.value, relation.target),
                    relation.provenance.locator.path if relation.provenance.locator else None,
                ))
            if rank[relation.evidence] > rank[existing.evidence]:
                relations[identity] = relation
        findings.extend(result.diagnostics)
    snapshot = GraphSnapshot(
        nodes=tuple(sorted(nodes, key=lambda item: (item.id, item.locator.path))),
        relations=tuple(sorted(relations.values(), key=lambda item: (
            item.source, item.relation.value, item.target, item.evidence.value, item.lifecycle.value
        ))),
    )
    return snapshot, tuple(findings)


def _direction_valid(relation: Relation, nodes: Mapping[str, Node]) -> bool:
    source = nodes.get(relation.source)
    target = nodes.get(relation.target)
    if source is None or target is None:
        return True
    name = relation.relation.value
    source_kind, target_kind = source.kind.value, target.kind.value
    if name == "produces":
        return (source_kind in {"source_document", "decision", "work_order"}
                and target_kind == "output_artifact")
    if name == "provides":
        return (source_kind == "output_artifact" and source.artifact_kind.value in {"code", "config", "schema"}
                and target_kind == "capability")
    if name == "uses":
        return (source_kind == "output_artifact" and (target_kind == "capability" or
                (target_kind == "output_artifact" and target.artifact_kind.value in {"api", "code"})))
    if name == "implements":
        return (source_kind == "output_artifact" and source.artifact_kind.value in {"code", "config", "schema"}
                and (target_kind in {"claim", "decision"}
                     or (target_kind == "output_artifact" and target.artifact_kind.value == "api")))
    if name == "documents":
        return source_kind in {"source_document", "document_section", "document_item"} and target_kind == "output_artifact"
    if name == "verifies":
        return ((source_kind == "output_artifact" and source.artifact_kind.value == "test")
                or source_kind == "verification_result") and (
                    target_kind in {"capability", "decision"} or
                    (target_kind == "output_artifact" and target.artifact_kind.value in {"api", "code"}))
    if name == "governed_by":
        return source_kind == "output_artifact" and target_kind in {"source_document", "decision"}
    if name == "depends_on":
        admitted = {"source_document", "work_order", "work_step", "output_artifact"}
        return source_kind in admitted and target_kind in admitted
    if name == "supersedes":
        return source_kind == target_kind
    if name == "derived_from":
        return source_kind == "output_artifact" and target_kind == "output_artifact"
    return True


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
    evidence_admitted = relation.evidence == Evidence.DECLARED
    if relation.evidence == Evidence.OBSERVED:
        provenance = relation.provenance
        try:
            owner = PatchOwner(provenance.attested_by)
            surface = PatchSurface(provenance.surface)
        except (TypeError, ValueError):
            evidence_admitted = False
        else:
            evidence_admitted = bool(
                provenance.locator is not None
                and patch_owner_matches_surface(owner, surface, provenance.locator.path)
            )
    return bool(
        source is not None and target is not None
        and relation.relation == RelationType.SUPERSEDES
        and relation.lifecycle == Lifecycle.ACTIVE
        and evidence_admitted
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
            locator_path = _safe_path(root, node.locator.path)
        except ValueError as error:
            findings.append(diagnostic("locator_path_invalid", str(error), node.locator.path))
        else:
            if not locator_path.exists():
                findings.append(diagnostic("locator_path_missing", "locator path does not exist", node.locator.path))
            elif locator_path.is_file():
                try:
                    text = locator_path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    text = None
                if text is not None:
                    observable_text = text
                    if node.locator.path.lower().endswith((".md", ".markdown")):
                        observable_text = re.sub(r"\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)", "", observable_text,
                                                 flags=re.DOTALL)
                        observable_text = re.sub(r"<!--.*?-->", "", observable_text, flags=re.DOTALL)
                    else:
                        observable_text = "\n".join(
                            line for line in observable_text.splitlines()
                            if not re.search(r"(?:keystone|key)\s*:", line)
                        )
                    locator_checks = (
                        ("heading", "locator_heading_stale", lambda value: bool(re.search(
                            r"^\s*#{1,6}\s+" + re.escape(value) + r"\s*$", observable_text, re.MULTILINE))),
                        ("symbol", "locator_symbol_stale", lambda value: value in observable_text),
                        ("test_name", "locator_test_name_stale", lambda value: value in observable_text),
                        ("config_key", "locator_config_key_stale", lambda value: value in observable_text),
                        ("schema_name", "locator_schema_name_stale", lambda value: value in observable_text),
                    )
                    for field, code, predicate in locator_checks:
                        value = getattr(node.locator, field)
                        if value and not predicate(value):
                            findings.append(diagnostic(code, "declared %s was not found in source text" % field,
                                                       node.locator.path))
    for node_id in sorted(duplicate_ids):
        findings.append(diagnostic("duplicate_id", "duplicate node id across sources: %s" % node_id))

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
                findings.append(diagnostic("active_orphan", "active relation source is missing: %s" % relation.source,
                                           relation.provenance.locator.path if relation.provenance.locator else None))
        if relation.target not in by_id:
            findings.append(diagnostic("missing_target", "relation target is missing: %s" % relation.target,
                                       relation.provenance.locator.path if relation.provenance.locator else None))
        elif (relation.lifecycle == Lifecycle.ACTIVE
              and by_id[relation.target].lifecycle in {Lifecycle.DEPRECATED, Lifecycle.REMOVED}
              and not _canonical_replacement_targets_retired(relation, by_id)):
            findings.append(diagnostic(
                "active_relation_to_retired", "active semantic relation targets a retired node: %s" % relation.target,
                relation.provenance.locator.path if relation.provenance.locator else None,
            ))
        if not _direction_valid(relation, by_id):
            findings.append(diagnostic(
                "invalid_relation_direction",
                "relation direction is invalid for %s" % relation.relation.value,
                relation.provenance.locator.path if relation.provenance.locator else None,
            ))
    for cycle in _supersession_cycles(snapshot.relations):
        findings.append(diagnostic("supersession_cycle", "supersession cycle: %s" % " -> ".join(cycle)))
    return tuple(sorted(findings, key=lambda item: (item.path or "", item.code, item.message)))


def _locator_wire(locator) -> Dict[str, Any]:
    return {name: getattr(locator, name) for name in
            ("path", "heading", "symbol", "test_name", "config_key", "schema_name")
            if getattr(locator, name) is not None}


def _provenance_wire(provenance) -> Dict[str, Any]:
    result = {"produced_from": list(provenance.produced_from),
              "governed_by": list(provenance.governed_by)}
    if provenance.surface is not None:
        result["surface"] = provenance.surface
    if provenance.locator is not None:
        result["locator"] = _locator_wire(provenance.locator)
    if provenance.attested_by is not None:
        result["attested_by"] = provenance.attested_by
    return result


def snapshot_wire(snapshot: GraphSnapshot) -> Dict[str, Any]:
    return {
        "schema_version": snapshot.schema_version,
        "nodes": [{"id": node.id, "kind": node.kind.value,
                   "artifact_kind": node.artifact_kind.value,
                   "locator": _locator_wire(node.locator), "lifecycle": node.lifecycle.value,
                   "provenance": _provenance_wire(node.provenance)} for node in snapshot.nodes],
        "relations": [{"source": relation.source, "relation": relation.relation.value,
                       "target": relation.target, "evidence": relation.evidence.value,
                       "provenance": _provenance_wire(relation.provenance),
                       "lifecycle": relation.lifecycle.value} for relation in snapshot.relations],
    }


def _normalized_wire(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalized_wire(item) for key, item in sorted(value.items()) if item is not None}
    if isinstance(value, list):
        normalized = [_normalized_wire(item) for item in value]
        if all(isinstance(item, dict) and "id" in item for item in normalized):
            return sorted(normalized, key=lambda item: item["id"])
        if all(isinstance(item, dict) and {"source", "relation", "target"} <= set(item) for item in normalized):
            return sorted(normalized, key=lambda item: (item["source"], item["relation"], item["target"]))
        return normalized
    return value


def _locator_valid(value: Any) -> bool:
    allowed = {"path", "heading", "symbol", "test_name", "config_key", "schema_name"}
    return (isinstance(value, dict) and set(value) <= allowed
            and isinstance(value.get("path"), str) and bool(value["path"])
            and all(item is None or isinstance(item, str) for item in value.values()))


def _provenance_valid(value: Any) -> bool:
    if not isinstance(value, dict) or not set(value) <= {
            "produced_from", "governed_by", "surface", "locator", "attested_by"}:
        return False
    for field in ("produced_from", "governed_by"):
        if not isinstance(value.get(field, []), list) or not all(isinstance(item, str) for item in value.get(field, [])):
            return False
    return ((value.get("surface") is None or isinstance(value.get("surface"), str))
            and (value.get("attested_by") is None or isinstance(value.get("attested_by"), str))
            and (value.get("locator") is None or _locator_valid(value.get("locator"))))


def _node_wire_valid(value: Any) -> bool:
    required = {"id", "kind", "artifact_kind", "locator", "lifecycle", "provenance"}
    return (isinstance(value, dict) and set(value) == required
            and isinstance(value.get("id"), str) and bool(value["id"])
            and value.get("kind") in NODE_KINDS and value.get("artifact_kind") in ARTIFACT_KINDS
            and value.get("lifecycle") in {"active", "deprecated", "removed"}
            and _locator_valid(value.get("locator")) and _provenance_valid(value.get("provenance")))


def _relation_wire_valid(value: Any) -> bool:
    required = {"source", "relation", "target", "evidence", "provenance", "lifecycle"}
    return (isinstance(value, dict) and set(value) == required
            and isinstance(value.get("source"), str) and bool(value["source"])
            and isinstance(value.get("target"), str) and bool(value["target"])
            and value.get("relation") in RELATION_NAMES
            and value.get("evidence") in {"declared", "observed"}
            and value.get("lifecycle") in {"active", "deprecated", "removed"}
            and _provenance_valid(value.get("provenance")))


def _entity_identity(entity: str, value: Any):
    if not isinstance(value, dict):
        return None
    if entity == "node":
        return value.get("id")
    return (value.get("source"), value.get("relation"), value.get("target"))


def _mechanical_envelope_valid(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {
            "schema_version", "status", "diagnostics", "summary"}:
        return False
    diagnostics, summary = value.get("diagnostics"), value.get("summary")
    if value.get("schema_version") != 1 or value.get("status") not in {"pass", "fail"}:
        return False
    if not isinstance(diagnostics, list) or not isinstance(summary, dict):
        return False
    if not all(isinstance(item, dict) and isinstance(item.get("code"), str)
               and isinstance(item.get("message"), str)
               and item.get("severity") in {"info", "warning", "error"} for item in diagnostics):
        return False
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    expected_status = "fail" if errors else "pass"
    return (value["status"] == expected_status
            and summary == {"errors": errors, "warnings": warnings})


def _mechanical_envelope_passes(value: Any) -> bool:
    return _mechanical_envelope_valid(value) and value["status"] == "pass"


def _apply_mutation_delta(baseline: Any, mutations: Sequence[Any]):
    if not isinstance(baseline, dict) or baseline.get("schema_version") != 1:
        return None
    if not isinstance(baseline.get("nodes"), list) or not isinstance(baseline.get("relations"), list):
        return None
    current = json.loads(json.dumps(baseline))
    for mutation in mutations:
        if not isinstance(mutation, dict) or mutation.get("entity") not in {"node", "relation"}:
            return None
        collection = current["nodes" if mutation["entity"] == "node" else "relations"]
        before, after, operation = mutation.get("before"), mutation.get("after"), mutation.get("operation")
        normalized = [_normalized_wire(item) for item in collection]
        if operation == "add":
            identity = _entity_identity(mutation["entity"], after)
            if any(_entity_identity(mutation["entity"], item) == identity for item in collection):
                return None
            collection.append(after)
        elif operation in {"update", "remove"}:
            matches = [index for index, item in enumerate(normalized) if item == _normalized_wire(before)]
            if len(matches) != 1:
                return None
            collection.pop(matches[0])
            if operation == "update":
                if any(_entity_identity(mutation["entity"], item) == _entity_identity(mutation["entity"], after)
                       for item in collection):
                    return None
                collection.append(after)
        else:
            return None
    return current


def validate_transaction(value: Any, root: Path = None,
                         source_snapshot: GraphSnapshot = None) -> Tuple[Diagnostic, ...]:
    if not isinstance(value, dict):
        return (diagnostic("transaction_shape_invalid", "transaction must be a JSON object"),)
    findings: List[Diagnostic] = []
    state = value.get("state")
    if state not in TRANSACTION_STATES:
        findings.append(diagnostic("transaction_state_invalid", "unsupported transaction state: %s" % state))
    if value.get("schema_version") != 1:
        findings.append(diagnostic("transaction_schema_invalid", "transaction schema_version must be 1"))
    for field in ("transaction_id", "scope_ref"):
        if not isinstance(value.get(field), str) or not value[field]:
            findings.append(diagnostic("transaction_field_missing", "%s is required" % field))
    input_deltas = value.get("input_deltas", [])
    if not isinstance(input_deltas, list):
        findings.append(diagnostic("input_deltas_invalid", "input_deltas must be an array"))
        input_deltas = []
    for delta in input_deltas:
        valid = (isinstance(delta, dict) and set(delta) == {"kind", "source_surface", "changed_locators",
                 "semantic_summary", "baseline_digest", "graph_relevant"}
                 and delta.get("kind") in {"document_delta", "artifact_delta"}
                 and isinstance(delta.get("source_surface"), str) and bool(delta["source_surface"])
                 and isinstance(delta.get("changed_locators"), list)
                 and all(_locator_valid(locator) for locator in delta.get("changed_locators", []))
                 and isinstance(delta.get("semantic_summary"), str)
                 and bool(_DIGEST.fullmatch(str(delta.get("baseline_digest", ""))))
                 and isinstance(delta.get("graph_relevant"), bool))
        if not valid:
            findings.append(diagnostic("input_delta_invalid", "input delta does not match change_delta wire"))
    if not isinstance(value.get("coverage_debt", []), list) or not all(
            isinstance(item, str) for item in value.get("coverage_debt", []) if isinstance(value.get("coverage_debt", []), list)):
        findings.append(diagnostic("coverage_debt_invalid", "coverage_debt must be an array of strings"))
    mutations = value.get("canonical_mutations", [])
    if not isinstance(mutations, list):
        findings.append(diagnostic("transaction_mutations_invalid", "canonical_mutations must be an array"))
        mutations = []
    mutation_identities = set()
    for index, mutation in enumerate(mutations):
        if not isinstance(mutation, dict):
            findings.append(diagnostic("transaction_mutation_invalid", "canonical_mutations[%d] must be an object" % index))
        elif mutation.get("operation") not in {"add", "update", "remove"}:
            findings.append(diagnostic("mutation_operation_invalid", "mutation operation is invalid"))
        elif mutation.get("entity") not in {"node", "relation"}:
            findings.append(diagnostic("mutation_entity_invalid", "mutation entity is invalid"))
        elif mutation.get("evidence") == "inferred":
            findings.append(diagnostic("inferred_mutation_forbidden", "inferred evidence cannot be a canonical mutation"))
        elif mutation.get("evidence") not in {"declared", "observed"}:
            findings.append(diagnostic("mutation_evidence_invalid", "mutation evidence must be declared or observed"))
        else:
            operation = mutation["operation"]
            before, after = mutation.get("before"), mutation.get("after")
            if ((operation == "add" and (before is not None or not isinstance(after, dict)))
                    or (operation == "remove" and (not isinstance(before, dict) or after is not None))
                    or (operation == "update" and (not isinstance(before, dict) or not isinstance(after, dict)))):
                findings.append(diagnostic("mutation_shape_invalid",
                                           "mutation before/after values do not match operation"))
            entity_values = [item for item in (before, after) if item is not None]
            validator = _node_wire_valid if mutation["entity"] == "node" else _relation_wire_valid
            if any(not validator(item) for item in entity_values):
                findings.append(diagnostic("mutation_%s_invalid" % mutation["entity"],
                                           "canonical mutation entity does not match the canonical wire"))
            identities = {_entity_identity(mutation["entity"], item) for item in entity_values}
            if len(identities) > 1:
                findings.append(diagnostic("mutation_identity_changed",
                                           "update/remove mutation identity must remain stable"))
            identity = next(iter(identities), None)
            key = (mutation["entity"], identity)
            if identity is not None and key in mutation_identities:
                findings.append(diagnostic("mutation_identity_duplicate",
                                           "multiple canonical mutations target the same identity"))
            mutation_identities.add(key)

    patches = value.get("surface_patches", [])
    attestations = value.get("attestations", [])
    results = value.get("apply_results", [])
    if not all(isinstance(items, list) for items in (patches, attestations, results)):
        findings.append(diagnostic("transaction_collection_invalid", "patch, attestation, and result fields must be arrays"))
        return tuple(findings)
    patch_by_id = {}
    for patch in patches:
        if not isinstance(patch, dict):
            findings.append(diagnostic("surface_patch_invalid", "surface patch must be an object"))
            continue
        patch_id = patch.get("patch_id")
        if not isinstance(patch_id, str) or not patch_id:
            findings.append(diagnostic("patch_id_missing", "surface patch requires patch_id"))
        elif patch_id in patch_by_id:
            findings.append(diagnostic("patch_id_duplicate", "surface patch ID is duplicated: %s" % patch_id))
        else:
            patch_by_id[patch_id] = patch
        if patch.get("owner") not in {"author", "main", "coordinator"}:
            findings.append(diagnostic("patch_owner_invalid", "surface patch owner is invalid"))
        if patch.get("surface") not in {"document_metadata", "code_anchor", "config_anchor", "schema_anchor",
                                         "api_anchor", "test_anchor", "companion_metadata"}:
            findings.append(diagnostic("patch_surface_invalid", "surface patch surface is invalid"))
        elif patch.get("owner") in {"author", "main", "coordinator"} and not patch_owner_matches_surface(
                PatchOwner(patch["owner"]), PatchSurface(patch["surface"]), patch.get("target_path")):
            findings.append(diagnostic("patch_owner_surface_invalid",
                                       "patch owner does not own the described surface"))
        if not isinstance(patch.get("target_path"), str) or not patch["target_path"]:
            findings.append(diagnostic("patch_target_missing", "surface patch target_path is required"))
        elif root is not None:
            try:
                _safe_path(root, patch["target_path"])
            except ValueError as error:
                findings.append(diagnostic("patch_target_invalid", str(error), patch["target_path"]))
        if not isinstance(patch.get("exact_patch"), str) or not patch["exact_patch"]:
            findings.append(diagnostic("patch_exact_patch_invalid", "surface patch exact_patch must be non-empty"))
        if not isinstance(patch.get("required"), bool):
            findings.append(diagnostic("patch_required_invalid", "surface patch required must be boolean"))
        if not _DIGEST.fullmatch(str(patch.get("baseline_digest", ""))):
            findings.append(diagnostic("patch_baseline_invalid", "patch baseline_digest is invalid"))
    required = {patch_id: patch for patch_id, patch in patch_by_id.items()
                if patch.get("required") is True}
    if mutations and not required:
        findings.append(diagnostic("graph_change_required_patch_missing",
                                   "graph-changing transaction requires at least one required patch"))
    confirmed = set()
    rejected = set()
    needs_revision = set()
    applied = set()
    stale_baselines = set()
    failed_results = set()
    seen_attestations = set()
    for item in attestations:
        if not isinstance(item, dict):
            findings.append(diagnostic("attestation_invalid", "attestation must be an object"))
            continue
        shape_valid = (set(item) == {"patch_id", "owner", "decision", "evidence"}
                       and isinstance(item.get("patch_id"), str) and bool(item["patch_id"])
                       and item.get("owner") in {"author", "main", "coordinator"}
                       and item.get("decision") in {"confirm", "reject", "needs_revision"}
                       and isinstance(item.get("evidence"), str) and bool(item["evidence"].strip()))
        if not shape_valid:
            findings.append(diagnostic("attestation_invalid", "attestation does not match canonical wire"))
        attestation_key = item.get("patch_id")
        if attestation_key in seen_attestations:
            findings.append(diagnostic("attestation_duplicate", "patch has duplicate attestations"))
        seen_attestations.add(attestation_key)
        patch = patch_by_id.get(item.get("patch_id"))
        if patch is None:
            findings.append(diagnostic("attestation_patch_unknown", "attestation references an unknown patch"))
        elif item.get("owner") != patch.get("owner"):
            findings.append(diagnostic("attestation_owner_mismatch", "attestation owner does not own patch"))
        if item.get("decision") not in {"confirm", "reject", "needs_revision"}:
            findings.append(diagnostic("attestation_decision_invalid", "attestation decision is invalid"))
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
            findings.append(diagnostic("attestation_evidence_missing", "attestation evidence is required"))
        if shape_valid and patch is not None and item["owner"] == patch.get("owner"):
            evidence_set = {
                "confirm": confirmed,
                "reject": rejected,
                "needs_revision": needs_revision,
            }[item["decision"]]
            evidence_set.add(item["patch_id"])
    seen_results = set()
    for item in results:
        if not isinstance(item, dict):
            findings.append(diagnostic("apply_result_invalid", "apply result must be an object"))
            continue
        shape_valid = (set(item) == {"patch_id", "result", "resulting_digest", "evidence"}
                       and isinstance(item.get("patch_id"), str) and bool(item["patch_id"])
                       and item.get("result") in {"applied", "failed", "stale_baseline"}
                       and (item.get("resulting_digest") is None or isinstance(item.get("resulting_digest"), str))
                       and isinstance(item.get("evidence"), str) and bool(item["evidence"].strip()))
        if not shape_valid:
            findings.append(diagnostic("application_result_invalid",
                                       "application result does not match canonical wire"))
        result_key = item.get("patch_id")
        if result_key in seen_results:
            findings.append(diagnostic("apply_result_duplicate", "patch has duplicate application results"))
        seen_results.add(result_key)
        patch = patch_by_id.get(item.get("patch_id"))
        if patch is None:
            findings.append(diagnostic("apply_result_patch_unknown", "apply result references an unknown patch"))
            continue
        if item.get("result") not in {"applied", "failed", "stale_baseline"}:
            findings.append(diagnostic("application_status_invalid", "application result status is invalid"))
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
            findings.append(diagnostic("application_evidence_missing", "application result evidence is required"))
        resulting_digest = item.get("resulting_digest")
        if item.get("result") == "applied" and not _DIGEST.fullmatch(str(resulting_digest or "")):
            findings.append(diagnostic("resulting_digest_invalid", "applied result requires a sha256 digest"))
        elif item.get("result") == "applied" and root is not None:
            try:
                target = _safe_path(root, patch.get("target_path"))
            except ValueError as error:
                findings.append(diagnostic("patch_target_invalid", str(error), patch.get("target_path")))
            else:
                actual = ("sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
                          if target.is_file() else "absent")
                if resulting_digest != actual:
                    findings.append(diagnostic("resulting_digest_mismatch",
                                               "resulting digest does not match current source bytes",
                                               patch.get("target_path")))
        if shape_valid and patch is not None:
            evidence_set = {
                "applied": applied,
                "stale_baseline": stale_baselines,
                "failed": failed_results,
            }[item["result"]]
            evidence_set.add(item["patch_id"])
    if state == "proposed" and (attestations or results):
        findings.append(diagnostic("proposed_evidence_forbidden",
                                   "proposed transaction cannot contain attestation or apply evidence"))
    if state == "awaiting_attestation" and results:
        findings.append(diagnostic("preapply_result_forbidden",
                                   "awaiting_attestation transaction cannot contain apply results"))
    if state in {"ready_to_apply", "applying", "partially_applied", "verified"}:
        if not set(required) <= confirmed:
            findings.append(diagnostic("state_attestation_incomplete",
                                       "%s requires all required patch confirmations" % state))
    if state == "partially_applied":
        if not (applied & set(required)) or not (set(required) - applied):
            findings.append(diagnostic("partial_application_missing",
                                       "partially_applied requires both applied and pending required patches"))
    if state == "conflicted":
        if not (rejected or needs_revision or stale_baselines):
            findings.append(diagnostic("conflict_evidence_missing",
                                       "conflicted requires rejection, revision, or stale-baseline evidence"))
    if state == "failed":
        mechanical = value.get("mechanical_validation")
        failed_validation = (_mechanical_envelope_valid(mechanical)
                             and mechanical["status"] == "fail")
        if not (failed_results or failed_validation):
            findings.append(diagnostic("failure_evidence_missing",
                                       "failed requires failed application or mechanical error evidence"))
    mechanical = value.get("mechanical_validation")
    if mechanical is not None and not _mechanical_envelope_valid(mechanical):
        findings.append(diagnostic("mechanical_validation_invalid",
                                   "mechanical_validation must be a structurally valid diagnostic envelope"))
    if state == "verified":
        if not required or not mutations:
            findings.append(diagnostic("verified_closure_vacuous",
                                       "verified requires required patches and canonical mutations"))
        for patch_id in sorted(required):
            if patch_id not in confirmed:
                findings.append(diagnostic("verified_attestation_missing", "verified patch lacks confirm: %s" % patch_id))
            if patch_id not in applied:
                findings.append(diagnostic("verified_apply_missing", "verified patch lacks applied result: %s" % patch_id))
        reconstruction_evidence = value.get("reconstruction")
        if not (isinstance(reconstruction_evidence, dict)
                and set(reconstruction_evidence) == {"baseline", "result"}
                and isinstance(reconstruction_evidence.get("baseline"), dict)
                and isinstance(reconstruction_evidence.get("result"), dict)):
            findings.append(diagnostic("verified_reconstruction_missing", "verified transaction requires reconstruction"))
        elif source_snapshot is not None and _normalized_wire(reconstruction_evidence["result"]) != _normalized_wire(snapshot_wire(source_snapshot)):
            findings.append(diagnostic("verified_reconstruction_mismatch",
                                       "verified reconstruction differs from source-only reconstruction"))
        mechanical = value.get("mechanical_validation")
        if not isinstance(mechanical, dict):
            findings.append(diagnostic("verified_validation_missing", "verified transaction requires mechanical_validation"))
            if mechanical == []:
                findings.append(diagnostic("verified_validation_empty",
                                           "verified transaction requires explicit passing mechanical evidence"))
        elif not _mechanical_envelope_passes(mechanical):
            findings.append(diagnostic("verified_validation_failed", "verified mechanical envelope does not pass"))
        baseline = reconstruction_evidence.get("baseline") if isinstance(reconstruction_evidence, dict) else None
        reconstruction = reconstruction_evidence.get("result") if isinstance(reconstruction_evidence, dict) else None
        applied_snapshot = _apply_mutation_delta(baseline, mutations)
        if applied_snapshot is None or not isinstance(reconstruction, dict) or (
                _normalized_wire(applied_snapshot) != _normalized_wire(reconstruction)):
            findings.append(diagnostic("mutation_baseline_closure_mismatch",
                                       "baseline plus canonical mutations must exactly equal reconstruction"))
            findings.append(diagnostic("mutation_reconstruction_mismatch",
                                       "canonical mutation delta differs from reconstruction"))
    return tuple(findings)


def diagnostic_dict(item: Diagnostic) -> Dict[str, Any]:
    result = {"code": item.code, "message": item.message, "severity": item.severity.value}
    if item.path is not None:
        result["path"] = item.path
    if item.locator is not None:
        result["locator"] = {key: value for key, value in asdict(item.locator).items() if value is not None}
    return result


def envelope(diagnostics: Iterable[Diagnostic], *, execution_error: bool = False) -> Dict[str, Any]:
    serialized = [diagnostic_dict(item) for item in diagnostics]
    errors = sum(item["severity"] == "error" for item in serialized)
    warnings = sum(item["severity"] == "warning" for item in serialized)
    return {
        "schema_version": 1,
        "status": "error" if execution_error else ("fail" if errors else "pass"),
        "diagnostics": serialized,
        "summary": {"errors": errors, "warnings": warnings},
    }
