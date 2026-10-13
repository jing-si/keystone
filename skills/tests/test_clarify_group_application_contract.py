# keystone: id=key.test.r013.clarify-group-application kind=output_artifact artifact_kind=test verifies=key.standard.project.std-keystone-060 key.standard.skill.clarify.topic-boundary key.standard.skill.author.clarification-log-application
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


class ClarifyGroupApplicationContractTest(unittest.TestCase):
    def test_project_standard_keeps_one_minimal_log_per_broad_subject(self):
        rules = normalized(section(
            read("00_docs/standards/01_key-project-standard.md"),
            "### STD-KEYSTONE-060:",
        ))

        for phrase in (
            "파일은 그룹별이 아니라 대주제별로 하나",
            "clarify/{YYYYMMDDTHHmmssZ}-{topic-slug}.md",
            "## G01 - {수정 범위}",
            "### Q01 - {질문 요약}",
            "`질문`, `답변`, `답변일시`",
            "별도 remaining-question 목록을 만들지 않는다",
            "`Group Decision`, `Author Application`",
            "source authority, edit permission 또는 평가 근거가 아니다",
        ):
            self.assertIn(phrase, rules)

    def test_clarify_groups_by_application_scope_and_asks_one_question(self):
        standard = normalized(section(
            read("00_docs/standards/skills/clarify/key-standard-clarify.md"),
            "## 대주제, 그룹과 topic 경계",
        ))
        skill = normalized(section(
            read("skills/keystone-clarify/SKILL.md"),
            "## Broad Subject and Group Queue",
        ))

        for phrase in (
            "그룹은 질문 묶음이나 별도 결정이 아니라",
            "같은 원천 문서·section",
            "답변들을 함께 해석",
            "한 번에 하나씩 질문",
            "별도 `Group Decision`",
            "모든 그룹이 끝나면",
        ):
            self.assertIn(phrase, standard)

        for phrase in (
            "one coherent source-document application boundary",
            "same documents or sections",
            "answers must be interpreted together",
            "ask exactly one decision question",
            "Do not create a `Group Decision`",
            "After every group is handled, resume",
        ):
            self.assertIn(phrase, skill)

    def test_author_separates_answer_log_from_group_source_application(self):
        standard = normalized(section(
            read("00_docs/standards/skills/author/key-standard-author.md"),
            "## Clarification log와 그룹 적용",
        ))
        skill = normalized(section(
            read("skills/keystone-author/SKILL.md"),
            "## Clarification Log and Group Application",
        ))

        for phrase in (
            "답변별 log append와 그룹 종료별 원천 문서 적용",
            "`답변`, `답변일시`다",
            "Work State, graph reconstruction",
            "그 그룹의 affected source document 범위만 한 번 적용",
        ):
            self.assertIn(phrase, standard)

        for phrase in (
            "per-answer log persistence and per-group source application",
            "Base fields are `질문`, `답변`, and `답변일시`",
            "Do not run Progress updates, Work State, graph reconstruction",
            "Apply that group's affected source scope exactly once",
        ):
            self.assertIn(phrase, skill)

    def test_standard_indexes_expose_the_group_log_contract(self):
        for path in (
            "00_docs/standards/00_key-index.md",
            "00_docs/standards/skills/00_key-index.md",
            "00_docs/standards/skills/clarify/00_key-index.md",
            "00_docs/standards/skills/author/00_key-index.md",
        ):
            text = read(path)
            self.assertIn("clarification log", text)
            self.assertIn("그룹", text)


if __name__ == "__main__":
    unittest.main()
