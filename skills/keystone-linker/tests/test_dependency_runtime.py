import unittest

from graph_runtime.dependency import (
    DependencyStatus,
    DependencyTargetState,
    evaluate_dependency_graph,
    evaluate_dependency_sources,
    parse_work_gates,
)
from graph_runtime.adapters import MarkdownAdapter
from graph_runtime.metadata import parse_source


def gate(source, target, step="S01", *, optional=False):
    parsed, diagnostics = parse_work_gates(
        [{
            "dependency": target,
            "applies_to": {"steps": [step]},
            "condition": {
                "work_status": "complete",
                "approval_state": "accepted",
            },
            "optional": optional,
        }],
        [target],
        source,
    )
    if diagnostics:
        raise AssertionError(diagnostics)
    return parsed[0]


class DependencyRuntimeTest(unittest.TestCase):
    def test_legacy_html_dependency_is_retained_for_completion_candidate(self):
        parsed = parse_source(
            """<!-- keystone: id=key.work.source kind=work_order depends_on=key.work.target -->
# Source
""",
            "00_docs/works/source/order.md",
            MarkdownAdapter(),
        )

        self.assertEqual(("key.work.target",),
                         parsed.dependency_sources[0].legacy_dependencies)

    def test_missing_source_step_is_invalid_and_blocks_required_gate(self):
        result = evaluate_dependency_graph(
            (gate("key.work.source", "key.work.target", "S99"),),
            {"key.work.target": DependencyTargetState("complete", "accepted")},
            source_steps={"key.work.source": ("S01",)},
        )

        self.assertEqual(DependencyStatus.INVALID, result.evaluations[0].status)
        self.assertTrue(result.evaluations[0].blocking)
        self.assertIn("work_gate_step_invalid", {item.code for item in result.diagnostics})

    def test_missing_source_work_is_invalid(self):
        result = evaluate_dependency_graph(
            (gate("key.work.missing", "key.work.target"),),
            {"key.work.target": DependencyTargetState("complete", "accepted")},
            source_steps={},
        )

        self.assertEqual(DependencyStatus.INVALID, result.evaluations[0].status)
        self.assertIn("work_gate_source_missing", {item.code for item in result.diagnostics})

    def test_legacy_only_dependency_becomes_non_start_blocking_completion_candidate(self):
        result = evaluate_dependency_graph(
            (),
            {"key.work.target": DependencyTargetState("in_progress", "pending")},
            source_steps={"key.work.source": ("S01",)},
            legacy_dependencies={"key.work.source": ("key.work.target",)},
            structured_dependencies={"key.work.source": ()},
        )

        evaluation = result.evaluations[0]
        self.assertEqual("legacy_completion_candidate", evaluation.origin)
        self.assertEqual((), evaluation.steps)
        self.assertTrue(evaluation.work_completion)
        self.assertEqual(DependencyStatus.WAITING, evaluation.status)
        self.assertTrue(evaluation.blocking)

    def test_flat_non_work_dependency_stays_typed_without_completion_gate(self):
        parsed = parse_source(
            """<!-- key: id=key.claim.source kind=claim depends_on=key.claim.target -->
# Claim
""",
            "docs/claim.md",
            MarkdownAdapter(),
        )

        self.assertEqual(1, len(parsed.snapshot.relations))
        self.assertFalse(parsed.dependency_sources[0].is_work)
        self.assertEqual(
            (), evaluate_dependency_sources(parsed.dependency_sources).evaluations
        )

    def test_structured_work_dependency_never_becomes_legacy_completion_gate(self):
        parsed = parse_source(
            """---
key:
  id: key.work.source
  kind: work_order
  depends_on: [key.work.target]
  relations:
    depends_on: [key.work.target]
---
""",
            "docs/work.md",
            MarkdownAdapter(),
        )

        source = parsed.dependency_sources[0]
        self.assertEqual(("key.work.target",), source.structured_dependencies)
        self.assertEqual((), source.legacy_dependencies)

    def test_optional_waiting_gate_is_not_blocking(self):
        result = evaluate_dependency_graph(
            (gate("key.work.source", "key.work.target", optional=True),),
            {"key.work.target": DependencyTargetState("in_progress", "pending")},
            source_steps={"key.work.source": ("S01",)},
        )

        self.assertEqual(DependencyStatus.WAITING, result.evaluations[0].status)
        self.assertFalse(result.evaluations[0].blocking)

    def test_missing_target_is_unresolvable_and_required(self):
        result = evaluate_dependency_graph(
            (gate("key.work.source", "key.work.missing"),),
            {},
            source_steps={"key.work.source": ("S01",)},
        )

        self.assertEqual(DependencyStatus.UNRESOLVABLE, result.evaluations[0].status)
        self.assertTrue(result.evaluations[0].blocking)

    def test_self_undeclared_and_duplicate_gates_remain_distinct_invalid_evidence(self):
        raw = [{
            "dependency": "key.work.source",
            "applies_to": {"steps": ["S01"]},
            "condition": {"work_status": "complete", "approval_state": "accepted"},
        }, {
            "dependency": "key.work.other",
            "applies_to": {"steps": ["S01"]},
            "condition": {"work_status": "complete", "approval_state": "accepted"},
        }, {
            "dependency": "key.work.other",
            "applies_to": {"steps": ["S01"]},
            "condition": {"work_status": "complete", "approval_state": "accepted"},
        }]
        gates, diagnostics = parse_work_gates(
            raw,
            ["key.work.source"],
            "key.work.source",
        )
        result = evaluate_dependency_graph(
            gates,
            {
                "key.work.source": DependencyTargetState("complete", "accepted"),
                "key.work.other": DependencyTargetState("complete", "accepted"),
            },
            source_steps={"key.work.source": ("S01",)},
        )

        codes = {item[0] for item in diagnostics}
        self.assertTrue({
            "work_gate_self_reference",
            "work_gate_dependency_undeclared",
            "work_gate_duplicate",
        }.issubset(codes))
        self.assertTrue(all(item.status == DependencyStatus.INVALID
                            for item in result.evaluations))
        self.assertEqual((), result.cycles)

    def test_structured_legacy_conflict_invalidates_structured_gate(self):
        result = evaluate_dependency_graph(
            (gate("key.work.source", "key.work.structured"),),
            {
                "key.work.structured": DependencyTargetState("complete", "accepted"),
            },
            source_steps={"key.work.source": ("S01",)},
            legacy_dependencies={"key.work.source": ("key.work.legacy",)},
            structured_dependencies={"key.work.source": ("key.work.structured",)},
        )

        self.assertEqual(DependencyStatus.INVALID, result.evaluations[0].status)
        self.assertIn("structured_legacy_dependency_conflict",
                      {item.code for item in result.diagnostics})

    def test_direct_and_indirect_cycles_use_deterministic_expanded_event_scc(self):
        direct = evaluate_dependency_graph(
            (
                gate("key.work.a", "key.work.b"),
                gate("key.work.b", "key.work.a"),
            ),
            {
                "key.work.a": DependencyTargetState("in_progress", "pending"),
                "key.work.b": DependencyTargetState("in_progress", "pending"),
            },
            source_steps={"key.work.a": ("S01",), "key.work.b": ("S01",)},
        )
        indirect = evaluate_dependency_graph(
            (
                gate("key.work.a", "key.work.b"),
                gate("key.work.b", "key.work.c"),
                gate("key.work.c", "key.work.a"),
            ),
            {
                work: DependencyTargetState("in_progress", "pending")
                for work in ("key.work.a", "key.work.b", "key.work.c")
            },
            source_steps={work: ("S01",) for work in (
                "key.work.a", "key.work.b", "key.work.c")},
        )

        self.assertTrue(all(item.status == DependencyStatus.INVALID
                            for item in direct.evaluations))
        self.assertTrue(all(item.status == DependencyStatus.INVALID
                            for item in indirect.evaluations))
        self.assertEqual(
            tuple(sorted(direct.cycles[0].events)),
            direct.cycles[0].events,
        )
        self.assertIn("dependency_cycle", {item.code for item in indirect.diagnostics})


if __name__ == "__main__":
    unittest.main()
