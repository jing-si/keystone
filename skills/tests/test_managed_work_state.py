"""Behavioral tests for current-only state and append-only management events."""

import importlib.util
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("managed_work_state_test", ROOT / "scripts/managed_work_state.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class ManagedWorkStateTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.order_path = "00_docs/works/r024-example/key-work-example.md"
        self.order = self.root / self.order_path
        self.order.parent.mkdir(parents=True)
        self.order.write_text("# Work\n\nKeep human evidence.\n", encoding="utf-8")
        self.store = runtime.StateStore(self.root)
        self.entry = {"ref": "R024", "kind": "round", "parent": None,
                      "order_path": self.order_path, "execution": "planned",
                      "approval": "pending", "finalization": None}

    def token(self):
        return runtime.digest(self.store.read(self.store.source_path))

    def change(self, action, entry=None, **options):
        item = entry or self.entry
        token = runtime.digest(self.store.read(self.store.source_path))
        self.store.change(action, item, expected_digest=token,
                          at="2026-10-12", note="Test evidence", **options)

    def assert_code(self, code, function, *args, **kwargs):
        with self.assertRaises(runtime.StateError) as caught:
            function(*args, **kwargs)
        self.assertEqual(code, caught.exception.code)

    def test_create_is_planned_and_does_not_write_open_field(self):
        self.change("create")
        self.assertEqual("planned", self.store.current()["items"][0]["execution"])
        self.assertNotIn("open", self.order.read_text())
        self.assertEqual("created", runtime.events(self.order.read_bytes(), "R024")[0]["event"])

    def test_daily_list_never_reads_work_order(self):
        self.change("create")
        read = self.store.read
        def read_current_only(path):
            self.assertNotIn("/works/", path)
            return read(path)
        with patch.object(self.store, "read", side_effect=read_current_only):
            self.assertEqual(1, len(self.store.current()["items"]))

    def test_fifty_rounds_share_one_state_first_file_and_one_digest(self):
        for number in range(1, 51):
            item = dict(self.entry, ref="R%03d" % number,
                        execution="blocked" if number % 2 else "planned")
            self.change("create", item)
        path = self.root / "00_docs/state/current.json"
        self.assertTrue(path.exists())
        value = json.loads(path.read_text())
        self.assertEqual(2, value["schema_version"])
        self.assertEqual(25, len(value["states"]["blocked"]))
        self.assertEqual(25, len(value["states"]["planned"]))
        self.assertNotIn("execution", value["states"]["blocked"][0])
        self.assertFalse((path.parent / "rounds").exists())
        self.assertEqual(1, len(self.store.current()["sources"]))
        stale = self.token()
        self.change("update", dict(self.entry, ref="R001", execution="in_progress"))
        self.assert_code("state_stale", self.store.change, "update",
                         dict(self.entry, ref="R002", execution="complete"),
                         expected_digest=stale, at="2026-10-13", note="Another writer")

    def test_regular_update_moves_group_and_appends_state_change_history(self):
        self.change("create")
        before = self.order.read_bytes()
        self.entry["execution"] = "in_progress"
        self.change("update")
        self.assertTrue(self.order.read_bytes().startswith(before))
        event = runtime.events(self.order.read_bytes(), "R024")[-1]
        self.assertEqual("updated", event["event"])
        self.assertEqual("planned", event["before"]["execution"])
        self.assertEqual("in_progress", event["result"]["execution"])
        groups = json.loads(self.store.read(self.store.source_path))["states"]
        self.assertNotIn("planned", groups)
        self.assertEqual("R024", groups["in_progress"][0]["ref"])
        self.assertEqual("in_progress", self.store.current()["items"][0]["execution"])

    def test_completion_waits_for_acceptance_and_finalization(self):
        self.change("create")
        self.entry["execution"] = "complete"
        self.change("update")
        self.assert_code("state_close_unfinished", self.change, "close", reason="complete")
        self.entry.update(approval="accepted", finalization="in_progress")
        self.change("update")
        self.assert_code("state_close_unfinished", self.change, "close", reason="complete")
        self.assertEqual(1, len(self.store.current()["items"]))

    def test_close_removes_state_and_reopen_preserves_closed_event(self):
        self.change("create")
        self.entry.update(execution="complete", approval="accepted", finalization="complete")
        self.change("update")
        self.change("close", reason="complete")
        closed_bytes = self.order.read_bytes()
        self.assertEqual([], self.store.current()["items"])
        self.assertEqual({}, json.loads(self.store.read(self.store.source_path))["states"])
        self.assertEqual("closed", self.store.inspect("R024", self.order_path)["status"])
        self.entry.update(execution="planned", approval="pending", finalization=None)
        self.change("reopen")
        self.assertTrue(self.order.read_bytes().startswith(closed_bytes))
        self.assertEqual(["created", "updated", "closed", "reopened"],
                         [e["event"] for e in runtime.events(self.order.read_bytes(), "R024")])
        self.assertEqual("managed", self.store.inspect("R024", self.order_path)["status"])

    def test_absence_is_unknown_or_missing_never_implicitly_complete(self):
        self.assertEqual("unknown", self.store.inspect("R024", self.order_path)["status"])
        self.change("create")
        self.store.path(self.store.source_path).unlink()
        self.assertEqual("missing", self.store.inspect("R024", self.order_path)["status"])

    def test_cancel_skip_and_supersede_are_distinct_events(self):
        for reason, execution in (("cancelled", "cancelled"), ("skipped", "planned"),
                                  ("superseded", "superseded")):
            with self.subTest(reason=reason):
                if self.store.inspect("R024", self.order_path)["status"] == "closed":
                    self.entry["execution"] = execution
                    self.change("reopen")
                else:
                    self.entry["execution"] = execution
                    self.change("create")
                self.change("close", reason=reason)
                self.assertEqual(reason, self.store.inspect("R024", self.order_path)["last_event"]["reason"])

    def test_stale_writer_cannot_overwrite_new_state(self):
        self.change("create")
        stale = self.token()
        self.entry["execution"] = "in_progress"
        self.change("update")
        before = self.token()
        self.entry["execution"] = "blocked"
        self.assert_code("state_stale", self.store.change, "update", self.entry,
                         expected_digest=stale, at="2026-10-13", note="Stale update")
        self.assertEqual(before, self.token())

    def test_parent_cannot_close_before_managed_child(self):
        self.change("create")
        child = dict(self.entry, ref="R024/build", parent="R024", kind="work")
        self.change("create", child)
        self.assert_code("state_children_managed", self.change, "close", reason="skipped")

    def test_invalid_parent_and_identity_are_rejected(self):
        self.change("create")
        child = dict(self.entry, ref="R024/S01", parent="R024/missing", kind="step")
        self.assert_code("state_parent_missing", self.change, "create", child)
        self.assert_code("state_identity_invalid", runtime.validate_entry,
                         dict(self.entry, ref="R024/S01", kind="work"))

    def test_interrupted_close_reports_pending_and_recovers(self):
        self.change("create")
        replace = self.store._replace
        state_path = self.store.source_path
        def interrupted(path, raw):
            if path == state_path:
                raise OSError("simulated failure after history write")
            return replace(path, raw)
        with patch.object(self.store, "_replace", side_effect=interrupted):
            with self.assertRaises(OSError):
                self.change("close", reason="skipped")
        self.assert_code("state_recovery_required", self.store.current)
        self.assertTrue(self.store.recover())
        self.assertFalse(self.store.recover())
        self.assertEqual("closed", self.store.inspect("R024", self.order_path)["status"])
        self.assertEqual(2, len(runtime.events(self.order.read_bytes(), "R024")))

    def test_recovery_does_not_overwrite_external_edit(self):
        replace = self.store._replace
        def interrupted(path, raw):
            if path == self.store.source_path:
                raise OSError("interrupted")
            return replace(path, raw)
        with patch.object(self.store, "_replace", side_effect=interrupted):
            with self.assertRaises(OSError):
                self.change("create")
        self.order.write_text(self.order.read_text() + "\nExternal change\n")
        before = self.order.read_bytes()
        self.assert_code("state_recovery_conflict", self.store.recover)
        self.assertEqual(before, self.order.read_bytes())

    def test_lock_blocks_read_and_write_without_stealing_lock(self):
        lock = self.store.path(self.store.lock_path)
        lock.parent.mkdir(parents=True)
        lock.write_text("another writer")
        self.assert_code("state_busy", self.store.current)
        self.assert_code("state_busy", self.change, "create")
        self.assertEqual("another writer", lock.read_text())

    def test_malformed_state_and_duplicate_keys_are_not_fallbacks(self):
        self.change("create")
        path = self.store.path(self.store.source_path)
        path.write_text('{"schema_version": 1, "schema_version": 2}')
        self.assert_code("state_json_duplicate_key", self.store.current)
        path.write_text('{bad')
        self.assert_code("state_json_invalid", self.store.current)

    def test_symlink_and_path_traversal_are_rejected(self):
        self.assert_code("state_path_invalid", self.store.path, "../outside")
        self.assert_code("state_path_invalid", self.store.path, "/tmp/other")
        alias = self.root / "alias"
        alias.symlink_to(self.order.parent, target_is_directory=True)
        self.assert_code("state_path_unsafe", self.store.path, "alias/key-work-example.md")

    def test_identity_cannot_change_on_update(self):
        self.change("create")
        changed = dict(self.entry, order_path="00_docs/works/r024-example/other.md")
        self.assert_code("state_identity_change", self.change, "update", changed)

    def test_event_times_require_real_date_or_zoned_timestamp(self):
        for at in ("2026-02-30", "2026-10-12T12:00:00", None):
            with self.subTest(at=at):
                self.assert_code("state_event_time_invalid", self.store.change, "create", self.entry,
                                 expected_digest=None, at=at, note="created")

    def test_fenced_or_quoted_examples_are_not_history(self):
        example = '<!-- keystone-work-event {"not":"an event"} -->'
        self.order.write_text("# Work\n\n```markdown\n" + example + "\n```\n> " + example + "\n")
        self.change("create")
        self.assertEqual(1, len(runtime.events(self.order.read_bytes(), "R024")))

    def test_event_note_cannot_break_out_of_comment(self):
        self.store.change("create", self.entry, expected_digest=None, at="2026-10-12",
                          note="human note --> <script>")
        event = runtime.events(self.order.read_bytes(), "R024")[0]
        self.assertEqual("human note --> <script>", event["note"])

    def test_read_only_cli_and_error_envelope(self):
        args = [sys.executable, str(ROOT / "scripts/managed_work_state.py"), "--root", str(self.root)]
        p = subprocess.run(args + ["list"], capture_output=True, text=True)
        self.assertEqual(0, p.returncode)
        self.assertEqual([], json.loads(p.stdout)["result"]["items"])
        self.assertFalse((self.root / "00_docs/state").exists())
        self.change("create")
        self.store.path(self.store.source_path).write_text("bad")
        p = subprocess.run(args + ["list"], capture_output=True, text=True)
        self.assertEqual(1, p.returncode)
        self.assertEqual("state_json_invalid", json.loads(p.stdout)["diagnostics"][0]["code"])

    def test_current_projection_recovers_active_step_without_reading_history(self):
        self.change("create")
        work = dict(self.entry, ref="R024/build", kind="work", parent="R024", execution="in_progress")
        self.change("create", work)
        step = dict(work, ref="R024/S01", kind="step", parent=work["ref"])
        self.change("create", step)
        with patch.object(Path, "rglob", side_effect=AssertionError("No historical tree scan")):
            view = runtime.work_state_projection(self.store)
        self.assertEqual(6, view["state"]["schema_version"])
        self.assertEqual(["R024/S01"], view["state"]["active_steps"])
        self.assertEqual(["R024"], view["state"]["active_rounds"])
        self.assertEqual("open", view["state"]["round_hierarchy"][0]["management"])
        self.assertFalse(view["state"]["execution_ready"])
        self.assertEqual("not_evaluated", view["state"]["dependency_coverage"])
        self.assertEqual(1, view["generation"]["source_count"])

    def test_child_round_requires_managed_parent_and_blocks_parent_closure(self):
        child = dict(self.entry, ref="R024-A")
        self.assert_code("state_parent_missing", self.change, "create", child)
        self.change("create")
        self.change("create", child)
        view = runtime.work_state_projection(self.store)
        parent = view["state"]["round_hierarchy"][0]
        self.assertEqual("open", parent["management"])
        self.assertEqual("R024-A", parent["child_rounds"][0]["round_ref"])
        self.assertEqual(["R024", "R024-A"], view["state"]["open_rounds"])
        self.assert_code("state_children_managed", self.change, "close", reason="skipped")

    def test_package_local_managed_mode_is_standalone(self):
        self.change("create")
        for name in ("keystone-reader", "keystone-author", "keystone-coordinator"):
            with self.subTest(package=name):
                package = self.root / name
                package.mkdir()
                source = ROOT / "skills" / name / "scripts"
                for filename in ("work_state_runtime.py", "managed_work_state.py",
                                 "managed_work_integration.py", "work_dependency_policy.py"):
                    shutil.copyfile(source / filename, package / filename)
                p = subprocess.run([sys.executable, str(package / "work_state_runtime.py"),
                                    "--root", str(self.root), "--managed"],
                                   capture_output=True, text=True)
                self.assertEqual(0, p.returncode, p.stderr)
                self.assertEqual(["R024"], json.loads(p.stdout)["state"]["open_rounds"])

    def test_cli_write_requires_compare_and_swap_digest(self):
        entry_file = self.root / "entry.json"
        entry_file.write_bytes(runtime.encode(self.entry))
        command = [sys.executable, str(ROOT / "scripts/managed_work_state.py"),
                   "--root", str(self.root), "create", "--entry-json", str(entry_file),
                   "--expected-digest", "none", "--at", "2026-10-12", "--note", "Creation"]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, first.returncode, first.stderr)
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(1, second.returncode)
        self.assertEqual("state_stale", json.loads(second.stdout)["diagnostics"][0]["code"])

    def test_malformed_vocabulary_returns_diagnostic_not_type_error(self):
        self.assert_code("state_entry_invalid", self.store.change, "create", 4, expected_digest=None)
        for field in ("execution", "approval", "finalization"):
            self.assert_code("state_value_invalid", runtime.validate_entry,
                             dict(self.entry, **{field: []}))
        bad = '<!-- keystone-work-event {"ref":"R024","event":[],"note":"x"} -->'
        self.assert_code("state_event_invalid", runtime.events, bad.encode(), "R024")

    def test_missing_order_does_not_create_state_or_events(self):
        self.order.unlink()
        self.assert_code("state_order_missing", self.change, "create")
        self.assertEqual([], self.store.current()["items"])

    def test_recovery_rejects_escaping_pending_path(self):
        path = self.store.path(self.store.pending_path)
        path.parent.mkdir(parents=True)
        path.write_bytes(runtime.encode({"schema_version": 1, "changes": [
            {"path": "../outside", "before": None, "after": "eA=="}]}))
        self.assert_code("state_path_invalid", self.store.recover)

    def test_inspection_detects_wrong_order_and_closed_record_conflict(self):
        self.change("create")
        self.assert_code("state_order_mismatch", self.store.inspect, "R024", "other.md")
        before = self.store.read(self.store.source_path)
        self.change("close", reason="skipped")
        self.store._replace(self.store.source_path, before)
        self.assertEqual("conflict", self.store.inspect("R024", self.order_path)["status"])

    def test_legacy_round_files_are_reported_instead_of_silently_ignored(self):
        self.change("create")
        legacy = self.root / "00_docs/state/rounds"
        legacy.mkdir()
        (legacy / "R024.json").write_text("{}")
        self.assert_code("state_layout_legacy", self.store.current)
        self.assert_code("state_layout_legacy", self.change, "update")

    def test_unchanged_update_does_not_add_history(self):
        self.change("create")
        before = self.order.read_bytes(), self.token()
        self.change("update")
        self.assertEqual(before, (self.order.read_bytes(), self.token()))

    def test_update_recovery_keeps_log_and_group_move_together(self):
        self.change("create")
        self.entry["execution"] = "blocked"
        replace = self.store._replace
        def interrupted(path, raw):
            if path == self.store.source_path:
                raise OSError("interrupted update")
            return replace(path, raw)
        with patch.object(self.store, "_replace", side_effect=interrupted):
            with self.assertRaises(OSError):
                self.change("update")
        self.assert_code("state_recovery_required", self.store.current)
        self.store.recover()
        result = self.store.inspect("R024", self.order_path)
        self.assertEqual("managed", result["status"])
        self.assertEqual("blocked", result["entry"]["execution"])
        self.assertEqual(2, len(runtime.events(self.order.read_bytes(), "R024")))

    def test_groups_reject_closed_duplicate_refs_and_duplicate_execution(self):
        self.change("create")
        value = json.loads(self.store.read(self.store.source_path))
        row = value["states"]["planned"][0]
        self.assert_code("state_document_invalid", runtime.validate_document,
                         dict(value, states={"closed": [row]}))
        self.assert_code("state_duplicate_ref", runtime.validate_document,
                         dict(value, states={"planned": [row], "blocked": [row]}))
        self.assert_code("state_entry_invalid", runtime.validate_document,
                         dict(value, states={"planned": [dict(row, execution="planned")]}))

    def test_legacy_creation_without_snapshot_can_append_new_update(self):
        self.change("create")
        event = {"ref": "R024", "event": "created", "at": "2026-10-12", "note": "Legacy"}
        self.order.write_text("# Work\n" + runtime.EVENT_PREFIX + json.dumps(event) + " -->\n")
        self.entry["execution"] = "in_progress"
        self.change("update")
        history = runtime.events(self.order.read_bytes(), "R024")
        self.assertEqual(["created", "updated"], [item["event"] for item in history])
        self.assertEqual("managed", self.store.inspect("R024", self.order_path)["status"])

    def test_current_snapshot_conflict_cannot_be_hidden_by_next_update(self):
        self.change("create")
        value = runtime.group_entries([dict(self.entry, execution="blocked")])
        self.store.path(self.store.source_path).write_bytes(runtime.encode(value))
        self.assertEqual("conflict", self.store.inspect("R024", self.order_path)["status"])
        self.entry["execution"] = "complete"
        self.assert_code("state_event_conflict", self.change, "update")


if __name__ == "__main__":
    unittest.main()
