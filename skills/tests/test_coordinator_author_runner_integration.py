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


CAPTURE_RUNNER = COORDINATOR_SCRIPTS / "capture_assignment_snapshot.py"
ACCEPTANCE_RUNNER = COORDINATOR_SCRIPTS / "record_acceptance_event.py"
COORDINATOR_RUNNER = COORDINATOR_SCRIPTS / "validate_closure.py"
AUTHOR_RUNNER = (
    REPOSITORY_ROOT / "skills" / "keystone-author" / "scripts"
    / "run_finalization_validation.py"
)
IMPACT_CATEGORIES = (
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


class CoordinatorAuthorRunnerIntegrationTest(unittest.TestCase):
    def test_actual_post_acceptance_chain_runs_package_author_and_coordinator(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            evidence = base / "evidence"
            source = root / "src" / "example.py"
            work_directory = root / "00_docs" / "r010-fixture" / "work"
            accepted_round_directory = root / "00_docs" / "r009-accepted"
            source.parent.mkdir(parents=True)
            work_directory.mkdir(parents=True)
            accepted_round_directory.mkdir(parents=True)
            evidence.mkdir()
            source.write_text("before\n", encoding="utf-8")

            capture_key = base / "coordinator-capture.key"
            main_key = base / "main-acceptance.key"
            capture_key.write_bytes(b"C" * 32)
            main_key.write_bytes(b"M" * 32)
            capture_key.chmod(0o600)
            main_key.chmod(0o600)
            capture_key_digest = file_digest(capture_key)
            main_key_digest = file_digest(main_key)

            policy = {
                "schema_version": 3,
                "include_paths": ["."],
                "exclusions": [],
                "entry_budget": 1000,
            }
            policy_path = evidence / "snapshot-policy.json"
            policy_path.write_bytes(json_bytes(policy))
            context = self.context()
            assignment = self.assignment(context, policy)
            subject_digest = assignment_subject_digest(assignment)
            context_digest = digest_json(context)
            assignment_capture = self.capture_phase(
                root, evidence, policy_path, "assignment", "absent", "absent",
                "assignment-capture.json", assignment["assignment_id"],
                subject_digest, context_digest, capture_key, capture_key_digest,
            )
            assignment_snapshot = parse_repository_snapshot_v3(
                assignment_capture["snapshot"]
            )
            assignment["assignment_phase"] = {
                "phase_id": "assignment",
                "actor": "coordinator",
                "authority": "verification",
                "result_snapshot": assignment_snapshot.wire(),
                "capture_evidence": assignment_capture["capture_evidence"],
            }
            assignment_path = evidence / "assignment.json"
            assignment_path.write_bytes(json_bytes(assignment))
            assignment_digest = file_digest(assignment_path)

            source.write_text("after\n", encoding="utf-8")
            worker_capture = self.capture_phase(
                root, evidence, policy_path, "worker",
                assignment_snapshot.snapshot_digest,
                assignment_capture["capture_evidence"]["digest"],
                "worker-capture.json", assignment["assignment_id"],
                subject_digest, context_digest, capture_key, capture_key_digest,
            )
            worker_snapshot = parse_repository_snapshot_v3(worker_capture["snapshot"])
            worker_changes = changed_paths_v3(assignment_snapshot, worker_snapshot)
            worker_delta = self.delta(
                "artifact_delta",
                "src/example.py",
                assignment_snapshot,
                worker_snapshot,
                graph_relevant=False,
            )

            pre_capture = self.capture_phase(
                root, evidence, policy_path, "pre_acceptance_closure",
                worker_snapshot.snapshot_digest,
                worker_capture["capture_evidence"]["digest"],
                "pre-capture.json", assignment["assignment_id"],
                subject_digest, context_digest, capture_key, capture_key_digest,
            )
            pre_snapshot = parse_repository_snapshot_v3(pre_capture["snapshot"])
            pre_snapshot_path = evidence / "pre-snapshot.json"
            pre_snapshot_path.write_bytes(json_bytes(pre_snapshot.wire()))

            acceptance_ref = "R010/S02/main-acceptance"
            acceptance = self.record_acceptance(
                root, evidence, pre_snapshot, assignment, assignment_digest,
                context_digest, pre_capture["capture_evidence"]["digest"],
                acceptance_ref, main_key, main_key_digest,
            )

            finalization_manifest = self.write_author_sources(
                root, acceptance_ref
            )
            finalization_path = evidence / "author-finalization.json"
            finalization_path.write_bytes(json_bytes(finalization_manifest))
            author_payload = self.run_json([
                sys.executable,
                str(AUTHOR_RUNNER),
                "--root",
                str(root),
                "--manifest",
                str(finalization_path),
            ])
            self.assertEqual("pass", author_payload["status"], author_payload)
            author_envelope_digest = digest_json(author_payload)

            post_capture = self.capture_phase(
                root, evidence, policy_path, "post_acceptance",
                pre_snapshot.snapshot_digest,
                acceptance["acceptance_event"]["digest"],
                "post-capture.json", assignment["assignment_id"],
                subject_digest, context_digest, capture_key, capture_key_digest,
            )
            post_snapshot = parse_repository_snapshot_v3(post_capture["snapshot"])
            post_changes = changed_paths_v3(pre_snapshot, post_snapshot)
            post_deltas = [
                self.delta(
                    "document_delta", item["path"], pre_snapshot, post_snapshot,
                    graph_relevant=False,
                )
                for item in post_changes
                if item["path"] in post_snapshot.entry_map
                and post_snapshot.entry_map[item["path"]].path_type
                in {"regular_file", "symlink"}
            ]

            all_deltas = [worker_delta, *post_deltas]
            graph_reason = "All bounded changes are graph-neutral in this fixture."
            classification = {
                "schema_version": 1,
                "disposition": "not_applicable",
                "delta_set_digest": digest_json(all_deltas),
                "reason": graph_reason,
            }
            classification_path = evidence / "graph-classification.json"
            classification_path.write_bytes(json_bytes(classification))

            closure = self.closure_manifest(
                assignment,
                assignment_digest,
                assignment_snapshot,
                worker_snapshot,
                worker_capture["capture_evidence"],
                worker_changes,
                worker_delta,
                pre_snapshot,
                pre_capture["capture_evidence"],
                post_snapshot,
                post_capture["capture_evidence"],
                post_changes,
                post_deltas,
                acceptance["acceptance_event"],
                acceptance_ref,
                file_digest(finalization_path),
                author_envelope_digest,
                graph_reason,
                file_digest(classification_path),
                digest_json(all_deltas),
            )
            closure_path = evidence / "closure.json"
            closure_path.write_bytes(json_bytes(closure))
            result = self.run_json([
                sys.executable,
                str(COORDINATOR_RUNNER),
                "--root",
                str(root),
                "--assignment",
                str(assignment_path),
                "--manifest",
                str(closure_path),
                "--evidence-root",
                str(evidence),
                "--capture-authority-key",
                str(capture_key),
                "--trusted-capture-authority-key-sha256",
                capture_key_digest,
                "--acceptance-authority-key",
                str(main_key),
                "--trusted-acceptance-authority-key-sha256",
                main_key_digest,
            ])

        self.assertEqual("pass", result["status"], result)
        self.assertEqual([], result["diagnostics"])

    @staticmethod
    def run_json(command):
        process = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        payload = json.loads(process.stdout) if process.stdout.strip() else {
            "stderr": process.stderr
        }
        if process.returncode != 0:
            raise AssertionError(process.stderr or payload)
        return payload

    @classmethod
    def capture_phase(
        cls, root, evidence, policy_path, phase_id, parent_snapshot_digest,
        parent_evidence_digest, evidence_path, assignment_id, subject_digest,
        context_digest, capture_key, capture_key_digest,
    ):
        return cls.run_json([
            sys.executable,
            str(CAPTURE_RUNNER),
            "--root",
            str(root),
            "--policy",
            str(policy_path),
            "--phase-id",
            phase_id,
            "--parent-snapshot-digest",
            parent_snapshot_digest,
            "--parent-evidence-digest",
            parent_evidence_digest,
            "--assignment-id",
            assignment_id,
            "--assignment-subject-digest",
            subject_digest,
            "--context-digest",
            context_digest,
            "--evidence-root",
            str(evidence),
            "--capture-evidence-path",
            evidence_path,
            "--capture-authority-key",
            str(capture_key),
            "--trusted-capture-authority-key-sha256",
            capture_key_digest,
        ])

    @classmethod
    def record_acceptance(
        cls, root, evidence, pre_snapshot, assignment, assignment_digest,
        context_digest, parent_evidence_digest, acceptance_ref,
        main_key, main_key_digest,
    ):
        return cls.run_json([
            sys.executable,
            str(ACCEPTANCE_RUNNER),
            "--root",
            str(root),
            "--evidence-root",
            str(evidence),
            "--acceptance-event-path",
            "acceptance-event.json",
            "--assignment-id",
            assignment["assignment_id"],
            "--assignment-digest",
            assignment_digest,
            "--context-digest",
            context_digest,
            "--policy-digest",
            pre_snapshot.policy.digest,
            "--closure-target",
            "step",
            "--closure-step-ref",
            "R010/S02",
            "--pre-snapshot-path",
            "pre-snapshot.json",
            "--pre-snapshot-digest",
            pre_snapshot.snapshot_digest,
            "--parent-evidence-digest",
            parent_evidence_digest,
            "--acceptance-ref",
            acceptance_ref,
            "--accepted-step",
            "R010/S02",
            "--accepted-by",
            "main",
            "--acceptance-authority-key",
            str(main_key),
            "--trusted-acceptance-authority-key-sha256",
            main_key_digest,
        ])

    @staticmethod
    def context():
        scope = {
            "read_scope": ["."],
            "allowed_edit_scope": ["src"],
            "excluded_scope": [],
        }
        return {
            "main_context_checkpoint": "R010/S02 actual Author closure integration.",
            "work_context": {
                "round_ref": "R010",
                "work_ref": "R010/authority-chain-snapshot-closure",
                "step_refs": ["R010/S02"],
            },
            "source_documents": [
                "00_docs/r010-fixture/work/key-progress.md"
            ],
            "applicable_standards": ["00_docs/convention.md"],
            "accepted_decisions": [],
            "completion_criteria": ["Actual Author runner closes finalization."],
            "scope_boundaries": deepcopy(scope),
            "forbidden_changes": ["Worker must not edit documents."],
            "verification_expectations": ["Package runners pass without mocks."],
            "artifact_context": {
                "status": "ready",
                "evidence": ["Bounded source delta"],
            },
            "reader_context": {
                "status": "ready",
                "evidence": ["R010/S02 recovered"],
            },
            "author_context": {
                "status": "ready",
                "evidence": ["Finalization sources planned"],
            },
            "dependency_status": "satisfied",
            "active_step_gates": [],
            "work_completion_gates": [],
        }

    @staticmethod
    def assignment(context, policy):
        scope = deepcopy(context["scope_boundaries"])
        return {
            "schema_version": 3,
            "assignment_id": "R010-S02-author-integration",
            "execution_mode": "direct_execution",
            "purpose": "implement",
            "authority": "bounded_edit",
            "goal": "Verify the actual post-acceptance Author closure chain.",
            "context_pack": deepcopy(context),
            "injected_skills": [{
                "skill_id": "keystone-default-bounded-worker",
                "mode": "default",
            }],
            "scope": scope,
            "document_root": "00_docs",
            "snapshot_policy": deepcopy(policy),
            "assignment_phase": None,
            "phase_authorities": {
                "worker": {
                    "authority": "bounded_edit",
                    "allowed_edit_scope": ["src"],
                    "excluded_scope": [],
                },
                "author": {
                    "authority": "document_edit",
                    "allowed_edit_scope": ["00_docs"],
                    "excluded_scope": [],
                },
                "repository_owner": {
                    "authority": "bounded_edit",
                    "allowed_edit_scope": ["src"],
                    "excluded_scope": [],
                },
                "linker": {
                    "authority": "read_only",
                    "allowed_edit_scope": [],
                    "excluded_scope": [],
                },
            },
        }

    @staticmethod
    def delta(kind, path, before, after, graph_relevant):
        before_entry = before.entry_map.get(path)
        after_entry = after.entry_map.get(path)
        return {
            "kind": kind,
            "source_surface": path,
            "change_kind": (
                "added" if before_entry is None
                else "deleted" if after_entry is None
                else "modified"
            ),
            "changed_locators": [{"path": path}],
            "semantic_summary": "Bounded actual-state integration delta.",
            "baseline_digest": (
                before_entry.raw_byte_digest if before_entry is not None else "absent"
            ),
            "resulting_digest": (
                after_entry.raw_byte_digest if after_entry is not None else "absent"
            ),
            "graph_relevant": graph_relevant,
        }

    @staticmethod
    def actor_delta(assignment, actor, changes, deltas):
        authority = assignment["phase_authorities"][actor]
        return {
            "actor": actor,
            "authority": authority["authority"],
            "allowed_edit_scope": deepcopy(authority["allowed_edit_scope"]),
            "excluded_scope": deepcopy(authority["excluded_scope"]),
            "changed_paths": deepcopy(changes),
            "artifact_deltas": deepcopy(deltas),
        }

    @classmethod
    def closure_manifest(
        cls, assignment, assignment_digest, assignment_snapshot, worker_snapshot,
        worker_capture, worker_changes, worker_delta, pre_snapshot, pre_capture,
        post_snapshot, post_capture, post_changes, post_deltas,
        acceptance_event, acceptance_ref, finalization_digest,
        author_envelope_digest, graph_reason, classification_digest,
        delta_set_digest,
    ):
        linker_delta = cls.actor_delta(assignment, "linker", [], [])
        return {
            "schema_version": 3,
            "closure_stage": "post_acceptance",
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
                "artifact_deltas": [deepcopy(worker_delta)],
                "scope_check": "within_scope",
                "forbidden_change_check": "none",
                "verification": {
                    "status": "pass",
                    "evidence": ["Worker source bytes verified."],
                },
            },
            "worker_phase": {
                "phase_id": "worker",
                "baseline_snapshot_digest": assignment_snapshot.snapshot_digest,
                "result_snapshot": worker_snapshot.wire(),
                "capture_evidence": worker_capture,
                "actor_delta": cls.actor_delta(
                    assignment, "worker", worker_changes, [worker_delta]
                ),
            },
            "pre_acceptance_closure_phase": {
                "phase_id": "pre_acceptance_closure",
                "baseline_snapshot_digest": worker_snapshot.snapshot_digest,
                "result_snapshot": pre_snapshot.wire(),
                "capture_evidence": pre_capture,
                "actor_deltas": [deepcopy(linker_delta)],
            },
            "post_acceptance_phase": {
                "phase_id": "post_acceptance",
                "baseline_snapshot_digest": pre_snapshot.snapshot_digest,
                "result_snapshot": post_snapshot.wire(),
                "acceptance_ref": acceptance_ref,
                "acceptance_event": deepcopy(acceptance_event),
                "accepted_steps": ["R010/S02"],
                "capture_evidence": post_capture,
                "author_evidence_binding": {
                    "finalization_manifest_digest": finalization_digest,
                    "runner_envelope_digest": author_envelope_digest,
                    "source_snapshot_digest": post_snapshot.snapshot_digest,
                },
                "actor_deltas": [
                    cls.actor_delta(assignment, "author", post_changes, post_deltas),
                    deepcopy(linker_delta),
                ],
            },
            "keystone_closure": {
                "document_sync": {
                    "disposition": "required",
                    "state": "complete",
                    "reason": "Author wrote finalization sources after Main acceptance.",
                    "evidence": ["Post snapshot attributes exact document bytes."],
                },
                "metadata_sync": {
                    "disposition": "required",
                    "state": "complete",
                    "reason": "Author synchronized typed status metadata.",
                    "evidence": ["Schema-v5 Author runner passed."],
                },
                "graph_sync": {
                    "disposition": "not_applicable",
                    "state": "not_applicable",
                    "reason": graph_reason,
                    "classification_path": "graph-classification.json",
                    "classification_digest": classification_digest,
                    "delta_set_digest": delta_set_digest,
                },
                "acceptance_ref": acceptance_ref,
                "acceptance_event": deepcopy(acceptance_event),
                "accepted_steps": ["R010/S02"],
                "finalization": {
                    "state": "complete",
                    "acceptance_ref": acceptance_ref,
                    "evidence": ["Actual package Author runner passed."],
                    "manifest_path": "author-finalization.json",
                    "manifest_digest": finalization_digest,
                    "envelope_digest": author_envelope_digest,
                    "runner_status": "pass",
                },
            },
            "coordinator_review": {
                "assignment_id": assignment["assignment_id"],
                "assignment_digest": assignment_digest,
                "decision": "closure_complete",
                "main_acceptance_allowed": False,
                "evidence": ["Actual post-acceptance package chain passed."],
            },
        }

    @staticmethod
    def write_author_sources(root, acceptance_ref):
        progress = "00_docs/r010-fixture/work/key-progress.md"
        work_index = "00_docs/r010-fixture/work/00_key-index.md"
        round_index = "00_docs/r010-fixture/00_key-index.md"
        root_index = "00_docs/00_key-index.md"
        context_map = "00_docs/key-context-map.md"
        accepted_round = "00_docs/r009-accepted/00_key-index.md"
        common_state = (
            "global_state:\n"
            "  active_round: R010\n"
            "  latest_accepted_round: R009\n"
            "  active_steps: []\n"
        )
        contents = {
            progress: (
                "---\n"
                "doc_type: progress\n"
                "work_status: complete\n"
                "step_ref: R010/S02\n"
                "work_ref: R010/authority-chain-snapshot-closure\n"
                "approval:\n  state: accepted\n"
                "finalization:\n  state: complete\n"
                f"  acceptance_ref: {acceptance_ref}\n"
                "key: {id: key.work.authority-chain.progress}\n"
                "---\n# Progress\n"
            ),
            work_index: (
                "---\ndoc_type: work\nwork_status: complete\n"
                "key: {id: key.work.authority-chain.index}\n"
                f"{common_state}---\n# Work\n"
            ),
            round_index: (
                "---\ndoc_type: work_round\nround_status: active\n"
                "key: {id: key.work.round.r010-fixture.index}\n"
                f"{common_state}---\n# Round\n"
            ),
            root_index: (
                "---\ndoc_type: work_round_index\n"
                "key: {id: key.work.index}\n"
                f"{common_state}---\n# Works\n"
            ),
            context_map: (
                "---\ndoc_type: context_map\n"
                "key: {id: key.context-map}\n"
                f"{common_state}---\n# Context\n"
            ),
            accepted_round: (
                "---\ndoc_type: work_round\nround_status: accepted\n"
                "key: {id: key.work.round.r009-accepted.index}\n"
                "---\n# Accepted Round\n"
            ),
        }
        for relative, content in contents.items():
            (root / relative).write_text(content, encoding="utf-8")

        candidates = []
        for category in IMPACT_CATEGORIES:
            path = accepted_round if category == "standard_decision_plan" else round_index
            candidate = {
                "category": category,
                "artifact": category,
                "path": path,
                "disposition": "no_change",
                "reason": "%s was reviewed for the integration fixture." % category,
            }
            if category == "implementation_gate":
                candidate.update(
                    gate_state="resolved", gate_scope="R010/S02 implementation"
                )
            elif category == "residual_risk":
                candidate.update(risk_state="none", risk_items=[])
            elif category == "namespace":
                candidate.update(namespace_state="checked")
            candidates.append(candidate)
        return {
            "schema_version": 5,
            "acceptance_ref": acceptance_ref,
            "steps": [{
                "ref": "R010/S02",
                "work_ref": "R010/authority-chain-snapshot-closure",
                "status": "complete",
                "approval_state": "accepted",
                "finalization_state": "complete",
                "finalization_acceptance_ref": acceptance_ref,
                "progress_path": progress,
            }],
            "accepted_steps": ["R010/S02"],
            "execution_transitions": [{
                "ref": "R010/S02", "from": "in_progress", "to": "complete",
            }],
            "approval_transitions": [{
                "ref": "R010/S02",
                "from": "pending",
                "to": "accepted",
                "evidence": acceptance_ref,
            }],
            "active_steps": [],
            "active_step_sources": [
                {"category": "work_index", "path": work_index},
                {"category": "round_index", "path": round_index},
                {"category": "context_map", "path": context_map},
            ],
            "global_state": {
                "active_round": "R010",
                "latest_accepted_round": "R009",
                "active_steps": [],
                "sources": [
                    {
                        "category": "work_index",
                        "path": work_index,
                        "key_id": "key.work.authority-chain.index",
                    },
                    {
                        "category": "round_index",
                        "path": round_index,
                        "key_id": "key.work.round.r010-fixture.index",
                    },
                    {
                        "category": "root_index",
                        "path": root_index,
                        "key_id": "key.work.index",
                    },
                    {
                        "category": "context_map",
                        "path": context_map,
                        "key_id": "key.context-map",
                    },
                ],
            },
            "early_work": [],
            "finalization": {
                "required": True,
                "state": "complete",
                "progress_path": progress,
                "evidence": [
                    "main_acceptance",
                    "impact_dispositions",
                    "source_updates",
                    "semantic_review",
                    "post_edit_verification",
                ],
            },
            "graph_sync": {
                "required": False,
                "disposition": "not_applicable",
                "reason": "No graph mutation is required by finalization docs.",
            },
            "impact_candidates": candidates,
            "namespace_entries": [],
        }


if __name__ == "__main__":
    unittest.main()
