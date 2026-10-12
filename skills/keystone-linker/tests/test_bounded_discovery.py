"""R018: bounded preparation must not silently reconstruct a repository."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from graph_runtime.readiness import context_readiness
from graph_runtime.readiness_cli import _response
from graph_runtime.scanner import ReferenceScanner


class BoundedDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.cache = Path(self.temp.name) / 'cache.sqlite3'
        self.write('00_docs/work.md', '---\ndoc_type: work_order\nkey:\n  id: key.work.example\n  relations:\n    produces: [key.code.example]\n---\n# Example\n')
        self.write('src/example.kt', '// keystone: id=key.code.example kind=output_artifact locator.symbol=Example\nclass Example\n')
        self.write('unrelated/noise.kt', '// keystone: id=key.code.noise kind=output_artifact\n')

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def request(self, **kwargs):
        args = dict(initiator='reader', artifact_context=True, discovery_mode='targeted',
                    anchors=[{'id': 'key.work.example', 'path': '00_docs/work.md'}])
        args.update(kwargs)
        return context_readiness(self.root, self.cache, **args)

    def test_targeted_expands_declared_output_without_tree_discovery(self):
        with mock.patch.object(ReferenceScanner, '_paths', side_effect=AssertionError('full scan')):
            result = self.request(owner_paths={'key.code.example': 'src/example.kt'},
                                  relation_types=['produces'], include_source_views=True)
        payload = _response(result)
        self.assertEqual({'key.work.example', 'key.code.example'},
                         {owner.id for owner in result.result.owners})
        self.assertEqual(4, payload['schema_version'])
        self.assertEqual('bounded', payload['discovery']['coverage_kind'])
        self.assertEqual('targeted', payload['discovery']['mode'])
        self.assertNotIn('unrelated/noise.kt', result.result.freshness.discovered_paths)
        self.assertIsNotNone(result.result.source_views)

    def test_missing_locator_never_promotes_to_audit(self):
        with mock.patch.object(ReferenceScanner, '_paths', side_effect=AssertionError('full scan')):
            result = self.request(relation_types=['produces'])
        self.assertIn('owner_unresolved', {d.code for d in result.diagnostics})
        self.assertFalse(_response(result)['complete'])

    def test_stale_anchor_digest_is_visible(self):
        result = self.request(anchors=[{'id': 'key.work.example', 'path': '00_docs/work.md',
                                        'digest': 'sha256:' + '0' * 64}])
        self.assertIn('stale_anchor', {d.code for d in result.diagnostics})
        self.assertFalse(_response(result)['complete'])

    def test_missing_anchor_does_not_scan(self):
        with mock.patch.object(ReferenceScanner, '_paths', side_effect=AssertionError('full scan')):
            result = self.request(anchors=[])
        self.assertFalse(_response(result)['complete'])
        self.assertEqual((), result.result.owners)

    def test_lookup_admits_exact_owner_not_string_mentions(self):
        self.write('src/fake.kt', 'val example = "key.code.example"\n')
        result = self.request(discovery_mode='lookup', anchors=[{'id': 'key.code.example'}],
                              lookup_roots=['src'])
        payload = _response(result)
        self.assertEqual(['key.code.example'], [o.id for o in result.result.owners])
        self.assertEqual(['src'], payload['discovery']['search_roots'])
        self.assertEqual(2, payload['discovery']['searched_files'])
        self.assertIsNone(result.result.typed_graph)

    def test_path_escape_and_symlink_are_rejected(self):
        for path in ['../outside.kt', str(self.root / 'src/example.kt')]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.request(anchors=[{'id': 'key.code.example', 'path': path}])
        (self.root / 'alias').symlink_to(self.root / 'src', target_is_directory=True)
        result = self.request(anchors=[{'id': 'key.code.example', 'path': 'alias/example.kt'}])
        self.assertFalse(_response(result)['complete'])

    def test_audit_remains_explicit(self):
        result = self.request(discovery_mode='audit', anchors=[])
        self.assertIn('key.code.noise', {o.id for o in result.result.owners})
        self.assertEqual('scope', _response(result)['discovery']['coverage_kind'])

    def test_ignored_tree_is_pruned_before_visit(self):
        self.write('node_modules/nested/file.kt', '// keystone: id=key.ignored\n')
        import os
        original = os.scandir
        def guarded(path):
            self.assertNotIn('node_modules', Path(path).parts)
            self.assertNotIn('unrelated', Path(path).parts)
            return original(path)
        with mock.patch('os.scandir', side_effect=guarded):
            result = self.request(discovery_mode='audit', anchors=[], includes=['src/*.kt'])
        self.assertEqual({'key.code.example'}, {o.id for o in result.result.owners})

    def test_depth_and_file_budgets_report_incomplete_without_audit(self):
        for extra in ({'max_depth': 0}, {'max_files': 1}):
            with self.subTest(extra=extra):
                result = self.request(owner_paths={'key.code.example': 'src/example.kt'},
                                      relation_types=['produces'], **extra)
                self.assertFalse(_response(result)['complete'])
                self.assertIn('owner_unresolved', {d.code for d in result.diagnostics})

    def test_cache_states_do_not_change_targeted_scope_or_require_access(self):
        from graph_runtime.index_store import SQLiteIndexStore
        with mock.patch.object(SQLiteIndexStore, 'load', side_effect=AssertionError('cache access')):
            self.cache.write_bytes(b'corrupt cache')
            before = self.cache.read_bytes()
            first = self.request()
            self.write('00_docs/work.md', '---\nkey: {id: key.work.example}\n---\n# Changed\n')
            second = self.request()
        self.assertEqual(before, self.cache.read_bytes())
        self.assertNotEqual(first.result.freshness.digest, second.result.freshness.digest)

    def test_lookup_negative_evidence_is_bound_to_searched_bytes(self):
        first = self.request(discovery_mode='lookup', anchors=[{'id': 'key.code.absent'}],
                             lookup_roots=['src'])
        self.write('src/added.kt', '// keystone: id=key.code.absent kind=output_artifact\n')
        second = self.request(discovery_mode='lookup', anchors=[{'id': 'key.code.absent'}],
                              lookup_roots=['src'])
        self.assertNotEqual(first.discovery.search_digest, second.discovery.search_digest)
        self.assertEqual(['key.code.absent'], [o.id for o in second.result.owners])

    def test_lookup_filters_other_ids_in_candidate_source(self):
        self.write('src/ref.kt', '// keystone: id=key.code.other refs=key.code.example\n')
        result = self.request(discovery_mode='lookup', anchors=[{'id': 'key.code.example'}],
                              lookup_roots=['src'])
        self.assertEqual(['key.code.example'], [o.id for o in result.result.owners])

    def test_lookup_missing_root_is_not_complete(self):
        result = self.request(discovery_mode='lookup', anchors=[{'id': 'key.code.example'}],
                              lookup_roots=['missing'])
        self.assertIn('lookup_root_unavailable', {d.code for d in result.diagnostics})
        self.assertFalse(_response(result)['complete'])

    def test_ambiguous_owner_and_invalid_anchor_inputs_are_not_hidden(self):
        self.write('src/duplicate.kt', '// keystone: id=key.code.example kind=output_artifact\n')
        result = self.request(discovery_mode='lookup', anchors=[{'id': 'key.code.example'}],
                              lookup_roots=['src'])
        self.assertIn('owner_ambiguous', {d.code for d in result.diagnostics})
        for extra in ({'anchors': [{'id': 'key.work.example', 'digest': 'bad'}]},
                      {'source_paths': '../outside'}, {'follow_refs': 'yes'},
                      {'max_depth': -1}, {'relation_types': ['unknown']}):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.request(**extra)

    def test_explicit_missing_source_resolves_canonical_companion(self):
        import json
        companion = {
            'schema_version': 1,
            'source': {'path': 'src/generated.py', 'surface': 'companion_metadata',
                       'baseline_digest': 'absent'},
            'nodes': [{'id': 'key.code.generated', 'kind': 'output_artifact',
                       'artifact_kind': 'code', 'locator': {'path': 'src/generated.py',
                       'symbol': 'generated'}, 'lifecycle': 'active',
                       'provenance': {'produced_from': [], 'governed_by': []}}],
            'relations': [],
        }
        self.write('src/generated.py.keystone.json', json.dumps(companion))
        result = self.request(anchors=[{'id': 'key.code.generated', 'path': 'src/generated.py'}],
                              include_source_views=True)
        self.assertEqual(['key.code.generated'], [owner.id for owner in result.result.owners])
        self.assertTrue(_response(result)['complete'])

    def test_legacy_suffix_glob_and_explicit_rooted_glob_are_separate(self):
        self.write('nested/src/extra.kt', '// keystone: id=key.code.extra kind=output_artifact\n')
        from graph_runtime.scanner import ScanScope
        legacy = ReferenceScanner(self.root, includes=['src/*.kt']).scan(ScanScope.REPOSITORY)
        explicit = self.request(discovery_mode='audit', anchors=[], includes=['src/*.kt'])
        self.assertIn('key.code.extra', {owner.id for owner in legacy.owners})
        self.assertNotIn('key.code.extra', {owner.id for owner in explicit.result.owners})

    def test_unsupported_explicit_source_with_views_is_diagnostic(self):
        self.write('src/data.unknown', 'opaque data')
        result = self.request(source_paths=['src/data.unknown'], include_source_views=True)
        self.assertIn('unsupported_surface', {d.code for d in result.result.diagnostics})
        self.assertFalse(_response(result)['complete'])

    def test_legacy_docs_ignore_plain_json_while_explicit_target_reports_it(self):
        from graph_runtime.scanner import ScanScope
        self.write('00_docs/history.json', '{}')
        legacy = ReferenceScanner(self.root).scan(ScanScope.DOCS)
        self.assertNotIn('unsupported_surface', {d.code for d in legacy.diagnostics})
        targeted = self.request(source_paths=['00_docs/history.json'])
        self.assertIn('unsupported_surface', {d.code for d in targeted.result.diagnostics})


if __name__ == '__main__':
    unittest.main()
