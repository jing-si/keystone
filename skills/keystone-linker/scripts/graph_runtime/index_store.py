"""Atomic, caller-located SQLite storage for disposable index generations."""

import json
import sqlite3
from pathlib import Path

from .index_model import (
    FreshnessEntry, FreshnessToken, IndexDiagnostic, IndexResult, OwnerRecord,
    RefRecord, ScanScope, TypedEdge, TypedGraph,
)


class StoreUnavailable(RuntimeError):
    pass


class SQLiteIndexStore:
    def __init__(self, cache_path, *, repository_root, timeout=0.1):
        self.path = Path(cache_path).resolve()
        root = Path(repository_root).resolve()
        if self.path == root or root in self.path.parents:
            raise ValueError("reference index cache must be outside the repository")
        self.timeout = timeout

    def load(self, freshness: FreshnessToken):
        if not self.path.exists():
            return None
        try:
            with sqlite3.connect(str(self.path), timeout=self.timeout) as connection:
                row = connection.execute(
                    "SELECT payload FROM generations WHERE freshness_digest = ?",
                    (freshness.digest,),
                ).fetchone()
            return _decode(row[0]) if row else None
        except (sqlite3.Error, OSError, ValueError, KeyError, TypeError) as error:
            raise StoreUnavailable(str(error)) from error

    def replace(self, result: IndexResult) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(self.path), timeout=self.timeout) as connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS generations "
                    "(freshness_digest TEXT PRIMARY KEY, payload TEXT NOT NULL)"
                )
                connection.execute("DELETE FROM generations")
                connection.execute(
                    "INSERT INTO generations (freshness_digest, payload) VALUES (?, ?)",
                    (result.freshness.digest, _encode(result)),
                )
                connection.commit()
        except (sqlite3.Error, OSError) as error:
            raise StoreUnavailable(str(error)) from error


def _encode(result: IndexResult) -> str:
    value = {
        "scope": result.scope.value,
        "freshness": {
            "worktree_identity": result.freshness.worktree_identity,
            "scope": result.freshness.scope,
            "digest": result.freshness.digest,
            "entries": [[item.path, item.digest] for item in result.freshness.entries],
        },
        "owners": [[item.id, item.path, item.locator] for item in result.owners],
        "refs": [[item.source_id, item.target_id, item.path, item.locator] for item in result.refs],
        "diagnostics": [[item.code, item.message, item.path] for item in result.diagnostics],
        "typed_edges": (None if result.typed_graph is None else [
            [item.source_id, item.relation, item.target_id] for item in result.typed_graph.edges]),
    }
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _decode(payload: str) -> IndexResult:
    value = json.loads(payload)
    freshness = value["freshness"]
    graph = value["typed_edges"]
    return IndexResult(
        ScanScope(value["scope"]),
        FreshnessToken(
            freshness["worktree_identity"], freshness["scope"],
            tuple(FreshnessEntry(*item) for item in freshness["entries"]), freshness["digest"],
        ),
        tuple(OwnerRecord(*item) for item in value["owners"]),
        tuple(RefRecord(*item) for item in value["refs"]),
        tuple(IndexDiagnostic(*item) for item in value["diagnostics"]),
        None if graph is None else TypedGraph(tuple(TypedEdge(*item) for item in graph)),
    )
