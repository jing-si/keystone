"""Shared evidence and lifecycle admission policy for graph relations."""

from .model import (
    Evidence,
    Lifecycle,
    PatchOwner,
    PatchSurface,
    patch_owner_matches_surface,
)


RETIRED_LIFECYCLES = frozenset({
    Lifecycle.SUPERSEDED,
    Lifecycle.ARCHIVED,
    Lifecycle.DEPRECATED,
    Lifecycle.REMOVED,
})
EXCLUDED_IMPACT_LIFECYCLES = frozenset({
    Lifecycle.SUPERSEDED,
    Lifecycle.ARCHIVED,
    Lifecycle.REMOVED,
})
DOCUMENT_NODE_KINDS = frozenset({
    "source_document", "document_section", "document_item", "claim", "decision",
    "work_order", "work_step", "capability",
})
DOCUMENT_NODE_LIFECYCLES = frozenset({
    Lifecycle.DRAFT,
    Lifecycle.ACTIVE,
    Lifecycle.SUPERSEDED,
    Lifecycle.ARCHIVED,
})
ARTIFACT_NODE_LIFECYCLES = frozenset({
    Lifecycle.ACTIVE,
    Lifecycle.DEPRECATED,
    Lifecycle.REMOVED,
})
RELATION_LIFECYCLES = frozenset({
    Lifecycle.ACTIVE,
    Lifecycle.DEPRECATED,
    Lifecycle.ARCHIVED,
    Lifecycle.REMOVED,
})


def node_lifecycle_domain(node_kind) -> str:
    value = getattr(node_kind, "value", node_kind)
    return "document" if value in DOCUMENT_NODE_KINDS else "artifact"


def node_lifecycle_admitted(node_kind, lifecycle) -> bool:
    try:
        lifecycle = Lifecycle(lifecycle)
    except (TypeError, ValueError):
        return False
    admitted = (
        DOCUMENT_NODE_LIFECYCLES
        if node_lifecycle_domain(node_kind) == "document"
        else ARTIFACT_NODE_LIFECYCLES
    )
    return lifecycle in admitted


def relation_lifecycle_admitted(lifecycle) -> bool:
    try:
        return Lifecycle(lifecycle) in RELATION_LIFECYCLES
    except (TypeError, ValueError):
        return False


def relation_lifecycle_for_node(node_lifecycle: Lifecycle) -> Lifecycle:
    """Map a node lifecycle into the canonical relation lifecycle domain."""
    lifecycle = Lifecycle(node_lifecycle)
    if lifecycle in {Lifecycle.DRAFT, Lifecycle.ACTIVE}:
        return Lifecycle.ACTIVE
    if lifecycle in {Lifecycle.SUPERSEDED, Lifecycle.ARCHIVED}:
        return Lifecycle.ARCHIVED
    return lifecycle


def observed_evidence_attested(relation) -> bool:
    """Return whether observed relation evidence is bound to its owning surface."""
    if relation.evidence != Evidence.OBSERVED:
        return False
    provenance = relation.provenance
    try:
        owner = PatchOwner(provenance.attested_by)
        surface = PatchSurface(provenance.surface)
    except (TypeError, ValueError):
        return False
    return bool(
        provenance.locator is not None
        and patch_owner_matches_surface(owner, surface, provenance.locator.path)
    )


def replacement_evidence_admitted(relation) -> bool:
    return (
        relation.evidence == Evidence.DECLARED
        or observed_evidence_attested(relation)
    )
