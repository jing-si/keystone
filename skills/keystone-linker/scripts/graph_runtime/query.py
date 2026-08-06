"""Pure queries over immutable index generations."""

from typing import Optional, Tuple

from .index_model import IndexResult, OwnerRecord, RefRecord


def owner_for(result: IndexResult, owner_id: str) -> Optional[OwnerRecord]:
    return next((owner for owner in result.owners if owner.id == owner_id), None)


def refs_to(result: IndexResult, target_id: str) -> Tuple[RefRecord, ...]:
    return tuple(ref for ref in result.refs if ref.target_id == target_id)
