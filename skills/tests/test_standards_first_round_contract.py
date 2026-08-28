# keystone: id=key.test.r017.standards-first-round-contract kind=output_artifact artifact_kind=test verifies=key.standard.project.std-keystone-062 key.standard.skill.author.round-creation-execution-boundary
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


class StandardsFirstRoundContractTest(unittest.TestCase):
    def test_project_standard_fixes_constraints_not_one_pipeline(self):
        project = normalized(section(
            read("00_docs/standards/01_key-project-standard.md"),
            "### STD-KEYSTONE-062:",
        ))

        for phrase in (
            "`planned / pending`, Active Step 없음",
            "작업서 생성 이후 작업을 바로 진행해주세요",
            "첫 production 구현 전에 기준서 정합화",
            "Round 완료 전 accepted 기준서 의미",
            "하나의 고정 pipeline을 강제하지 않는다",
        ):
            self.assertIn(phrase, project)

    def test_author_standard_separates_creation_from_execution(self):
        author = normalized(section(
            read("00_docs/standards/skills/author/key-standard-author.md"),
            "## Round 생성과 실행 경계",
        ))

        for phrase in (
            "Active Step 없음으로 작성하고",
            "추가 문서 수정은 실행 승인이 아니다",
            "만들고 바로 진행해 주세요",
            "`no_change`와 근거",
            "하나의 고정 pipeline을 강제하지 않는다",
        ):
            self.assertIn(phrase, author)

    def test_skill_supports_combined_request_and_goal_specific_topology(self):
        skill = normalized(section(
            read("skills/keystone-author/SKILL.md"),
            "## Round Creation and Execution Boundary",
        ))

        for phrase in (
            "Separate creation from execution",
            "planned / pending` with no Active Step",
            "create the Round and proceed immediately",
            "Do not infer execution authority",
            "do not impose one fixed pipeline",
            "A document-only Round needs no implementation Step",
            "verify alignment among accepted standard meaning",
        ):
            self.assertIn(phrase, skill)

    def test_child_session_suffixes_use_uppercase_excel_numbering(self):
        skill = normalized(section(
            read("skills/keystone-author/SKILL.md"),
            "## Document Rules",
        ))

        for phrase in (
            "`A` through `Z`, then `AA`, `AB`, ... `AZ`, `BA`, ... `ZZ`, `AAA`",
            "`R010-A`",
            "`R010/S01-A`",
            "`R010-A/S01-A`",
            "historical compatibility inputs only",
            "digits, letter-number mixtures, lower-case letters, or semantic labels",
        ):
            self.assertIn(phrase, skill)

    def test_work_order_acceptance_covers_stop_combined_and_flexible_cases(self):
        work_order = read(
            "00_docs/works/r017-standards-first-round-construction/"
            "standards-first-round-construction/"
            "key-work-standards-first-round-construction.md"
        )

        for criterion in (
            "R017-CC-08",
            "R017-CC-09",
            "R017-CC-10",
        ):
            self.assertIn(criterion, work_order)


if __name__ == "__main__":
    unittest.main()
