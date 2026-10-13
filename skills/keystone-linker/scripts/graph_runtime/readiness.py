"""Docs-first, fail-soft context readiness orchestration."""

from dataclasses import replace
from pathlib import Path

from .bounded_discovery import DiscoverySummary, bounded_discovery
from .index_model import CallTrace, IndexDiagnostic, ReadinessResult
from .index_store import CacheBusy, CacheCorrupt, SQLiteIndexStore, StoreUnavailable
from .scanner import ReferenceScanner, ScanScope
from .managed_state import is_managed


# keystone: id=key.code.linker.context-readiness kind=output_artifact artifact_kind=code refs=key.standard.skill.linker.reference-index-readiness locator.symbol=context_readiness
def context_readiness(repository_root, cache_path, *, initiator, artifact_context=False,
                      include_typed_graph=False, include_source_views=False, trace=None,
                      document_root="00_docs", includes=(), excludes=(), discovery_mode=None,
                      anchors=(), source_paths=(), owner_paths=None, relation_types=(),
                      follow_refs=False, max_depth=1, lookup_roots=(),
                      max_files=128, max_total_bytes=50 * 1024 * 1024):
    if discovery_mode is None and (anchors or source_paths or lookup_roots):
        discovery_mode = "targeted"
    if initiator not in {"reader", "linker"}:
        raise ValueError("initiator must be reader or linker")
    current = trace if isinstance(trace, CallTrace) else CallTrace.from_json(trace) if trace else CallTrace()
    if not current.entries:
        current = current.enter(initiator, "context_readiness")
    elif current.entries[-1].lane != initiator:
        current = current.enter(initiator, "context_readiness")
    if initiator == "reader":
        current = current.enter("linker", "index_readiness")
    scope = ScanScope.REPOSITORY if artifact_context else ScanScope.DOCS
    materialize_graph = include_typed_graph and scope == ScanScope.REPOSITORY
    scanner = ReferenceScanner(repository_root, document_root=document_root,
                               includes=includes, excludes=excludes,
                               anchored_includes=discovery_mode is not None)
    if discovery_mode not in {None, "targeted", "lookup", "audit"}:
        raise ValueError("unknown discovery_mode")
    if discovery_mode in {"targeted", "lookup"}:
        if (type(max_files) is not int or not 1 <= max_files <= 50000
                or type(max_total_bytes) is not int
                or not 1 <= max_total_bytes <= 50 * 1024 * 1024):
            raise ValueError("invalid bounded file or byte budget")
        scanner.max_files = max_files
        scanner.max_total_bytes = max_total_bytes
        discovery, summary, findings = bounded_discovery(
            scanner, scope, mode=discovery_mode, anchors=anchors, source_paths=source_paths,
            owner_paths=owner_paths, relation_types=relation_types, follow_refs=follow_refs,
            max_depth=max_depth, lookup_roots=lookup_roots)
        result = scanner.scan_discovery(
            discovery, include_typed_graph=materialize_graph and discovery_mode != "lookup",
            include_source_views=include_source_views and discovery_mode != "lookup")
        if discovery_mode == "lookup":
            requested_ids = {anchor["id"] for anchor in anchors}
            result = replace(result, owners=tuple(owner for owner in result.owners
                                                 if owner.id in requested_ids), refs=())
        complete = summary.complete and not any(
            item.code in {"owner_unresolved", "out_of_scope_ref"} or item.severity == "error"
            for item in result.diagnostics)
        if not complete and not any(d.code == "bounded_coverage_incomplete" for d in findings):
            findings += (IndexDiagnostic("bounded_coverage_incomplete",
                "bounded request contains unresolved or omitted evidence", severity="warning"),)
        return ReadinessResult(result, "bounded_source", findings, current,
                               replace(summary, complete=complete))
    discovery = scanner.discover(scope)
    readiness = _cached_readiness(scanner, discovery, cache_path, repository_root,
                                 materialize_graph, include_source_views, current)
    if discovery_mode == "audit":
        return replace(readiness, discovery=DiscoverySummary(
            "audit", "scope", discovery.freshness.complete))
    return readiness


def _cached_readiness(scanner, discovery, cache_path, repository_root,
                      materialize_graph, include_source_views, current):
    if is_managed(scanner.root, scanner.document_root):
        result = scanner.scan_discovery(discovery, include_typed_graph=materialize_graph,
                                        include_source_views=include_source_views)
        return ReadinessResult(result, "managed_source", (), current)
    if include_source_views:
        result = scanner.scan_discovery(
            discovery,
            include_typed_graph=materialize_graph,
            include_source_views=True,
        )
        cache_status = (
            "source_projection" if discovery.freshness.complete
            else "source_fallback"
        )
        return ReadinessResult(result, cache_status, (), current)
    store = SQLiteIndexStore(cache_path, repository_root=repository_root)
    cache_diagnostics = []
    if not discovery.freshness.complete:
        result = scanner.scan_discovery(discovery, include_typed_graph=materialize_graph)
        cache_diagnostics.append(IndexDiagnostic(
            "cache_bypassed_incomplete_discovery",
            "incomplete discovery generation is not cacheable",
            str(Path(cache_path)),
            "warning",
        ))
        return ReadinessResult(result, "source_fallback", tuple(cache_diagnostics), current)
    try:
        loaded = store.load(discovery.freshness)
        if loaded is not None and (not materialize_graph or loaded.typed_graph is not None):
            if not materialize_graph and loaded.typed_graph is not None:
                loaded = replace(loaded, typed_graph=None)
            return ReadinessResult(loaded, "reused", (), current)
    except CacheCorrupt as error:
        cache_diagnostics.append(IndexDiagnostic("cache_unavailable", str(error), str(Path(cache_path))))
        result = scanner.scan_discovery(discovery, include_typed_graph=materialize_graph)
        try:
            store.recover(result)
            cache_diagnostics.append(IndexDiagnostic(
                "cache_recovered", "structurally invalid disposable cache was replaced",
                str(Path(cache_path))))
        except StoreUnavailable as recovery_error:
            cache_diagnostics.append(IndexDiagnostic(
                "cache_recovery_failed", str(recovery_error), str(Path(cache_path))))
        return ReadinessResult(result, "source_fallback", tuple(cache_diagnostics), current)
    except (CacheBusy, StoreUnavailable) as error:
        cache_diagnostics.append(IndexDiagnostic("cache_unavailable", str(error), str(Path(cache_path))))
        result = scanner.scan_discovery(discovery, include_typed_graph=materialize_graph)
        return ReadinessResult(result, "source_fallback", tuple(cache_diagnostics), current)
    result = scanner.scan_discovery(discovery, include_typed_graph=materialize_graph)
    try:
        store.replace(result)
        return ReadinessResult(result, "refreshed", (), current)
    except CacheCorrupt as error:
        cache_diagnostics.append(IndexDiagnostic("cache_unavailable", str(error), str(Path(cache_path))))
        try:
            store.recover(result)
            cache_diagnostics.append(IndexDiagnostic(
                "cache_recovered", "structurally invalid disposable cache was replaced",
                str(Path(cache_path))))
        except StoreUnavailable as recovery_error:
            cache_diagnostics.append(IndexDiagnostic(
                "cache_recovery_failed", str(recovery_error), str(Path(cache_path))))
        return ReadinessResult(result, "source_fallback", tuple(cache_diagnostics), current)
    except StoreUnavailable as error:
        cache_diagnostics.append(IndexDiagnostic("cache_unavailable", str(error), str(Path(cache_path))))
        return ReadinessResult(result, "source_fallback", tuple(cache_diagnostics), current)
