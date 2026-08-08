import hashlib
import json
import os
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


PACKAGE_ROOT = Path(__file__).parents[1]
SCRIPTS = PACKAGE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import closure_v3  # noqa: E402
import closure_actual_state as actual_state  # noqa: E402


def json_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_json(value):
    return "sha256:" + hashlib.sha256(json_bytes(value)).hexdigest()


def file_digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class FakePolicy:
    def __init__(self, wire):
        self._wire = deepcopy(wire)

    def to_wire(self):
        return deepcopy(self._wire)


class FakeEntry:
    def __init__(self, raw_digest):
        self.path_type = "regular_file"
        self.raw_byte_digest = raw_digest
        self.entry_digest = raw_digest


class FakeSnapshot:
    def __init__(self, entries, policy):
        self.entries = deepcopy(entries)
        self.policy = deepcopy(policy)
        self.expected_absences = ()
        self.snapshot_digest = digest_json({"entries": self.entries, "policy": self.policy})

    @property
    def entry_map(self):
        return {path: FakeEntry(value) for path, value in self.entries.items()}

    def to_wire(self):
        return {
            "policy": deepcopy(self.policy),
            "policy_digest": digest_json(self.policy),
            "entries": [
                {"path": path, "entry_digest": entry_digest}
                for path, entry_digest in sorted(self.entries.items())
            ],
            "snapshot_digest": self.snapshot_digest,
        }


def fake_changed_paths(before, after):
    changes = []
    for path in sorted(set(before.entries) | set(after.entries)):
        before_digest = before.entries.get(path, "absent")
        after_digest = after.entries.get(path, "absent")
        if before_digest == after_digest:
            continue
        if before_digest == "absent":
            kind = "added"
        elif after_digest == "absent":
            kind = "deleted"
        else:
            kind = "modified"
        changes.append({
            "path": path,
            "change_kind": kind,
            "before_entry_digest": before_digest,
            "after_entry_digest": after_digest,
        })
    return changes


def artifact_delta(
    path, change_kind="modified", before="absent", after="absent",
    kind="artifact_delta",
):
    return {
        "kind": kind,
        "source_surface": path,
        "change_kind": change_kind,
        "changed_locators": [{"path": path}],
        "semantic_summary": "Bounded source change.",
        "baseline_digest": before,
        "resulting_digest": after,
        "graph_relevant": False,
    }


