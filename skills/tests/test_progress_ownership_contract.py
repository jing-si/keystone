# keystone: id=key.test.r011.progress-ownership kind=output_artifact artifact_kind=test verifies=key.standard.skill.author.progress-ownership key.standard.skill.author.terminal-status-reconciliation
import unittest
from pathlib import Path

from skills.tests import test_work_state_runtime as fixtures


ROOT = Path(__file__).parents[2]
RUNTIME = fixtures.RUNTIME


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class ProgressOwnershipContractTest(unittest.TestCase):
    def split_progress_sources(self):
        sources = fixtures.base_sources()
        aggregate_path = "00_docs/works/r010-active/runtime/key-progress.md"
        sources[aggregate_path] = fixtures.frontmatter("""
doc_type: progress
work_status: in_progress
approval: {state: pending}
finalization: {state: pending}
work_ref: R010/runtime
key: {id: key.work.runtime.progress}
""")
        sources[
            "00_docs/works/r010-active/runtime/key-progress-s03.md"
        ] = fixtures.frontmatter("""
doc_type: progress
work_status: complete
step_ref: R010/S03
work_ref: R010/runtime
approval: {state: accepted}
finalization:
  state: complete
  acceptance_ref: R010/S03/main-acceptance
key: {id: key.work.runtime.progress.s03}
""")
        sources[
            "00_docs/works/r010-active/runtime/key-progress-s04.md"
        ] = fixtures.frontmatter("""
doc_type: progress
work_status: in_progress
step_ref: R010/S04
work_ref: R010/runtime
approval: {state: pending}
finalization: {state: pending}
key: {id: key.work.runtime.progress.s04}
""")
        return sources

    def test_split_work_and_step_progress_recovers_only_the_active_step(self):
        result = RUNTIME.derive_work_state(self.split_progress_sources())

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual(["R010/S04"], result["state"]["active_steps"])
        active_work = result["state"]["active_works"][0]
        self.assertEqual("resolved", active_work["active_step_resolution"])
        self.assertEqual(
            [
                {
                    "path": (
                        "00_docs/works/r010-active/runtime/"
                        "key-progress-s03.md"
                    ),
                    "step_ref": "R010/S03",
                    "work_status": "complete",
                },
                {
                    "path": (
                        "00_docs/works/r010-active/runtime/"
                        "key-progress-s04.md"
                    ),
                    "step_ref": "R010/S04",
                    "work_status": "in_progress",
                },
            ],
            active_work["active_step_candidates"],
        )

    def test_aggregate_progress_state_cannot_be_overridden_by_work_index(self):
        sources = fixtures.base_sources()
        aggregate_path = "00_docs/works/r010-active/runtime/key-progress.md"
        sources[aggregate_path] = sources[aggregate_path].replace(
            b"work_status: in_progress", b"work_status: complete"
        ).replace(
            b"approval: {state: pending}", b"approval: {state: accepted}"
        ).replace(
            b"finalization: {state: pending}",
            b"finalization:\n  state: complete\n"
            b"  acceptance_ref: R010/S04/main-acceptance",
        )
        result = RUNTIME.derive_work_state(sources)

        self.assertIn(
            "work_state_work_projection_stale",
            {item["code"] for item in result["diagnostics"]},
        )
        self.assertEqual([], result["state"]["active_works"])

    def test_active_work_aggregate_cannot_use_completed_finalization(self):
        sources = fixtures.base_sources()
        aggregate_path = "00_docs/works/r010-active/runtime/key-progress.md"
        sources[aggregate_path] = sources[aggregate_path].replace(
            b"finalization: {state: pending}",
            b"finalization:\n  state: complete\n"
            b"  acceptance_ref: R010/S03/main-acceptance",
        )

        result = RUNTIME.derive_work_state(sources)

        self.assertIn(
            "work_state_progress_ownership_conflict",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_author_contract_requires_split_only_when_state_diverges(self):
        standard = read(
            "00_docs/standards/skills/author/key-standard-author.md"
        )
        skill = read("skills/keystone-author/SKILL.md")
        for phrase in (
            "Aggregate Work Progress",
            "Step Progress",
            "상태가 갈라질 때만",
            "key-progress-{step-slug}.md",
        ):
            self.assertIn(phrase, standard)
            self.assertIn(phrase, skill)

    def test_author_terminal_reconciliation_is_transition_only_and_bounded(self):
        standard = read(
            "00_docs/standards/skills/author/key-standard-author.md"
        )
        skill = read("skills/keystone-author/SKILL.md")

        for phrase in (
            "## Terminal status reconciliation",
            "실제 상태 전이",
            "owning Round subtree",
            "Optional projection이 없으면 정상",
            "stale conflict",
            "Historical Progress",
            "exact-ref 검색",
        ):
            self.assertIn(phrase, standard)

        for phrase in (
            "## Terminal Status Reconciliation",
            "actually changes",
            "owning Round subtree",
            "missing optional projection is valid",
            "stale conflict",
            "Preserve historical Progress",
            "exact-ref search",
        ):
            self.assertIn(phrase, skill)


if __name__ == "__main__":
    unittest.main()
