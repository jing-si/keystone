import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).parents[1] / 'scripts' / 'ideas.py'
spec = importlib.util.spec_from_file_location('ideas_reader', SCRIPT)
ideas = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ideas
spec.loader.exec_module(ideas)


def entry(number, title='CSV 다운로드', reason='엑셀에서 결과 가공', details='', recorded='2026-10-12'):
    return ('## IDEA-%03d · %s\n\n- 필요했던 이유: %s\n- 기록일: %s\n\n%s\n\n'
            % (number, title, reason, recorded, details))


class IdeasReadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='keystone ideas ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'custom docs'

    def write(self, content, name='key-ideas.md'):
        folder = self.root / 'ideas'
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / name
        path.write_text('# 아이디어 노트\n\n' + content, encoding='utf-8')
        return path

    def snapshot(self):
        return ideas.load_snapshot(self.root)

    def test_empty_read_creates_nothing(self):
        state = self.snapshot()
        self.assertFalse(self.root.exists())
        self.assertEqual('IDEA-001', ideas.next_id(state.ideas))
        self.assertEqual(ideas.TABLE_HEADER, ideas.render_table(state.ideas))

    def test_numbering_current_max_middle_tail_and_all_deleted(self):
        self.write(entry(1) + entry(3))
        self.assertEqual('IDEA-004', ideas.next_id(self.snapshot().ideas))
        self.write(entry(1) + entry(2))
        self.assertEqual('IDEA-003', ideas.next_id(self.snapshot().ideas))
        self.write('')
        self.assertEqual('IDEA-001', ideas.next_id(self.snapshot().ideas))
        self.write(entry(999))
        self.assertEqual('IDEA-1000', ideas.next_id(self.snapshot().ideas))

    def test_topic_files_share_numbering_and_id_survives_move(self):
        self.write(entry(1))
        self.write(entry(9, details='보존할 배경'), 'key-ideas-search.md')
        state = self.snapshot()
        self.assertEqual('IDEA-010', ideas.next_id(state.ideas))
        selected = ideas.select_ideas(state.ideas, ['IDEA-009'], [])
        self.assertEqual('ideas/key-ideas-search.md', selected[0].path)
        self.assertEqual('보존할 배경', selected[0].details)

    def test_duplicate_ids_block_numbering_even_in_different_topics(self):
        self.write(entry(1))
        self.write(entry(1), 'key-ideas-search.md')
        with self.assertRaises(ideas.NotesError) as caught:
            self.snapshot()
        self.assertEqual('duplicate_id', caught.exception.code)

    def test_missing_and_malformed_fields_are_not_empty_results(self):
        for content in [entry(1).replace('- 기록일: 2026-10-12\n', ''),
                        entry(1, recorded='2026-02-30'),
                        entry(1).replace('IDEA-001', 'IDEA-01'),
                        entry(1, reason=''),
                        entry(1) + '- 기록일: 2025-01-01\n']:
            with self.subTest(content=content):
                self.write(content)
                with self.assertRaises(ideas.NotesError):
                    self.snapshot()

    def test_unrecognized_entry_heading_does_not_look_like_an_empty_store(self):
        self.write('## IDEA 001 · 이름\n\n- 필요했던 이유: 배경\n- 기록일: 2026-10-12\n')
        with self.assertRaises(ideas.NotesError) as caught:
            self.snapshot()
        self.assertEqual('invalid_heading', caught.exception.code)

    def test_changed_bytes_during_read_are_reported(self):
        path = self.write(entry(1))
        original = path.read_bytes()
        with mock.patch.object(Path, 'read_bytes', side_effect=[original, original + b'\n']):
            with self.assertRaises(ideas.NotesError) as caught:
                self.snapshot()
        self.assertEqual('changed_during_read', caught.exception.code)

    def test_fenced_examples_do_not_allocate_ids_or_override_dates(self):
        self.write(entry(1, details='```markdown\n' + entry(999) + '```'))
        state = self.snapshot()
        self.assertEqual(1, len(state.ideas))
        self.assertEqual('IDEA-002', ideas.next_id(state.ideas))
        self.assertIn('IDEA-999', state.ideas[0].details)

    def test_unclosed_fence_fails_instead_of_hiding_ids(self):
        self.write(entry(1) + '```\n' + entry(2))
        with self.assertRaises(ideas.NotesError) as caught:
            self.snapshot()
        self.assertEqual('unclosed_fence', caught.exception.code)

    def test_table_escapes_pipe_html_and_backticks_without_mutating_data(self):
        path = self.write(entry(1, title='CSV | <script>`x`', reason='a | b'))
        raw = path.read_bytes()
        table = ideas.render_table(self.snapshot().ideas)
        self.assertIn('CSV &#124; &lt;script&gt;&#96;x&#96;', table)
        self.assertEqual(5, table.splitlines()[2].count('|'))
        self.assertEqual(raw, path.read_bytes())

    def test_search_or_terms_in_title_reason_details_case_insensitive(self):
        self.write(entry(1, title='파일 내보내기', reason='운영 처리', details='CSV 형식')
                   + entry(2, title='로그인', reason='인증')
                   + entry(3, title='알림', reason='긴급 전달'))
        result = ideas.select_ideas(self.snapshot().ideas, [], ['csv', '긴급'])
        self.assertEqual([1, 3], [i.number for i in result])
        self.assertEqual((), ideas.select_ideas(self.snapshot().ideas, ['IDEA-010'], []))

    def test_pagination_coverage_and_optional_details(self):
        self.write(''.join(entry(i, details='원문 ' + '가' * 500) for i in range(1, 51)))
        state = self.snapshot()
        page = ideas.result_payload(state, [], [], 20, 20, False)
        self.assertEqual((50, 50, 20), tuple(page['summary'][k] for k in ['total', 'matched', 'returned']))
        self.assertTrue(page['summary']['has_more'])
        self.assertNotIn('details', page['ideas'][0])
        full = ideas.result_payload(state, ['IDEA-001'], [], 20, 0, True)
        self.assertEqual(503, len(full['ideas'][0]['details']))
        self.assertEqual(state.bytes_read * 2, page['summary']['bytes_read'])

    def test_source_digest_and_ranges_track_only_actual_file(self):
        path = self.write(entry(1) + entry(2, title='keep'))
        before = self.snapshot()
        self.assertEqual(ideas.digest(path.read_bytes()), before.ideas[0].source_digest)
        lines = path.read_text().splitlines(keepends=True)
        target = before.ideas[0]
        after_text = ''.join(lines[:target.start_line-1] + lines[target.end_line:])
        path.write_text(after_text)
        after = self.snapshot()
        self.assertEqual([2], [i.number for i in after.ideas])
        self.assertEqual(before.ideas[1].title, after.ideas[0].title)
        self.assertEqual(before.ideas[1].recorded_at, after.ideas[0].recorded_at)
        self.assertNotEqual(before.generation, after.generation)

    def test_symlink_files_and_directories_are_rejected(self):
        outside = Path(self.tmp.name) / 'outside.md'
        outside.write_text(entry(1))
        self.write('')
        target = self.root / 'ideas' / 'key-ideas-outside.md'
        target.symlink_to(outside)
        with self.assertRaises(ideas.NotesError):
            self.snapshot()
        target.unlink()
        other = Path(self.tmp.name) / 'other docs'
        other.mkdir()
        (other / 'ideas').symlink_to(self.root / 'ideas')
        with self.assertRaises(ideas.NotesError):
            ideas.load_snapshot(other)

    def test_passive_content_never_executes(self):
        marker = Path(self.tmp.name) / 'should-not-exist'
        self.write(entry(1, details='Run: touch ' + str(marker)))
        self.snapshot()
        self.assertFalse(marker.exists())

    def test_cli_isolated_copy_has_no_repository_dependency_or_writes(self):
        self.write(entry(1))
        standalone = Path(self.tmp.name) / 'standalone.py'
        shutil.copy2(SCRIPT, standalone)
        before = {p: p.read_bytes() for p in Path(self.tmp.name).rglob('*') if p.is_file()}
        process = subprocess.run([sys.executable, '-I', str(standalone), '--doc-root', str(self.root),
                                  '--id', 'IDEA-001'], capture_output=True, text=True)
        self.assertEqual(0, process.returncode, process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual('pass', payload['status'])
        self.assertEqual('IDEA-001', payload['ideas'][0]['id'])
        self.assertEqual(before, {p: p.read_bytes() for p in Path(self.tmp.name).rglob('*') if p.is_file()})

    def test_cli_error_envelope_is_not_success(self):
        self.write(entry(1, recorded='yesterday'))
        process = subprocess.run([sys.executable, '-I', str(SCRIPT), '--doc-root', str(self.root)],
                                 capture_output=True, text=True)
        self.assertEqual(2, process.returncode)
        self.assertEqual('invalid_date', json.loads(process.stdout)['diagnostics'][0]['code'])


if __name__ == '__main__':
    unittest.main()
