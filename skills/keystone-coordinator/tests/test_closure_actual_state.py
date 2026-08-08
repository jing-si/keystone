import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import closure_actual_state as actual_state  # noqa: E402
from closure_actual_state import (  # noqa: E402
    SnapshotCaptureError,
    capture_repository_snapshot_v3,
    changed_paths_v3,
    normalize_snapshot_policy_v3,
    parse_repository_snapshot_v3,
    repository_snapshot,
    snapshot_symlink_violations_v3,
    validate_expected_absences,
    validate_snapshot_wire_v3,
)


def policy(*, exclusions=(), entry_budget=100):
    return {
        "schema_version": 3,
        "include_paths": ["."],
        "exclusions": [
            {"path": path, "reason": reason}
            for path, reason in exclusions
        ],
        "entry_budget": entry_budget,
    }


class ClosureActualStateV3Test(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def capture(self, **kwargs):
        return capture_repository_snapshot_v3(self.root, policy(), **kwargs)

    @staticmethod
    def entries(snapshot):
        return {entry.path: entry for entry in snapshot.entries}

    def assert_error(self, code, callback):
        with self.assertRaises(SnapshotCaptureError) as raised:
            callback()
        self.assertEqual(code, raised.exception.code)

    def test_complete_snapshot_captures_dotfile_empty_directory_and_raw_bytes(self):
        (self.root / ".hidden").write_bytes(b"\xff\x00hidden")
        (self.root / "empty").mkdir()
        source = self.root / "src" / "run.sh"
        source.parent.mkdir()
        source.write_bytes(b"#!/bin/sh\n")
        source.chmod(0o755)

        snapshot = self.capture(expected_absences=("src/generated.py",))
        wire = snapshot.wire()
        entries = self.entries(snapshot)

        self.assertEqual(
            {".hidden", "empty", "src", "src/run.sh"},
            set(entries),
        )
        self.assertEqual("directory", entries["empty"].path_type)
        self.assertEqual("regular_file", entries[".hidden"].path_type)
        self.assertTrue(entries["src/run.sh"].executable)
        self.assertEqual(4, wire["discovered_path_count"])
        self.assertEqual(["src/generated.py"], wire["expected_absences"])
        self.assertEqual(1, wire["expected_absence_count"])
        self.assertTrue(wire["complete"])
        self.assertFalse(wire["truncated"])
        self.assertEqual(snapshot, parse_repository_snapshot_v3(wire))
        self.assertEqual(snapshot, validate_snapshot_wire_v3(wire))
        self.assertEqual(wire, self.capture(expected_absences=("src/generated.py",)).wire())

    def test_v3_policy_has_no_implicit_git_exclusion(self):
        metadata = self.root / ".git" / "HEAD"
        metadata.parent.mkdir()
        metadata.write_text("ref: refs/heads/main\n", encoding="utf-8")

        full = capture_repository_snapshot_v3(self.root, policy())
        excluded = capture_repository_snapshot_v3(
            self.root,
            policy(exclusions=((".git", "version-control internals"),)),
        )

        self.assertIn(".git/HEAD", self.entries(full))
        self.assertNotIn(".git", self.entries(excluded))
        self.assertNotIn(".git/HEAD", self.entries(excluded))
        self.assertNotEqual(full.policy.digest, excluded.policy.digest)

    def test_snapshot_wire_omission_and_structural_tampering_fail_integrity(self):
        (self.root / "a.txt").write_text("a\n", encoding="utf-8")
        (self.root / "b.txt").write_text("b\n", encoding="utf-8")
        wire = self.capture().wire()

        omitted = copy.deepcopy(wire)
        omitted["entries"].pop()
        self.assert_error(
            "snapshot_path_count_mismatch",
            lambda: parse_repository_snapshot_v3(omitted),
        )

        for field, value, code in (
            ("discovered_path_count", True, "snapshot_path_count_mismatch"),
            ("complete", False, "snapshot_incomplete"),
            ("truncated", True, "snapshot_incomplete"),
            (
                "path_set_digest",
                "sha256:" + "0" * 64,
                "snapshot_path_set_digest_mismatch",
            ),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(wire)
                changed[field] = value
                self.assert_error(
                    code,
                    lambda changed=changed: parse_repository_snapshot_v3(changed),
                )

        unknown = copy.deepcopy(wire)
        unknown["trusted"] = True
        self.assert_error(
            "snapshot_wire_invalid",
            lambda: parse_repository_snapshot_v3(unknown),
        )

        for field_path, code in (
            (("schema_version",), "snapshot_schema_invalid"),
            (("policy", "schema_version"), "snapshot_policy_schema_invalid"),
            (("policy", "entry_budget"), "snapshot_entry_budget_invalid"),
        ):
            with self.subTest(field_path=field_path):
                changed = copy.deepcopy(wire)
                target = changed
                for component in field_path[:-1]:
                    target = target[component]
                target[field_path[-1]] = True
                self.assert_error(
                    code,
                    lambda changed=changed: parse_repository_snapshot_v3(changed),
                )

        reordered = copy.deepcopy(wire)
        reordered["entries"] = list(reversed(reordered["entries"]))
        self.assert_error(
            "snapshot_entries_not_canonical",
            lambda: parse_repository_snapshot_v3(reordered),
        )

    def test_expected_absence_is_separate_and_checked_pre_and_post(self):
        (self.root / "src").mkdir()
        snapshot = self.capture(expected_absences=("src/output.py",))
        evidence = validate_expected_absences(
            self.root,
            snapshot.expected_absences,
            policy=snapshot.policy,
        )
        self.assertTrue(evidence.complete)
        self.assertEqual(1, evidence.count)

        (self.root / "src" / "output.py").write_text("created\n", encoding="utf-8")
        self.assert_error(
            "expected_absence_present",
            lambda: validate_expected_absences(
                self.root,
                snapshot.expected_absences,
                policy=snapshot.policy,
            ),
        )
        self.assert_error(
            "expected_absence_present",
            lambda: self.capture(expected_absences=("src/output.py",)),
        )

    def test_expected_absence_rejects_symlink_parent(self):
        outside = self.root.parent / (self.root.name + "-outside")
        outside.mkdir()
        try:
            (self.root / "escape").symlink_to(outside, target_is_directory=True)
            self.assert_error(
                "expected_absence_parent_symlink",
                lambda: self.capture(expected_absences=("escape/output.py",)),
            )
        finally:
            outside.rmdir()

    def test_type_replacement_cannot_hide_behind_equal_raw_byte_digest(self):
        subject = self.root / "subject"
        subject.write_bytes(b"target")
        before = self.capture()
        subject.unlink()
        subject.symlink_to("target")
        after = self.capture()

        before_entry = self.entries(before)["subject"]
        after_entry = self.entries(after)["subject"]
        self.assertEqual(before_entry.raw_byte_digest, after_entry.raw_byte_digest)
        self.assertNotEqual(before_entry.entry_digest, after_entry.entry_digest)
        self.assertEqual("type_replaced", changed_paths_v3(before, after)[0]["change_kind"])

    def test_executable_bit_and_symlink_target_are_digest_bearing(self):
        source = self.root / "tool"
        source.write_text("tool\n", encoding="utf-8")
        source.chmod(0o644)
        before_mode = self.capture()
        source.chmod(0o755)
        after_mode = self.capture()
        mode_delta = changed_paths_v3(before_mode, after_mode)
        self.assertEqual("modified", mode_delta[0]["change_kind"])
        self.assertEqual(
            self.entries(before_mode)["tool"].raw_byte_digest,
            self.entries(after_mode)["tool"].raw_byte_digest,
        )

        link = self.root / "link"
        link.symlink_to("one")
        before_target = self.capture()
        link.unlink()
        link.symlink_to("two")
        after_target = self.capture()
        target_delta = [
            item for item in changed_paths_v3(before_target, after_target)
            if item["path"] == "link"
        ]
        self.assertEqual("modified", target_delta[0]["change_kind"])
        self.assertNotEqual(
            self.entries(before_target)["link"].symlink_target_b64,
            self.entries(after_target)["link"].symlink_target_b64,
        )

    def test_recorded_symlink_direct_parent_escape_is_reported(self):
        (self.root / "escape").symlink_to("../outside")
        self.assertEqual(
            [{"path": "escape", "reason": "escapes_root"}],
            snapshot_symlink_violations_v3(self.capture()),
        )

    def test_recorded_symlink_absolute_escape_is_reported(self):
        (self.root / "escape").symlink_to("/outside")
        self.assertEqual(
            [{"path": "escape", "reason": "absolute_target"}],
            snapshot_symlink_violations_v3(self.capture()),
        )

    def test_recorded_symlink_in_root_target_is_allowed(self):
        (self.root / "target").write_text("target\n", encoding="utf-8")
        (self.root / "link").symlink_to("target")
        self.assertEqual([], snapshot_symlink_violations_v3(self.capture()))

    def test_recorded_symlink_target_under_exclusion_is_reported(self):
        (self.root / "secret").mkdir()
        (self.root / "src").mkdir()
        (self.root / "src" / "link").symlink_to("../secret")
        snapshot = capture_repository_snapshot_v3(
            self.root,
            policy(exclusions=(("secret", "outside assignment authority"),)),
        )
        self.assertEqual(
            [{"path": "src/link", "reason": "target_excluded"}],
            snapshot_symlink_violations_v3(snapshot),
        )

    def test_recorded_symlink_target_outside_include_policy_is_reported(self):
        (self.root / "secret").mkdir()
        (self.root / "src").mkdir()
        (self.root / "src" / "link").symlink_to("../secret")
        snapshot = capture_repository_snapshot_v3(
            self.root,
            {
                "schema_version": 3,
                "include_paths": ["src"],
                "exclusions": [],
                "entry_budget": 100,
            },
        )
        self.assertEqual(
            [{"path": "src/link", "reason": "target_outside_policy"}],
            snapshot_symlink_violations_v3(snapshot),
        )

    def test_recorded_symlink_chained_escape_is_reported_for_each_origin(self):
        (self.root / "inner").symlink_to("../outside")
        (self.root / "outer").symlink_to("inner")
        self.assertEqual(
            [
                {"path": "inner", "reason": "escapes_root"},
                {"path": "outer", "reason": "escapes_root"},
            ],
            snapshot_symlink_violations_v3(self.capture()),
        )

    def test_recorded_symlink_cycle_is_reported_for_each_origin(self):
        (self.root / "a").symlink_to("b")
        (self.root / "b").symlink_to("a")
        self.assertEqual(
            [
                {"path": "a", "reason": "target_cycle"},
                {"path": "b", "reason": "target_cycle"},
            ],
            snapshot_symlink_violations_v3(self.capture()),
        )

    def test_recorded_symlink_invalid_target_is_reported(self):
        (self.root / "invalid").symlink_to("bad\\target")
        self.assertEqual(
            [{"path": "invalid", "reason": "invalid_target"}],
            snapshot_symlink_violations_v3(self.capture()),
        )

    def test_unicode_casefold_collision_is_host_independent(self):
        conflicting = {
            "schema_version": 3,
            "include_paths": ["STRASSE", "Straße"],
            "exclusions": [],
            "entry_budget": 10,
        }
        self.assert_error(
            "snapshot_path_casefold_collision",
            lambda: normalize_snapshot_policy_v3(conflicting),
        )

        (self.root / "alpha").write_text("a", encoding="utf-8")
        (self.root / "beta").write_text("b", encoding="utf-8")
        with mock.patch.object(actual_state, "_casefold_key", return_value="collision"):
            self.assert_error(
                "snapshot_path_casefold_collision",
                lambda: self.capture(),
            )

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO is unavailable on this host")
    def test_unsupported_filesystem_type_fails_before_byte_read(self):
        os.mkfifo(self.root / "pipe")
        self.assert_error(
            "snapshot_path_type_unsupported",
            lambda: self.capture(),
        )

    def test_path_set_drift_retries_then_passes_or_fails_closed(self):
        (self.root / "value.txt").write_text("stable\n", encoding="utf-8")
        original = actual_state._discover_paths_v3
        calls = {"count": 0}

        def transient(root, snapshot_policy):
            calls["count"] += 1
            result = original(root, snapshot_policy)
            if calls["count"] == 2:
                return result + ("phantom",)
            return result

        with mock.patch.object(actual_state, "_discover_paths_v3", side_effect=transient):
            snapshot = capture_repository_snapshot_v3(
                self.root, policy(), max_attempts=2
            )
        self.assertEqual(5, calls["count"])
        self.assertIn("value.txt", self.entries(snapshot))

        calls["count"] = 0

        def persistent(root, snapshot_policy):
            calls["count"] += 1
            result = original(root, snapshot_policy)
            return result + (("phantom",) if calls["count"] % 2 == 0 else ())

        with mock.patch.object(actual_state, "_discover_paths_v3", side_effect=persistent):
            self.assert_error(
                "snapshot_generation_unstable",
                lambda: capture_repository_snapshot_v3(
                    self.root, policy(), max_attempts=2
                ),
            )

    def test_identity_drift_uses_the_same_bounded_retry(self):
        (self.root / "value.txt").write_text("stable\n", encoding="utf-8")
        original = actual_state._capture_entry_v3
        calls = {"count": 0}

        def transient(root_fd, relative):
            calls["count"] += 1
            if calls["count"] == 1:
                raise actual_state._SnapshotDrift("identity drift", relative)
            return original(root_fd, relative)

        with mock.patch.object(actual_state, "_capture_entry_v3", side_effect=transient):
            snapshot = capture_repository_snapshot_v3(
                self.root, policy(), max_attempts=2
            )
        self.assertIn("value.txt", self.entries(snapshot))

    def test_global_entry_drift_between_path_captures_retries(self):
        first = self.root / "a.txt"
        last = self.root / "z.txt"
        first.write_text("before\n", encoding="utf-8")
        last.write_text("stable\n", encoding="utf-8")
        original = actual_state._capture_entry_v3
        mutated = {"done": False}

        def mutate_earlier_entry(root_fd, relative):
            entry = original(root_fd, relative)
            if relative == "z.txt" and not mutated["done"]:
                first.write_text("after\n", encoding="utf-8")
                mutated["done"] = True
            return entry

        with mock.patch.object(
            actual_state,
            "_capture_entry_v3",
            side_effect=mutate_earlier_entry,
        ):
            snapshot = capture_repository_snapshot_v3(
                self.root, policy(), max_attempts=2
            )

        self.assertEqual(
            actual_state.digest_bytes(first.read_bytes()),
            self.entries(snapshot)["a.txt"].raw_byte_digest,
        )

    def test_snapshot_wire_rejects_entries_outside_or_under_exclusion(self):
        source = self.root / "src" / "inside.txt"
        source.parent.mkdir()
        source.write_text("inside\n", encoding="utf-8")
        snapshot = capture_repository_snapshot_v3(
            self.root,
            {
                "schema_version": 3,
                "include_paths": ["src"],
                "exclusions": [],
                "entry_budget": 100,
            },
        )
        wire = snapshot.wire()
        forged = copy.deepcopy(wire)
        forged["entries"][0]["path"] = "secret"
        forged["entries"][0]["entry_digest"] = actual_state._digest_canonical({
            key: forged["entries"][0][key]
            for key in (
                "path", "path_type", "raw_byte_digest", "executable",
                "symlink_target_b64",
            )
        })
        forged["path_set_digest"] = actual_state._digest_canonical(["secret"])
        payload = {
            key: value for key, value in forged.items() if key != "snapshot_digest"
        }
        forged["snapshot_digest"] = actual_state._digest_canonical(payload)
        self.assert_error(
            "snapshot_entry_out_of_policy",
            lambda: parse_repository_snapshot_v3(forged),
        )

        excluded_policy = policy(exclusions=(("secret", "not assigned"),))
        excluded = copy.deepcopy(forged)
        excluded["policy"] = excluded_policy
        excluded["policy_digest"] = actual_state._digest_canonical(excluded_policy)
        payload = {
            key: value for key, value in excluded.items() if key != "snapshot_digest"
        }
        excluded["snapshot_digest"] = actual_state._digest_canonical(payload)
        self.assert_error(
            "snapshot_entry_excluded",
            lambda: parse_repository_snapshot_v3(excluded),
        )

    def test_budget_overflow_and_noncanonical_policy_fail_closed(self):
        (self.root / "one").write_text("1", encoding="utf-8")
        (self.root / "two").write_text("2", encoding="utf-8")
        self.assert_error(
            "snapshot_entry_budget_exceeded",
            lambda: capture_repository_snapshot_v3(
                self.root, policy(entry_budget=1)
            ),
        )
        bad_budget = policy()
        bad_budget["entry_budget"] = True
        self.assert_error(
            "snapshot_entry_budget_invalid",
            lambda: normalize_snapshot_policy_v3(bad_budget),
        )

    def test_missing_root_has_stable_capture_error(self):
        self.assert_error(
            "snapshot_root_unreadable",
            lambda: capture_repository_snapshot_v3(
                self.root / "missing",
                policy(),
            ),
        )

    def test_legacy_repository_snapshot_shape_is_preserved(self):
        (self.root / "empty").mkdir()
        (self.root / "value.txt").write_text("value\n", encoding="utf-8")
        legacy = repository_snapshot(self.root)
        self.assertIsInstance(legacy, dict)
        self.assertEqual(["value.txt"], sorted(legacy))
        self.assertIsInstance(legacy["value.txt"], str)


if __name__ == "__main__":
    unittest.main()
