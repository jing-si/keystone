"""Pure canonical-wire predicates and mutation closure reconstruction."""

import json
import re
from typing import Any, Sequence

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


def is_node_wire(value: Any) -> bool:
    required = {"id", "kind", "artifact_kind", "locator", "lifecycle", "provenance"}
    optional = {"declared_metadata", "effective_metadata", "parent_id"}
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
    return (
        metadata_valid
        and isinstance(value.get("id"), str)
        and bool(value["id"])
        and value.get("kind") in NODE_KINDS
        and value.get("artifact_kind") in ARTIFACT_KINDS
        and value.get("lifecycle") in {
            "draft", "active", "superseded", "archived", "deprecated", "removed",
        }
        and (value.get("parent_id") is None or isinstance(value.get("parent_id"), str))
        and is_locator_wire(value.get("locator"))
        and is_provenance_wire(value.get("provenance"))
    )


def is_relation_wire(value: Any) -> bool:
    required = {"source", "relation", "target", "evidence", "provenance", "lifecycle"}
    return (
        isinstance(value, dict)
        and set(value) == required
        and isinstance(value.get("source"), str)
        and bool(value["source"])
        and isinstance(value.get("target"), str)
        and bool(value["target"])
        and value.get("relation") in RELATION_NAMES
        and value.get("evidence") in {"declared", "observed"}
        and value.get("lifecycle") in {
            "draft", "active", "superseded", "archived", "deprecated", "removed",
        }
        and is_provenance_wire(value.get("provenance"))
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
    if value.get("schema_version") != 1 or value.get("status") not in {"pass", "fail"}:
        return False
    if not isinstance(diagnostics, list) or not isinstance(summary, dict):
        return False
    if not all(
        isinstance(item, dict)
        and isinstance(item.get("code"), str)
        and isinstance(item.get("message"), str)
        and item.get("severity") in {"info", "warning", "error"}
        for item in diagnostics
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
    if not isinstance(baseline, dict) or baseline.get("schema_version") != 1:
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
