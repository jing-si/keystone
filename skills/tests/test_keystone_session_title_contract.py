# keystone: id=key.test.r019.keystone-session-title-contract kind=output_artifact artifact_kind=test verifies=key.standard.project.std-keystone-063 key.standard.skill.init.codex-session-title key.standard.skill.reader.round-session-focus
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.9-3.10 compatibility
    tomllib = None


ROOT = Path(__file__).parents[2]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class KeystoneSessionTitleContractTest(unittest.TestCase):
    def test_project_standard_limits_session_title_to_project_opt_in(self):
        text = read("00_docs/standards/01_key-project-standard.md")

        for phrase in (
            "### STD-KEYSTONE-063:",
            "Keystone 세션 제목 표시",
            ".codex/config.toml",
            "`~/.codex/config.toml`은 변경하지 않는다",
            '["activity", "thread-title", "task-progress"]',
            "/rename 프로그래스 {Round ref}:{대표 문구}",
            "5자 이내",
        ):
            self.assertIn(phrase, text)

    def test_init_skill_owns_only_the_bounded_project_setting(self):
        text = read("skills/keystone-init/SKILL.md")

        for phrase in (
            "## Optional Codex Project Integration",
            "IntelliJ·터미널 탭에 Keystone 작업 세션 제목을 표시할까요? (yes/no)",
            "selects `configure` and is itself consent",
            "create or replace only",
            "Never reserialize the whole file",
            "Never edit `~/.codex/config.toml`",
            "write nothing and report the conflict",
        ):
            self.assertIn(phrase, text)

    def test_recommended_terminal_title_is_valid_toml(self):
        if tomllib is None:
            self.skipTest("tomllib is available in Python 3.11+")
        parsed = tomllib.loads(
            '[tui]\nterminal_title = ["activity", "thread-title", "task-progress"]\n'
        )

        self.assertEqual(
            parsed["tui"]["terminal_title"],
            ["activity", "thread-title", "task-progress"],
        )

    def test_reader_proposes_but_never_claims_to_execute_rename(self):
        text = " ".join(read("skills/keystone-reader/SKILL.md").split())

        for phrase in (
            "after Round focus is known",
            "/rename 프로그래스 {Round ref}:{대표 문구}",
            "five Korean characters or fewer",
            "Do not propose it before focus",
            "execute a slash command",
            "claim the rename succeeded",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
