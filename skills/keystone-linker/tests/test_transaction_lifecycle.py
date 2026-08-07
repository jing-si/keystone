import unittest
from dataclasses import replace

from graph_runtime.transaction_evidence import TransactionEvidence
from graph_runtime.transaction_input import TransactionInput
from graph_runtime.transaction_lifecycle import validate_transaction_lifecycle


class TransactionLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.empty_evidence = TransactionEvidence(
            patches=(),
            attestations=(),
            results=(),
            required_patch_ids=frozenset(),
            confirmed_patch_ids=frozenset(),
            rejected_patch_ids=frozenset(),
            revision_patch_ids=frozenset(),
            applied_patch_ids=frozenset(),
            stale_baseline_patch_ids=frozenset(),
            failed_patch_ids=frozenset(),
        )

    def test_preapply_states_reject_later_phase_evidence(self):
        cases = (
            (
                TransactionInput("proposed", None, ()),
                replace(self.empty_evidence, attestations=({"patch_id": "p"},)),
                "proposed_evidence_forbidden",
            ),
            (
                TransactionInput("awaiting_attestation", None, ()),
                replace(self.empty_evidence, results=({"patch_id": "p"},)),
                "preapply_result_forbidden",
            ),
        )

        for transaction_input, evidence, expected_code in cases:
            with self.subTest(state=transaction_input.state):
                diagnostics = validate_transaction_lifecycle(
                    {}, transaction_input, evidence
                )
                self.assertEqual([expected_code], [item.code for item in diagnostics])

    def test_conflict_reason_requires_matching_validated_evidence(self):
        transaction_input = TransactionInput("conflicted", "reject", ())

        missing = validate_transaction_lifecycle(
            {}, transaction_input, self.empty_evidence
        )
        present = validate_transaction_lifecycle(
            {},
            transaction_input,
            replace(
                self.empty_evidence,
                rejected_patch_ids=frozenset({"p"}),
            ),
        )

        self.assertEqual(
            ["conflict_evidence_missing"],
            [item.code for item in missing],
        )
        self.assertEqual((), present)

    def test_empty_verified_closure_keeps_diagnostic_order(self):
        diagnostics = validate_transaction_lifecycle(
            {"mechanical_validation": []},
            TransactionInput("verified", None, ()),
            self.empty_evidence,
        )

        self.assertEqual(
            [
                "mechanical_validation_invalid",
                "verified_closure_vacuous",
                "verified_reconstruction_missing",
                "verified_validation_missing",
                "verified_validation_empty",
                "mutation_baseline_closure_mismatch",
                "mutation_reconstruction_mismatch",
            ],
            [item.code for item in diagnostics],
        )

    def test_verified_reconstruction_must_use_transaction_wire_version(self):
        snapshot_v1 = {"schema_version": 1, "nodes": [], "relations": []}
        diagnostics = validate_transaction_lifecycle(
            {
                "schema_version": 2,
                "reconstruction": {
                    "baseline": snapshot_v1,
                    "result": snapshot_v1,
                },
                "mechanical_validation": {
                    "schema_version": 1,
                    "status": "pass",
                    "diagnostics": [],
                    "summary": {"errors": 0, "warnings": 0},
                },
            },
            TransactionInput("verified", None, ({"entity": "node"},)),
            replace(
                self.empty_evidence,
                required_patch_ids=frozenset({"p"}),
                confirmed_patch_ids=frozenset({"p"}),
                applied_patch_ids=frozenset({"p"}),
            ),
        )

        self.assertIn(
            "verified_reconstruction_wire_invalid",
            {item.code for item in diagnostics},
        )


if __name__ == "__main__":
    unittest.main()
