# keystone: id=key.test.r011.derived-work-state-projection kind=output_artifact artifact_kind=test verifies=key.standard.project.derived-work-state-projection
import unittest
from pathlib import Path

from skills.tests import test_work_state_runtime as fixtures


ROOT = Path(__file__).parents[2]
RUNTIME = fixtures.RUNTIME
LEGACY_POINTER = b"""global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S04]
"""


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class DerivedProjectionContractTest(unittest.TestCase):
    def codes(self, result):
        return {item["code"] for item in result["diagnostics"]}

    def test_aggregate_progress_owns_work_state_when_index_projection_is_absent(self):
        sources = fixtures.base_sources()
        work_index = "00_docs/works/r010-active/runtime/00_key-index.md"
        sources[work_index] = sources[work_index].replace(
            b"work_status: in_progress\n", b""
        ).replace(
            b"approval: {state: pending}\n", b""
        )

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        active_work = result["state"]["active_works"][0]
        self.assertEqual("in_progress", active_work["status"])
        self.assertEqual({
            "path": "00_docs/works/r010-active/runtime/key-progress.md",
            "mode": "aggregate_progress",
        }, active_work["state_source"])

    def test_stale_work_index_projection_does_not_hide_progress_authority(self):
        sources = fixtures.base_sources()
        work_index = "00_docs/works/r010-active/runtime/00_key-index.md"
        sources[work_index] = sources[work_index].replace(
            b"work_status: in_progress", b"work_status: complete"
        ).replace(
            b"approval: {state: pending}", b"approval: {state: accepted}"
        )

        result = RUNTIME.derive_work_state(sources)

        self.assertIn("work_state_work_projection_stale", self.codes(result))
        active_work = result["state"]["active_works"][0]
        self.assertEqual("in_progress", active_work["status"])
        self.assertEqual(
            "aggregate_progress", active_work["state_source"]["mode"]
        )

    def test_global_pointer_documents_are_optional_compatibility_projections(self):
        sources = fixtures.base_sources()
        for path in (
            "00_docs/works/00_key-index.md",
            "00_docs/key-context-map.md",
            "00_docs/works/r010-active/00_key-index.md",
            "00_docs/works/r010-active/runtime/00_key-index.md",
        ):
            sources[path] = sources[path].replace(LEGACY_POINTER, b"")

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual([], result["state"]["pointer_claims"])
        self.assertEqual(["R010/S04"], result["state"]["active_steps"])

    def test_dependency_gate_uses_aggregate_progress_state_owner(self):
        sources = fixtures.base_sources()
        source_order = "00_docs/works/r010-active/runtime/key-work-runtime.md"
        target_order = "00_docs/works/r009-history/accepted/key-work-accepted.md"
        target_index = "00_docs/works/r009-history/accepted/00_key-index.md"
        target_progress = "00_docs/works/r009-history/accepted/key-progress.md"
        sources[source_order] = fixtures.frontmatter("""
doc_type: work_order
key:
  id: key.work.runtime.order
  relations:
    depends_on: [key.work.accepted.order]
work_gates:
  - dependency: key.work.accepted.order
    applies_to: {steps: [S04]}
    condition: {work_status: complete, approval_state: accepted}
""")
        sources[target_order] = fixtures.frontmatter("""
doc_type: work_order
work_status: in_progress
approval: {state: pending}
key: {id: key.work.accepted.order}
""")
        sources[target_index] = sources[target_index].replace(
            b"work_status: complete\n", b""
        ).replace(
            b"approval: {state: accepted}\n", b""
        )

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        evaluation = result["state"]["dependency_evaluations"][0]
        self.assertEqual("satisfied", evaluation["result"])
        self.assertEqual({
            "work_status": "complete",
            "approval_state": "accepted",
            "state_source": {
                "path": target_progress,
                "mode": "aggregate_progress",
            },
        }, evaluation["target_state"])

    def test_dependency_gate_keeps_legacy_work_index_fallback(self):
        sources = fixtures.base_sources()
        source_order = "00_docs/works/r010-active/runtime/key-work-runtime.md"
        target_order = "00_docs/works/r009-history/accepted/key-work-accepted.md"
        target_progress = "00_docs/works/r009-history/accepted/key-progress.md"
        sources[source_order] = fixtures.frontmatter("""
doc_type: work_order
key: {id: key.work.runtime.order}
work_gates:
  - dependency: key.work.accepted.order
    applies_to: {work_completion: true}
    condition: {work_status: complete, approval_state: accepted}
""")
        sources[target_order] = fixtures.frontmatter("""
doc_type: work_order
key: {id: key.work.accepted.order}
""")
        del sources[target_progress]

        result = RUNTIME.derive_work_state(sources)

        evaluation = result["state"]["dependency_evaluations"][0]
        self.assertEqual("satisfied", evaluation["result"])
        self.assertEqual(
            "legacy_work_index",
            evaluation["target_state"]["state_source"]["mode"],
        )

    def test_source_contract_rejects_persisted_projection_as_authority(self):
        project = read("00_docs/standards/01_key-project-standard.md")
        author = read("00_docs/standards/skills/author/key-standard-author.md")
        skill = read("skills/keystone-author/SKILL.md")
        for phrase in (
            "optional compatibility projection",
            "aggregate Progress authority",
            "새 persistent projection artifact를 만들지 않는다",
        ):
            self.assertIn(phrase, project + author)
            self.assertIn(phrase, skill)

    def test_semantic_views_are_source_bound_opt_in_session_outputs(self):
        project = read("00_docs/standards/01_key-project-standard.md")
        reader = read("skills/keystone-reader/SKILL.md")
        linker = read("skills/keystone-linker/SKILL.md")

        for phrase in (
            "include_source_views",
            "source_generation",
            "session-only",
            "automatic acceptance",
        ):
            self.assertIn(phrase, project + reader + linker)
        self.assertIn("same reconstructed `GraphSnapshot`", project + linker)
        self.assertIn("default readiness", project + linker)

    def test_current_source_changes_do_not_rewrite_historical_acceptance_binding(self):
        sources = fixtures.base_sources()
        before = RUNTIME.derive_work_state(sources)
        event_digest = before["state"]["historical_acceptance"][
            "acceptance_event_head"
        ]["subject_digest"]
        current_progress = "00_docs/works/r010-active/runtime/key-progress.md"
        sources[current_progress] += b"\n# Current-only narrative change\n"

        after = RUNTIME.derive_work_state(sources)

        self.assertNotEqual(
            before["generation"]["source_generation"],
            after["generation"]["source_generation"],
        )
        self.assertEqual(
            event_digest,
            after["state"]["historical_acceptance"][
                "acceptance_event_head"
            ]["subject_digest"],
        )
        self.assertEqual("pass", after["status"], after["diagnostics"])


if __name__ == "__main__":
    unittest.main()
