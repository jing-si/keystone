# keystone: id=key.test.r016.worktree-locator-contract kind=output_artifact artifact_kind=test verifies=key.standard.project.std-keystone-061 locator.test_name=WorktreeLocatorContractTest
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def section(text, heading):
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    return text[start:] if next_heading == -1 else text[start:next_heading]


class WorktreeLocatorContractTest(unittest.TestCase):
    def test_reader_uses_recorded_path_without_global_fallback(self):
        text = read("skills/keystone-reader/SKILL.md")
        readiness = section(text, "## Session Context Readiness")

        work_order = readiness.index("selected Work order")
        recorded_path = readiness.index("`key.worktree.path`")
        artifact_discovery = readiness.index("artifact context")

        self.assertLess(work_order, recorded_path)
        self.assertLess(recorded_path, artifact_discovery)
        self.assertIn("exact path", readiness)
        self.assertIn("current worktree", readiness)
        self.assertIn("stale", readiness)
        self.assertIn("same Git common directory", readiness)
        self.assertIn("never enumerate registered worktrees", readiness.lower())
        self.assertNotIn("git worktree list", readiness.lower())

    def test_author_owns_canonical_work_order_locator_write(self):
        text = read("skills/keystone-author/SKILL.md")
        locator = section(text, "## Worktree Locator Metadata")

        self.assertIn("canonical Work Order", locator)
        self.assertIn("`key.worktree.path`", locator)
        self.assertIn("before substantive repository edits", locator)
        self.assertIn("document-level", locator)
        self.assertIn("only `path`", locator)
        self.assertIn("does not create or select worktrees", locator)

    def test_coordinator_pauses_setup_until_fresh_confirmation(self):
        text = read("skills/keystone-coordinator/SKILL.md")
        locator = section(text, "## Worktree Setup and Locator Gate")

        setup = locator.index("create or select")
        author = locator.index("Ask Author")
        confirm = locator.index("fresh canonical Work Order")
        implementation = locator.index("substantive repository edits")

        self.assertLess(setup, author)
        self.assertLess(author, confirm)
        self.assertLess(confirm, implementation)
        self.assertIn("external implementation skill", locator)
        self.assertIn("same Git common directory", locator)
        self.assertIn("do not search other worktrees", locator)
        self.assertNotIn("git worktree list", locator)


if __name__ == "__main__":
    unittest.main()
