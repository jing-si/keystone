import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


def read(skill):
    return (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")


class R006ContextReadinessContractTest(unittest.TestCase):
    def test_reader_starts_docs_first_readiness_and_expands_repository_lazily(self):
        text = read("keystone-reader")
        self.assertIn("## Session Context Readiness", text)
        self.assertIn("docs discovery scope", text)
        self.assertIn("permissionless Linker", text)
        self.assertIn("lazy repository scope", text)
        self.assertIn("worktree identity", text)
        self.assertIn("raw-byte SHA-256", text)
        self.assertIn("recursion guard", text)
        self.assertIn("initiator: reader", text)

    def test_linker_owns_external_derived_index_without_source_authority(self):
        text = read("keystone-linker")
        self.assertIn("Owner/Ref Index Readiness", text)
        self.assertIn("permissionless internal mode", text)
        self.assertIn("outside the repository", text)
        self.assertIn("single writer", text)
        self.assertIn("sorted path set", text)
        self.assertIn("raw-byte SHA-256", text)
        self.assertIn("fail-soft", text)
        self.assertIn("user-facing command", text)
        self.assertIn("initiating lane", text)

    def test_linker_keeps_graph_and_transaction_optional(self):
        text = read("keystone-linker")
        self.assertIn("requires_verification_of", text)
        self.assertIn("typed graph projection", text)
        self.assertIn("multiple source surfaces", text)
        self.assertIn("stale_baseline", text)
        self.assertIn("needs_revision", text)
        self.assertIn("reconstruction_mismatch", text)
        self.assertIn("transient_application_failure", text)
        self.assertIn("transaction scope", text)
        self.assertIn("repository scope", text)

    def test_author_separates_state_and_invalidates_changed_scope(self):
        text = read("keystone-author")
        self.assertIn("requires_verification_of", text)
        self.assertIn("declared metadata", text)
        self.assertIn("effective metadata", text)
        self.assertIn("document_lifecycle", text)
        self.assertIn("work_status", text)
        self.assertIn("approval.state", text)
        self.assertIn("affected discovery scope", text)
        self.assertIn("multiple source surfaces", text)

    def test_coordinator_permission_does_not_cover_internal_linker_readiness(self):
        text = read("keystone-coordinator")
        self.assertIn("## Permissionless Linker Boundary", text)
        self.assertIn("does not require Coordinator permission", text)
        self.assertIn("fresh Reader context token", text)
        self.assertIn("lazy repository scope", text)
        self.assertIn("affected discovery scope", text)
        self.assertIn("coverage debt", text)

    def test_init_and_clarify_do_not_turn_cache_management_into_user_work(self):
        init = read("keystone-init")
        clarify = read("keystone-clarify")
        self.assertIn("## Context Readiness Boundary", init)
        self.assertIn("not an Init mode", init)
        self.assertIn("does not lower", init)
        self.assertIn("## Internal Index and Graph Management Boundary", clarify)
        self.assertIn("not a user decision topic", clarify)
        self.assertIn("requires_verification_of", clarify)
        self.assertIn("does not promote", clarify)


if __name__ == "__main__":
    unittest.main()
