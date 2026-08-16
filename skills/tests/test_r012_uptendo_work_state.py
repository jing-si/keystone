# keystone: id=key.test.r012.uptendo-no-event-work-state kind=output_artifact artifact_kind=test verifies=key.claim.current-work-state.uptendo-no-event-recovery
import unittest

from skills.tests import test_work_state_runtime as fixtures


RUNTIME = fixtures.RUNTIME


def uptendo_shaped_sources():
    sources = fixtures.hierarchical_sources()
    sources.pop(RUNTIME.ACCEPTANCE_EVENT_PATH)

    for old_path in tuple(sources):
        if "r009-history" not in old_path:
            continue
        new_path = old_path.replace("r009-history", "r011-history")
        sources[new_path] = sources.pop(old_path).replace(b"R009", b"R011").replace(
            b"r009", b"r011"
        )

    old_state = b"""global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010-a/S01]"""
    current_state = b"""global_state:
  schema_version: 5
  active_rounds: [R008, R010]
  active_steps: [R008/S02, R010-a/S01]"""
    for path in (
        "00_docs/works/00_key-index.md",
        "00_docs/key-context-map.md",
        "00_docs/works/r010-active/00_key-index.md",
    ):
        sources[path] = sources[path].replace(old_state, current_state)

    sources["00_docs/works/r008-active/00_key-index.md"] = fixtures.frontmatter("""
doc_type: work_round
round_status: active
approval: {state: pending}
key: {id: key.work.round.r008-active.index}
""")
    sources["00_docs/works/r008-active/migration/00_key-index.md"] = fixtures.frontmatter("""
doc_type: work
work_id: migration
work_status: in_progress
approval: {state: pending}
key: {id: key.work.r008.migration.index}
""")
    sources["00_docs/works/r008-active/migration/key-progress.md"] = fixtures.frontmatter("""
doc_type: progress
work_status: in_progress
step_ref: R008/S02
approval: {state: pending}
key: {id: key.work.r008.migration.progress}
""")
    return sources


class R012UptendoWorkStateTest(unittest.TestCase):
    def test_no_event_parallel_parent_and_child_state_recovers_without_diagnostics(self):
        result = RUNTIME.derive_work_state(uptendo_shaped_sources())

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual([], result["diagnostics"])
        self.assertEqual(["R008", "R010"], result["state"]["active_rounds"])
        self.assertEqual(["R010-a"], result["state"]["active_child_rounds"])
        self.assertEqual(
            ["R008/S02", "R010-a/S01"], result["state"]["active_steps"]
        )
        self.assertEqual(["R011"], result["state"]["accepted_rounds"])
        self.assertNotIn("historical_acceptance", result["state"])


if __name__ == "__main__":
    unittest.main()
