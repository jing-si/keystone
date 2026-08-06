import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).parents[1]
VALIDATOR = PACKAGE_ROOT / "scripts" / "validate_finalization.py"
RUNNER = PACKAGE_ROOT / "scripts" / "run_finalization_validation.py"
HOOK = PACKAGE_ROOT / "scripts" / "check_finalization_hook.sh"
CORE_CATEGORIES = [
    "progress",
    "work_order_change_set",
    "work_index",
    "round_index",
    "root_index",
    "context_map",
    "standard_decision_plan",
    "recovery",
    "implementation_gate",
    "residual_risk",
    "namespace",
]


class R008FinalizationFixture(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.write("s06-c.md", self.progress("R008/S06-C", "R008/credential-auth", "accepted", finalization=True))
        self.write("s06-d.md", self.progress("R008/S06-D", "R008/distributed-limiter", "in_progress"))
        self.write("s06-e.md", self.progress("R008/S06-E", "R008/future-work", "planned"))
        for name in ("work-index.md", "round-index.md", "context-map.md"):
            self.write(name, "# State\n\nActive steps: [R008/S06-D]\n")
        self.write("candidate.md", "# Candidate\n\nR008/S06-D is active.\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def write(self, name, content):
        path = self.docs / name
        path.write_text(content, encoding="utf-8")
        return path

    def progress(self, step_ref, work_ref, status, finalization=False):
        text = f"---\nwork_status: {status}\nstep_ref: {step_ref}\nwork_ref: {work_ref}\n---\n# Progress\n"
        if finalization:
            text += (
                "\nfinalization:\n"
                "  state: in_progress\n"
                "  acceptance_ref: R008/S06-C/main-acceptance\n"
            )
        return text

    def manifest(self):
        manifest = {
            "schema_version": 1,
            "acceptance_ref": "R008/S06-C/main-acceptance",
            "steps": [
                {"ref": "R008/S06-C", "work_ref": "R008/credential-auth", "status": "accepted", "progress_path": "docs/s06-c.md"},
                {"ref": "R008/S06-D", "work_ref": "R008/distributed-limiter", "status": "in_progress", "progress_path": "docs/s06-d.md"},
                {"ref": "R008/S06-E", "work_ref": "R008/future-work", "status": "planned", "progress_path": "docs/s06-e.md"},
            ],
            "accepted_steps": ["R008/S06-C"],
            "status_transitions": [
                {"ref": "R008/S06-C", "from": "in_progress", "to": "accepted", "kind": "step"}
            ],
            "active_steps": ["R008/S06-D"],
            "active_step_sources": [
                {"category": "work_index", "path": "docs/work-index.md"},
                {"category": "round_index", "path": "docs/round-index.md"},
                {"category": "context_map", "path": "docs/context-map.md"},
            ],
            "early_work": [
                {
                    "target_step": "R008/S06-E",
                    "cause": "S06-C required a future integration seam.",
                    "completed_scope": ["integration seam"],
                    "remaining_scope": ["S06-E implementation"],
                    "status_effect": "none",
                }
            ],
            "finalization": {
                "required": True,
                "state": "in_progress",
                "progress_path": "docs/s06-c.md",
                "evidence": ["main_acceptance", "impact_dispositions", "source_updates", "semantic_review"],
            },
            "impact_candidates": [],
            "namespace_entries": [],
        }
        for category in CORE_CATEGORIES:
            candidate = {
                "category": category,
                "artifact": category,
                "path": "docs/candidate.md",
                "disposition": "no_change_required",
                "reason": f"{category} evaluated by the public fixture.",
            }
            if category == "implementation_gate":
                candidate.update(gate_state="resolved", gate_scope="R008/S06-C")
            elif category == "residual_risk":
                candidate.update(risk_state="none", risk_items=[])
            elif category == "namespace":
                candidate.update(namespace_state="checked")
            manifest["impact_candidates"].append(candidate)
        return manifest

    def run_command(self, command, manifest=None):
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest or self.manifest()), encoding="utf-8")
        process = subprocess.run(
            [*command, "--root", str(self.root), "--manifest", str(manifest_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(process.stdout) if process.stdout else None
        return process, payload

    def codes(self, payload):
        return {item["code"] for item in payload.get("diagnostics", [])}

    def test_01_accepted_step_parallel_active_step_and_aggregate_sources_converge(self):
        process, payload = self.run_command([sys.executable, str(VALIDATOR)])
        self.assertEqual(0, process.returncode)
        self.assertEqual("pass", payload["status"])

    def test_02_different_active_step_reference_in_round_index_is_detected(self):
        self.write("round-index.md", "# Round\n\nActive steps: [R008/S06-B]\n")
        process, payload = self.run_command([sys.executable, str(VALIDATOR)])
        self.assertEqual(1, process.returncode)
        self.assertIn("active_steps_source_mismatch", self.codes(payload))

    def test_03_live_worker_step_claim_is_stale_but_historical_claim_is_allowed(self):
        stale = self.write("stale.md", "# Recovery\n\nWorker S06-B\n")
        manifest = self.manifest()
        manifest["impact_candidates"][0].update(path="docs/stale.md", disposition="updated")
        process, payload = self.run_command([sys.executable, str(VALIDATOR)], manifest)
        self.assertEqual(1, process.returncode)
        self.assertIn("singular_current_step_claim", self.codes(payload))

        manifest["impact_candidates"][0]["disposition"] = "historical"
        process, payload = self.run_command([sys.executable, str(VALIDATOR)], manifest)
        self.assertEqual(0, process.returncode)

    def test_04_unresolved_gate_and_unrecorded_residual_risk_fail(self):
        manifest = self.manifest()
        for item in manifest["impact_candidates"]:
            if item["category"] in {"implementation_gate", "residual_risk"}:
                item.clear()
                item.update(category="other", artifact="missing", disposition="out_of_scope", reason="omitted")
        process, payload = self.run_command([sys.executable, str(VALIDATOR)], manifest)
        self.assertEqual(1, process.returncode)
        self.assertIn("impact_category_missing", self.codes(payload))

    def test_05_r008_r010_flyway_v12_collision_requires_integration_resolution(self):
        manifest = self.manifest()
        manifest["namespace_entries"] = [
            {"namespace": "flyway", "value": "V12", "owner": "R008"},
            {"namespace": "flyway", "value": "V12", "owner": "R010"},
        ]
        process, payload = self.run_command([sys.executable, str(VALIDATOR)], manifest)
        self.assertEqual(1, process.returncode)
        self.assertIn("namespace_collision", self.codes(payload))

    def test_06_missing_validator_and_malformed_process_output_are_distinct_failures(self):
        process, payload = self.run_command(
            [sys.executable, str(RUNNER), "--validator", str(self.root / "missing.py")]
        )
        self.assertEqual("validator_unavailable", payload["diagnostics"][0]["code"])

        broken = self.write("broken.py", "print('not json')\n")
        process, payload = self.run_command([sys.executable, str(RUNNER), "--validator", str(broken)])
        self.assertEqual("validator_execution_failed", payload["diagnostics"][0]["code"])

    def test_07_only_accepted_step_transitions_while_independent_active_step_continues(self):
        manifest = self.manifest()
        manifest["status_transitions"].append(
            {"ref": "R008/S06-D", "from": "in_progress", "to": "accepted", "kind": "step"}
        )
        process, payload = self.run_command([sys.executable, str(VALIDATOR)], manifest)
        self.assertEqual(1, process.returncode)
        self.assertIn("direct_step_transition_not_accepted", self.codes(payload))

    def test_08_failed_namespace_finalization_can_resume_with_preserved_acceptance(self):
        manifest = self.manifest()
        manifest["namespace_entries"] = [
            {"namespace": "flyway", "value": "V12", "owner": "R008"},
            {"namespace": "flyway", "value": "V12", "owner": "R010"},
        ]
        failed, _ = self.run_command([sys.executable, str(VALIDATOR)], manifest)
        manifest["namespace_entries"][1]["value"] = "V13"
        resumed, payload = self.run_command([sys.executable, str(VALIDATOR)], manifest)
        self.assertEqual(1, failed.returncode)
        self.assertEqual("accepted", manifest["steps"][0]["status"])
        self.assertEqual(0, resumed.returncode)
        self.assertEqual("pass", payload["status"])

    def test_09_passing_project_extension_cannot_override_core_failure(self):
        extension = self.write(
            "extension.py",
            "import json\nprint(json.dumps({'schema_version':1,'status':'pass','diagnostics':[],"
            "'summary':{'errors':0,'warnings':0}}))\n",
        )
        manifest = self.manifest()
        manifest["namespace_entries"] = [
            {"namespace": "flyway", "value": "V12", "owner": "R008"},
            {"namespace": "flyway", "value": "V12", "owner": "R010"},
        ]
        process, payload = self.run_command(
            [sys.executable, str(RUNNER), "--extension", str(extension)], manifest
        )
        self.assertEqual(1, process.returncode)
        self.assertIn("namespace_collision", self.codes(payload))

    def test_10_hook_wrapper_invokes_the_same_package_runner(self):
        process, payload = self.run_command(["bash", str(HOOK)])
        self.assertEqual(0, process.returncode)
        self.assertEqual("pass", payload["status"])

    def test_11_equal_active_steps_and_future_early_work_do_not_change_future_status(self):
        manifest = self.manifest()
        self.write("s06-f.md", self.progress("R008/S06-F", "R008/parallel-work", "in_progress"))
        manifest["steps"].append(
            {"ref": "R008/S06-F", "work_ref": "R008/parallel-work", "status": "in_progress", "progress_path": "docs/s06-f.md"}
        )
        manifest["active_steps"].append("R008/S06-F")
        for name in ("work-index.md", "round-index.md", "context-map.md"):
            self.write(name, "# State\n\nActive steps: [R008/S06-D, R008/S06-F]\n")
        process, payload = self.run_command([sys.executable, str(VALIDATOR)], manifest)
        self.assertEqual(0, process.returncode)
        self.assertEqual("planned", manifest["steps"][2]["status"])
        self.assertEqual("none", manifest["early_work"][0]["status_effect"])


if __name__ == "__main__":
    unittest.main()
