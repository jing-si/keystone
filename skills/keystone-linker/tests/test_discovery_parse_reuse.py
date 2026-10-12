"""Lexical admission, owner/ref and source views share one parse per source."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from graph_runtime.adapters import KotlinJavaAdapter
from graph_runtime.readiness import context_readiness
from graph_runtime.scanner import ReferenceScanner, ScanScope
from graph_runtime.snapshot_validation import reconstruct
from graph_runtime.source_views import source_views_from_snapshot


class DiscoveryParseReuseTests(unittest.TestCase):
    def test_one_lexical_scan_for_targeted_expansion_and_source_views(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'work.md').write_text('---\ndoc_type: work_order\nkey:\n  id: key.work.example\n  relations:\n    produces: [key.code.example]\n---\n# Work\n')
            (root/'Example.kt').write_text('// keystone: id=key.code.example kind=output_artifact locator.symbol=Example\nclass Example\n')
            original = KotlinJavaAdapter.scan_metadata
            calls = []
            def counted(adapter, text):
                calls.append(text)
                return original(adapter, text)
            with mock.patch.object(KotlinJavaAdapter, 'scan_metadata', counted):
                readiness = context_readiness(root, root.parent/'unused-cache.sqlite3',
                    initiator='reader', artifact_context=True, discovery_mode='targeted',
                    anchors=[{'id': 'key.work.example', 'path': 'work.md'}],
                    owner_paths={'key.code.example': 'Example.kt'}, relation_types=['produces'],
                    include_source_views=True)
            self.assertEqual(1, len(calls))
            snapshot, findings = reconstruct(root, ['work.md', 'Example.kt'])
            self.assertEqual((), findings)
            self.assertEqual(source_views_from_snapshot(snapshot, readiness.result.freshness.digest),
                             readiness.result.source_views)

    def test_same_scanner_invalidates_parse_after_raw_byte_change(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root/'Example.kt'
            source.write_text('// keystone: id=key.code.before kind=output_artifact\n')
            scanner = ReferenceScanner(root)
            before = scanner.scan(ScanScope.REPOSITORY)
            source.write_text('// keystone: id=key.code.after kind=output_artifact\n')
            after = scanner.scan(ScanScope.REPOSITORY)
            self.assertEqual(['key.code.after'], [o.id for o in after.owners])
            self.assertNotEqual(before.freshness.digest, after.freshness.digest)


if __name__ == '__main__':
    unittest.main()
