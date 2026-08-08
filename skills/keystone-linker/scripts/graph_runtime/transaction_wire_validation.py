"""Pure canonical-wire predicates and mutation closure reconstruction."""

import json
import re
from typing import Any, Sequence

from .lifecycle_policy import node_lifecycle_admitted, node_lifecycle_domain
from .model import RelationType


RELATION_NAMES = {item.value for item in RelationType}
NODE_KINDS = {
    "source_document",
    "document_section",
    "document_item",
    "claim",
    "decision",
    "work_order",
    "work_step",
    "capability",
    "output_artifact",
    "verification_result",
}
ARTIFACT_KINDS = {
    "skill_source",
    "code",
    "config",
    "schema",
    "api",
    "test",
    "generated_file",
    "doc_artifact",
    "none",
}
_DIGEST = re.compile(r"(?:absent|sha256:[0-9a-f]{64})\Z")


def is_digest_wire(value: Any) -> bool:
    return bool(_DIGEST.fullmatch(str(value)))


def normalized_wire(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalized_wire(item)
            for key, item in sorted(value.items())
            if item is not None
        }
    if isinstance(value, list):
        normalized = [normalized_wire(item) for item in value]
        if all(isinstance(item, dict) and "id" in item for item in normalized):
            return sorted(normalized, key=lambda item: item["id"])
        if all(
            isinstance(item, dict)
            and {"source", "relation", "target"} <= set(item)
            for item in normalized
        ):
            return sorted(
                normalized,
                key=lambda item: (item["source"], item["relation"], item["target"]),
            )
        return normalized
    return value


def is_locator_wire(value: Any) -> bool:
    allowed = {"path", "heading", "symbol", "test_name", "config_key", "schema_name"}
    return (
        isinstance(value, dict)
        and set(value) <= allowed
        and isinstance(value.get("path"), str)
        and bool(value["path"])
        and all(item is None or isinstance(item, str) for item in value.values())
    )


def is_provenance_wire(value: Any) -> bool:
    allowed = {"produced_from", "governed_by", "surface", "locator", "attested_by"}
    if not isinstance(value, dict) or not set(value) <= allowed:
        return False
    for field in ("produced_from", "governed_by"):
        items = value.get(field, [])
        if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
            return False
    return (
        value.get("surface") is None or isinstance(value.get("surface"), str)
    ) and (
        value.get("attested_by") is None
        or isinstance(value.get("attested_by"), str)
    ) and (
        value.get("locator") is None or is_locator_wire(value.get("locator"))
    )


def is_authority_wire(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(
            isinstance(item, list)
            and len(item) == 2
            and all(isinstance(part, str) for part in item)
            for item in value
        )
    )


def _metadata_wire_valid(value: Any, *, effective: bool) -> bool:
    metadata_fields = {
        "document_lifecycle", "approval_state", "governed_by", "source_authority",
    }
    lifecycle_values = {
        "draft", "active", "superseded", "archived", "deprecated", "removed",
    }
    if not effective:
        lifecycle_values = lifecycle_values | {None}
    return (
        isinstance(value, dict)
        and set(value) == metadata_fields
        and value.get("document_lifecycle") in lifecycle_values
        and value.get("approval_state") in {None, "pending", "accepted", "rejected"}
        and isinstance(value.get("governed_by"), list)
        and all(isinstance(item, str) for item in value["governed_by"])
        and is_authority_wire(value.get("source_authority"))
    )


def _artifact_metadata_wire_valid(value: Any) -> bool:
    if value.get("lifecycle_domain") != "artifact":
        return True
    provenance = value.get("provenance")
    governed_by = (
        provenance.get("governed_by") if isinstance(provenance, dict) else None
    )
    declared = value.get("declared_metadata")
    effective = value.get("effective_metadata")
    if declared is None and effective is None:
        return value.get("lifecycle") == "active" and governed_by == []
    if not isinstance(declared, dict) or not isinstance(effective, dict):
        return False
    expected_lifecycle = declared.get("document_lifecycle") or "active"
    expected_approval = declared.get("approval_state")
    expected_governed_by = declared.get("governed_by")
    expected_authority = declared.get("source_authority")
    return (
        value.get("lifecycle") == expected_lifecycle
        and effective.get("document_lifecycle") == expected_lifecycle
        and effective.get("approval_state") == expected_approval
        and effective.get("governed_by") == expected_governed_by
        and effective.get("source_authority") == expected_authority
        and governed_by == expected_governed_by
    )


