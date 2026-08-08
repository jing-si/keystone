import hashlib
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from graph_runtime.model import (
    ApplicationResult,
    ApplicationStatus,
    ApprovalState,
    ArtifactKind,
    AttestationDecision,
    CanonicalMutation,
    ConflictReason,
    Diagnostic,
    Delta,
    DeltaKind,
    Evidence,
    GraphRelevance,
    GraphSnapshot,
    GraphTransaction,
    Lifecycle,
    Locator,
    MutationEntity,
    MutationOperation,
    Node,
    NodeKind,
    PatchOwner,
    PatchSurface,
    Provenance,
    Severity,
    SurfaceAttestation,
    SurfacePatch,
    TransactionState,
    attempt_history_wire,
    transaction_wire,
)
from graph_runtime.reconciler import AttemptHistory
from graph_runtime.validator import validate_transaction


class GraphWireTest(unittest.TestCase):
    def setUp(self):
        self.node = Node(
            "key.code.wire", NodeKind.OUTPUT_ARTIFACT, ArtifactKind.CODE,
            Locator("src/wire.py", symbol="wire"), Lifecycle.ACTIVE,
            Provenance(surface="code_anchor", locator=Locator("src/wire.py", symbol="wire")),
        )
        self.patch = SurfacePatch(
            "patch-wire", PatchOwner.MAIN, PatchSurface.CODE_ANCHOR, "src/wire.py",
            "sha256:" + "1" * 64, "add graph anchor", True,
        )
        self.verified = GraphTransaction(
            "tx-wire", "R005/S03", canonical_mutations=(CanonicalMutation(
                MutationOperation.ADD, MutationEntity.NODE, None, self.node, Evidence.DECLARED),),
            surface_patches=(self.patch,),
            attestations=(SurfaceAttestation(
                "patch-wire", PatchOwner.MAIN, AttestationDecision.CONFIRM, "owner confirmed meaning"),),
            apply_results=(ApplicationResult(
                "patch-wire", ApplicationStatus.APPLIED, "sha256:" + "2" * 64,
                "source write completed"),),
            state=TransactionState.VERIFIED,
            reconstruction=GraphSnapshot(nodes=(self.node,)),
        )

    def test_verified_model_serializes_to_validator_canonical_wire(self):
        baseline = GraphSnapshot()
        wire = transaction_wire(self.verified, baseline_snapshot=baseline)

        self.assertEqual({"baseline", "result"}, set(wire["reconstruction"]))
        self.assertEqual("pass", wire["mechanical_validation"]["status"])
        self.assertEqual([], wire["mechanical_validation"]["diagnostics"])
        self.assertEqual((), validate_transaction(
            wire, source_snapshot=self.verified.reconstruction))

    def test_transaction_schema_version_rejects_boolean_and_float_values(self):
        baseline = GraphSnapshot()
        valid_wire = transaction_wire(self.verified, baseline_snapshot=baseline)

        for invalid_version in (True, 1.0):
            with self.subTest(boundary="validation", value=invalid_version):
                invalid_wire = dict(valid_wire, schema_version=invalid_version)
                self.assertIn(
                    "transaction_schema_invalid",
                    {
                        item.code for item in validate_transaction(
                            invalid_wire,
                            source_snapshot=self.verified.reconstruction,
                        )
                    },
                )
            with self.subTest(boundary="serialization", value=invalid_version):
                invalid_transaction = replace(
                    self.verified,
                    schema_version=invalid_version,
                )
                with self.assertRaisesRegex(ValueError, "schema_version"):
                    transaction_wire(
                        invalid_transaction,
                        baseline_snapshot=baseline,
                    )

    # keystone: id=key.test.linker.graph-transaction-wire-contract kind=output_artifact artifact_kind=test verifies=key.code.linker.graph-transaction-validator locator.test_name=test_schema_v2_transaction_round_trips_canonical_lifecycle_wire
    def test_schema_v2_transaction_round_trips_canonical_lifecycle_wire(self):
        body = "after\n"
        digest = "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
        patch = SurfacePatch(
            "patch-wire-v2", PatchOwner.MAIN, PatchSurface.CODE_ANCHOR,
            "src/wire.py", "absent", body, True,
            patch_format="full_replacement", patch_body=body,
            expected_after_digest=digest, baseline_content=None,
        )
        transaction = GraphTransaction(
            "tx-wire-v2", "R008/S06",
            input_deltas=(Delta(
                DeltaKind.ARTIFACT,
                patch.target_path,
                (Locator(patch.target_path, symbol="wire"),),
                "bind executable patch",
                patch.baseline_digest,
            ),),
            canonical_mutations=(CanonicalMutation(
                MutationOperation.ADD, MutationEntity.NODE, None, self.node,
                Evidence.DECLARED,
            ),),
            surface_patches=(patch,),
            attestations=(SurfaceAttestation(
                patch.patch_id, PatchOwner.MAIN, AttestationDecision.CONFIRM,
                "owner confirmed meaning",
            ),),
            apply_results=(ApplicationResult(
                patch.patch_id, ApplicationStatus.APPLIED, digest,
                "source write completed",
            ),),
            state=TransactionState.VERIFIED,
            reconstruction=GraphSnapshot(nodes=(self.node,)),
            schema_version=2,
        )

        wire = transaction_wire(transaction, baseline_snapshot=GraphSnapshot())

        self.assertEqual(2, wire["reconstruction"]["baseline"]["schema_version"])
        self.assertEqual(
            "artifact",
            wire["canonical_mutations"][0]["after"]["lifecycle_domain"],
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/wire.py").write_text(body, encoding="utf-8")
            self.assertEqual((), validate_transaction(
                wire,
                root=root,
                source_snapshot=transaction.reconstruction,
            ))

        rootless_codes = {
            item.code for item in validate_transaction(
                wire,
                source_snapshot=transaction.reconstruction,
            )
        }
        sourceless_codes = {
            item.code for item in validate_transaction(wire, root=Path(directory))
        }
        self.assertTrue({
            "actual_state_unverified",
            "verified_actual_state_root_missing",
        } <= rootless_codes)
        self.assertIn("verified_source_snapshot_missing", sourceless_codes)

    def test_unfinished_and_failed_states_round_trip_without_promotion(self):
        proposed = GraphTransaction("tx-proposed", "R005/S03")
        proposed_wire = transaction_wire(proposed)
        self.assertEqual("proposed", proposed_wire["state"])
        self.assertIsNone(proposed_wire["reconstruction"])
        self.assertEqual((), validate_transaction(proposed_wire))

        failed = GraphTransaction(
            "tx-failed", "R005/S03", state=TransactionState.FAILED,
            mechanical_validation=(Diagnostic("broken", "broken graph", Severity.ERROR),),
        )
        failed_wire = transaction_wire(failed)
        self.assertEqual("failed", failed_wire["state"])
        self.assertEqual("fail", failed_wire["mechanical_validation"]["status"])
        self.assertEqual((), validate_transaction(failed_wire))

        conflicted = GraphTransaction(
            "tx-conflicted", "R007/S04", state=TransactionState.CONFLICTED,
            conflict_reason=ConflictReason.NEEDS_REVISION,
            surface_patches=(self.patch,),
            attestations=(SurfaceAttestation(
                "patch-wire", PatchOwner.MAIN, AttestationDecision.NEEDS_REVISION,
                "patch wording must change"),),
        )
        conflicted_wire = transaction_wire(conflicted)
        self.assertEqual("needs_revision", conflicted_wire["conflict_reason"])
        self.assertEqual((), validate_transaction(conflicted_wire))

    def test_v1_wire_cannot_hide_v2_patch_fields_or_path_aliases(self):
        mixed = replace(
            self.patch,
            patch_format="full_replacement",
            patch_body="after\n",
            expected_after_digest="sha256:" + "a" * 64,
            baseline_content="before\n",
        )
        with self.assertRaisesRegex(ValueError, "schema-v1 patch"):
            transaction_wire(GraphTransaction(
                "tx-mixed", "R010/S01", surface_patches=(mixed,)
            ))

        alias = replace(
            self.patch,
            patch_id="patch-alias",
            target_path="src/../src/wire.py",
        )
        with self.assertRaisesRegex(ValueError, "canonical repository-relative"):
            transaction_wire(GraphTransaction(
                "tx-alias", "R010/S01", surface_patches=(self.patch, alias)
            ))

    def test_transaction_rejects_unknown_root_fields(self):
        payload = transaction_wire(GraphTransaction("tx-unknown", "key.work.scope"))
        payload["mystery"] = True

        self.assertTrue(any(item.code == "transaction_unknown_field"
                            for item in validate_transaction(payload)))

    def test_effective_metadata_node_is_canonical_transaction_wire(self):
        node = Node(
            "key.doc.old", NodeKind.SOURCE_DOCUMENT, locator=Locator("old.md"),
            lifecycle=Lifecycle.ARCHIVED,
            approval_state=ApprovalState.REJECTED,
            source_authority=(("source", "project-standard"),),
            declared_lifecycle=Lifecycle.ARCHIVED,
            declared_approval_state=ApprovalState.REJECTED,
            declared_governed_by=("key.standard.project",),
            declared_source_authority=(("source", "project-standard"),),
        )
        transaction = GraphTransaction(
            "tx-metadata", "key.work.scope",
            canonical_mutations=(CanonicalMutation(
                MutationOperation.ADD, MutationEntity.NODE, None, node, Evidence.DECLARED),),
        )

        codes = {item.code for item in validate_transaction(transaction_wire(transaction))}
        self.assertNotIn("mutation_node_invalid", codes)

    def test_history_and_graph_relevance_are_outside_transaction_wire(self):
        proposed = GraphTransaction("tx-current", "R005/S03")
        history = AttemptHistory(proposed, (self.verified,))
        envelope = attempt_history_wire(
            history,
            GraphRelevance(True, "required", "changed code anchor has declared graph metadata"),
            prior_baselines=(GraphSnapshot(),),
        )

        self.assertEqual({"schema_version", "graph_relevance", "transaction", "prior_attempts"},
                         set(envelope))
        self.assertNotIn("prior_attempts", envelope["transaction"])
        self.assertNotIn("graph_relevance", envelope["transaction"])
        self.assertEqual("required", envelope["graph_relevance"]["disposition"])
        self.assertEqual("verified", envelope["prior_attempts"][0]["state"])
        self.assertEqual((), validate_transaction(envelope["transaction"]))


if __name__ == "__main__":
    unittest.main()
