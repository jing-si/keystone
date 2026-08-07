"""Canonical source-adjacent companion metadata parser."""

import hashlib
import json
import re
from typing import Any, List, Optional

from .lifecycle_policy import (
    node_lifecycle_admitted,
    node_lifecycle_domain,
    relation_lifecycle_admitted,
)
from .metadata_support import metadata_strings, sorted_snapshot
from .model import (
    ArtifactKind,
    Diagnostic,
    Evidence,
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
from .yaml_subset import MetadataError


def load_authoritative_json(text: str) -> Any:
    """Decode external JSON while rejecting duplicate keys at every depth."""
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: %s" % key)
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("non-canonical JSON constant: %s" % value)

    return json.loads(
        text,
        object_pairs_hook=object_pairs,
        parse_constant=reject_constant,
    )


def parse_companion(
    text: str,
    companion_path: str,
    expected_source_path: str,
    *,
    source_exists: Optional[bool] = None,
    source_bytes: Optional[bytes] = None,
) -> ParseResult:
    expected_companion_path = expected_source_path + ".keystone.json"
    if companion_path != expected_companion_path:
        diagnostic = Diagnostic(
            "companion_path_mismatch",
            "companion path %r must be source-adjacent %r"
            % (companion_path, expected_companion_path),
            path=companion_path,
        )
        return ParseResult(diagnostics=(diagnostic,))
    try:
        value = load_authoritative_json(text)
        _validate_root(value)
        source = value["source"]
        source_path = source["path"]
        if source_path != expected_source_path:
            diagnostic = Diagnostic(
                "companion_source_mismatch",
                "companion source %r does not match %r"
                % (source_path, expected_source_path),
                path=companion_path,
            )
            return ParseResult(diagnostics=(diagnostic,))
        baseline = source["baseline_digest"]
        baseline_diagnostic = _validate_baseline(
            baseline,
            companion_path,
            source_exists,
            source_bytes,
        )
        if baseline_diagnostic is not None:
            return ParseResult(diagnostics=(baseline_diagnostic,))
        nodes = [
            _parse_node(raw, expected_source_path)
            for raw in value["nodes"]
        ]
        relations = [
            _parse_relation(raw, expected_source_path)
            for raw in value["relations"]
        ]
        diagnostics = []
        for node in nodes:
            if not node_lifecycle_admitted(node.kind, node.lifecycle):
                diagnostics.append(Diagnostic(
                    "node_lifecycle_domain_invalid",
                    "%s node cannot use %s lifecycle" % (
                        node_lifecycle_domain(node.kind), node.lifecycle.value,
                    ),
                    path=companion_path,
                    locator=node.locator,
                ))
        for relation in relations:
            if not relation_lifecycle_admitted(relation.lifecycle):
                diagnostics.append(Diagnostic(
                    "relation_lifecycle_domain_invalid",
                    "relation cannot use %s lifecycle" % relation.lifecycle.value,
                    path=companion_path,
                    locator=relation.provenance.locator,
                ))
        return ParseResult(
            sorted_snapshot(nodes, relations),
            diagnostics=tuple(diagnostics),
            baseline_digest=str(baseline),
        )
    except (json.JSONDecodeError, MetadataError, KeyError, TypeError, ValueError) as error:
        diagnostic = Diagnostic(
            "malformed_companion", str(error), path=companion_path
        )
        return ParseResult(diagnostics=(diagnostic,))


def _validate_root(value: Any) -> None:
    if not isinstance(value, dict):
        raise MetadataError("companion root must be an object")
    if set(value) != {"schema_version", "source", "nodes", "relations"}:
        raise MetadataError(
            "companion root requires exactly schema_version, source, nodes, and relations"
        )
    if type(value.get("schema_version")) is not int or value["schema_version"] != SCHEMA_VERSION:
        raise MetadataError("companion schema_version must be 1")
    source = value.get("source")
    if not isinstance(source, dict):
        raise MetadataError("companion source must be an object")
    if set(source) != {"path", "surface", "baseline_digest"}:
        raise MetadataError(
            "companion source requires path, surface, and baseline_digest"
        )
    if not isinstance(source.get("path"), str) or not source["path"]:
        raise MetadataError("companion source path must be a non-empty string")
    if not isinstance(source.get("surface"), str) or not source["surface"]:
        raise MetadataError("companion source surface must be a non-empty string")
    if source["surface"] != "companion_metadata":
        raise MetadataError("companion source surface must be companion_metadata")
    if not isinstance(value.get("nodes"), list):
        raise MetadataError("companion nodes must be an array")
    if not isinstance(value.get("relations"), list):
        raise MetadataError("companion relations must be an array")


def _validate_baseline(
    baseline: Any,
    companion_path: str,
    source_exists: Optional[bool],
    source_bytes: Optional[bytes],
) -> Optional[Diagnostic]:
    if baseline != "absent" and not re.fullmatch(
        r"sha256:[0-9a-f]{64}", str(baseline)
    ):
        raise MetadataError("baseline_digest must be lowercase sha256 or absent")
    if source_exists is None:
        raise MetadataError("source existence must be supplied for baseline validation")
    if source_exists:
        if source_bytes is None:
            raise MetadataError(
                "existing source raw bytes are required for baseline validation"
            )
        actual = "sha256:" + hashlib.sha256(source_bytes).hexdigest()
        if baseline != actual:
            return Diagnostic(
                "companion_baseline_mismatch",
                "companion baseline does not match existing source bytes",
                path=companion_path,
            )
    elif baseline != "absent":
        return Diagnostic(
            "companion_baseline_mismatch",
            "new source baseline must be the string absent",
            path=companion_path,
        )
    return None


def _parse_node(raw: Any, source_path: str) -> Node:
    if not isinstance(raw, dict):
        raise MetadataError("node must be an object")
    if set(raw) != {
        "id", "kind", "artifact_kind", "locator", "lifecycle", "provenance"
    }:
        raise MetadataError("node does not match canonical companion fields")
    if not isinstance(raw["id"], str) or not raw["id"]:
        raise MetadataError("node id must be a non-empty string")
    return Node(
        id=raw["id"],
        kind=NodeKind(raw["kind"]),
        artifact_kind=ArtifactKind(raw["artifact_kind"]),
        locator=_locator(raw["locator"], source_path),
        lifecycle=Lifecycle(raw["lifecycle"]),
        provenance=_provenance(raw["provenance"], source_path, relation=False),
    )


def _parse_relation(raw: Any, source_path: str) -> Relation:
    if not isinstance(raw, dict):
        raise MetadataError("relation must be an object")
    if set(raw) != {
        "source", "relation", "target", "evidence", "provenance", "lifecycle"
    }:
        raise MetadataError("relation does not match canonical companion fields")
    if not all(
        isinstance(raw[field], str) and raw[field]
        for field in ("source", "target")
    ):
        raise MetadataError("relation source and target must be non-empty strings")
    return Relation(
        source=raw["source"],
        relation=RelationType(raw["relation"]),
        target=raw["target"],
        evidence=Evidence(raw["evidence"]),
        provenance=_provenance(raw["provenance"], source_path, relation=True),
        lifecycle=Lifecycle(raw["lifecycle"]),
    )


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
    if any(
        item is not None and not isinstance(item, str)
        for item in value.values()
    ):
        raise MetadataError("locator fields must be strings or null")
    return Locator(
        path=path,
        heading=value.get("heading"),
        symbol=value.get("symbol"),
        test_name=value.get("test_name"),
        config_key=value.get("config_key"),
        schema_name=value.get("schema_name"),
    )


def _provenance(
    value: Any,
    default_path: str,
    *,
    relation: bool,
) -> Provenance:
    if not isinstance(value, dict):
        raise MetadataError("provenance must be an object")
    required = (
        {"surface", "locator", "attested_by"}
        if relation
        else {"produced_from", "governed_by"}
    )
    if set(value) != required:
        raise MetadataError(
            "%s provenance requires exactly: %s"
            % (
                "relation" if relation else "node",
                ", ".join(sorted(required)),
            )
        )
    if relation:
        if not isinstance(value["surface"], str) or not value["surface"]:
            raise MetadataError(
                "relation provenance surface must be a non-empty string"
            )
        if value["attested_by"] is not None and not isinstance(
            value["attested_by"], str
        ):
            raise MetadataError(
                "relation provenance attested_by must be a string or null"
            )
    else:
        for field in ("produced_from", "governed_by"):
            if not isinstance(value[field], list) or not all(
                isinstance(item, str) and item for item in value[field]
            ):
                raise MetadataError(
                    "node provenance %s must be an array of non-empty strings"
                    % field
                )
    locator = value.get("locator")
    return Provenance(
        produced_from=metadata_strings(value.get("produced_from")),
        governed_by=metadata_strings(value.get("governed_by")),
        surface=value.get("surface"),
        locator=_locator(locator, default_path) if locator is not None else None,
        attested_by=value.get("attested_by"),
    )
