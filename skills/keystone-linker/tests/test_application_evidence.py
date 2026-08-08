import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


LINKER_ROOT = Path(__file__).parents[1]
SCRIPTS = LINKER_ROOT / "scripts"
REPOSITORY_ROOT = LINKER_ROOT.parents[1]
AUTHOR_RUNNER = (
    REPOSITORY_ROOT
    / "skills"
    / "keystone-author"
    / "scripts"
    / "run_owned_surface_apply.py"
)
sys.path.insert(0, str(SCRIPTS))

from graph_runtime.application_evidence import (  # noqa: E402
    application_plan_digest,
    validate_application_evidence,
)
import graph_runtime.application_evidence as application_evidence  # noqa: E402
from graph_runtime.model import (  # noqa: E402
    ApplicationResult,
    ApplicationStatus,
    ArtifactKind,
    AttestationDecision,
    Delta,
    DeltaKind,
    GraphSnapshot,
    Locator,
    Node,
    NodeKind,
    PatchOwner,
    PatchSurface,
    Provenance,
    SurfaceAttestation,
    TransactionState,
)
from graph_runtime.planner import PatchSpec, plan_graph_sync  # noqa: E402
from graph_runtime.reconciler import (  # noqa: E402
    begin_application,
    begin_attestation,
    finalize_transaction,
    record_application,
    record_attestation,
)
from graph_runtime.wire import transaction_wire  # noqa: E402


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()


class ApplicationEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / "repository"
        self.evidence_root = self.base / "evidence"
        self.root.mkdir()
        self.evidence_root.mkdir()
        self.key = self.base / "author.key"
        self.key.write_bytes(b"author-application-evidence-test-key-material")
        self.key.chmod(0o600)
        self.key_digest = digest_bytes(self.key.read_bytes())
        self.target = self.root / "00_docs" / "work.md"
        self.target.parent.mkdir(parents=True)
        self.target.write_text("before\n", encoding="utf-8")
        self.patch = {
            "patch_id": "patch-author",
            "owner": "author",
            "surface": "document_metadata",
            "target_path": "00_docs/work.md",
            "baseline_digest": digest_bytes(b"before\n"),
            "baseline_content": "before\n",
            "exact_patch": "after\n",
            "patch_format": "full_replacement",
            "patch_body": "after\n",
            "expected_after_digest": digest_bytes(b"after\n"),
            "required": True,
        }
        empty = {"schema_version": 2, "nodes": [], "relations": []}
        self.transaction = {
            "schema_version": 2,
            "transaction_id": "transaction-1",
            "scope_ref": "R010/S03",
            "input_deltas": [],
            "canonical_mutations": [],
            "surface_patches": [self.patch],
            "attestations": [{
                "patch_id": "patch-author",
                "owner": "author",
                "decision": "confirm",
                "evidence": "Author confirmed the exact patch.",
            }],
            "apply_results": [{
                "patch_id": "patch-author",
                "result": "applied",
                "resulting_digest": self.patch["expected_after_digest"],
                "evidence": "Trusted owner apply receipt.",
            }],
            "state": "verified",
            "conflict_reason": None,
            "failure_reason": None,
            "reconstruction": {"baseline": empty, "result": empty},
            "mechanical_validation": {
                "schema_version": 1,
                "status": "pass",
                "diagnostics": [],
                "summary": {"errors": 0, "warnings": 0},
            },
            "coverage_debt": [],
        }
        self.assignment_id = "assignment-1"
        self.assignment_digest = digest_bytes(b"assignment")
        self.phase_baseline = digest_bytes(b"phase-baseline")
        self.phase_parent = digest_bytes(b"phase-parent")
        self.scope = {"allowed": ["00_docs"], "excluded": []}

    def tearDown(self):
        self.temporary.cleanup()

    def write_receipt(self):
        request = {
            "schema_version": 1,
            "transaction_id": self.transaction["transaction_id"],
            "transaction_digest": application_plan_digest(self.transaction),
            "assignment_id": self.assignment_id,
            "assignment_digest": self.assignment_digest,
            "phase_id": "pre_acceptance_closure",
            "phase_baseline_snapshot_digest": self.phase_baseline,
            "phase_parent_evidence_digest": self.phase_parent,
            "repository_root_digest": digest_bytes(canonical_bytes({
                "repository_root": str(self.root.resolve(strict=True)),
            })),
            "owner": "author",
            "scope": self.scope,
            "scope_digest": digest_bytes(canonical_bytes(self.scope)),
            "prior_receipt_digest": "absent",
            "patch": self.patch,
        }
        request_path = self.evidence_root / "request.json"
        request_path.write_bytes(canonical_bytes(request))
        receipt_path = self.evidence_root / "receipts" / "author.json"
        receipt_path.parent.mkdir()
        process = subprocess.run(
            [
                sys.executable,
                str(AUTHOR_RUNNER),
                "--root",
                str(self.root),
                "--request",
                str(request_path),
                "--evidence-root",
                str(self.evidence_root),
                "--output",
                str(receipt_path),
                "--authority-key",
                str(self.key),
                "--pinned-key-sha256",
                self.key_digest,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        aggregate = {
            "schema_version": 1,
            "transaction_id": self.transaction["transaction_id"],
            "transaction_digest": application_plan_digest(self.transaction),
            "repository_root_digest": request["repository_root_digest"],
            "assignment_id": self.assignment_id,
            "assignment_digest": self.assignment_digest,
            "receipts": [{
                "path": "receipts/author.json",
                "digest": digest_bytes(receipt_path.read_bytes()),
            }],
        }
        aggregate_path = self.evidence_root / "application.json"
        aggregate_path.write_bytes(canonical_bytes(aggregate))
        return aggregate_path, aggregate

    def validate(self, aggregate_path, aggregate):
        return validate_application_evidence(
            transaction=self.transaction,
            application_evidence={
                "path": aggregate_path.relative_to(self.evidence_root).as_posix(),
                "digest": digest_bytes(aggregate_path.read_bytes()),
            },
            root=self.root,
            evidence_root=self.evidence_root,
            owner_keys={"author": self.key},
            owner_key_digests={"author": self.key_digest},
        )

    def test_real_author_receipt_is_verified(self):
        aggregate_path, aggregate = self.write_receipt()

        result = self.validate(aggregate_path, aggregate)

        self.assertEqual((), result.diagnostics)
        self.assertIsNotNone(result.evidence)
        self.assertEqual("patch-author", result.evidence.receipts[0].patch_id)

    def test_tampered_receipt_and_missing_receipt_fail_closed(self):
        aggregate_path, aggregate = self.write_receipt()
        receipt_path = self.evidence_root / aggregate["receipts"][0]["path"]
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["subject"]["assignment_id"] = "substituted"
        receipt_path.write_bytes(canonical_bytes(receipt))
        aggregate["receipts"][0]["digest"] = digest_bytes(receipt_path.read_bytes())
        aggregate_path.write_bytes(canonical_bytes(aggregate))

        tampered = self.validate(aggregate_path, aggregate)
        missing = copy.deepcopy(aggregate)
        missing["receipts"] = []
        aggregate_path.write_bytes(canonical_bytes(missing))
        missing_result = self.validate(aggregate_path, missing)

        tampered_codes = {item.code for item in tampered.diagnostics}
        missing_codes = {item.code for item in missing_result.diagnostics}
        self.assertIn("application_receipt_mac_invalid", tampered_codes)
        self.assertIn("application_receipt_cardinality_mismatch", missing_codes)

    def test_plan_digest_excludes_dynamic_attestation_and_result_state(self):
        expected = application_plan_digest(self.transaction)
        changed = copy.deepcopy(self.transaction)
        changed["state"] = "failed"
        changed["attestations"] = []
        changed["apply_results"] = []
        changed["coverage_debt"] = ["late verification output"]
        changed["mechanical_validation"] = None

        self.assertEqual(expected, application_plan_digest(changed))

        changed["surface_patches"][0]["patch_body"] = "substituted\n"
        self.assertNotEqual(expected, application_plan_digest(changed))

    def test_planner_origin_digest_stays_stable_through_verified_evidence(self):
        baseline = GraphSnapshot(schema_version=2)
        node = Node(
            "key.doc.application-plan",
            NodeKind.SOURCE_DOCUMENT,
            ArtifactKind.NONE,
            Locator("00_docs/work.md"),
            provenance=Provenance(
                surface="document_metadata",
                locator=Locator("00_docs/work.md"),
            ),
        )
        delta = Delta(
            DeltaKind.DOCUMENT,
            "00_docs/work.md",
            (Locator("00_docs/work.md"),),
            "declare application plan evidence",
            self.patch["baseline_digest"],
        )
        planned = plan_graph_sync(
            baseline,
            (delta,),
            "R010/S03",
            requested_nodes_after=(node,),
            patch_specs=(PatchSpec(
                PatchOwner.AUTHOR,
                PatchSurface.DOCUMENT_METADATA,
                self.patch["target_path"],
                self.patch["baseline_digest"],
                self.patch["exact_patch"],
                patch_format=self.patch["patch_format"],
                patch_body=self.patch["patch_body"],
                expected_after_digest=self.patch["expected_after_digest"],
                baseline_content=self.patch["baseline_content"],
            ),),
        )
        ready = record_attestation(
            begin_attestation(planned),
            SurfaceAttestation(
                planned.surface_patches[0].patch_id,
                PatchOwner.AUTHOR,
                AttestationDecision.CONFIRM,
                "Owner confirmed the exact patch.",
            ),
        )
        self.assertEqual(TransactionState.READY_TO_APPLY, ready.state)
        ready_wire = transaction_wire(ready)
        planner_digest = application_plan_digest(ready_wire)

        applying = begin_application(
            ready,
            {ready.surface_patches[0].patch_id: self.patch["baseline_digest"]},
        )
        applied = record_application(
            applying,
            ApplicationResult(
                ready.surface_patches[0].patch_id,
                ApplicationStatus.APPLIED,
                self.patch["expected_after_digest"],
                "Authenticated owner receipt.",
            ),
        )
        verified = finalize_transaction(
            applied,
            GraphSnapshot(nodes=(node,), schema_version=2),
            (),
            {ready.surface_patches[0].patch_id: self.patch["expected_after_digest"]},
            baseline_snapshot=baseline,
        )
        self.assertEqual(TransactionState.VERIFIED, verified.state)
        verified_wire = transaction_wire(
            verified,
            baseline_snapshot=baseline,
        )
        self.assertEqual(
            planner_digest,
            application_plan_digest(verified_wire),
        )

        changed_mutation = copy.deepcopy(verified_wire)
        changed_mutation["canonical_mutations"][0]["evidence"] = "observed"
        changed_patch = copy.deepcopy(verified_wire)
        changed_patch["surface_patches"][0]["patch_body"] = "substituted\n"
        self.assertNotEqual(
            planner_digest,
            application_plan_digest(changed_mutation),
        )
        self.assertNotEqual(
            planner_digest,
            application_plan_digest(changed_patch),
        )

    def test_distinct_applied_owners_cannot_share_one_key_fingerprint(self):
        second_patch = {
            "patch_id": "patch-coordinator",
            "owner": "coordinator",
            "surface": "code_anchor",
            "target_path": "src/example.py",
            "baseline_digest": "absent",
            "baseline_content": None,
            "exact_patch": "value = 1\n",
            "patch_format": "full_replacement",
            "patch_body": "value = 1\n",
            "expected_after_digest": digest_bytes(b"value = 1\n"),
            "required": True,
        }
        self.transaction["surface_patches"].append(second_patch)
        self.transaction["attestations"].append({
            "patch_id": second_patch["patch_id"],
            "owner": "coordinator",
            "decision": "confirm",
            "evidence": "Coordinator confirmed the patch.",
        })
        self.transaction["apply_results"].append({
            "patch_id": second_patch["patch_id"],
            "result": "applied",
            "resulting_digest": second_patch["expected_after_digest"],
            "evidence": "Trusted receipt.",
        })
        aggregate = {
            "schema_version": 1,
            "transaction_id": self.transaction["transaction_id"],
            "transaction_digest": application_plan_digest(self.transaction),
            "repository_root_digest": digest_bytes(canonical_bytes({
                "repository_root": str(self.root.resolve(strict=True)),
            })),
            "assignment_id": self.assignment_id,
            "assignment_digest": self.assignment_digest,
            "receipts": [],
        }
        aggregate_path = self.evidence_root / "same-key-application.json"
        aggregate_path.write_bytes(canonical_bytes(aggregate))

        result = validate_application_evidence(
            transaction=self.transaction,
            application_evidence={
                "path": aggregate_path.name,
                "digest": digest_bytes(aggregate_path.read_bytes()),
            },
            root=self.root,
            evidence_root=self.evidence_root,
            owner_keys={"author": self.key, "coordinator": self.key},
            owner_key_digests={
                "author": self.key_digest,
                "coordinator": self.key_digest,
            },
        )

        self.assertIn(
            "application_owner_key_separation_required",
            {item.code for item in result.diagnostics},
        )

    def test_excessive_json_nesting_is_reported_for_aggregate_and_receipt(self):
        deeply_nested = ("[" * 2000 + "0" + "]" * 2000).encode("ascii")
        aggregate_path = self.evidence_root / "application.json"
        aggregate_path.write_bytes(deeply_nested)

        aggregate_result = validate_application_evidence(
            transaction=self.transaction,
            application_evidence={
                "path": aggregate_path.name,
                "digest": digest_bytes(deeply_nested),
            },
            root=self.root,
            evidence_root=self.evidence_root,
            owner_keys={"author": self.key},
            owner_key_digests={"author": self.key_digest},
        )

        receipt_path = self.evidence_root / "nested-receipt.json"
        receipt_path.write_bytes(deeply_nested)
        aggregate = {
            "schema_version": 1,
            "transaction_id": self.transaction["transaction_id"],
            "transaction_digest": application_plan_digest(self.transaction),
            "repository_root_digest": digest_bytes(canonical_bytes({
                "repository_root": str(self.root.resolve(strict=True)),
            })),
            "assignment_id": self.assignment_id,
            "assignment_digest": self.assignment_digest,
            "receipts": [{
                "path": receipt_path.name,
                "digest": digest_bytes(deeply_nested),
            }],
        }
        aggregate_path.write_bytes(canonical_bytes(aggregate))
        receipt_result = self.validate(aggregate_path, aggregate)

        self.assertIn(
            "application_evidence_invalid",
            {item.code for item in aggregate_result.diagnostics},
        )
        self.assertIn(
            "application_receipt_invalid",
            {item.code for item in receipt_result.diagnostics},
        )

    def test_receipt_read_rejects_detached_ancestor_directory(self):
        receipts = self.evidence_root / "receipts"
        receipts.mkdir()
        receipt_path = receipts / "receipt.json"
        receipt_path.write_bytes(b"receipt-bytes")
        original_read = application_evidence.os.read
        replaced = False

        def replace_ancestor(file_descriptor, size):
            nonlocal replaced
            chunk = original_read(file_descriptor, size)
            if not replaced:
                replaced = True
                receipts.rename(self.evidence_root / "detached-receipts")
                receipts.mkdir()
                (receipts / "receipt.json").write_bytes(b"replacement")
            return chunk

        with mock.patch.object(
            application_evidence.os,
            "read",
            side_effect=replace_ancestor,
        ), self.assertRaisesRegex(OSError, "ancestor chain changed"):
            application_evidence._read_relative_single_link(
                self.evidence_root, "receipts/receipt.json"
            )


if __name__ == "__main__":
    unittest.main()
