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
