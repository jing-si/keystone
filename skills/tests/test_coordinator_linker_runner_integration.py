import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).parents[2]
COORDINATOR_RUNNER = (
    REPOSITORY_ROOT / "skills" / "keystone-coordinator" / "scripts"
    / "validate_closure.py"
)


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
            base = Path(directory)
            root = base / "repository"
            evidence_root = base / "evidence"
            source = root / "src" / "example.py"
            source.parent.mkdir(parents=True)
            evidence_root.mkdir()
            baseline = "before\n"
            source.write_text(baseline, encoding="utf-8")
            baseline_digest = file_digest(source)
            assignment = self._assignment(baseline_digest)
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
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            result = json.loads(process.stdout)

        self.assertEqual(0, process.returncode, process.stderr or result)
        self.assertEqual("pass", result["status"], result)
        self.assertEqual([], result["diagnostics"])

    @staticmethod
    def _assignment(baseline_digest):
        scope = {
            "read_scope": ["."],
            "allowed_edit_scope": ["src"],
            "excluded_scope": ["secret"],
        }
        context = {
            "main_context_checkpoint": "R010 scope and acceptance remain with Main.",
            "work_context": {
                "round_ref": "R010",
                "work_ref": "R010/production-control-plane-hardening",
                "step_refs": ["R010/S01"],
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
        return {
            "schema_version": 2,
            "assignment_id": "R010-S01-linker-integration",
            "execution_mode": "direct_execution",
            "purpose": "implement",
            "authority": "bounded_edit",
            "goal": "Verify the Coordinator to Linker authority chain.",
            "context_pack": context,
            "injected_skills": [{
                "skill_id": "keystone-default-bounded-worker",
                "mode": "default",
            }],
            "scope": scope,
            "baseline_snapshot": [{
                "path": "src/example.py",
                "digest": baseline_digest,
            }],
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
                "scope_ref": "R010/S01",
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
        assignment, assignment_digest, delta, graph_digest, envelope_digest
    ):
        return {
            "schema_version": 2,
            "closure_phase": "pre_acceptance",
            "closure_target": "step",
            "closure_step_ref": "R010/S01",
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
