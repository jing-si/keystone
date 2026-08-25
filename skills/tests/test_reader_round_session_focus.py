# keystone: id=key.test.r012.reader-round-session-focus kind=output_artifact artifact_kind=test verifies=key.standard.skill.reader.round-session-focus
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


class ReaderRoundSessionFocusContractTest(unittest.TestCase):
    def test_reader_selects_parent_round_before_candidate_deep_readiness(self):
        readiness = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Session Context Readiness",
        ))

        context_map = readiness.index("key-context-map.md")
        project_standard = readiness.index("accepted top-level project standard")
        project_brief = readiness.index("project_brief")
        work_state = readiness.index("work_state_runtime.py")
        focus_gate = readiness.index("session focus")
        linker_readiness = readiness.index("permissionless Linker readiness")

        self.assertLess(context_map, project_standard)
        self.assertLess(project_standard, project_brief)
        self.assertLess(project_brief, work_state)
        self.assertLess(work_state, focus_gate)
        self.assertLess(focus_gate, linker_readiness)
        for phrase in (
            "two or more active parent Rounds",
            "active Step refs or unresolved reason",
            "해당 세션에서 어떤 라운드를 작업할까요?",
            "Do not read every candidate Round's Work order or Progress",
            "Do not start conditional Linker readiness",
            "non-authoritative session context",
        ):
            self.assertIn(phrase, readiness)
        self.assertNotIn("which Work to handle in this session", readiness)

    def test_reader_skips_round_question_when_scope_is_already_clear(self):
        readiness = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Session Context Readiness",
        ))

        for phrase in (
            "zero or one active parent Round",
            "explicitly identifies a parent Round",
            "all active parent Rounds or a cross-Round comparison",
            "resume automatically with the selected Round",
            "never persist the selection",
        ):
            self.assertIn(phrase, readiness)

    def test_reader_informs_steps_and_selects_lowest_executable_without_asking(self):
        readiness = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Session Context Readiness",
        ))

        for phrase in (
            "inform the user of the current in-progress Steps",
            "Do not ask the user to choose a Step",
            "lowest-numbered executable active Step",
            "dependency evaluations and `work_gates`",
            "explain the blocker and select the next executable Step",
            "Do not change Step status or priority",
        ):
            self.assertIn(phrase, readiness)

    def test_result_contract_uses_session_round_without_retired_current_fields(self):
        result_contract = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Result Contract",
        ))

        self.assertIn("selected_round:", result_contract)
        self.assertIn("authority: non_authoritative", result_contract)
        self.assertNotIn("selected_work:", result_contract)
        self.assertNotIn("latest_accepted_round:", result_contract)


if __name__ == "__main__":
    unittest.main()
