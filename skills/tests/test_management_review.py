"""R015-A review decisions, event identity, concurrency and recoverable storage."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('review_state_test', ROOT / 'scripts/managed_work_state.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = m.StateStore(self.root)
        self.configure()

    def token(self):
        return m.digest(self.store.read(self.store.source_path))

    def operation(self, action, payload):
        return self.store.review(action, payload, expected_digest=self.token())

    def configure(self, mode='general'):
        return self.operation('configure', {'mode': mode})

    def entry(self, ref):
        path = '00_docs/works/' + ref.lower() + '/key-work-test.md'
        full = self.root / path
        full.parent.mkdir(parents=True, exist_ok=True)
        if not full.exists():
            full.write_text('# Test\n')
        return dict(ref=ref, kind='round', parent=None, order_path=path,
                    execution='complete', approval='accepted', finalization=None)

    def change(self, action, entry, reason=None):
        return self.store.change(action, entry, expected_digest=self.token(),
                                 at='2026-10-13', note='fixture', reason=reason)

    def close(self, ref):
        entry = self.entry(ref)
        self.change('create', entry)
        return self.change('close', entry, 'complete')

    def review(self):
        return self.store.current()['review']

    def finish(self, ticket, **overrides):
        return self.operation('finish', dict(ticket=ticket, outcome='complete',
                                             results_applied=True, **overrides))

    def test_fixed_guidance_body_matches_approved_source_and_all_packages(self):
        source = (ROOT / '00_docs/works/r015-keystone-consumer-goal-effectiveness-review'
                  / 'keystone-consumer-goal-effectiveness-review/templates/work-structure-and-review-mode.ko.md')
        body = source.read_text().split('<!-- output:start -->\n')[1].split('<!-- output:end -->')[0]
        for name in ('init', 'author', 'reader', 'coordinator', 'linker'):
            output = ROOT / ('skills/keystone-'+name) / 'references/work-structure-and-review-mode.ko.md'
            self.assertEqual(body, output.read_text())

    def test_round_can_directly_own_steps(self):
        parent = self.entry('R001'); self.change('create', parent)
        step = dict(parent, ref='R001/S01', kind='step', parent='R001', execution='in_progress')
        self.change('create', step)
        view = m.work_state_projection(self.store)['state']
        self.assertEqual(['R001/S01'], view['active_steps'])
        self.assertEqual('R001', view['active_works'][0]['execution_ref'])
        self.assertIsNone(view['active_works'][0]['work_ref'])

    def test_general_prompt_only_at_multiples_on_closed_event(self):
        for number in range(1, 11):
            advice = self.close('R%03d' % number)
            self.assertEqual(number in (5, 10), advice['prompt'])
            self.assertFalse(m.review_advice(self.review(), closed_event=False)['prompt'])
        self.assertEqual(10, len(self.review()['closed_list']))

    def test_wait_suppresses_periodic_then_prompts_every_close(self):
        blocker = self.entry('R020')
        self.change('create', blocker)
        self.operation('defer', {'rounds': ['R020'], 'reason': 'standard revision'})
        for number in range(1, 6):
            self.assertFalse(self.close('R%03d' % number)['prompt'])
        self.assertTrue(self.change('close', blocker, 'complete')['prompt'])
        self.assertTrue(self.close('R006')['prompt'])
        ticket = self.store.review_ticket('a' * 40)
        self.finish(ticket)
        self.assertEqual([], self.review()['closed_list'])
        self.assertEqual([], self.review()['full_check_wait_for'])

    def test_reopen_removes_closed_evidence_but_preserves_wait(self):
        self.close('R001')
        self.operation('defer', {'rounds': ['R001'], 'reason': 'follow-up'})
        entry = self.entry('R001')
        self.change('reopen', entry)
        self.assertEqual([], self.review()['closed_list'])
        with self.assertRaisesRegex(m.StateError, 'not closed'):
            self.store.review_ticket('a' * 40)
        self.assertTrue(self.change('close', entry, 'complete')['prompt'])

    def test_finish_preserves_concurrent_addition_and_same_ref_reclosure(self):
        self.close('R001'); self.close('R002')
        ticket = self.store.review_ticket('a' * 40)
        self.close('R003')
        entry = self.entry('R001')
        self.change('reopen', entry); self.change('close', entry, 'complete')
        self.finish(ticket)
        self.assertEqual(['R003', 'R001'], self.review()['closed_list'])

    def test_finish_preserves_new_wait_even_for_reviewed_round(self):
        self.close('R001')
        ticket = self.store.review_ticket('a' * 40)
        self.operation('defer', {'rounds': ['R001'], 'reason': 'new concern'})
        self.finish(ticket)
        self.assertEqual(['R001'], self.review()['full_check_wait_for'])
        self.assertEqual(['R001'], self.review()['closed_list'])

    def test_partial_review_and_unapplied_results_preserve_lists(self):
        self.close('R001')
        ticket = self.store.review_ticket('a' * 40)
        before = self.token()
        for outcome, applied in [('partial', True), ('complete', False)]:
            with self.assertRaises(m.StateError):
                self.operation('finish', dict(ticket=ticket, outcome=outcome, results_applied=applied))
            self.assertEqual(before, self.token())

    def test_sprint_closure_includes_parent_and_preserves_other_closures(self):
        self.configure('sprint')
        parent = self.entry('R010'); self.change('create', parent)
        self.close('R010-A')
        ticket = self.store.review_ticket('a' * 40, sprint_round='R010')
        self.close('R020')
        self.change('close', parent, 'complete')
        self.finish(ticket)
        self.assertEqual(['R020'], self.review()['closed_list'])

    def test_sprint_reopened_after_snapshot_is_not_cleaned(self):
        self.configure('sprint')
        parent = self.entry('R010'); self.change('create', parent)
        ticket = self.store.review_ticket('a' * 40, sprint_round='R010')
        self.change('close', parent, 'complete')
        self.change('reopen', parent); self.change('close', parent, 'complete')
        with self.assertRaises(m.StateError):
            self.finish(ticket)
        self.assertEqual(['R010'], self.review()['closed_list'])

    def test_no_self_wait_unknown_round_or_stale_writer(self):
        parent = self.entry('R010'); self.change('create', parent)
        for payload in [dict(rounds=['R010'], reason='x', sprint_round='R010'),
                        dict(rounds=['R999'], reason='x')]:
            with self.assertRaises(m.StateError):
                self.operation('defer', payload)
        with self.assertRaises(m.StateError):
            self.store.review('configure', {'mode': 'sprint'}, expected_digest=None)

    def test_all_reasons_and_only_rounds_count(self):
        for number, reason in enumerate(['complete', 'skipped', 'cancelled', 'superseded'], 1):
            entry = self.entry('R%03d' % number)
            if reason in ('cancelled', 'superseded'):
                entry['execution'] = reason
            self.change('create', entry); self.change('close', entry, reason)
        self.assertEqual(4, len(self.review()['closed_list']))
        parent = self.entry('R010'); self.change('create', parent)
        work = dict(parent, ref='R010/work', kind='work', parent='R010')
        self.change('create', work); self.change('close', work, 'complete')
        self.assertEqual(4, len(self.review()['closed_list']))

    def test_configuration_keeps_lists_and_legacy_v2_still_valid(self):
        self.close('R001'); self.configure('sprint')
        self.assertEqual(['R001'], self.review()['closed_list'])
        self.assertNotIn('review', m.validate_document({'schema_version': 2, 'states': {}}))
        for mode in [[], None, 42, 'bad']:
            with self.assertRaises(m.StateError):
                self.configure(mode)

    def test_closed_event_and_review_state_recover_together(self):
        entry = self.entry('R001'); self.change('create', entry)
        replace = self.store._replace
        def fail_state(path, raw):
            if path == self.store.source_path:
                raise OSError('interrupted')
            replace(path, raw)
        with patch.object(self.store, '_replace', side_effect=fail_state):
            with self.assertRaises(OSError):
                self.change('close', entry, 'complete')
        self.assertTrue(self.store.recover())
        self.assertEqual(['R001'], self.review()['closed_list'])
        self.assertEqual('closed', self.store.inspect('R001', entry['order_path'])['status'])


if __name__ == '__main__':
    unittest.main()
