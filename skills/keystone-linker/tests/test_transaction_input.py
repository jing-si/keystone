import unittest

from graph_runtime.transaction_input import validate_transaction_input


class TransactionInputTest(unittest.TestCase):
    def test_header_diagnostics_keep_canonical_order(self):
        result = validate_transaction_input({
            "schema_version": 2,
            "state": "unknown",
            "conflict_reason": "unknown",
            "a_unknown": True,
            "z_unknown": True,
        })

        self.assertEqual(
            [
                "transaction_unknown_field",
                "transaction_unknown_field",
                "transaction_state_invalid",
                "transaction_schema_invalid",
                "conflict_reason_invalid",
                "conflict_reason_unexpected",
                "transaction_field_missing",
                "transaction_field_missing",
            ],
            [item.code for item in result.diagnostics],
        )

    def test_invalid_collections_are_reported_and_mutations_normalize_empty(self):
        result = validate_transaction_input({
            "schema_version": 1,
            "transaction_id": "tx",
            "scope_ref": "scope",
            "state": "proposed",
            "input_deltas": {},
            "coverage_debt": {},
            "canonical_mutations": {},
        })

        self.assertEqual(
            [
                "input_deltas_invalid",
                "coverage_debt_invalid",
                "transaction_mutations_invalid",
            ],
            [item.code for item in result.diagnostics],
        )
        self.assertEqual((), result.transaction_input.mutations)

    def test_duplicate_mutation_identity_is_reported_without_dropping_inputs(self):
        node = {
            "id": "key.capability.example",
            "kind": "capability",
            "artifact_kind": "none",
            "locator": {"path": "source.md"},
            "lifecycle": "active",
            "provenance": {"produced_from": [], "governed_by": []},
        }
        mutation = {
            "operation": "add",
            "entity": "node",
            "before": None,
            "after": node,
            "evidence": "declared",
        }
        mutations = [mutation, mutation]

        result = validate_transaction_input({
            "schema_version": 1,
            "transaction_id": "tx",
            "scope_ref": "scope",
            "state": "proposed",
            "canonical_mutations": mutations,
        })

        self.assertEqual(
            ["mutation_identity_duplicate"],
            [item.code for item in result.diagnostics],
        )
        self.assertEqual(tuple(mutations), result.transaction_input.mutations)


if __name__ == "__main__":
    unittest.main()
