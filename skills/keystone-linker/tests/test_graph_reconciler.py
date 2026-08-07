import hashlib
import unittest
from dataclasses import replace

from graph_runtime.model import (
    ApplicationResult,
    ApplicationStatus,
    AttestationDecision,
    CanonicalMutation,
    ConflictReason,
    Delta,
    DeltaKind,
    Diagnostic,
    Evidence,
    FailureReason,
    GraphSnapshot,
    GraphTransaction,
    Locator,
    MutationEntity,
    MutationEvidence,
    MutationOperation,
    Node,
    NodeKind,
    PatchOwner,
    PatchSurface,
    Relation,
    RelationType,
    Severity,
    SurfaceAttestation,
    SurfacePatch,
    TransactionState,
)
from graph_runtime.planner import PatchSpec, plan_graph_sync
from graph_runtime.reconciler import (
    AttemptHistory,
    begin_application,
    begin_attestation,
    finalize_transaction,
    new_attempt,
    record_application,
    record_attestation,
    resume_application,
)


class GraphReconcilerTests(unittest.TestCase):
    def setUp(self):
        self.node = Node("key.capability.new", NodeKind.CAPABILITY,
                         locator=Locator("00_docs/new.md"))
        self.mutation = CanonicalMutation(MutationOperation.ADD, MutationEntity.NODE,
                                          None, self.node, MutationEvidence.DECLARED)
        self.patch_a = SurfacePatch("patch-a", PatchOwner.AUTHOR,
                                    PatchSurface.DOCUMENT_METADATA, "00_docs/new.md",
                                    "sha256:" + "1" * 64, "doc patch")
        self.patch_b = SurfacePatch("patch-b", PatchOwner.MAIN,
                                    PatchSurface.CODE_ANCHOR, "src/new.py",
                                    "sha256:" + "2" * 64, "code patch")
        self.proposed = GraphTransaction("tx-1", "scope:s02",
                                         canonical_mutations=(self.mutation,),
                                         surface_patches=(self.patch_a, self.patch_b))

    def _confirmed(self):
        transaction = begin_attestation(self.proposed)
        transaction = record_attestation(
            transaction, SurfaceAttestation("patch-a", PatchOwner.AUTHOR,
                                            AttestationDecision.CONFIRM, "author confirms"))
        return record_attestation(
            transaction, SurfaceAttestation("patch-b", PatchOwner.MAIN,
                                            AttestationDecision.CONFIRM, "main confirms"))

    def test_required_confirmations_reach_ready_to_apply(self):
        transaction = self._confirmed()
        self.assertEqual(transaction.state, TransactionState.READY_TO_APPLY)

    def test_reconciler_rejects_boolean_and_float_schema_versions(self):
        for invalid_version in (True, 1.0):
            with self.subTest(value=invalid_version):
                with self.assertRaisesRegex(ValueError, "schema_version"):
                    begin_attestation(replace(
                        self.proposed,
                        schema_version=invalid_version,
                    ))

    def test_observed_mutation_cannot_be_ready_without_owner_confirmation(self):
        observed = replace(self.proposed, canonical_mutations=(replace(
            self.mutation, evidence=MutationEvidence.OBSERVED),))
        awaiting = begin_attestation(observed)
        awaiting = record_attestation(
            awaiting, SurfaceAttestation("patch-a", PatchOwner.AUTHOR,
                                         AttestationDecision.CONFIRM))
        self.assertEqual(awaiting.state, TransactionState.AWAITING_ATTESTATION)

    def test_unrelated_patch_confirmation_cannot_admit_observed_mutation(self):
        unrelated = replace(self.patch_a, patch_id="patch-unrelated",
                            target_path="00_docs/unrelated.md")
        observed = replace(
            self.proposed,
            canonical_mutations=(replace(self.mutation, evidence=MutationEvidence.OBSERVED),),
            surface_patches=(unrelated,),
        )
        awaiting = record_attestation(
            begin_attestation(observed),
            SurfaceAttestation(unrelated.patch_id, PatchOwner.AUTHOR,
                               AttestationDecision.CONFIRM),
        )
        self.assertEqual(awaiting.state, TransactionState.AWAITING_ATTESTATION)

    def test_reject_and_needs_revision_conflict(self):
        for decision in (AttestationDecision.REJECT, AttestationDecision.NEEDS_REVISION):
            with self.subTest(decision=decision):
                awaiting = begin_attestation(self.proposed)
                result = record_attestation(
                    awaiting, SurfaceAttestation("patch-a", PatchOwner.AUTHOR, decision))
                self.assertEqual(result.state, TransactionState.CONFLICTED)
                self.assertEqual(
                    ConflictReason.REJECT if decision == AttestationDecision.REJECT
                    else ConflictReason.NEEDS_REVISION,
                    result.conflict_reason,
                )

    def test_stale_baseline_conflicts_before_application(self):
        result = begin_application(self._confirmed(), {
            "patch-a": "sha256:" + "9" * 64,
            "patch-b": self.patch_b.baseline_digest,
        })
        self.assertEqual(result.state, TransactionState.CONFLICTED)
        self.assertEqual(ConflictReason.STALE_BASELINE, result.conflict_reason)
        self.assertEqual(result.apply_results[0].result, ApplicationStatus.STALE_BASELINE)

    def test_partial_apply_and_resume_preserve_completed_patch(self):
        applying = begin_application(self._confirmed(), {
            "patch-a": self.patch_a.baseline_digest,
            "patch-b": self.patch_b.baseline_digest,
        })
        partial = record_application(
            applying, ApplicationResult("patch-a", ApplicationStatus.APPLIED,
                                        "sha256:" + "a" * 64, "written"))
        self.assertEqual(partial.state, TransactionState.PARTIALLY_APPLIED)

        resumed = resume_application(partial, {
            "patch-a": "sha256:" + "a" * 64,
            "patch-b": self.patch_b.baseline_digest,
        })
        self.assertEqual(resumed.state, TransactionState.APPLYING)
        self.assertEqual(resumed.apply_results, partial.apply_results)
        with self.assertRaisesRegex(ValueError, "already applied"):
            record_application(resumed, ApplicationResult(
                "patch-a", ApplicationStatus.APPLIED, "sha256:" + "b" * 64))

    def test_resume_conflicts_when_applied_result_digest_changed(self):
        applying = begin_application(self._confirmed(), {
            "patch-a": self.patch_a.baseline_digest,
            "patch-b": self.patch_b.baseline_digest,
        })
        partial = record_application(applying, ApplicationResult(
            "patch-a", ApplicationStatus.APPLIED, "sha256:" + "a" * 64))
        resumed = resume_application(partial, {
            "patch-a": "sha256:" + "b" * 64,
            "patch-b": self.patch_b.baseline_digest,
        })
        self.assertEqual(resumed.state, TransactionState.CONFLICTED)

    def test_verified_requires_exact_reconstruction_and_clean_validation(self):
        applying = begin_application(self._confirmed(), {
            "patch-a": self.patch_a.baseline_digest,
            "patch-b": self.patch_b.baseline_digest,
        })
        partial = record_application(applying, ApplicationResult(
            "patch-a", ApplicationStatus.APPLIED, "sha256:" + "a" * 64))
        applying = resume_application(partial, {
            "patch-a": "sha256:" + "a" * 64,
            "patch-b": self.patch_b.baseline_digest,
        })
        applied = record_application(applying, ApplicationResult(
            "patch-b", ApplicationStatus.APPLIED, "sha256:" + "b" * 64))

        mismatch = finalize_transaction(applied, GraphSnapshot(), (), {
            "patch-a": "sha256:" + "a" * 64, "patch-b": "sha256:" + "b" * 64,
        }, baseline_snapshot=GraphSnapshot())
        self.assertEqual(mismatch.state, TransactionState.CONFLICTED)

        validation_failure = finalize_transaction(
            applied, GraphSnapshot(nodes=(self.node,)),
            (Diagnostic("missing_target", "broken", Severity.ERROR),),
            {"patch-a": "sha256:" + "a" * 64, "patch-b": "sha256:" + "b" * 64},
            baseline_snapshot=GraphSnapshot())
        self.assertEqual(validation_failure.state, TransactionState.FAILED)

        verified = finalize_transaction(
            replace(applied, coverage_debt=("legacy metadata gap",)),
            GraphSnapshot(nodes=(self.node,)), (),
            {"patch-a": "sha256:" + "a" * 64, "patch-b": "sha256:" + "b" * 64},
            baseline_snapshot=GraphSnapshot())
        self.assertEqual(verified.state, TransactionState.VERIFIED)
        self.assertEqual(verified.coverage_debt, ("legacy metadata gap",))

    def test_binary_companion_uses_logical_locator_and_physical_patch_through_verify(self):
        node = Node(
            "key.asset.binary",
            NodeKind.OUTPUT_ARTIFACT,
            locator=Locator("assets/model.bin"),
        )
        baseline = "sha256:" + "c" * 64
        delta = Delta(
            DeltaKind.ARTIFACT,
            "assets/model.bin.keystone.json",
            (Locator("assets/model.bin"),),
            "declare binary companion metadata",
            baseline,
        )
        patch = PatchSpec(
            PatchOwner.MAIN,
            PatchSurface.COMPANION_METADATA,
            "assets/model.bin.keystone.json",
            baseline,
            "replace companion metadata",
        )
        proposed = plan_graph_sync(
            GraphSnapshot(),
            (delta,),
            "R008/S04",
            requested_nodes_after=(node,),
            patch_specs=(patch,),
            evidence=Evidence.OBSERVED,
            transaction_schema_version=1,
        )
        patch_id = proposed.surface_patches[0].patch_id
        awaiting = begin_attestation(proposed)
        ready = record_attestation(
            awaiting,
            SurfaceAttestation(
                patch_id,
                PatchOwner.MAIN,
                AttestationDecision.CONFIRM,
                "main confirms companion semantics",
            ),
        )
        applying = begin_application(ready, {patch_id: baseline})
        applied = record_application(
            applying,
            ApplicationResult(
                patch_id,
                ApplicationStatus.APPLIED,
                "sha256:" + "d" * 64,
                "companion written",
            ),
        )
        verified = finalize_transaction(
            applied,
            GraphSnapshot(nodes=(node,)),
            (),
            {patch_id: "sha256:" + "d" * 64},
            baseline_snapshot=GraphSnapshot(),
        )

        self.assertEqual(TransactionState.VERIFIED, verified.state)
        self.assertEqual("assets/model.bin", node.locator.path)
        self.assertEqual(
            "assets/model.bin.keystone.json",
            verified.surface_patches[0].target_path,
        )

    def test_reconstruction_rejects_unintended_unchanged_graph_difference(self):
        applying = begin_application(self._confirmed(), {
            "patch-a": self.patch_a.baseline_digest,
            "patch-b": self.patch_b.baseline_digest,
        })
        partial = record_application(applying, ApplicationResult(
            "patch-a", ApplicationStatus.APPLIED, "sha256:" + "a" * 64))
        applying = resume_application(partial, {
            "patch-a": "sha256:" + "a" * 64,
            "patch-b": self.patch_b.baseline_digest,
        })
        applied = record_application(applying, ApplicationResult(
            "patch-b", ApplicationStatus.APPLIED, "sha256:" + "b" * 64))
        unrelated = Node("key.capability.existing", NodeKind.CAPABILITY,
                         locator=Locator("00_docs/existing.md"))
        existing_test = Node("key.test.existing", NodeKind.OUTPUT_ARTIFACT,
                             locator=Locator("tests/test_existing.py"))
        existing_relation = Relation(existing_test.id, RelationType.VERIFIES,
                                     unrelated.id, Evidence.DECLARED)

        result = finalize_transaction(
            applied, GraphSnapshot(nodes=(self.node,)), (),
            {"patch-a": "sha256:" + "a" * 64, "patch-b": "sha256:" + "b" * 64},
            baseline_snapshot=GraphSnapshot(
                nodes=(unrelated, existing_test), relations=(existing_relation,)),
        )
        self.assertEqual(result.state, TransactionState.CONFLICTED)

    def test_failed_application_never_verifies(self):
        applying = begin_application(self._confirmed(), {
            "patch-a": self.patch_a.baseline_digest,
            "patch-b": self.patch_b.baseline_digest,
        })
        failed = record_application(
            applying, ApplicationResult("patch-a", ApplicationStatus.FAILED, evidence="io error"))
        self.assertEqual(failed.state, TransactionState.FAILED)
        with self.assertRaisesRegex(ValueError, "applying"):
            finalize_transaction(failed, GraphSnapshot(nodes=(self.node,)), (), {},
                                 baseline_snapshot=GraphSnapshot())

    def test_reject_or_revision_retry_allows_same_baseline_with_changed_patch(self):
        conflicted = record_attestation(
            begin_attestation(self.proposed),
            SurfaceAttestation("patch-a", PatchOwner.AUTHOR, AttestationDecision.REJECT))
        revised = replace(self.proposed, transaction_id="tx-2", surface_patches=(
            replace(self.patch_a, exact_patch="revised doc patch"), self.patch_b))
        history = new_attempt(AttemptHistory(conflicted), revised)
        self.assertEqual(history.current.state, TransactionState.PROPOSED)
        self.assertEqual(history.prior_attempts, (conflicted,))
        with self.assertRaisesRegex(ValueError, "changed mutation or patch"):
            new_attempt(AttemptHistory(conflicted), replace(self.proposed, transaction_id="tx-3"))

    def test_stale_baseline_retry_requires_new_baseline(self):
        conflicted = begin_application(self._confirmed(), {
            "patch-a": "sha256:" + "9" * 64,
            "patch-b": self.patch_b.baseline_digest,
        })
        with self.assertRaisesRegex(ValueError, "new baseline"):
            new_attempt(AttemptHistory(conflicted), replace(self.proposed, transaction_id="tx-stale"))
        revised = replace(self.proposed, transaction_id="tx-stale-2", surface_patches=(
            replace(self.patch_a, baseline_digest="sha256:" + "9" * 64), self.patch_b))
        self.assertEqual(TransactionState.PROPOSED,
                         new_attempt(AttemptHistory(conflicted), revised).current.state)

    def test_failed_transient_retry_may_keep_baseline_and_preserves_history(self):
        failed = replace(self.proposed, state=TransactionState.FAILED,
                         failure_reason=FailureReason.TRANSIENT_IO,
                         apply_results=(ApplicationResult(
                             "patch-a", ApplicationStatus.FAILED, evidence="transient io"),))
        retry = replace(self.proposed, transaction_id="tx-retry")
        history = new_attempt(AttemptHistory(failed), retry)
        self.assertEqual(history.current.state, TransactionState.PROPOSED)
        self.assertEqual(history.prior_attempts, (failed,))
        self.assertEqual(history.prior_attempts[0].apply_results[0].evidence, "transient io")

    def test_non_transient_failed_retry_requires_changed_input(self):
        failed = replace(
            self.proposed,
            state=TransactionState.FAILED,
            failure_reason=FailureReason.PERMISSION_DENIED,
            apply_results=(ApplicationResult(
                "patch-a", ApplicationStatus.FAILED, evidence="permission denied"
            ),),
        )
        unchanged = replace(self.proposed, transaction_id="tx-retry-denied")

        with self.assertRaisesRegex(ValueError, "non-transient"):
            new_attempt(AttemptHistory(failed), unchanged)

        changed = replace(
            unchanged,
            surface_patches=(replace(self.patch_a, exact_patch="changed"), self.patch_b),
        )
        self.assertEqual(
            TransactionState.PROPOSED,
            new_attempt(AttemptHistory(failed), changed).current.state,
        )

    def test_finalize_requires_authoritative_baseline_snapshot(self):
        with self.assertRaises(TypeError):
            finalize_transaction(self.proposed, GraphSnapshot(), (), {})

    def test_runtime_rejects_graph_change_without_required_patch(self):
        optional = replace(self.patch_a, required=False)
        invalid = replace(self.proposed, surface_patches=(optional,))
        with self.assertRaisesRegex(ValueError, "required patch"):
            begin_attestation(invalid)

    def test_runtime_rejects_owner_surface_pairing_like_planner(self):
        invalid_patch = replace(self.patch_a, owner=PatchOwner.MAIN)
        invalid = replace(self.proposed, surface_patches=(invalid_patch,))
        with self.assertRaisesRegex(ValueError, "owner.*surface"):
            begin_attestation(invalid)

    def test_runtime_rejects_duplicate_physical_patch_target(self):
        duplicate = replace(
            self.patch_a,
            patch_id="patch-duplicate",
            owner=PatchOwner.AUTHOR,
            surface=PatchSurface.COMPANION_METADATA,
            target_path=self.patch_a.target_path,
        )
        invalid = replace(self.proposed, surface_patches=(self.patch_a, duplicate))

        with self.assertRaisesRegex(ValueError, "physical target"):
            begin_attestation(invalid)

    def test_runtime_rejects_noncanonical_physical_target_alias(self):
        alias = replace(
            self.patch_a,
            patch_id="patch-alias",
            target_path="00_docs/../00_docs/feature.md",
        )
        invalid = replace(self.proposed, surface_patches=(self.patch_a, alias))

        with self.assertRaisesRegex(ValueError, "canonical repository-relative"):
            begin_attestation(invalid)

    def test_schema_v2_application_digest_must_match_planned_digest(self):
        baseline_content = "before\n"
        baseline_digest = "sha256:" + hashlib.sha256(
            baseline_content.encode("utf-8")
        ).hexdigest()
        expected = "sha256:" + hashlib.sha256(b"after\n").hexdigest()
        patch = replace(
            self.patch_a,
            baseline_digest=baseline_digest,
            exact_patch="after\n",
            patch_format="full_replacement",
            patch_body="after\n",
            expected_after_digest=expected,
            baseline_content=baseline_content,
        )
        proposed = replace(
            self.proposed,
            surface_patches=(patch,),
            schema_version=2,
        )
        ready = record_attestation(
            begin_attestation(proposed),
            SurfaceAttestation(
                patch.patch_id,
                PatchOwner.AUTHOR,
                AttestationDecision.CONFIRM,
                "confirmed",
            ),
        )
        applying = begin_application(ready, {patch.patch_id: patch.baseline_digest})

        with self.assertRaisesRegex(ValueError, "expected_after_digest"):
            record_application(
                applying,
                ApplicationResult(
                    patch.patch_id,
                    ApplicationStatus.APPLIED,
                    "sha256:" + "f" * 64,
                    "written",
                ),
            )

    def test_finalize_defends_against_forged_schema_v2_result_digest(self):
        baseline_content = "before\n"
        baseline_digest = "sha256:" + hashlib.sha256(
            baseline_content.encode("utf-8")
        ).hexdigest()
        expected = "sha256:" + hashlib.sha256(b"after\n").hexdigest()
        patch = replace(
            self.patch_a,
            baseline_digest=baseline_digest,
            exact_patch="after\n",
            patch_format="full_replacement",
            patch_body="after\n",
            expected_after_digest=expected,
            baseline_content=baseline_content,
        )
        attestation = SurfaceAttestation(
            patch.patch_id,
            PatchOwner.AUTHOR,
            AttestationDecision.CONFIRM,
            "confirmed",
        )
        forged = replace(
            self.proposed,
            surface_patches=(patch,),
            attestations=(attestation,),
            apply_results=(ApplicationResult(
                patch.patch_id,
                ApplicationStatus.APPLIED,
                "sha256:" + "b" * 64,
                "forged",
            ),),
            state=TransactionState.APPLYING,
            schema_version=2,
        )

        with self.assertRaisesRegex(ValueError, "expected_after_digest"):
            finalize_transaction(
                forged,
                GraphSnapshot(nodes=(self.node,)),
                (),
                {patch.patch_id: "sha256:" + "b" * 64},
                baseline_snapshot=GraphSnapshot(),
            )


if __name__ == "__main__":
    unittest.main()
