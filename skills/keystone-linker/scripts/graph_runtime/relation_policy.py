"""Single executable policy for Artifact Graph relation semantics."""

from typing import Mapping


RELATION_POLICY = {
    "produces": {"forward_grade": "required", "reverse_grade": "strong_candidate", "direct_item_artifact": "forbidden"},
    "provides": {"forward_grade": "strong_candidate", "reverse_grade": "required", "direct_item_artifact": "forbidden"},
    "uses": {"forward_grade": "informational", "reverse_grade": "strong_candidate", "direct_item_artifact": "forbidden"},
    "implements": {"forward_grade": "informational", "reverse_grade": "required", "direct_item_artifact": "forbidden"},
    "requires_verification_of": {"forward_grade": "informational", "reverse_grade": "required", "direct_item_artifact": "allowed"},
    "verifies": {"forward_grade": "informational", "reverse_grade": "required", "direct_item_artifact": "forbidden"},
    "depends_on": {"forward_grade": "informational", "reverse_grade": "required", "direct_item_artifact": "forbidden"},
    "governed_by": {"forward_grade": "informational", "reverse_grade": "required", "direct_item_artifact": "forbidden"},
    "documents": {"forward_grade": "informational", "reverse_grade": "strong_candidate", "direct_item_artifact": "bounded"},
    "supersedes": {"forward_grade": "informational", "reverse_grade": "required", "direct_item_artifact": "forbidden"},
    "derived_from": {"forward_grade": "informational", "reverse_grade": "strong_candidate", "direct_item_artifact": "forbidden"},
}


RELATION_NAMES = tuple(RELATION_POLICY)


def policy_for(name: str) -> Mapping[str, str]:
    try:
        return RELATION_POLICY[name]
    except KeyError as error:
        raise ValueError("unknown relation policy: %s" % name) from error


def relation_direction_allowed(source_kind: str, source_artifact_kind: str,
                               relation: str, target_kind: str,
                               target_artifact_kind: str) -> bool:
    """Return whether a declared relation follows the canonical direction policy."""
    if relation not in RELATION_POLICY:
        return False
    if relation == "produces":
        return source_kind in {"source_document", "decision", "work_order"} and target_kind == "output_artifact"
    if relation == "provides":
        return (source_kind == "output_artifact" and source_artifact_kind in {"code", "config", "schema"}
                and target_kind == "capability")
    if relation == "uses":
        return (source_kind == "output_artifact" and (target_kind == "capability" or
                (target_kind == "output_artifact" and target_artifact_kind in {"api", "code"})))
    if relation == "implements":
        return (source_kind == "output_artifact" and source_artifact_kind in {"code", "config", "schema"}
                and (target_kind in {"claim", "decision"}
                     or (target_kind == "output_artifact" and target_artifact_kind == "api")))
    if relation == "requires_verification_of":
        return source_kind in {"document_item", "claim"} and (
            target_kind in {"capability", "decision", "claim"} or
            (target_kind == "output_artifact" and target_artifact_kind in {"api", "code"}))
    if relation == "verifies":
        return ((source_kind == "output_artifact" and source_artifact_kind == "test")
                or source_kind == "verification_result") and (
                    target_kind in {"capability", "decision", "claim"} or
                    (target_kind == "output_artifact" and target_artifact_kind in {"api", "code"}))
    if relation == "governed_by":
        governed_sources = {
            "source_document", "document_section", "document_item", "claim",
            "decision", "work_order", "work_step", "output_artifact",
        }
        return source_kind in governed_sources and target_kind in {"source_document", "decision"}
    if relation == "documents":
        return source_kind in {"source_document", "document_section", "document_item"} and target_kind == "output_artifact"
    if relation == "depends_on":
        admitted = {"source_document", "work_order", "work_step", "output_artifact"}
        return source_kind in admitted and target_kind in admitted
    if relation == "supersedes":
        return source_kind == target_kind
    if relation == "derived_from":
        return (source_kind == "output_artifact"
                and target_kind in {"output_artifact", "source_document", "document_section",
                                    "document_item", "claim", "decision", "work_order"})
    return False
