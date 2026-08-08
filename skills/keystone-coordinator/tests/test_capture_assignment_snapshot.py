import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from closure_actual_state import digest_bytes  # noqa: E402

PACKAGE_ROOT = Path(__file__).parents[1]
RUNNER = PACKAGE_ROOT / "scripts" / "capture_assignment_snapshot.py"


class CaptureAssignmentSnapshotTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.base = Path(self.directory.name).resolve()
        self.root = self.base / "repo"
        self.evidence = self.base / "evidence"
        self.root.mkdir()
        self.evidence.mkdir()
        (self.root / "src").mkdir()
        (self.root / "src" / "example.py").write_bytes(b"example\n")
        self.policy = self.base / "policy.json"
        self.policy.write_text(
            json.dumps({
                "schema_version": 3,
                "include_paths": ["."],
                "exclusions": [],
                "entry_budget": 100,
            }),
            encoding="utf-8",
        )
        self.capture_key = self.base / "capture-authority.key"
        self.capture_key.write_bytes(b"coordinator-capture-authority-key")
        self.capture_key.chmod(0o600)
        self.capture_key_digest = digest_bytes(self.capture_key.read_bytes())

    def tearDown(self):
        self.directory.cleanup()

    def run_capture(self, *extra):
        return subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--root",
                str(self.root),
                "--policy",
                str(self.policy),
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    @staticmethod
    def phase_binding_arguments():
        return (
            "--assignment-id",
            "R010-S02-capture-test",
            "--assignment-subject-digest",
            "sha256:" + "2" * 64,
            "--context-digest",
            "sha256:" + "1" * 64,
        )

    def phase_authority_arguments(self):
        return (
            "--parent-evidence-digest",
            "absent",
            "--capture-authority-key",
            str(self.capture_key),
            "--trusted-capture-authority-key-sha256",
            self.capture_key_digest,
        )

    def test_package_runner_captures_complete_typed_snapshot(self):
        process = self.run_capture("--expected-absence", "src/generated.py")
        payload = json.loads(process.stdout)

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["diagnostics"])
        snapshot = payload["snapshot"]
        self.assertTrue(snapshot["complete"])
        self.assertFalse(snapshot["truncated"])
        self.assertEqual(2, snapshot["discovered_path_count"])
        self.assertEqual(["src/generated.py"], snapshot["expected_absences"])
        self.assertEqual(
            ["directory", "regular_file"],
            [entry["path_type"] for entry in snapshot["entries"]],
        )

    def test_present_expected_absence_fails_closed(self):
        process = self.run_capture("--expected-absence", "src/example.py")
        payload = json.loads(process.stdout)

        self.assertEqual(1, process.returncode)
        self.assertEqual("fail", payload["status"])
        self.assertEqual("expected_absence_present", payload["diagnostics"][0]["code"])
        self.assertIsNone(payload["snapshot"])

    def test_duplicate_policy_key_is_an_execution_error(self):
        self.policy.write_text(
            '{"schema_version":999,"schema_version":3,"include_paths":["."],'
            '"exclusions":[],"entry_budget":100}',
            encoding="utf-8",
        )
        process = self.run_capture()
        payload = json.loads(process.stdout)

        self.assertEqual(2, process.returncode)
        self.assertEqual("error", payload["status"])
        self.assertEqual("snapshot_policy_unreadable", payload["diagnostics"][0]["code"])

    def test_package_runner_writes_canonical_assignment_phase_evidence(self):
        process = self.run_capture(
            "--phase-id",
            "assignment",
            "--parent-snapshot-digest",
            "absent",
            *self.phase_authority_arguments(),
            *self.phase_binding_arguments(),
            "--evidence-root",
            str(self.evidence),
            "--capture-evidence-path",
            "assignment.json",
        )
        payload = json.loads(process.stdout)

        self.assertEqual(0, process.returncode, process.stderr)
        reference = payload["capture_evidence"]
        evidence_path = self.evidence / reference["path"]
        raw = evidence_path.read_bytes()
        envelope = json.loads(raw)
        self.assertEqual(
            json.dumps(
                envelope,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
            raw,
        )
        self.assertEqual("assignment", envelope["phase_id"])
        self.assertEqual("absent", envelope["parent_snapshot_digest"])
        self.assertEqual(
            "R010-S02-capture-test", envelope["subject"]["assignment_id"]
        )
        self.assertEqual(
            "sha256:" + "2" * 64,
            envelope["subject"]["assignment_subject_digest"],
        )
        self.assertEqual(
            "sha256:" + "1" * 64, envelope["subject"]["context_digest"]
        )
        self.assertEqual(payload["snapshot"]["snapshot_digest"], envelope["snapshot_digest"])
        self.assertEqual(
            self.capture_key_digest,
            envelope["receipt"]["authority_key_fingerprint"],
        )
        self.assertEqual(
            "keystone-coordinator.capture-assignment-snapshot",
            envelope["receipt"]["command_id"],
        )
        self.assertEqual("absent", envelope["receipt"]["parent_evidence_digest"])
        self.assertRegex(envelope["receipt"]["mac"], r"^hmac-sha256:[0-9a-f]{64}$")
        self.assertEqual(digest_bytes(raw), reference["digest"])

    def test_phase_evidence_is_exclusive_and_cannot_be_overwritten(self):
        arguments = (
            "--phase-id",
            "assignment",
            "--parent-snapshot-digest",
            "absent",
            *self.phase_authority_arguments(),
            *self.phase_binding_arguments(),
            "--evidence-root",
            str(self.evidence),
            "--capture-evidence-path",
            "assignment.json",
        )
        first = self.run_capture(*arguments)
        second = self.run_capture(*arguments)

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(2, second.returncode)
        self.assertEqual(
            "phase_capture_execution_failed",
            json.loads(second.stdout)["diagnostics"][0]["code"],
        )

    def test_phase_capture_rejects_unpinned_authority_key(self):
        process = self.run_capture(
            "--phase-id",
            "assignment",
            "--parent-snapshot-digest",
            "absent",
            "--parent-evidence-digest",
            "absent",
            *self.phase_binding_arguments(),
            "--evidence-root",
            str(self.evidence),
            "--capture-evidence-path",
            "assignment.json",
            "--capture-authority-key",
            str(self.capture_key),
            "--trusted-capture-authority-key-sha256",
            "sha256:" + "0" * 64,
        )
        payload = json.loads(process.stdout)

        self.assertEqual(2, process.returncode)
        self.assertEqual("error", payload["status"])
        self.assertEqual(
            "phase_capture_execution_failed",
            payload["diagnostics"][0]["code"],
        )


if __name__ == "__main__":
    unittest.main()
