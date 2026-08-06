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


def sync_result(disposition="not_applicable", state="not_applicable"):
    return {
        "disposition": disposition,
        "state": state,
        "reason": "No independently addressable Keystone meaning changed.",
        "evidence": ["reviewed changed locators"],
    }


def orchestration_manifest():
    return {
        "schema_version": 1,
        "execution_mode": "orchestration",
        "closure_phase": "pre_acceptance",
        "context_pack": {
            "main_context_checkpoint": "main intent and accepted decisions",
            "work_context": {
                "round_ref": "R009",
                "work_ref": "R009/coordinator-keystone-closure",
                "step_refs": ["R009/S01"],
            },
            "source_documents": [
                "00_docs/standards/skills/coordinator/key-standard-coordinator.md"
            ],
            "applicable_standards": ["00_docs/standards/subagents/key-standard-subagents.md"],
            "accepted_decisions": [],
            "completion_criteria": ["bounded closure is verified"],
            "scope_boundaries": {
                "read_scope": ["skills/keystone-coordinator"],
                "allowed_edit_scope": ["skills/keystone-coordinator"],
                "excluded_scope": ["R008"],
            },
            "forbidden_changes": ["overwrite unrelated changes"],
            "verification_expectations": ["run coordinator validator tests"],
            "artifact_context": {
                "status": "ready",
                "evidence": ["Linker assignment seed"],
            },
            "reader_context": {
                "status": "ready",
                "evidence": ["Reader work recovery brief"],
            },
            "author_context": {
                "status": "not_applicable",
                "evidence": ["No source document edits are in scope"],
            },
        },
        "injected_skills": [{"skill_id": "superpowers:test-driven-development", "mode": "tdd"}],
        "worker_report": {
            "execution_mode": "orchestration",
            "status": "DONE",
            "changed_files": ["src/example.py"],
            "artifact_deltas": [
                {
                    "kind": "artifact_delta",
                    "source_surface": "src/example.py",
                    "changed_locators": ["Example.run"],
                    "semantic_summary": "Add bounded behavior.",
                    "baseline_digest": "absent",
                }
            ],
            "scope_check": "within_scope",
            "forbidden_change_check": "none",
            "verification": {"status": "pass", "evidence": ["unit tests passed"]},
        },
        "keystone_closure": {
            "document_sync": sync_result(),
            "metadata_sync": sync_result(),
            "graph_sync": sync_result(),
            "finalization": {"state": "not_started", "evidence": []},
        },
        "coordinator_review": {
            "decision": "accept_candidate",
            "main_acceptance_allowed": True,
            "evidence": ["actual state reviewed"],
        },
    }


def codes(result):
    return {diagnostic["code"] for diagnostic in result["diagnostics"]}


