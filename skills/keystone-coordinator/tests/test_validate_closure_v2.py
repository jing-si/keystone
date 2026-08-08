import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


PACKAGE_ROOT = Path(__file__).parents[1]
SCRIPTS = PACKAGE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_closure import validate_manifest  # noqa: E402
from closure_actual_state import repository_snapshot  # noqa: E402
import closure_v2  # noqa: E402
from closure_v2 import _valid_runner_envelope  # noqa: E402


def json_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_json(value):
    return digest_bytes(json_bytes(value))


def file_digest(path):
    return digest_bytes(path.read_bytes())


def sync_result(disposition="not_applicable", state="not_applicable"):
    return {
        "disposition": disposition,
        "state": state,
        "reason": "No independently addressable Keystone meaning changed.",
        "evidence": ["reviewed actual changed locators"],
    }


class ClosureV2ValidationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.evidence = self.base / "evidence"
        self.root.mkdir()
        self.evidence.mkdir()
        source = self.root / "src" / "example.py"
        source.parent.mkdir()
        source.write_text("before\n", encoding="utf-8")
        self.assignment = self.make_assignment(source)
        self.assignment_digest = digest_bytes(json_bytes(self.assignment))
        self.manifest = self.make_manifest()
        self.write_classification()

    def tearDown(self):
        self.temp.cleanup()

    def make_assignment(self, source):
        context = {
            "main_context_checkpoint": "R010 intent and boundaries",
            "work_context": {
                "round_ref": "R010",
                "work_ref": "R010/production-control-plane-hardening",
                "step_refs": ["R010/S01"],
            },
            "source_documents": ["00_docs/works/r010/key-work.md"],
            "applicable_standards": ["00_docs/convention.md"],
            "accepted_decisions": [],
            "completion_criteria": ["actual state is verified"],
            "scope_boundaries": {
                "read_scope": ["."],
                "allowed_edit_scope": ["src"],
                "excluded_scope": ["secret"],
            },
            "forbidden_changes": ["overwrite unrelated changes"],
            "verification_expectations": ["unit tests pass"],
            "artifact_context": {"status": "ready", "evidence": ["Linker seed"]},
            "reader_context": {"status": "ready", "evidence": ["Reader brief"]},
            "author_context": {
                "status": "not_applicable",
                "evidence": ["No document edit"],
            },
            "dependency_status": "satisfied",
            "active_step_gates": [],
            "work_completion_gates": [],
        }
        return {
            "schema_version": 2,
            "assignment_id": "R010-S01-worker-1",
            "execution_mode": "orchestration",
            "purpose": "implement",
            "authority": "bounded_edit",
            "goal": "Bind closure to actual repository state.",
            "context_pack": context,
            "injected_skills": [
                {"skill_id": "example:worker", "mode": "implementation"}
            ],
            "scope": deepcopy(context["scope_boundaries"]),
            "baseline_snapshot": [
                {"path": "src/example.py", "digest": file_digest(source)}
            ],
        }

    def make_manifest(self):
        report = {
            "assignment_id": self.assignment["assignment_id"],
            "assignment_digest": self.assignment_digest,
            "context_digest": digest_json(self.assignment["context_pack"]),
            "execution_mode": self.assignment["execution_mode"],
            "status": "DONE",
            "purpose": self.assignment["purpose"],
            "authority": self.assignment["authority"],
            "goal": self.assignment["goal"],
            "skill_usage": [
                {
                    "skill_id": "example:worker",
                    "mode": "implementation",
                    "outputs_used": ["implementation workflow"],
                    "limits_hit": [],
                }
            ],
            "changed_files": [],
            "artifact_deltas": [],
            "scope_check": "within_scope",
            "forbidden_change_check": "none",
            "verification": {"status": "pass", "evidence": ["unit tests passed"]},
        }
        return {
            "schema_version": 2,
            "closure_phase": "pre_acceptance",
            "closure_target": "step",
            "closure_step_ref": "R010/S01",
            "worker_report": report,
            "keystone_closure": {
                "document_sync": sync_result(),
                "metadata_sync": sync_result(),
                "graph_sync": {},
                "finalization": {"state": "not_started", "evidence": []},
            },
            "coordinator_review": {
                "assignment_id": self.assignment["assignment_id"],
                "assignment_digest": self.assignment_digest,
                "decision": "accept_candidate",
                "main_acceptance_allowed": True,
                "evidence": ["actual state reviewed"],
            },
        }

    def delta_digest(self):
        return digest_json(self.manifest["worker_report"]["artifact_deltas"])

    def write_classification(self):
        delta_digest = self.delta_digest()
        classification = {
            "schema_version": 1,
            "disposition": "not_applicable",
            "delta_set_digest": delta_digest,
            "reason": "No canonical graph mutation is required.",
        }
        path = self.evidence / "classification.json"
        path.write_bytes(json_bytes(classification))
        self.manifest["keystone_closure"]["graph_sync"] = {
            "disposition": "not_applicable",
            "state": "not_applicable",
            "reason": classification["reason"],
            "classification_path": "classification.json",
            "classification_digest": file_digest(path),
            "delta_set_digest": delta_digest,
        }

    def validate(self, manifest=None, **kwargs):
        return validate_manifest(
            manifest or self.manifest,
            root=self.root,
            assignment=self.assignment,
            assignment_digest=self.assignment_digest,
            evidence_root=self.evidence,
            **kwargs,
        )

    @staticmethod
    def codes(result):
        return {item["code"] for item in result["diagnostics"]}

    def assert_historical_v2_valid(self, result):
        self.assertEqual("fail", result["status"])
        self.assertEqual({"legacy_schema_not_authoritative"}, self.codes(result))

    @staticmethod
    def runner_process(payload, returncode):
        return subprocess.CompletedProcess(
            args=[], returncode=returncode,
            stdout=json.dumps(payload, sort_keys=True), stderr="",
        )

    def record_modified_source(self, content="after\n"):
        source = self.root / "src" / "example.py"
        baseline = self.assignment["baseline_snapshot"][0]["digest"]
        source.write_text(content, encoding="utf-8")
        self.manifest["worker_report"]["changed_files"] = ["src/example.py"]
        self.manifest["worker_report"]["artifact_deltas"] = [{
            "kind": "artifact_delta",
            "source_surface": "src/example.py",
            "change_kind": "modified",
            "changed_locators": [{
                "path": "src/example.py",
                "symbol": "Example.run",
            }],
            "semantic_summary": "Change bounded behavior.",
            "baseline_digest": baseline,
            "resulting_digest": file_digest(source),
            "graph_relevant": False,
        }]
        self.write_classification()

    def test_valid_v2_no_change_is_bound_to_actual_state(self):
        result = self.validate()
        self.assert_historical_v2_valid(result)

    def test_actual_modified_file_requires_exact_report_and_digests(self):
        self.record_modified_source()
        self.assert_historical_v2_valid(self.validate())

        self.manifest["worker_report"]["artifact_deltas"][0]["resulting_digest"] = (
            "sha256:" + "0" * 64
        )
        self.assertIn("artifact_resulting_digest_mismatch", self.codes(self.validate()))

    def test_artifact_delta_requires_canonical_locator_objects(self):
        invalid_locators = (
            None,
            [],
            "Example.run",
            {"path": "src/example.py", "symbol": "Example.run"},
            ["Example.run"],
            [{}],
            [{"path": ""}],
            [{"path": "src/example.py", "unknown": "value"}],
            [{"path": "src/example.py", "symbol": 7}],
        )
        for changed_locators in invalid_locators:
            with self.subTest(changed_locators=changed_locators):
                self.record_modified_source()
                self.manifest["worker_report"]["artifact_deltas"][0][
                    "changed_locators"
                ] = changed_locators
                result = self.validate()
                self.assertEqual("fail", result["status"])
                findings = [
                    item for item in result["diagnostics"]
                    if item["code"] == "artifact_delta_evidence_missing"
                ]
                self.assertEqual(1, len(findings), result)
                self.assertEqual("error", findings[0]["severity"])
                self.assertEqual("worker_report.artifact_deltas[0]", findings[0]["path"])

        self.record_modified_source()
        self.manifest["worker_report"]["artifact_deltas"][0][
            "changed_locators"
        ] = [{
            "path": "src/example.py",
            "heading": None,
            "symbol": "Example.run",
            "test_name": None,
            "config_key": None,
            "schema_name": None,
        }]
        self.write_classification()
        self.assert_historical_v2_valid(self.validate())

    def test_scope_is_computed_instead_of_trusting_worker_claim(self):
        secret = self.root / "secret" / "value.txt"
        secret.parent.mkdir()
        secret.write_text("changed\n", encoding="utf-8")
        self.manifest["worker_report"]["scope_check"] = "within_scope"
        self.assertIn("actual_change_out_of_scope", self.codes(self.validate()))

    def test_report_must_match_assignment_and_actual_change_set(self):
        self.record_modified_source()
        self.manifest["worker_report"]["assignment_id"] = "forged"
        self.manifest["worker_report"]["changed_files"] = []
        self.assertTrue(
            {"assignment_id_mismatch", "actual_changed_files_mismatch"}
            <= self.codes(self.validate())
        )

    def test_skill_usage_must_exactly_match_injected_skills(self):
        self.manifest["worker_report"]["skill_usage"][0]["skill_id"] = "other:skill"
        self.assertIn("skill_usage_mismatch", self.codes(self.validate()))

    def test_work_closure_applies_required_work_completion_gate(self):
        self.manifest["closure_target"] = "work"
        self.manifest.pop("closure_step_ref")
        self.assignment["context_pack"]["dependency_status"] = "waiting"
        self.assignment["context_pack"]["work_completion_gates"] = [{
            "gate_id": "gate-1",
            "source": "key.work.source",
            "dependency": "key.work.target",
            "scope": {"steps": [], "work_completion": True},
            "result": "waiting",
            "blocking": True,
        }]
        self.manifest["worker_report"]["context_digest"] = digest_json(
            self.assignment["context_pack"]
        )
        self.assertIn("work_completion_dependency_blocking", self.codes(self.validate()))

    def test_work_closure_rejects_blocking_active_step_gate(self):
        self.manifest["closure_target"] = "work"
        self.manifest.pop("closure_step_ref")
        self.assignment["context_pack"]["dependency_status"] = "waiting"
        self.assignment["context_pack"]["active_step_gates"] = [{
            "gate_id": "active-step-block",
            "source": "key.work.source",
            "dependency": "key.work.target",
            "scope": {"steps": ["R010/S01"], "work_completion": False},
            "result": "waiting",
            "blocking": True,
        }]
        self.manifest["worker_report"]["context_digest"] = digest_json(
            self.assignment["context_pack"]
        )
        result = self.validate()
        self.assertEqual("fail", result["status"])
        self.assertIn("active_step_dependency_blocking", self.codes(result))

    def test_unknown_authority_field_fails_closed(self):
        self.manifest["worker_report"]["trusted"] = True
        self.assertIn("unknown_field", self.codes(self.validate()))

    def test_path_traversal_and_symlink_escape_fail_closed(self):
        self.assignment["scope"]["allowed_edit_scope"] = ["../outside"]
        result_codes = self.codes(self.validate())
        self.assertIn("path_invalid", result_codes)

        self.assignment["scope"] = deepcopy(
            self.assignment["context_pack"]["scope_boundaries"]
        )
        outside = self.base / "outside"
        outside.mkdir()
        (self.root / "src" / "escape").symlink_to(outside, target_is_directory=True)
        self.assertIn("symlink_scope_escape", self.codes(self.validate()))

    def test_exact_and_descendant_scope_cannot_cross_escaping_symlink(self):
        outside_directory = self.base / "outside-directory"
        outside_directory.mkdir()
        outside_file = self.base / "outside-file.txt"
        outside_file.write_text("outside\n", encoding="utf-8")
        directory_link = self.root / "src" / "escape-directory"
        file_link = self.root / "src" / "escape-file"
        directory_link.symlink_to(outside_directory, target_is_directory=True)
        file_link.symlink_to(outside_file)
        self.assignment["baseline_snapshot"] = [
            {"path": path, "digest": digest}
            for path, digest in repository_snapshot(self.root).items()
        ]

        for selector in (
            "src/escape-file",
            "src/escape-directory/value.txt",
        ):
            with self.subTest(selector=selector):
                for scope in (
                    self.assignment["scope"],
                    self.assignment["context_pack"]["scope_boundaries"],
                ):
                    scope["allowed_edit_scope"] = [selector]
                self.manifest["worker_report"]["context_digest"] = digest_json(
                    self.assignment["context_pack"]
                )
                self.assertIn("symlink_scope_escape", self.codes(self.validate()))

    def test_missing_or_non_directory_root_is_execution_error(self):
        for root in (self.base / "missing", self.base / "root-file"):
            if root.name == "root-file":
                root.write_text("not a repository\n", encoding="utf-8")
            with self.subTest(root=root):
                result = validate_manifest(
                    self.manifest,
                    root=root,
                    assignment=self.assignment,
                    assignment_digest=self.assignment_digest,
                    evidence_root=self.evidence,
                )
                self.assertEqual("error", result["status"])
                self.assertIn("repository_root_unavailable", self.codes(result))

    def test_misfiled_work_gate_and_missing_gate_evidence_fail_closed(self):
        self.manifest["closure_target"] = "work"
        self.manifest.pop("closure_step_ref")
        self.assignment["context_pack"]["dependency_status"] = "waiting"
        self.assignment["context_pack"]["active_step_gates"] = [{
            "gate_id": "hidden-work-gate",
            "source": "key.work.source",
            "dependency": "key.work.target",
            "scope": {"steps": [], "work_completion": True},
            "result": "waiting",
            "blocking": True,
        }]
        self.manifest["worker_report"]["context_digest"] = digest_json(
            self.assignment["context_pack"]
        )
        self.assertIn("dependency_gate_group_mismatch", self.codes(self.validate()))

        self.assignment["context_pack"]["active_step_gates"] = []
        self.manifest["worker_report"]["context_digest"] = digest_json(
            self.assignment["context_pack"]
        )
        self.assertIn("dependency_status_gate_mismatch", self.codes(self.validate()))

    def test_malformed_injected_skill_returns_diagnostics_without_crashing(self):
        self.assignment["injected_skills"].append({})
        result = self.validate()
        self.assertEqual("fail", result["status"])
        self.assertIn("injected_skill_invalid", self.codes(result))

    def test_assignment_digest_requires_canonical_host_digest(self):
        result = validate_manifest(
            self.manifest,
            root=self.root,
            assignment=self.assignment,
            assignment_digest="not-a-digest",
            evidence_root=self.evidence,
        )
        self.assertEqual("fail", result["status"])
        self.assertIn("assignment_digest_invalid", self.codes(result))

    def test_direct_api_normalizes_path_strings(self):
        result = validate_manifest(
            self.manifest,
            root=str(self.root),
            assignment=self.assignment,
            assignment_digest=self.assignment_digest,
            evidence_root=str(self.evidence),
        )
        self.assert_historical_v2_valid(result)

    def test_direct_api_malformed_runtime_context_returns_error_envelope(self):
        cases = (
            {"assignment": []},
            {"root": object()},
            {"evidence_root": object()},
            {"linker_runner": object()},
            {"author_runner": object()},
        )
        for overrides in cases:
            arguments = {
                "root": self.root,
                "assignment": self.assignment,
                "assignment_digest": self.assignment_digest,
                "evidence_root": self.evidence,
            }
            arguments.update(overrides)
            with self.subTest(field=next(iter(overrides))):
                result = validate_manifest(self.manifest, **arguments)
                self.assertEqual("error", result["status"])
                self.assertIn("v2_runtime_context_invalid", self.codes(result))

    def test_v2_runner_overrides_fail_closed(self):
        for field in ("linker_runner", "author_runner"):
            with self.subTest(field=field):
                result = self.validate(**{field: self.evidence / "forged-runner.py"})
                self.assertEqual("error", result["status"])
                self.assertIn("v2_runner_override_forbidden", self.codes(result))

    def test_runner_envelopes_are_exact_by_package_contract(self):
        base = {
            "schema_version": 1,
            "status": "pass",
            "diagnostics": [],
            "summary": {"errors": 0, "warnings": 0},
        }
        invalid = (
            dict(base, unknown=True),
            dict(base, schema_version=True),
            dict(base, summary={"errors": False, "warnings": 0}),
            dict(base, diagnostics=[{
                "severity": "warning", "code": "warning", "message": "warning",
                "detail": "forged",
            }]),
        )
        for payload in invalid:
            with self.subTest(payload=payload):
                self.assertFalse(_valid_runner_envelope(payload, 0, "linker"))
                self.assertFalse(_valid_runner_envelope(payload, 0, "author"))

        coverage = {
            "mode": "full",
            "complete": True,
            "path_digest": "sha256:" + "1" * 64,
            "discovered_sources": ["source.md"],
            "parsed_sources": ["source.md"],
            "omitted_sources": [],
            "declared_only_sources": [],
            "skipped_sources": [],
            "counts": {
                "discovered": 1,
                "parsed": 1,
                "omitted": 0,
                "declared_only": 0,
                "skipped": 0,
            },
        }
        linker = dict(base, coverage=coverage)
        self.assertTrue(_valid_runner_envelope(linker, 0, "linker"))
        self.assertFalse(_valid_runner_envelope(linker, 0, "author"))

        malformed = deepcopy(coverage)
        malformed["counts"]["parsed"] = 0
        self.assertFalse(_valid_runner_envelope(
            dict(base, coverage=malformed), 0, "linker"
        ))

    def test_step_gate_binds_to_assignment_and_concrete_closure_step(self):
        gate = {
            "gate_id": "step-gate",
            "source": "key.work.source",
            "dependency": "key.work.target",
            "scope": {"steps": ["R011/S01"], "work_completion": False},
            "result": "waiting",
            "blocking": True,
        }
        self.assignment["context_pack"]["dependency_status"] = "waiting"
        self.assignment["context_pack"]["active_step_gates"] = [gate]
        self.manifest["worker_report"]["context_digest"] = digest_json(
            self.assignment["context_pack"]
        )
        codes = self.codes(self.validate())
        self.assertIn("dependency_gate_step_scope_invalid", codes)
        self.assertIn("dependency_gate_closure_step_mismatch", codes)

        gate["scope"] = {"steps": [], "work_completion": True}
        self.assignment["context_pack"]["work_completion_gates"] = [deepcopy(gate)]
        self.manifest["worker_report"]["context_digest"] = digest_json(
            self.assignment["context_pack"]
        )
        self.assertIn("dependency_gate_duplicate", self.codes(self.validate()))

    def test_missing_classification_is_execution_error(self):
        (self.evidence / "classification.json").unlink()
        result = self.validate()
        self.assertEqual("error", result["status"])
        self.assertIn("evidence_unreadable", self.codes(result))

    def test_evidence_root_must_be_disjoint_from_repository(self):
        (self.base / "classification.json").write_bytes(
            (self.evidence / "classification.json").read_bytes()
        )
        result = validate_manifest(
            self.manifest,
            root=self.root,
            assignment=self.assignment,
            assignment_digest=self.assignment_digest,
            evidence_root=self.base,
        )
        self.assertEqual("fail", result["status"])
        self.assertIn("evidence_root_contains_repository", self.codes(result))

    def test_added_and_deleted_files_are_derived_from_snapshot(self):
        source = self.root / "src" / "example.py"
        source.unlink()
        added = self.root / "src" / "added.py"
        added.write_text("added\n", encoding="utf-8")
        self.manifest["worker_report"]["changed_files"] = [
            "src/added.py",
            "src/example.py",
        ]
        self.manifest["worker_report"]["artifact_deltas"] = [
            {
                "kind": "artifact_delta",
                "source_surface": "src/added.py",
                "change_kind": "added",
                "changed_locators": [{"path": "src/added.py", "symbol": "added"}],
                "semantic_summary": "Add a bounded source.",
                "baseline_digest": "absent",
                "resulting_digest": file_digest(added),
                "graph_relevant": False,
            },
            {
                "kind": "artifact_delta",
                "source_surface": "src/example.py",
                "change_kind": "deleted",
                "changed_locators": [{
                    "path": "src/example.py",
                    "symbol": "Example",
                }],
                "semantic_summary": "Remove a bounded source.",
                "baseline_digest": self.assignment["baseline_snapshot"][0]["digest"],
                "resulting_digest": "absent",
                "graph_relevant": False,
            },
        ]
        self.write_classification()
        self.assert_historical_v2_valid(self.validate())

    def test_required_graph_sync_executes_runner_and_binds_transaction(self):
        self.record_modified_source()
        delta = self.manifest["worker_report"]["artifact_deltas"][0]
        graph_manifest = {
            "schema_version": 1,
            "sources": [],
            "transaction": {
                "schema_version": 2,
                "transaction_id": "tx-R010",
                "state": "verified",
                "input_deltas": [{
                    "kind": delta["kind"],
                    "source_surface": delta["source_surface"],
                    "changed_locators": delta["changed_locators"],
                    "semantic_summary": delta["semantic_summary"],
                    "baseline_digest": delta["baseline_digest"],
                    "graph_relevant": delta["graph_relevant"],
                }],
            },
        }
        graph_path = self.evidence / "graph.json"
        graph_path.write_bytes(json_bytes(graph_manifest))
        runner_payload = {
            "schema_version": 1,
            "status": "pass",
            "diagnostics": [],
            "summary": {"errors": 0, "warnings": 0},
        }
        self.manifest["keystone_closure"]["graph_sync"] = {
            "disposition": "required",
            "state": "verified",
            "reason": "Graph mutation was reconstructed.",
            "validation_manifest_path": "graph.json",
            "validation_manifest_digest": file_digest(graph_path),
            "transaction_id": "tx-R010",
            "delta_set_digest": self.delta_digest(),
            "envelope_digest": digest_json(runner_payload),
        }

        with mock.patch.object(
            closure_v2.subprocess, "run",
            return_value=self.runner_process(runner_payload, 0),
        ) as run:
            self.assert_historical_v2_valid(self.validate())
            command = run.call_args.args[0]
            self.assertEqual(
                closure_v2.package_runner_paths()[0], Path(command[1]).resolve()
            )
            graph_manifest["transaction"]["schema_version"] = 1
            graph_path.write_bytes(json_bytes(graph_manifest))
            self.manifest["keystone_closure"]["graph_sync"][
                "validation_manifest_digest"
            ] = file_digest(graph_path)
            self.assertIn(
                "graph_transaction_schema_not_authoritative",
                self.codes(self.validate()),
            )
            graph_manifest["transaction"]["schema_version"] = 2
            graph_path.write_bytes(json_bytes(graph_manifest))
            self.manifest["keystone_closure"]["graph_sync"][
                "validation_manifest_digest"
            ] = file_digest(graph_path)
            self.manifest["keystone_closure"]["graph_sync"]["transaction_id"] = "forged"
            self.assertIn("graph_transaction_mismatch", self.codes(self.validate()))

        error_payload = {
            "schema_version": 1,
            "status": "error",
            "diagnostics": [{
                "severity": "error",
                "code": "validator_execution_failed",
                "message": "runner failed",
            }],
            "summary": {"errors": 1, "warnings": 0},
        }
        self.manifest["keystone_closure"]["graph_sync"]["transaction_id"] = "tx-R010"
        self.manifest["keystone_closure"]["graph_sync"][
            "envelope_digest"
        ] = digest_json(error_payload)
        with mock.patch.object(
            closure_v2.subprocess, "run",
            return_value=self.runner_process(error_payload, 2),
        ):
            execution_error = self.validate()
        self.assertEqual("error", execution_error["status"])
        self.assertIn("runner_reported_error", self.codes(execution_error))

    def test_post_acceptance_executes_author_runner_and_binds_acceptance(self):
        acceptance_ref = "R010/S01/main-acceptance"
        finalization_manifest = {
            "schema_version": 5,
            "acceptance_ref": acceptance_ref,
            "steps": [{"ref": "R010/S01"}],
            "accepted_steps": ["R010/S01"],
            "finalization": {"required": True, "state": "complete"},
        }
        finalization_path = self.evidence / "finalization.json"
        finalization_path.write_bytes(json_bytes(finalization_manifest))
        runner_payload = {
            "schema_version": 1,
            "status": "pass",
            "diagnostics": [],
            "summary": {"errors": 0, "warnings": 0},
        }
        self.manifest["closure_phase"] = "post_acceptance"
        self.manifest["keystone_closure"].update({
            "acceptance_ref": acceptance_ref,
            "acceptance_evidence": ["Main accepted R010/S01"],
            "accepted_steps": ["R010/S01"],
            "finalization": {
                "state": "complete",
                "acceptance_ref": acceptance_ref,
                "evidence": ["Author runner passed"],
                "manifest_path": "finalization.json",
                "manifest_digest": file_digest(finalization_path),
                "envelope_digest": digest_json(runner_payload),
                "runner_status": "pass",
            },
        })
        self.manifest["coordinator_review"].update({
            "decision": "closure_complete",
            "main_acceptance_allowed": False,
        })

        with mock.patch.object(
            closure_v2.subprocess, "run",
            return_value=self.runner_process(runner_payload, 0),
        ) as run:
            self.assert_historical_v2_valid(self.validate())
            command = run.call_args.args[0]
            self.assertEqual(
                closure_v2.package_runner_paths()[1], Path(command[1]).resolve()
            )
            finalization_manifest["schema_version"] = 4
            finalization_path.write_bytes(json_bytes(finalization_manifest))
            self.manifest["keystone_closure"]["finalization"][
                "manifest_digest"
            ] = file_digest(finalization_path)
            self.assertIn(
                "author_manifest_schema_invalid", self.codes(self.validate())
            )

            finalization_manifest["schema_version"] = 5
            finalization_path.write_bytes(json_bytes(finalization_manifest))
            self.manifest["keystone_closure"]["finalization"][
                "manifest_digest"
            ] = file_digest(finalization_path)
            self.manifest["keystone_closure"]["finalization"]["acceptance_ref"] = "forged"
            self.assertIn("acceptance_ref_mismatch", self.codes(self.validate()))

            self.manifest["keystone_closure"]["finalization"]["acceptance_ref"] = acceptance_ref
            self.manifest["keystone_closure"]["accepted_steps"] = [{}]
            finalization_manifest["steps"] = [{"ref": {}}]
            finalization_manifest["accepted_steps"] = [{}]
            finalization_path.write_bytes(json_bytes(finalization_manifest))
            self.manifest["keystone_closure"]["finalization"][
                "manifest_digest"
            ] = file_digest(finalization_path)
            malformed = self.validate()
        self.assertEqual("fail", malformed["status"])
        self.assertIn("accepted_steps_mismatch", self.codes(malformed))

    def test_v1_readiness_decisions_are_non_authoritative(self):
        legacy = {
            "schema_version": 1,
            "coordinator_review": {"decision": "accept_candidate"},
        }
        self.assertIn("legacy_schema_not_authoritative", self.codes(validate_manifest(legacy)))

    def test_cli_requires_root_and_assignment_for_v2(self):
        manifest_path = self.evidence / "closure.json"
        assignment_path = self.evidence / "assignment.json"
        manifest_path.write_bytes(json_bytes(self.manifest))
        assignment_path.write_bytes(json_bytes(self.assignment))
        process = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "validate_closure.py"),
                "--manifest",
                str(manifest_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, process.returncode)
        self.assertIn("v2_runtime_context_missing", self.codes(json.loads(process.stdout)))

    def test_cli_reads_complete_v2_context_but_denies_authority(self):
        manifest_path = self.evidence / "closure.json"
        assignment_path = self.evidence / "assignment.json"
        manifest_path.write_bytes(json_bytes(self.manifest))
        assignment_path.write_bytes(json_bytes(self.assignment))
        process = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "validate_closure.py"),
                "--root",
                str(self.root),
                "--assignment",
                str(assignment_path),
                "--manifest",
                str(manifest_path),
                "--evidence-root",
                str(self.evidence),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(1, process.returncode, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual("fail", payload["status"])
        self.assertEqual(
            {"legacy_schema_not_authoritative"}, self.codes(payload)
        )

    def test_cli_runner_overrides_fail_closed(self):
        manifest_path = self.evidence / "closure.json"
        assignment_path = self.evidence / "assignment.json"
        manifest_path.write_bytes(json_bytes(self.manifest))
        assignment_path.write_bytes(json_bytes(self.assignment))
        for flag in ("--linker-runner", "--author-runner"):
            with self.subTest(flag=flag):
                process = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPTS / "validate_closure.py"),
                        "--root", str(self.root),
                        "--assignment", str(assignment_path),
                        "--manifest", str(manifest_path),
                        "--evidence-root", str(self.evidence),
                        flag, str(self.evidence / "forged-runner.py"),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(process.stdout)
                self.assertEqual(2, process.returncode, process.stdout)
                self.assertIn("v2_runner_override_forbidden", self.codes(payload))

    def test_cli_rejects_duplicate_manifest_and_assignment_keys(self):
        command = [
            sys.executable,
            str(SCRIPTS / "validate_closure.py"),
            "--root", str(self.root),
            "--evidence-root", str(self.evidence),
        ]
        manifest_path = self.evidence / "closure.json"
        assignment_path = self.evidence / "assignment.json"
        assignment_path.write_bytes(json_bytes(self.assignment))
        raw_manifest = json_bytes(self.manifest).decode("utf-8").replace(
            '"schema_version":2', '"schema_version":999,"schema_version":2', 1
        )
        manifest_path.write_text(raw_manifest, encoding="utf-8")
        process = subprocess.run(
            command + [
                "--assignment", str(assignment_path),
                "--manifest", str(manifest_path),
            ],
            check=False, capture_output=True, text=True,
        )
        payload = json.loads(process.stdout)
        self.assertEqual(2, process.returncode)
        self.assertIn("manifest_json_invalid", self.codes(payload))

        manifest_path.write_bytes(json_bytes(self.manifest))
        raw_assignment = json_bytes(self.assignment).decode("utf-8").replace(
            '"schema_version":2', '"schema_version":999,"schema_version":2', 1
        )
        assignment_path.write_text(raw_assignment, encoding="utf-8")
        process = subprocess.run(
            command + [
                "--assignment", str(assignment_path),
                "--manifest", str(manifest_path),
            ],
            check=False, capture_output=True, text=True,
        )
        payload = json.loads(process.stdout)
        self.assertEqual(2, process.returncode)
        self.assertIn("assignment_json_invalid", self.codes(payload))

    def test_cli_rejects_recursive_duplicate_assignment_key(self):
        manifest_path = self.evidence / "closure.json"
        assignment_path = self.evidence / "assignment.json"
        manifest_path.write_bytes(json_bytes(self.manifest))
        raw_assignment = json_bytes(self.assignment).decode("utf-8").replace(
            '"round_ref":"R010"',
            '"round_ref":"forged","round_ref":"R010"',
            1,
        )
        assignment_path.write_text(raw_assignment, encoding="utf-8")
        process = subprocess.run(
            [
                sys.executable, str(SCRIPTS / "validate_closure.py"),
                "--root", str(self.root),
                "--assignment", str(assignment_path),
                "--manifest", str(manifest_path),
                "--evidence-root", str(self.evidence),
            ],
            check=False, capture_output=True, text=True,
        )
        payload = json.loads(process.stdout)
        self.assertEqual(2, process.returncode)
        self.assertIn("assignment_json_invalid", self.codes(payload))

    def test_schema_versions_reject_boolean_values(self):
        self.manifest["schema_version"] = True
        self.assertIn("schema_version_invalid", self.codes(self.validate()))

        self.manifest["schema_version"] = 2
        self.assignment["schema_version"] = True
        self.assertIn("assignment_schema_invalid", self.codes(self.validate()))

    def test_v2_root_envelopes_require_explicit_fields_and_object_types(self):
        del self.manifest["coordinator_review"]
        self.manifest["worker_report"] = []
        codes = self.codes(self.validate())
        self.assertIn("required_field_missing", codes)
        self.assertIn("authoritative_field_type_invalid", codes)

        self.manifest = self.make_manifest()
        self.write_classification()
        self.assignment["context_pack"] = []
        self.assertIn(
            "authoritative_field_type_invalid", self.codes(self.validate())
        )

    def test_cli_missing_root_returns_error_envelope_and_exit_two(self):
        manifest_path = self.evidence / "closure.json"
        assignment_path = self.evidence / "assignment.json"
        manifest_path.write_bytes(json_bytes(self.manifest))
        assignment_path.write_bytes(json_bytes(self.assignment))
        process = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "validate_closure.py"),
                "--root",
                str(self.base / "missing"),
                "--assignment",
                str(assignment_path),
                "--manifest",
                str(manifest_path),
                "--evidence-root",
                str(self.evidence),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        payload = json.loads(process.stdout)
        self.assertEqual(2, process.returncode, payload)
        self.assertEqual("error", payload["status"])
        self.assertIn("repository_root_unavailable", self.codes(payload))

    def test_evidence_digest_parse_and_runner_use_one_captured_byte_generation(self):
        evidence_path = self.evidence / "stable-manifest.json"
        original = json_bytes({"schema_version": 1, "value": "captured"})
        replacement = json_bytes({"schema_version": 1, "value": "replaced"})
        evidence_path.write_bytes(original)
        diagnostics = []

        def digest_then_replace(raw):
            evidence_path.write_bytes(replacement)
            return digest_bytes(raw)

        with mock.patch.object(
            closure_v2,
            "digest_bytes",
            side_effect=digest_then_replace,
        ):
            _, payload, captured = closure_v2._read_evidence_json(
                self.evidence,
                "stable-manifest.json",
                digest_bytes(original),
                "evidence",
                diagnostics,
            )

        self.assertEqual([], diagnostics)
        self.assertEqual("captured", payload["value"])
        self.assertEqual(original, captured)

        runner_inputs = []

        def inspect_runner(command, *_args):
            runner_inputs.append(Path(command[-1]).read_bytes())
            return {"status": "pass"}

        with mock.patch.object(
            closure_v2,
            "_run_evidence",
            side_effect=inspect_runner,
        ):
            closure_v2._run_captured_manifest(
                Path("runner.py"),
                self.root,
                captured,
                1.0,
                digest_json({"status": "pass"}),
                "evidence.envelope_digest",
                diagnostics,
                "author",
            )

        self.assertEqual([original], runner_inputs)

    def test_v2_captured_manifest_runner_has_no_extra_arguments_by_default(self):
        commands = []

        def capture_command(command, *_args):
            commands.append(command)
            return {"status": "pass"}

        with mock.patch.object(
            closure_v2,
            "_run_evidence",
            side_effect=capture_command,
        ):
            closure_v2._run_captured_manifest(
                Path("runner.py"),
                self.root,
                json_bytes({"schema_version": 1}),
                1.0,
                digest_json({"status": "pass"}),
                "evidence.envelope_digest",
                [],
                "author",
            )

        self.assertEqual(1, len(commands))
        self.assertEqual(6, len(commands[0]))
        self.assertEqual(
            [
                sys.executable,
                "runner.py",
                "--root",
                str(self.root),
                "--manifest",
            ],
            commands[0][:-1],
        )


if __name__ == "__main__":
    unittest.main()
