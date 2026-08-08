import copy
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_RUNTIME = REPOSITORY_ROOT / "scripts" / "owned_surface_apply_runtime.py"
GENERATOR = REPOSITORY_ROOT / "scripts" / "generate_owned_surface_apply_runtimes.py"
AUTHOR_RUNTIME = (
    REPOSITORY_ROOT
    / "skills"
    / "keystone-author"
    / "scripts"
    / "owned_surface_apply_runtime.py"
)
COORDINATOR_RUNTIME = (
    REPOSITORY_ROOT
    / "skills"
    / "keystone-coordinator"
    / "scripts"
    / "owned_surface_apply_runtime.py"
)
AUTHOR_RUNNER = (
    REPOSITORY_ROOT
    / "skills"
    / "keystone-author"
    / "scripts"
    / "run_owned_surface_apply.py"
)
COORDINATOR_RUNNER = (
    REPOSITORY_ROOT
    / "skills"
    / "keystone-coordinator"
    / "scripts"
    / "run_owned_surface_apply.py"
)


def load_runtime(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = load_runtime(CANONICAL_RUNTIME, "owned_surface_apply_runtime_test")


class OwnedSurfaceApplyFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve(strict=True)
        self.root = self.base / "repository"
        self.evidence_root = self.base / "evidence"
        self.root.mkdir()
        self.evidence_root.mkdir()
        self.request_root = self.evidence_root / "requests"
        self.request_root.mkdir()
        self.key = self.base / "authority.key"
        self.key_bytes = b"owner-apply-test-key-material-32-bytes-minimum"
        self.key.write_bytes(self.key_bytes)
        self.key.chmod(0o600)
        self.key_digest = runtime.digest_bytes(self.key_bytes)
        self.request_counter = 0

    def tearDown(self):
        self.temporary.cleanup()

    def build_request(
        self,
        *,
        owner="author",
        surface="document_metadata",
        target_path="00_docs/work.md",
        before=b"before\n",
        after="after\n",
        patch_format="full_replacement",
        patch_body=None,
        required=True,
        allowed=None,
        excluded=None,
    ):
        target = self.root / target_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if before is None:
            if target.exists() or target.is_symlink():
                target.unlink()
            baseline_digest = "absent"
            baseline_content = None
        else:
            target.write_bytes(before)
            baseline_digest = runtime.digest_bytes(before)
            baseline_content = before.decode("utf-8")
        body = after if patch_body is None else patch_body
        expected = runtime.replay_patch(
            b"" if before is None else before,
            patch_format,
            body,
        )
        scope = {
            "allowed": sorted(["."] if allowed is None else allowed),
            "excluded": sorted([] if excluded is None else excluded),
        }
        request = {
            "schema_version": 1,
            "transaction_id": "transaction-1",
            "transaction_digest": runtime.digest_json({"transaction": 1}),
            "assignment_id": "assignment-1",
            "assignment_digest": runtime.digest_json({"assignment": 1}),
            "phase_id": "worker",
            "phase_baseline_snapshot_digest": runtime.digest_json(
                {"phase": "worker", "snapshot": "baseline"}
            ),
            "phase_parent_evidence_digest": runtime.digest_json(
                {"phase": "assignment", "evidence": "capture"}
            ),
            "repository_root_digest": runtime.digest_json(
                {"repository_root": str(self.root.resolve(strict=True))}
            ),
            "owner": owner,
            "scope": scope,
            "scope_digest": runtime.digest_json(scope),
            "prior_receipt_digest": "absent",
            "patch": {
                "patch_id": "patch-1",
                "owner": owner,
                "surface": surface,
                "target_path": target_path,
                "baseline_digest": baseline_digest,
                "baseline_content": baseline_content,
                "exact_patch": body,
                "patch_format": patch_format,
                "patch_body": body,
                "expected_after_digest": runtime.digest_bytes(expected),
                "required": required,
            },
        }
        return request, target, expected

    def write_request(self, request):
        self.request_counter += 1
        path = self.request_root / ("request-%d.json" % self.request_counter)
        path.write_bytes(runtime.canonical_json_bytes(request))
        return path

    def output_path(self):
        self.request_counter += 1
        return self.evidence_root / ("receipt-%d.json" % self.request_counter)

    def apply(
        self,
        request,
        *,
        allowed_owners=frozenset({"author"}),
        key=None,
        pinned_digest=None,
        output=None,
        runner_path=CANONICAL_RUNTIME,
    ):
        request_path = self.write_request(request)
        output_path = self.output_path() if output is None else output
        result = runtime.apply_owned_surface_patch(
            root=self.root,
            request_path=request_path,
            evidence_root=self.evidence_root,
            output_path=output_path,
            authority_key=self.key if key is None else key,
            pinned_key_sha256=(
                self.key_digest if pinned_digest is None else pinned_digest
            ),
            allowed_owners=allowed_owners,
            runner_path=runner_path,
        )
        return result, output_path

    def run_entrypoint(self, runner, request, output):
        request_path = self.write_request(request)
        return subprocess.run(
            [
                sys.executable,
                "-I",
                str(runner),
                "--root",
                str(self.root),
                "--request",
                str(request_path),
                "--evidence-root",
                str(self.evidence_root),
                "--output",
                str(output),
                "--authority-key",
                str(self.key),
                "--pinned-key-sha256",
                self.key_digest,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_error(self, code, request, **kwargs):
        with self.assertRaises(runtime.ApplyError) as raised:
            self.apply(request, **kwargs)
        self.assertEqual(code, raised.exception.code)
        return raised.exception


class ValidApplyTests(OwnedSurfaceApplyFixture):
    def test_author_entrypoint_applies_one_document_patch_and_writes_receipt(self):
        request, target, expected = self.build_request()
        output = self.evidence_root / "author-receipt.json"

        completed = self.run_entrypoint(AUTHOR_RUNNER, request, output)

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        stdout = json.loads(completed.stdout)
        self.assertEqual(
            {"schema_version", "status", "diagnostics", "summary"},
            set(stdout),
        )
        self.assertEqual("pass", stdout["status"])
        self.assertEqual(expected, target.read_bytes())
        envelope = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual("applied", envelope["status"])
        self.assertEqual(
            {"schema_version", "producer", "status", "subject", "receipt"},
            set(envelope),
        )
        self.assertEqual(
            {
                "transaction_id",
                "transaction_digest",
                "assignment_id",
                "assignment_digest",
                "phase_id",
                "phase_baseline_snapshot_digest",
                "phase_parent_evidence_digest",
                "repository_root_digest",
                "owner",
                "scope_digest",
            },
            set(envelope["subject"]),
        )
        self.assertEqual(
            {
                "schema_version",
                "trust_model",
                "command_id",
                "runner_executable_digest",
                "runtime_digest",
                "evidence_root_digest",
                "request_digest",
                "prior_receipt_digest",
                "nonce",
                "authority_key_fingerprint",
                "patch_receipt",
                "mac",
            },
            set(envelope["receipt"]),
        )
        self.assertEqual(request["patch"], envelope["receipt"]["patch_receipt"]["patch"])
        self.assertEqual(
            runtime.digest_bytes(AUTHOR_RUNNER.read_bytes()),
            envelope["receipt"]["runner_executable_digest"],
        )
        self.assertEqual(
            runtime.digest_bytes(AUTHOR_RUNTIME.read_bytes()),
            envelope["receipt"]["runtime_digest"],
        )

    def test_coordinator_entrypoint_applies_one_code_patch(self):
        request, target, expected = self.build_request(
            owner="coordinator",
            surface="code_anchor",
            target_path="src/feature.py",
            before=b"value = 1\n",
            after="value = 2\n",
        )
        output = self.evidence_root / "coordinator-receipt.json"

        completed = self.run_entrypoint(COORDINATOR_RUNNER, request, output)

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertEqual("pass", json.loads(completed.stdout)["status"])
        self.assertEqual(expected, target.read_bytes())
        envelope = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual("coordinator", envelope["subject"]["owner"])
        self.assertEqual(
            runtime.digest_bytes(COORDINATOR_RUNTIME.read_bytes()),
            envelope["receipt"]["runtime_digest"],
        )

    def test_optional_patch_uses_same_confirmed_request_without_runner_decision(self):
        request, target, expected = self.build_request(
            owner="main",
            surface="test_anchor",
            target_path="tests/test_feature.py",
            required=False,
        )

        envelope, _ = self.apply(
            request,
            allowed_owners=frozenset({"main", "coordinator"}),
        )

        self.assertFalse(envelope["receipt"]["patch_receipt"]["patch"]["required"])
        self.assertEqual(expected, target.read_bytes())
        self.assertEqual([], list(target.parent.glob(".keystone-owned-apply-*.tmp")))

    def test_absent_target_and_unified_diff_apply_canonical_patch_bytes(self):
        request, target, expected = self.build_request(
            target_path="00_docs/new.md",
            before=None,
            after="new\n",
        )
        envelope, _ = self.apply(request)
        self.assertEqual(expected, target.read_bytes())
        self.assertEqual(
            request["patch"]["expected_after_digest"],
            envelope["receipt"]["patch_receipt"]["resulting_digest"],
        )

        request, target, expected = self.build_request(
            target_path="00_docs/diff.md",
            before=b"before\nold\n",
            after="unused",
            patch_format="unified_diff",
            patch_body="@@ -1,2 +1,2 @@\n before\n-old\n+new\n",
        )
        self.apply(request)
        self.assertEqual(expected, target.read_bytes())

    def test_absent_publish_never_overwrites_a_racing_writer(self):
        request, target, _ = self.build_request(
            target_path="00_docs/raced.md",
            before=None,
            after="runner\n",
        )
        output = self.evidence_root / "raced.json"
        original_link = os.link

        def publish_racing_target(*args, **kwargs):
            target.write_bytes(b"concurrent writer\n")
            return original_link(*args, **kwargs)

        with mock.patch.object(runtime.os, "link", side_effect=publish_racing_target):
            self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"concurrent writer\n", target.read_bytes())
        self.assertFalse(output.exists())

    def test_existing_publish_atomically_rejects_a_last_moment_byte_write(self):
        request, target, _ = self.build_request()
        output = self.evidence_root / "existing-byte-race.json"
        original_exchange = runtime._atomic_exchange
        raced = False

        def exchange_after_write(directory_fd, first, second):
            nonlocal raced
            if not raced:
                raced = True
                target.write_bytes(b"concurrent writer\n")
            return original_exchange(directory_fd, first, second)

        with mock.patch.object(
            runtime,
            "_atomic_exchange",
            side_effect=exchange_after_write,
        ):
            self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"concurrent writer\n", target.read_bytes())
        self.assertFalse(output.exists())

    def test_existing_publish_atomically_rejects_a_last_moment_replacement(self):
        request, target, _ = self.build_request()
        output = self.evidence_root / "existing-replacement-race.json"
        replacement = target.with_name("replacement.md")
        original_exchange = runtime._atomic_exchange
        raced = False

        def exchange_after_replace(directory_fd, first, second):
            nonlocal raced
            if not raced:
                raced = True
                replacement.write_bytes(b"concurrent replacement\n")
                os.replace(replacement, target)
            return original_exchange(directory_fd, first, second)

        with mock.patch.object(
            runtime,
            "_atomic_exchange",
            side_effect=exchange_after_replace,
        ):
            self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"concurrent replacement\n", target.read_bytes())
        self.assertFalse(output.exists())

    def test_existing_publish_rejects_same_bytes_with_changed_identity_state(self):
        request, target, _ = self.build_request()
        output = self.evidence_root / "existing-same-bytes-race.json"
        original_exchange = runtime._atomic_exchange
        raced = False

        def exchange_after_same_byte_write(directory_fd, first, second):
            nonlocal raced
            if not raced:
                raced = True
                target.write_bytes(b"before\n")
                target.chmod(0o640)
            return original_exchange(directory_fd, first, second)

        with mock.patch.object(
            runtime,
            "_atomic_exchange",
            side_effect=exchange_after_same_byte_write,
        ):
            self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"before\n", target.read_bytes())
        self.assertEqual(0o640, stat.S_IMODE(target.stat().st_mode))
        self.assertFalse(output.exists())

    def test_existing_publish_fails_closed_without_atomic_exchange(self):
        request, target, _ = self.build_request()
        output = self.evidence_root / "exchange-unavailable.json"
        unavailable = runtime.ApplySecurityError(
            "atomic_exchange_unavailable",
            "simulated unsupported filesystem",
            request["patch"]["target_path"],
        )

        with mock.patch.object(
            runtime,
            "_atomic_exchange",
            side_effect=unavailable,
        ):
            self.assert_error(
                "atomic_exchange_unavailable",
                request,
                output=output,
            )

        self.assertEqual(b"before\n", target.read_bytes())
        self.assertFalse(output.exists())
        self.assertEqual([], list(target.parent.glob(".keystone-owned-apply-*.tmp")))


