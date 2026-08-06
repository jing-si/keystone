"""Pure queries over immutable index generations."""

from typing import Tuple

from .index_model import IndexResult, OwnerLookupResult, RefRecord


def owner_for(result: IndexResult, owner_id: str) -> OwnerLookupResult:
    candidates = tuple(owner for owner in result.owners if owner.id == owner_id)
    status = "missing" if not candidates else "unique" if len(candidates) == 1 else "ambiguous"
    return OwnerLookupResult(status, candidates)


def refs_to(result: IndexResult, target_id: str) -> Tuple[RefRecord, ...]:
    return tuple(ref for ref in result.refs if ref.target_id == target_id)
