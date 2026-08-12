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
    def test_reader_selects_session_focus_before_multi_work_deep_readiness(self):
        readiness = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Session Context Readiness",
        ))

        work_state = readiness.index("work_state_runtime.py")
        focus_gate = readiness.index("session focus")
        linker_readiness = readiness.index("permissionless Linker readiness")

        self.assertLess(work_state, focus_gate)
        self.assertLess(focus_gate, linker_readiness)
        for phrase in (
            "two or more active Works",
            "does not identify one Work",
            "exactly one focused question",
            "Do not read every candidate Work order or Progress",
            "Do not start Linker docs readiness",
            "non-authoritative session context",
        ):
            self.assertIn(phrase, readiness)

    def test_reader_skips_focus_question_when_scope_is_already_clear(self):
        readiness = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Session Context Readiness",
        ))

        for phrase in (
            "zero or one active Work",
            "explicitly identifies a Work",
            "all active Works or a cross-Work comparison",
            "resume automatically with the selected Work",
            "Never mark unselected Works inactive or lower priority",
        ):
            self.assertIn(phrase, readiness)

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
