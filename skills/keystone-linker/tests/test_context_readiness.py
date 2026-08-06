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
from graph_runtime.scanner import ScanScope


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


if __name__ == "__main__":
    unittest.main()
