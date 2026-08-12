import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


PACKAGE_ROOT = Path(__file__).parents[1]
SCRIPTS = PACKAGE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_closure import validate_manifest  # noqa: E402


def current_manifest(phase="pre_acceptance"):
    manifest = {
        "schema_version": 1,
        "execution_mode": "direct_execution",
        "closure_phase": phase,
        "worker_report": {
            "status": "DONE",
            "changed_files": ["src/example.py"],
            "scope_check": "within_scope",
            "forbidden_change_check": "none",
            "verification": {"status": "pass", "evidence": ["unit tests passed"]},
        },
        "keystone_closure": {},
        "coordinator_review": {"decision": "accept_candidate"},
    }
    if phase == "post_acceptance":
        manifest["coordinator_review"] = {
            "decision": "closure_complete",
            "acceptance_ref": "R010/S06/main-acceptance",
        }
        manifest["keystone_closure"]["progress"] = {
            "state": "updated",
            "evidence": ["Progress records the accepted current result"],
        }
    return manifest


def codes(result):
    return {item["code"] for item in result["diagnostics"]}


class ClosureValidationTest(unittest.TestCase):
    def test_current_direct_execution_passes_without_secret_or_external_evidence(self):
        result = validate_manifest(current_manifest())
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["diagnostics"])

    def test_current_orchestration_requires_selected_skill(self):
        manifest = current_manifest()
        manifest["execution_mode"] = "orchestration"
        result = validate_manifest(manifest)
        self.assertIn("orchestration_skill_missing", codes(result))
        manifest["injected_skills"] = [{"skill_id": "test-driven-development"}]
        self.assertEqual("pass", validate_manifest(manifest)["status"])

    def test_optional_sync_requires_evidence_only_when_required(self):
        manifest = current_manifest()
        manifest["keystone_closure"]["graph_sync"] = {
            "disposition": "not_applicable",
            "reason": "No graph-relevant source changed.",
        }
        self.assertEqual("pass", validate_manifest(manifest)["status"])
        manifest["keystone_closure"]["graph_sync"] = {
            "disposition": "required",
            "reason": "Metadata changed.",
        }
        self.assertIn("sync_evidence_missing", codes(validate_manifest(manifest)))

    def test_accept_candidate_requires_verified_in_scope_done_result(self):
        for path, value in (
            (("worker_report", "status"), "BLOCKED"),
            (("worker_report", "scope_check"), "outside_scope"),
            (("worker_report", "verification", "status"), "fail"),
        ):
            manifest = current_manifest()
            target = manifest
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            self.assertIn("acceptance_candidate_not_ready", codes(validate_manifest(manifest)))

    def test_post_acceptance_requires_main_reference_and_progress(self):
        manifest = current_manifest("post_acceptance")
        self.assertEqual("pass", validate_manifest(manifest)["status"])
        del manifest["coordinator_review"]["acceptance_ref"]
        del manifest["keystone_closure"]["progress"]
        result = validate_manifest(manifest)
        self.assertIn("acceptance_ref_missing", codes(result))
        self.assertIn("progress_sync_incomplete", codes(result))

    def test_cli_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "closure.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_closure.py"), "--manifest", str(path)],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(2, process.returncode)
        self.assertEqual("error", json.loads(process.stdout)["status"])


if __name__ == "__main__":
    unittest.main()
