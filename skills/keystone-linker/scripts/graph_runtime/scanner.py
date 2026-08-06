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
from .metadata import parse_reference_declaration, parse_source
from .yaml_subset import MetadataError


@dataclass(frozen=True)
class SourceSnapshot:
    relative: str
    raw_bytes: bytes


@dataclass(frozen=True)
class Discovery:
    scope: ScanScope
    sources: Tuple[SourceSnapshot, ...]
    freshness: FreshnessToken
    diagnostics: Tuple[IndexDiagnostic, ...] = ()


_IGNORED_DIRS = frozenset({
    ".git", ".worktrees", "__pycache__", "node_modules", ".venv", "venv", "dist",
    "build", ".gradle", "target", "vendor", "Pods", "DerivedData", "coverage", ".next", "out",
})
_TAXONOMY_REF_PREFIXES = (
    "key.topic.",
    "key.role.",
    "key.boundary.",
    "key.section.",
    "key.step.",
    "key.artifact.",
    "key.mode.",
)
_TAXONOMY_REF_IDS = frozenset({
    "key.contract.output",
    "key.contract.report",
    "key.doc.decision",
    "key.doc.decision-record",
    "key.doc.derived-agent",
    "key.doc.progress",
    "key.doc.source",
    "key.doc.standard",
    "key.doc.work",
    "key.doc.work-order",
    "key.output.artifact",
    "key.output.context-pack",
    "key.output.current-step-brief",
    "key.output.edit-plan",
    "key.output.worker-assignment-seed",
})
_COMPATIBILITY_NAVIGATION_REF_IDS = frozenset({"key.standard.artifact"})
_DOCS_EXTERNAL_OWNER_PREFIXES = ("key.skill.",)


