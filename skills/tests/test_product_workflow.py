# keystone: id=key.test.r010.product-workflow kind=output_artifact artifact_kind=test refs=key.work.production-candidate-85-closure.order locator.test_name=ProductWorkflowIntegrationTest
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
LINKER_SCRIPTS = ROOT / "skills" / "keystone-linker" / "scripts"
READER_RUNTIME = ROOT / "skills" / "keystone-reader" / "scripts" / "work_state_runtime.py"
GRAPH_VALIDATOR = LINKER_SCRIPTS / "validate_graph.py"
GRAPH_CLASSIFIER = LINKER_SCRIPTS / "run_graph_classification.py"

sys.path.insert(0, str(LINKER_SCRIPTS))
from graph_runtime.impact import changed_seed_candidates  # noqa: E402
from graph_runtime.readiness import context_readiness  # noqa: E402
from graph_runtime.scanner import ReferenceScanner, ScanScope  # noqa: E402
from graph_runtime.snapshot_validation import reconstruct, validate_snapshot  # noqa: E402


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WORK_STATE = load_module("keystone_product_workflow_state", ROOT / "scripts/work_state_runtime.py")


def json_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_json(value):
    return digest_bytes(json_bytes(value))


class ProductWorkflowIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="keystone-product-workflow-")
        self.base = Path(self.temporary.name)
        self.root = self.base / "repository"
        self.cache = self.base / "cache" / "reference-index.sqlite3"
        (self.root / ".git").mkdir(parents=True)
        self.write(".git/HEAD", "ref: refs/heads/main\n")
        self.create_fixture()

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative, text):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def create_fixture(self):
        global_state = """global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S07]"""
        self.write(
            "00_docs/key-context-map.md",
            """---
doc_type: context_map
key: {id: key.context-map}
%s
---
# Context Map
""" % global_state,
        )
        self.write(
            "00_docs/works/00_key-index.md",
            """---
doc_type: work_round_index
key: {id: key.work.index}
%s
---
# Works
""" % global_state,
        )
        self.write(
            "00_docs/works/r009-history/00_key-index.md",
            """---
doc_type: work_round
round_status: accepted
approval: {state: accepted}
key: {id: key.work.round.r009-history.index}
---
# R009
""",
        )
        self.write(
            "00_docs/works/r009-history/accepted/00_key-index.md",
            """---
doc_type: work
work_id: accepted
work_status: complete
approval: {state: accepted}
key: {id: key.work.accepted.index}
---
# Accepted Work
""",
        )
        self.write(
            "00_docs/works/r009-history/accepted/key-progress.md",
            """---
doc_type: progress
work_status: complete
step_ref: R009/S01
approval: {state: accepted}
finalization: {state: complete, acceptance_ref: R009/S01/main-acceptance}
key: {id: key.work.accepted.progress}
---
# Accepted Progress
""",
        )
        self.write(
            "00_docs/works/r010-product-workflow/00_key-index.md",
            """---
doc_type: work_round
round_status: active
approval: {state: pending}
key: {id: key.work.round.r010-product-workflow.index}
%s
---
# R010 Product Workflow
""" % global_state,
        )
        self.write(
            "00_docs/works/r010-product-workflow/verification/00_key-index.md",
            """---
doc_type: work
work_id: verification
work_status: in_progress
approval: {state: pending}
key: {id: key.work.product-workflow.index}
%s
---
# Product Workflow Verification
""" % global_state,
        )
        self.work_order = self.write(
            "00_docs/works/r010-product-workflow/verification/key-work-verification.md",
            """---
doc_type: work_order
work_status: in_progress
approval: {state: pending}
key:
  id: key.work.product-workflow.order
---
# Product Workflow Work

## Goal

Apply the accepted policy limit without losing traceability.

## Completion Criteria

<!-- key: id=key.acceptance.fixture.limit kind=claim requires_verification_of=key.code.fixture.policy -->
- The implementation and test enforce the standard limit.
""",
        )
        self.progress = self.write(
            "00_docs/works/r010-product-workflow/verification/key-progress.md",
            """---
doc_type: progress
work_status: in_progress
step_ref: R010/S07
approval: {state: pending}
finalization: {state: pending}
key: {id: key.work.product-workflow.progress}
---
# Product Workflow Progress

## Current Evidence

- Implementation: pending
- Verification: pending
- Resume point: update code and its focused test.
""",
        )
        self.standard = self.write(
            "00_docs/standards/policy.md",
            """---
doc_type: standard
document_lifecycle: active
approval: {state: accepted}
key:
  id: key.standard.fixture.policy
  relations:
    produces:
      - target: key.code.fixture.policy
---
# Fixture Policy

The accepted maximum is 3.
""",
        )
        self.code = self.write(
            "src/policy.py",
            """# keystone: id=key.code.fixture.policy kind=output_artifact artifact_kind=code implements=key.acceptance.fixture.limit locator.symbol=normalize_limit
def normalize_limit(value):
    return min(value, 3)
""",
        )
        self.test = self.write(
            "tests/test_policy.py",
            """# keystone: id=key.test.fixture.policy kind=output_artifact artifact_kind=test verifies=key.code.fixture.policy locator.test_name=test_limit
import importlib.util
import unittest
from pathlib import Path


POLICY_PATH = Path(__file__).parents[1] / "src" / "policy.py"
SPEC = importlib.util.spec_from_file_location("fixture_policy", POLICY_PATH)
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


class PolicyTest(unittest.TestCase):
    def test_limit(self):
        self.assertEqual(3, POLICY.normalize_limit(5))


if __name__ == "__main__":
    unittest.main()
""",
        )
        sources = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in (self.root / "00_docs").rglob("*")
            if path.is_file()
        }
        historical_digest = WORK_STATE.historical_projection_digest(sources)
        event = {
            "schema_version": 1,
            "events": [{
                "id": "R009/accepted-round-migration-genesis",
                "sequence": 0,
                "previous_event_ref": None,
                "round_ref": "R009",
                "accepted_steps": ["R009/S01"],
                "acceptance_ref": "R009/S01/main-acceptance",
                "subject_digest": historical_digest,
                "accepted_at": "2026-08-06",
                "accepted_by": "main",
            }],
        }
        event_path = self.root / WORK_STATE.ACCEPTANCE_EVENT_PATH
        event_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.write_bytes(WORK_STATE.canonical_json_bytes(event))

    def repository_context(self):
        return context_readiness(
            self.root,
            self.cache,
            initiator="linker",
            artifact_context=True,
            include_typed_graph=True,
        )

    def reader_state(self):
        process = subprocess.run(
            [sys.executable, "-I", str(READER_RUNTIME), "--root", str(self.root)],
            cwd=str(self.root),
            env={"PATH": os.defpath},
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(process.stdout)
        self.assertEqual(0, process.returncode, payload)
        return payload

    def test_pwf01_standard_to_implementation_and_progress(self):
        before = self.repository_context()
        edges = {
            (item.source_id, item.relation, item.target_id)
            for item in before.result.typed_graph.edges
        }
        self.assertIn(
            ("key.standard.fixture.policy", "produces", "key.code.fixture.policy"),
            edges,
        )
        self.assertIn(
            ("key.acceptance.fixture.limit", "requires_verification_of",
             "key.code.fixture.policy"),
            edges,
        )
        self.assertIn(
            ("key.code.fixture.policy", "implements", "key.acceptance.fixture.limit"),
            edges,
        )
        self.assertIn(
            ("key.test.fixture.policy", "verifies", "key.code.fixture.policy"),
            edges,
        )

        self.standard.write_text(
            self.standard.read_text(encoding="utf-8")
            .replace("approval: {state: accepted}", "approval: {state: pending}")
            .replace("maximum is 3", "maximum is 2"),
            encoding="utf-8",
        )
        self.code.write_text(
            self.code.read_text(encoding="utf-8").replace("min(value, 3)", "min(value, 2)"),
            encoding="utf-8",
        )
        self.test.write_text(
            self.test.read_text(encoding="utf-8")
            .replace("assertEqual(3", "assertEqual(2"),
            encoding="utf-8",
        )
        self.progress.write_text(
            self.progress.read_text(encoding="utf-8")
            .replace("Implementation: pending", "Implementation: bounded change complete")
            .replace("Verification: pending", "Verification: pass")
            .replace("update code and its focused test", "Main review"),
            encoding="utf-8",
        )

        verification = subprocess.run(
            [sys.executable, "-I", str(self.test)],
            cwd=str(self.root),
            env={"PATH": os.defpath},
            capture_output=True,
            text=True,
            check=False,
        )
        after = self.repository_context()

        self.assertEqual(0, verification.returncode, verification.stderr)
        self.assertEqual("refreshed", after.cache_status)
        self.assertNotEqual(before.result.freshness.digest, after.result.freshness.digest)
        self.assertIn("Verification: pass", self.progress.read_text(encoding="utf-8"))
        self.assertIn("Resume point: Main review", self.progress.read_text(encoding="utf-8"))

    def test_pwf02_reverse_stale_and_metadata_gap_are_distinct(self):
        graph_sources = (
            "00_docs/standards/policy.md",
            "00_docs/works/r010-product-workflow/verification/key-work-verification.md",
            "src/policy.py",
            "tests/test_policy.py",
        )
        snapshot, parse_diagnostics = reconstruct(self.root, graph_sources)
        self.assertEqual((), validate_snapshot(self.root, snapshot, parse_diagnostics))
        candidates = {
            item.node.id: item.grade.value
            for item in changed_seed_candidates(snapshot, ("key.code.fixture.policy",))
        }
        self.assertEqual("strong_candidate", candidates["key.standard.fixture.policy"])
        self.assertEqual("required", candidates["key.acceptance.fixture.limit"])
        self.assertEqual("required", candidates["key.test.fixture.policy"])

        self.code.write_text(
            self.code.read_text(encoding="utf-8")
            .replace("def normalize_limit", "def clamp_limit"),
            encoding="utf-8",
        )
        stale_snapshot, stale_parse = reconstruct(self.root, graph_sources)
        mechanical = {
            item.code for item in validate_snapshot(self.root, stale_snapshot, stale_parse)
        }
        self.assertIn("locator_symbol_stale", mechanical)

        unowned = self.write("src/untracked.py", "def untracked():\n    return True\n")
        indexed = ReferenceScanner(self.root).scan(ScanScope.REPOSITORY)
        self.assertNotIn("src/untracked.py", {item.path for item in indexed.owners})
        delta = {
            "kind": "artifact_delta",
            "source_surface": "src/untracked.py",
            "change_kind": "added",
            "changed_locators": [{"path": "src/untracked.py", "symbol": "untracked"}],
            "semantic_summary": "Unowned source requires an explicit owner handoff decision.",
            "baseline_digest": "absent",
            "resulting_digest": digest_bytes(unowned.read_bytes()),
            "graph_relevant": False,
        }
        sources = ["src/untracked.py"]
        manifest = {
            "schema_version": 1,
            "delta_set_digest": digest_json([delta]),
            "deltas": [delta],
            "source_context": {
                "repository_root_digest": digest_json(str(self.root.resolve())),
                "coverage": {
                    "mode": "delta_set",
                    "complete": True,
                    "source_count": 1,
                    "source_path_digest": digest_json(sources),
                },
                "sources": sources,
            },
        }
        manifest_path = self.base / "classification-input.json"
        manifest_path.write_bytes(json_bytes(manifest))
        process = subprocess.run(
            [sys.executable, str(GRAPH_CLASSIFIER), "--root", str(self.root),
             "--manifest", str(manifest_path)],
            cwd=str(self.root),
            env={"PATH": os.defpath},
            capture_output=True,
            text=True,
            check=False,
        )
        classification = json.loads(process.stdout)

        self.assertEqual(0, process.returncode, classification)
        self.assertEqual("not_applicable", classification["disposition"])
        self.assertEqual(["added_plain_unowned_source"], classification["reason_codes"])
        self.assertEqual("def untracked():\n    return True\n", unowned.read_text(encoding="utf-8"))

    def test_pwf03_fresh_reader_recovers_and_detects_drift(self):
        before_state = self.reader_state()
        before_context = self.repository_context()
        checkpoint = {
            "work_state": before_state["generation"]["source_generation"],
            "repository": before_context.result.freshness.digest,
        }

        order_text = self.work_order.read_text(encoding="utf-8")
        progress_text = self.progress.read_text(encoding="utf-8")
        self.assertIn("## Goal", order_text)
        self.assertIn("## Completion Criteria", order_text)
        self.assertIn("Implementation: pending", progress_text)
        self.assertIn("Resume point: update code and its focused test", progress_text)
        self.assertEqual(["R010/S07"], before_state["state"]["active_steps"])

        self.progress.write_text(
            progress_text.replace(
                "Implementation: pending",
                "Implementation: code changed; verification pending",
            ),
            encoding="utf-8",
        )
        self.code.write_text(
            self.code.read_text(encoding="utf-8").replace("min(value, 3)", "min(value, 2)"),
            encoding="utf-8",
        )
        after_state = self.reader_state()
        after_context = self.repository_context()

        self.assertEqual(["R010/S07"], after_state["state"]["active_steps"])
        self.assertNotEqual(
            checkpoint["work_state"], after_state["generation"]["source_generation"]
        )
        self.assertNotEqual(checkpoint["repository"], after_context.result.freshness.digest)

    def test_pwf04_default_local_operation_needs_no_external_trust(self):
        reader = self.reader_state()
        process = subprocess.run(
            [sys.executable, "-I", str(GRAPH_VALIDATOR), "--root", str(self.root),
             "--scope", "repository"],
            cwd=str(self.root),
            env={"PATH": os.defpath},
            capture_output=True,
            text=True,
            check=False,
        )
        graph = json.loads(process.stdout)
        context = self.repository_context()
        forbidden_outputs = [
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*")
            if path.is_file()
            and (path.suffix == ".key" or "receipt" in path.name.lower()
                 or "evidence" in path.name.lower())
        ]

        self.assertEqual("pass", reader["status"])
        self.assertEqual(0, process.returncode, graph)
        self.assertEqual("pass", graph["status"])
        self.assertTrue(context.result.freshness.complete)
        self.assertEqual([], forbidden_outputs)


if __name__ == "__main__":
    unittest.main()