def is_node_wire(value: Any, schema_version: int = 1) -> bool:
    required = {"id", "kind", "artifact_kind", "locator", "lifecycle", "provenance"}
    optional = {"declared_metadata", "effective_metadata", "parent_id"}
    if type(schema_version) is not int:
        return False
    if schema_version == 2:
        required.add("lifecycle_domain")
    elif schema_version != 1:
        return False
    if (
        not isinstance(value, dict)
        or not required <= set(value)
        or not set(value) <= required | optional
    ):
        return False
    if set(value) & optional and set(value) & optional != optional:
        return False
    declared = value.get("declared_metadata")
    effective = value.get("effective_metadata")
    metadata_valid = declared is None or _metadata_wire_valid(declared, effective=False)
    if effective is not None:
        metadata_valid = metadata_valid and _metadata_wire_valid(effective, effective=True)
    kind = value.get("kind")
    lifecycle = value.get("lifecycle")
    lifecycle_valid = lifecycle in {
        "draft", "active", "superseded", "archived", "deprecated", "removed",
    }
    if schema_version == 2:
        domain = value.get("lifecycle_domain")
        expected_domain = node_lifecycle_domain(kind)
        lifecycle_valid = (
            domain == expected_domain
            and node_lifecycle_admitted(kind, lifecycle)
        )
    return (
        metadata_valid
        and _artifact_metadata_wire_valid(value)
        and isinstance(value.get("id"), str)
        and bool(value["id"])
        and kind in NODE_KINDS
        and value.get("artifact_kind") in ARTIFACT_KINDS
        and lifecycle_valid
        and (value.get("parent_id") is None or isinstance(value.get("parent_id"), str))
        and is_locator_wire(value.get("locator"))
        and is_provenance_wire(value.get("provenance"))
    )


def is_relation_wire(value: Any, schema_version: int = 1,
                     allow_inferred: bool = False) -> bool:
    required = {"source", "relation", "target", "evidence", "provenance", "lifecycle"}
    if type(schema_version) is not int:
        return False
    if schema_version == 2:
        required.add("lifecycle_domain")
    elif schema_version != 1:
        return False
    return (
        isinstance(value, dict)
        and set(value) == required
        and isinstance(value.get("source"), str)
        and bool(value["source"])
        and isinstance(value.get("target"), str)
        and bool(value["target"])
        and value.get("relation") in RELATION_NAMES
        and value.get("evidence") in (
            {"declared", "observed", "inferred"}
            if allow_inferred else {"declared", "observed"}
        )
        and value.get("lifecycle") in (
            {"active", "deprecated", "archived", "removed"}
            if schema_version == 2 else
            {"draft", "active", "superseded", "archived", "deprecated", "removed"}
        )
        and (schema_version == 1 or value.get("lifecycle_domain") == "relation")
        and is_provenance_wire(value.get("provenance"))
    )


def is_snapshot_wire(value: Any, schema_version: int,
                     allow_inferred: bool = True) -> bool:
    return (
        type(schema_version) is int
        and schema_version in {1, 2}
        and isinstance(value, dict)
        and set(value) == {"schema_version", "nodes", "relations"}
        and type(value.get("schema_version")) is int
        and value.get("schema_version") == schema_version
        and isinstance(value.get("nodes"), list)
        and all(is_node_wire(node, schema_version) for node in value["nodes"])
        and isinstance(value.get("relations"), list)
        and all(is_relation_wire(
            relation, schema_version, allow_inferred=allow_inferred
        ) for relation in value["relations"])
    )


