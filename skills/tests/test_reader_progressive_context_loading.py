# keystone: id=key.test.r014.reader-progressive-context-loading kind=output_artifact artifact_kind=test verifies=key.standard.skill.reader.context-readiness
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


def assert_order(test_case, text, phrases):
    positions = [text.index(phrase) for phrase in phrases]
    test_case.assertEqual(sorted(positions), positions)


class ReaderProgressiveContextLoadingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = normalized(read("00_docs/standards/01_key-project-standard.md"))
        cls.standard = normalized(
            read("00_docs/standards/skills/reader/key-standard-reader.md")
        )
        cls.skill = normalized(read("skills/keystone-reader/SKILL.md"))

    def test_initial_orientation_order_is_consistent(self):
        project_rule = normalized(section(
            read("00_docs/standards/01_key-project-standard.md"),
            "### STD-KEYSTONE-040",
        ))
        standard_workflow = normalized(section(
            read("00_docs/standards/skills/reader/key-standard-reader.md"),
            "## Common workflow",
        ))
        skill_readiness = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Session Context Readiness",
        ))

        assert_order(self, project_rule, (
            "document root(1)",
            "key-context-map.md",
            "accepted top-level 프로젝트 기준서(3)",
            "Child 기준서",
            "project brief",
            "canonical Work State",
        ))
        assert_order(self, standard_workflow, (
            "document root",
            "key-context-map.md",
            "accepted top-level 프로젝트 기준서",
            "child 기준서",
            "project_brief",
            "Work State runtime",
        ))
        assert_order(self, skill_readiness, (
            "document root",
            "key-context-map.md",
            "accepted top-level project standard",
            "child-standard indexes",
            "project_brief",
            "work_state_runtime.py",
        ))

    def test_active_round_zero_one_and_multi_boundaries_are_preserved(self):
        for phrase in (
            "Active parent Round가 없으면",
            "하나뿐이어도 자동으로",
            "자유로운 검토·조사·확인",
        ):
            self.assertIn(phrase, self.project)

        for phrase in (
            "Active parent Round가 0개이면",
            "후보가 하나여도 자동 선택하지 않는다",
            "자유로운 검토 범위",
        ):
            self.assertIn(phrase, self.standard)

        for phrase in (
            "no incomplete Rounds",
            "A sole active Round is reported but never selected automatically",
            "unaccepted parent and child Rounds",
            "complete / pending · 수용 대기",
            "Exclude only `accepted` and `cancelled`",
            "Free-form follow-up",
        ):
            self.assertIn(phrase, self.skill)

    def test_child_and_linker_expansion_are_bounded_by_concrete_need(self):
        for text, phrases in (
            (self.project, (
                "구체적인 공백",
                "Work 또는 문서 ID를 anchor",
                "Full graph는 명시적 graph audit, release verification 또는 scope conflict",
            )),
            (self.standard, (
                "구체적인 공백",
                "Work 또는 문서 ID를 anchor",
                "Full graph는 명시적 graph audit, release verification 또는 scope conflict",
            )),
            (self.skill, (
                "concrete gaps in project purpose, scope, document structure, or authority",
                "selected Work or document ID",
                "full graph only for an explicit graph audit, release verification, or scope conflict",
            )),
        ):
            for phrase in phrases:
                self.assertIn(phrase, text)

        self.assertIn("초기 orientation만으로 Linker를 기본 호출하지 않는다", self.project)
        self.assertIn("초기 orientation에서는 Linker를 기본 호출하지 않고", self.standard)
        self.assertIn("Do not invoke Linker merely because Reader was invoked", self.skill)

    def test_missing_implementation_is_not_automatically_a_metadata_gap(self):
        for text in (self.project, self.standard):
            self.assertIn("구현 확인 불가", text)
            self.assertIn("미구현 가능", text)
            self.assertIn("Code candidate가 존재하지만", text)
            self.assertIn("metadata gap", text)

        self.assertIn("implementation unavailable", self.skill)
        self.assertIn("possibly unimplemented", self.skill)
        self.assertIn("metadata gap only when a code candidate exists", self.skill)

    def test_cache_fallback_and_payload_boundary_remain_unchanged(self):
        project_readiness = normalized(section(
            read("00_docs/standards/01_key-project-standard.md"),
            "### STD-KEYSTONE-059",
        ))
        standard_readiness = normalized(section(
            read("00_docs/standards/skills/reader/key-standard-reader.md"),
            "## Session context readiness",
        ))
        skill_readiness = normalized(section(
            read("skills/keystone-reader/SKILL.md"),
            "## Session Context Readiness",
        ))

        self.assertIn("Cache 실패나 miss는 source 직접 탐색으로 fail-soft", project_readiness)
        self.assertIn("stale/missing/corrupt이면 Linker refresh 또는 source 직접 탐색", standard_readiness)
        self.assertIn("missing, stale, corrupt, or cannot be locked or written", skill_readiness)
        self.assertIn("fall back fail-soft to source discovery", skill_readiness)

        self.assertIn("agent-facing structured payload", self.project)
        self.assertIn("Reader는 `reader_output`과 `keystone_context_brief`를 agent-facing", self.standard)
        self.assertIn("Keep raw readiness and index payloads agent-facing", self.skill)
        self.assertIn("Do not expose the full `reader_output`", self.skill)


if __name__ == "__main__":
    unittest.main()
