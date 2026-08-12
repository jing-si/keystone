import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
CANONICAL = ROOT / "scripts" / "work_state_runtime.py"
GENERATOR = ROOT / "scripts" / "generate_work_state_runtimes.py"
PACKAGE_RUNTIMES = (
    ROOT / "skills" / "keystone-reader" / "scripts" / "work_state_runtime.py",
    ROOT / "skills" / "keystone-coordinator" / "scripts" / "work_state_runtime.py",
    ROOT / "skills" / "keystone-author" / "scripts" / "work_state_runtime.py",
)


def load_runtime(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_script(path, name):
    directory = str(path.parent)
    sys.path.insert(0, directory)
    try:
        return load_runtime(path, name)
    finally:
        sys.path.remove(directory)


RUNTIME = load_runtime(CANONICAL, "keystone_test_work_state_runtime")


def frontmatter(body):
    return ("---\n" + body.strip() + "\n---\n# Fixture\n").encode("utf-8")


def base_sources():
    sources = {
        "00_docs/works/00_key-index.md": frontmatter("""
doc_type: work_round_index
key: {id: key.work.index}
global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S04]
"""),
        "00_docs/key-context-map.md": frontmatter("""
doc_type: context_map
key: {id: key.context-map}
global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S04]
"""),
        "00_docs/works/r009-history/00_key-index.md": frontmatter("""
doc_type: work_round
round_status: accepted
approval: {state: accepted}
key: {id: key.work.round.r009-history.index}
"""),
        "00_docs/works/r009-history/accepted/00_key-index.md": frontmatter("""
doc_type: work
work_id: accepted
work_status: complete
approval: {state: accepted}
key: {id: key.work.accepted.index}
"""),
        "00_docs/works/r009-history/accepted/key-progress.md": frontmatter("""
doc_type: progress
work_status: complete
step_ref: R009/S01
approval: {state: accepted}
finalization:
  state: complete
  acceptance_ref: R009/S01/main-acceptance
key: {id: key.work.accepted.progress}
"""),
        "00_docs/works/r010-active/00_key-index.md": frontmatter("""
doc_type: work_round
round_status: active
approval: {state: pending}
key: {id: key.work.round.r010-active.index}
global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S04]
"""),
        "00_docs/works/r010-active/runtime/00_key-index.md": frontmatter("""
doc_type: work
work_id: runtime
work_status: in_progress
approval: {state: pending}
key: {id: key.work.runtime.index}
global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S04]
"""),
        "00_docs/works/r010-active/runtime/key-progress.md": frontmatter("""
doc_type: progress
work_status: in_progress
step_ref: R010/S04
approval: {state: pending}
finalization: {state: pending}
key: {id: key.work.runtime.progress}
"""),
    }
    digest = RUNTIME.historical_projection_digest(sources)
    events = {
        "schema_version": 1,
        "events": [{
            "id": "R009/accepted-round-migration-genesis",
            "sequence": 0,
            "previous_event_ref": None,
            "round_ref": "R009",
            "accepted_steps": ["R009/S01"],
            "acceptance_ref": "R009/S01/main-acceptance",
            "subject_digest": digest,
            "accepted_at": "2026-08-06",
            "accepted_by": "main",
        }],
    }
    sources[RUNTIME.ACCEPTANCE_EVENT_PATH] = RUNTIME.canonical_json_bytes(events)
    return sources


def multi_active_sources():
    sources = base_sources()
    legacy_state = """global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S04]"""
    versioned_state = """global_state:
  schema_version: 2
  active_rounds: [R010, R011]
  latest_accepted_round: R009
  active_steps: [R010/S04, R011/S01]"""
    for path in (
        "00_docs/works/00_key-index.md",
        "00_docs/key-context-map.md",
        "00_docs/works/r010-active/00_key-index.md",
        "00_docs/works/r010-active/runtime/00_key-index.md",
    ):
        sources[path] = sources[path].replace(
            legacy_state.encode("utf-8"), versioned_state.encode("utf-8")
        )
    sources["00_docs/works/r011-other/00_key-index.md"] = frontmatter("""
doc_type: work_round
round_status: active
key: {id: key.work.round.r011-other.index}
global_state:
  schema_version: 2
  active_rounds: [R010, R011]
  latest_accepted_round: R009
  active_steps: [R010/S04, R011/S01]
""")
    sources["00_docs/works/r011-other/other/00_key-index.md"] = frontmatter("""
doc_type: work
work_id: other
work_status: in_progress
approval: {state: pending}
key: {id: key.work.other.index}
global_state:
  schema_version: 2
  active_rounds: [R010, R011]
  latest_accepted_round: R009
  active_steps: [R010/S04, R011/S01]
""")
    sources["00_docs/works/r011-other/other/key-progress.md"] = frontmatter("""
doc_type: progress
work_status: in_progress
step_ref: R011/S01
approval: {state: pending}
finalization: {state: pending}
key: {id: key.work.other.progress}
""")
    return sources


def hierarchical_sources():
    sources = base_sources()
    for path in (
        "00_docs/works/00_key-index.md",
        "00_docs/key-context-map.md",
        "00_docs/works/r010-active/00_key-index.md",
    ):
        sources[path] = sources[path].replace(
            b"active_steps: [R010/S04]", b"active_steps: [R010-a/S01]"
        )
    parent_path = "00_docs/works/r010-active/00_key-index.md"
    sources[parent_path] = sources[parent_path].replace(
        b"approval: {state: pending}\n",
        b"approval: {state: pending}\nchild_rounds: [R010-a, R010-b]\n",
    )
    del sources["00_docs/works/r010-active/runtime/00_key-index.md"]
    del sources["00_docs/works/r010-active/runtime/key-progress.md"]
    sources["00_docs/works/r010-active/r010-a/00_key-index.md"] = frontmatter("""
doc_type: work_round
round_status: active
approval: {state: pending}
key: {id: key.work.round.r010-a.index}
""")
    sources["00_docs/works/r010-active/r010-a/runtime/00_key-index.md"] = frontmatter("""
doc_type: work
work_id: runtime
work_status: in_progress
approval: {state: pending}
key: {id: key.work.r010-a.runtime.index}
""")
    sources["00_docs/works/r010-active/r010-a/runtime/key-progress.md"] = frontmatter("""
doc_type: progress
work_status: in_progress
step_ref: R010-a/S01
approval: {state: pending}
finalization: {state: pending}
key: {id: key.work.r010-a.runtime.progress}
""")
    sources["00_docs/works/r010-active/r010-b/00_key-index.md"] = frontmatter("""
doc_type: work_round
round_status: planned
approval: {state: pending}
key: {id: key.work.round.r010-b.index}
""")
    return sources


def r008_unresolved_r010_active_sources():
    sources = base_sources()
    legacy_state = """global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S04]"""
    versioned_state = """global_state:
  schema_version: 2
  active_rounds: [R008, R010]
  latest_accepted_round: R009
  active_steps: [R010/S04]"""
    for path in (
        "00_docs/works/00_key-index.md",
        "00_docs/key-context-map.md",
        "00_docs/works/r010-active/00_key-index.md",
        "00_docs/works/r010-active/runtime/00_key-index.md",
    ):
        sources[path] = sources[path].replace(
            legacy_state.encode("utf-8"), versioned_state.encode("utf-8")
        )
    sources["00_docs/works/r008-legacy/00_key-index.md"] = frontmatter("""
doc_type: work_round
round_status: active
key: {id: key.work.round.r008-legacy.index}
global_state:
  schema_version: 2
  active_rounds: [R008, R010]
  latest_accepted_round: R009
  active_steps: [R010/S04]
""")
    sources["00_docs/works/r008-legacy/migration/00_key-index.md"] = frontmatter("""
doc_type: work
work_id: migration
work_status: in_progress
approval: {state: pending}
key: {id: key.work.migration.index}
global_state:
  schema_version: 2
  active_rounds: [R008, R010]
  latest_accepted_round: R009
  active_steps: [R010/S04]
""")
    events = json.loads(sources[RUNTIME.ACCEPTANCE_EVENT_PATH])
    events["events"][0]["subject_digest"] = RUNTIME.historical_projection_digest(
        sources
    )
    sources[RUNTIME.ACCEPTANCE_EVENT_PATH] = RUNTIME.canonical_json_bytes(events)
    return sources


def accepted_r010_with_r011_active_sources():
    sources = multi_active_sources()
    multi_state = """global_state:
  schema_version: 2
  active_rounds: [R010, R011]
  latest_accepted_round: R009
  active_steps: [R010/S04, R011/S01]"""
    remaining_state = """global_state:
  schema_version: 2
  active_rounds: [R011]
  latest_accepted_round: R010
  active_steps: [R011/S01]"""
    for path in (
        "00_docs/works/00_key-index.md",
        "00_docs/key-context-map.md",
        "00_docs/works/r010-active/00_key-index.md",
        "00_docs/works/r010-active/runtime/00_key-index.md",
        "00_docs/works/r011-other/00_key-index.md",
        "00_docs/works/r011-other/other/00_key-index.md",
    ):
        sources[path] = sources[path].replace(
            multi_state.encode("utf-8"), remaining_state.encode("utf-8")
        )
    r010_round = "00_docs/works/r010-active/00_key-index.md"
    sources[r010_round] = sources[r010_round].replace(
        b"round_status: active", b"round_status: accepted"
    ).replace(b"approval: {state: pending}", b"approval: {state: accepted}")
    r010_work = "00_docs/works/r010-active/runtime/00_key-index.md"
    sources[r010_work] = sources[r010_work].replace(
        b"work_status: in_progress", b"work_status: complete"
    ).replace(b"approval: {state: pending}", b"approval: {state: accepted}")
    r010_progress = "00_docs/works/r010-active/runtime/key-progress.md"
    sources[r010_progress] = sources[r010_progress].replace(
        b"work_status: in_progress", b"work_status: complete"
    ).replace(
        b"approval: {state: pending}", b"approval: {state: accepted}"
    ).replace(
        b"finalization: {state: pending}",
        b"finalization: {state: complete, acceptance_ref: R010/S04/main-acceptance}",
    )
    events = json.loads(sources[RUNTIME.ACCEPTANCE_EVENT_PATH])
    events["events"].append({
        "id": "R010/accepted-round",
        "sequence": 1,
        "previous_event_ref": "R009/accepted-round-migration-genesis",
        "round_ref": "R010",
        "accepted_steps": ["R010/S04"],
        "acceptance_ref": "R010/S04/main-acceptance",
        "subject_digest": "sha256:" + "1" * 64,
        "accepted_at": "2026-08-11",
        "accepted_by": "main",
    })
    sources[RUNTIME.ACCEPTANCE_EVENT_PATH] = RUNTIME.canonical_json_bytes(events)
    return sources


def write_sources(root, sources):
    for relative, raw in sources.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


class WorkStateRuntimeTest(unittest.TestCase):
    def codes(self, result):
        return {item["code"] for item in result["diagnostics"]}

    def test_whole_tree_state_and_generation_are_derived(self):
        result = RUNTIME.derive_work_state(base_sources())

        self.assertEqual("pass", result["status"])
        self.assertEqual("R010", result["state"]["active_round"])
        self.assertEqual(["R010/S04"], result["state"]["active_steps"])
        self.assertEqual("R009", result["state"]["latest_accepted_round"])
        self.assertEqual(1, len(result["state"]["active_works"]))
        self.assertTrue(result["generation"]["complete"])
        self.assertRegex(result["generation"]["source_generation"], r"^sha256:[0-9a-f]{64}$")

    def test_early_work_is_projected_from_finalization_sources(self):
        sources = base_sources()
        path = "00_docs/works/r009-history/key-finalization-manifest.json"
        sources[path] = RUNTIME.canonical_json_bytes({
            "schema_version": 3,
            "early_work": [{
                "target_step": "R009/S01",
                "cause": "independent execution",
                "status_effect": "none",
            }],
        })

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual([{
            "source_path": path,
            "source_index": 0,
            "record": {
                "target_step": "R009/S01",
                "cause": "independent execution",
                "status_effect": "none",
            },
        }], result["state"]["early_work"])

    def test_schema_v6_runtime_binding_is_digest_neutral(self):
        sources = base_sources()
        path = "00_docs/works/r010-active/key-finalization-manifest.json"
        manifest = {
            "schema_version": 6,
            "early_work": [],
            "work_state_runtime": {
                "policy_digest": "pending",
                "result_digest": "pending",
                "source_generation": "pending",
                "path_set_digest": "pending",
                "complete": False,
            },
        }
        sources[path] = RUNTIME.canonical_json_bytes(manifest)
        before = RUNTIME.derive_work_state(sources)
        manifest["work_state_runtime"] = {
            "policy_digest": before["policy_digest"],
            "result_digest": before["result_digest"],
            "source_generation": before["generation"]["source_generation"],
            "path_set_digest": before["generation"]["path_set_digest"],
            "complete": before["generation"]["complete"],
        }
        sources[path] = RUNTIME.canonical_json_bytes(manifest)

        after = RUNTIME.derive_work_state(sources)

        self.assertEqual(before["generation"], after["generation"])
        self.assertEqual(before["result_digest"], after["result_digest"])

    def test_current_repository_projection_is_authoritative(self):
        result = RUNTIME.evaluate_repository(ROOT)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual("none", result["state"]["active_round"])
        self.assertEqual([], result["state"]["active_steps"])
        self.assertEqual("R011", result["state"]["latest_accepted_round"])

    def test_multiple_active_rounds_are_recovered_without_implicit_priority(self):
        sources = multi_active_sources()

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual(4, result["state"]["schema_version"])
        self.assertIsNone(result["state"]["active_round"])
        self.assertEqual(["R010", "R011"], result["state"]["active_rounds"])
        self.assertEqual(["R010/S04", "R011/S01"], result["state"]["active_steps"])
        self.assertEqual(
            ["runtime", "other"],
            [item["work_ref"] for item in result["state"]["active_works"]],
        )
        self.assertTrue(all(
            item["active_step_resolution"] == "resolved"
            for item in result["state"]["active_works"]
        ))

    def test_hierarchical_rounds_keep_parent_global_and_child_local_state(self):
        result = RUNTIME.derive_work_state(hierarchical_sources())

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual(4, result["state"]["schema_version"])
        self.assertEqual("R010", result["state"]["active_round"])
        self.assertEqual(["R010"], result["state"]["active_rounds"])
        self.assertEqual(["R010-a"], result["state"]["active_child_rounds"])
        self.assertEqual(["R010-a/S01"], result["state"]["active_steps"])
        active_work = result["state"]["active_works"][0]
        self.assertEqual("R010-a", active_work["round_ref"])
        self.assertEqual("R010", active_work["parent_round_ref"])
        hierarchy = {
            item["round_ref"]: item for item in result["state"]["round_hierarchy"]
        }
        self.assertEqual(
            ["R010-a", "R010-b"],
            [item["round_ref"] for item in hierarchy["R010"]["child_rounds"]],
        )
        self.assertEqual(
            ["active", "planned"],
            [item["status"] for item in hierarchy["R010"]["child_rounds"]],
        )

    def test_planned_child_can_be_added_without_renumbering_existing_children(self):
        sources = hierarchical_sources()
        parent_path = "00_docs/works/r010-active/00_key-index.md"
        sources[parent_path] = sources[parent_path].replace(
            b"child_rounds: [R010-a, R010-b]",
            b"child_rounds: [R010-a, R010-b, R010-c]",
        )
        sources["00_docs/works/r010-active/r010-c/00_key-index.md"] = frontmatter("""
doc_type: work_round
round_status: planned
approval: {state: pending}
key: {id: key.work.round.r010-c.index}
""")

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        parent = next(
            item for item in result["state"]["round_hierarchy"]
            if item["round_ref"] == "R010"
        )
        self.assertEqual(
            ["R010-a", "R010-b", "R010-c"],
            [item["round_ref"] for item in parent["child_rounds"]],
        )

    def test_multiple_active_children_project_one_global_parent(self):
        sources = hierarchical_sources()
        child_path = "00_docs/works/r010-active/r010-b/00_key-index.md"
        sources[child_path] = sources[child_path].replace(
            b"round_status: planned", b"round_status: active"
        )
        sources["00_docs/works/r010-active/r010-b/other/00_key-index.md"] = frontmatter("""
doc_type: work
work_id: other
work_status: in_progress
approval: {state: pending}
key: {id: key.work.r010-b.other.index}
""")
        sources["00_docs/works/r010-active/r010-b/other/key-progress.md"] = frontmatter("""
doc_type: progress
work_status: in_progress
step_ref: R010-b/S02
approval: {state: pending}
finalization: {state: pending}
key: {id: key.work.r010-b.other.progress}
""")
        for path in (
            "00_docs/works/00_key-index.md",
            "00_docs/key-context-map.md",
            "00_docs/works/r010-active/00_key-index.md",
        ):
            sources[path] = sources[path].replace(
                b"active_steps: [R010-a/S01]",
                b"active_steps: [R010-a/S01, R010-b/S02]",
            )

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual(["R010"], result["state"]["active_rounds"])
        self.assertEqual(
            ["R010-a", "R010-b"], result["state"]["active_child_rounds"]
        )

    def test_child_acceptance_does_not_change_global_acceptance_identity(self):
        sources = hierarchical_sources()
        child_path = "00_docs/works/r010-active/r010-b/00_key-index.md"
        sources[child_path] = sources[child_path].replace(
            b"round_status: planned", b"round_status: accepted"
        ).replace(
            b"approval: {state: pending}", b"approval: {state: accepted}"
        )

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual(["R009"], result["state"]["accepted_rounds"])
        self.assertEqual("R009", result["state"]["latest_accepted_round"])

    def test_parent_acceptance_requires_every_declared_child_to_be_accepted(self):
        sources = hierarchical_sources()
        parent_path = "00_docs/works/r010-active/00_key-index.md"
        sources[parent_path] = sources[parent_path].replace(
            b"round_status: active", b"round_status: accepted"
        ).replace(
            b"approval: {state: pending}", b"approval: {state: accepted}", 1
        )

        result = RUNTIME.derive_work_state(sources)

        self.assertIn(
            "work_state_parent_acceptance_gate_unsatisfied", self.codes(result)
        )

    def test_parent_with_children_rejects_direct_detailed_work(self):
        sources = hierarchical_sources()
        sources["00_docs/works/r010-active/direct/00_key-index.md"] = frontmatter("""
doc_type: work
work_id: direct
work_status: planned
approval: {state: pending}
key: {id: key.work.direct.index}
""")

        result = RUNTIME.derive_work_state(sources)

        self.assertIn("work_state_parent_detail_work_conflict", self.codes(result))

    def test_child_membership_depth_and_identity_fail_closed(self):
        missing_sources = hierarchical_sources()
        parent_path = "00_docs/works/r010-active/00_key-index.md"
        missing_sources[parent_path] = missing_sources[parent_path].replace(
            b"child_rounds: [R010-a, R010-b]",
            b"child_rounds: [R010-a, R010-b, R010-c]",
        )
        missing_result = RUNTIME.derive_work_state(missing_sources)
        self.assertIn("work_state_child_round_unresolved", self.codes(missing_result))

        undeclared_sources = hierarchical_sources()
        undeclared_sources[
            "00_docs/works/r010-active/r010-d/00_key-index.md"
        ] = frontmatter("""
doc_type: work_round
round_status: planned
approval: {state: pending}
key: {id: key.work.round.r010-d.index}
""")
        undeclared_result = RUNTIME.derive_work_state(undeclared_sources)
        self.assertIn(
            "work_state_child_round_undeclared", self.codes(undeclared_result)
        )

        deep_sources = hierarchical_sources()
        deep_sources[
            "00_docs/works/r010-active/r010-a/r010-a/00_key-index.md"
        ] = frontmatter("""
doc_type: work_round
round_status: planned
key: {id: key.work.round.r010-a-a.index}
""")
        deep_result = RUNTIME.derive_work_state(deep_sources)
        self.assertIn("work_state_round_depth_invalid", self.codes(deep_result))

        suffix_sources = hierarchical_sources()
        suffix_sources[
            "00_docs/works/r010-active/r010-a-a/00_key-index.md"
        ] = frontmatter("""
doc_type: work_round
round_status: planned
key: {id: key.work.round.r010-a-a.index}
""")
        suffix_result = RUNTIME.derive_work_state(suffix_sources)
        self.assertIn(
            "work_state_child_round_ref_invalid", self.codes(suffix_result)
        )

        mismatch_sources = hierarchical_sources()
        mismatch_sources[
            "00_docs/works/r010-active/r011-e/00_key-index.md"
        ] = frontmatter("""
doc_type: work_round
round_status: planned
key: {id: key.work.round.r011-e.index}
""")
        mismatch_result = RUNTIME.derive_work_state(mismatch_sources)
        self.assertIn(
            "work_state_round_identity_invalid", self.codes(mismatch_result)
        )

    def test_active_work_without_active_progress_is_visible_as_unresolved(self):
        sources = base_sources()
        progress_path = "00_docs/works/r010-active/runtime/key-progress-s04.md"
        sources[progress_path] = sources.pop(
            "00_docs/works/r010-active/runtime/key-progress.md"
        )
        sources[progress_path] = sources[progress_path].replace(
            b"work_status: in_progress", b"work_status: planned"
        )
        for path in (
            "00_docs/works/00_key-index.md",
            "00_docs/key-context-map.md",
            "00_docs/works/r010-active/00_key-index.md",
            "00_docs/works/r010-active/runtime/00_key-index.md",
        ):
            sources[path] = sources[path].replace(
                b"active_steps: [R010/S04]", b"active_steps: []"
            )

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual([], result["state"]["active_steps"])
        active_work = result["state"]["active_works"][0]
        self.assertEqual("unresolved", active_work["active_step_resolution"])
        self.assertEqual("active_progress_inactive", active_work["unresolved_reason"])
        self.assertEqual([{
            "path": progress_path,
            "step_ref": "R010/S04",
            "work_status": "planned",
        }], active_work["active_step_candidates"])

    def test_r008_unresolved_work_and_r010_step_are_both_preserved(self):
        result = RUNTIME.derive_work_state(r008_unresolved_r010_active_sources())

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertIsNone(result["state"]["active_round"])
        self.assertEqual(["R008", "R010"], result["state"]["active_rounds"])
        self.assertEqual(["R010/S04"], result["state"]["active_steps"])
        works = {
            item["work_ref"]: item for item in result["state"]["active_works"]
        }
        self.assertEqual("unresolved", works["migration"]["active_step_resolution"])
        self.assertEqual("active_progress_missing", works["migration"]["unresolved_reason"])
        self.assertEqual("resolved", works["runtime"]["active_step_resolution"])

    def test_round_pointer_and_progress_body_conflicts_are_explicit(self):
        round_sources = base_sources()
        round_path = "00_docs/works/r010-active/00_key-index.md"
        round_sources[round_path] = round_sources[round_path].replace(
            b"round_status: active", b"round_status: planned"
        )
        round_result = RUNTIME.derive_work_state(round_sources)
        self.assertIn("work_state_round_source_conflict", self.codes(round_result))

        pointer_sources = base_sources()
        pointer_path = "00_docs/works/00_key-index.md"
        pointer_sources[pointer_path] = pointer_sources[pointer_path].replace(
            b"active_steps: [R010/S04]", b"active_steps: []"
        )
        pointer_result = RUNTIME.derive_work_state(pointer_sources)
        self.assertIn("work_state_pointer_stale", self.codes(pointer_result))

        body_sources = base_sources()
        progress_path = "00_docs/works/r010-active/runtime/key-progress.md"
        body_sources[progress_path] = body_sources[progress_path].replace(
            b"# Fixture\n",
            b"# Fixture\n\n## Current State\n\n"
            b"- Work status: complete\n- Step: R010/S04\n- Active: false\n",
        )
        body_result = RUNTIME.derive_work_state(body_sources)
        self.assertIn("work_state_progress_body_conflict", self.codes(body_result))

    def test_legacy_pointer_fails_explicitly_when_multiple_rounds_are_active(self):
        sources = base_sources()
        sources["00_docs/works/r011-other/00_key-index.md"] = frontmatter("""
doc_type: work_round
round_status: active
key: {id: key.work.round.r011-other.index}
""")
        sources["00_docs/works/r011-other/other/00_key-index.md"] = frontmatter("""
doc_type: work
work_id: other
work_status: in_progress
approval: {state: pending}
key: {id: key.work.other.index}
""")
        sources["00_docs/works/r011-other/other/key-progress.md"] = frontmatter("""
doc_type: progress
work_status: in_progress
step_ref: R011/S01
approval: {state: pending}
finalization: {state: pending}
key: {id: key.work.other.progress}
""")

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual(["R010", "R011"], result["state"]["active_rounds"])
        self.assertEqual(["R010/S04", "R011/S01"], result["state"]["active_steps"])
        self.assertIn(
            "work_state_legacy_active_round_unrepresentable", self.codes(result)
        )

    def test_incomplete_discovery_is_fail_closed(self):
        result = RUNTIME.derive_work_state(base_sources(), complete=False)

        self.assertEqual("fail", result["status"])
        self.assertIn("work_state_discovery_incomplete", self.codes(result))

    def test_terminal_state_rejects_residual_planned_work(self):
        sources = base_sources()
        for path in (
            "00_docs/works/r010-active/00_key-index.md",
            "00_docs/works/r010-active/runtime/key-progress.md",
        ):
            sources.pop(path)
        sources["00_docs/works/r010-active/runtime/00_key-index.md"] = frontmatter("""
doc_type: work
work_id: runtime
work_status: planned
approval: {state: pending}
key: {id: key.work.runtime.index}
""")
        for path in ("00_docs/works/00_key-index.md", "00_docs/key-context-map.md"):
            text = sources[path].decode("utf-8")
            text = text.replace("active_round: R010", "active_round: none")
            text = text.replace("active_steps: [R010/S04]", "active_steps: []")
            sources[path] = text.encode("utf-8")

        result = RUNTIME.derive_work_state(sources)

        self.assertIn("work_state_terminal_residual_work", self.codes(result))

    def test_terminal_state_allows_work_planned_under_future_planned_round(self):
        sources = base_sources()
        for path in (
            "00_docs/works/r010-active/00_key-index.md",
            "00_docs/works/r010-active/runtime/00_key-index.md",
            "00_docs/works/r010-active/runtime/key-progress.md",
        ):
            sources.pop(path)
        sources["00_docs/works/r011-future/00_key-index.md"] = frontmatter("""
doc_type: work_round
round_status: planned
approval: {state: pending}
key: {id: key.work.round.r011-future.index}
""")
        sources["00_docs/works/r011-future/future/00_key-index.md"] = frontmatter("""
doc_type: work
work_id: future
work_status: planned
approval: {state: pending}
key: {id: key.work.future.index}
""")
        for path in ("00_docs/works/00_key-index.md", "00_docs/key-context-map.md"):
            text = sources[path].decode("utf-8")
            text = text.replace("active_round: R010", "active_round: none")
            text = text.replace("active_steps: [R010/S04]", "active_steps: []")
            sources[path] = text.encode("utf-8")

        result = RUNTIME.derive_work_state(sources)

        self.assertEqual("pass", result["status"], result["diagnostics"])
        self.assertEqual("none", result["state"]["active_round"])
        self.assertEqual([], result["state"]["active_steps"])

    def test_event_fork_and_sequence_duplicate_fail(self):
        sources = base_sources()
        events = json.loads(sources[RUNTIME.ACCEPTANCE_EVENT_PATH])
        genesis = events["events"][0]
        for index, round_ref in enumerate(("R010", "R011"), start=1):
            events["events"].append({
                "id": "%s/event" % round_ref,
                "sequence": index,
                "previous_event_ref": genesis["id"],
                "round_ref": round_ref,
                "accepted_steps": [round_ref + "/S01"],
                "acceptance_ref": round_ref + "/S01/main-acceptance",
                "subject_digest": "sha256:" + str(index) * 64,
                "accepted_at": "2026-08-09",
                "accepted_by": "main",
            })

        _head, diagnostics = RUNTIME.validate_acceptance_event_chain(
            events, genesis["subject_digest"]
        )

        self.assertIn("acceptance_event_fork", {item["code"] for item in diagnostics})

    def test_event_order_uses_chain_not_date_or_round_number(self):
        sources = base_sources()
        events = json.loads(sources[RUNTIME.ACCEPTANCE_EVENT_PATH])
        genesis = events["events"][0]
        events["events"].append({
            "id": "R008/forward-event",
            "sequence": 1,
            "previous_event_ref": genesis["id"],
            "round_ref": "R008",
            "accepted_steps": ["R008/S01"],
            "acceptance_ref": "R008/S01/main-acceptance",
            "subject_digest": "sha256:" + "a" * 64,
            "accepted_at": genesis["accepted_at"],
            "accepted_by": "main",
        })

        head, diagnostics = RUNTIME.validate_acceptance_event_chain(
            events, genesis["subject_digest"]
        )

        self.assertEqual([], diagnostics)
        self.assertEqual("R008", head["round_ref"])

    def test_next_event_is_bound_to_the_unique_head_and_plus_one_sequence(self):
        sources = base_sources()
        events = json.loads(sources[RUNTIME.ACCEPTANCE_EVENT_PATH])
        genesis = events["events"][0]

        event = RUNTIME.build_next_acceptance_event(
            events, genesis["subject_digest"],
            event_id="R010/accepted-round",
            round_ref="R010",
            accepted_steps=["R010/S01"],
            acceptance_ref="R010/S01/main-acceptance",
            subject_digest="sha256:" + "f" * 64,
            accepted_at="2026-08-10",
        )

        self.assertEqual(1, event["sequence"])
        self.assertEqual(genesis["id"], event["previous_event_ref"])

    def test_prerequisite_closure_requires_evidence_and_waiver_details(self):
        complete = {
            "work_ref": "R010/S02", "result": "complete",
            "waiver_reason": None, "follow_up": None,
            "acceptance_ref": "R010/S02/main-acceptance",
            "manifest_digest": "sha256:" + "1" * 64,
            "envelope_digest": "sha256:" + "2" * 64,
            "author_runner_status": "pass",
        }
        waived = dict(complete, work_ref="R010/S03", result="waived",
                       waiver_reason="", follow_up="")

        closures, diagnostics = RUNTIME.validate_prerequisite_closures(
            [complete, waived]
        )

        self.assertEqual(2, len(closures))
        self.assertIn(
            "prerequisite_closure_waiver_incomplete",
            {item["code"] for item in diagnostics},
        )

        _closures, stale = RUNTIME.validate_prerequisite_closures(
            [complete],
            {"R010/S02": {
                "manifest_digest": "sha256:" + "3" * 64,
                "envelope_digest": complete["envelope_digest"],
                "author_runner_status": "pass",
            }},
        )
        self.assertIn(
            "prerequisite_closure_evidence_stale",
            {item["code"] for item in stale},
        )

    def test_generated_runtimes_have_byte_api_policy_and_result_parity(self):
        process = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"], cwd=str(ROOT),
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        canonical_bytes = CANONICAL.read_bytes()
        expected = RUNTIME.derive_work_state(base_sources())
        for index, path in enumerate(PACKAGE_RUNTIMES):
            with self.subTest(path=path):
                self.assertEqual(canonical_bytes, path.read_bytes())
                package = load_runtime(path, "keystone_package_work_state_%d" % index)
                self.assertEqual(RUNTIME.policy_digest(), package.policy_digest())
                self.assertEqual(RUNTIME.public_api_digest(), package.public_api_digest())
                self.assertEqual(expected, package.derive_work_state(base_sources()))

    def test_package_copy_runs_without_repository_sibling_imports(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            fixture = base / "fixture"
            write_sources(fixture, base_sources())
            for index, runtime in enumerate(PACKAGE_RUNTIMES):
                isolated = base / ("package-%d" % index)
                isolated.mkdir()
                copied = isolated / "work_state_runtime.py"
                shutil.copy2(runtime, copied)
                process = subprocess.run(
                    [sys.executable, "-I", str(copied), "--root", str(fixture)],
                    cwd=str(isolated), capture_output=True, text=True, check=False,
                )
                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("pass", json.loads(process.stdout)["status"])

    def test_four_consumer_entry_points_use_the_canonical_projection(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary) / "fixture"
            write_sources(fixture, base_sources())

            reader = subprocess.run(
                [sys.executable, "-I", str(PACKAGE_RUNTIMES[0]), "--root", str(fixture)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual("pass", json.loads(reader.stdout)["status"])

            coordinator = load_script(
                ROOT / "skills" / "keystone-coordinator" / "scripts" / "validate_closure.py",
                "keystone_test_coordinator_work_state_consumer",
            )
            self.assertEqual(
                "pass", coordinator.derive_repository_work_state(fixture)["status"]
            )

            author = load_script(
                ROOT / "skills" / "keystone-author" / "scripts" / "validate_finalization.py",
                "keystone_test_author_work_state_consumer",
            )
            runtime = RUNTIME.evaluate_repository(fixture)
            generation = runtime["generation"]
            manifest = {
                "work_state_runtime": {
                    "policy_digest": runtime["policy_digest"],
                    "result_digest": runtime["result_digest"],
                    "source_generation": generation["source_generation"],
                    "path_set_digest": generation["path_set_digest"],
                    "complete": True,
                },
                "global_state": {
                    "active_round": "R010",
                    "latest_accepted_round": "R009",
                    "active_steps": ["R010/S04"],
                },
            }
            original = author.evaluate_repository
            author.evaluate_repository = lambda _root: runtime
            try:
                self.assertEqual([], author._validate_work_state_runtime(fixture, manifest))
            finally:
                author.evaluate_repository = original

            release_root = Path(temporary) / "release"
            shutil.copytree(fixture / "00_docs", release_root / "00_docs")
            (release_root / "scripts").mkdir()
            shutil.copy2(CANONICAL, release_root / "scripts" / "work_state_runtime.py")
            release = load_script(
                ROOT / "scripts" / "run_release_gate.py",
                "keystone_test_release_work_state_consumer",
            )
            self.assertEqual(0, release._work_state_check(release_root).returncode)

    def test_multi_active_projection_is_preserved_by_actual_consumers(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary) / "fixture"
            write_sources(fixture, multi_active_sources())
            runtime = RUNTIME.evaluate_repository(fixture)
            expected_state = runtime["state"]

            reader = subprocess.run(
                [sys.executable, "-I", str(PACKAGE_RUNTIMES[0]), "--root", str(fixture)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(expected_state, json.loads(reader.stdout)["state"])

            coordinator = load_script(
                ROOT / "skills" / "keystone-coordinator" / "scripts" / "validate_closure.py",
                "keystone_test_coordinator_multi_work_state_consumer",
            )
            self.assertEqual(
                expected_state,
                coordinator.derive_repository_work_state(fixture)["state"],
            )

            author = load_script(
                ROOT / "skills" / "keystone-author" / "scripts" / "validate_finalization.py",
                "keystone_test_author_multi_work_state_consumer",
            )
            generation = runtime["generation"]
            manifest = {
                "schema_version": 6,
                "steps": [{"ref": "R010/S04"}],
                "accepted_steps": ["R010/S04"],
                "active_steps": ["R010/S04", "R011/S01"],
                "work_state_runtime": {
                    "policy_digest": runtime["policy_digest"],
                    "result_digest": runtime["result_digest"],
                    "source_generation": generation["source_generation"],
                    "path_set_digest": generation["path_set_digest"],
                    "complete": True,
                },
                "global_state": {
                    "schema_version": 2,
                    "active_rounds": ["R010", "R011"],
                    "latest_accepted_round": "R009",
                    "active_steps": ["R010/S04", "R011/S01"],
                    "sources": [
                        {
                            "category": "work_index",
                            "path": "00_docs/works/r010-active/runtime/00_key-index.md",
                            "key_id": "key.work.runtime.index",
                        },
                        {
                            "category": "round_index",
                            "path": "00_docs/works/r010-active/00_key-index.md",
                            "key_id": "key.work.round.r010-active.index",
                        },
                        {
                            "category": "root_index",
                            "path": "00_docs/works/00_key-index.md",
                            "key_id": "key.work.index",
                        },
                        {
                            "category": "context_map",
                            "path": "00_docs/key-context-map.md",
                            "key_id": "key.context-map",
                        },
                    ],
                },
            }
            original = author.evaluate_repository
            author.evaluate_repository = lambda _root: runtime
            try:
                self.assertEqual(
                    [], author._validate_work_state_runtime(fixture, manifest)
                )
            finally:
                author.evaluate_repository = original
            self.assertEqual(
                [], author.validate_global_state(fixture, manifest, 6)
            )

            release_root = Path(temporary) / "release"
            shutil.copytree(fixture / "00_docs", release_root / "00_docs")
            (release_root / "scripts").mkdir()
            shutil.copy2(CANONICAL, release_root / "scripts" / "work_state_runtime.py")
            release = load_script(
                ROOT / "scripts" / "run_release_gate.py",
                "keystone_test_release_multi_work_state_consumer",
            )
            self.assertEqual(0, release._work_state_check(release_root).returncode)

    def test_author_consumer_keeps_v2_global_pointer_compatibility_for_v3_state(self):
        runtime = RUNTIME.derive_work_state(hierarchical_sources())
        self.assertEqual("pass", runtime["status"], runtime["diagnostics"])
        author = load_script(
            ROOT / "skills" / "keystone-author" / "scripts" / "validate_finalization.py",
            "keystone_test_author_hierarchical_work_state_consumer",
        )
        finalization_global = load_script(
            ROOT / "skills" / "keystone-author" / "scripts" / "finalization_global.py",
            "keystone_test_author_hierarchical_global_state_consumer",
        )
        generation = runtime["generation"]
        manifest = {
            "work_state_runtime": {
                "policy_digest": runtime["policy_digest"],
                "result_digest": runtime["result_digest"],
                "source_generation": generation["source_generation"],
                "path_set_digest": generation["path_set_digest"],
                "complete": True,
            },
            "global_state": {
                "schema_version": 2,
                "active_rounds": ["R010"],
                "latest_accepted_round": "R009",
                "active_steps": ["R010-a/S01"],
            },
        }
        original = author.evaluate_repository
        author.evaluate_repository = lambda _root: runtime
        try:
            self.assertEqual(
                [], author._validate_work_state_runtime(ROOT, manifest)
            )
        finally:
            author.evaluate_repository = original
        active_match = finalization_global.ACTIVE_STEP_PATTERN.fullmatch(
            "R010-a/S01"
        )
        self.assertIsNotNone(active_match)
        self.assertEqual("R010", active_match.group(1))
        self.assertIsNone(
            finalization_global.STEP_PATTERN.fullmatch("R010-a/S01")
        )

    def test_finalization_can_close_one_round_while_another_remains_active(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary) / "fixture"
            write_sources(fixture, accepted_r010_with_r011_active_sources())
            runtime = RUNTIME.evaluate_repository(fixture)
            self.assertEqual("pass", runtime["status"], runtime["diagnostics"])
            self.assertEqual(["R011"], runtime["state"]["active_rounds"])
            self.assertEqual("R010", runtime["state"]["latest_accepted_round"])

            author = load_script(
                ROOT / "skills" / "keystone-author" / "scripts" / "validate_finalization.py",
                "keystone_test_author_remaining_active_round_consumer",
            )
            manifest = {
                "schema_version": 6,
                "steps": [{"ref": "R010/S04"}],
                "accepted_steps": ["R010/S04"],
                "active_steps": ["R011/S01"],
                "global_state": {
                    "schema_version": 2,
                    "active_rounds": ["R011"],
                    "latest_accepted_round": "R010",
                    "active_steps": ["R011/S01"],
                    "sources": [
                        {
                            "category": "work_index",
                            "path": "00_docs/works/r010-active/runtime/00_key-index.md",
                            "key_id": "key.work.runtime.index",
                        },
                        {
                            "category": "round_index",
                            "path": "00_docs/works/r010-active/00_key-index.md",
                            "key_id": "key.work.round.r010-active.index",
                        },
                        {
                            "category": "root_index",
                            "path": "00_docs/works/00_key-index.md",
                            "key_id": "key.work.index",
                        },
                        {
                            "category": "context_map",
                            "path": "00_docs/key-context-map.md",
                            "key_id": "key.context-map",
                        },
                    ],
                },
            }
            self.assertEqual(
                [], author.validate_global_state(fixture, manifest, 6)
            )


if __name__ == "__main__":
    unittest.main()
