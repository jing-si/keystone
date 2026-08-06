import tempfile
import unittest
from pathlib import Path

from graph_runtime.model import GraphTransaction, transaction_wire
from graph_runtime.validator import (
    diagnostic,
    envelope,
    reconstruct,
    validate_snapshot,
    validate_transaction,
)


class ValidatorFacadeTest(unittest.TestCase):
    def test_public_facade_preserves_snapshot_and_transaction_entry_points(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.md").write_text(
                "---\nkey: {id: key.doc.source, kind: source_document}\n---\n",
                encoding="utf-8",
            )

            snapshot, parse_diagnostics = reconstruct(root, ("source.md",))

            self.assertEqual((), validate_snapshot(root, snapshot, parse_diagnostics))
            self.assertEqual(
                (),
                validate_transaction(transaction_wire(
                    GraphTransaction("tx-facade", "R007/S02"))),
            )

    def test_public_facade_preserves_diagnostic_envelope(self):
        payload = envelope((diagnostic("broken", "broken source", "source.md"),))

        self.assertEqual(1, payload["schema_version"])
        self.assertEqual("fail", payload["status"])
        self.assertEqual({"errors": 1, "warnings": 0}, payload["summary"])
        self.assertEqual("broken", payload["diagnostics"][0]["code"])


if __name__ == "__main__":
    unittest.main()
