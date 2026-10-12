# keystone: id=key.test.r019.keystone-session-title-contract kind=output_artifact artifact_kind=test verifies=key.standard.project.std-keystone-063 key.standard.skill.init.codex-session-title key.standard.skill.reader.round-session-focus
import unittest
from pathlib import Path
import stat

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
            "UserPromptSubmit",
            "codex queue",
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

    def test_init_hook_command_quotes_path_without_literal_escape_characters(self):
        text = read("skills/keystone-init/SKILL.md")
        command = (
            "command = '\"$HOME/.codex/skills/keystone-reader/scripts/"
            "keystone_session_title.py\" --hook'"
        )

        self.assertIn(command, text)
        self.assertNotIn("command = '\\\"$HOME/", text)

    def test_recommended_project_integration_is_valid_toml(self):
        if tomllib is None:
            self.skipTest("tomllib is available in Python 3.11+")
        parsed = tomllib.loads(read(".codex/config.toml"))

        self.assertEqual(
            parsed["tui"]["terminal_title"],
            ["activity", "thread-title", "task-progress"],
        )
        hook = parsed["hooks"]["UserPromptSubmit"][0]["hooks"][0]
        self.assertEqual("command", hook["type"])
        self.assertIn("keystone_session_title.py", hook["command"])
        self.assertIn("--hook", hook["command"])

    def test_reader_uses_native_first_prompt_title_generation(self):
        text = " ".join(read("skills/keystone-reader/SKILL.md").split())

        for phrase in (
            "scripts/keystone_session_title.py",
            "UserPromptSubmit",
            "codex queue",
            "unaccepted parent and child Rounds",
            "complete / pending · 수용 대기",
            "MUST translate every displayed title",
            "{local Round ref}:{phrase}",
            "user's primary language",
            "without a `프로그래스` prefix",
            "Work Order creation, writing, revision, or amendment",
            "non-authoritative provisional value",
            "rechecked by Author immediately before the write",
            "fail open",
            "Never edit Codex SQLite, rollout, or config state directly",
            "never propose `/rename`",
        ):
            self.assertIn(phrase, text)

    def test_session_title_helper_is_a_narrow_installer_verified_executable(self):
        helper = ROOT / "skills/keystone-reader/scripts/keystone_session_title.py"
        installer = read("reinstall-local-keystone-skills.sh")

        self.assertTrue(helper.stat().st_mode & stat.S_IXUSR)
        self.assertIn(
            'require_executable "$base/keystone-reader/scripts/keystone_session_title.py"',
            installer,
        )
        self.assertIn(
            'run_direct_help "$base/keystone-reader/scripts/keystone_session_title.py"',
            installer,
        )


if __name__ == "__main__":
    unittest.main()
