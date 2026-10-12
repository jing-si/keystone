"""Source-bound targeted preparation and explicit exact-owner lookup."""
from dataclasses import dataclass, replace
from pathlib import Path
import re
from typing import Mapping, Optional, Sequence, Tuple

from .index_model import IndexDiagnostic, ScanScope
from .model import RelationType
from .scanner import Discovery, ReferenceScanner


@dataclass(frozen=True)
class DiscoverySummary:
    mode: str
    coverage_kind: str
    complete: bool
    search_roots: Tuple[str, ...] = ()
    searched_files: int = 0
    searched_bytes: int = 0
    search_digest: Optional[str] = None


def bounded_discovery(scanner: ReferenceScanner, scope: ScanScope, *, mode: str,
                      anchors: Sequence[Mapping], source_paths: Sequence[str] = (),
                      owner_paths: Mapping[str, str] = None,
                      relation_types: Sequence[str] = (), follow_refs: bool = False,
                      max_depth: int = 1, lookup_roots: Sequence[str] = ()
                      ) -> Tuple[Discovery, DiscoverySummary, Tuple[IndexDiagnostic, ...]]:
    """Resolve only supplied locators; lookup is explicit and never builds a graph."""
    if mode not in {'targeted', 'lookup'}:
        raise ValueError('bounded mode must be targeted or lookup')
    if type(max_depth) is not int or not 0 <= max_depth <= 8:
        raise ValueError('max_depth must be between zero and eight')
    if set(relation_types) - {item.value for item in RelationType}:
        raise ValueError('unknown expansion relation type')
    for values, label in ((source_paths, "source_paths"), (lookup_roots, "lookup_roots"),
                          (relation_types, "relation_types")):
        if (not isinstance(values, (tuple, list))
                or any(not isinstance(value, str) or not value for value in values)):
            raise ValueError(label + " must be a list of non-empty strings")
    if not isinstance(anchors, (tuple, list)) or type(follow_refs) is not bool:
        raise ValueError("anchors must be a list and follow_refs a boolean")
    if owner_paths is not None and not isinstance(owner_paths, Mapping):
        raise ValueError("owner_paths must map IDs to relative paths")
    hints = dict(owner_paths or {})
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in hints.items()):
        raise ValueError('owner_paths must map IDs to relative paths')
    requested = set()
    expected = {}
    paths = set(source_paths)
    diagnostics = []
    for anchor in anchors:
        if (not isinstance(anchor, dict) or set(anchor) - {'id', 'path', 'digest'}
                or not isinstance(anchor.get('id'), str) or not anchor['id']):
            raise ValueError('anchor requires an ID and optional path and digest')
        if "path" in anchor and (not isinstance(anchor["path"], str) or not anchor["path"]):
            raise ValueError("anchor path must be a non-empty relative path")
        if "digest" in anchor and (not isinstance(anchor["digest"], str)
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", anchor["digest"])):
            raise ValueError("anchor digest must be a raw-byte SHA-256")
        owner_id = anchor['id']
        if owner_id in requested:
            raise ValueError("duplicate anchor ID: " + owner_id)
        requested.add(owner_id)
        if anchor.get('path'):
            hints[owner_id] = anchor['path']
            paths.add(anchor['path'])
        if anchor.get('digest'):
            expected[owner_id] = anchor['digest']
    if not anchors and not source_paths:
        diagnostics.append(IndexDiagnostic('anchor_required',
            'targeted discovery requires an anchor or explicit source paths', severity='warning'))
    for owner_id in requested:
        if owner_id in hints:
            paths.add(hints[owner_id])
    searched_files = searched_bytes = 0
    search_digest = None
    roots = tuple(sorted(set(lookup_roots)))
    if mode == 'lookup':
        if not roots or not requested:
            raise ValueError('lookup requires explicit search roots and exact owner IDs')
        candidates = set()
        for relative in roots:
            value = Path(relative)
            if value.is_absolute() or '..' in value.parts:
                raise ValueError('lookup root must be repository-relative')
            base = scanner.root / value
            base.resolve().relative_to(scanner.root)
            if any(part.is_symlink() for part in (base, *base.parents) if part != scanner.root):
                raise ValueError('lookup root must not traverse symlinks')
            if scope == ScanScope.DOCS:
                try:
                    base.relative_to(scanner.root / scanner.document_root)
                except ValueError as error:
                    raise ValueError('docs lookup root must be inside document_root') from error
            if not base.is_dir():
                diagnostics.append(IndexDiagnostic("lookup_root_unavailable",
                    "lookup root is missing or inaccessible", relative, "warning"))
            candidates.update(scanner.lookup_paths(base, scope))
        searched = scanner.discover_paths(scope, candidates)
        search_digest = searched.freshness.digest
        searched_files = len(searched.sources)
        searched_bytes = sum(len(source.raw_bytes) for source in searched.sources)
        diagnostics.extend(searched.diagnostics)
        # Cheap byte candidates are admitted by the canonical parser below.
        for source in searched.sources:
            if (any(owner_id.encode('utf-8') in source.raw_bytes for owner_id in requested)
                    or b'\\' in source.raw_bytes):
                paths.add(source.relative)
    result = None
    for depth in range(max_depth + 1):
        admitted = scanner.exact_paths(sorted(paths), scope)
        discovery = scanner.discover_paths(scope, admitted)
        discovery = replace(discovery, bounded=True)
        result = scanner.scan_discovery(discovery, include_typed_graph=mode != 'lookup')
        owners = {}
        for owner in result.owners:
            owners.setdefault(owner.id, []).append(owner)
        targets = set(requested)
        if mode != 'lookup':
            frontier = requested or set(owners)
            if follow_refs:
                targets.update(ref.target_id for ref in result.refs if ref.source_id in frontier)
            if result.typed_graph:
                targets.update(edge.target_id for edge in result.typed_graph.edges
                               if edge.source_id in frontier and edge.relation in relation_types)
        additions = {hints[target] for target in targets if target not in owners and target in hints}
        additions -= paths
        requested.update(targets)
        if not additions or depth == max_depth:
            break
        paths.update(additions)
    findings = list(diagnostics)
    for owner_id in sorted(requested):
        matches = owners.get(owner_id, [])
        if not matches:
            findings.append(IndexDiagnostic('owner_unresolved',
                'owner not resolved in bounded scope: ' + owner_id, hints.get(owner_id), 'warning'))
        elif len(matches) > 1:
            findings.append(IndexDiagnostic('owner_ambiguous',
                'multiple bounded owners: ' + owner_id, severity='error'))
        elif owner_id in hints and matches[0].path != hints[owner_id]:
            findings.append(IndexDiagnostic('stale_locator',
                'owner does not match supplied locator: ' + owner_id, hints[owner_id], 'warning'))
        if owner_id in expected:
            digests = {entry.path: entry.digest for entry in discovery.freshness.entries}
            if not matches or digests.get(matches[0].path) != expected[owner_id]:
                findings.append(IndexDiagnostic('stale_anchor',
                    'anchor digest differs from current source: ' + owner_id,
                    hints.get(owner_id), 'warning'))
    admitted_paths = set(discovery.freshness.discovered_paths)
    for path in sorted(paths - admitted_paths):
        if path + '.keystone.json' in admitted_paths:
            continue
        findings.append(IndexDiagnostic('bounded_source_unavailable',
            'explicit source was missing, excluded, or outside permitted scope', path, 'warning'))
    complete = discovery.freshness.complete and not findings
    if not complete:
        findings.append(IndexDiagnostic('bounded_coverage_incomplete',
            'bounded request contains unresolved or omitted evidence', severity='warning'))
    summary = DiscoverySummary(mode, 'bounded', complete, roots, searched_files,
                               searched_bytes, search_digest)
    return discovery, summary, tuple(findings)
