"""Managed Work State adapter; never resolve current work from Progress projections."""

from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from .dependency import DependencyEvaluation, DependencyStatus
from .index_model import FreshnessEntry, FreshnessToken, IndexDiagnostic


def is_managed(root, document_root):
    path = Path(root) / document_root / "state/manifest.json"
    return path.exists() or path.is_symlink()


def bind_managed_result(root, document_root, result):
    """Bind dependency results to fresh state bytes, keeping graph scope unchanged."""
    if not is_managed(root, document_root):
        return result
    path = Path(__file__).resolve().parents[1] / "work_state_runtime.py"
    name = "keystone_linker_managed_runtime"
    spec = importlib.util.spec_from_file_location(name, path)
    runtime = importlib.util.module_from_spec(spec)
    sys.modules[name] = runtime
    spec.loader.exec_module(runtime)
    managed = runtime.evaluate_repository(root, document_root)
    diagnostics = list(result.diagnostics)
    diagnostics.extend(IndexDiagnostic(item["code"], item["message"], item.get("path"))
                       for item in managed.get("diagnostics", []))
    by_path = {item.path: item.digest for item in result.freshness.entries}
    coherent = True
    for source in managed.get("sources", []):
        path, digest = source["path"], source["digest"]
        if path in by_path and by_path[path] != digest:
            coherent = False
            diagnostics.append(IndexDiagnostic("state_source_changed",
                               "Graph and managed state captured different source bytes.", path))
        if digest is not None:
            by_path[path] = digest
    known = {owner.id for owner in result.owners}
    evaluations = []
    if managed.get("status") == "pass" and coherent:
        for item in managed["state"]["dependency_evaluations"]:
            if item["source_id"] not in known:
                continue
            evaluations.append(DependencyEvaluation(
                item["dependency"], DependencyStatus(item["result"]), item["blocking"],
                item["reason"], item["gate_id"], item["source_id"], tuple(item["steps"]),
                item["work_completion"], item["optional"], item["origin"],
                item["target_work_status"], item["target_approval_state"], tuple(item["cycle_events"])))
    entries = tuple(FreshnessEntry(path, digest) for path, digest in sorted(by_path.items()))
    original = result.freshness
    paths = tuple(sorted(set(original.discovered_paths) | set(by_path)))
    complete = original.complete and coherent and managed.get("status") == "pass"
    body = {"worktree_identity": original.worktree_identity, "scope": original.scope,
            "entries": [(item.path, item.digest) for item in entries],
            "discovered_paths": paths, "complete": complete}
    digest = "sha256:" + hashlib.sha256(json.dumps(body, separators=(",", ":"),
                                                 sort_keys=True).encode()).hexdigest()
    freshness = FreshnessToken(original.worktree_identity, original.scope, entries, digest,
                               paths, complete)
    views = replace(result.source_views, source_generation=digest) if result.source_views else None
    return replace(result, freshness=freshness, diagnostics=tuple(diagnostics),
                   dependency_evaluations=tuple(evaluations), source_views=views)
