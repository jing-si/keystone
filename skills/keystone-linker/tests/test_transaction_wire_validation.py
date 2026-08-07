import unittest

from graph_runtime.model import (
    ApprovalState,
    ArtifactKind,
    GraphSnapshot,
    Lifecycle,
    Locator,
    Node,
    NodeKind,
    Relation,
    RelationType,
)
from graph_runtime.transaction_wire_validation import (
    apply_mutation_delta,
    is_digest_wire,
    is_mechanical_envelope,
    is_node_wire,
    is_relation_wire,
    is_snapshot_wire,
    mechanical_envelope_passes,
    migrate_snapshot_wire_v1_to_v2,
    normalized_wire,
)
from graph_runtime.wire import graph_snapshot_wire


class TransactionWireValidationTest(unittest.TestCase):
    def setUp(self):
        self.source = Node(
            "key.claim.source", NodeKind.CLAIM, locator=Locator("source.md")
        )
        self.target = Node(
            "key.code.target", NodeKind.OUTPUT_ARTIFACT, locator=Locator("target.py")
        )
        self.relation = Relation(
            self.source.id,
            RelationType.REQUIRES_VERIFICATION_OF,
            self.target.id,
        )

    def test_canonical_snapshot_entities_match_wire_predicates(self):
        snapshot = graph_snapshot_wire(GraphSnapshot(
            nodes=(self.source, self.target), relations=(self.relation,)
        ))

        self.assertTrue(all(is_node_wire(item) for item in snapshot["nodes"]))
        self.assertTrue(all(is_relation_wire(item) for item in snapshot["relations"]))

    def test_v1_serializer_is_strict_core_and_v1_parser_accepts_legacy_extensions(self):
        extended = Node(
            "key.claim.extended",
            NodeKind.CLAIM,
            locator=Locator("source.md"),
            approval_state=ApprovalState.ACCEPTED,
            declared_approval_state=ApprovalState.ACCEPTED,
        )
        node = graph_snapshot_wire(GraphSnapshot(nodes=(extended,)))["nodes"][0]

        self.assertEqual(
            {"id", "kind", "artifact_kind", "locator", "lifecycle", "provenance"},
            set(node),
        )
        legacy_extended = dict(node)
        legacy_extended.update({
            "declared_metadata": {
                "document_lifecycle": None,
                "approval_state": "accepted",
                "governed_by": [],
                "source_authority": [],
            },
            "effective_metadata": {
                "document_lifecycle": "active",
                "approval_state": "accepted",
                "governed_by": [],
                "source_authority": [],
            },
            "parent_id": None,
        })
        self.assertTrue(is_node_wire(legacy_extended, 1))

    def test_v1_migration_matches_canonical_v2_and_rejects_domain_conflict(self):
        v1 = graph_snapshot_wire(GraphSnapshot(
            nodes=(self.source, self.target), relations=(self.relation,)
        ))
        v2 = graph_snapshot_wire(GraphSnapshot(
            nodes=(self.source, self.target), relations=(self.relation,),
            schema_version=2,
        ))

        self.assertEqual(normalized_wire(v2), migrate_snapshot_wire_v1_to_v2(v1))
        self.assertTrue(is_snapshot_wire(v1, 1))
        self.assertTrue(is_snapshot_wire(v2, 2))
        self.assertTrue(all(is_node_wire(item, 2) for item in v2["nodes"]))
        self.assertTrue(all(is_relation_wire(item, 2) for item in v2["relations"]))

        wrong_version = dict(v2, schema_version=1)
        self.assertFalse(is_snapshot_wire(wrong_version, 1))

        invalid = graph_snapshot_wire(GraphSnapshot(nodes=(Node(
            "key.code.archived",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("target.py"),
            Lifecycle.ARCHIVED,
        ),)))
        with self.assertRaisesRegex(ValueError, "lifecycle"):
            migrate_snapshot_wire_v1_to_v2(invalid)

    def test_digest_wire_accepts_absent_or_lowercase_sha256_only(self):
        self.assertTrue(is_digest_wire("absent"))
        self.assertTrue(is_digest_wire("sha256:" + "a" * 64))
        self.assertFalse(is_digest_wire("sha256:" + "A" * 64))

    def test_mechanical_envelope_requires_status_and_summary_consistency(self):
        passing = {
            "schema_version": 1,
            "status": "pass",
            "diagnostics": [],
            "summary": {"errors": 0, "warnings": 0},
        }
        inconsistent = dict(passing, status="fail")

        self.assertTrue(is_mechanical_envelope(passing))
        self.assertTrue(mechanical_envelope_passes(passing))
        self.assertFalse(is_mechanical_envelope(inconsistent))

    def test_mutation_delta_applies_canonical_add_without_mutating_baseline(self):
        baseline = graph_snapshot_wire(GraphSnapshot())
        node_wire = graph_snapshot_wire(GraphSnapshot(nodes=(self.source,)))["nodes"][0]
        mutation = {
            "operation": "add",
            "entity": "node",
            "before": None,
            "after": node_wire,
        }

        result = apply_mutation_delta(baseline, (mutation,))

        self.assertEqual([], baseline["nodes"])
        self.assertEqual([node_wire], result["nodes"])
        self.assertEqual(result, normalized_wire(result))
        self.assertIsNone(apply_mutation_delta(result, (mutation,)))


if __name__ == "__main__":
    unittest.main()
