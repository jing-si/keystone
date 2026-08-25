import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]
READER_SKILL = ROOT / "skills" / "keystone-reader" / "SKILL.md"
sys.path.insert(0, str(ROOT / "skills" / "keystone-linker" / "scripts"))

from graph_runtime.index_model import CallTrace  # noqa: E402
from graph_runtime.readiness import context_readiness  # noqa: E402


def section(text, heading):
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    return text[start:] if next_heading == -1 else text[start:next_heading]


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

    def test_initial_orientation_defers_linker_until_artifact_context_is_needed(self):
        readiness = section(
            READER_SKILL.read_text(encoding="utf-8"),
            "## Session Context Readiness",
        )

        context_map = readiness.index("`key-context-map.md`")
        project_standard = readiness.index("accepted top-level project standard")
        project_brief = readiness.index("`project_brief`")
        work_state = readiness.index("work_state_runtime.py")
        linker = readiness.index("Request permissionless Linker readiness only when")

        self.assertLess(context_map, project_standard)
        self.assertLess(project_standard, project_brief)
        self.assertLess(project_brief, work_state)
        self.assertLess(work_state, linker)
        self.assertIn("Do not treat initial orientation as an artifact-context trigger", readiness)

    # keystone: id=key.test.reader.linker-readiness-contract kind=output_artifact artifact_kind=test verifies=key.code.linker.context-readiness locator.test_name=test_selected_work_artifact_trigger_records_one_way_linker_handoff
    def test_selected_work_artifact_trigger_records_one_way_linker_handoff(self):
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
