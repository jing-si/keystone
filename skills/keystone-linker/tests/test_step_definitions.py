"""Declared definitions distinguish missing Steps from unidentified legacy plans."""
import unittest
from graph_runtime.adapters import MarkdownAdapter
from graph_runtime.metadata import parse_source
from graph_runtime.dependency import evaluate_dependency_sources, DependencyStatus


class StepDefinitionsTest(unittest.TestCase):
    def parse(self, definition=''):
        return parse_source('''---
doc_type: work_order
key:
  id: key.work.source
  relations:
    depends_on: [key.work.target]
'''+definition+'''work_gates:
  - dependency: key.work.target
    applies_to: {steps: [S02]}
    condition: {work_status: complete, approval_state: accepted}
---
### R001/S02 · Planned implementation
''', '00_docs/works/r001-test/source/key-work-source.md', MarkdownAdapter())

    def evaluate(self, parsed):
        target = parse_source('''---
doc_type: work_order
work_status: complete
approval: {state: accepted}
key: {id: key.work.target}
---
''','00_docs/works/r002-test/target/key-work-target.md',MarkdownAdapter())
        return evaluate_dependency_sources(parsed.dependency_sources+target.dependency_sources)

    def test_future_defined_step_without_progress_satisfies_gate(self):
        parsed = self.parse('  defined_steps: [S01, S02]\n')
        self.assertEqual((), parsed.diagnostics)
        result = self.evaluate(parsed)
        self.assertEqual((), result.diagnostics)
        self.assertEqual(DependencyStatus.SATISFIED, result.evaluations[0].status)

    def test_legacy_heading_without_definition_is_unknown_not_absent(self):
        result = self.evaluate(self.parse())
        self.assertEqual('work_gate_step_unidentified', result.diagnostics[0].code)
        self.assertEqual(DependencyStatus.UNKNOWN, result.evaluations[0].status)
        self.assertTrue(result.evaluations[0].blocking)

    def test_explicit_definition_missing_target_is_invalid(self):
        result = self.evaluate(self.parse('  defined_steps: [S01]\n'))
        self.assertEqual('work_gate_step_invalid', result.diagnostics[0].code)
        self.assertEqual(DependencyStatus.INVALID, result.evaluations[0].status)

    def test_malformed_and_duplicate_definitions(self):
        for value in ['[S01, S01]', '[R001/S02]', 'S02', '[42]']:
            self.assertIn('malformed_metadata',
                          [d.code for d in self.parse('  defined_steps: '+value+'\n').diagnostics])
