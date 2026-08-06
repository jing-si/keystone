"""Atomic, caller-located SQLite storage for disposable index generations."""

import json
import hashlib
import sqlite3
from pathlib import Path

from .index_model import (
    FreshnessEntry, FreshnessToken, IndexDiagnostic, IndexResult, OwnerRecord,
    RefRecord, ScanScope, TypedEdge, TypedGraph,
)


class StoreUnavailable(RuntimeError):
    pass


CACHE_SCHEMA_VERSION = 1


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
                    "SELECT schema_version, payload FROM generations WHERE freshness_digest = ?",
                    (freshness.digest,),
                ).fetchone()
            if row and row[0] != CACHE_SCHEMA_VERSION:
                raise StoreUnavailable("unsupported cache schema version")
            return _decode(row[1], freshness) if row else None
        except (sqlite3.Error, OSError, ValueError, KeyError, TypeError) as error:
            raise StoreUnavailable(str(error)) from error

    def replace(self, result: IndexResult) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(self.path), timeout=self.timeout) as connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS generations "
                    "(freshness_digest TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, "
                    "payload TEXT NOT NULL)"
                )
                connection.execute("DELETE FROM generations")
                connection.execute(
                    "INSERT INTO generations (freshness_digest, schema_version, payload) VALUES (?, ?, ?)",
                    (result.freshness.digest, CACHE_SCHEMA_VERSION, _encode(result)),
                )
                connection.commit()
        except (sqlite3.Error, OSError) as error:
            raise StoreUnavailable(str(error)) from error


def _encode(result: IndexResult) -> str:
    value = {
        "schema_version": CACHE_SCHEMA_VERSION,
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


def _decode(payload: str, expected: FreshnessToken) -> IndexResult:
    value = json.loads(payload)
    required = {"schema_version", "scope", "freshness", "owners", "refs", "diagnostics", "typed_edges"}
    if not isinstance(value, dict) or set(value) != required or value["schema_version"] != CACHE_SCHEMA_VERSION:
        raise ValueError("cache payload schema is invalid")
    freshness = value["freshness"]
    if not isinstance(freshness, dict) or set(freshness) != {
            "worktree_identity", "scope", "digest", "entries"}:
        raise ValueError("cache freshness payload is invalid")
    entries = tuple(FreshnessEntry(*item) for item in freshness["entries"])
    body = {"worktree_identity": freshness["worktree_identity"], "scope": freshness["scope"],
            "entries": [(item.path, item.digest) for item in entries]}
    recomputed = "sha256:" + hashlib.sha256(json.dumps(
        body, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
    decoded_token = FreshnessToken(
        freshness["worktree_identity"], freshness["scope"], entries, freshness["digest"])
    if recomputed != decoded_token.digest or decoded_token != expected or value["scope"] != expected.scope:
        raise ValueError("cache freshness does not match requested source generation")
    graph = value["typed_edges"]
    return IndexResult(
        ScanScope(value["scope"]),
        decoded_token,
        tuple(OwnerRecord(*item) for item in value["owners"]),
        tuple(RefRecord(*item) for item in value["refs"]),
        tuple(IndexDiagnostic(*item) for item in value["diagnostics"]),
        None if graph is None else TypedGraph(tuple(TypedEdge(*item) for item in graph)),
    )
