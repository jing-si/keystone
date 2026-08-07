"""Docs-first, fail-soft context readiness orchestration."""

from dataclasses import replace
from pathlib import Path

from .index_model import CallTrace, IndexDiagnostic, ReadinessResult
from .index_store import CacheBusy, CacheCorrupt, SQLiteIndexStore, StoreUnavailable
from .scanner import ReferenceScanner, ScanScope


# keystone: id=key.code.linker.context-readiness kind=output_artifact artifact_kind=code refs=key.standard.skill.linker.reference-index-readiness locator.symbol=context_readiness
def context_readiness(repository_root, cache_path, *, initiator, artifact_context=False,
                      include_typed_graph=False, trace=None, document_root="00_docs",
                      includes=(), excludes=()):
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
                               includes=includes, excludes=excludes)
    discovery = scanner.discover(scope)
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
