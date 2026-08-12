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

    def test_linker_uses_optional_cache_without_source_authority(self):
        text = read("keystone-linker")
        readiness = section(text, "## Source of Truth")
        for phrase in (
            "current repository source surfaces",
            "cache is disposable and optional",
            "scan source directly",
            "without asking for additional folder access",
        ):
            self.assertIn(phrase, readiness)
        self.assertIn("Linker is always read-only", text)

    def test_verification_requirement_direction_is_not_evidence(self):
        rules = normalized(section(read("keystone-linker"), "## Impact Output"))
        self.assertIn("relation evidence", rules)
        self.assertIn("Label inference explicitly", rules)
        self.assertIn("mechanical findings separate from user or policy decisions", rules)

    def test_linker_keeps_graph_and_transaction_optional(self):
        text = read("keystone-linker")
        source = section(text, "## Source of Truth")
        synchronization = section(text, "## Graph Relevance")
        self.assertIn("graph is reconstructed", source)
        self.assertIn("canonical meaning across surfaces", synchronization)
        self.assertIn("stale_baseline", text)
        self.assertIn("transaction-scope", text)
        self.assertIn("repository-scope", text)
        self.assertIn("Do not run a repository-wide graph pass", synchronization)

    def test_author_separates_state_and_invalidates_changed_scope(self):
        text = read("keystone-author")
        self.assertIn("requires_verification_of", text)
        self.assertIn("source-document metadata", text)
        self.assertIn("document_lifecycle", text)
        self.assertIn("work_status", text)
        self.assertIn("approval.state", text)
        self.assertIn("affected-scope reconstruction", text)
        self.assertIn("multiple source surfaces", text)

    def test_coordinator_uses_linker_only_when_graph_context_is_relevant(self):
        text = read("keystone-coordinator")
        boundary = section(text, "## Workflow")
        for phrase in (
            "Ask Linker for impact context only when graph",
            "affected graph scope only when graph-relevant sources changed",
            "update only durable Work/Progress/index/context sources whose state or meaning changed",
        ):
            self.assertIn(phrase, boundary)
        self.assertIn("Do not dump raw worker, Linker, Author", text)

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
