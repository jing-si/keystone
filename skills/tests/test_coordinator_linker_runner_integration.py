import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).parents[2]
COORDINATOR_SCRIPTS = (
    REPOSITORY_ROOT / "skills" / "keystone-coordinator" / "scripts"
)
sys.path.insert(0, str(COORDINATOR_SCRIPTS))

from closure_actual_state import (  # noqa: E402
    changed_paths_v3,
    parse_repository_snapshot_v3,
)
from closure_v3 import assignment_subject_digest  # noqa: E402

COORDINATOR_RUNNER = (
    REPOSITORY_ROOT / "skills" / "keystone-coordinator" / "scripts"
    / "validate_closure.py"
)
CAPTURE_RUNNER = COORDINATOR_SCRIPTS / "capture_assignment_snapshot.py"


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


class CoordinatorLinkerRunnerIntegrationTest(unittest.TestCase):
    def test_required_graph_sync_runs_package_linker_with_canonical_locators(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            evidence_root = base / "evidence"
            source = root / "src" / "example.py"
            source.parent.mkdir(parents=True)
            (root / "00_docs").mkdir()
            evidence_root.mkdir()
            capture_key = base / "capture-authority.key"
            capture_key.write_bytes(b"coordinator-capture-authority-key")
            capture_key.chmod(0o600)
            capture_key_digest = file_digest(capture_key)
            baseline = "before\n"
            source.write_text(baseline, encoding="utf-8")
            baseline_digest = file_digest(source)
            policy = {
                "schema_version": 3,
                "include_paths": ["."],
                "exclusions": [],
                "entry_budget": 100,
            }
            policy_path = evidence_root / "snapshot-policy.json"
            policy_path.write_bytes(json_bytes(policy))
            assignment_id = "R010-S02-linker-integration"
            context = self._context()
            context_digest = digest_json(context)
            subject_digest = assignment_subject_digest(
                self._assignment(policy, {}, {}, context)
            )
            assignment_capture = self._capture_phase(
                root,
                evidence_root,
                policy_path,
                "assignment",
                "absent",
                "absent",
                "assignment-capture.json",
                assignment_id,
                subject_digest,
                context_digest,
                capture_key,
                capture_key_digest,
            )
            assignment_snapshot = parse_repository_snapshot_v3(
                assignment_capture["snapshot"]
            )
            assignment = self._assignment(
                policy,
                assignment_snapshot.wire(),
                assignment_capture["capture_evidence"],
                context,
            )
            assignment_path = evidence_root / "assignment.json"
            assignment_path.write_bytes(json_bytes(assignment))
            assignment_digest = file_digest(assignment_path)

            after = (
                "# keystone: id=key.code.example kind=output_artifact "
                "artifact_kind=code locator.symbol=run\n\n"
                "def run():\n"
                "    return 'after'\n"
            )
            source.write_text(after, encoding="utf-8")
            resulting_digest = file_digest(source)
            worker_capture = self._capture_phase(
                root,
                evidence_root,
                policy_path,
                "worker",
                assignment_snapshot.snapshot_digest,
                assignment_capture["capture_evidence"]["digest"],
                "worker-capture.json",
                assignment_id,
                subject_digest,
                context_digest,
                capture_key,
                capture_key_digest,
            )
            worker_snapshot = parse_repository_snapshot_v3(worker_capture["snapshot"])
            worker_changes = changed_paths_v3(assignment_snapshot, worker_snapshot)
            pre_capture = self._capture_phase(
                root,
                evidence_root,
                policy_path,
                "pre_acceptance_closure",
                worker_snapshot.snapshot_digest,
                worker_capture["capture_evidence"]["digest"],
                "pre-capture.json",
                assignment_id,
                subject_digest,
                context_digest,
                capture_key,
                capture_key_digest,
            )
            pre_snapshot = parse_repository_snapshot_v3(pre_capture["snapshot"])
            locator = {"path": "src/example.py", "symbol": "run"}
            delta = {
                "kind": "artifact_delta",
                "source_surface": "src/example.py",
                "change_kind": "modified",
                "changed_locators": [locator],
                "semantic_summary": "Declare the changed implementation anchor.",
                "baseline_digest": baseline_digest,
                "resulting_digest": resulting_digest,
                "graph_relevant": True,
            }
            graph_manifest = self._graph_manifest(
                baseline, after, baseline_digest, resulting_digest, locator, delta
            )
            graph_path = evidence_root / "graph-validation.json"
            graph_path.write_bytes(json_bytes(graph_manifest))
            runner_payload = {
                "schema_version": 1,
                "status": "pass",
                "diagnostics": [],
                "summary": {"errors": 0, "warnings": 0},
            }
            manifest = self._closure_manifest(
                assignment,
                assignment_digest,
                delta,
                assignment_snapshot.snapshot_digest,
                worker_snapshot.wire(),
                worker_capture["capture_evidence"],
                worker_changes,
                pre_snapshot.wire(),
                pre_capture["capture_evidence"],
                file_digest(graph_path),
                digest_json(runner_payload),
            )
            manifest_path = evidence_root / "closure.json"
            manifest_path.write_bytes(json_bytes(manifest))

            process = subprocess.run(
                [
                    sys.executable,
                    str(COORDINATOR_RUNNER),
                    "--root",
                    str(root),
                    "--assignment",
                    str(assignment_path),
                    "--manifest",
                    str(manifest_path),
                    "--evidence-root",
                    str(evidence_root),
                    "--capture-authority-key",
                    str(capture_key),
                    "--trusted-capture-authority-key-sha256",
                    capture_key_digest,
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            result = (
                json.loads(process.stdout)
                if process.stdout.strip()
                else {"stderr": process.stderr}
            )

        self.assertEqual(0, process.returncode, process.stderr or result)
        self.assertEqual("pass", result["status"], result)
        self.assertEqual([], result["diagnostics"])

    @staticmethod
    def _capture_phase(
        root, evidence_root, policy_path, phase_id, parent_digest,
        parent_evidence_digest, evidence_path, assignment_id,
        assignment_subject_digest_value, context_digest,
        capture_key, capture_key_digest,
    ):
        process = subprocess.run(
            [
                sys.executable,
                str(CAPTURE_RUNNER),
                "--root",
                str(root),
                "--policy",
                str(policy_path),
                "--phase-id",
                phase_id,
                "--parent-snapshot-digest",
                parent_digest,
                "--parent-evidence-digest",
                parent_evidence_digest,
                "--assignment-id",
                assignment_id,
                "--assignment-subject-digest",
                assignment_subject_digest_value,
                "--context-digest",
                context_digest,
                "--evidence-root",
                str(evidence_root),
                "--capture-evidence-path",
                evidence_path,
                "--capture-authority-key",
                str(capture_key),
                "--trusted-capture-authority-key-sha256",
                capture_key_digest,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        payload = json.loads(process.stdout)
        if process.returncode != 0:
            raise AssertionError(process.stderr or payload)
        return payload

    @staticmethod
    def _context():
        scope = {
            "read_scope": ["."],
            "allowed_edit_scope": ["src"],
            "excluded_scope": ["secret"],
        }
        return {
            "main_context_checkpoint": "R010 scope and acceptance remain with Main.",
            "work_context": {
                "round_ref": "R010",
                "work_ref": "R010/production-control-plane-hardening",
                "step_refs": ["R010/S02"],
            },
            "source_documents": ["00_docs/works/r010/key-work.md"],
            "applicable_standards": ["00_docs/convention.md"],
            "accepted_decisions": [],
            "completion_criteria": ["Package-owned Linker validates actual deltas."],
            "scope_boundaries": deepcopy(scope),
            "forbidden_changes": ["Do not edit documents."],
            "verification_expectations": ["Linker runner passes."],
            "artifact_context": {"status": "ready", "evidence": ["Linker context"]},
            "reader_context": {"status": "ready", "evidence": ["Reader context"]},
            "author_context": {
                "status": "not_applicable",
                "evidence": ["No document change"],
            },
            "dependency_status": "satisfied",
            "active_step_gates": [],
            "work_completion_gates": [],
        }

    @staticmethod
    def _assignment(policy, baseline_snapshot, capture_evidence, context):
        scope = deepcopy(context["scope_boundaries"])
        return {
            "schema_version": 3,
            "assignment_id": "R010-S02-linker-integration",
            "execution_mode": "direct_execution",
            "purpose": "implement",
            "authority": "bounded_edit",
            "goal": "Verify the Coordinator to Linker authority chain.",
            "context_pack": deepcopy(context),
            "injected_skills": [{
                "skill_id": "keystone-default-bounded-worker",
                "mode": "default",
            }],
            "scope": scope,
            "document_root": "00_docs",
            "snapshot_policy": policy,
            "assignment_phase": {
                "phase_id": "assignment",
                "actor": "coordinator",
                "authority": "verification",
                "result_snapshot": baseline_snapshot,
                "capture_evidence": capture_evidence,
            },
            "phase_authorities": {
                "worker": {
                    "authority": "bounded_edit",
                    "allowed_edit_scope": ["src"],
                    "excluded_scope": ["secret"],
                },
                "author": {
                    "authority": "document_edit",
                    "allowed_edit_scope": ["00_docs"],
                    "excluded_scope": [],
                },
                "repository_owner": {
                    "authority": "bounded_edit",
                    "allowed_edit_scope": ["src"],
                    "excluded_scope": ["secret"],
                },
                "linker": {
                    "authority": "read_only",
                    "allowed_edit_scope": [],
                    "excluded_scope": [],
                },
            },
        }

    @staticmethod
    def _graph_manifest(
        baseline, after, baseline_digest, resulting_digest, locator, delta
    ):
        node = {
            "id": "key.code.example",
            "kind": "output_artifact",
            "artifact_kind": "code",
            "locator": locator,
            "lifecycle": "active",
            "lifecycle_domain": "artifact",
            "provenance": {
                "produced_from": [],
                "governed_by": [],
                "surface": "code_anchor",
                "locator": locator,
            },
        }
        empty = {"schema_version": 2, "nodes": [], "relations": []}
        result = {"schema_version": 2, "nodes": [node], "relations": []}
        patch = {
            "patch_id": "patch-code-anchor",
            "owner": "coordinator",
            "surface": "code_anchor",
            "target_path": "src/example.py",
            "baseline_digest": baseline_digest,
            "baseline_content": baseline,
            "exact_patch": after,
            "patch_format": "full_replacement",
            "patch_body": after,
            "expected_after_digest": resulting_digest,
            "required": True,
        }
        return {
            "schema_version": 1,
            "sources": ["src/example.py"],
            "transaction": {
                "schema_version": 2,
                "transaction_id": "tx-R010-coordinator-linker",
                "scope_ref": "R010/S02",
                "state": "verified",
                "input_deltas": [{
                    key: value for key, value in delta.items()
                    if key not in {"change_kind", "resulting_digest"}
                }],
                "canonical_mutations": [{
                    "operation": "add",
                    "entity": "node",
                    "before": None,
                    "after": node,
                    "evidence": "declared",
                    "direct_relation_reason": None,
                }],
                "surface_patches": [patch],
                "attestations": [{
                    "patch_id": patch["patch_id"],
                    "owner": patch["owner"],
                    "decision": "confirm",
                    "evidence": "Repository surface owner confirmed exact bytes.",
                }],
                "apply_results": [{
                    "patch_id": patch["patch_id"],
                    "result": "applied",
                    "resulting_digest": resulting_digest,
                    "evidence": "Current source bytes match the planned patch.",
                }],
                "reconstruction": {"baseline": empty, "result": result},
                "mechanical_validation": {
                    "schema_version": 1,
                    "status": "pass",
                    "diagnostics": [],
                    "summary": {"errors": 0, "warnings": 0},
                },
                "coverage_debt": [],
            },
        }

    @staticmethod
    def _closure_manifest(
        assignment, assignment_digest, delta, assignment_snapshot_digest,
        worker_snapshot, worker_capture_evidence, worker_changes,
        pre_snapshot, pre_capture_evidence, graph_digest, envelope_digest,
    ):
        worker_authority = assignment["phase_authorities"]["worker"]
        linker_authority = assignment["phase_authorities"]["linker"]
        return {
            "schema_version": 3,
            "closure_stage": "pre_acceptance",
            "closure_target": "step",
            "closure_step_ref": "R010/S02",
            "worker_report": {
                "assignment_id": assignment["assignment_id"],
                "assignment_digest": assignment_digest,
                "context_digest": digest_json(assignment["context_pack"]),
                "execution_mode": assignment["execution_mode"],
                "status": "DONE",
                "purpose": assignment["purpose"],
                "authority": assignment["authority"],
                "goal": assignment["goal"],
                "skill_usage": [{
                    "skill_id": "keystone-default-bounded-worker",
                    "mode": "default",
                    "outputs_used": ["bounded implementation"],
                    "limits_hit": [],
                }],
                "changed_files": ["src/example.py"],
                "artifact_deltas": [delta],
                "scope_check": "within_scope",
                "forbidden_change_check": "none",
                "verification": {
                    "status": "pass",
                    "evidence": ["Actual package Linker runner passed."],
                },
            },
            "worker_phase": {
                "phase_id": "worker",
                "baseline_snapshot_digest": assignment_snapshot_digest,
                "result_snapshot": worker_snapshot,
                "capture_evidence": worker_capture_evidence,
                "actor_delta": {
                    "actor": "worker",
                    "authority": worker_authority["authority"],
                    "allowed_edit_scope": worker_authority["allowed_edit_scope"],
                    "excluded_scope": worker_authority["excluded_scope"],
                    "changed_paths": worker_changes,
                    "artifact_deltas": [delta],
                },
            },
            "pre_acceptance_closure_phase": {
                "phase_id": "pre_acceptance_closure",
                "baseline_snapshot_digest": worker_snapshot["snapshot_digest"],
                "result_snapshot": pre_snapshot,
                "capture_evidence": pre_capture_evidence,
                "actor_deltas": [{
                    "actor": "linker",
                    "authority": linker_authority["authority"],
                    "allowed_edit_scope": linker_authority["allowed_edit_scope"],
                    "excluded_scope": linker_authority["excluded_scope"],
                    "changed_paths": [],
                    "artifact_deltas": [],
                }],
            },
            "post_acceptance_phase": None,
            "keystone_closure": {
                "document_sync": {
                    "disposition": "not_applicable",
                    "state": "not_applicable",
                    "reason": "No document source changed.",
                    "evidence": ["Actual delta is a code anchor."],
                },
                "metadata_sync": {
                    "disposition": "not_applicable",
                    "state": "not_applicable",
                    "reason": "The graph transaction owns the anchor synchronization.",
                    "evidence": ["Canonical mutation records the code anchor."],
                },
                "graph_sync": {
                    "disposition": "required",
                    "state": "verified",
                    "reason": "The implementation anchor changes the canonical graph.",
                    "validation_manifest_path": "graph-validation.json",
                    "validation_manifest_digest": graph_digest,
                    "transaction_id": "tx-R010-coordinator-linker",
                    "delta_set_digest": digest_json([delta]),
                    "envelope_digest": envelope_digest,
                },
                "finalization": {"state": "not_started", "evidence": []},
            },
            "coordinator_review": {
                "assignment_id": assignment["assignment_id"],
                "assignment_digest": assignment_digest,
                "decision": "accept_candidate",
                "main_acceptance_allowed": True,
                "evidence": ["Actual-state and package-runner evidence agree."],
            },
        }


if __name__ == "__main__":
    unittest.main()
