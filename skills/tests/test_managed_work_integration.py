"""Execution recovery and consumer parity against isolated managed projects."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_managed_work_state import runtime as backend, ROOT
from test_work_state_runtime import RUNTIME


class ManagedIntegrationTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.store = backend.StateStore(self.root)
        self.items = {}
        self.add_work("R001", "first")
        self.add_work("R002", "second")
        self.marker = self.root / "00_docs/state/manifest.json"
        self.marker.write_text('{"schema_version":1,"mode":"managed"}')

    def write_plan(self, round_ref, slug, extra=""):
        path = f"00_docs/works/{round_ref.lower()}-{slug}/key-work-{slug}.md"
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        old = target.read_text() if target.exists() else ""
        events = "\n".join(line for line in old.splitlines() if line.startswith(backend.EVENT_PREFIX))
        target.write_text(f"---\ndoc_type: work_order\nkey:\n  id: key.work.{slug}.order\n"
                          + extra + f"---\n# {slug}\n### {round_ref}/S01\n### {round_ref}/S02\n" + events + "\n")
        return path

    def add_work(self, ref, slug):
        path = self.write_plan(ref, slug)
        for key, kind, parent in ((ref, "round", None), (ref + "/" + slug, "work", ref),
                                  (ref + "/S01", "step", ref + "/" + slug),
                                  (ref + "/S02", "step", ref + "/" + slug)):
            item = {"ref": key, "kind": kind, "parent": parent, "order_path": path,
                    "execution": "planned", "approval": "pending", "finalization": None}
            self.change("create", item)
            item = dict(item, execution="in_progress")
            self.change("update", item)
            self.items[key] = item

    def test_round_direct_steps_recover_without_synthetic_work(self):
        path = self.write_plan("R003", "direct", "  defined_steps: [S01, S02]\n")
        for ref, kind, parent in (("R003", "round", None), ("R003/S01", "step", "R003"),
                                  ("R003/S02", "step", "R003")):
            item = dict(ref=ref, kind=kind, parent=parent, order_path=path,
                        execution="in_progress", approval="pending", finalization=None)
            self.change("create", item)
        result = RUNTIME.evaluate_repository(self.root)
        self.assertEqual("pass", result["status"], result["diagnostics"])
        selection = next(item for item in result["state"]["step_execution"] if item["work_ref"] == "R003")
        self.assertEqual("R003/S01", selection["selected_step"])
        self.assertFalse(any(item["kind"] == "work" and item["parent"] == "R003"
                             for item in self.store.current()["items"]))

    def change(self, action, item, **kwargs):
        token = backend.digest(self.store.read(self.store.source_path))
        self.store.change(action, item, expected_digest=token, at="2026-10-12",
                          note="Fixture evidence", **kwargs)

    def gate(self, extra="", target="key.work.first.order", optional=False):
        self.write_plan("R002", "second", f'''  relations:
    depends_on: [{target}]
work_gates:
  - dependency: {target}
    applies_to: {{steps: [S01], work_completion: true}}
    condition: {{work_status: complete, approval_state: accepted}}
    optional: {str(optional).lower()}
''' + extra)

    def evaluate(self):
        return RUNTIME.evaluate_repository(self.root)

    def complete(self, ref):
        item = dict(self.items[ref], execution="complete", approval="accepted", finalization="complete")
        self.change("update", item)
        self.items[ref] = item

    def close_first(self, reason="complete"):
        for ref in ("R001/S01", "R001/S02", "R001/first", "R001"):
            self.complete(ref)
            self.change("close", self.items[ref], reason=reason)

    def test_marker_activates_default_and_legacy_status_is_ignored(self):
        result = self.evaluate()
        self.assertEqual("pass", result["status"], result)
        self.assertTrue(result["state"]["execution_ready"])
        stale = self.root / "00_docs/works/r001-first/key-progress.md"
        stale.write_text("---\nwork_status: cancelled\napproval: {state: rejected}\n---")
        self.assertEqual(result, self.evaluate())
        self.marker.unlink()
        self.assertNotEqual("managed_state", self.evaluate().get("state", {}).get("mode"))

    def test_corrupt_marker_never_falls_back(self):
        self.marker.write_text("not json")
        result = self.evaluate()
        self.assertEqual("fail", result["status"])
        self.assertEqual("state_json_invalid", result["diagnostics"][0]["code"])

    def test_gate_blocks_lowest_step_and_selects_next_then_acceptance_unblocks(self):
        self.gate()
        result = self.evaluate()
        self.assertEqual("pass", result["status"], result)
        selection = result["state"]["step_execution"][1]
        self.assertEqual("R002/S02", selection["selected_step"])
        self.assertEqual("waiting", result["state"]["dependency_evaluations"][0]["result"])
        self.complete("R001/first")
        result = self.evaluate()
        self.assertEqual("R002/S01", result["state"]["step_execution"][1]["selected_step"])
        self.assertFalse(result["state"]["dependency_evaluations"][0]["blocking"])

    def test_closed_dependency_reads_only_exact_history(self):
        locator = '''work_state_targets:
  key.work.first.order:
    ref: R001/first
    order_path: 00_docs/works/r001-first/key-work-first.md
'''
        self.gate(locator)
        self.close_first()
        poison = self.root / "00_docs/works/r999-old/key-work-old.md"
        poison.parent.mkdir()
        poison.write_bytes(b"\xff")
        with patch.object(Path, "rglob", side_effect=AssertionError("recursive history scan")):
            result = self.evaluate()
        self.assertEqual("pass", result["status"], result)
        self.assertEqual("satisfied", result["state"]["dependency_evaluations"][0]["result"])
        self.assertNotIn("R001", result["state"]["open_rounds"])
        self.assertNotIn(str(poison.relative_to(self.root)), [s["path"] for s in result["sources"]])
        # Reopening makes the current state authoritative again, never the old closure.
        self.change("reopen", dict(self.items["R001"], execution="planned", approval="pending"))
        self.change("reopen", dict(self.items["R001/first"], execution="planned", approval="pending"))
        self.assertEqual("waiting", self.evaluate()["state"]["dependency_evaluations"][0]["result"])

    def test_absence_is_unresolvable_and_optional_does_not_block(self):
        self.gate(target="key.work.absent.order", optional=True)
        result = self.evaluate()
        gate = result["state"]["dependency_evaluations"][0]
        self.assertEqual("unresolvable", gate["result"])
        self.assertFalse(gate["blocking"])
        self.assertEqual("R002/S01", result["state"]["step_execution"][1]["selected_step"])

    def test_skipped_closure_cannot_satisfy_gate(self):
        self.gate('''work_state_targets:
  key.work.first.order: {ref: R001/first, order_path: 00_docs/works/r001-first/key-work-first.md}
''')
        self.close_first("skipped")
        self.assertEqual("unresolvable", self.evaluate()["state"]["dependency_evaluations"][0]["result"])

    def test_invalid_gate_and_cycle_fail_execution_readiness(self):
        self.gate()
        self.write_plan("R001", "first", '''  relations:
    depends_on: [key.work.second.order]
work_gates:
  - dependency: key.work.second.order
    applies_to: {steps: [S01], work_completion: true}
    condition: {work_status: complete, approval_state: accepted}
''')
        result = self.evaluate()
        self.assertEqual("fail", result["status"])
        self.assertFalse(result["state"]["execution_ready"])
        self.assertIn("dependency_cycle", [d["code"] for d in result["diagnostics"]])
        self.gate()
        path = self.root / self.items["R002/second"]["order_path"]
        path.write_text(path.read_text().replace("steps: [S01]", "steps: [S99]"))
        self.assertIn("work_gate_step_invalid", [d["code"] for d in self.evaluate()["diagnostics"]])

    def test_four_packages_execute_identical_standalone_projection(self):
        self.gate()
        baseline = self.evaluate()
        for name in ("keystone-reader", "keystone-author", "keystone-coordinator", "keystone-linker"):
            result = subprocess.run([sys.executable, str(ROOT / "skills" / name / "scripts/work_state_runtime.py"),
                                     "--root", str(self.root)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(baseline, json.loads(result.stdout))

    def test_state_change_changes_generation_and_appends_order_history(self):
        before = self.evaluate()
        path = self.root / self.items["R001/first"]["order_path"]
        raw = path.read_bytes()
        self.complete("R001/first")
        after = self.evaluate()
        self.assertTrue(path.read_bytes().startswith(raw))
        self.assertNotEqual(raw, path.read_bytes())
        self.assertNotEqual(before["generation"], after["generation"])

    def test_malformed_gate_does_not_silently_disappear(self):
        self.write_plan("R002", "second", "work_gates: broken\n")
        result = self.evaluate()
        self.assertEqual("fail", result["status"])
        self.assertIn("work_gates_invalid", [d["code"] for d in result["diagnostics"]])

    def test_unfinished_finalization_blocks_next_implementation_until_settled(self):
        item = dict(self.items["R002/S01"], execution="complete", approval="accepted",
                    finalization="in_progress")
        self.change("update", item)
        result = self.evaluate()
        selection = result["state"]["step_execution"][1]
        self.assertIsNone(selection["selected_step"])
        self.assertEqual(["R002/S01"], selection["blocked_steps"][0]["finalization_refs"])
        self.change("update", dict(item, finalization="complete"))
        self.assertEqual("R002/S02", self.evaluate()["state"]["step_execution"][1]["selected_step"])

    def test_step_closure_checks_its_own_required_gate(self):
        self.gate()
        self.complete("R002/S01")
        with self.assertRaises(backend.StateError) as caught:
            self.change("close", self.items["R002/S01"], reason="complete")
        self.assertEqual("state_close_dependency_blocked", caught.exception.code)


    def test_example_headings_do_not_create_phantom_steps(self):
        path = self.root / self.items["R002/second"]["order_path"]
        with path.open("a") as stream:
            stream.write("\n```markdown\n### R002/S99\n```\n> ### R002/S98\n")
        self.assertEqual("pass", self.evaluate()["status"])


    def test_missing_registered_step_is_not_treated_as_complete(self):
        path = self.root / self.store.source_path
        value = json.loads(path.read_text())
        value["states"] = {state: [item for item in rows if item["ref"] != "R002/S01"]
                           for state, rows in value["states"].items()}
        path.write_text(json.dumps(value))
        result = self.evaluate()
        self.assertEqual("fail", result["status"])
        self.assertEqual("state_step_missing", result["diagnostics"][0]["code"])

    def test_open_entry_without_creation_history_is_conflict(self):
        path = self.root / self.items["R002/second"]["order_path"]
        path.write_text("\n".join(line for line in path.read_text().splitlines()
                                  if not line.startswith(backend.EVENT_PREFIX)))
        self.assertEqual("state_history_conflict", self.evaluate()["diagnostics"][0]["code"])

    def linker(self):
        script = """import json, sys
