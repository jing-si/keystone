import hashlib
import json
import re
import shlex
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .adapters import Adapter
from .model import (
    ArtifactKind,
    Diagnostic,
    Evidence,
    GraphSnapshot,
    Lifecycle,
    Locator,
    Node,
    NodeKind,
    ParseResult,
    Provenance,
    Relation,
    RelationType,
    SCHEMA_VERSION,
)


_RELATIONS = {member.value: member for member in RelationType}


class MetadataError(ValueError):
    pass


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("["):
        if not value.endswith("]"):
            raise MetadataError("unterminated sequence")
        inner = value[1:-1].strip()
        return [] if not inner else [_scalar(part) for part in inner.split(",")]
    if value.startswith("{"):
        if not value.endswith("}"):
            raise MetadataError("unterminated mapping")
        return _inline_mapping(value[1:-1])
    if ((value.startswith("\"") and value.endswith("\"")) or
            (value.startswith("'") and value.endswith("'"))):
        return value[1:-1]
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _inline_mapping(body: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    parts = re.split(r",\s*(?![^\[]*\])", body)
    for part in parts:
        if not part.strip():
            continue
        if ":" not in part:
            raise MetadataError("invalid inline mapping")
        key, value = part.split(":", 1)
        result[key.strip()] = _scalar(value)
    return result


def _yaml_subset(text: str) -> Dict[str, Any]:
    if text == "__malformed_frontmatter__":
        raise MetadataError("frontmatter closing delimiter is missing")
    lines = [(len(raw) - len(raw.lstrip(" ")), raw.strip()) for raw in text.splitlines()
             if raw.strip() and not raw.lstrip().startswith("#")]
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Dict[str, Any]]] = [(-1, root)]
    index = 0
    while index < len(lines):
        indent, line = lines[index]
        if line.startswith("-"):
            raise MetadataError("sequence without mapping key")
        if ":" not in line:
            raise MetadataError("invalid mapping entry")
        key, raw_value = line.split(":", 1)
        key, raw_value = key.strip(), raw_value.strip()
        while stack[-1][0] >= indent:
            stack.pop()
        target = stack[-1][1]
        if raw_value:
            target[key] = _scalar(raw_value)
        else:
            # A following '- value' sequence belongs to this key.
            sequence: List[Any] = []
            cursor = index + 1
            while cursor < len(lines) and lines[cursor][0] > indent and lines[cursor][1].startswith("-"):
                sequence.append(_scalar(lines[cursor][1][1:].strip()))
                cursor += 1
            if sequence:
                target[key] = sequence
                index = cursor - 1
            else:
                child: Dict[str, Any] = {}
                target[key] = child
                stack.append((indent, child))
        index += 1
    return root


