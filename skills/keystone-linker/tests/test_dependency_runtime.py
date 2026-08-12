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
    def test_explicit_mapping_is_not_an_empty_gate_array(self):
        gates, diagnostics = parse_work_gates(
            {},
            (),
            "key.work.source",
        )

        self.assertFalse(gates)
        self.assertEqual("work_gates_invalid", diagnostics[0][0])

    def test_unknown_gate_and_scope_fields_are_rejected(self):
        gates, diagnostics = parse_work_gates(
            [{
                "dependency": "key.work.target",
                "applies_to": {
                    "steps": ["S01"],
                    "work_completion": False,
                    "all_steps": True,
                },
                "condition": {
                    "work_status": "complete",
                    "approval_state": "accepted",
                },
                "optional": False,
                "trusted": True,
            }],
            ["key.work.target"],
            "key.work.source",
        )

        self.assertEqual(1, len(gates))
        self.assertEqual(
            {"work_gate_field_unknown", "work_gate_scope_field_unknown"},
            {code for code, _message in diagnostics},
        )
        self.assertIn("work_gate_schema_invalid", gates[0].invalid_codes)

    def test_legacy_nested_approval_condition_is_rejected(self):
        gates, diagnostics = parse_work_gates(
            [{
                "dependency": "key.work.target",
                "applies_to": {"steps": ["S01"], "work_completion": False},
                "condition": {
                    "work_status": "complete",
                    "approval": {"state": "accepted"},
                },
                "optional": False,
            }],
            ["key.work.target"],
            "key.work.source",
        )

        self.assertEqual(1, len(gates))
        self.assertIn(
            "work_gate_approval_schema_legacy",
            {code for code, _message in diagnostics},
        )
        self.assertIn(
            "work_gate_condition_invalid",
            set(gates[0].invalid_codes),
        )

    def test_conflicting_flat_and_legacy_approval_conditions_are_rejected(self):
        gates, diagnostics = parse_work_gates(
            [{
                "dependency": "key.work.target",
                "applies_to": {"steps": ["S01"], "work_completion": False},
                "condition": {
                    "work_status": "complete",
                    "approval_state": "accepted",
                    "approval": {"state": "pending"},
                },
                "optional": False,
            }],
            ["key.work.target"],
            "key.work.source",
        )

        self.assertEqual(1, len(gates))
        self.assertIn(
            "work_gate_condition_conflict",
            {code for code, _message in diagnostics},
        )
        self.assertIn(
            "work_gate_condition_invalid",
            set(gates[0].invalid_codes),
        )

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

    def test_child_round_step_keeps_local_gate_scope(self):
        progress = parse_source(
            """---
doc_type: progress
work_status: in_progress
step_ref: R010-a/S01
approval: {state: pending}
key: {id: key.work.source.progress}
---
""",
            "00_docs/works/r010-parent/r010-a/source/key-progress.md",
            MarkdownAdapter(),
        )
        source = parse_source(
            """---
doc_type: work_order
work_status: in_progress
approval: {state: pending}
key:
  id: key.work.source
  kind: work_order
  depends_on: [key.work.target]
  relations:
    depends_on: [key.work.target]
work_gates:
  - dependency: key.work.target
    applies_to: {steps: [S01], work_completion: false}
    condition: {work_status: complete, approval_state: accepted}
    optional: false
---
""",
            "00_docs/works/r010-parent/r010-a/source/key-work-source.md",
            MarkdownAdapter(),
        )
        target = parse_source(
            """---
doc_type: work_order
work_status: complete
approval: {state: accepted}
key: {id: key.work.target, kind: work_order}
---
""",
            "00_docs/works/r010-parent/r010-b/target/key-work-target.md",
            MarkdownAdapter(),
        )

        result = evaluate_dependency_sources(
            progress.dependency_sources
            + source.dependency_sources
            + target.dependency_sources
        )

        self.assertEqual((), result.diagnostics)
        self.assertEqual(DependencyStatus.SATISFIED, result.evaluations[0].status)
        self.assertEqual(("S01",), result.evaluations[0].steps)

    def test_aggregate_progress_overrides_dependency_state_projections(self):
        source = parse_source(
            """---
doc_type: work_order
key:
  id: key.work.source
  kind: work_order
  relations:
    depends_on: [key.work.target]
work_gates:
  - dependency: key.work.target
    applies_to: {steps: [S01]}
    condition: {work_status: complete, approval_state: accepted}
---
""",
            "00_docs/works/r010-active/source/key-work-source.md",
            MarkdownAdapter(),
        )
        source_progress = parse_source(
            """---
doc_type: progress
work_status: in_progress
step_ref: R010/S01
approval: {state: pending}
key: {id: key.work.source.progress}
---
""",
            "00_docs/works/r010-active/source/key-progress.md",
            MarkdownAdapter(),
        )
        target = parse_source(
            """---
doc_type: work_order
work_status: in_progress
approval: {state: pending}
key: {id: key.work.target, kind: work_order}
---
""",
            "00_docs/works/r009-history/target/key-work-target.md",
            MarkdownAdapter(),
        )
        target_index = parse_source(
            """---
doc_type: work
work_status: in_progress
approval: {state: pending}
key: {id: key.work.target.index}
---
""",
            "00_docs/works/r009-history/target/00_key-index.md",
            MarkdownAdapter(),
        )
        target_progress = parse_source(
            """---
doc_type: progress
work_status: complete
approval: {state: accepted}
key: {id: key.work.target.progress}
---
""",
            "00_docs/works/r009-history/target/key-progress.md",
            MarkdownAdapter(),
        )

        parsed = (
            source.dependency_sources
            + source_progress.dependency_sources
            + target.dependency_sources
            + target_index.dependency_sources
            + target_progress.dependency_sources
        )
        result = evaluate_dependency_sources(parsed)

        self.assertEqual(DependencyStatus.SATISFIED, result.evaluations[0].status)
        self.assertIn(
            "dependency_state_projection_stale",
            {item.code for item in result.diagnostics},
        )

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
