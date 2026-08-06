import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


def read(skill):
    return (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")


def section(text, heading):
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    return text[start:] if next_heading == -1 else text[start:next_heading]


def normalized(text):
    return " ".join(text.split())


class R006ContextReadinessContractTest(unittest.TestCase):
    def test_reader_starts_docs_first_readiness_and_expands_repository_lazily(self):
        text = read("keystone-reader")
        readiness = section(text, "## Session Context Readiness")
        for phrase in (
            "docs discovery scope",
            "permissionless Linker",
            "lazy repository scope",
            "worktree identity",
            "raw-byte SHA-256",
            "recursion guard",
            "initiator: reader",
            "hidden from the user",
        ):
            self.assertIn(phrase, readiness)
        self.assertNotIn("repository scope on the first invocation", readiness)
        self.assertNotIn("Reader writes", readiness)

    def test_linker_owns_external_derived_index_without_source_authority(self):
        text = read("keystone-linker")
        readiness = section(text, "## Owner/Ref Index Readiness")
        for phrase in (
            "permissionless internal mode",
            "no repository source-write authority",
            "outside the repository",
            "single writer",
            "sorted path set",
            "raw-byte SHA-256",
            "fail-soft",
            "user-facing command",
            "initiating lane",
        ):
            self.assertIn(phrase, readiness)
        self.assertNotIn("write a repository source surface", readiness)
        self.assertNotIn("Linker requires Coordinator permission", readiness)

    def test_verification_requirement_direction_is_not_evidence(self):
        rules = normalized(section(read("keystone-linker"), "## Graph Interpretation Rules"))
        self.assertIn("acceptance criterion or claim -> target", rules)
        self.assertIn("review the requirement and verification plan", rules)
        self.assertIn("test artifact or verification result -> target", rules)
        self.assertIn("actual verification evidence", rules)

    def test_linker_keeps_graph_and_transaction_optional(self):
        text = read("keystone-linker")
        self.assertIn("requires_verification_of", text)
        readiness = section(text, "## Owner/Ref Index Readiness")
        synchronization = section(text, "## Graph Synchronization Mode")
        self.assertIn("typed graph projection", readiness)
        self.assertIn("multiple source surfaces", synchronization)
        self.assertIn("stale_baseline", text)
        self.assertIn("needs_revision", text)
        self.assertIn("reconstruction_mismatch", text)
        self.assertIn("transient_application_failure", text)
        self.assertIn("transaction scope", text)
        self.assertIn("repository scope", text)
        self.assertNotIn("automatically starts this mode", synchronization)
        self.assertNotIn("single-surface change requires a transaction", synchronization)

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
        boundary = section(text, "## Permissionless Linker Boundary")
        for phrase in (
            "does not require Coordinator permission",
            "fresh Reader context token",
            "lazy repository scope",
            "affected discovery scope",
            "coverage debt",
        ):
            self.assertIn(phrase, boundary)
        self.assertNotIn("permission governs internal Linker", boundary)
        self.assertNotIn("raw readiness payload to the user", boundary)

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
