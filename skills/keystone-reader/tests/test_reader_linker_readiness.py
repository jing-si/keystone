import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(ROOT / "skills" / "keystone-linker" / "scripts"))

from graph_runtime.index_model import CallTrace  # noqa: E402
from graph_runtime.readiness import context_readiness  # noqa: E402


class ReaderLinkerReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repository"
        (self.root / ".git").mkdir(parents=True)
        (self.root / "00_docs").mkdir()
        (self.root / "00_docs" / "context.md").write_text(
            "<!-- keystone: id=key.context kind=source_document -->\n# Context\n",
            encoding="utf-8",
        )
        self.cache = Path(self.temporary.name) / "cache" / "index.sqlite3"

    def tearDown(self):
        self.temporary.cleanup()

    def test_first_reader_invocation_records_one_way_linker_handoff(self):
        readiness = context_readiness(self.root, self.cache, initiator="reader")

        self.assertEqual(("reader", "linker"), tuple(item.lane for item in readiness.trace.entries))
        self.assertEqual("docs", readiness.result.scope.value)

    def test_linker_initiated_chain_does_not_reenter_reader(self):
        trace = CallTrace().enter("linker", "artifact_lookup")

        readiness = context_readiness(
            self.root, self.cache, initiator="linker", trace=trace)

        self.assertEqual(("linker",), tuple(item.lane for item in readiness.trace.entries))
        self.assertEqual({"key.context"}, {item.id for item in readiness.result.owners})


if __name__ == "__main__":
    unittest.main()
