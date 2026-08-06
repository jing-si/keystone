import unittest

from graph_runtime.model import (
    GraphSnapshot,
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
    mechanical_envelope_passes,
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
