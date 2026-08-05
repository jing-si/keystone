import unittest

from graph_runtime.model import (
    ApplicationResult,
    ApplicationStatus,
    ArtifactKind,
    AttestationDecision,
    CanonicalMutation,
    Diagnostic,
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
