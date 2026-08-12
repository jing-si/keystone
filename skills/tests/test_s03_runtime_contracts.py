import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class GraphSynchronizationSkillContractTest(unittest.TestCase):
    def test_linker_owns_mutation_decisions_without_source_write_authority(self):
        text = read("skills/keystone-linker/SKILL.md")
        self.assertIn("canonical mutation guidance", text)
        self.assertIn("Linker is always read-only", text)
        self.assertIn("## Current Apply and Verification", text)
        self.assertIn("exact owners, baselines, patches, and expected results", text)
        self.assertIn("stale_baseline", text)

    def test_author_contract_emits_and_reconciles_document_delta(self):
        text = read("skills/keystone-author/SKILL.md")
        self.assertIn("## Document Delta and Graph Synchronization", text)
        self.assertIn("applied | failed | stale_baseline", text)
        self.assertIn("owner: author", text)
        self.assertIn("affected-scope reconstruction", text)
        self.assertIn("Current completion does not require a new finalization manifest", text)

    def test_coordinator_contract_collects_artifact_delta_without_expanding_permission(self):
        text = read("skills/keystone-coordinator/SKILL.md")
        self.assertIn("## Ownership and Apply", text)
        self.assertIn("approved code/config/test/skill-source edits", text)
        self.assertIn("compare the expected baseline with current bytes", text)
        self.assertIn("current diff and verification result", text)
        self.assertIn("Historical owner-apply/application-evidence adapters", text)

    def test_readme_describes_mutation_ownership_and_current_authority(self):
        text = read("README.md")
        self.assertIn("canonical graph mutation", text)
        self.assertIn("Current apply does not use HMAC owner receipts", text)
        self.assertNotIn("Linker is read-only and may be used", text)
        self.assertNotIn("The R002 standards and all six repo-local skill sources are implemented and accepted", text)


if __name__ == "__main__":
    unittest.main()
