"""Bounded execution recovery over managed state and exact dependency history."""

from dataclasses import asdict
import importlib.util
from pathlib import Path
import re
import sys
from typing import Any, Callable, Dict, Mapping


def _sibling(name: str):
    key = "keystone_packaged_" + name + "_" + str(Path(__file__).parent)
    spec = importlib.util.spec_from_file_location(key, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


state = _sibling("managed_work_state")
policy = _sibling("work_dependency_policy")


def managed_enabled(root: Path, document_root: str = "00_docs") -> bool:
    """Presence selects managed mode, including corrupt markers (never legacy fallback)."""
    path = Path(root) / document_root / "state/manifest.json"
    return path.exists() or path.is_symlink()


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise state.StateError("state_plan_invalid", label + " must be a mapping.")
    return value


def _plan_steps(text: str, round_ref: str):
    pattern = re.compile(r"^ {0,3}#{1,6}\s+`?(" + re.escape(round_ref)
                         + r"/S[0-9]{2,}(?:-[A-Z]+)?)`?(?:\s|$)")
    result = []
    fence_char, fence_length = "", 0
    for line in text.splitlines():
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            token, tail = fence.groups()
            if not fence_char:
                fence_char, fence_length = token[0], len(token)
            elif token[0] == fence_char and len(token) >= fence_length and not tail.strip():
                fence_char, fence_length = "", 0
            continue
        match = pattern.match(line) if not fence_char else None
        if match:
            result.append(match.group(1))
    return tuple(dict.fromkeys(result))


def execution_projection(root: Path, document_root: str,
                         parse_frontmatter: Callable) -> Dict[str, Any]:
    """Read open plans and referenced history only; return gates and per-Work selection."""
    store = state.StateStore(root, document_root)
    marker_path = store.state_path + "/manifest.json"
    marker = store.read(marker_path)
    if marker is not None:
        value = state.decode(marker)
        if (not isinstance(value, dict) or type(value.get("schema_version")) is not int
                or value != {"schema_version": 1, "mode": "managed"}):
            raise state.StateError("state_manifest_invalid", "Invalid managed-state activation marker.")
    initial = store.current()
    result = state.work_state_projection(store, current=initial)
    captured = {path: store.read(path) for path in initial["sources"]}
    captured[marker_path] = marker
    by_ref = {item["ref"]: item for item in initial["items"]}
    plans, targets, steps, gates, declared, locators = {}, {}, {}, [], {}, {}
    findings = []

    def capture(path):
        if not path.startswith(document_root + "/works/") or not path.endswith(".md"):
            raise state.StateError("state_order_path_invalid", "Expected a work-order locator.")
        if path not in captured:
            captured[path] = store.read(path)
        raw = captured[path]
        if raw is None:
            raise state.StateError("state_order_missing", "Missing work order: " + path)
        try:
            text = raw.decode("utf-8")
            metadata = parse_frontmatter(text)
        except (ValueError, UnicodeError) as error:
            raise state.StateError("state_plan_invalid", str(error)) from error
        return text, metadata

    for item in initial["items"]:
        capture(item["order_path"])
        history = state.events(captured[item["order_path"]], item["ref"])
        if not history or history[-1]["event"] == "closed":
            raise state.StateError("state_history_conflict", "Open item lacks a creation/reopen event: " + item["ref"])
        if "result" in history[-1] and history[-1]["result"] != item:
            raise state.StateError("state_history_conflict", "Current state differs from its last event: " + item["ref"])
        direct_round = (item["kind"] == "round" and any(
            entry["kind"] == "step" and entry["parent"] == item["ref"] for entry in initial["items"]))
        if item["kind"] == "round" and not any(
                entry["kind"] == "work" and entry["parent"] == item["ref"] for entry in initial["items"]):
            _text, round_metadata = capture(item["order_path"])
            direct_round = direct_round or (round_metadata.get("doc_type") == "work_order"
                and "defined_steps" in _mapping(round_metadata.get("key", {}), "key"))
        if item["kind"] != "work" and not direct_round:
            continue
        text, metadata = capture(item["order_path"])
        key = _mapping(metadata.get("key", {}), "key")
        identity = key.get("id")
        if not isinstance(identity, str) or not identity or identity in plans:
            raise state.StateError("state_work_id_invalid", "Each open Work needs a unique key.id.")
        if metadata.get("doc_type") != "work_order":
            raise state.StateError("state_plan_invalid", "Work locator must identify a work_order.")
        plans[identity] = item
        targets[identity] = policy.DependencyTargetState(item["execution"], item["approval"])
        round_ref = item["ref"].split("/")[0]
        headings = _plan_steps(text, round_ref)
        defined = key.get("defined_steps")
        if defined is not None:
            if (not isinstance(defined, list) or any(not isinstance(step, str)
                    or not state.STEP.fullmatch(step) for step in defined)
                    or len(set(defined)) != len(defined)):
                raise state.StateError("state_plan_invalid", "Invalid key.defined_steps.")
            headings = tuple(dict.fromkeys(headings + tuple(round_ref + "/" + step for step in defined)))
        refs = {entry["ref"] for entry in initial["items"] if entry["parent"] == item["ref"]}
        refs.update(headings)
        for ref in headings:
            if ref not in by_ref:
                inspected = store.inspect(ref, item["order_path"])
                if inspected["status"] != "closed":
                    raise state.StateError("state_step_missing", "Planned Step is neither managed nor closed: " + ref)
        steps[identity] = tuple(sorted(ref.split("/")[1] for ref in refs))
        if not refs:
            raise state.StateError("state_steps_missing", "Work requires at least one Step: " + identity)
        relations = _mapping(key.get("relations", {}), "key.relations")
        dependencies = relations.get("depends_on", [])
        if not isinstance(dependencies, list) or any(not isinstance(dep, str) for dep in dependencies):
            raise state.StateError("state_plan_invalid", "depends_on must contain stable IDs.")
        declared[identity] = dependencies
        parsed, diagnostics = policy.parse_work_gates(metadata.get("work_gates"), dependencies, identity)
        gates.extend(parsed)
        findings.extend({"severity": "error", "code": code, "message": message,
                         "path": item["order_path"]} for code, message in diagnostics)
        for dependency, locator in _mapping(metadata.get("work_state_targets", {}),
                                             "work_state_targets").items():
            if (not isinstance(locator, dict) or set(locator) != {"ref", "order_path"}
                    or not isinstance(dependency, str)):
                raise state.StateError("state_target_locator_invalid", "Invalid dependency locator.")
            state.validate_entry(dict(locator, kind="work", parent=locator["ref"].split("/")[0]
                                 if isinstance(locator["ref"], str) else None,
                                 execution="planned", approval="pending", finalization=None))
            if dependency in locators and locators[dependency] != locator:
                raise state.StateError("state_target_locator_conflict", "Conflicting dependency locators.")
            locators[dependency] = locator

    for dependency in sorted({gate.dependency for gate in gates}):
        locator = locators.get(dependency)
        if dependency in targets:
            item = plans[dependency]
            if locator and any(locator[field] != item[field] for field in locator):
                raise state.StateError("state_target_locator_conflict", "Locator disagrees with open Work.")
            continue
        if locator is None:
            continue
        _text, metadata = capture(locator["order_path"])
        if (_mapping(metadata.get("key", {}), "target key").get("id") != dependency
                or metadata.get("doc_type") != "work_order"):
            raise state.StateError("state_target_identity_mismatch", "Dependency locator owner differs.")
        inspected = store.inspect(locator["ref"], locator["order_path"])
        if inspected["status"] == "closed":
            event = inspected["last_event"]
            item = event["result"]
            if item["order_path"] != locator["order_path"]:
                raise state.StateError("state_target_identity_mismatch", "Closure locator differs.")
            # Only actual completed closures satisfy dependency, never skipped work.
            targets[dependency] = policy.DependencyTargetState(
                item["execution"] if event["reason"] == "complete" else "cancelled", item["approval"])
        else:
            targets[dependency] = policy.DependencyTargetState()

    evaluated = policy.evaluate_dependency_graph(gates, targets, source_steps=steps,
                                                 structured_dependencies=declared)
    findings.extend({"severity": "error", "code": item.code, "message": item.message}
                    for item in evaluated.diagnostics)
    evaluations = []
    for item in evaluated.evaluations:
        row = asdict(item)
        row["steps"] = list(item.steps)
        row["cycle_events"] = list(item.cycle_events)
        row.update(result=item.status.value, status=item.status.value,
                   source_path=plans[item.source_id]["order_path"],
                   source_ref=plans[item.source_id]["ref"],
                   applies_to={"steps": list(item.steps), "work_completion": item.work_completion},
                   target_state={"work_status": item.target_work_status,
                                 "approval_state": item.target_approval_state})
        evaluations.append(row)
    view = result["state"]
    selections = []
    for work in view["active_works"]:
        ref = work.get("execution_ref") or work["round_ref"] + "/" + work["work_ref"]
        candidates = work["active_step_refs"]
        executable, blocked = [], []
        unfinished_finalization = [item["ref"] for item in initial["items"]
                                  if (item["ref"] == ref or item["parent"] == ref)
                                  and item["finalization"] in {"pending", "in_progress"}]
        for step_ref in candidates:
            gate_blocks = [item["gate_id"] for item in evaluations if item["source_ref"] == ref
                           and item["blocking"] and step_ref.split("/")[1] in item["steps"]]
            if (by_ref[step_ref]["execution"] == "blocked" or gate_blocks
                    or unfinished_finalization):
                blocked.append({"step_ref": step_ref, "gates": gate_blocks,
                                "finalization_refs": unfinished_finalization})
            else:
                executable.append(step_ref)
        work["executable_step_refs"] = executable
        selections.append({"work_ref": ref, "selected_step": executable[0] if executable else None,
                           "blocked_steps": blocked, "executable_steps": executable})
    # No new/current state may be missed while plans and exact history were read.
    if store.current() != initial or any(store.read(path) != raw for path, raw in captured.items()):
        raise state.StateError("state_source_changed", "State or plan changed during execution recovery.")
    sources = [{"path": path, "digest": state.digest(raw)} for path, raw in sorted(captured.items())]
    view.update(document_root=document_root, dependency_evaluations=evaluations, dependency_coverage="evaluated",
                execution_ready=not findings, step_execution=selections,
                dependency_targets={key: asdict(value) for key, value in sorted(targets.items())},
                work_registry={key: {"ref": value["ref"], "order_path": value["order_path"],
                                     "steps": list(steps[key])} for key, value in plans.items()},
                finalization_gates=[item for item in evaluations if item["work_completion"]],
                finalization_states=[{"ref": item["ref"], "state": item["finalization"],
                                     "order_path": item["order_path"]} for item in initial["items"]
                                    if item["finalization"] is not None])
    result.update(status="fail" if findings else "pass", diagnostics=findings,
                  summary={"errors": len(findings), "warnings": 0},
                  policy_version="keystone-managed-work-state-v1",
                  policy_digest=state.digest(Path(__file__).read_bytes()
                      + Path(__file__).with_name("managed_work_state.py").read_bytes()
                      + Path(__file__).with_name("work_dependency_policy.py").read_bytes()),
                  sources=sources)
    result["generation"] = {"complete": True, "source_count": len(sources),
                            "source_generation": state.digest(state.encode(sources)),
                            "path_set_digest": state.digest(state.encode([s["path"] for s in sources])),
                            "snapshot_digest": state.digest(state.encode(view))}
    result["result_digest"] = state.digest(state.encode({"state": view, "generation": result["generation"]}))
    return result
