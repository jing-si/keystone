import concurrent.futures
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from graph_runtime.readiness import context_readiness
from graph_runtime.scanner import ReferenceScanner, ScanScope


class ReferenceIndexIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repository"
        (self.root / ".git").mkdir(parents=True)
        (self.root / "00_docs").mkdir()
        self.cache = Path(self.temporary.name) / "external-cache" / "index.sqlite3"

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative, text):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def test_reader_docs_first_reuses_then_author_write_refreshes(self):
        source = self.write(
            "00_docs/standard.md",
            "<!-- keystone: id=key.claim.before kind=claim -->\n# Before\n",
        )

        first = context_readiness(self.root, self.cache, initiator="reader")
        reused = context_readiness(self.root, self.cache, initiator="reader")
        before_token = reused.result.freshness
        self.assertEqual({"key.claim.before"}, {item.id for item in reused.result.owners})
        source.write_text(
            "<!-- keystone: id=key.claim.after kind=claim refs=key.claim.before -->\n# After\n",
            encoding="utf-8",
        )
        refreshed = context_readiness(self.root, self.cache, initiator="reader")

        self.assertEqual("refreshed", first.cache_status)
        self.assertEqual("reused", reused.cache_status)
        self.assertEqual("refreshed", refreshed.cache_status)
        self.assertEqual({"key.claim.after"}, {item.id for item in refreshed.result.owners})
        self.assertNotEqual(before_token, refreshed.result.freshness)

    def test_fresh_repository_handoff_reuses_exact_result_without_rebuild(self):
        self.write("00_docs/standard.md", "<!-- keystone: id=key.claim.docs kind=claim -->\n# Docs\n")
        self.write(
            "src/App.kt",
            "// keystone: id=key.artifact.app kind=output_artifact refs=key.claim.docs\nclass App\n",
        )

        docs = context_readiness(self.root, self.cache, initiator="reader")
        repository = context_readiness(
            self.root, self.cache, initiator="linker", artifact_context=True)
        with mock.patch.object(
                ReferenceScanner, "scan_discovery",
                side_effect=AssertionError("fresh handoff must not rebuild source index")):
            downstream_reuse = context_readiness(
                self.root, self.cache, initiator="linker", artifact_context=True)

        self.assertEqual(ScanScope.DOCS, docs.result.scope)
        self.assertEqual({"key.claim.docs"}, {item.id for item in docs.result.owners})
        self.assertEqual(ScanScope.REPOSITORY, repository.result.scope)
        self.assertEqual(
            {"key.claim.docs", "key.artifact.app"},
            {item.id for item in repository.result.owners},
        )
        self.assertEqual("reused", downstream_reuse.cache_status)
        self.assertEqual(repository.result.freshness, downstream_reuse.result.freshness)
        self.assertEqual(repository.result, downstream_reuse.result)

    def test_forced_multi_process_contention_falls_back_without_cache_damage(self):
        source = self.write(
            "00_docs/context.md",
            "<!-- keystone: id=key.context.before kind=claim -->\n# Context\n")
        context_readiness(self.root, self.cache, initiator="reader")
        before_cache = self.cache.read_bytes()
        lock = subprocess.Popen(
            [sys.executable, "-c", (
                "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); "
                "c.execute('BEGIN IMMEDIATE'); print('locked', flush=True); "
                "sys.stdin.readline(); c.rollback(); c.close()"), str(self.cache)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.assertEqual("locked", lock.stdout.readline().strip())
        source.write_text(
            "<!-- keystone: id=key.context.after kind=claim -->\n# Changed\n",
            encoding="utf-8")

        def ready(_):
            return context_readiness(self.root, self.cache, initiator="reader")

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                results = tuple(pool.map(ready, range(12)))
        finally:
            lock.communicate("\n", timeout=5)

        for result in results:
            self.assertEqual({"key.context.after"}, {item.id for item in result.result.owners})
            self.assertEqual("source_fallback", result.cache_status)
            self.assertIn("cache_unavailable", {item.code for item in result.diagnostics})
        self.assertEqual(before_cache, self.cache.read_bytes())

        refreshed = context_readiness(self.root, self.cache, initiator="reader")
        reused = context_readiness(self.root, self.cache, initiator="reader")
        self.assertEqual("refreshed", refreshed.cache_status)
        self.assertEqual("reused", reused.cache_status)


if __name__ == "__main__":
    unittest.main()