class ReferenceScanner:
    def __init__(self, repository_root, *, document_root="00_docs",
                 includes: Sequence[str] = (), excludes: Sequence[str] = (),
                 max_file_bytes: int = 5 * 1024 * 1024,
                 max_total_bytes: int = 50 * 1024 * 1024,
                 max_files: int = 50000):
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
        self.max_file_bytes = max_file_bytes
        self.max_total_bytes = max_total_bytes
        self.max_files = max_files

    def discover(self, scope: ScanScope) -> Discovery:
        scope = ScanScope(scope)
        base = self._document_root_path if scope == ScanScope.DOCS else self.root
        paths = tuple(sorted(self._paths(base, scope), key=lambda item: item.as_posix()))
        discovered_paths = tuple(self._relative(path) for path in paths)
        sources = []
        diagnostics = []
        total_bytes = 0
        for path in paths:
            relative = self._relative(path)
            if len(sources) >= self.max_files:
                diagnostics.append(IndexDiagnostic(
                    "scan_truncated", "scan file budget was exceeded", relative, "warning"))
                break
            try:
                size = path.stat().st_size
            except OSError as error:
                diagnostics.append(IndexDiagnostic("source_unreadable", str(error), relative))
                continue
            if size > self.max_file_bytes:
                diagnostics.append(IndexDiagnostic(
                    "source_too_large", "source exceeds per-file scan budget", relative, "warning"))
                continue
            if total_bytes + size > self.max_total_bytes:
                diagnostics.append(IndexDiagnostic(
                    "scan_truncated", "scan byte budget was exceeded", relative, "warning"))
                break
            sources.append(SourceSnapshot(relative, path.read_bytes()))
            total_bytes += size
        sources = tuple(sources)
        entries = tuple(FreshnessEntry(source.relative, _digest(source.raw_bytes)) for source in sources)
        incomplete_codes = {"scan_truncated", "source_too_large", "source_unreadable"}
        complete = not any(item.code in incomplete_codes for item in diagnostics)
        identity = self._worktree_identity()
        body = {
            "worktree_identity": identity,
            "scope": scope.value,
            "entries": [(entry.path, entry.digest) for entry in entries],
            "discovered_paths": discovered_paths,
            "complete": complete,
        }
        token = FreshnessToken(
            identity, scope.value, entries,
            "sha256:" + hashlib.sha256(json.dumps(body, separators=(",", ":"),
                                                   sort_keys=True).encode("utf-8")).hexdigest(),
            discovered_paths,
            complete,
        )
        return Discovery(scope, sources, token, tuple(diagnostics))

    def scan(self, scope: ScanScope, *, include_typed_graph: bool = False) -> IndexResult:
        return self.scan_discovery(self.discover(scope), include_typed_graph=include_typed_graph)

    def scan_discovery(self, discovery: Discovery, *, include_typed_graph: bool = False) -> IndexResult:
        owners = []
        owner_counts = {}
        refs = []
        edges = []
        diagnostics = list(discovery.diagnostics)
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
                    locator = _owner_locator(node)
                    owner = OwnerRecord(node.id, node.locator.path, locator)
                    owner_counts[node.id] = owner_counts.get(node.id, 0) + 1
                    if owner_counts[node.id] > 1:
                        diagnostics.append(IndexDiagnostic(
                            "duplicate_owner", "owner ID is declared more than once: %s" % node.id,
                            relative))
                    owners.append(owner)
                    if not _has_machine_locator(node):
                        diagnostics.append(IndexDiagnostic(
                            "locator_gap", "owner has no machine-checkable locator: %s" % node.id,
                            relative, "warning"))
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
                locator = _owner_locator(node)
                owner = OwnerRecord(node.id, relative, locator)
                owner_counts[node.id] = owner_counts.get(node.id, 0) + 1
                if owner_counts[node.id] > 1:
                    diagnostics.append(IndexDiagnostic(
                        "duplicate_owner", "owner ID is declared more than once: %s" % node.id, relative))
                owners.append(owner)
                if not _has_machine_locator(node):
                    diagnostics.append(IndexDiagnostic(
                        "locator_gap", "owner has no machine-checkable locator: %s" % node.id,
                        relative, "warning"))
            for block, _construct, label in adapter.metadata_blocks(text):
                try:
                    declaration = parse_reference_declaration(block)
                    if declaration is None:
                        continue
                    source_id, targets = declaration
                    locator = label
                    if source_id in nodes_by_id:
                        locator = _owner_locator(nodes_by_id[source_id]) or label
                    for target in targets:
                        refs.append(RefRecord(source_id, target, relative, locator))
                except (MetadataError, TypeError, ValueError):
                    # The canonical parser already reports malformed metadata.
                    continue
            if include_typed_graph:
                edges.extend(TypedEdge(item.source, item.relation.value, item.target)
                             for item in parsed.snapshot.relations
                             if item.evidence.value == "declared")
        owner_ids = {owner.id for owner in owners}
        for ref in refs:
            if ref.target_id in owner_ids or _is_taxonomy_ref(ref.target_id):
                continue
            if (discovery.scope == ScanScope.DOCS
                    and ref.target_id.startswith(_DOCS_EXTERNAL_OWNER_PREFIXES)):
                diagnostics.append(IndexDiagnostic(
                    "out_of_scope_ref",
                    "ref target requires repository-scope owner resolution: %s" % ref.target_id,
                    ref.path,
                    "warning",
                ))
                continue
            diagnostics.append(IndexDiagnostic(
                "dangling_ref", "ref target has no owner: %s" % ref.target_id, ref.path))
        ordered_owners = tuple(sorted(owners, key=lambda item: (item.id, item.path, item.locator or "")))
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


def _owner_locator(node):
    locator = node.locator
    return (locator.heading or locator.symbol or locator.test_name or
            locator.config_key or locator.schema_name)


def _is_taxonomy_ref(target_id: str) -> bool:
    return (target_id in _TAXONOMY_REF_IDS
            or target_id in _COMPATIBILITY_NAVIGATION_REF_IDS
            or target_id.startswith(_TAXONOMY_REF_PREFIXES))


def _has_machine_locator(node) -> bool:
    locator = node.locator
    if node.kind.value == "source_document":
        return bool(locator.path)
    if node.artifact_kind.value == "skill_source":
        return bool(locator.path)
    if node.kind.value in {"document_section", "document_item", "claim", "decision",
                           "work_order", "work_step", "capability", "verification_result"}:
        return bool(locator.path and (locator.heading or locator.symbol))
    if node.artifact_kind.value == "test":
        return bool(locator.path and (locator.test_name or locator.symbol))
    if node.artifact_kind.value == "config":
        return bool(locator.path and (locator.config_key or locator.symbol))
    if node.artifact_kind.value == "schema":
        return bool(locator.path and (locator.schema_name or locator.symbol))
    return bool(locator.path and locator.symbol)
