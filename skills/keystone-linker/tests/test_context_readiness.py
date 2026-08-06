import sqlite3
import json
import tempfile
import unittest
from pathlib import Path

from graph_runtime.index_model import CallTrace, RecursionBlocked
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
