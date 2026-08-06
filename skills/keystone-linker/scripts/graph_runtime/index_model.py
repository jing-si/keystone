"""Immutable values used by the internal owner/ref index."""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class ScanScope(str, Enum):
    DOCS = "docs"
    REPOSITORY = "repository"


@dataclass(frozen=True)
class FreshnessEntry:
    path: str
    digest: str


@dataclass(frozen=True)
class FreshnessToken:
    worktree_identity: str
    scope: str
    entries: Tuple[FreshnessEntry, ...]
    digest: str
    discovered_paths: Tuple[str, ...] = ()
    complete: bool = True


@dataclass(frozen=True)
class OwnerRecord:
    id: str
    path: str
    locator: Optional[str] = None


@dataclass(frozen=True)
class OwnerLookupResult:
    status: str
    candidates: Tuple[OwnerRecord, ...] = ()

    @property
    def owner(self) -> Optional[OwnerRecord]:
        return self.candidates[0] if self.status == "unique" else None

    @property
    def path(self) -> Optional[str]:
        return self.owner.path if self.owner is not None else None


@dataclass(frozen=True)
class RefRecord:
    source_id: str
    target_id: str
    path: str
    locator: Optional[str] = None


@dataclass(frozen=True)
class TypedEdge:
    source_id: str
    relation: str
    target_id: str


@dataclass(frozen=True)
class TypedGraph:
    edges: Tuple[TypedEdge, ...] = ()


@dataclass(frozen=True)
class IndexDiagnostic:
    code: str
    message: str
    path: Optional[str] = None
    severity: str = "error"


@dataclass(frozen=True)
class IndexResult:
    scope: ScanScope
    freshness: FreshnessToken
    owners: Tuple[OwnerRecord, ...] = ()
    refs: Tuple[RefRecord, ...] = ()
    diagnostics: Tuple[IndexDiagnostic, ...] = ()
    typed_graph: Optional[TypedGraph] = None


@dataclass(frozen=True)
class ReadinessResult:
    result: IndexResult
    cache_status: str
    diagnostics: Tuple[IndexDiagnostic, ...] = ()
    trace: "CallTrace" = field(default_factory=lambda: CallTrace())


@dataclass(frozen=True)
class TraceEntry:
    lane: str
    operation: str


class RecursionBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class CallTrace:
    entries: Tuple[TraceEntry, ...] = ()

    def enter(self, lane: str, operation: str) -> "CallTrace":
        if lane not in {"reader", "linker"}:
            raise ValueError("trace lane must be reader or linker")
        if not isinstance(operation, str) or not operation:
            raise ValueError("trace operation must be a non-empty string")
        if lane in {entry.lane for entry in self.entries}:
            raise RecursionBlocked("recursion guard rejected re-entry into %s" % lane)
        return CallTrace(self.entries + (TraceEntry(lane, operation),))

    def to_json(self) -> str:
        return json.dumps(
            [{"lane": item.lane, "operation": item.operation} for item in self.entries],
            separators=(",", ":"), sort_keys=True,
        )

    @classmethod
    def from_json(cls, value: str) -> "CallTrace":
        raw = json.loads(value)
        if not isinstance(raw, list):
            raise ValueError("serialized trace must be an array")
        trace = cls()
        for item in raw:
            if not isinstance(item, dict) or set(item) != {"lane", "operation"}:
                raise ValueError("serialized trace entry is invalid")
            trace = trace.enter(item["lane"], item["operation"])
        return trace