class ValidationFailureTests(OwnedSurfaceApplyFixture):
    def test_stale_baseline_does_not_write_target_or_receipt(self):
        request, target, _ = self.build_request()
        target.write_bytes(b"changed after planning\n")
        output = self.evidence_root / "stale.json"

        self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"changed after planning\n", target.read_bytes())
        self.assertFalse(output.exists())

    def test_target_must_be_in_allowed_scope_and_outside_excluded_scope(self):
        request, target, _ = self.build_request(allowed=["different"])
        self.assert_error("target_scope_invalid", request)
        self.assertEqual(b"before\n", target.read_bytes())

        request, target, _ = self.build_request(
            allowed=["00_docs"], excluded=["00_docs/work.md"]
        )
        self.assert_error("target_excluded", request)
        self.assertEqual(b"before\n", target.read_bytes())

        request, target, _ = self.build_request(
            allowed=["SRC", "src"], excluded=[]
        )
        self.assert_error("scope_invalid", request)
        self.assertEqual(b"before\n", target.read_bytes())

        request, target, _ = self.build_request(
            allowed=["00_docs"], excluded=["00_DOCS"]
        )
        self.assert_error("scope_invalid", request)
        self.assertEqual(b"before\n", target.read_bytes())

    def test_owner_lane_and_surface_policy_are_both_enforced(self):
        request, target, _ = self.build_request(owner="coordinator")
        self.assert_error("owner_lane_invalid", request)
        self.assertEqual(b"before\n", target.read_bytes())

        request, target, _ = self.build_request(
            owner="author",
            surface="code_anchor",
            target_path="src/wrong.py",
        )
        self.assert_error("owner_surface_invalid", request)
        self.assertEqual(b"before\n", target.read_bytes())

    def test_replay_mismatch_and_caller_result_fields_are_rejected(self):
        request, target, _ = self.build_request()
        request["patch"]["expected_after_digest"] = runtime.digest_bytes(b"other")
        self.assert_error("patch_replay_mismatch", request)
        self.assertEqual(b"before\n", target.read_bytes())

        request, target, _ = self.build_request()
        request["patch"]["resulting_digest"] = request["patch"]["expected_after_digest"]
        self.assert_error("request_schema_invalid", request)
        self.assertEqual(b"before\n", target.read_bytes())

        for non_integer_version in (True, 1.0):
            request, target, _ = self.build_request()
            request["schema_version"] = non_integer_version
            self.assert_error("request_schema_invalid", request)
            self.assertEqual(b"before\n", target.read_bytes())

    def test_request_bytes_root_scope_and_baseline_are_cryptographically_bound(self):
        request, target, _ = self.build_request()
        request_path = self.write_request(request)
        request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
        output = self.output_path()
        with self.assertRaises(runtime.ApplyError) as raised:
            runtime.apply_owned_surface_patch(
                root=self.root,
                request_path=request_path,
                evidence_root=self.evidence_root,
                output_path=output,
                authority_key=self.key,
                pinned_key_sha256=self.key_digest,
                allowed_owners=frozenset({"author"}),
                runner_path=CANONICAL_RUNTIME,
            )
        self.assertEqual("request_not_canonical", raised.exception.code)

        request, _, _ = self.build_request()
        request["repository_root_digest"] = runtime.digest_json({"repository_root": "other"})
        self.assert_error("repository_root_digest_mismatch", request)

        request, _, _ = self.build_request()
        request["scope_digest"] = runtime.digest_json({"allowed": ["other"], "excluded": []})
        self.assert_error("scope_digest_mismatch", request)

        request, _, _ = self.build_request()
        request["patch"]["baseline_content"] = "substituted\n"
        self.assert_error("patch_baseline_mismatch", request)
        self.assertEqual(b"before\n", target.read_bytes())

    def test_unpaired_unicode_surrogate_returns_a_canonical_diagnostic(self):
        request, target, _ = self.build_request()
        request_path = self.write_request(request)
        raw = request_path.read_bytes().replace(
            b'"transaction_id":"transaction-1"',
            b'"transaction_id":"\\ud800"',
        )
        request_path.write_bytes(raw)
        output = self.output_path()

        completed = subprocess.run(
            [
                sys.executable,
                str(AUTHOR_RUNNER),
                "--root",
                str(self.root),
                "--request",
                str(request_path),
                "--evidence-root",
                str(self.evidence_root),
                "--output",
                str(output),
                "--authority-key",
                str(self.key),
                "--pinned-key-sha256",
                self.key_digest,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, completed.returncode)
        self.assertEqual("", completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("fail", payload["status"])
        self.assertEqual("request_json_invalid", payload["diagnostics"][0]["code"])
        self.assertEqual(b"before\n", target.read_bytes())
        self.assertFalse(output.exists())

    def test_deeply_nested_json_returns_a_canonical_diagnostic(self):
        request, target, _ = self.build_request()
        request_path = self.write_request(request)
        request_path.write_bytes(b"[" * 1100 + b"0" + b"]" * 1100)
        output = self.output_path()

        completed = subprocess.run(
            [
                sys.executable,
                str(AUTHOR_RUNNER),
                "--root",
                str(self.root),
                "--request",
                str(request_path),
                "--evidence-root",
                str(self.evidence_root),
                "--output",
                str(output),
                "--authority-key",
                str(self.key),
                "--pinned-key-sha256",
                self.key_digest,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, completed.returncode)
        self.assertEqual("", completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("fail", payload["status"])
        self.assertEqual("request_json_invalid", payload["diagnostics"][0]["code"])
        self.assertEqual(b"before\n", target.read_bytes())
        self.assertFalse(output.exists())

    def test_existing_output_is_never_overwritten_and_target_is_unchanged(self):
        request, target, _ = self.build_request()
        output = self.evidence_root / "existing.json"
        output.write_bytes(b"sentinel")

        self.assert_error("output_exists", request, output=output)

        self.assertEqual(b"sentinel", output.read_bytes())
        self.assertEqual(b"before\n", target.read_bytes())

    def test_failure_after_output_reservation_rolls_back_and_unlinks_marker(self):
        request, target, _ = self.build_request()
        output = self.evidence_root / "write-failure.json"

        with mock.patch.object(
            runtime,
            "_write_receipt_to_reserved_output",
            side_effect=OSError("simulated receipt write failure"),
        ):
            self.assert_error("apply_io_failed", request, output=output)

        self.assertEqual(b"before\n", target.read_bytes())
        self.assertFalse(output.exists())
        self.assertEqual([], list(target.parent.glob(".keystone-owned-apply-*.tmp")))

    def test_changed_baseline_backup_is_never_restored_or_deleted(self):
        request, target, expected = self.build_request()
        output = self.evidence_root / "changed-backup.json"
        tampered = b"tampered hidden backup\n"

        def tamper_backup_then_fail(*_args, **_kwargs):
            backups = list(target.parent.glob(".keystone-owned-apply-*.tmp"))
            self.assertEqual(1, len(backups))
            backups[0].write_bytes(tampered)
            raise OSError("simulated receipt write failure")

        with mock.patch.object(
            runtime,
            "_write_receipt_to_reserved_output",
            side_effect=tamper_backup_then_fail,
        ):
            self.assert_error("rollback_failed", request, output=output)

        self.assertEqual(expected, target.read_bytes())
        self.assertFalse(output.exists())
        recovery = list(target.parent.glob(".keystone-owned-apply-*.tmp"))
        self.assertEqual(1, len(recovery))
        self.assertEqual(tampered, recovery[0].read_bytes())

    def test_symlinked_baseline_backup_is_preserved_off_the_live_target(self):
        request, target, expected = self.build_request()
        output = self.evidence_root / "symlinked-backup.json"
        external = self.base / "concurrent-backup.txt"
        external.write_bytes(b"concurrent backup bytes\n")

        def replace_backup_with_symlink_then_fail(*_args, **_kwargs):
            backups = list(target.parent.glob(".keystone-owned-apply-*.tmp"))
            self.assertEqual(1, len(backups))
            backups[0].unlink()
            backups[0].symlink_to(external)
            raise OSError("simulated receipt write failure")

        with mock.patch.object(
            runtime,
            "_write_receipt_to_reserved_output",
            side_effect=replace_backup_with_symlink_then_fail,
        ):
            self.assert_error("rollback_failed", request, output=output)

        self.assertEqual(expected, target.read_bytes())
        self.assertFalse(target.is_symlink())
        self.assertEqual(b"concurrent backup bytes\n", external.read_bytes())
        recovery = list(target.parent.glob(".keystone-owned-apply-*.tmp"))
        self.assertEqual(1, len(recovery))
        self.assertTrue(recovery[0].is_symlink())
        self.assertFalse(output.exists())

    def test_absent_rollback_quarantines_then_restores_a_concurrent_writer(self):
        request, target, _ = self.build_request(
            target_path="00_docs/absent-rollback.md",
            before=None,
            after="runner\n",
        )
        output = self.evidence_root / "absent-rollback.json"
        original_move = runtime._move_to_private_quarantine
        raced = False

        def replace_before_quarantine(directory_fd, source, label):
            nonlocal raced
            if label == "absent-rollback" and not raced:
                raced = True
                target.write_bytes(b"concurrent writer bytes\n")
            return original_move(directory_fd, source, label)

        with mock.patch.object(
            runtime,
            "_write_receipt_to_reserved_output",
            side_effect=OSError("simulated receipt write failure"),
        ), mock.patch.object(
            runtime,
            "_move_to_private_quarantine",
            side_effect=replace_before_quarantine,
        ):
            self.assert_error("rollback_failed", request, output=output)

        self.assertEqual(b"concurrent writer bytes\n", target.read_bytes())
        self.assertFalse(output.exists())

    def test_reserved_output_cleanup_restores_a_concurrent_replacement(self):
        request, target, _ = self.build_request()
        target.write_bytes(b"stale before apply\n")
        output = self.evidence_root / "reserved-output-race.json"
        original_move = runtime._move_to_private_quarantine
        raced = False

        def replace_output_before_quarantine(directory_fd, source, label):
            nonlocal raced
            if label == "receipt" and not raced:
                raced = True
                output.unlink()
                output.write_bytes(b"concurrent evidence bytes\n")
            return original_move(directory_fd, source, label)

        with mock.patch.object(
            runtime,
            "_move_to_private_quarantine",
            side_effect=replace_output_before_quarantine,
        ):
            self.assert_error("rollback_failed", request, output=output)

        self.assertEqual(b"stale before apply\n", target.read_bytes())
        self.assertEqual(b"concurrent evidence bytes\n", output.read_bytes())

    def test_concurrent_write_after_receipt_write_is_preserved_without_receipt(self):
        request, target, _ = self.build_request()
        output = self.evidence_root / "post-receipt-race.json"
        original_live_check = runtime._require_live_target_state
        calls = 0

        def write_before_final_check(state, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                target.write_bytes(b"concurrent after receipt\n")
            return original_live_check(state, **kwargs)

        with mock.patch.object(
            runtime,
            "_require_live_target_state",
            side_effect=write_before_final_check,
        ):
            self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"concurrent after receipt\n", target.read_bytes())
        self.assertFalse(output.exists())
        self.assertEqual([], list(target.parent.glob(".keystone-owned-apply-*.tmp")))

    def test_concurrent_write_before_backup_discard_is_preserved_without_receipt(self):
        request, target, _ = self.build_request()
        output = self.evidence_root / "backup-discard-race.json"
        original_discard = runtime._discard_existing_backup

        def write_then_discard(state, expected_content):
            target.write_bytes(b"concurrent before discard\n")
            return original_discard(state, expected_content)

        with mock.patch.object(
            runtime,
            "_discard_existing_backup",
            side_effect=write_then_discard,
        ):
            self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"concurrent before discard\n", target.read_bytes())
        self.assertFalse(output.exists())
        self.assertEqual([], list(target.parent.glob(".keystone-owned-apply-*.tmp")))

    def test_parent_namespace_change_before_publish_never_writes_detached_target(self):
        request, _, _ = self.build_request()
        output = self.evidence_root / "detached-before.json"
        original_replace = runtime._replace_target_bytes
        detached = self.root / "detached-before"

        def detach_then_replace(state, payload, mode, **kwargs):
            (self.root / "00_docs").rename(detached)
            (self.root / "00_docs").mkdir()
            (self.root / "00_docs" / "work.md").write_bytes(b"concurrent\n")
            return original_replace(state, payload, mode, **kwargs)

        with mock.patch.object(
            runtime, "_replace_target_bytes", side_effect=detach_then_replace
        ):
            self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"before\n", (detached / "work.md").read_bytes())
        self.assertEqual(
            b"concurrent\n", (self.root / "00_docs" / "work.md").read_bytes()
        )
        self.assertFalse(output.exists())

    def test_parent_namespace_change_after_publish_rolls_back_without_receipt(self):
        request, _, _ = self.build_request()
        output = self.evidence_root / "detached-after.json"
        original_live_check = runtime._require_live_target_state
        detached = self.root / "detached-after"
        calls = 0

        def detach_before_receipt(state, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                (self.root / "00_docs").rename(detached)
                (self.root / "00_docs").mkdir()
                (self.root / "00_docs" / "work.md").write_bytes(b"concurrent\n")
            return original_live_check(state, **kwargs)

        with mock.patch.object(
            runtime,
            "_require_live_target_state",
            side_effect=detach_before_receipt,
        ):
            self.assert_error("baseline_stale", request, output=output)

        self.assertEqual(b"before\n", (detached / "work.md").read_bytes())
        self.assertEqual(
            b"concurrent\n", (self.root / "00_docs" / "work.md").read_bytes()
        )
        self.assertFalse(output.exists())

    def test_cli_distinguishes_validation_from_security_failures(self):
        request, _, _ = self.build_request(allowed=["different"])
        validation_output = self.evidence_root / "validation.json"
        completed = self.run_entrypoint(AUTHOR_RUNNER, request, validation_output)
        self.assertEqual(1, completed.returncode)
        self.assertEqual("fail", json.loads(completed.stdout)["status"])

        request, _, _ = self.build_request()
        security_output = self.evidence_root / "security.json"
        security_output.write_bytes(b"exists")
        completed = self.run_entrypoint(AUTHOR_RUNNER, request, security_output)
        self.assertEqual(2, completed.returncode)
        self.assertEqual("error", json.loads(completed.stdout)["status"])
        self.assertEqual("output_exists", json.loads(completed.stdout)["diagnostics"][0]["code"])

        completed = subprocess.run(
            [sys.executable, "-I", str(AUTHOR_RUNNER)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, completed.returncode)
        self.assertEqual("error", json.loads(completed.stdout)["status"])
        self.assertEqual(
            "invocation_invalid",
            json.loads(completed.stdout)["diagnostics"][0]["code"],
        )


class FilesystemSecurityTests(OwnedSurfaceApplyFixture):
    def test_repository_and_evidence_roots_must_be_disjoint(self):
        request, target, _ = self.build_request()
        request_path = self.write_request(request)
        inside_repository = self.root / "evidence"
        inside_repository.mkdir()

        with self.assertRaises(runtime.ApplyError) as raised:
            runtime.apply_owned_surface_patch(
                root=self.root,
                request_path=request_path,
                evidence_root=inside_repository,
                output_path=inside_repository / "receipt.json",
                authority_key=self.key,
                pinned_key_sha256=self.key_digest,
                allowed_owners=frozenset({"author"}),
                runner_path=CANONICAL_RUNTIME,
            )
        self.assertEqual("evidence_root_security_invalid", raised.exception.code)
        self.assertEqual(b"before\n", target.read_bytes())

        with self.assertRaises(runtime.ApplyError) as raised:
            runtime.apply_owned_surface_patch(
                root=self.root,
                request_path=request_path,
                evidence_root=self.base,
                output_path=self.base / "receipt.json",
                authority_key=self.key,
                pinned_key_sha256=self.key_digest,
                allowed_owners=frozenset({"author"}),
                runner_path=CANONICAL_RUNTIME,
            )
        self.assertEqual("evidence_root_security_invalid", raised.exception.code)
        self.assertEqual(b"before\n", target.read_bytes())

    def test_request_must_be_a_single_link_evidence_root_descendant(self):
        request, target, _ = self.build_request()
        outside_request = self.base / "outside-request.json"
        outside_request.write_bytes(runtime.canonical_json_bytes(request))

        with self.assertRaises(runtime.ApplyError) as raised:
            runtime.apply_owned_surface_patch(
                root=self.root,
                request_path=outside_request,
                evidence_root=self.evidence_root,
                output_path=self.evidence_root / "outside-request-receipt.json",
                authority_key=self.key,
                pinned_key_sha256=self.key_digest,
                allowed_owners=frozenset({"author"}),
                runner_path=CANONICAL_RUNTIME,
            )
        self.assertEqual("request_security_invalid", raised.exception.code)
        self.assertEqual(b"before\n", target.read_bytes())

        inside_request = self.write_request(request)
        hard_link = self.request_root / "request-hardlink.json"
        os.link(inside_request, hard_link)
        with self.assertRaises(runtime.ApplyError) as raised:
            runtime.apply_owned_surface_patch(
                root=self.root,
                request_path=inside_request,
                evidence_root=self.evidence_root,
                output_path=self.evidence_root / "hardlink-request-receipt.json",
                authority_key=self.key,
                pinned_key_sha256=self.key_digest,
                allowed_owners=frozenset({"author"}),
                runner_path=CANONICAL_RUNTIME,
            )
        self.assertEqual("request_security_invalid", raised.exception.code)
        self.assertEqual(b"before\n", target.read_bytes())

    def test_key_must_be_external_private_owned_regular_and_single_link(self):
        request, target, _ = self.build_request()

        insecure = self.base / "insecure.key"
        insecure.write_bytes(self.key_bytes)
        insecure.chmod(0o644)
        self.assert_error("authority_key_security_invalid", request, key=insecure)

        key_link = self.base / "key-link"
        key_link.symlink_to(self.key)
        self.assert_error("authority_key_security_invalid", request, key=key_link)

        real_key_parent = self.base / "real-key-parent"
        real_key_parent.mkdir()
        nested_key = real_key_parent / "nested.key"
        nested_key.write_bytes(self.key_bytes)
        nested_key.chmod(0o600)
        linked_key_parent = self.base / "linked-key-parent"
        linked_key_parent.symlink_to(real_key_parent, target_is_directory=True)
        self.assert_error(
            "authority_key_security_invalid",
            request,
            key=linked_key_parent / "nested.key",
        )

        hard_link = self.base / "hard-key"
        os.link(self.key, hard_link)
        self.assert_error("authority_key_security_invalid", request, key=hard_link)
        hard_link.unlink()

        repository_key = self.root / "repository.key"
        repository_key.write_bytes(self.key_bytes)
        repository_key.chmod(0o600)
        self.assert_error("authority_key_security_invalid", request, key=repository_key)
        self.assertEqual(b"before\n", target.read_bytes())

    def test_target_and_every_parent_must_not_be_symlinks_or_hardlinks(self):
        request, target, _ = self.build_request()
        outside = self.base / "outside.md"
        outside.write_bytes(b"before\n")
        target.unlink()
        target.symlink_to(outside)
        self.assert_error("target_security_invalid", request)
        self.assertEqual(b"before\n", outside.read_bytes())

        request, target, _ = self.build_request(target_path="00_docs/hard.md")
        second_link = self.base / "hard.md"
        os.link(target, second_link)
        self.assert_error("target_security_invalid", request)
        self.assertEqual(b"before\n", target.read_bytes())

        real_parent = self.root / "real-parent"
        real_parent.mkdir()
        (real_parent / "work.md").write_bytes(b"before\n")
        linked_parent = self.root / "linked-parent"
        linked_parent.symlink_to(real_parent, target_is_directory=True)
        request, _, _ = self.build_request(target_path="linked-parent/work.md")
        self.assert_error("target_security_invalid", request)
        self.assertEqual(b"before\n", (real_parent / "work.md").read_bytes())

    def test_output_parent_symlink_is_rejected_before_target_write(self):
        request, target, _ = self.build_request()
        real_output_parent = self.evidence_root / "real"
        real_output_parent.mkdir()
        linked_output_parent = self.evidence_root / "linked"
        linked_output_parent.symlink_to(real_output_parent, target_is_directory=True)

        self.assert_error(
            "output_security_invalid",
            request,
            output=linked_output_parent / "receipt.json",
        )

        self.assertEqual(b"before\n", target.read_bytes())
        self.assertFalse((real_output_parent / "receipt.json").exists())


class ReceiptAndParityTests(OwnedSurfaceApplyFixture):
    def test_receipt_hmac_authenticates_exact_envelope_and_patch(self):
        request, _, _ = self.build_request()
        envelope, output = self.apply(request)
        self.assertEqual(runtime.canonical_json_bytes(envelope), output.read_bytes())

        unsigned_envelope = dict(envelope)
        receipt = unsigned_envelope.pop("receipt")
        unsigned_receipt = dict(receipt)
        mac = unsigned_receipt.pop("mac")
        derived = hashlib.sha256(
            b"keystone-owned-surface-apply-key-v1\0" + self.key_bytes
        ).digest()
        payload = runtime.canonical_json_bytes(
            {"envelope": unsigned_envelope, "receipt": unsigned_receipt}
        )
        expected = "hmac-sha256:" + hmac.new(
            derived, payload, hashlib.sha256
        ).hexdigest()
        self.assertTrue(hmac.compare_digest(expected, mac))

        substituted = copy.deepcopy(unsigned_receipt)
        substituted["patch_receipt"]["patch"]["patch_id"] = "substituted"
        substituted_payload = runtime.canonical_json_bytes(
            {"envelope": unsigned_envelope, "receipt": substituted}
        )
        substituted_mac = "hmac-sha256:" + hmac.new(
            derived, substituted_payload, hashlib.sha256
        ).hexdigest()
        self.assertFalse(hmac.compare_digest(substituted_mac, mac))

    def test_generated_runtime_copies_are_byte_identical_and_generator_checks(self):
        canonical = CANONICAL_RUNTIME.read_bytes()
        self.assertEqual(canonical, AUTHOR_RUNTIME.read_bytes())
        self.assertEqual(canonical, COORDINATOR_RUNTIME.read_bytes())
        for generated in (AUTHOR_RUNTIME, COORDINATOR_RUNTIME):
            self.assertFalse(generated.is_symlink())
            self.assertEqual(1, generated.stat().st_nlink)

        completed = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
