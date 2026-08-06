import concurrent.futures
import tempfile
import unittest
from pathlib import Path

from graph_runtime.readiness import context_readiness
from graph_runtime.scanner import ScanScope


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
        source.write_text(
            "<!-- keystone: id=key.claim.after kind=claim refs=key.claim.before -->\n# After\n",
            encoding="utf-8",
        )
        refreshed = context_readiness(self.root, self.cache, initiator="reader")

        self.assertEqual("refreshed", first.cache_status)
        self.assertEqual("reused", reused.cache_status)
        self.assertEqual("refreshed", refreshed.cache_status)
        self.assertEqual({"key.claim.after"}, {item.id for item in refreshed.result.owners})
        self.assertNotEqual(reused.result.freshness.digest, refreshed.result.freshness.digest)

    def test_code_context_is_lazy_and_coordinator_can_reuse_fresh_result(self):
        self.write("00_docs/standard.md", "<!-- keystone: id=key.claim.docs kind=claim -->\n# Docs\n")
        self.write(
            "src/App.kt",
            "// keystone: id=key.artifact.app kind=output_artifact refs=key.claim.docs\nclass App\n",
        )

        docs = context_readiness(self.root, self.cache, initiator="reader")
        repository = context_readiness(
            self.root, self.cache, initiator="linker", artifact_context=True)
        coordinator_reuse = context_readiness(
            self.root, self.cache, initiator="linker", artifact_context=True)

        self.assertEqual(ScanScope.DOCS, docs.result.scope)
        self.assertEqual({"key.claim.docs"}, {item.id for item in docs.result.owners})
        self.assertEqual(ScanScope.REPOSITORY, repository.result.scope)
        self.assertEqual(
            {"key.claim.docs", "key.artifact.app"},
            {item.id for item in repository.result.owners},
        )
        self.assertEqual("reused", coordinator_reuse.cache_status)
        self.assertEqual(repository.result, coordinator_reuse.result)

    def test_multi_agent_requests_serialize_or_fail_soft_without_losing_source(self):
        self.write("00_docs/context.md", "<!-- keystone: id=key.context kind=claim -->\n# Context\n")

        def ready(_):
            return context_readiness(self.root, self.cache, initiator="reader")

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = tuple(pool.map(ready, range(18)))

        for result in results:
            self.assertEqual({"key.context"}, {item.id for item in result.result.owners})
            self.assertIn(result.cache_status, {"refreshed", "reused", "source_fallback"})
        final = context_readiness(self.root, self.cache, initiator="reader")
        self.assertEqual("reused", final.cache_status)


if __name__ == "__main__":
    unittest.main()
