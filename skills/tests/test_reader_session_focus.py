# keystone: id=key.test.r011.reader-session-focus kind=output_artifact artifact_kind=test verifies=key.standard.skill.reader.session-focus
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


class ReaderSessionFocusContractTest(unittest.TestCase):
    def test_historical_work_focus_claim_is_preserved_as_compatibility(self):
        standard = normalized(
            read("00_docs/standards/skills/reader/key-standard-reader.md")
        )

        for phrase in (
            "key.standard.skill.reader.session-focus",
            "historical compatibility claim",
            "key.standard.skill.reader.round-session-focus",
            "새 Work 선택 질문을 만들지 않는다",
        ):
            self.assertIn(phrase, standard)

    def test_current_reader_contract_does_not_retain_work_selection_question(self):
        readiness = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Session Context Readiness",
        ))

        self.assertIn("active parent Rounds", readiness)
        self.assertNotIn("which Work to handle in this session", readiness)
        self.assertNotIn("resume automatically with the selected Work", readiness)

    def test_reader_standard_owns_the_same_session_focus_boundary(self):
        standard = normalized(
            read("00_docs/standards/skills/reader/key-standard-reader.md")
        )

        for phrase in (
            "session focus",
            "Work State 요약",
            "Work Order와 Progress 본문을 상세 탐색하지 않는다",
            "Linker docs readiness를 시작하지 않는다",
            "비권위 세션 문맥",
            "상태·우선순위를 변경하지 않는다",
        ):
            self.assertIn(phrase, standard)


if __name__ == "__main__":
    unittest.main()
