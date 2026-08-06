import unittest
import re
from pathlib import Path


ROOT = Path(__file__).parents[2]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def section(text, heading):
    start = text.index(heading)
    remainder = text[start + len(heading) :]
    next_heading = remainder.find("\n## ")
    return remainder if next_heading < 0 else remainder[:next_heading]


def compact(text):
    return " ".join(text.split())


def fenced_yaml_after(text, marker):
    start = text.index(marker)
    fence_start = text.index("```yaml", start)
    fence_end = text.index("```", fence_start + len("```yaml"))
    return text[fence_start + len("```yaml") : fence_end]


def duplicate_mapping_keys(yaml):
    """Detect duplicate plain mapping keys by indentation without a YAML dependency."""
    stacks = []
    duplicates = []
    for line in yaml.splitlines():
        match = re.match(r"^( *)([A-Za-z_][A-Za-z0-9_]*):", line)
        if not match:
            continue
        indent, key = len(match.group(1)), match.group(2)
        while stacks and stacks[-1][0] > indent:
            stacks.pop()
        if not stacks or stacks[-1][0] < indent:
            stacks.append((indent, set()))
        keys = stacks[-1][1]
        if key in keys:
            duplicates.append(key)
        keys.add(key)
    return duplicates


class CoordinatorKeystoneClosureContractTest(unittest.TestCase):
    def test_user_decision_separates_execution_and_closure_ownership(self):
        decisions = read("00_docs/works/key-decisions.md")

        self.assertIn("DEC-WORKS-026", decisions)
        self.assertIn("direct_execution", decisions)
        self.assertIn("orchestration", decisions)
        self.assertIn("Linker", decisions)
        self.assertIn("Author", decisions)
        self.assertIn("accept_candidate", decisions)

    def test_installed_contract_provides_main_and_keystone_context(self):
        contract = read("skills/keystone-coordinator/SKILL.md")
        context = section(contract, "## Pre-implementation Context Provisioning")

        self.assertIn("main_context_checkpoint", context)
        self.assertIn("source documents", context)
        self.assertIn("Reader recovery evidence", context)
        self.assertIn("Linker artifact context", context)
        self.assertIn("Author Change Set", context)
        self.assertIn("Do not start implementation", context)

    def test_external_worker_owns_implementation_but_not_keystone_completion(self):
        contract = read("skills/keystone-coordinator/SKILL.md")
        modes = compact(section(contract, "## Execution Modes"))

        self.assertIn("direct_execution", modes)
        self.assertIn("orchestration", modes)
        self.assertIn("It does not duplicate", modes)
        self.assertIn("unsupervised child workers", modes)
        self.assertIn("worker evidence only", modes)
        self.assertIn("finalization", modes)

    def test_closure_is_fail_closed_and_preserves_linker_author_authority(self):
        contract = read("skills/keystone-coordinator/SKILL.md")
        closure = compact(section(contract, "## Post-implementation Keystone Closure"))

        self.assertIn("one `artifact_delta` per changed surface", closure)
        self.assertIn("Ask Linker to classify", closure)
        self.assertIn("Route required source-document", closure)
        self.assertIn("prevents `accept_candidate`", closure)
        self.assertIn("closure_complete", closure)
        self.assertIn("closure-validator.md", closure)

    def test_source_and_runtime_contracts_use_the_same_closure_vocabulary(self):
        subagent = read("00_docs/standards/subagents/key-standard-subagents.md")
        coordinator = read("00_docs/standards/skills/coordinator/key-standard-coordinator.md")
        installed = read("skills/keystone-coordinator/SKILL.md")

        for term in (
            "direct_execution",
            "orchestration",
            "artifact_deltas",
            "document_sync",
            "metadata_sync",
            "graph_sync",
            "required | not_applicable | deferred",
        ):
            self.assertIn(term, subagent)
            self.assertIn(term, coordinator)
            self.assertIn(term, installed)

    def test_installed_package_contains_executable_closure_validator(self):
        self.assertTrue(
            (ROOT / "skills/keystone-coordinator/scripts/validate_closure.py").is_file()
        )
        self.assertTrue(
            (ROOT / "skills/keystone-coordinator/references/closure-validator.md").is_file()
        )

    def test_worker_assignment_example_has_no_duplicate_mapping_keys(self):
        contract = read("skills/keystone-coordinator/SKILL.md")
        example = fenced_yaml_after(contract, "## Output Contract")

        self.assertEqual([], duplicate_mapping_keys(example))


if __name__ == "__main__":
    unittest.main()
