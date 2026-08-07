import re
import shlex
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .adapters import Adapter
from .companion import parse_companion
from .dependency import DependencySource
from .metadata_support import metadata_strings, sorted_snapshot
from .model import (
    ArtifactKind,
    Diagnostic,
    Locator,
    Node,
    NodeKind,
    ParseResult,
    Relation,
)
from .source_hierarchy import build_source_node
from .source_relations import RELATION_TYPES, build_source_relations
from .source_unit import SourceSurface, resolve_source_unit
from .yaml_subset import MetadataError, parse_yaml_subset


_COMPACT_MULTI_VALUE_FIELDS = frozenset({
    "refs", "produced_from", "governed_by", "legacy_terms", "aliases",
}) | frozenset(RELATION_TYPES)


def _compact(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    current_key: Optional[str] = None
    for token in shlex.split(text.replace(", ", ",")):
        if "=" in token:
            key, value = token.split("=", 1)
            values = [part for part in value.split(",") if part]
            if key in _COMPACT_MULTI_VALUE_FIELDS:
                existing = result.get(key, [])
                if not isinstance(existing, list):
                    existing = [existing] if existing else []
                result[key] = existing + values
            else:
                result[key] = values if len(values) > 1 else (values[0] if values else "")
            current_key = key
            continue
        if current_key not in _COMPACT_MULTI_VALUE_FIELDS:
            raise MetadataError(
                "bare compact metadata token is not attached to a list field: %s" % token
            )
        continuations = [part for part in token.split(",") if part]
        existing = result.get(current_key, [])
        if not isinstance(existing, list):
            existing = [existing] if existing else []
        result[current_key] = existing + continuations
    if not result:
        raise MetadataError("metadata contains no key/value declarations")
    return result


def _metadata(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    if "=" in stripped and not re.search(r"^\s*[\w.]+\s*:", stripped, re.MULTILINE):
        compact = _compact(stripped)
        locator: Dict[str, Any] = {}
        for key in tuple(compact):
            if key.startswith("locator."):
                locator[key[len("locator."):]] = compact.pop(key)
        if locator:
            compact["locator"] = locator
        if compact.get("depends_on"):
            compact["_legacy_dependencies"] = metadata_strings(compact["depends_on"])
        return compact
    raw = parse_yaml_subset(stripped)
    key_value = raw.get("key")
    if isinstance(key_value, dict):
        data = dict(key_value)
    elif isinstance(key_value, str):
        data = {"id": key_value}
    else:
        data = {}
    structured_relations = data.pop("relations", None)
    legacy_dependencies = metadata_strings(data.get("depends_on"))
    structured_dependencies: Tuple[str, ...] = ()
    relation_conflicts = []
    if structured_relations is not None:
        if not isinstance(structured_relations, dict):
            raise MetadataError("key.relations must be a mapping")
        for name, raw_targets in structured_relations.items():
            if name not in RELATION_TYPES:
                raise MetadataError("unknown structured relation: %s" % name)
            if not isinstance(raw_targets, list):
                raw_targets = [raw_targets]
            targets = []
            for raw_target in raw_targets:
                if isinstance(raw_target, dict):
                    if set(raw_target) != {"target"} or not isinstance(raw_target.get("target"), str):
                        raise MetadataError("structured relation target must contain only target")
                    targets.append(raw_target["target"])
                elif isinstance(raw_target, str):
                    targets.append(raw_target)
                else:
                    raise MetadataError("structured relation target must be a string or mapping")
            legacy_targets = metadata_strings(data.get(name))
            if legacy_targets and set(legacy_targets) != set(targets):
                relation_conflicts.append(name)
            data[name] = targets
            if name == "depends_on":
                structured_dependencies = tuple(targets)
    for key, value in raw.items():
        if key.startswith("key."):
            data[key[4:]] = value
        elif key == "locator":
            data["locator"] = value
        elif key.startswith("locator."):
            locator = data.setdefault("locator", {})
            if not isinstance(locator, dict):
                raise MetadataError("locator must be a mapping")
            locator[key[len("locator."):]] = value
    if "document_lifecycle" in raw:
        data["_document_lifecycle"] = raw["document_lifecycle"]
    approval = raw.get("approval")
    if isinstance(approval, dict) and "state" in approval:
        data["_approval_state"] = approval["state"]
    if "authority" in raw:
        data["_source_authority"] = raw["authority"]
    if "work_gates" in raw:
        data["_work_gates"] = raw["work_gates"]
    for field in ("doc_type", "work_status", "step_ref", "work_ref"):
        if field in raw:
            data["_" + field] = raw[field]
    if legacy_dependencies and (
            not structured_dependencies
            or set(legacy_dependencies) != set(structured_dependencies)):
        data["_legacy_dependencies"] = legacy_dependencies
    if structured_dependencies:
        data["_structured_dependencies"] = structured_dependencies
    if relation_conflicts:
        data["_relation_conflicts"] = tuple(sorted(relation_conflicts))
    if not data and "id" in raw:
        data = raw
    return data


def parse_reference_declaration(text: str) -> Optional[Tuple[str, Tuple[str, ...]]]:
    """Return one owner ID and its untyped navigation refs from a metadata block."""
    data = _metadata(text)
    source_id = data.get("id")
    if not isinstance(source_id, str) or not source_id:
        return None
    return source_id, metadata_strings(data.get("refs"))


def _kind(value: Any, construct: Optional[str], markdown: bool) -> NodeKind:
    if value:
        try:
            return NodeKind(str(value))
        except ValueError:
            aliases = {"code_artifact": NodeKind.OUTPUT_ARTIFACT, "artifact": NodeKind.OUTPUT_ARTIFACT}
            if str(value) in aliases:
                return aliases[str(value)]
            raise MetadataError("unknown node kind: %s" % value)
    if construct == "document":
        return NodeKind.SOURCE_DOCUMENT
    if construct == "heading":
        return NodeKind.DOCUMENT_SECTION
    if construct in {"list", "table"}:
        return NodeKind.DOCUMENT_ITEM
    return NodeKind.DOCUMENT_ITEM if markdown else NodeKind.OUTPUT_ARTIFACT


def _artifact_kind(value: Any, kind: NodeKind, surface: str) -> ArtifactKind:
    if value:
        try:
            return ArtifactKind(str(value))
        except ValueError as error:
            raise MetadataError("unknown artifact kind: %s" % value) from error
    if kind != NodeKind.OUTPUT_ARTIFACT:
        return ArtifactKind.NONE
    defaults = {
        "code_anchor": ArtifactKind.CODE,
        "config_anchor": ArtifactKind.CONFIG,
        "schema_anchor": ArtifactKind.SCHEMA,
        "api_anchor": ArtifactKind.API,
        "test_anchor": ArtifactKind.TEST,
        "companion_metadata": ArtifactKind.NONE,
        "document_metadata": ArtifactKind.NONE,
    }
    return defaults.get(surface, ArtifactKind.NONE)


_KNOWN_METADATA = {
    "id", "kind", "artifact_kind", "refs", "lifecycle", "produced_from", "governed_by",
    "legacy_terms", "aliases", "locator", "_document_lifecycle", "_approval_state",
    "_source_authority", "_work_gates", "_relation_conflicts", "_doc_type",
    "_work_status", "_step_ref", "_work_ref", "_legacy_dependencies",
    "_structured_dependencies",
} | set(RELATION_TYPES)


def _declared_locator(data: Mapping[str, Any], path: str, construct: Optional[str],
                      label: Optional[str]) -> Tuple[Locator, Tuple[Diagnostic, ...]]:
    raw = data.get("locator", {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise MetadataError("locator must be a mapping")
    allowed = {"path", "heading", "symbol", "test_name", "config_key", "schema_name"}
    unknown = set(raw) - allowed
    if unknown:
        raise MetadataError("unknown locator fields: %s" % sorted(unknown))
    diagnostics: List[Diagnostic] = []
    declared_path = raw.get("path")
    if declared_path is not None and (not isinstance(declared_path, str) or not declared_path):
        raise MetadataError("locator path must be a non-empty string")
    if declared_path and declared_path != path:
        diagnostics.append(Diagnostic("locator_conflict", "declared locator path does not match source path",
                                      path=path))
    observed_heading = label if construct == "heading" else None
    observed_symbol = label if construct in {"list", "table"} else None
    if raw.get("heading") and observed_heading and raw["heading"] != observed_heading:
        diagnostics.append(Diagnostic("locator_conflict", "declared heading conflicts with observed heading",
                                      path=path))
    if raw.get("symbol") and observed_symbol and raw["symbol"] != observed_symbol:
        diagnostics.append(Diagnostic("locator_conflict", "declared symbol conflicts with observed item",
                                      path=path))
    return Locator(path=path,
                   heading=observed_heading or raw.get("heading"),
                   symbol=raw.get("symbol") or observed_symbol,
                   test_name=raw.get("test_name"), config_key=raw.get("config_key"),
                   schema_name=raw.get("schema_name")), tuple(diagnostics)


# keystone: id=key.code.linker.metadata-parser kind=output_artifact artifact_kind=code refs=key.standard.skill.linker.metadata-parsing locator.symbol=parse_source
def parse_source(text: str, path: str, adapter: Optional[Adapter], *,
                 companion_text: Optional[str] = None,
                 companion_path: Optional[str] = None,
                 companion_source_exists: Optional[bool] = None,
                 companion_source_bytes: Optional[bytes] = None) -> ParseResult:
    if adapter is not None and companion_text is not None:
        unit = resolve_source_unit(
            path,
            text.encode("utf-8"),
            companion_text.encode("utf-8"),
        )
        if unit.diagnostics:
            return ParseResult(diagnostics=unit.diagnostics)
        if unit.surface == SourceSurface.COMPANION:
            return parse_companion(
                companion_text,
                companion_path or path + ".keystone.json",
                path,
                source_exists=companion_source_exists,
                source_bytes=companion_source_bytes,
            )
    if adapter is None:
        if companion_text is None:
            diagnostic = Diagnostic("unsupported_surface", "no mechanically safe adapter or companion", path=path)
            return ParseResult(diagnostics=(diagnostic,))
        return parse_companion(companion_text, companion_path or path + ".keystone.json", path,
                               source_exists=companion_source_exists, source_bytes=companion_source_bytes)

    nodes: Dict[str, Node] = {}
    relations: Dict[Tuple[str, str, str], Relation] = {}
    diagnostics: List[Diagnostic] = []
    markdown = adapter.surface == "document_metadata"
    document_node: Optional[Node] = None
    current_section_node: Optional[Node] = None
    section_nodes_by_offset: Dict[int, Node] = {}
    parsed_work_gates = ()
    dependency_sources = []
    contextual_blocks = (
        adapter.metadata_blocks_with_context(text)
        if markdown and hasattr(adapter, "metadata_blocks_with_context")
        else None
    )
    blocks = contextual_blocks if contextual_blocks is not None else adapter.metadata_blocks(text)
    for raw_block in blocks:
        if hasattr(raw_block, "text"):
            block = raw_block.text
            construct = raw_block.construct
            label = raw_block.label
            target_offset = raw_block.target_offset
            enclosing_heading_offset = raw_block.enclosing_heading_offset
        else:
            block, construct, label = raw_block
            target_offset = None
            enclosing_heading_offset = None
        try:
            data = _metadata(block)
            node_id = str(data.get("id", "")).strip()
            if not node_id:
                raise MetadataError("metadata id is required")
            kind = _kind(data.get("kind"), construct, markdown)
            locator, locator_diagnostics = _declared_locator(data, path, construct, label)
            diagnostics.extend(locator_diagnostics)
            for unknown in sorted(set(data) - _KNOWN_METADATA):
                diagnostics.append(Diagnostic("unknown_metadata_field",
                                              "unknown metadata field: %s" % unknown, path=path,
                                              locator=locator))
            parent = None
            if markdown and construct != "document":
                if target_offset is not None:
                    parent = section_nodes_by_offset.get(enclosing_heading_offset)
                else:
                    parent = (current_section_node
                              if construct in {"list", "table", None}
                              else document_node)
                if parent is None:
                    parent = document_node
            node_result = build_source_node(
                data,
                node_id,
                kind,
                _artifact_kind(data.get("artifact_kind"), kind, adapter.surface),
                locator,
                adapter.surface,
                parent,
                path,
            )
            diagnostics.extend(node_result.diagnostics)
            node = node_result.node
            if node_id in nodes:
                diagnostics.append(Diagnostic("duplicate_id", "duplicate node id: %s" % node_id,
                                              path=path, locator=locator))
                continue
            nodes[node_id] = node
            if markdown and construct == "document":
                document_node = node
            elif markdown and construct == "heading":
                current_section_node = node
                if target_offset is not None:
                    section_nodes_by_offset[target_offset] = node
            relation_result = build_source_relations(
                data,
                node,
                construct,
                adapter.surface,
                path,
                locator,
            )
            diagnostics.extend(relation_result.diagnostics)
            if relation_result.work_gates is not None:
                parsed_work_gates = relation_result.work_gates
            if (construct == "document"
                    or data.get("depends_on")
                    or data.get("_legacy_dependencies")
                    or relation_result.work_gates is not None):
                dependency_sources.append(DependencySource(
                    source_id=node.id,
                    path=path,
                    work_status=str(data.get("_work_status", "")),
                    approval_state=str(data.get("_approval_state", "")),
                    step_ref=str(data.get("_step_ref", "")),
                    work_ref=str(data.get("_work_ref", "")),
                    structured_dependencies=tuple(data.get("_structured_dependencies", ())),
                    legacy_dependencies=tuple(data.get("_legacy_dependencies", ())),
                    gates=relation_result.work_gates or (),
                    is_work=(node.kind == NodeKind.WORK_ORDER
                             or data.get("_doc_type") == "work_order"),
                ))
            for relation in relation_result.relations:
                key = (relation.source, relation.relation.value, relation.target)
                if relation.evidence.value == "inferred" and key in relations:
                    continue
                relations[key] = relation
            # refs remain navigation evidence and are deliberately not typed relations.
        except (MetadataError, ValueError, TypeError) as error:
            diagnostics.append(Diagnostic("malformed_metadata", str(error), path=path))
    return ParseResult(sorted_snapshot(nodes.values(), relations.values()), tuple(diagnostics),
                       work_gates=parsed_work_gates,
                       dependency_sources=tuple(dependency_sources))
