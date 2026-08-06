import unittest

from graph_runtime.model import (
    GraphRelevance,
    GraphSnapshot,
    GraphTransaction,
    Node,
    NodeKind,
    attempt_history_wire as model_attempt_history_wire,
    graph_snapshot_wire as model_graph_snapshot_wire,
    transaction_wire as model_transaction_wire,
)
from graph_runtime.reconciler import AttemptHistory
from graph_runtime.wire import (
    attempt_history_wire,
    graph_snapshot_wire,
    transaction_wire,
)


class WireFacadeCharacterizationTest(unittest.TestCase):
    def test_model_facade_matches_direct_snapshot_and_transaction_wire(self):
        snapshot = GraphSnapshot(nodes=(Node("key.doc.one", NodeKind.SOURCE_DOCUMENT),))
        transaction = GraphTransaction("tx-wire-facade", "R007/S02")

        self.assertEqual(
            graph_snapshot_wire(snapshot), model_graph_snapshot_wire(snapshot)
        )
        self.assertEqual(
            transaction_wire(transaction), model_transaction_wire(transaction)
        )

    def test_model_facade_matches_direct_attempt_history_wire(self):
        current = GraphTransaction("tx-current", "R007/S02")
        history = AttemptHistory(current)
        relevance = GraphRelevance(True, "required", "graph metadata changed")

        self.assertEqual(
            attempt_history_wire(history, relevance),
            model_attempt_history_wire(history, relevance),
        )


if __name__ == "__main__":
    unittest.main()