def entity_identity(entity: str, value: Any):
    if not isinstance(value, dict):
        return None
    if entity == "node":
        return value.get("id")
    return value.get("source"), value.get("relation"), value.get("target")


def is_mechanical_envelope(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {
        "schema_version", "status", "diagnostics", "summary",
    }:
        return False
    diagnostics, summary = value.get("diagnostics"), value.get("summary")
    if (type(value.get("schema_version")) is not int
            or value.get("schema_version") != 1
            or value.get("status") not in {"pass", "fail"}):
        return False
    if not isinstance(diagnostics, list) or not isinstance(summary, dict):
        return False
    diagnostic_required = {"code", "message", "severity"}
    diagnostic_optional = {"path", "locator"}
    if not all(
        isinstance(item, dict)
        and diagnostic_required <= set(item)
        and set(item) <= diagnostic_required | diagnostic_optional
        and isinstance(item.get("code"), str)
        and isinstance(item.get("message"), str)
        and item.get("severity") in {"info", "warning", "error"}
        and (
            item.get("path") is None
            or isinstance(item.get("path"), str)
        )
        and (
            item.get("locator") is None
            or is_locator_wire(item.get("locator"))
        )
        for item in diagnostics
    ):
        return False
    if (
        set(summary) != {"errors", "warnings"}
        or type(summary.get("errors")) is not int
        or type(summary.get("warnings")) is not int
        or summary["errors"] < 0
        or summary["warnings"] < 0
    ):
        return False
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    expected_status = "fail" if errors else "pass"
    return (
        value["status"] == expected_status
        and summary == {"errors": errors, "warnings": warnings}
    )


def mechanical_envelope_passes(value: Any) -> bool:
    return is_mechanical_envelope(value) and value["status"] == "pass"


def apply_mutation_delta(baseline: Any, mutations: Sequence[Any]):
    if (not isinstance(baseline, dict)
            or type(baseline.get("schema_version")) is not int
            or baseline.get("schema_version") not in {1, 2}):
        return None
    if (
        not isinstance(baseline.get("nodes"), list)
        or not isinstance(baseline.get("relations"), list)
    ):
        return None
    current = json.loads(json.dumps(baseline))
    for mutation in mutations:
        if (
            not isinstance(mutation, dict)
            or mutation.get("entity") not in {"node", "relation"}
        ):
            return None
        collection = current[
            "nodes" if mutation["entity"] == "node" else "relations"
        ]
        before = mutation.get("before")
        after = mutation.get("after")
        operation = mutation.get("operation")
        normalized = [normalized_wire(item) for item in collection]
        if operation == "add":
            identity = entity_identity(mutation["entity"], after)
            if any(
                entity_identity(mutation["entity"], item) == identity
                for item in collection
            ):
                return None
            collection.append(after)
        elif operation in {"update", "remove"}:
            matches = [
                index for index, item in enumerate(normalized)
                if item == normalized_wire(before)
            ]
            if len(matches) != 1:
                return None
            collection.pop(matches[0])
            if operation == "update":
                after_identity = entity_identity(mutation["entity"], after)
                if any(
                    entity_identity(mutation["entity"], item) == after_identity
                    for item in collection
                ):
                    return None
                collection.append(after)
        else:
            return None
    return current


def migrate_snapshot_wire_v1_to_v2(value: Any):
    """Deterministically migrate an accepted v1 snapshot wire to canonical v2."""
    if not is_snapshot_wire(value, 1, allow_inferred=True):
        raise ValueError("snapshot does not match the permissive v1 wire")
    migrated = json.loads(json.dumps(value))
    migrated["schema_version"] = 2
    for node in migrated["nodes"]:
        node["lifecycle_domain"] = node_lifecycle_domain(node["kind"])
    for relation in migrated["relations"]:
        relation["lifecycle_domain"] = "relation"
    if not is_snapshot_wire(migrated, 2, allow_inferred=True):
        raise ValueError("v1 lifecycle vocabulary cannot migrate to canonical v2")
    return normalized_wire(migrated)
