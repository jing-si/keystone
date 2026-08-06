"""Source-only discovery and reconstruction for the owner/ref index."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence, Tuple

from .adapters import adapter_for_path
from .index_model import (
    FreshnessEntry, FreshnessToken, IndexDiagnostic, IndexResult, OwnerRecord, ScanScope,
    RefRecord, TypedEdge, TypedGraph,
)
from .metadata import MetadataError, _metadata, _strings, parse_source


@dataclass(frozen=True)
class SourceSnapshot:
    relative: str
    raw_bytes: bytes


@dataclass(frozen=True)
class Discovery:
    scope: ScanScope
    sources: Tuple[SourceSnapshot, ...]
    freshness: FreshnessToken


_IGNORED_DIRS = frozenset({".git", ".worktrees", "__pycache__", "node_modules"})


class ReferenceScanner:
    def __init__(self, repository_root, *, document_root="00_docs",
                 includes: Sequence[str] = (), excludes: Sequence[str] = ()):
        self.root = Path(repository_root).resolve()
        declared_root = Path(document_root)
        if declared_root.is_absolute() or ".." in declared_root.parts:
            raise ValueError("document_root must be repository-relative and cannot escape root")
        resolved_document_root = (self.root / declared_root).resolve()
        try:
            resolved_document_root.relative_to(self.root)
        except ValueError as error:
            raise ValueError("document_root resolves outside repository") from error
        self.document_root = declared_root.as_posix()
        self._document_root_path = resolved_document_root
        self.includes = tuple(includes)
        self.excludes = tuple(excludes)

    def discover(self, scope: ScanScope) -> Discovery:
        scope = ScanScope(scope)
        base = self._document_root_path if scope == ScanScope.DOCS else self.root
        paths = tuple(sorted(self._paths(base, scope), key=lambda item: item.as_posix()))
        sources = tuple(SourceSnapshot(self._relative(path), path.read_bytes()) for path in paths)
        entries = tuple(FreshnessEntry(source.relative, _digest(source.raw_bytes)) for source in sources)
        identity = self._worktree_identity()
        body = {
            "worktree_identity": identity,
            "scope": scope.value,
            "entries": [(entry.path, entry.digest) for entry in entries],
        }
        token = FreshnessToken(
            identity, scope.value, entries,
            "sha256:" + hashlib.sha256(json.dumps(body, separators=(",", ":"),
                                                   sort_keys=True).encode("utf-8")).hexdigest(),
        )
        return Discovery(scope, sources, token)

    def scan(self, scope: ScanScope, *, include_typed_graph: bool = False) -> IndexResult:
        return self.scan_discovery(self.discover(scope), include_typed_graph=include_typed_graph)

    def scan_discovery(self, discovery: Discovery, *, include_typed_graph: bool = False) -> IndexResult:
        owners = {}
        refs = []
        edges = []
        diagnostics = []
        raw_by_path = {source.relative: source.raw_bytes for source in discovery.sources}
        for source in discovery.sources:
            relative = source.relative
            if relative.endswith(".keystone.json"):
                source_relative = relative[:-len(".keystone.json")]
                try:
                    companion_text = source.raw_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    diagnostics.append(IndexDiagnostic("unsupported_encoding", "companion is not UTF-8", relative))
                    continue
                parsed = parse_source(
                    "", source_relative, None, companion_text=companion_text,
                    companion_path=relative, companion_source_exists=source_relative in raw_by_path,
                    companion_source_bytes=raw_by_path.get(source_relative),
                )
                diagnostics.extend(IndexDiagnostic(item.code, item.message, item.path)
                                   for item in parsed.diagnostics)
                for node in parsed.snapshot.nodes:
                    locator = node.locator.heading or node.locator.symbol
                    owner = OwnerRecord(node.id, node.locator.path, locator)
                    if node.id in owners:
                        diagnostics.append(IndexDiagnostic(
                            "duplicate_owner", "owner ID is declared more than once: %s" % node.id,
                            relative))
                    else:
                        owners[node.id] = owner
                    if not _has_machine_locator(node.locator):
                        diagnostics.append(IndexDiagnostic(
                            "locator_gap", "owner has no machine-checkable locator: %s" % node.id,
                            relative))
                if include_typed_graph:
                    edges.extend(TypedEdge(item.source, item.relation.value, item.target)
                                 for item in parsed.snapshot.relations
                                 if item.evidence.value == "declared")
                continue
            adapter = adapter_for_path(relative)
            if adapter is None:
                continue
            try:
                text = source.raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                diagnostics.append(IndexDiagnostic("unsupported_encoding", "source is not UTF-8", relative))
                continue
            parsed = parse_source(text, relative, adapter)
            diagnostics.extend(IndexDiagnostic(item.code, item.message, item.path) for item in parsed.diagnostics)
            nodes_by_id = {node.id: node for node in parsed.snapshot.nodes}
            for node in parsed.snapshot.nodes:
                locator = node.locator.heading or node.locator.symbol
                owner = OwnerRecord(node.id, relative, locator)
                if node.id in owners:
                    diagnostics.append(IndexDiagnostic(
                        "duplicate_owner", "owner ID is declared more than once: %s" % node.id, relative))
                else:
                    owners[node.id] = owner
                if not _has_machine_locator(node.locator):
                    diagnostics.append(IndexDiagnostic(
                        "locator_gap", "owner has no machine-checkable locator: %s" % node.id,
                        relative))
            for block, _construct, label in adapter.metadata_blocks(text):
                try:
                    data = _metadata(block)
                    source_id = data.get("id")
                    if not isinstance(source_id, str) or not source_id:
                        continue
                    locator = label
                    if source_id in nodes_by_id:
                        locator = (nodes_by_id[source_id].locator.heading or
                                   nodes_by_id[source_id].locator.symbol or label)
                    for target in _strings(data.get("refs")):
                        refs.append(RefRecord(source_id, target, relative, locator))
                except (MetadataError, TypeError, ValueError):
                    # The canonical parser already reports malformed metadata.
                    continue
            if include_typed_graph:
                edges.extend(TypedEdge(item.source, item.relation.value, item.target)
                             for item in parsed.snapshot.relations
                             if item.evidence.value == "declared")
        owner_ids = set(owners)
        for ref in refs:
            if ref.target_id not in owner_ids:
                diagnostics.append(IndexDiagnostic(
                    "dangling_ref", "ref target has no owner: %s" % ref.target_id, ref.path))
        ordered_owners = tuple(sorted(owners.values(), key=lambda item: (item.id, item.path)))
        ordered_refs = tuple(sorted(set(refs), key=lambda item: (item.target_id, item.source_id, item.path)))
        ordered_diagnostics = tuple(sorted(diagnostics, key=lambda item: (item.code, item.path or "", item.message)))
        graph = (TypedGraph(tuple(sorted(set(edges), key=lambda item: (
            item.source_id, item.relation, item.target_id)))) if include_typed_graph else None)
        return IndexResult(discovery.scope, discovery.freshness, ordered_owners, ordered_refs,
                           ordered_diagnostics, graph)

    def _paths(self, base: Path, scope: ScanScope) -> Iterable[Path]:
        if not base.is_dir():
            return ()
        found = set()
        for path in base.rglob("*"):
            if path.is_symlink() or not path.is_file():
                continue
            relative = self._relative(path)
            if not self._admitted(relative):
                continue
            companion_source = None
            if relative.endswith(".keystone.json"):
                source_relative = relative[:-len(".keystone.json")]
                source = Path(str(path)[:-len(".keystone.json")])
                if source.is_file():
                    if source.is_symlink() or not self._admitted(source_relative):
                        continue
                    try:
                        source.resolve().relative_to(self.root)
                    except ValueError:
                        continue
                    companion_source = source
            if (scope == ScanScope.DOCS or adapter_for_path(relative) is not None or
                    relative.endswith(".keystone.json")):
                found.add(path)
                if companion_source is not None:
                    found.add(companion_source)
        return found

    def _admitted(self, relative: str) -> bool:
        parts = Path(relative).parts
        if any(part in _IGNORED_DIRS for part in parts):
            return False
        if self.excludes and any(Path(relative).match(pattern) for pattern in self.excludes):
            return False
        return not self.includes or any(Path(relative).match(pattern) for pattern in self.includes)

    def _relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def _worktree_identity(self) -> str:
        marker = self.root / ".git"
        marker_value = ""
        if marker.is_file():
            marker_value = marker.read_text(encoding="utf-8", errors="replace").strip()
        elif marker.is_dir():
            head = marker / "HEAD"
            marker_value = head.read_text(encoding="utf-8", errors="replace").strip() if head.exists() else ".git"
        value = "%s\0%s" % (self.root, marker_value)
        return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _has_machine_locator(locator) -> bool:
    return any((locator.heading, locator.symbol, locator.test_name,
                locator.config_key, locator.schema_name))