class ClosureV3ValidationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "repo"
        self.evidence = self.base / "evidence"
        self.root.mkdir()
        self.evidence.mkdir()
        (self.root / "00_docs").mkdir()
        self.capture_key = self.base / "coordinator-capture.key"
        self.acceptance_key = self.base / "main-acceptance.key"
        self.capture_key.write_bytes(b"coordinator-capture-authority-key-v1")
        self.acceptance_key.write_bytes(b"main-acceptance-authority-key-v1!!")
        self.capture_key.chmod(0o600)
        self.acceptance_key.chmod(0o600)
        self.capture_key_digest = file_digest(self.capture_key)
        self.acceptance_key_digest = file_digest(self.acceptance_key)
        self.command_digest = digest_json("package-command-fixture")
        self.capture_references = {}
        self.capture_serial = 0
        self.acceptance_event_reference = None
        self.policy = {
            "schema_version": 3,
            "include_paths": ["."],
            "exclusions": [],
            "entry_budget": 100,
        }
        self.assignment_snapshot = self.snapshot({
            "src/example.py": digest_json("worker-before"),
        })
        self.worker_snapshot = self.snapshot({
            "src/example.py": digest_json("worker-after"),
        })
        self.pre_snapshot = self.worker_snapshot
        self.live_snapshot = self.pre_snapshot
        self.assignment = self.make_assignment()
        self.assignment_digest = digest_json(self.assignment)
        self.manifest = self.make_manifest()

    def tearDown(self):
        self.temp.cleanup()

    def snapshot(self, entries):
        return FakeSnapshot(entries, self.policy)

    @staticmethod
    def sync_result():
        return {
            "disposition": "not_applicable",
            "state": "not_applicable",
            "reason": "No source synchronization required.",
            "evidence": ["phase reviewed"],
        }

    def make_context(self):
        scope = {
            "read_scope": ["."],
            "allowed_edit_scope": ["src"],
            "excluded_scope": ["secret"],
        }
        return {
            "main_context_checkpoint": "R010/S02 bounded assignment",
            "work_context": {
                "round_ref": "R010",
                "work_ref": "R010/authority-chain-snapshot-closure",
                "step_refs": ["R010/S02"],
            },
            "source_documents": ["00_docs/works/r010/key-work.md"],
            "applicable_standards": ["00_docs/convention.md"],
            "accepted_decisions": [],
            "completion_criteria": ["phase attribution is exact"],
            "scope_boundaries": scope,
            "forbidden_changes": ["cross-actor source writes"],
            "verification_expectations": ["focused tests pass"],
            "artifact_context": {"status": "ready", "evidence": ["Linker context"]},
            "reader_context": {"status": "ready", "evidence": ["Reader context"]},
            "author_context": {"status": "ready", "evidence": ["Author context"]},
            "dependency_status": "satisfied",
            "active_step_gates": [],
            "work_completion_gates": [],
        }

    def make_assignment(self):
        context = self.make_context()
        assignment = {
            "schema_version": 3,
            "assignment_id": "R010-S02-worker-1",
            "execution_mode": "orchestration",
            "purpose": "implement",
            "authority": "bounded_edit",
            "goal": "Verify phase-separated source authority.",
            "context_pack": context,
            "injected_skills": [{"skill_id": "example:worker", "mode": "implementation"}],
            "scope": deepcopy(context["scope_boundaries"]),
            "document_root": "00_docs",
            "snapshot_policy": deepcopy(self.policy),
            "assignment_phase": {
                "phase_id": "assignment",
                "actor": "coordinator",
                "authority": "verification",
                "result_snapshot": self.assignment_snapshot.to_wire(),
                "capture_evidence": None,
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
        self.assignment = assignment
        assignment["assignment_phase"]["capture_evidence"] = self.capture_evidence(
            "assignment",
            "absent",
            self.assignment_snapshot,
            "2026-08-08T09:59:00Z",
        )
        return assignment

    def actor_delta(self, actor, changes, artifacts=None):
        authority = self.assignment["phase_authorities"][actor]
        return {
            "actor": actor,
            "authority": authority["authority"],
            "allowed_edit_scope": deepcopy(authority["allowed_edit_scope"]),
            "excluded_scope": deepcopy(authority["excluded_scope"]),
            "changed_paths": deepcopy(changes),
            "artifact_deltas": deepcopy(artifacts or []),
        }

    def capture_evidence(
        self, phase_id, parent_snapshot_digest, snapshot, captured_at
    ):
        assignment = getattr(self, "assignment", {})
        assignment_id = assignment.get("assignment_id", "R010-S02-worker-1")
        context = assignment.get("context_pack", self.make_context())
        parent_evidence_digest = {
            "assignment": "absent",
            "worker": self.capture_references.get("assignment", {}).get("digest"),
            "pre_acceptance_closure": self.capture_references.get(
                "worker", {}
            ).get("digest"),
            "post_acceptance": (self.acceptance_event_reference or {}).get("digest"),
        }[phase_id]
        with mock.patch.object(
            closure_v3, "_command_executable_digest", return_value=self.command_digest,
        ):
            envelope = closure_v3.build_phase_capture_envelope(
                root=self.root,
                phase_id=phase_id,
                parent_snapshot_digest=parent_snapshot_digest,
                snapshot=snapshot,
                captured_at=captured_at,
                assignment_id=assignment_id,
                assignment_subject_digest=closure_v3.assignment_subject_digest(
                    assignment
                ),
                context_digest=digest_json(context),
                evidence_root=self.evidence,
                parent_evidence_digest=parent_evidence_digest,
                capture_authority_key=self.capture_key,
                capture_authority_key_digest=self.capture_key_digest,
            )
        self.capture_serial += 1
        relative = "%03d-%s-capture.json" % (self.capture_serial, phase_id)
        path = self.evidence / relative
        path.write_bytes(json_bytes(envelope))
        reference = {"path": relative, "digest": file_digest(path)}
        self.capture_references[phase_id] = reference
        return reference

    def make_report(self, worker_changes, worker_artifacts):
        return {
            "assignment_id": self.assignment["assignment_id"],
            "assignment_digest": self.assignment_digest,
            "context_digest": digest_json(self.assignment["context_pack"]),
            "execution_mode": self.assignment["execution_mode"],
            "status": "DONE",
            "purpose": self.assignment["purpose"],
            "authority": self.assignment["authority"],
            "goal": self.assignment["goal"],
            "skill_usage": [{
                "skill_id": "example:worker",
                "mode": "implementation",
                "outputs_used": ["implementation workflow"],
                "limits_hit": [],
            }],
            "changed_files": [item["path"] for item in worker_changes],
            "artifact_deltas": deepcopy(worker_artifacts),
            "scope_check": "within_scope",
            "forbidden_change_check": "none",
            "verification": {"status": "pass", "evidence": ["unit tests passed"]},
        }

    def make_manifest(self):
        worker_changes = fake_changed_paths(self.assignment_snapshot, self.worker_snapshot)
        worker_artifacts = [artifact_delta(
            "src/example.py",
            before=self.assignment_snapshot.entries["src/example.py"],
            after=self.worker_snapshot.entries["src/example.py"],
        )]
        return {
            "schema_version": 3,
            "closure_stage": "pre_acceptance",
            "closure_target": "step",
            "closure_step_ref": "R010/S02",
            "worker_report": self.make_report(worker_changes, worker_artifacts),
            "worker_phase": {
                "phase_id": "worker",
                "baseline_snapshot_digest": self.assignment_snapshot.snapshot_digest,
                "result_snapshot": self.worker_snapshot.to_wire(),
                "capture_evidence": self.capture_evidence(
                    "worker",
                    self.assignment_snapshot.snapshot_digest,
                    self.worker_snapshot,
                    "2026-08-08T10:00:00Z",
                ),
                "actor_delta": self.actor_delta("worker", worker_changes, worker_artifacts),
            },
            "pre_acceptance_closure_phase": {
                "phase_id": "pre_acceptance_closure",
                "baseline_snapshot_digest": self.worker_snapshot.snapshot_digest,
                "result_snapshot": self.pre_snapshot.to_wire(),
                "capture_evidence": self.capture_evidence(
                    "pre_acceptance_closure",
                    self.worker_snapshot.snapshot_digest,
                    self.pre_snapshot,
                    "2026-08-08T10:01:00Z",
                ),
                "actor_deltas": [self.actor_delta("linker", [])],
            },
            "post_acceptance_phase": None,
            "keystone_closure": {
                "document_sync": self.sync_result(),
                "metadata_sync": self.sync_result(),
                "graph_sync": {},
                "finalization": {"state": "not_started", "evidence": []},
            },
            "coordinator_review": {
                "assignment_id": self.assignment["assignment_id"],
                "assignment_digest": self.assignment_digest,
                "decision": "accept_candidate",
                "main_acceptance_allowed": True,
                "evidence": ["phase chain reviewed"],
            },
        }

    def refresh_bindings(self):
        self.assignment_digest = digest_json(self.assignment)
        self.manifest["worker_report"]["assignment_digest"] = self.assignment_digest
        self.manifest["worker_report"]["context_digest"] = digest_json(
            self.assignment["context_pack"]
        )
        self.manifest["coordinator_review"]["assignment_digest"] = self.assignment_digest

    def recapture_pre_acceptance_chain(self):
        self.assignment["assignment_phase"]["capture_evidence"] = self.capture_evidence(
            "assignment", "absent", self.assignment_snapshot,
            "2026-08-08T09:59:00Z",
        )
        self.manifest["worker_phase"]["capture_evidence"] = self.capture_evidence(
            "worker", self.assignment_snapshot.snapshot_digest,
            self.worker_snapshot, "2026-08-08T10:00:00Z",
        )
        self.manifest["pre_acceptance_closure_phase"][
            "capture_evidence"
        ] = self.capture_evidence(
            "pre_acceptance_closure", self.worker_snapshot.snapshot_digest,
            self.pre_snapshot, "2026-08-08T10:01:00Z",
        )

    def validate(self):
        canonical_linker, canonical_author = closure_v3.package_runner_paths()
        snapshots = {
            snapshot.snapshot_digest: snapshot
            for snapshot in (
                self.assignment_snapshot,
                self.worker_snapshot,
                self.pre_snapshot,
                self.live_snapshot,
            )
        }

        def parse_snapshot(wire):
            return snapshots[wire["snapshot_digest"]]

        with mock.patch.object(
            closure_v3, "_normalize_policy", return_value=FakePolicy(self.policy)
        ), mock.patch.object(
            closure_v3, "_parse_snapshot", side_effect=parse_snapshot
        ), mock.patch.object(
            closure_v3, "_changed_paths", side_effect=fake_changed_paths
        ), mock.patch.object(
            closure_v3, "_capture_snapshot", return_value=self.live_snapshot
        ), mock.patch.object(
            actual_state, "snapshot_symlink_violations_v3", return_value=[]
        ), mock.patch.object(
            closure_v3, "validate_sync_evidence"
        ), mock.patch.object(
            closure_v3, "validate_graph_sync_evidence"
        ), mock.patch.object(
            closure_v3,
            "validate_finalization_evidence",
            return_value=(
                "pass" if self.manifest["closure_stage"] == "post_acceptance" else None
            ),
        ), mock.patch.object(
            closure_v3, "_command_executable_digest", return_value=self.command_digest,
        ):
            return closure_v3.validate_v3(
                self.manifest,
                root=self.root,
                assignment=self.assignment,
                assignment_digest=self.assignment_digest,
                evidence_root=self.evidence,
                linker_runner=canonical_linker,
                author_runner=canonical_author,
                timeout_seconds=1.0,
                capture_authority_key=self.capture_key,
                capture_authority_key_digest=self.capture_key_digest,
                acceptance_authority_key=(
                    self.acceptance_key
                    if self.manifest["closure_stage"] == "post_acceptance"
                    else None
                ),
                acceptance_authority_key_digest=(
                    self.acceptance_key_digest
                    if self.manifest["closure_stage"] == "post_acceptance"
                    else None
                ),
            )

    @staticmethod
    def codes(diagnostics):
        return {item["code"] for item in diagnostics}

    def resign_reference(self, reference, key):
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        receipt = envelope["receipt"]
        unsigned_receipt = dict(receipt)
        unsigned_receipt.pop("mac", None)
        unsigned_envelope = dict(envelope)
        unsigned_envelope.pop("receipt", None)
        receipt["mac"] = closure_v3._receipt_mac(
            key.read_bytes(), unsigned_envelope, unsigned_receipt,
        )
        path.write_bytes(json_bytes(envelope))
        reference["digest"] = file_digest(path)
        return envelope

    def record_pre_author_change(self, path="00_docs/key-progress.md"):
        self.pre_snapshot = self.snapshot({
            **self.worker_snapshot.entries,
            path: digest_json({"path": path, "state": "pre"}),
        })
        self.live_snapshot = self.pre_snapshot
        changes = fake_changed_paths(self.worker_snapshot, self.pre_snapshot)
        artifacts = [artifact_delta(
            path,
            "added",
            after=self.pre_snapshot.entries[path],
            kind="document_delta",
        )]
        self.manifest["pre_acceptance_closure_phase"].update({
            "result_snapshot": self.pre_snapshot.to_wire(),
            "capture_evidence": self.capture_evidence(
                "pre_acceptance_closure",
                self.worker_snapshot.snapshot_digest,
                self.pre_snapshot,
                "2026-08-08T10:01:00Z",
            ),
            "actor_deltas": [
                self.actor_delta("author", changes, artifacts),
                self.actor_delta("linker", []),
            ],
        })

    def record_post_finalization(self):
        self.manifest["closure_stage"] = "post_acceptance"
        acceptance_ref = "R010/S02/main-acceptance"
        with mock.patch.object(
            closure_v3, "_command_executable_digest", return_value=self.command_digest,
        ):
            acceptance_event = closure_v3.build_acceptance_event_envelope(
                root=self.root,
                evidence_root=self.evidence,
                assignment_id=self.assignment["assignment_id"],
                assignment_digest=self.assignment_digest,
                context_digest=digest_json(self.assignment["context_pack"]),
                policy_digest=self.pre_snapshot.to_wire()["policy_digest"],
                closure_target=self.manifest["closure_target"],
                closure_step_ref=self.manifest["closure_step_ref"],
                pre_snapshot_digest=self.pre_snapshot.snapshot_digest,
                observed_snapshot_digest=self.pre_snapshot.snapshot_digest,
                parent_evidence_digest=self.manifest[
                    "pre_acceptance_closure_phase"
                ]["capture_evidence"]["digest"],
                acceptance_ref=acceptance_ref,
                accepted_steps=["R010/S02"],
                accepted_at="2026-08-08T10:01:30Z",
                accepted_by="main",
                acceptance_authority_key=self.acceptance_key,
                acceptance_authority_key_digest=self.acceptance_key_digest,
            )
        acceptance_path = self.evidence / "acceptance-event.json"
        acceptance_path.write_bytes(json_bytes(acceptance_event))
        self.acceptance_event_reference = {
            "path": acceptance_path.name,
            "digest": file_digest(acceptance_path),
        }
        post_snapshot = self.snapshot({
            **self.pre_snapshot.entries,
            "00_docs/key-context-map.md": digest_json("terminal"),
        })
        changes = fake_changed_paths(self.pre_snapshot, post_snapshot)
        artifacts = [artifact_delta(
            "00_docs/key-context-map.md",
            "added",
            after=post_snapshot.entries["00_docs/key-context-map.md"],
            kind="document_delta",
        )]
        finalization_manifest = {
            "schema_version": 5,
            "acceptance_ref": acceptance_ref,
            "steps": [{
                "ref": "R010/S02",
                "progress_path": "00_docs/key-context-map.md",
            }],
            "accepted_steps": ["R010/S02"],
            "active_step_sources": [],
            "global_state": {"sources": []},
            "finalization": {
                "progress_path": "00_docs/key-context-map.md",
            },
            "impact_candidates": [],
            "namespace_entries": [],
        }
        finalization_path = self.evidence / "finalization.json"
        finalization_path.write_bytes(json_bytes(finalization_manifest))
        manifest_digest = file_digest(finalization_path)
        runner_digest = digest_json("envelope")
        self.live_snapshot = post_snapshot
        self.manifest["post_acceptance_phase"] = {
            "phase_id": "post_acceptance",
            "baseline_snapshot_digest": self.pre_snapshot.snapshot_digest,
            "result_snapshot": post_snapshot.to_wire(),
            "capture_evidence": self.capture_evidence(
                "post_acceptance",
                self.pre_snapshot.snapshot_digest,
                post_snapshot,
                "2026-08-08T10:02:00Z",
            ),
            "acceptance_ref": acceptance_ref,
            "acceptance_event": deepcopy(self.acceptance_event_reference),
            "accepted_steps": ["R010/S02"],
            "author_evidence_binding": {
                "finalization_manifest_digest": manifest_digest,
                "runner_envelope_digest": runner_digest,
                "source_snapshot_digest": post_snapshot.snapshot_digest,
            },
            "actor_deltas": [
                self.actor_delta("author", changes, artifacts),
                self.actor_delta("linker", []),
            ],
        }
        self.manifest["keystone_closure"].update({
            "acceptance_ref": acceptance_ref,
            "acceptance_event": deepcopy(self.acceptance_event_reference),
            "accepted_steps": ["R010/S02"],
            "finalization": {
                "state": "complete",
                "acceptance_ref": acceptance_ref,
                "evidence": ["Author finalization passed"],
                "manifest_path": "finalization.json",
                "manifest_digest": manifest_digest,
                "envelope_digest": runner_digest,
                "runner_status": "pass",
            },
        })
        self.manifest["coordinator_review"].update({
            "decision": "closure_complete",
            "main_acceptance_allowed": False,
        })

    def test_worker_only_pre_acceptance_phase_passes(self):
        self.assertEqual([], self.validate())

    def test_worker_and_author_document_sync_are_separately_attributed(self):
        self.record_pre_author_change()
        self.assertEqual([], self.validate())
        self.assertEqual(
            ["src/example.py"], self.manifest["worker_report"]["changed_files"]
        )

    def test_post_acceptance_finalization_phase_passes(self):
        self.record_pre_author_change()
        self.record_post_finalization()
        self.assertEqual([], self.validate())

    def test_post_acceptance_requires_main_signed_acceptance_event(self):
        self.record_post_finalization()
        self.manifest["post_acceptance_phase"].pop("acceptance_event")
        self.manifest["post_acceptance_phase"]["acceptance_evidence"] = [
            "self-claimed Main acceptance"
        ]
        self.manifest["keystone_closure"].pop("acceptance_event")
        self.manifest["keystone_closure"]["acceptance_evidence"] = [
            "self-claimed Main acceptance"
        ]
        codes = self.codes(self.validate())
        self.assertIn("required_field_missing", codes)
        self.assertIn("acceptance_event_path_invalid", codes)

    def test_acceptance_event_subject_is_bound_to_raw_assignment(self):
        self.record_post_finalization()
        reference = self.manifest["post_acceptance_phase"]["acceptance_event"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["subject"]["assignment_digest"] = digest_json("other-assignment")
        path.write_bytes(json_bytes(envelope))
        self.resign_reference(reference, self.acceptance_key)
        self.manifest["keystone_closure"]["acceptance_event"] = deepcopy(reference)
        self.assertIn("acceptance_event_subject_mismatch", self.codes(self.validate()))

    def test_acceptance_event_subject_binds_main_observed_pre_snapshot(self):
        self.record_post_finalization()
        reference = self.manifest["post_acceptance_phase"]["acceptance_event"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["subject"]["observed_snapshot_digest"] = digest_json(
            "stale-live-state"
        )
        path.write_bytes(json_bytes(envelope))
        self.resign_reference(reference, self.acceptance_key)
        self.manifest["keystone_closure"]["acceptance_event"] = deepcopy(reference)
        self.assertIn("acceptance_event_subject_mismatch", self.codes(self.validate()))

    def test_acceptance_builder_rejects_stale_observed_snapshot(self):
        with self.assertRaisesRegex(ValueError, "observed live snapshot"):
            closure_v3.build_acceptance_event_envelope(
                root=self.root,
                evidence_root=self.evidence,
                assignment_id=self.assignment["assignment_id"],
                assignment_digest=self.assignment_digest,
                context_digest=digest_json(self.assignment["context_pack"]),
                policy_digest=self.pre_snapshot.to_wire()["policy_digest"],
                closure_target="step",
                closure_step_ref="R010/S02",
                pre_snapshot_digest=self.pre_snapshot.snapshot_digest,
                observed_snapshot_digest=digest_json("stale-live-state"),
                parent_evidence_digest=self.manifest[
                    "pre_acceptance_closure_phase"
                ]["capture_evidence"]["digest"],
                acceptance_ref="R010/S02/main-acceptance",
                accepted_steps=["R010/S02"],
                accepted_at="2026-08-08T10:01:30Z",
                accepted_by="main",
                acceptance_authority_key=self.acceptance_key,
                acceptance_authority_key_digest=self.acceptance_key_digest,
            )

    def test_hand_written_acceptance_event_cannot_forge_main_receipt(self):
        self.record_post_finalization()
        reference = self.manifest["post_acceptance_phase"]["acceptance_event"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["accepted_at"] = "2026-08-08T10:01:31Z"
        path.write_bytes(json_bytes(envelope))
        reference["digest"] = file_digest(path)
        self.manifest["keystone_closure"]["acceptance_event"] = deepcopy(reference)
        self.assertIn("host_receipt_mac_invalid", self.codes(self.validate()))

    def test_acceptance_event_receipt_must_follow_pre_capture(self):
        self.record_post_finalization()
        reference = self.manifest["post_acceptance_phase"]["acceptance_event"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["receipt"]["parent_evidence_digest"] = self.assignment[
            "assignment_phase"
        ]["capture_evidence"]["digest"]
        path.write_bytes(json_bytes(envelope))
        self.resign_reference(reference, self.acceptance_key)
        self.manifest["keystone_closure"]["acceptance_event"] = deepcopy(reference)
        self.assertIn("host_receipt_parent_mismatch", self.codes(self.validate()))

    def test_post_capture_receipt_must_follow_acceptance_event(self):
        self.record_post_finalization()
        reference = self.manifest["post_acceptance_phase"]["capture_evidence"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["receipt"]["parent_evidence_digest"] = self.manifest[
            "pre_acceptance_closure_phase"
        ]["capture_evidence"]["digest"]
        path.write_bytes(json_bytes(envelope))
        self.resign_reference(reference, self.capture_key)
        self.assertIn("host_receipt_parent_mismatch", self.codes(self.validate()))

    def test_acceptance_event_must_be_between_pre_and_post_captures(self):
        self.record_post_finalization()
        reference = self.manifest["post_acceptance_phase"]["acceptance_event"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["accepted_at"] = "2026-08-08T10:01:00Z"
        path.write_bytes(json_bytes(envelope))
        self.resign_reference(reference, self.acceptance_key)
        self.manifest["keystone_closure"]["acceptance_event"] = deepcopy(reference)
        self.assertIn("acceptance_event_order_invalid", self.codes(self.validate()))

    def test_acceptance_event_requires_main_role_identity(self):
        self.record_post_finalization()
        reference = self.manifest["post_acceptance_phase"]["acceptance_event"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["accepted_by"] = "coordinator"
        path.write_bytes(json_bytes(envelope))
        self.resign_reference(reference, self.acceptance_key)
        self.manifest["keystone_closure"]["acceptance_event"] = deepcopy(reference)
        self.assertIn("acceptance_event_actor_invalid", self.codes(self.validate()))

    def test_main_and_capture_authority_keys_must_be_distinct(self):
        self.record_post_finalization()
        self.acceptance_key = self.capture_key
        self.acceptance_key_digest = self.capture_key_digest
        self.assertIn("authority_key_separation_required", self.codes(self.validate()))

    def test_zero_suffix_key_cannot_make_capture_key_a_main_hmac_alias(self):
        self.record_post_finalization()
        capture_raw = self.capture_key.read_bytes()
        alias_key = self.base / "main-zero-suffix.key"
        alias_key.write_bytes(capture_raw + b"\0")
        alias_key.chmod(0o600)
        self.acceptance_key = alias_key
        self.acceptance_key_digest = file_digest(alias_key)

        reference = self.manifest["post_acceptance_phase"]["acceptance_event"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["accepted_at"] = "2026-08-08T10:01:31Z"
        path.write_bytes(json_bytes(envelope))
        self.resign_reference(reference, self.capture_key)
        self.manifest["keystone_closure"]["acceptance_event"] = deepcopy(reference)
        self.assertIn("host_receipt_mac_invalid", self.codes(self.validate()))

    def test_finalization_acceptance_ref_must_equal_main_event(self):
        self.record_post_finalization()
        self.manifest["keystone_closure"]["finalization"][
            "acceptance_ref"
        ] = "R010/S02/other-acceptance"
        self.assertIn(
            "finalization_acceptance_ref_mismatch", self.codes(self.validate())
        )

    def test_repository_owner_write_after_acceptance_requires_new_attempt(self):
        self.record_post_finalization()
        delta = self.manifest["post_acceptance_phase"]["actor_deltas"][0]
        authority = self.assignment["phase_authorities"]["repository_owner"]
        delta.update({
            "actor": "repository_owner",
            "authority": authority["authority"],
            "allowed_edit_scope": deepcopy(authority["allowed_edit_scope"]),
            "excluded_scope": deepcopy(authority["excluded_scope"]),
        })
        delta["artifact_deltas"][0]["kind"] = "artifact_delta"
        self.assertIn("phase_actor_invalid", self.codes(self.validate()))

    def test_worker_document_write_fails_actor_scope(self):
        path = "00_docs/worker-edit.md"
        self.worker_snapshot = self.snapshot({
            **self.assignment_snapshot.entries,
            path: digest_json("worker-doc"),
        })
        self.pre_snapshot = self.worker_snapshot
        self.live_snapshot = self.pre_snapshot
        changes = fake_changed_paths(self.assignment_snapshot, self.worker_snapshot)
        artifacts = [artifact_delta(
            path, "added", after=self.worker_snapshot.entries[path],
        )]
        self.manifest["worker_phase"].update({
            "result_snapshot": self.worker_snapshot.to_wire(),
            "capture_evidence": self.capture_evidence(
                "worker",
                self.assignment_snapshot.snapshot_digest,
                self.worker_snapshot,
                "2026-08-08T10:00:00Z",
            ),
            "actor_delta": self.actor_delta("worker", changes, artifacts),
        })
        self.manifest["worker_report"] = self.make_report(changes, artifacts)
        self.manifest["pre_acceptance_closure_phase"].update({
            "baseline_snapshot_digest": self.worker_snapshot.snapshot_digest,
            "result_snapshot": self.pre_snapshot.to_wire(),
            "capture_evidence": self.capture_evidence(
                "pre_acceptance_closure",
                self.worker_snapshot.snapshot_digest,
                self.pre_snapshot,
                "2026-08-08T10:01:00Z",
            ),
        })
        self.refresh_bindings()
        self.assertIn("actor_change_out_of_scope", self.codes(self.validate()))

    def test_signed_assignment_cannot_authorize_worker_document_scope(self):
        scope = self.assignment["scope"]
        scope["allowed_edit_scope"] = ["00_docs"]
        self.assignment["context_pack"]["scope_boundaries"] = deepcopy(scope)
        self.assignment["phase_authorities"]["worker"][
            "allowed_edit_scope"
        ] = ["00_docs"]
        path = "00_docs/worker-edit.md"
        self.worker_snapshot = self.snapshot({
            **self.assignment_snapshot.entries,
            path: digest_json("worker-doc"),
        })
        self.pre_snapshot = self.worker_snapshot
        self.live_snapshot = self.pre_snapshot
        changes = fake_changed_paths(self.assignment_snapshot, self.worker_snapshot)
        artifacts = [artifact_delta(
            path, "added", after=self.worker_snapshot.entries[path],
        )]
        self.manifest["worker_phase"].update({
            "result_snapshot": self.worker_snapshot.to_wire(),
            "actor_delta": self.actor_delta("worker", changes, artifacts),
        })
        self.manifest["worker_report"] = self.make_report(changes, artifacts)
        self.manifest["pre_acceptance_closure_phase"].update({
            "baseline_snapshot_digest": self.worker_snapshot.snapshot_digest,
            "result_snapshot": self.pre_snapshot.to_wire(),
        })
        self.recapture_pre_acceptance_chain()
        self.refresh_bindings()

        self.assertIn(
            "source_actor_scope_overlaps_document_root", self.codes(self.validate())
        )

    def test_author_code_write_fails_actor_scope(self):
        self.record_pre_author_change("src/author-edit.py")
        self.assertIn("actor_change_out_of_scope", self.codes(self.validate()))

    def test_assignment_cannot_self_authorize_author_code_scope(self):
        self.assignment["phase_authorities"]["author"][
            "allowed_edit_scope"
        ] = ["src"]
        self.record_pre_author_change("src/author-edit.py")
        self.refresh_bindings()
        self.assertIn(
            "author_scope_outside_document_root", self.codes(self.validate())
        )

    def test_assignment_document_root_must_match_repository_configuration(self):
        self.assignment["document_root"] = "src"
        self.assignment["phase_authorities"]["author"][
            "allowed_edit_scope"
        ] = ["src"]
        self.refresh_bindings()
        self.assertIn("document_root_mismatch", self.codes(self.validate()))

    def test_repository_root_document_root_forbids_source_actor_write_scopes(self):
        config = self.root / ".keystone" / "config.yaml"
        config.parent.mkdir()
        config.write_text("version: 1\ndocument_root: '.'\n", encoding="utf-8")
        self.assignment["document_root"] = "."
        self.recapture_pre_acceptance_chain()
        self.refresh_bindings()
        self.assertIn(
            "source_actor_scope_overlaps_document_root", self.codes(self.validate())
        )

    def test_repository_root_document_root_cannot_relabel_author_code_write(self):
        config = self.root / ".keystone" / "config.yaml"
        config.parent.mkdir()
        config.write_text("version: 1\ndocument_root: '.'\n", encoding="utf-8")
        self.assignment["document_root"] = "."
        self.assignment["scope"]["allowed_edit_scope"] = []
        self.assignment["context_pack"]["scope_boundaries"] = deepcopy(
            self.assignment["scope"]
        )
        self.assignment["phase_authorities"]["worker"]["allowed_edit_scope"] = []
        self.assignment["phase_authorities"]["repository_owner"][
            "allowed_edit_scope"
        ] = []
        self.assignment["phase_authorities"]["author"][
            "allowed_edit_scope"
        ] = ["src"]
        self.worker_snapshot = self.assignment_snapshot
        path = "src/author-code.py"
        self.pre_snapshot = self.snapshot({
            **self.worker_snapshot.entries,
            path: digest_json("author-code"),
        })
        self.live_snapshot = self.pre_snapshot
        self.manifest["worker_phase"].update({
            "result_snapshot": self.worker_snapshot.to_wire(),
            "actor_delta": self.actor_delta("worker", [], []),
        })
        self.manifest["worker_report"] = self.make_report([], [])
        author_changes = fake_changed_paths(self.worker_snapshot, self.pre_snapshot)
        author_artifacts = [artifact_delta(
            path, "added", after=self.pre_snapshot.entries[path],
            kind="document_delta",
        )]
        self.manifest["pre_acceptance_closure_phase"].update({
            "baseline_snapshot_digest": self.worker_snapshot.snapshot_digest,
            "result_snapshot": self.pre_snapshot.to_wire(),
            "actor_deltas": [
                self.actor_delta("author", author_changes, author_artifacts),
                self.actor_delta("linker", [], []),
            ],
        })
        self.recapture_pre_acceptance_chain()
        self.refresh_bindings()

        self.assertIn(
            "repository_root_document_write_ambiguous", self.codes(self.validate())
        )

    def test_duplicate_document_root_configuration_fails(self):
        config = self.root / ".keystone" / "config.yaml"
        config.parent.mkdir()
        config.write_text(
            "document_root: 00_docs\ndocument_root: src\n", encoding="utf-8",
        )
        self.assertIn(
            "document_root_configuration_invalid", self.codes(self.validate())
        )

    def test_phase_parent_mismatch_fails(self):
        self.manifest["pre_acceptance_closure_phase"][
            "baseline_snapshot_digest"
        ] = digest_json("forged-parent")
        self.assertIn("phase_parent_snapshot_mismatch", self.codes(self.validate()))

    def test_phase_capture_envelope_parent_cannot_be_rebound(self):
        reference = self.manifest["worker_phase"]["capture_evidence"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["parent_snapshot_digest"] = digest_json("forged-parent")
        path.write_bytes(json_bytes(envelope))
        reference["digest"] = file_digest(path)
        self.assertIn("phase_capture_parent_mismatch", self.codes(self.validate()))

    def test_hand_written_phase_capture_cannot_forge_host_receipt(self):
        reference = self.manifest["worker_phase"]["capture_evidence"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["captured_at"] = "2026-08-08T10:00:30Z"
        path.write_bytes(json_bytes(envelope))
        reference["digest"] = file_digest(path)
        self.assertIn("host_receipt_mac_invalid", self.codes(self.validate()))

    def test_signed_phase_receipt_must_continue_parent_evidence_chain(self):
        reference = self.manifest["pre_acceptance_closure_phase"][
            "capture_evidence"
        ]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["receipt"]["parent_evidence_digest"] = self.assignment[
            "assignment_phase"
        ]["capture_evidence"]["digest"]
        path.write_bytes(json_bytes(envelope))
        self.resign_reference(reference, self.capture_key)
        self.assertIn("host_receipt_parent_mismatch", self.codes(self.validate()))

    def test_phase_receipt_nonce_cannot_be_reused(self):
        worker_reference = self.manifest["worker_phase"]["capture_evidence"]
        worker_envelope = json.loads(
            (self.evidence / worker_reference["path"]).read_text(encoding="utf-8")
        )
        pre_reference = self.manifest["pre_acceptance_closure_phase"][
            "capture_evidence"
        ]
        pre_path = self.evidence / pre_reference["path"]
        pre_envelope = json.loads(pre_path.read_text(encoding="utf-8"))
        pre_envelope["receipt"]["nonce"] = worker_envelope["receipt"]["nonce"]
        pre_path.write_bytes(json_bytes(pre_envelope))
        self.resign_reference(pre_reference, self.capture_key)
        self.assertIn("host_receipt_nonce_reused", self.codes(self.validate()))

    def test_assignment_capture_evidence_is_required_and_validated(self):
        self.assignment["assignment_phase"]["capture_evidence"] = True
        self.refresh_bindings()
        self.assertIn("phase_capture_path_invalid", self.codes(self.validate()))

    def test_assignment_capture_subject_cannot_be_reused(self):
        reference = self.assignment["assignment_phase"]["capture_evidence"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["subject"]["assignment_id"] = "R010-S02-forged"
        path.write_bytes(json_bytes(envelope))
        reference["digest"] = file_digest(path)
        self.refresh_bindings()
        self.assertIn("phase_capture_assignment_mismatch", self.codes(self.validate()))

    def test_valid_capture_chain_cannot_replay_under_another_assignment(self):
        self.assignment["assignment_id"] = "R010-S02-worker-replay"
        self.manifest["worker_report"]["assignment_id"] = self.assignment[
            "assignment_id"
        ]
        self.manifest["coordinator_review"]["assignment_id"] = self.assignment[
            "assignment_id"
        ]
        self.refresh_bindings()
        self.assertIn("phase_capture_assignment_mismatch", self.codes(self.validate()))

    def test_worker_capture_must_follow_assignment_capture(self):
        reference = self.manifest["worker_phase"]["capture_evidence"]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["captured_at"] = "2026-08-08T09:58:00Z"
        path.write_bytes(json_bytes(envelope))
        reference["digest"] = file_digest(path)
        self.assertIn("phase_capture_order_invalid", self.codes(self.validate()))

    def test_phase_capture_times_must_increase(self):
        reference = self.manifest["pre_acceptance_closure_phase"][
            "capture_evidence"
        ]
        path = self.evidence / reference["path"]
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope["captured_at"] = "2026-08-08T09:59:00Z"
        path.write_bytes(json_bytes(envelope))
        reference["digest"] = file_digest(path)
        self.assertIn("phase_capture_order_invalid", self.codes(self.validate()))

    def test_phase_capture_reference_digest_is_strict(self):
        self.manifest["worker_phase"]["capture_evidence"]["digest"] = "sha256:bad"
        self.assertIn(
            "phase_capture_reference_digest_invalid", self.codes(self.validate())
        )

    def test_phase_capture_rejects_symlinked_ancestor(self):
        reference = self.manifest["worker_phase"]["capture_evidence"]
        original = self.evidence / reference["path"]
        actual_directory = self.evidence / "actual"
        actual_directory.mkdir()
        copied = actual_directory / "capture.json"
        copied.write_bytes(original.read_bytes())
        (self.evidence / "alias").symlink_to(
            actual_directory, target_is_directory=True
        )
        reference.update({
            "path": "alias/capture.json",
            "digest": file_digest(copied),
        })
        self.assertIn("phase_capture_evidence_unreadable", self.codes(self.validate()))

    def test_phase_capture_rejects_hardlink(self):
        reference = self.manifest["worker_phase"]["capture_evidence"]
        original = self.evidence / reference["path"]
        hardlink = self.evidence / "hardlink-capture.json"
        os.link(original, hardlink)
        reference.update({
            "path": hardlink.name,
            "digest": file_digest(hardlink),
        })
        self.assertIn("phase_capture_evidence_unreadable", self.codes(self.validate()))

    def test_phase_capture_rejects_duplicate_and_nonfinite_json(self):
        reference = self.manifest["worker_phase"]["capture_evidence"]
        path = self.evidence / reference["path"]
        raw = path.read_bytes()
        duplicate = raw.replace(
            b'{"captured_at"', b'{"schema_version":1,"captured_at"', 1
        )
        path.write_bytes(duplicate)
        reference["digest"] = file_digest(path)
        self.assertIn("phase_capture_evidence_unreadable", self.codes(self.validate()))

        path.write_bytes(raw.replace(b'"schema_version":1', b'"schema_version":NaN'))
        reference["digest"] = file_digest(path)
        self.assertIn("phase_capture_evidence_unreadable", self.codes(self.validate()))

    def test_unattributed_pre_acceptance_change_fails(self):
        self.record_pre_author_change()
        self.manifest["pre_acceptance_closure_phase"]["actor_deltas"] = [
            self.actor_delta("linker", [])
        ]
        self.assertIn("phase_change_attribution_mismatch", self.codes(self.validate()))

    def test_finalization_before_acceptance_fails(self):
        self.manifest["keystone_closure"]["finalization"] = {
            "state": "complete",
            "evidence": ["premature"],
        }
        self.assertIn("finalization_before_acceptance", self.codes(self.validate()))

    def test_finalization_in_progress_before_acceptance_fails(self):
        self.manifest["keystone_closure"]["finalization"] = {
            "state": "in_progress",
            "evidence": [],
        }
        self.assertIn("finalization_before_acceptance", self.codes(self.validate()))

    def test_closure_complete_requires_actual_post_acceptance_author_bytes(self):
        self.record_post_finalization()
        post_phase = self.manifest["post_acceptance_phase"]
        post_phase["result_snapshot"] = self.pre_snapshot.to_wire()
        post_phase["capture_evidence"] = self.capture_evidence(
            "post_acceptance",
            self.pre_snapshot.snapshot_digest,
            self.pre_snapshot,
            "2026-08-08T10:02:00Z",
        )
        post_phase["author_evidence_binding"][
            "source_snapshot_digest"
        ] = self.pre_snapshot.snapshot_digest
        post_phase["actor_deltas"] = [self.actor_delta("linker", [])]
        self.live_snapshot = self.pre_snapshot
        codes = self.codes(self.validate())
        self.assertIn("post_acceptance_author_delta_missing", codes)
        self.assertIn("post_finalization_sources_not_changed", codes)

    def test_post_finalization_manifest_rejects_nonfinite_json(self):
        self.record_post_finalization()
        path = self.evidence / "finalization.json"
        path.write_bytes(b'{"schema_version":NaN}')
        manifest_digest = file_digest(path)
        self.manifest["keystone_closure"]["finalization"][
            "manifest_digest"
        ] = manifest_digest
        self.manifest["post_acceptance_phase"]["author_evidence_binding"][
            "finalization_manifest_digest"
        ] = manifest_digest
        self.assertIn(
            "post_finalization_manifest_unreadable", self.codes(self.validate())
        )

    def test_step_acceptance_must_match_closure_step_exactly(self):
        self.record_post_finalization()
        self.manifest["post_acceptance_phase"]["accepted_steps"] = ["R010/S03"]
        self.manifest["keystone_closure"]["accepted_steps"] = ["R010/S03"]
        self.assertIn("accepted_steps_scope_mismatch", self.codes(self.validate()))

    def test_live_repository_must_equal_terminal_phase(self):
        self.live_snapshot = self.snapshot({
            **self.pre_snapshot.entries,
            "src/unattributed.py": digest_json("unexpected-live-change"),
        })
        self.assertIn("live_terminal_snapshot_mismatch", self.codes(self.validate()))

    def test_unknown_authority_field_is_fail_closed(self):
        self.manifest["worker_phase"]["trusted"] = True
        self.assertIn("unknown_field", self.codes(self.validate()))

    def test_worker_document_delta_domain_claim_fails(self):
        self.manifest["worker_phase"]["actor_delta"]["artifact_deltas"][0][
            "kind"
        ] = "document_delta"
        self.manifest["worker_report"]["artifact_deltas"][0][
            "kind"
        ] = "document_delta"
        self.assertIn("actor_delta_domain_mismatch", self.codes(self.validate()))

    def test_forged_artifact_resulting_digest_fails(self):
        forged = digest_json("forged")
        self.manifest["worker_phase"]["actor_delta"]["artifact_deltas"][0][
            "resulting_digest"
        ] = forged
        self.manifest["worker_report"]["artifact_deltas"][0][
            "resulting_digest"
        ] = forged
        self.assertIn("artifact_resulting_digest_mismatch", self.codes(self.validate()))

    def test_artifact_locator_must_bind_normalized_source_surface(self):
        for delta in (
            self.manifest["worker_phase"]["actor_delta"]["artifact_deltas"][0],
            self.manifest["worker_report"]["artifact_deltas"][0],
        ):
            delta["changed_locators"] = [{
                "path": "../outside",
                "symbol": ["not", "text"],
            }]
        self.assertIn("artifact_delta_locator_invalid", self.codes(self.validate()))

    def test_excluded_scope_uses_portable_casefold_comparison(self):
        authority = deepcopy(self.assignment["phase_authorities"])
        authority["worker"]["excluded_scope"] = ["src/secret"]
        raw = {
            "actor": "worker",
            "authority": "bounded_edit",
            "allowed_edit_scope": ["src"],
            "excluded_scope": ["src/secret"],
            "changed_paths": [{
                "path": "src/Secret/example.py",
                "change_kind": "added",
                "before_entry_digest": "absent",
                "after_entry_digest": digest_json("case-alias"),
            }],
            "artifact_deltas": [artifact_delta(
                "src/Secret/example.py",
                "added",
                after=digest_json("case-alias"),
            )],
        }
        diagnostics = []
        closure_v3._validate_actor_delta(
            raw, "worker_phase.actor_delta", {"worker"}, authority, diagnostics,
        )
        self.assertIn("actor_change_out_of_scope", self.codes(diagnostics))

    def test_allowed_scope_rejects_case_alias_on_case_sensitive_hosts(self):
        authority = deepcopy(self.assignment["phase_authorities"])
        raw = {
            "actor": "worker",
            "authority": "bounded_edit",
            "allowed_edit_scope": ["src"],
            "excluded_scope": ["secret"],
            "changed_paths": [{
                "path": "SRC/example.py",
                "change_kind": "added",
                "before_entry_digest": "absent",
                "after_entry_digest": digest_json("case-alias"),
            }],
            "artifact_deltas": [artifact_delta(
                "SRC/example.py", "added", after=digest_json("case-alias"),
            )],
        }
        diagnostics = []
        closure_v3._validate_actor_delta(
            raw, "worker_phase.actor_delta", {"worker"}, authority, diagnostics,
        )
        self.assertIn("actor_change_out_of_scope", self.codes(diagnostics))

    def test_snapshot_exclusion_cannot_hide_actor_write_scope(self):
        self.policy = {
            "schema_version": 3,
            "include_paths": ["."],
            "exclusions": [{"path": "src/hidden", "reason": "fixture"}],
            "entry_budget": 100,
        }
        self.assignment_snapshot = self.snapshot({
            "src/example.py": digest_json("worker-before"),
        })
        self.worker_snapshot = self.snapshot({
            "src/example.py": digest_json("worker-after"),
        })
        self.pre_snapshot = self.worker_snapshot
        self.live_snapshot = self.pre_snapshot
        self.assignment = self.make_assignment()
        self.assignment_digest = digest_json(self.assignment)
        self.manifest = self.make_manifest()
        self.assertIn(
            "actor_scope_excluded_from_snapshot", self.codes(self.validate())
        )

    def test_snapshot_include_must_cover_every_actor_write_scope(self):
        self.policy = {
            "schema_version": 3,
            "include_paths": ["src"],
            "exclusions": [],
            "entry_budget": 100,
        }
        self.assignment_snapshot = self.snapshot({
            "src/example.py": digest_json("worker-before"),
        })
        self.worker_snapshot = self.snapshot({
            "src/example.py": digest_json("worker-after"),
        })
        self.pre_snapshot = self.worker_snapshot
        self.live_snapshot = self.pre_snapshot
        self.assignment = self.make_assignment()
        self.assignment_digest = digest_json(self.assignment)
        self.manifest = self.make_manifest()
        self.assertIn(
            "actor_scope_outside_snapshot_policy", self.codes(self.validate())
        )

    def test_recorded_escaping_symlink_overlapping_write_scope_fails(self):
        source = self.root / "src"
        outside = self.base / "outside"
        source.mkdir()
        outside.mkdir()
        (source / "escape").symlink_to(outside, target_is_directory=True)
        snapshot = actual_state.capture_repository_snapshot_v3(self.root, self.policy)
        diagnostics = []
        closure_v3._validate_snapshot_symlink_scopes(
            snapshot,
            self.assignment["phase_authorities"],
            "assignment.assignment_phase.result_snapshot",
            diagnostics,
        )
        self.assertIn("symlink_scope_escape", self.codes(diagnostics))

    def test_recorded_symlink_into_excluded_path_fails(self):
        source = self.root / "src"
        private = self.root / "private"
        source.mkdir()
        private.mkdir()
        (source / "alias").symlink_to("../private", target_is_directory=True)
        policy = {
            "schema_version": 3,
            "include_paths": ["."],
            "exclusions": [{"path": "private", "reason": "fixture"}],
            "entry_budget": 100,
        }
        snapshot = actual_state.capture_repository_snapshot_v3(self.root, policy)
        diagnostics = []
        closure_v3._validate_snapshot_symlink_scopes(
            snapshot,
            self.assignment["phase_authorities"],
            "assignment.assignment_phase.result_snapshot",
            diagnostics,
        )
        self.assertIn("symlink_scope_escape", self.codes(diagnostics))

    def test_package_phase_capture_builder_binds_assignment_subject(self):
        snapshot = actual_state.capture_repository_snapshot_v3(self.root, self.policy)
        context_digest = digest_json(self.assignment["context_pack"])
        with mock.patch.object(
            closure_v3, "_command_executable_digest", return_value=self.command_digest,
        ):
            envelope = closure_v3.build_phase_capture_envelope(
                root=self.root,
                phase_id="assignment",
                parent_snapshot_digest="absent",
                snapshot=snapshot,
                captured_at="2026-08-08T09:59:00Z",
                assignment_id=self.assignment["assignment_id"],
                assignment_subject_digest=closure_v3.assignment_subject_digest(
                    self.assignment
                ),
                context_digest=context_digest,
                evidence_root=self.evidence,
                parent_evidence_digest="absent",
                capture_authority_key=self.capture_key,
                capture_authority_key_digest=self.capture_key_digest,
            )
        self.assertEqual(self.assignment["assignment_id"], envelope["subject"]["assignment_id"])
        self.assertEqual(
            closure_v3.assignment_subject_digest(self.assignment),
            envelope["subject"]["assignment_subject_digest"],
        )
        self.assertEqual(context_digest, envelope["subject"]["context_digest"])

    def test_phase_receipts_reject_assignment_authority_scope_replay(self):
        self.assignment["phase_authorities"]["repository_owner"][
            "allowed_edit_scope"
        ] = ["outside", "src"]
        self.refresh_bindings()

        self.assertIn("phase_capture_assignment_subject_mismatch", self.codes(self.validate()))

    def test_phase_capture_builder_never_creates_missing_authority_key(self):
        snapshot = actual_state.capture_repository_snapshot_v3(self.root, self.policy)
        missing = self.base / "missing-capture.key"
        with mock.patch.object(
            closure_v3, "_command_executable_digest", return_value=self.command_digest,
        ), self.assertRaises(FileNotFoundError):
            closure_v3.build_phase_capture_envelope(
                root=self.root,
                phase_id="assignment",
                parent_snapshot_digest="absent",
                snapshot=snapshot,
                captured_at="2026-08-08T09:59:00Z",
                assignment_id=self.assignment["assignment_id"],
                assignment_subject_digest=closure_v3.assignment_subject_digest(
                    self.assignment
                ),
                context_digest=digest_json(self.assignment["context_pack"]),
                evidence_root=self.evidence,
                parent_evidence_digest="absent",
                capture_authority_key=missing,
                capture_authority_key_digest=digest_json("missing"),
            )

    def test_blocking_active_step_gate_cannot_be_bypassed_by_phase_evidence(self):
        context = self.assignment["context_pack"]
        context["dependency_status"] = "waiting"
        context["active_step_gates"] = [{
            "gate_id": "R010-S02-start",
            "source": "R010/S01",
            "dependency": "R010/S02",
            "scope": {"steps": ["R010/S02"], "work_completion": False},
            "result": "waiting",
            "blocking": True,
        }]
        self.refresh_bindings()
        self.assertIn("active_step_dependency_blocking", self.codes(self.validate()))

    def test_closure_step_ref_must_belong_to_assignment_context(self):
        self.manifest["closure_step_ref"] = "R999/S99"
        self.assertIn("closure_step_ref_out_of_scope", self.codes(self.validate()))

    def test_real_snapshot_capture_parse_diff_and_v3_validation_chain(self):
        source = self.root / "src" / "example.py"
        source.parent.mkdir()
        source.write_text("before\n", encoding="utf-8")
        assignment_snapshot = actual_state.capture_repository_snapshot_v3(
            self.root, self.policy, expected_absences=["src/future.py"]
        )
        source.write_text("after\n", encoding="utf-8")
        worker_snapshot = actual_state.capture_repository_snapshot_v3(
            self.root, self.policy, expected_absences=["src/future.py"]
        )
        worker_changes = actual_state.changed_paths_v3(
            assignment_snapshot, worker_snapshot
        )
        worker_artifacts = [artifact_delta(
            "src/example.py",
            before=assignment_snapshot.entry_map["src/example.py"].raw_byte_digest,
            after=worker_snapshot.entry_map["src/example.py"].raw_byte_digest,
        )]

        self.assignment_snapshot = assignment_snapshot
        self.worker_snapshot = worker_snapshot
        self.pre_snapshot = worker_snapshot
        self.live_snapshot = worker_snapshot
        self.assignment = self.make_assignment()
        self.assignment_digest = digest_json(self.assignment)
        self.manifest = {
            "schema_version": 3,
            "closure_stage": "pre_acceptance",
            "closure_target": "step",
            "closure_step_ref": "R010/S02",
            "worker_report": self.make_report(worker_changes, worker_artifacts),
            "worker_phase": {
                "phase_id": "worker",
                "baseline_snapshot_digest": assignment_snapshot.snapshot_digest,
                "result_snapshot": worker_snapshot.to_wire(),
                "capture_evidence": self.capture_evidence(
                    "worker",
                    assignment_snapshot.snapshot_digest,
                    worker_snapshot,
                    "2026-08-08T10:00:00Z",
                ),
                "actor_delta": self.actor_delta(
                    "worker", worker_changes, worker_artifacts
                ),
            },
            "pre_acceptance_closure_phase": {
                "phase_id": "pre_acceptance_closure",
                "baseline_snapshot_digest": worker_snapshot.snapshot_digest,
                "result_snapshot": worker_snapshot.to_wire(),
                "capture_evidence": self.capture_evidence(
                    "pre_acceptance_closure",
                    worker_snapshot.snapshot_digest,
                    worker_snapshot,
                    "2026-08-08T10:01:00Z",
                ),
                "actor_deltas": [self.actor_delta("linker", [])],
            },
            "post_acceptance_phase": None,
            "keystone_closure": {
                "document_sync": self.sync_result(),
                "metadata_sync": self.sync_result(),
                "graph_sync": {},
                "finalization": {"state": "not_started", "evidence": []},
            },
            "coordinator_review": {
                "assignment_id": self.assignment["assignment_id"],
                "assignment_digest": self.assignment_digest,
                "decision": "accept_candidate",
                "main_acceptance_allowed": True,
                "evidence": ["phase chain reviewed"],
            },
        }
        reason = "No canonical graph mutation is required."
        classification = {
            "schema_version": 1,
            "disposition": "not_applicable",
            "delta_set_digest": digest_json(worker_artifacts),
            "reason": reason,
        }
        classification_path = self.evidence / "classification.json"
        classification_path.write_bytes(json_bytes(classification))
        self.manifest["keystone_closure"]["graph_sync"] = {
            "disposition": "not_applicable",
            "state": "not_applicable",
            "reason": reason,
            "classification_path": "classification.json",
            "classification_digest": file_digest(classification_path),
            "delta_set_digest": digest_json(worker_artifacts),
        }
        canonical_linker, canonical_author = closure_v3.package_runner_paths()
        with mock.patch.object(
            closure_v3, "_command_executable_digest", return_value=self.command_digest,
        ):
            diagnostics = closure_v3.validate_v3(
                self.manifest,
                root=self.root,
                assignment=self.assignment,
                assignment_digest=self.assignment_digest,
                evidence_root=self.evidence,
                linker_runner=canonical_linker,
                author_runner=canonical_author,
                timeout_seconds=1.0,
                capture_authority_key=self.capture_key,
                capture_authority_key_digest=self.capture_key_digest,
            )
        self.assertEqual([], diagnostics)


if __name__ == "__main__":
    unittest.main()
