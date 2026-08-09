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
        self.assertEqual("R010", result["state"]["active_round"])
        self.assertEqual(["R010/S05"], result["state"]["active_steps"])
        self.assertEqual("R009", result["state"]["latest_accepted_round"])

    def test_multiple_active_round_and_stale_pointer_fail(self):
        sources = base_sources()
        sources["00_docs/works/r011-other/00_key-index.md"] = frontmatter("""
doc_type: work_round
round_status: active
key: {id: key.work.round.r011-other.index}
""")

        result = RUNTIME.derive_work_state(sources)

        self.assertIn("work_state_multiple_active_rounds", self.codes(result))
        self.assertIn("work_state_pointer_stale", self.codes(result))

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


if __name__ == "__main__":
    unittest.main()
