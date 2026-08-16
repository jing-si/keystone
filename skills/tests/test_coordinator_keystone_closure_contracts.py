import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class CoordinatorKeystoneClosureContractTest(unittest.TestCase):
    def test_source_and_package_contracts_share_lean_current_authority(self):
        standard = read("00_docs/standards/skills/coordinator/key-standard-coordinator.md")
        skill = read("skills/keystone-coordinator/SKILL.md")
        reference = read("skills/keystone-coordinator/references/closure-validator.md")
        combined = standard + skill + reference
        for term in (
            "direct_execution",
            "orchestration",
            "current diff",
            "Progress",
            "Work State",
            "historical_structure_only",
        ):
            self.assertIn(term, combined)

    def test_current_contract_rejects_external_evidence_as_prerequisite(self):
        skill = read("skills/keystone-coordinator/SKILL.md")
        reference = read("skills/keystone-coordinator/references/closure-validator.md")
        self.assertIn("does not require a cryptographic receipt", skill)
        self.assertIn("does not accept or require an assignment snapshot", reference)
        self.assertIn("do not request access", reference)

    def test_installed_package_keeps_only_historical_parsers_not_producers(self):
        current = ROOT / "skills/keystone-coordinator/scripts"
        self.assertTrue((current / "validate_closure.py").is_file())
        self.assertTrue((current / "closure_v2.py").is_file())
        self.assertTrue((current / "closure_v3.py").is_file())
        self.assertFalse((current / "capture_assignment_snapshot.py").exists())
        self.assertFalse((current / "record_acceptance_event.py").exists())
        self.assertFalse((current / "run_owned_surface_apply.py").exists())

    def test_release_contract_is_tiered(self):
        skill = read("skills/keystone-coordinator/SKILL.md")
        self.assertIn("Default Work", skill)
        self.assertIn("Escalated", skill)
        self.assertIn("Release", skill)
        self.assertIn("preflight, package tests, shared skills tests, compileall", skill)

    def test_main_retains_acceptance(self):
        skill = read("skills/keystone-coordinator/SKILL.md")
        self.assertIn("Main retains scope control", skill)
        self.assertIn("Return evidence and residual risk to Main for acceptance", skill)

    def test_current_work_state_round_and_step_selection(self):
        standard = read("00_docs/standards/01_key-project-standard.md")
        skill = read("skills/keystone-coordinator/SKILL.md")

        for phrase in (
            "해당 세션에서 어떤 라운드를 작업할까요?",
            "선택은 session-only",
            "Step 선택 자체는 사용자 질문으로 만들지\n않는다",
            "active Step 중 번호가\n가장 낮은 Step",
            "다음 실행 가능 Step",
        ):
            self.assertIn(phrase, standard)

        for phrase in (
            "Work State schema v5",
            "`selection_required`",
            "해당 세션에서 어떤 라운드를 작업할까요?",
            "session-only",
            "Do not ask the user to choose a Step",
            "lowest-numbered executable active Step",
            "next executable Step",
            "status or priority",
        ):
            self.assertIn(phrase, skill)

        self.assertNotIn("For Work State schema\n   v3", skill)


if __name__ == "__main__":
    unittest.main()
