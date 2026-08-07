import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class GraphSynchronizationSkillContractTest(unittest.TestCase):
    def test_linker_owns_mutation_decisions_without_source_write_authority(self):
        text = read("skills/keystone-linker/SKILL.md")
        self.assertIn("sole canonical graph mutation decision owner", text)
        self.assertIn("source-write-free", text)
        self.assertIn("## Graph Synchronization Mode", text)
        self.assertIn("document_delta", text)
        self.assertIn("artifact_delta", text)
        self.assertIn("new attempt", text)

    def test_author_contract_emits_and_reconciles_document_delta(self):
        text = read("skills/keystone-author/SKILL.md")
        self.assertIn("## Document Delta and Graph Synchronization", text)
        self.assertIn("kind: document_delta", text)
        self.assertIn("confirm | reject | needs_revision", text)
        self.assertIn("applied | failed | stale_baseline", text)
        self.assertIn("schema_version: 5", text)
        self.assertIn("global_state", text)
        self.assertIn("graph_sync", text)

    def test_coordinator_contract_collects_artifact_delta_without_expanding_permission(self):
        text = read("skills/keystone-coordinator/SKILL.md")
        self.assertIn("## Artifact Delta and Graph Synchronization", text)
        self.assertIn("kind: artifact_delta", text)
        self.assertIn("graph_attestations", text)
        self.assertIn("graph_apply_results", text)
        self.assertIn("does not create Coordinator permission", text)
        self.assertIn("partially_applied", text)

    def test_readme_describes_mutation_ownership_and_current_authority(self):
        text = read("README.md")
        self.assertIn("canonical graph mutation", text)
        self.assertNotIn("Linker is read-only and may be used", text)
        self.assertNotIn("The R002 standards and all six repo-local skill sources are implemented and accepted", text)


if __name__ == "__main__":
    unittest.main()
