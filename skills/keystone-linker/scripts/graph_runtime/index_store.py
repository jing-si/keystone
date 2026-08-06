"""Atomic, caller-located SQLite storage for disposable index generations."""

import json
import hashlib
import errno
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ImportError:  # Safe fallback: structural cache recovery stays fail-soft.
    fcntl = None

from .index_model import (
    FreshnessEntry, FreshnessToken, IndexDiagnostic, IndexResult, OwnerRecord,
    RefRecord, ScanScope, TypedEdge, TypedGraph,
)


class StoreUnavailable(RuntimeError):
    pass


class CacheCorrupt(StoreUnavailable):
    pass


class CacheBusy(StoreUnavailable):
    pass


CACHE_SCHEMA_VERSION = 3
MAX_GENERATIONS = 4


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
                    "SELECT schema_version, payload, payload_digest FROM generations "
                    "WHERE freshness_digest = ?", (freshness.digest,),
                ).fetchone()
        except sqlite3.Error as error:
            _raise_sqlite(error)
        except OSError as error:
            raise StoreUnavailable(str(error)) from error
        if not row:
            return None
        if row[0] != CACHE_SCHEMA_VERSION:
            raise CacheCorrupt("unsupported cache schema version")
        if not isinstance(row[1], str) or row[2] != _payload_digest(row[1]):
            raise CacheCorrupt("cache payload integrity check failed")
        try:
            return _decode(row[1], freshness)
        except (ValueError, KeyError, TypeError, IndexError) as error:
            raise CacheCorrupt(str(error)) from error

    def replace(self, result: IndexResult) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            _write_generation(self.path, result, timeout=self.timeout)
        except sqlite3.Error as error:
            _raise_sqlite(error)
        except OSError as error:
            raise StoreUnavailable(str(error)) from error

    def recover(self, result: IndexResult) -> None:
        """Atomically replace only a structurally unusable disposable cache."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with _target_recovery_lock(self.path):
            descriptor, temporary = tempfile.mkstemp(
                prefix=self.path.name + ".", suffix=".repair", dir=str(self.path.parent))
            os.close(descriptor)
            temporary_path = Path(temporary)
            try:
                _write_generation(temporary_path, result, timeout=self.timeout)
                os.replace(str(temporary_path), str(self.path))
            except sqlite3.Error as error:
                _raise_sqlite(error)
            except OSError as error:
                raise StoreUnavailable(str(error)) from error
            finally:
                _cleanup_repair_files(temporary_path)


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
        "diagnostics": [[item.code, item.message, item.path, item.severity]
                        for item in result.diagnostics],
        "typed_edges": (None if result.typed_graph is None else [
            [item.source_id, item.relation, item.target_id] for item in result.typed_graph.edges]),
    }
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _payload_digest(payload: str) -> str:
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _write_generation(path: Path, result: IndexResult, *, timeout: float) -> None:
    payload = _encode(result)
    with sqlite3.connect(str(path), timeout=timeout) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS generations "
            "(freshness_digest TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, "
            "payload TEXT NOT NULL, payload_digest TEXT NOT NULL, updated_at INTEGER NOT NULL)"
        )
        connection.execute(
            "INSERT OR REPLACE INTO generations "
            "(freshness_digest, schema_version, payload, payload_digest, updated_at) "
            "VALUES (?, ?, ?, ?, CAST(strftime('%s','now') AS INTEGER))",
            (result.freshness.digest, CACHE_SCHEMA_VERSION, payload, _payload_digest(payload)),
        )
        connection.execute(
            "DELETE FROM generations WHERE freshness_digest IN ("
            "SELECT freshness_digest FROM generations ORDER BY updated_at DESC, freshness_digest DESC "
            "LIMIT -1 OFFSET ?)",
            (MAX_GENERATIONS,),
        )
        connection.commit()


def _raise_sqlite(error: sqlite3.Error) -> None:
    message = str(error).lower()
    if "locked" in message or "busy" in message:
        raise CacheBusy(str(error)) from error
    raise CacheCorrupt(str(error)) from error


@contextmanager
def _target_recovery_lock(path: Path):
    if fcntl is None:
        raise StoreUnavailable("atomic cache recovery lock is unavailable on this platform")
    try:
        descriptor = os.open(str(path), os.O_RDWR)
    except OSError as error:
        raise StoreUnavailable(str(error)) from error
    try:
        try:
            fcntl.lockf(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise CacheBusy("cache is locked during recovery") from error
        except OSError as error:
            if error.errno in {errno.EACCES, errno.EAGAIN}:
                raise CacheBusy("cache is locked during recovery") from error
            raise StoreUnavailable(str(error)) from error
        yield
    finally:
        try:
            fcntl.lockf(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _cleanup_repair_files(path: Path) -> None:
    for candidate in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm"),
                      Path(str(path) + "-journal")):
        try:
            candidate.unlink()
        except FileNotFoundError:
            pass


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
