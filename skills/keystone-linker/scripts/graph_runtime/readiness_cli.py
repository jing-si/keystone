#!/usr/bin/env python3
"""Deterministic JSON wrapper for internal owner/ref context readiness."""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from .readiness import context_readiness


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request-json", required=True,
                        help="JSON object, '-' for stdin, or @path for a JSON file")
    parser.add_argument("--response-json", default="-",
                        help="'-' for stdout or a response file path")
    return parser


def _read_request(value):
    if value == "-":
        raw = sys.stdin.read()
    elif value.startswith("@"):
        raw = Path(value[1:]).read_text(encoding="utf-8")
    else:
        raw = value
    request = json.loads(raw)
    allowed = {
        "repository_root", "cache_path", "initiator", "artifact_context",
        "include_typed_graph", "trace", "document_root", "includes", "excludes",
    }
    if not isinstance(request, dict) or set(request) - allowed:
        raise ValueError("request must be an object containing only supported fields")
    if not isinstance(request.get("repository_root"), str) or not request["repository_root"]:
        raise ValueError("repository_root is required")
    return request


def _default_cache(repository_root):
    root_digest = hashlib.sha256(str(Path(repository_root).resolve()).encode("utf-8")).hexdigest()
    codex_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return codex_root / "cache" / "keystone" / root_digest / "reference-index.sqlite3"


def _diagnostic(item):
    value = {"code": item.code, "message": item.message, "severity": item.severity}
    if item.path is not None:
        value["path"] = item.path
    return value


def _response(readiness):
    result = readiness.result
    freshness = result.freshness
    diagnostics = [_diagnostic(item) for item in result.diagnostics + readiness.diagnostics]
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    discovered_paths = tuple(freshness.discovered_paths)
    parsed_paths = tuple(item.path for item in freshness.entries)
    parsed_set = frozenset(parsed_paths)
    skipped_paths = tuple(path for path in discovered_paths if path not in parsed_set)
    skip_reasons = {
        item["path"]: item["code"]
        for item in diagnostics
        if item.get("path") in skipped_paths
        and item["code"] in {"scan_truncated", "source_too_large", "source_unreadable"}
    }
    path_digest = "sha256:" + hashlib.sha256(json.dumps(
        discovered_paths, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    payload = {
        "schema_version": 2,
        "status": "fail" if errors else "pass",
        "diagnostics": diagnostics,
        "summary": {"errors": errors, "warnings": warnings},
        "cache_status": readiness.cache_status,
        "scope": result.scope.value,
        "freshness_digest": freshness.digest,
        "complete": freshness.complete,
        "coverage": {
            "path_digest": path_digest,
            "discovered": len(discovered_paths),
            "parsed": len(parsed_paths),
            "skipped": len(skipped_paths),
            "skipped_sources": [
                {"path": path, "reason": skip_reasons.get(path, "scan_truncated")}
                for path in skipped_paths
            ],
        },
        "owners": [{"id": item.id, "path": item.path, "locator": item.locator}
                   for item in result.owners],
        "refs": [{"source_id": item.source_id, "target_id": item.target_id,
                  "path": item.path, "locator": item.locator} for item in result.refs],
        "typed_edges": (None if result.typed_graph is None else [
            {"source_id": item.source_id, "relation": item.relation,
             "target_id": item.target_id} for item in result.typed_graph.edges]),
        "dependency_evaluations": [{
            "gate_id": item.gate_id,
            "source": item.source_id,
            "dependency": item.dependency,
            "scope": {
                "steps": list(item.steps),
                "work_completion": item.work_completion,
            },
            "target_state": {
                "work_status": item.target_work_status,
                "approval_state": item.target_approval_state,
            },
            "result": item.status.value,
            "blocking": item.blocking,
            "optional": item.optional,
            "origin": item.origin,
            "reason": item.reason,
            "cycle_events": list(item.cycle_events),
        } for item in result.dependency_evaluations],
        "trace": [{"lane": item.lane, "operation": item.operation}
                  for item in readiness.trace.entries],
    }
    return payload


def main():
    args = _parser().parse_args()
    try:
        request = _read_request(args.request_json)
        repository_root = request.pop("repository_root")
        cache_path = request.pop("cache_path", None) or _default_cache(repository_root)
        result = context_readiness(repository_root, cache_path, **request)
        payload = _response(result)
        exit_code = 1 if payload["summary"]["errors"] else 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        payload = {
            "schema_version": 2, "status": "error",
            "diagnostics": [{"code": "readiness_execution_failed", "message": str(error),
                             "severity": "error"}],
            "summary": {"errors": 1, "warnings": 0},
        }
        exit_code = 2
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if args.response_json == "-":
        print(serialized)
    else:
        Path(args.response_json).write_text(serialized + "\n", encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