from graph_runtime.readiness import context_readiness
r = context_readiness(sys.argv[1], sys.argv[2], initiator='reader',
    discovery_mode='targeted', source_paths=[sys.argv[3]])
print(json.dumps({'digest':r.result.freshness.digest,
    'gates':[(g.dependency,g.status.value,g.blocking) for g in r.result.dependency_evaluations],
    'codes':[d.code for d in r.result.diagnostics]}))
"""
        env = dict(os.environ, PYTHONPATH=str(ROOT / "skills/keystone-linker/scripts"))
        result = subprocess.run([sys.executable, "-c", script, str(self.root),
                                 str(self.root / "cache.sqlite"), self.items["R002/second"]["order_path"]],
                                env=env, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_linker_matches_reader_and_invalidates_after_state_only_update(self):
        self.gate()
        before = self.linker()
        self.assertEqual([["key.work.first.order", "waiting", True]], before["gates"])
        self.complete("R001/first")
        after = self.linker()
        self.assertEqual([["key.work.first.order", "satisfied", False]], after["gates"])
        self.assertNotEqual(before["digest"], after["digest"])
        self.marker.write_text("broken")
        broken = self.linker()
        self.assertEqual([], broken["gates"])
        self.assertIn("state_json_invalid", broken["codes"])

    def finalization_manifest(self):
        result = self.evaluate()
        generation = result["generation"]
        return {"schema_version": 7, "document_root": "00_docs", "acceptance_ref": "main-test",
                "accepted_refs": [{"ref": "R002/S01", "order_path": self.items["R002/S01"]["order_path"]}],
                "work_state_runtime": {"policy_digest": result["policy_digest"],
                "result_digest": result["result_digest"], "complete": generation["complete"],
                "source_generation": generation["source_generation"],
                "path_set_digest": generation["path_set_digest"]}}

    def finalize(self, manifest):
        path = self.root / "finalization.json"
        path.write_text(json.dumps(manifest))
        result = subprocess.run([sys.executable,
            str(ROOT / "skills/keystone-author/scripts/validate_finalization.py"),
            "--root", str(self.root), "--manifest", str(path)], capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_finalization_uses_current_state_and_rejects_stale_binding(self):
        self.complete("R002/S01")
        manifest = self.finalization_manifest()
        self.assertEqual("pass", self.finalize(manifest)["status"])
        item = dict(self.items["R002/S01"], finalization="in_progress")
        self.change("update", item)
        codes = [d["code"] for d in self.finalize(manifest)["diagnostics"]]
        self.assertIn("work_state_runtime_binding_mismatch", codes)
        self.assertIn("managed_finalization_unfinished", codes)

    def test_finalization_rejects_blocked_step_and_old_manifest(self):
        self.gate()
        self.complete("R002/S01")
        codes = [d["code"] for d in self.finalize(self.finalization_manifest())["diagnostics"]]
        self.assertIn("managed_finalization_dependency_blocked", codes)
        self.assertEqual("managed_finalization_legacy_manifest",
                         self.finalize({"schema_version":6})["diagnostics"][0]["code"])

    def test_complete_work_cannot_close_with_required_dependency_unresolved(self):
        self.gate()
        path = self.root / self.items["R002/second"]["order_path"]
        path.write_text(path.read_text().replace("steps: [S01]", "steps: []"))
        for ref in ("R002/S01", "R002/S02", "R002/second"):
            self.complete(ref)
        for ref in ("R002/S01", "R002/S02"):
            self.change("close", self.items[ref], reason="complete")
        with self.assertRaises(backend.StateError) as caught:
            self.change("close", self.items["R002/second"], reason="complete")
        self.assertEqual("state_close_dependency_blocked", caught.exception.code)
        self.complete("R001/first")
        self.change("close", self.items["R002/second"], reason="complete")
        self.assertEqual("closed", self.store.inspect("R002/second",
                         self.items["R002/second"]["order_path"])["status"])


if __name__ == "__main__":
    unittest.main()
