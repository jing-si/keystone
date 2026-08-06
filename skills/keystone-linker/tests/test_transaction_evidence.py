import unittest

from graph_runtime.transaction_evidence import validate_transaction_evidence


class TransactionEvidenceTest(unittest.TestCase):
    def test_non_array_collection_stops_evidence_collection(self):
        result = validate_transaction_evidence(
            {
                "surface_patches": {},
                "attestations": [],
                "apply_results": [],
            },
            root=None,
            mutations=(),
        )

        self.assertIsNone(result.evidence)
        self.assertEqual(
            ["transaction_collection_invalid"],
            [item.code for item in result.diagnostics],
        )

    def test_valid_evidence_is_collected_in_immutable_sets(self):
        patch = {
            "patch_id": "p1",
            "owner": "main",
            "surface": "code_anchor",
            "target_path": "src/example.py",
            "exact_patch": "replace symbol",
            "required": True,
            "baseline_digest": "absent",
        }
        result = validate_transaction_evidence(
            {
                "surface_patches": [patch],
                "attestations": [{
                    "patch_id": "p1",
                    "owner": "main",
                    "decision": "confirm",
                    "evidence": "reviewed",
                }],
                "apply_results": [{
                    "patch_id": "p1",
                    "result": "applied",
                    "resulting_digest": "sha256:" + "0" * 64,
                    "evidence": "written",
                }],
            },
            root=None,
            mutations=(),
        )

        self.assertEqual((), result.diagnostics)
        self.assertEqual(frozenset({"p1"}), result.evidence.required_patch_ids)
        self.assertEqual(frozenset({"p1"}), result.evidence.confirmed_patch_ids)
        self.assertEqual(frozenset({"p1"}), result.evidence.applied_patch_ids)

    def test_patch_attestation_and_result_diagnostics_keep_source_order(self):
        result = validate_transaction_evidence(
            {
                "surface_patches": ["bad patch"],
                "attestations": ["bad attestation"],
                "apply_results": ["bad result"],
            },
            root=None,
            mutations=(),
        )

        self.assertEqual(
            ["surface_patch_invalid", "attestation_invalid", "apply_result_invalid"],
            [item.code for item in result.diagnostics],
        )


if __name__ == "__main__":
    unittest.main()
