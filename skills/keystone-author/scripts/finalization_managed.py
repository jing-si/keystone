"""Optional v7 finalization check against managed state and exact history."""

from pathlib import Path
from typing import Any, Dict, List

from managed_work_state import StateError, StateStore
from work_state_runtime import evaluate_repository
from finalization_support import diagnostic


def validate_managed_finalization(root: Path, manifest: Dict[str, Any]) -> List[Dict[str, str]]:
    required = {"schema_version", "document_root", "acceptance_ref", "accepted_refs",
                "work_state_runtime"}
    if set(manifest) != required or not isinstance(manifest.get("document_root"), str):
        return [diagnostic("managed_finalization_invalid", "Invalid v7 finalization fields.")]
    if not isinstance(manifest["acceptance_ref"], str) or not manifest["acceptance_ref"].strip():
        return [diagnostic("acceptance_ref_missing", "An explicit acceptance reference is required.")]
    targets = manifest["accepted_refs"]
    if not isinstance(targets, list) or not targets:
        return [diagnostic("managed_finalization_invalid", "accepted_refs must be nonempty.")]
    runtime = evaluate_repository(root, manifest["document_root"], managed=True)
    if runtime["status"] != "pass":
        return runtime["diagnostics"]
    generation = runtime["generation"]
    expected = {"policy_digest": runtime["policy_digest"], "result_digest": runtime["result_digest"],
                "source_generation": generation["source_generation"],
                "path_set_digest": generation["path_set_digest"], "complete": generation["complete"]}
    findings = []
    if manifest["work_state_runtime"] != expected:
        findings.append(diagnostic("work_state_runtime_binding_mismatch", "Stale runtime binding."))
    try:
        store = StateStore(root, manifest["document_root"])
        seen = set()
        captured = {}
        for target in targets:
            if (not isinstance(target, dict) or set(target) != {"ref", "order_path"}
                    or not isinstance(target["ref"], str) or target["ref"] in seen):
                findings.append(diagnostic("managed_finalization_target_invalid", "Invalid or duplicate target."))
                continue
            seen.add(target["ref"])
            inspected = store.inspect(target["ref"], target["order_path"])
            captured[target["order_path"]] = store.read(target["order_path"])
            if inspected["status"] == "managed":
                item = inspected["entry"]
            elif inspected["status"] == "closed" and inspected["last_event"]["reason"] == "complete":
                item = inspected["last_event"]["result"]
                if item["order_path"] != target["order_path"]:
                    findings.append(diagnostic("state_order_mismatch", "Closed result has another owner."))
                    continue
            else:
                findings.append(diagnostic("managed_finalization_source_unresolved",
                                           "Acceptance target is " + inspected["status"] + "."))
                continue
            descendants = [child for child in runtime["state"]["managed_items"]
                           if child["parent"] == item["ref"]
                           or (item["kind"] == "round" and
                               (child["ref"].startswith(item["ref"] + "/")
                                or child["ref"].startswith(item["ref"] + "-")))]
            for entry in [item] + descendants:
                if (entry["execution"] != "complete" or entry["approval"] != "accepted"
                        or entry["finalization"] not in {None, "complete", "waived"}):
                    findings.append(diagnostic("managed_finalization_unfinished",
                                               "Still requires management: " + entry["ref"]))
            for gate in runtime["state"]["dependency_evaluations"]:
                applies = gate["source_ref"] == item["ref"] and gate["work_completion"]
                applies = applies or (item["kind"] == "step" and gate["source_ref"] == item["parent"]
                                      and item["ref"].split("/")[1] in gate["steps"])
                if gate["blocking"] and applies:
                    findings.append(diagnostic("managed_finalization_dependency_blocked", gate["gate_id"]))
        after = evaluate_repository(root, manifest["document_root"], managed=True)
        if (after.get("result_digest") != runtime["result_digest"]
                or any(store.read(path) != raw for path, raw in captured.items())):
            findings.append(diagnostic("state_source_changed", "Sources changed during finalization check."))
    except (StateError, OSError) as error:
        findings.append(diagnostic(getattr(error, "code", "state_io_error"), str(error)))
    return findings
