import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from closure_actual_state import capture_repository_snapshot_v3, digest_bytes  # noqa: E402

PACKAGE_ROOT = Path(__file__).parents[1]
RUNNER = PACKAGE_ROOT / "scripts" / "record_acceptance_event.py"


class RecordAcceptanceEventTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.base = Path(self.directory.name).resolve()
        self.root = self.base / "repo"
        self.evidence = self.base / "evidence"
        self.root.mkdir()
        self.evidence.mkdir()
        self.key = self.base / "main-acceptance.key"
        self.key.write_bytes(b"main-acceptance-authority-key-material")
        self.key.chmod(0o600)
        self.key_digest = digest_bytes(self.key.read_bytes())
        self.pre_snapshot = capture_repository_snapshot_v3(
            self.root,
            {
                "schema_version": 3,
                "include_paths": ["."],
                "exclusions": [],
                "entry_budget": 100,
            },
        )
        self.pre_snapshot_path = self.evidence / "pre-snapshot.json"
        self.pre_snapshot_path.write_text(
            json.dumps(
                self.pre_snapshot.wire(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.directory.cleanup()

    def arguments(self):
        return [
            "--root", str(self.root),
            "--evidence-root", str(self.evidence),
            "--acceptance-event-path", "acceptance.json",
            "--assignment-id", "R010-S02-acceptance-test",
            "--assignment-digest", "sha256:" + "1" * 64,
            "--context-digest", "sha256:" + "2" * 64,
            "--policy-digest", self.pre_snapshot.policy.digest,
            "--closure-target", "step",
            "--closure-step-ref", "R010/S02",
            "--pre-snapshot-path", "pre-snapshot.json",
            "--pre-snapshot-digest", self.pre_snapshot.snapshot_digest,
            "--parent-evidence-digest", "sha256:" + "5" * 64,
            "--acceptance-ref", "R010/S02/main-acceptance",
            "--accepted-step", "R010/S02",
            "--accepted-by", "main",
            "--acceptance-authority-key", str(self.key),
            "--trusted-acceptance-authority-key-sha256", self.key_digest,
        ]

    def run_event(self, arguments=None):
        return subprocess.run(
            [sys.executable, str(RUNNER), *(arguments or self.arguments())],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_runner_records_canonical_main_acceptance_event(self):
        process = self.run_event()
        payload = json.loads(process.stdout)

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual("pass", payload["status"])
        reference = payload["acceptance_event"]
        raw = (self.evidence / reference["path"]).read_bytes()
        event = json.loads(raw)
        self.assertEqual(
            json.dumps(
                event,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
            raw,
        )
        self.assertEqual("main", event["accepted_by"])
        self.assertEqual(["R010/S02"], event["accepted_steps"])
        self.assertEqual("sha256:" + "1" * 64, event["subject"]["assignment_digest"])
        self.assertEqual(
            "keystone-coordinator.record-acceptance-event",
            event["receipt"]["command_id"],
        )
        self.assertEqual(
            "sha256:" + "5" * 64,
            event["receipt"]["parent_evidence_digest"],
        )
        self.assertEqual(
            self.pre_snapshot.snapshot_digest,
            event["subject"]["observed_snapshot_digest"],
        )
        self.assertEqual(self.key_digest, event["receipt"]["authority_key_fingerprint"])
        self.assertRegex(event["receipt"]["mac"], r"^hmac-sha256:[0-9a-f]{64}$")
        self.assertEqual(digest_bytes(raw), reference["digest"])

    def test_runner_rejects_unpinned_main_key(self):
        arguments = self.arguments()
        arguments[-1] = "sha256:" + "0" * 64
        process = self.run_event(arguments)
        payload = json.loads(process.stdout)

        self.assertEqual(2, process.returncode)
        self.assertEqual("error", payload["status"])
        self.assertEqual(
            "acceptance_event_execution_failed",
            payload["diagnostics"][0]["code"],
        )

    def test_runner_does_not_overwrite_existing_event(self):
        first = self.run_event()
        second = self.run_event()

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(2, second.returncode)
        self.assertEqual(
            "acceptance_event_execution_failed",
            json.loads(second.stdout)["diagnostics"][0]["code"],
        )

    def test_step_event_requires_matching_step_ref(self):
        arguments = self.arguments()
        index = arguments.index("--closure-step-ref")
        del arguments[index:index + 2]
        process = self.run_event(arguments)

        self.assertEqual(2, process.returncode)
        self.assertEqual(
            "acceptance_event_execution_failed",
            json.loads(process.stdout)["diagnostics"][0]["code"],
        )

    def test_runner_rejects_repository_changed_after_pre_snapshot(self):
        (self.root / "finalization-before-acceptance.md").write_text(
            "already finalized\n",
            encoding="utf-8",
        )

        process = self.run_event()
        payload = json.loads(process.stdout)

        self.assertEqual(2, process.returncode)
        self.assertEqual("error", payload["status"])
        self.assertIn(
            "does not equal the pre-acceptance snapshot",
            payload["diagnostics"][0]["message"],
        )

    def test_runner_rejects_policy_digest_not_bound_to_pre_snapshot(self):
        arguments = self.arguments()
        index = arguments.index("--policy-digest")
        arguments[index + 1] = "sha256:" + "0" * 64

        process = self.run_event(arguments)
        payload = json.loads(process.stdout)

        self.assertEqual(2, process.returncode)
        self.assertEqual("error", payload["status"])
        self.assertIn(
            "policy digest does not match",
            payload["diagnostics"][0]["message"],
        )


if __name__ == "__main__":
    unittest.main()
