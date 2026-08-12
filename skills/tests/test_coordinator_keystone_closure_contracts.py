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


if __name__ == "__main__":
    unittest.main()
