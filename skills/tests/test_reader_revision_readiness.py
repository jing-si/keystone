# keystone: id=key.test.r011.reader-revision-readiness kind=output_artifact artifact_kind=test verifies=key.standard.skill.reader.revision-readiness
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def section(text, heading):
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    return text[start:] if next_heading == -1 else text[start:next_heading]


def normalized(text):
    return " ".join(text.split())


class ReaderRevisionReadinessContractTest(unittest.TestCase):
    def test_pending_revision_is_separate_from_initialization_state(self):
        rules = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Pending Revision Readiness",
        ))

        for phrase in (
            "does not change `initialization_state` by itself",
            "pending_with_baseline",
            "pending_without_baseline",
            "Do not call Init",
            "frontmatter",
        ):
            self.assertIn(phrase, rules)

    def test_pending_text_and_stale_projection_do_not_become_authority(self):
        rules = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Pending Revision Readiness",
        ))

        for phrase in (
            "proposal and navigation evidence",
            "never accepted authority",
            "Context Map or index",
            "cannot override pending source frontmatter",
            "Author or Main",
        ):
            self.assertIn(phrase, rules)

    def test_reader_standard_owns_the_same_revision_matrix(self):
        standard = normalized(section(
            read("00_docs/standards/skills/reader/key-standard-reader.md"),
            "## Pending revision readiness",
        ))

        for phrase in (
            "pending_with_baseline",
            "pending_without_baseline",
            "초기화 상태를 자동으로 `partial`로 낮추지 않는다",
            "Context Map이나 Index",
            "Author 또는 Main",
        ):
            self.assertIn(phrase, standard)

    def test_revision_readiness_is_session_output_not_a_new_source(self):
        reader = read("skills/keystone-reader/SKILL.md")
        context = section(reader, "## Result Contract")
        rules = normalized(section(reader, "## Pending Revision Readiness"))

        self.assertIn("revision_readiness:", context)
        self.assertIn("Do not persist this readiness result", rules)

    def test_revision_view_binds_sources_without_promoting_pending_meaning(self):
        reader = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Pending Revision Readiness",
        ))
        standard = normalized(section(
            read("00_docs/standards/skills/reader/key-standard-reader.md"),
            "## Pending revision readiness",
        ))

        for phrase in (
            "stable `key.id`",
            "raw-byte digest",
            "effective authority",
            "review overlay",
            "deterministic",
        ):
            self.assertIn(phrase, reader)
        for phrase in (
            "stable `key.id`",
            "raw-byte digest",
            "effective authority",
            "review overlay",
            "deterministic",
        ):
            self.assertIn(phrase, standard)


if __name__ == "__main__":
    unittest.main()
