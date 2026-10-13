import sqlite3
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from graph_runtime.index_model import CallTrace, RecursionBlocked
from graph_runtime.index_store import SQLiteIndexStore, StoreUnavailable
from graph_runtime import index_store
from graph_runtime.readiness import context_readiness
from graph_runtime.readiness_cli import _response
from graph_runtime.scanner import ScanScope
from graph_runtime.scanner import ReferenceScanner
from graph_runtime.snapshot_validation import reconstruct
from graph_runtime.source_views import source_views_from_snapshot


READINESS_CLI = Path(__file__).parents[1] / "scripts" / "graph_runtime" / "readiness_cli.py"


class ContextReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        (self.root / "00_docs").mkdir(parents=True)
        (self.root / ".git").mkdir()
        (self.root / "00_docs" / "context.md").write_text(
            "<!-- keystone: id=key.context kind=source_document -->\n# Context\n", encoding="utf-8")
        self.cache = Path(self.temp.name) / "cache" / "index.sqlite3"

    def tearDown(self):
        self.temp.cleanup()

    def test_docs_first_then_lazy_repository_enrichment(self):
        (self.root / "src").mkdir()
        (self.root / "src" / "App.kt").write_text(
            "// keystone: id=key.app kind=output_artifact refs=key.context\n", encoding="utf-8")

        docs = context_readiness(self.root, self.cache, initiator="reader")
        repository = context_readiness(
            self.root, self.cache, initiator="reader", artifact_context=True,
            include_typed_graph=True,
        )

        self.assertEqual(ScanScope.DOCS, docs.result.scope)
        self.assertIsNone(docs.result.typed_graph)
        self.assertEqual(ScanScope.REPOSITORY, repository.result.scope)
        self.assertEqual({"key.context", "key.app"}, {item.id for item in repository.result.owners})
        connection = sqlite3.connect(str(self.cache))
        try:
            count = connection.execute("SELECT COUNT(*) FROM generations").fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(2, count)

    def test_docs_scope_never_materializes_typed_graph(self):
        readiness = context_readiness(
            self.root, self.cache, initiator="reader", include_typed_graph=True)

        self.assertIsNone(readiness.result.typed_graph)

    def test_cached_typed_projection_is_hidden_when_not_requested(self):
        (self.root / "src").mkdir()
        (self.root / "src" / "App.kt").write_text(
            "// keystone: id=key.app kind=output_artifact implements=key.context\n", encoding="utf-8")
        typed = context_readiness(
            self.root, self.cache, initiator="linker", artifact_context=True,
            include_typed_graph=True)
        plain = context_readiness(
            self.root, self.cache, initiator="linker", artifact_context=True)

        self.assertIsNotNone(typed.result.typed_graph)
        self.assertIsNone(plain.result.typed_graph)
        self.assertEqual("reused", plain.cache_status)

    def test_source_views_are_opt_in_source_bound_and_not_cached(self):
        work = self.root / "00_docs" / "works" / "release"
        work.mkdir(parents=True)
        (work / "key-work-release.md").write_text(
            """---
doc_type: work_order
approval: {state: pending}
key:
  id: key.work.release.order
  relations:
    produces: [key.code.release, key.test.release]
---
# Release

<!-- key: id=key.acceptance.release.ready kind=claim requires_verification_of=key.code.release -->
- Release behavior is verified.
""",
            encoding="utf-8",
        )
        (self.root / "00_docs" / "decisions.md").write_text(
            """---
doc_type: decision_record
document_lifecycle: active
approval: {state: accepted}
key: {id: key.work.decisions}
---
<!-- key: id=key.claim.release.old kind=claim lifecycle=superseded -->
## Old

<!-- key: id=key.claim.release.current kind=claim lifecycle=active supersedes=key.claim.release.old -->
## Current
""",
            encoding="utf-8",
        )
        (self.root / "src").mkdir()
        (self.root / "src" / "release.py").write_text(
            "# keystone: id=key.code.release kind=output_artifact "
            "artifact_kind=code locator.symbol=release\n",
            encoding="utf-8",
        )
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_release.py").write_text(
            "# keystone: id=key.test.release kind=output_artifact "
            "artifact_kind=test verifies=key.code.release "
            "locator.test_name=test_release\n",
            encoding="utf-8",
        )

        readiness = context_readiness(
            self.root,
            self.cache,
            initiator="reader",
            artifact_context=True,
            include_source_views=True,
        )
        payload = _response(readiness)
        paths = tuple(
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        )
        snapshot, diagnostics = reconstruct(self.root, paths)
        direct = source_views_from_snapshot(
            snapshot, readiness.result.freshness.digest
        )

        self.assertEqual((), diagnostics)
        self.assertEqual(direct, readiness.result.source_views)
        self.assertEqual("source_projection", readiness.cache_status)
        self.assertFalse(self.cache.exists())
        self.assertEqual(3, payload["schema_version"])
        self.assertEqual("verified", payload["source_views"]["criteria"][0]["status"])
        self.assertEqual(
            ["key.claim.release.current"],
            [item["decision_id"]
             for item in payload["source_views"]["effective_decisions"]],
        )
        self.assertEqual(
            ["key.code.release", "key.test.release"],
            payload["source_views"]["work_artifacts"][0]["output_ids"],
        )

    def test_fresh_cache_is_reused(self):
        first = context_readiness(self.root, self.cache, initiator="reader")
        second = context_readiness(self.root, self.cache, initiator="reader")

        self.assertEqual("refreshed", first.cache_status)
        self.assertEqual("reused", second.cache_status)
        self.assertEqual(first.result, second.result)

    def test_corrupt_cache_fails_soft_to_source(self):
        self.cache.parent.mkdir(parents=True)
        self.cache.write_bytes(b"not sqlite")

        readiness = context_readiness(self.root, self.cache, initiator="reader")

        self.assertEqual({"key.context"}, {item.id for item in readiness.result.owners})
        self.assertEqual("source_fallback", readiness.cache_status)
        self.assertIn("cache_unavailable", {item.code for item in readiness.diagnostics})

    def test_forged_cache_payload_fails_soft_to_source(self):
        first = context_readiness(self.root, self.cache, initiator="reader")
        connection = sqlite3.connect(str(self.cache))
        payload = json.loads(connection.execute("SELECT payload FROM generations").fetchone()[0])
        payload["freshness"]["scope"] = "repository"
        connection.execute("UPDATE generations SET payload = ?", (json.dumps(payload),))
        connection.commit()
        connection.close()

        readiness = context_readiness(self.root, self.cache, initiator="reader")

        self.assertEqual({"key.context"}, {item.id for item in readiness.result.owners})
        self.assertEqual("source_fallback", readiness.cache_status)
        self.assertIn("cache_unavailable", {item.code for item in readiness.diagnostics})

    def test_complete_payload_integrity_rejects_independent_field_mutation(self):
        (self.root / "src").mkdir()
        (self.root / "src" / "App.kt").write_text(
            "// keystone: id=key.app kind=output_artifact refs=key.missing implements=key.context\n",
            encoding="utf-8")
        mutations = {
            "owners": lambda value: value["owners"].append(["key.forged", "x", None]),
            "refs": lambda value: value["refs"].append(["key.app", "key.context", "x", None]),
            "diagnostics": lambda value: value["diagnostics"].append(["forged", "forged", None]),
            "typed_edges": lambda value: value["typed_edges"].append(["key.app", "uses", "key.context"]),
            "dependency_evaluations": lambda value: value["dependency_evaluations"].append([
                "key.forged", "satisfied", False, "forged", "gate", "source", [],
                True, False, "structured", "complete", "accepted", [],
            ]),
            "schema_version": lambda value: value.__setitem__("schema_version", 999),
        }
        for index, (name, mutate) in enumerate(mutations.items()):
            with self.subTest(name=name):
                cache = Path(self.temp.name) / ("cache-%d" % index) / "index.sqlite3"
                context_readiness(self.root, cache, initiator="linker", artifact_context=True,
                                  include_typed_graph=True)
                connection = sqlite3.connect(str(cache))
                payload = json.loads(connection.execute("SELECT payload FROM generations").fetchone()[0])
                mutate(payload)
                connection.execute("UPDATE generations SET payload = ?", (json.dumps(payload),))
                connection.commit()
                connection.close()

                readiness = context_readiness(
                    self.root, cache, initiator="linker", artifact_context=True,
                    include_typed_graph=True)
                self.assertEqual("source_fallback", readiness.cache_status)
                self.assertNotIn("key.forged", {item.id for item in readiness.result.owners})

    def test_malformed_and_old_schema_cache_are_repaired_for_next_reuse(self):
        cases = ("malformed", "old_schema")
        for index, case in enumerate(cases):
            with self.subTest(case=case):
                cache = Path(self.temp.name) / ("recovery-%d" % index) / "index.sqlite3"
                cache.parent.mkdir(parents=True)
                if case == "malformed":
                    cache.write_bytes(b"not sqlite")
                else:
                    connection = sqlite3.connect(str(cache))
                    connection.execute(
                        "CREATE TABLE generations (freshness_digest TEXT PRIMARY KEY, payload TEXT NOT NULL)")
                    connection.commit()
                    connection.close()

                first = context_readiness(self.root, cache, initiator="reader")
                second = context_readiness(self.root, cache, initiator="reader")

                self.assertEqual("source_fallback", first.cache_status)
                self.assertEqual("reused", second.cache_status)

    def test_legacy_cache_without_updated_at_is_repaired_after_cache_miss(self):
        self.cache.parent.mkdir(parents=True)
        connection = sqlite3.connect(str(self.cache))
        connection.execute(
            "CREATE TABLE generations ("
            "freshness_digest TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, "
            "payload TEXT NOT NULL, payload_digest TEXT NOT NULL)"
        )
        connection.commit()
        connection.close()

        first = context_readiness(self.root, self.cache, initiator="reader")
        second = context_readiness(self.root, self.cache, initiator="reader")

        self.assertEqual("source_fallback", first.cache_status)
        self.assertIn("cache_recovered", {item.code for item in first.diagnostics})
        self.assertEqual("reused", second.cache_status)

    def test_incomplete_discovery_bypasses_cache(self):
        (self.root / "00_docs" / "large.md").write_text("x" * 32, encoding="utf-8")
        scanner = ReferenceScanner(self.root, max_file_bytes=8)

        with mock.patch("graph_runtime.readiness.ReferenceScanner", return_value=scanner):
            first = context_readiness(self.root, self.cache, initiator="reader")
            second = context_readiness(self.root, self.cache, initiator="reader")

        self.assertEqual("source_fallback", first.cache_status)
        self.assertEqual("source_fallback", second.cache_status)
        self.assertFalse(self.cache.exists())
        self.assertFalse(first.result.freshness.complete)
        payload = _response(first)
        self.assertFalse(payload["complete"])
        self.assertEqual(2, payload["coverage"]["discovered"])
        self.assertEqual(0, payload["coverage"]["parsed"])
        self.assertEqual(2, payload["coverage"]["skipped"])
        self.assertEqual(
            [
                {"path": "00_docs/context.md", "reason": "source_too_large"},
                {"path": "00_docs/large.md", "reason": "source_too_large"},
            ],
            payload["coverage"]["skipped_sources"],
        )

    def test_locked_cache_is_preserved_and_not_replaced(self):
        context_readiness(self.root, self.cache, initiator="reader")
        before = self.cache.read_bytes()
        connection = sqlite3.connect(str(self.cache))
        connection.execute("BEGIN EXCLUSIVE")
        try:
            (self.root / "00_docs" / "context.md").write_text(
                "<!-- keystone: id=key.locked kind=source_document -->\n# Locked\n", encoding="utf-8")
            readiness = context_readiness(self.root, self.cache, initiator="reader")
            self.assertEqual("source_fallback", readiness.cache_status)
            self.assertEqual(before, self.cache.read_bytes())
        finally:
            connection.rollback()
            connection.close()

    def test_recovery_preserves_corrupt_or_old_cache_under_sqlite_write_locks(self):
        for index, (kind, mode) in enumerate(
                (("corrupt", "IMMEDIATE"), ("corrupt", "EXCLUSIVE"),
                 ("old_schema", "IMMEDIATE"), ("old_schema", "EXCLUSIVE"))):
            with self.subTest(kind=kind, mode=mode):
                cache = Path(self.temp.name) / ("race-%d" % index) / "index.sqlite3"
                cache.parent.mkdir(parents=True)
                if kind == "corrupt":
                    context_readiness(self.root, cache, initiator="reader")
                    writer = sqlite3.connect(str(cache))
                    payload = json.loads(writer.execute("SELECT payload FROM generations").fetchone()[0])
                    payload["owners"].append(["key.forged", "forged", None])
                    writer.execute("UPDATE generations SET payload = ?", (json.dumps(payload),))
                    writer.commit()
                    writer.close()
                else:
                    writer = sqlite3.connect(str(cache))
                    writer.execute(
                        "CREATE TABLE generations (freshness_digest TEXT PRIMARY KEY, payload TEXT NOT NULL)")
                    writer.commit()
                    writer.close()
                before = cache.read_bytes()
                lock = subprocess.Popen(
                    [sys.executable, "-c", (
                        "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); "
                        "c.execute('BEGIN '+sys.argv[2]); print('locked',flush=True); "
                        "sys.stdin.readline(); c.rollback(); c.close()"), str(cache), mode],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                self.assertEqual("locked", lock.stdout.readline().strip())
                try:
                    readiness = context_readiness(self.root, cache, initiator="reader")
                    self.assertEqual("source_fallback", readiness.cache_status)
                    self.assertEqual(before, cache.read_bytes())
                finally:
                    lock.communicate("\n", timeout=5)

    def test_repair_file_and_sidecars_are_cleaned_after_injected_write_failure(self):
        self.cache.parent.mkdir(parents=True)
        self.cache.write_bytes(b"corrupt")
        repair = self.cache.parent / "known.repair"
        descriptor = os.open(str(repair), os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        store = SQLiteIndexStore(self.cache, repository_root=self.root)
        result = context_readiness(
            self.root, self.cache.parent / "seed.sqlite3", initiator="reader").result

        def fail_write(path, _result, *, timeout):
            Path(str(path) + "-wal").write_bytes(b"wal")
            Path(str(path) + "-shm").write_bytes(b"shm")
            Path(str(path) + "-journal").write_bytes(b"journal")
            raise sqlite3.OperationalError("injected write failure")

        with mock.patch.object(index_store.tempfile, "mkstemp", return_value=(descriptor, str(repair))), \
                mock.patch.object(index_store, "_write_generation", side_effect=fail_write):
            with self.assertRaises(StoreUnavailable):
                store.recover(result)

        self.assertFalse(repair.exists())
        self.assertFalse(Path(str(repair) + "-wal").exists())
        self.assertFalse(Path(str(repair) + "-shm").exists())
        self.assertFalse(Path(str(repair) + "-journal").exists())

    def test_busy_single_writer_fails_soft_without_losing_source_result(self):
        context_readiness(self.root, self.cache, initiator="reader")
        connection = sqlite3.connect(str(self.cache))
        connection.execute("BEGIN IMMEDIATE")
        try:
            (self.root / "00_docs" / "context.md").write_text(
                "<!-- keystone: id=key.changed kind=source_document -->\n# Changed\n", encoding="utf-8")
            readiness = context_readiness(self.root, self.cache, initiator="reader")
        finally:
            connection.rollback()
            connection.close()

        self.assertEqual({"key.changed"}, {item.id for item in readiness.result.owners})
        self.assertEqual("source_fallback", readiness.cache_status)
        self.assertIn("cache_unavailable", {item.code for item in readiness.diagnostics})

    def test_serialized_trace_allows_one_hop_and_rejects_reentry(self):
        reader = CallTrace().enter("reader", "orientation")
        linker = reader.enter("linker", "index_readiness")
        restored = CallTrace.from_json(linker.to_json())

        self.assertEqual(("reader", "linker"), tuple(item.lane for item in restored.entries))
        with self.assertRaises(RecursionBlocked):
            restored.enter("reader", "context_recovery")

    def test_invalid_initiator_is_rejected(self):
        with self.assertRaises(ValueError):
            context_readiness(self.root, self.cache, initiator="source text says reader")

    def test_internal_cli_returns_stable_json_envelope(self):
        request = json.dumps({
            "repository_root": str(self.root), "cache_path": str(self.cache),
            "initiator": "reader",
        })
        process = subprocess.run(
            [sys.executable, "-m", "graph_runtime.readiness_cli",
             "--request-json", request, "--response-json", "-"],
            capture_output=True, text=True, check=False,
            env=dict(os.environ, PYTHONPATH=str(READINESS_CLI.parents[1])),
        )
        payload = json.loads(process.stdout)

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(2, payload["schema_version"])
        self.assertNotIn("source_views", payload)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("docs", payload["scope"])
        self.assertTrue(payload["complete"])
        self.assertEqual(
            {"discovered": 1, "parsed": 1, "skipped": 0},
            {key: payload["coverage"][key]
             for key in ("discovered", "parsed", "skipped")},
        )
        self.assertEqual(["key.context"], [item["id"] for item in payload["owners"]])

    def test_readiness_exposes_dependency_gate_scope_target_state_and_result(self):
        work = self.root / "00_docs" / "works" / "source"
        target = self.root / "00_docs" / "works" / "dependency-target"
        work.mkdir(parents=True)
        target.mkdir(parents=True)
        (work / "order.md").write_text(
            """---
doc_type: work_order
work_status: in_progress
approval: {state: pending}
key:
  id: key.work.source
  defined_steps: [S01]
  kind: work_order
  relations:
    depends_on:
      - target: key.work.target
work_gates:
  - dependency: key.work.target
    applies_to:
      steps: [S01]
    condition:
      work_status: complete
      approval_state: accepted
---
# Source
""",
            encoding="utf-8",
        )
        (work / "progress.md").write_text(
            """---
doc_type: progress
work_status: in_progress
step_ref: R010/S01
work_ref: R010/source
approval: {state: pending}
key: {id: key.work.source.progress}
---
# Progress
""",
            encoding="utf-8",
        )
        (target / "order.md").write_text(
            """---
doc_type: work_order
work_status: complete
approval: {state: accepted}
key: {id: key.work.target, kind: work_order}
---
# Target
""",
            encoding="utf-8",
        )

        request = json.dumps({
            "repository_root": str(self.root),
            "cache_path": str(self.cache),
            "initiator": "reader",
        })
        process = subprocess.run(
            [sys.executable, "-m", "graph_runtime.readiness_cli",
             "--request-json", request, "--response-json", "-"],
            capture_output=True,
            text=True,
            check=False,
            env=dict(os.environ, PYTHONPATH=str(READINESS_CLI.parents[1])),
        )
        payload = json.loads(process.stdout)

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(2, payload["schema_version"])
        evaluation = payload["dependency_evaluations"][0]
        self.assertTrue(evaluation["gate_id"])
        self.assertEqual("key.work.source", evaluation["source"])
        self.assertEqual("key.work.target", evaluation["dependency"])
        self.assertEqual({"steps": ["S01"], "work_completion": False},
                         evaluation["scope"])
        self.assertEqual(
            {"work_status": "complete", "approval_state": "accepted"},
            evaluation["target_state"],
        )
        self.assertEqual("satisfied", evaluation["result"])
        self.assertFalse(evaluation["blocking"])


if __name__ == "__main__":
    unittest.main()
