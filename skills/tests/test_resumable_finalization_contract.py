# keystone: id=key.test.r011.resumable-finalization kind=output_artifact artifact_kind=test verifies=key.standard.skill.author.resumable-finalization
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


class ResumableFinalizationContractTest(unittest.TestCase):
    def test_reader_returns_a_three_state_candidate_without_mutation(self):
        rules = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Resumable Finalization Candidates",
        ))

        for phrase in (
            "blocked | resumable | unknown",
            "recorded blocker",
            "resolved_by_source_change",
            "resolved_by_contract_change",
            "Author resume action",
            "Never complete finalization automatically",
        ):
            self.assertIn(phrase, rules)

    def test_author_resumes_current_checks_without_legacy_evidence_rebuild(self):
        rules = normalized(section(
            read("skills/keystone-author/SKILL.md"),
            "## Resumable Finalization",
        ))

        for phrase in (
            "current targeted verification",
            "Do not recreate legacy manifests, snapshots, HMAC receipts, keys, or evidence roots",
            "preserve the old failure as history",
            "Main post-edit review",
            "never complete automatically",
        ):
            self.assertIn(phrase, rules)

    def test_completed_finalization_is_history_not_a_resume_candidate(self):
        reader_rules = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Resumable Finalization Candidates",
        ))
        author_rules = normalized(section(
            read("skills/keystone-author/SKILL.md"),
            "## Resumable Finalization",
        ))

        phrase = "complete or waived finalization is not a resume candidate"
        self.assertIn(phrase, reader_rules)
        self.assertIn(phrase, author_rules)

    def test_author_standard_owns_the_same_resume_boundary(self):
        standard = normalized(section(
            read("00_docs/standards/skills/author/key-standard-author.md"),
            "## Resumable finalization",
        ))

        for phrase in (
            "blocked | resumable | unknown",
            "source_change | contract_change",
            "자동으로 `complete`로 바꾸지 않는다",
            "과거 HMAC",
        ):
            self.assertIn(phrase, standard)


if __name__ == "__main__":
    unittest.main()