class ClosureValidationTest(unittest.TestCase):
    def test_valid_orchestration_is_ready_for_main_acceptance(self):
        result = validate_manifest(orchestration_manifest())

        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["diagnostics"])

    def test_direct_execution_allows_only_default_worker_contract(self):
        manifest = orchestration_manifest()
        manifest["execution_mode"] = "direct_execution"
        manifest["injected_skills"] = [
            {"skill_id": "keystone-default-bounded-worker", "mode": "default"}
        ]
        manifest["worker_report"]["execution_mode"] = "direct_execution"

        self.assertEqual("pass", validate_manifest(manifest)["status"])

    def test_orchestration_requires_an_external_skill(self):
        manifest = orchestration_manifest()
        manifest["injected_skills"] = [
            {"skill_id": "keystone-default-bounded-worker", "mode": "default"}
        ]

        self.assertIn("orchestration_external_skill_missing", codes(validate_manifest(manifest)))

    def test_direct_execution_rejects_external_skill(self):
        manifest = orchestration_manifest()
        manifest["execution_mode"] = "direct_execution"

        self.assertIn(
            "direct_execution_external_skill_forbidden",
            codes(validate_manifest(manifest)),
        )

    def test_direct_execution_requires_default_worker_contract(self):
        manifest = orchestration_manifest()
        manifest["execution_mode"] = "direct_execution"
        manifest["injected_skills"] = []

        self.assertIn(
            "direct_execution_default_skill_missing",
            codes(validate_manifest(manifest)),
        )

    def test_context_pack_requires_main_and_keystone_context(self):
        manifest = orchestration_manifest()
        manifest["context_pack"]["main_context_checkpoint"] = ""
        manifest["context_pack"]["source_documents"] = []

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("main_context_checkpoint_missing", result_codes)
        self.assertIn("source_documents_missing", result_codes)

    def test_context_pack_requires_every_bounded_contract_field(self):
        manifest = orchestration_manifest()
        context = manifest["context_pack"]
        for field in (
            "accepted_decisions",
            "completion_criteria",
            "scope_boundaries",
            "forbidden_changes",
            "verification_expectations",
            "reader_context",
            "author_context",
        ):
            del context[field]

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("accepted_decisions_missing", result_codes)
        self.assertIn("completion_criteria_missing", result_codes)
        self.assertIn("scope_boundaries_missing", result_codes)
        self.assertIn("forbidden_changes_missing", result_codes)
        self.assertIn("verification_expectations_missing", result_codes)
        self.assertIn("reader_context_status_invalid", result_codes)
        self.assertIn("author_context_status_invalid", result_codes)

    def test_context_status_requires_evidence_and_blocks_readiness(self):
        manifest = orchestration_manifest()
        manifest["context_pack"]["reader_context"] = {"status": "ready", "evidence": []}
        manifest["context_pack"]["author_context"] = {"status": "blocked", "evidence": []}

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("reader_context_evidence_missing", result_codes)
        self.assertIn("accept_candidate_not_ready", result_codes)

    def test_every_changed_file_requires_an_artifact_delta(self):
        manifest = orchestration_manifest()
        manifest["worker_report"]["changed_files"].append("tests/test_example.py")

        self.assertIn("artifact_delta_missing", codes(validate_manifest(manifest)))

    def test_changed_files_rejects_non_string_and_blank_entries(self):
        for entry in (42, "   "):
            with self.subTest(entry=entry):
                manifest = orchestration_manifest()
                manifest["worker_report"]["changed_files"] = [entry]
                manifest["worker_report"]["artifact_deltas"] = []

                self.assertIn(
                    "worker_report_changed_file_invalid",
                    codes(validate_manifest(manifest)),
                )

    def test_changed_files_rejects_duplicates_before_matching_artifact_deltas(self):
        manifest = orchestration_manifest()
        manifest["worker_report"]["changed_files"] = ["src/example.py", "src/example.py"]

        self.assertIn(
            "worker_report_changed_file_duplicate",
            codes(validate_manifest(manifest)),
        )

    def test_worker_report_requires_explicit_arrays_matching_execution_mode_and_delta_kind(self):
        manifest = orchestration_manifest()
        del manifest["worker_report"]["changed_files"]
        del manifest["worker_report"]["artifact_deltas"]
        manifest["worker_report"]["execution_mode"] = "direct_execution"

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("worker_report_changed_files_missing", result_codes)
        self.assertIn("worker_report_artifact_deltas_missing", result_codes)
        self.assertIn("worker_report_execution_mode_invalid", result_codes)

    def test_no_change_report_uses_explicit_empty_arrays(self):
        manifest = orchestration_manifest()
        manifest["worker_report"]["changed_files"] = []
        manifest["worker_report"]["artifact_deltas"] = []

        self.assertEqual("pass", validate_manifest(manifest)["status"])

    def test_artifact_delta_kind_and_one_to_one_changed_surface_are_required(self):
        manifest = orchestration_manifest()
        manifest["worker_report"]["artifact_deltas"][0]["kind"] = "other"
        manifest["worker_report"]["artifact_deltas"].append(
            deepcopy(manifest["worker_report"]["artifact_deltas"][0])
        )

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("artifact_delta_kind_invalid", result_codes)
        self.assertIn("artifact_delta_duplicate", result_codes)

    def test_accept_candidate_rejects_every_non_ready_report_status(self):
        for status in ("BLOCKED", "NEEDS_CONTEXT", "NEEDS_SCOPE_CHANGE", "DONE_WITH_CONCERNS"):
            with self.subTest(status=status):
                manifest = orchestration_manifest()
                manifest["worker_report"]["status"] = status

                result_codes = codes(validate_manifest(manifest))
                self.assertIn("worker_report_not_ready_for_acceptance", result_codes)
                self.assertIn("accept_candidate_not_ready", result_codes)

    def test_required_sync_must_be_complete_with_evidence(self):
        manifest = orchestration_manifest()
        manifest["keystone_closure"]["metadata_sync"] = sync_result("required", "pending")

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("metadata_sync_incomplete", result_codes)
        self.assertIn("accept_candidate_not_ready", result_codes)

    def test_not_applicable_sync_requires_reason_and_evidence(self):
        manifest = orchestration_manifest()
        manifest["keystone_closure"]["graph_sync"]["reason"] = ""
        manifest["keystone_closure"]["graph_sync"]["evidence"] = []

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("graph_sync_reason_missing", result_codes)
        self.assertIn("graph_sync_evidence_missing", result_codes)

    def test_external_done_does_not_bypass_keystone_closure(self):
        manifest = orchestration_manifest()
        manifest["keystone_closure"]["document_sync"] = sync_result("deferred", "pending")

        result = validate_manifest(manifest)

        self.assertEqual("fail", result["status"])
        self.assertIn("accept_candidate_not_ready", codes(result))

    def test_post_acceptance_requires_acceptance_and_finalization_evidence(self):
        manifest = orchestration_manifest()
        manifest["closure_phase"] = "post_acceptance"
        manifest["keystone_closure"]["acceptance_ref"] = "R009/S01/main-acceptance"
        manifest["keystone_closure"]["acceptance_evidence"] = ["Main acceptance recorded"]
        manifest["keystone_closure"]["finalization"] = {
            "state": "complete",
            "evidence": ["schema-v3 finalization passed"],
            "acceptance_ref": "R009/S01/main-acceptance",
        }
        manifest["coordinator_review"] = {
            "decision": "closure_complete",
            "main_acceptance_allowed": False,
            "evidence": ["Main acceptance recorded"],
        }

        self.assertEqual("pass", validate_manifest(manifest)["status"])

        manifest["keystone_closure"]["finalization"]["acceptance_ref"] = ""
        self.assertIn("finalization_acceptance_ref_missing", codes(validate_manifest(manifest)))

    def test_every_post_acceptance_decision_requires_acceptance_evidence(self):
        manifest = orchestration_manifest()
        manifest["closure_phase"] = "post_acceptance"
        manifest["coordinator_review"] = {
            "decision": "repair",
            "main_acceptance_allowed": False,
            "evidence": ["repair needed after Main acceptance"],
        }

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("acceptance_ref_missing", result_codes)
        self.assertIn("acceptance_evidence_missing", result_codes)

    def test_closure_complete_requires_context_scope_and_verification_readiness(self):
        manifest = orchestration_manifest()
        manifest["closure_phase"] = "post_acceptance"
        manifest["keystone_closure"]["acceptance_ref"] = "R009/S01/main-acceptance"
        manifest["keystone_closure"]["acceptance_evidence"] = ["Main acceptance recorded"]
        manifest["keystone_closure"]["finalization"] = {
            "state": "complete",
            "acceptance_ref": "R009/S01/main-acceptance",
            "evidence": ["Author finalization passed"],
        }
        manifest["coordinator_review"] = {
            "decision": "closure_complete",
            "main_acceptance_allowed": False,
            "evidence": ["post-acceptance review"],
        }
        manifest["worker_report"]["scope_check"] = "out_of_scope"
        manifest["worker_report"]["verification"] = {"status": "fail", "evidence": ["test failed"]}

        result_codes = codes(validate_manifest(manifest))
        self.assertIn("post_acceptance_closure_incomplete", result_codes)

    def test_waived_finalization_requires_concrete_waiver_reason(self):
        manifest = orchestration_manifest()
        manifest["closure_phase"] = "post_acceptance"
        manifest["keystone_closure"]["acceptance_ref"] = "R009/S01/main-acceptance"
        manifest["keystone_closure"]["acceptance_evidence"] = ["Main acceptance recorded"]
        manifest["keystone_closure"]["finalization"] = {
            "state": "waived",
            "acceptance_ref": "R009/S01/main-acceptance",
            "evidence": ["Main waived finalization"],
            "waiver_reason": "",
        }
        manifest["coordinator_review"] = {
            "decision": "closure_complete",
            "main_acceptance_allowed": False,
            "evidence": ["waiver reviewed"],
        }

        self.assertIn("finalization_waiver_reason_missing", codes(validate_manifest(manifest)))

    def test_cli_uses_diagnostic_envelope_and_exit_codes(self):
        manifest = orchestration_manifest()
        manifest["keystone_closure"]["graph_sync"] = sync_result("required", "pending")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_closure.py"), "--manifest", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

        payload = json.loads(process.stdout)
        self.assertEqual(1, process.returncode)
        self.assertEqual(1, payload["schema_version"])
        self.assertEqual("fail", payload["status"])
        self.assertGreater(payload["summary"]["errors"], 0)

    def test_cli_returns_zero_for_complete_pre_acceptance_closure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_text(json.dumps(orchestration_manifest()), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_closure.py"), "--manifest", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

        payload = json.loads(process.stdout)
        self.assertEqual(0, process.returncode)
        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["diagnostics"])

    def test_cli_preserves_error_envelope_for_unicode_decode_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_bytes(b"\xff")
            process = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_closure.py"), "--manifest", str(path)],
                check=False,
                capture_output=True,
            )

        payload = json.loads(process.stdout.decode("utf-8"))
        self.assertEqual(2, process.returncode)
        self.assertEqual("error", payload["status"])
        self.assertEqual("manifest_unreadable", payload["diagnostics"][0]["code"])


if __name__ == "__main__":
    unittest.main()
