import unittest

from graph_runtime.transaction_input import validate_transaction_input


class TransactionInputTest(unittest.TestCase):
    def _validate_v2_node(self, node):
        return validate_transaction_input({
            "schema_version": 2,
            "transaction_id": "tx",
            "scope_ref": "scope",
            "state": "proposed",
            "canonical_mutations": [{
                "operation": "add",
                "entity": "node",
                "before": None,
                "after": node,
                "evidence": "declared",
                "direct_relation_reason": None,
            }],
        })

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
                "conflict_reason_invalid",
                "conflict_reason_unexpected",
                "transaction_field_missing",
                "transaction_field_missing",
            ],
            [item.code for item in result.diagnostics],
        )

    def test_schema_v2_scope_ref_cannot_be_whitespace(self):
        result = validate_transaction_input({
            "schema_version": 2,
            "transaction_id": "tx",
            "scope_ref": "   ",
            "state": "proposed",
            "canonical_mutations": [],
        })

        self.assertIn(
            "transaction_field_missing",
            {item.code for item in result.diagnostics},
        )

    def test_schema_v2_failed_transaction_requires_typed_failure_reason(self):
        missing = validate_transaction_input({
            "schema_version": 2,
            "transaction_id": "tx",
            "scope_ref": "scope",
            "state": "failed",
        })
        valid = validate_transaction_input({
            "schema_version": 2,
            "transaction_id": "tx",
            "scope_ref": "scope",
            "state": "failed",
            "failure_reason": "transient_io",
        })

        self.assertIn("failure_reason_missing", [item.code for item in missing.diagnostics])
        self.assertNotIn("failure_reason_missing", [item.code for item in valid.diagnostics])

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

    def test_schema_v2_canonical_mutation_uses_exact_nested_fields(self):
        node = {
            "id": "key.capability.example",
            "kind": "capability",
            "artifact_kind": "none",
            "locator": {"path": "source.md"},
            "lifecycle": "active",
            "lifecycle_domain": "document",
            "provenance": {"produced_from": [], "governed_by": []},
        }
        mutation = {
            "operation": "add",
            "entity": "node",
            "before": None,
            "after": node,
            "evidence": "declared",
            "direct_relation_reason": None,
            "trusted": True,
        }

        result = validate_transaction_input({
            "schema_version": 2,
            "transaction_id": "tx",
            "scope_ref": "scope",
            "state": "proposed",
            "canonical_mutations": [mutation],
        })

        self.assertIn(
            "mutation_unknown_field",
            {item.code for item in result.diagnostics},
        )

    def test_schema_v2_direct_relation_reason_must_be_null_or_nonempty_text(self):
        relation = {
            "source": "key.item.example",
            "relation": "documents",
            "target": "key.code.example",
            "evidence": "declared",
            "provenance": {
                "produced_from": [],
                "governed_by": [],
                "surface": "document_metadata",
                "locator": {"path": "source.md"},
            },
            "lifecycle": "active",
            "lifecycle_domain": "relation",
        }
        for invalid in (True, 1, float("nan"), ""):
            with self.subTest(value=invalid):
                mutation = {
                    "operation": "add",
                    "entity": "relation",
                    "before": None,
                    "after": relation,
                    "evidence": "declared",
                    "direct_relation_reason": invalid,
                }
                result = validate_transaction_input({
                    "schema_version": 2,
                    "transaction_id": "tx",
                    "scope_ref": "scope",
                    "state": "proposed",
                    "canonical_mutations": [mutation],
                })
                self.assertIn(
                    "direct_relation_reason_invalid",
                    {item.code for item in result.diagnostics},
                )

    def test_schema_v1_mutation_without_direct_reason_remains_compatible(self):
        node = {
            "id": "key.capability.example",
            "kind": "capability",
            "artifact_kind": "none",
            "locator": {"path": "source.md"},
            "lifecycle": "active",
            "provenance": {"produced_from": [], "governed_by": []},
        }
        result = validate_transaction_input({
            "schema_version": 1,
            "transaction_id": "tx",
            "scope_ref": "scope",
            "state": "proposed",
            "canonical_mutations": [{
                "operation": "add",
                "entity": "node",
                "before": None,
                "after": node,
                "evidence": "declared",
            }],
        })

        self.assertEqual((), result.diagnostics)

    def test_schema_v2_artifact_mutation_rejects_parent_derived_effective_metadata(self):
        node = {
            "id": "key.code.example",
            "kind": "output_artifact",
            "artifact_kind": "code",
            "locator": {"path": "src/example.py"},
            "lifecycle": "active",
            "lifecycle_domain": "artifact",
            "provenance": {
                "produced_from": [],
                "governed_by": ["key.standard.parent"],
                "surface": "code_anchor",
                "locator": {"path": "src/example.py"},
            },
            "declared_metadata": {
                "document_lifecycle": None,
                "approval_state": None,
                "governed_by": [],
                "source_authority": [],
            },
            "effective_metadata": {
                "document_lifecycle": "active",
                "approval_state": "pending",
                "governed_by": ["key.standard.parent"],
                "source_authority": [["source", "parent"]],
            },
            "parent_id": "key.doc.parent",
        }

        result = self._validate_v2_node(node)

        self.assertIn(
            "mutation_node_invalid",
            {item.code for item in result.diagnostics},
        )

    def test_schema_v2_artifact_mutation_accepts_only_direct_metadata(self):
        node = {
            "id": "key.code.example",
            "kind": "output_artifact",
            "artifact_kind": "code",
            "locator": {"path": "src/example.py"},
            "lifecycle": "deprecated",
            "lifecycle_domain": "artifact",
            "provenance": {
                "produced_from": [],
                "governed_by": ["key.standard.artifact"],
                "surface": "code_anchor",
                "locator": {"path": "src/example.py"},
            },
            "declared_metadata": {
                "document_lifecycle": "deprecated",
                "approval_state": "accepted",
                "governed_by": ["key.standard.artifact"],
                "source_authority": [["owner", "repository"]],
            },
            "effective_metadata": {
                "document_lifecycle": "deprecated",
                "approval_state": "accepted",
                "governed_by": ["key.standard.artifact"],
                "source_authority": [["owner", "repository"]],
            },
            "parent_id": "key.doc.parent",
        }

        result = self._validate_v2_node(node)

        self.assertEqual((), result.diagnostics)

    def test_schema_v2_document_child_mutation_keeps_document_inheritance(self):
        node = {
            "id": "key.item.example",
            "kind": "document_item",
            "artifact_kind": "none",
            "locator": {"path": "source.md"},
            "lifecycle": "archived",
            "lifecycle_domain": "document",
            "provenance": {
                "produced_from": [],
                "governed_by": ["key.standard.parent", "key.standard.direct"],
                "surface": "document_metadata",
                "locator": {"path": "source.md"},
            },
            "declared_metadata": {
                "document_lifecycle": None,
                "approval_state": None,
                "governed_by": ["key.standard.direct"],
                "source_authority": [],
            },
            "effective_metadata": {
                "document_lifecycle": "archived",
                "approval_state": "pending",
                "governed_by": ["key.standard.parent", "key.standard.direct"],
                "source_authority": [["source", "parent"]],
            },
            "parent_id": "key.doc.parent",
        }

        result = self._validate_v2_node(node)

        self.assertEqual((), result.diagnostics)


if __name__ == "__main__":
    unittest.main()