def _compact(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for token in shlex.split(text.replace(", ", ",")):
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        values = [part for part in value.split(",") if part]
        result[key] = values if len(values) > 1 else (values[0] if values else "")
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
        return compact
    raw = _yaml_subset(stripped)
    key_value = raw.get("key")
    if isinstance(key_value, dict):
        data = dict(key_value)
    elif isinstance(key_value, str):
        data = {"id": key_value}
    else:
        data = {}
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
    if not data and "id" in raw:
        data = raw
    return data


def _strings(value: Any) -> Tuple[str, ...]:
    if value is None or value == "":
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return (str(value),)


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


def _lifecycle(value: Any) -> Lifecycle:
    try:
        return Lifecycle(str(value or "active"))
    except ValueError as error:
        raise MetadataError("unknown lifecycle: %s" % value) from error


def _relation_values(data: Mapping[str, Any]) -> Iterable[Tuple[RelationType, str]]:
    for name, relation in _RELATIONS.items():
        for target in _strings(data.get(name)):
            yield relation, target


_KNOWN_METADATA = {
    "id", "kind", "artifact_kind", "refs", "lifecycle", "produced_from", "governed_by",
    "legacy_terms", "aliases", "locator",
} | set(_RELATIONS)


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


def _sort_snapshot(nodes: Iterable[Node], relations: Iterable[Relation]) -> GraphSnapshot:
    ordered_nodes = tuple(sorted(nodes, key=lambda node: (node.id, node.locator.path)))
    ordered_relations = tuple(sorted(
        relations,
        key=lambda relation: (relation.source, relation.relation.value, relation.target,
                              relation.evidence.value, relation.lifecycle.value),
    ))
    return GraphSnapshot(nodes=ordered_nodes, relations=ordered_relations)


def parse_source(text: str, path: str, adapter: Optional[Adapter], *,
                 companion_text: Optional[str] = None,
                 companion_path: Optional[str] = None,
                 companion_source_exists: Optional[bool] = None,
                 companion_source_bytes: Optional[bytes] = None) -> ParseResult:
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
    for block, construct, label in adapter.metadata_blocks(text):
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
            provenance = Provenance(
                produced_from=_strings(data.get("produced_from")),
                governed_by=_strings(data.get("governed_by")),
                surface=adapter.surface,
                locator=locator,
            )
            node = Node(node_id, kind, _artifact_kind(data.get("artifact_kind"), kind, adapter.surface),
                        locator, _lifecycle(data.get("lifecycle")), provenance)
            if node_id in nodes:
                diagnostics.append(Diagnostic("duplicate_id", "duplicate node id: %s" % node_id,
                                              path=path, locator=locator))
                continue
            nodes[node_id] = node
            for relation_type, target in _relation_values(data):
                relation = Relation(node_id, relation_type, target, Evidence.DECLARED,
                                    Provenance(surface=adapter.surface, locator=locator), node.lifecycle)
                relations[(node_id, relation_type.value, target)] = relation
            if node.kind == NodeKind.OUTPUT_ARTIFACT:
                for source_id in node.provenance.produced_from:
                    key = (source_id, RelationType.PRODUCES.value, node_id)
                    if key not in relations:
                        relations[key] = Relation(
                            source_id, RelationType.PRODUCES, node_id, Evidence.INFERRED,
                            Provenance(surface="derived_produced_from", locator=locator),
                            node.lifecycle,
                        )
            # refs remain navigation evidence and are deliberately not typed relations.
        except (MetadataError, ValueError, TypeError) as error:
            diagnostics.append(Diagnostic("malformed_metadata", str(error), path=path))
    return ParseResult(_sort_snapshot(nodes.values(), relations.values()), tuple(diagnostics))


def _locator(value: Any, default_path: str) -> Locator:
    if not isinstance(value, dict):
        raise MetadataError("locator must be an object")
    allowed = {"path", "heading", "symbol", "test_name", "config_key", "schema_name"}
    unknown = set(value) - allowed
    if unknown:
        raise MetadataError("unknown locator fields: %s" % sorted(unknown))
    path = value.get("path", default_path)
    if not isinstance(path, str) or not path:
        raise MetadataError("locator path must be a non-empty string")
    if any(item is not None and not isinstance(item, str) for item in value.values()):
        raise MetadataError("locator fields must be strings or null")
    return Locator(path=path,
                   heading=value.get("heading"), symbol=value.get("symbol"),
                   test_name=value.get("test_name"), config_key=value.get("config_key"),
                   schema_name=value.get("schema_name"))


def _companion_provenance(value: Any, default_path: str, *, relation: bool) -> Provenance:
    if not isinstance(value, dict):
        raise MetadataError("provenance must be an object")
    required = ({"surface", "locator", "attested_by"} if relation
                else {"produced_from", "governed_by"})
    if set(value) != required:
        raise MetadataError("%s provenance requires exactly: %s" % (
            "relation" if relation else "node", ", ".join(sorted(required))))
    if relation:
        if not isinstance(value["surface"], str) or not value["surface"]:
            raise MetadataError("relation provenance surface must be a non-empty string")
        if value["attested_by"] is not None and not isinstance(value["attested_by"], str):
            raise MetadataError("relation provenance attested_by must be a string or null")
    else:
        for field in ("produced_from", "governed_by"):
            if not isinstance(value[field], list) or not all(
                    isinstance(item, str) and item for item in value[field]):
                raise MetadataError("node provenance %s must be an array of non-empty strings" % field)
    locator = value.get("locator")
    return Provenance(produced_from=_strings(value.get("produced_from")),
                      governed_by=_strings(value.get("governed_by")),
                      surface=value.get("surface"),
                      locator=_locator(locator, default_path) if locator is not None else None,
                      attested_by=value.get("attested_by"))


def parse_companion(text: str, companion_path: str, expected_source_path: str, *,
                    source_exists: Optional[bool] = None,
                    source_bytes: Optional[bytes] = None) -> ParseResult:
    expected_companion_path = expected_source_path + ".keystone.json"
    if companion_path != expected_companion_path:
        diagnostic = Diagnostic("companion_path_mismatch",
                                "companion path %r must be source-adjacent %r" %
                                (companion_path, expected_companion_path), path=companion_path)
        return ParseResult(diagnostics=(diagnostic,))
    try:
        value = json.loads(text)
        if not isinstance(value, dict):
            raise MetadataError("companion root must be an object")
        if set(value) != {"schema_version", "source", "nodes", "relations"}:
            raise MetadataError("companion root requires exactly schema_version, source, nodes, and relations")
        if type(value.get("schema_version")) is not int or value["schema_version"] != SCHEMA_VERSION:
            raise MetadataError("companion schema_version must be 1")
        source = value.get("source")
        if not isinstance(source, dict):
            raise MetadataError("companion source must be an object")
        if set(source) != {"path", "surface", "baseline_digest"}:
            raise MetadataError("companion source requires path, surface, and baseline_digest")
        if not isinstance(source.get("path"), str) or not source["path"]:
            raise MetadataError("companion source path must be a non-empty string")
        if not isinstance(source.get("surface"), str) or not source.get("surface"):
            raise MetadataError("companion source surface must be a non-empty string")
        if source["surface"] != "companion_metadata":
            raise MetadataError("companion source surface must be companion_metadata")
        if "nodes" not in value or not isinstance(value["nodes"], list):
            raise MetadataError("companion nodes must be an array")
        if "relations" not in value or not isinstance(value["relations"], list):
            raise MetadataError("companion relations must be an array")
        source_path = source.get("path")
        if source_path != expected_source_path:
            diagnostic = Diagnostic("companion_source_mismatch",
                                    "companion source %r does not match %r" % (source_path, expected_source_path),
                                    path=companion_path)
            return ParseResult(diagnostics=(diagnostic,))
        baseline = source.get("baseline_digest")
        if baseline != "absent" and not re.fullmatch(r"sha256:[0-9a-f]{64}", str(baseline)):
            raise MetadataError("baseline_digest must be lowercase sha256 or absent")
        if source_exists is None:
            raise MetadataError("source existence must be supplied for baseline validation")
        if source_exists:
            if source_bytes is None:
                raise MetadataError("existing source raw bytes are required for baseline validation")
            actual = "sha256:" + hashlib.sha256(source_bytes).hexdigest()
            if baseline != actual:
                diagnostic = Diagnostic("companion_baseline_mismatch",
                                        "companion baseline does not match existing source bytes",
                                        path=companion_path)
                return ParseResult(diagnostics=(diagnostic,))
        elif baseline != "absent":
            diagnostic = Diagnostic("companion_baseline_mismatch",
                                    "new source baseline must be the string absent", path=companion_path)
            return ParseResult(diagnostics=(diagnostic,))
        nodes: List[Node] = []
        for raw in value["nodes"]:
            if not isinstance(raw, dict):
                raise MetadataError("node must be an object")
            if set(raw) != {"id", "kind", "artifact_kind", "locator", "lifecycle", "provenance"}:
                raise MetadataError("node does not match canonical companion fields")
            if not isinstance(raw["id"], str) or not raw["id"]:
                raise MetadataError("node id must be a non-empty string")
            nodes.append(Node(
                id=raw["id"], kind=NodeKind(raw["kind"]), artifact_kind=ArtifactKind(raw["artifact_kind"]),
                locator=_locator(raw["locator"], expected_source_path), lifecycle=Lifecycle(raw["lifecycle"]),
                provenance=_companion_provenance(raw["provenance"], expected_source_path, relation=False),
            ))
        relations: List[Relation] = []
        for raw in value["relations"]:
            if not isinstance(raw, dict):
                raise MetadataError("relation must be an object")
            if set(raw) != {"source", "relation", "target", "evidence", "provenance", "lifecycle"}:
                raise MetadataError("relation does not match canonical companion fields")
            if not all(isinstance(raw[field], str) and raw[field] for field in ("source", "target")):
                raise MetadataError("relation source and target must be non-empty strings")
            relations.append(Relation(
                source=raw["source"], relation=RelationType(raw["relation"]), target=raw["target"],
                evidence=Evidence(raw["evidence"]),
                provenance=_companion_provenance(raw["provenance"], expected_source_path, relation=True),
                lifecycle=Lifecycle(raw["lifecycle"]),
            ))
        return ParseResult(_sort_snapshot(nodes, relations), baseline_digest=str(baseline))
    except (json.JSONDecodeError, MetadataError, KeyError, TypeError, ValueError) as error:
        diagnostic = Diagnostic("malformed_companion", str(error), path=companion_path)
        return ParseResult(diagnostics=(diagnostic,))
