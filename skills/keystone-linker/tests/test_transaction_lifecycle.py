import unittest
from dataclasses import replace

from graph_runtime.model import (
    ArtifactKind,
    Evidence,
    GraphSnapshot,
    Lifecycle,
    Locator,
    Node,
    NodeKind,
    Provenance,
    Relation,
    RelationType,
)
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

    def test_schema_v2_relation_mutation_rechecks_direction_policy(self):
        capability = Node(
            "key.capability.example",
            NodeKind.CAPABILITY,
            locator=Locator("source.md"),
        )
        code = Node(
            "key.code.example",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/example.py"),
        )
        relation = {
            "source": capability.id,
            "relation": "provides",
            "target": code.id,
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
        mutation = {
            "operation": "add",
            "entity": "relation",
            "before": None,
            "after": relation,
            "evidence": "declared",
            "direct_relation_reason": None,
        }

        diagnostics = validate_transaction_lifecycle(
            {"schema_version": 2},
            TransactionInput("proposed", None, (mutation,)),
            self.empty_evidence,
            GraphSnapshot(nodes=(capability, code)),
        )

        self.assertIn(
            "mutation_relation_direction_invalid",
            {item.code for item in diagnostics},
        )

    def test_schema_v2_bounded_direct_relation_requires_reason(self):
        item = Node(
            "key.item.example",
            NodeKind.DOCUMENT_ITEM,
            locator=Locator("source.md"),
        )
        code = Node(
            "key.code.example",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/example.py"),
        )
        relation = {
            "source": item.id,
            "relation": "documents",
            "target": code.id,
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
        mutation = {
            "operation": "add",
            "entity": "relation",
            "before": None,
            "after": relation,
            "evidence": "declared",
            "direct_relation_reason": None,
        }

        diagnostics = validate_transaction_lifecycle(
            {"schema_version": 2},
            TransactionInput("proposed", None, (mutation,)),
            self.empty_evidence,
            GraphSnapshot(nodes=(item, code)),
        )

        self.assertIn(
            "direct_relation_reason_missing",
            {item.code for item in diagnostics},
        )

    def test_schema_v2_node_mutation_before_must_match_source_snapshot(self):
        actual = Node(
            "key.capability.example",
            NodeKind.CAPABILITY,
            locator=Locator("source.md"),
        )
        stale = replace(actual, lifecycle=Lifecycle.ARCHIVED)
        after = replace(actual, lifecycle=Lifecycle.SUPERSEDED)
        from graph_runtime.wire import graph_snapshot_wire
        stale_wire = graph_snapshot_wire(
            GraphSnapshot(nodes=(stale,), schema_version=2), schema_version=2
        )["nodes"][0]
        after_wire = graph_snapshot_wire(
            GraphSnapshot(nodes=(after,), schema_version=2), schema_version=2
        )["nodes"][0]
        mutation = {
            "operation": "update",
            "entity": "node",
            "before": stale_wire,
            "after": after_wire,
            "evidence": "declared",
            "direct_relation_reason": None,
        }

        diagnostics = validate_transaction_lifecycle(
            {"schema_version": 2},
            TransactionInput("proposed", None, (mutation,)),
            self.empty_evidence,
            GraphSnapshot(nodes=(actual,)),
        )

        self.assertIn(
            "mutation_baseline_context_mismatch",
            {item.code for item in diagnostics},
        )

    def test_schema_v2_relation_before_must_match_preapply_source_snapshot(self):
        source = Node(
            "key.code.example",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/example.py"),
        )
        target = Node(
            "key.capability.example",
            NodeKind.CAPABILITY,
            locator=Locator("source.md"),
        )
        actual = Relation(
            source.id,
            RelationType.USES,
            target.id,
            Evidence.DECLARED,
            Provenance(
                surface="code_anchor",
                locator=Locator("src/example.py"),
            ),
            Lifecycle.ACTIVE,
        )
        stale = replace(actual, lifecycle=Lifecycle.REMOVED)
        after = replace(actual, lifecycle=Lifecycle.ARCHIVED)
        from graph_runtime.wire import graph_snapshot_wire
        stale_wire = graph_snapshot_wire(
            GraphSnapshot(relations=(stale,), schema_version=2),
            schema_version=2,
        )["relations"][0]
        after_wire = graph_snapshot_wire(
            GraphSnapshot(relations=(after,), schema_version=2),
            schema_version=2,
        )["relations"][0]
        mutation = {
            "operation": "update",
            "entity": "relation",
            "before": stale_wire,
            "after": after_wire,
            "evidence": "declared",
            "direct_relation_reason": None,
        }

        diagnostics = validate_transaction_lifecycle(
            {"schema_version": 2},
            TransactionInput("ready_to_apply", None, (mutation,)),
            replace(
                self.empty_evidence,
                required_patch_ids=frozenset({"p"}),
                confirmed_patch_ids=frozenset({"p"}),
            ),
            GraphSnapshot(nodes=(source, target), relations=(actual,)),
        )

        self.assertIn(
            "mutation_baseline_context_mismatch",
            {item.code for item in diagnostics},
        )

    def test_verified_schema_v2_binds_reconstruction_to_application_baseline(self):
        source = Node(
            "key.code.example",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/example.py"),
        )
        target = Node(
            "key.capability.example",
            NodeKind.CAPABILITY,
            locator=Locator("source.md"),
        )
        actual = Relation(
            source.id,
            RelationType.USES,
            target.id,
            Evidence.DECLARED,
            Provenance(
                surface="code_anchor",
                locator=Locator("src/example.py"),
            ),
            Lifecycle.ACTIVE,
        )
        stale = replace(actual, lifecycle=Lifecycle.REMOVED)
        after = replace(actual, lifecycle=Lifecycle.ARCHIVED)
        baseline_snapshot = GraphSnapshot(
            nodes=(source, target), relations=(actual,), schema_version=2,
        )
        stale_snapshot = GraphSnapshot(
            nodes=(source, target), relations=(stale,), schema_version=2,
        )
        result_snapshot = GraphSnapshot(
            nodes=(source, target), relations=(after,), schema_version=2,
        )
        from graph_runtime.wire import graph_snapshot_wire
        stale_wire = graph_snapshot_wire(stale_snapshot, schema_version=2)
        result_wire = graph_snapshot_wire(result_snapshot, schema_version=2)
        mutation = {
            "operation": "update",
            "entity": "relation",
            "before": stale_wire["relations"][0],
            "after": result_wire["relations"][0],
            "evidence": "declared",
            "direct_relation_reason": None,
        }

        diagnostics = validate_transaction_lifecycle(
            {
                "schema_version": 2,
                "reconstruction": {
                    "baseline": stale_wire,
                    "result": result_wire,
                },
                "mechanical_validation": {
                    "schema_version": 1,
                    "status": "pass",
                    "diagnostics": [],
                    "summary": {"errors": 0, "warnings": 0},
                },
            },
            TransactionInput("verified", None, (mutation,)),
            replace(
                self.empty_evidence,
                required_patch_ids=frozenset({"p"}),
                confirmed_patch_ids=frozenset({"p"}),
                applied_patch_ids=frozenset({"p"}),
                actual_state_root_available=True,
            ),
            result_snapshot,
            baseline_source_snapshot=baseline_snapshot,
        )

        codes = {item.code for item in diagnostics}
        self.assertIn("verified_baseline_snapshot_mismatch", codes)
        self.assertIn("mutation_baseline_context_mismatch", codes)

    def test_schema_v2_optional_first_partial_state_is_valid(self):
        diagnostics = validate_transaction_lifecycle(
            {"schema_version": 2},
            TransactionInput("partially_applied", None, ()),
            replace(
                self.empty_evidence,
                required_patch_ids=frozenset({"required"}),
                confirmed_patch_ids=frozenset({"required", "optional"}),
                applied_patch_ids=frozenset({"optional"}),
                results=({
                    "patch_id": "optional",
                    "result": "applied",
                },),
            ),
        )

        self.assertNotIn(
            "partial_application_missing",
            {item.code for item in diagnostics},
        )

    def test_schema_v2_preapply_reconstruction_cannot_override_source_context(self):
        from graph_runtime.wire import graph_snapshot_wire

        actual_source = Node(
            "key.capability.source",
            NodeKind.CAPABILITY,
            locator=Locator("source.md"),
        )
        actual_target = Node(
            "key.code.target",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("target.py"),
        )
        fake_source = Node(
            actual_source.id,
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("fake.py"),
        )
        fake_target = Node(
            actual_target.id,
            NodeKind.CAPABILITY,
            locator=Locator("fake.md"),
        )
        fake = graph_snapshot_wire(
            GraphSnapshot(nodes=(fake_source, fake_target), schema_version=2),
            schema_version=2,
        )
        relation = {
            "source": actual_source.id,
            "relation": "provides",
            "target": actual_target.id,
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
        mutation = {
            "operation": "add",
            "entity": "relation",
            "before": None,
            "after": relation,
            "evidence": "declared",
            "direct_relation_reason": None,
        }

        diagnostics = validate_transaction_lifecycle(
            {
                "schema_version": 2,
                "reconstruction": {"baseline": fake, "result": fake},
            },
            TransactionInput("proposed", None, (mutation,)),
            self.empty_evidence,
            GraphSnapshot(nodes=(actual_source, actual_target)),
        )
        codes = {item.code for item in diagnostics}

        self.assertIn("preverification_reconstruction_forbidden", codes)
        self.assertIn("mutation_relation_direction_invalid", codes)

    def test_schema_v2_ready_state_rejects_preloaded_apply_results(self):
        diagnostics = validate_transaction_lifecycle(
            {"schema_version": 2},
            TransactionInput("ready_to_apply", None, ()),
            replace(
                self.empty_evidence,
                results=({
                    "patch_id": "p",
                    "result": "applied",
                },),
            ),
        )

        self.assertIn(
            "ready_apply_result_forbidden",
            {item.code for item in diagnostics},
        )


if __name__ == "__main__":
    unittest.main()
