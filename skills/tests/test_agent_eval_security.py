import hashlib
import hmac
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "scripts" / "agent_eval_scenarios.json"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "agent_eval_security_validator", ROOT / "scripts" / "validate_agent_evals.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest(path):
    return digest_bytes(path.read_bytes())


def timestamp(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class AgentEvalSecurityTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.evidence_root = self.base / "evidence"
        self.evidence_root.mkdir()
        self.results_path = self.evidence_root / "results.json"
        self.key_path = self.base / "reviewer.key"
        self.key_path.write_bytes(b"independent-reviewer-key-material-32-bytes-minimum")
        self.key_path.chmod(0o600)
        self.key_digest = digest(self.key_path)
        self.reviewer = "reviewer:security-suite"
        self.now = datetime.now(timezone.utc).replace(microsecond=0)
        self.spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

    def tearDown(self):
        self.temporary.cleanup()

    def write_attachment(self, relative, value):
        path = self.evidence_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, bytes):
            path.write_bytes(value)
        else:
            path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
        return {"path": relative, "sha256": digest(path)}

    def sign_and_write(self, value, key=None):
        key_bytes = self.key_path.read_bytes() if key is None else key
        unsigned = dict(value)
        unsigned.pop("attestation", None)
        body = json.dumps(
            unsigned, ensure_ascii=True, separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")
        value["attestation"] = {
            "reviewer_id": self.reviewer,
            "algorithm": "hmac-sha256",
            "hmac_sha256": hmac.new(key_bytes, body, hashlib.sha256).hexdigest(),
        }
        self.results_path.write_text(json.dumps(value), encoding="utf-8")

    def valid_results(self):
        subject = VALIDATOR.expected_subject(ROOT)
        runner_executable = self.write_attachment(
            "identity/runner-executable.bin", b"measured runner executable"
        )
        runner_config = self.write_attachment(
            "identity/runner-config.json", b'{"runner":"strict"}'
        )
        model_executable = self.write_attachment(
            "identity/model-executable.bin", b"measured model executable"
        )
        model_config = self.write_attachment(
            "identity/model-config.json", b'{"model":"fixture-security"}'
        )
        scenarios = []
        for index, scenario in enumerate(self.spec["scenarios"]):
            transcript = {
                "schema_version": 1,
                "scenario_id": scenario["id"],
                "subject": subject,
                "turns": [
                    {"role": "user", "content": scenario["prompt"]},
                    {"role": "assistant", "content": "Measured behavior %02d" % index},
                ],
            }
            evidence = {
                "schema_version": 1,
                "scenario_id": scenario["id"],
                "subject": subject,
                "checks": [
                    {"id": check, "status": "pass", "evidence": "%s measured" % check}
                    for check in scenario["required_checks"]
                ],
            }
            scenarios.append({
                "id": scenario["id"],
                "transcript": self.write_attachment(
                    "scenarios/%02d-transcript.json" % index, transcript
                ),
                "evidence": self.write_attachment(
                    "scenarios/%02d-evidence.json" % index, evidence
                ),
                "outcome": {
                    "status": "pass",
                    "expected": scenario["expected_outcome"],
                    "observed": "Exact required checks passed.",
                    "recorded_by": self.reviewer,
                    "recorded_at": timestamp(self.now - timedelta(minutes=20)),
                },
            })
        return {
            "schema_version": 1,
            "suite_id": self.spec["suite_id"],
            "spec": {
                "path": SPEC_PATH.relative_to(ROOT).as_posix(),
                "sha256": digest(SPEC_PATH),
            },
            "subject": subject,
            "runner": {
                "name": "measured-runner", "version": "1", "identity": "runner:one",
                "executable": runner_executable, "config": runner_config,
                "invocation_id": "runner-invocation-one",
            },
            "model": {
                "name": "measured-model", "version": "1", "identity": "model:one",
                "executable": model_executable, "config": model_config,
                "invocation_id": "model-invocation-one",
            },
            "started_at": timestamp(self.now - timedelta(hours=1)),
            "completed_at": timestamp(self.now - timedelta(minutes=10)),
            "scenarios": scenarios,
        }

    def validate(self, value=None, **overrides):
        if value is not None:
            self.sign_and_write(value)
        arguments = {
            "evidence_root": self.evidence_root,
            "reviewer_key_path": self.key_path,
            "trusted_reviewer_id": self.reviewer,
            "trusted_reviewer_key_sha256": self.key_digest,
            "now": self.now,
        }
        arguments.update(overrides)
        return VALIDATOR.validate_agent_eval_results(
            ROOT, SPEC_PATH, self.results_path, **arguments
        )

    def test_measured_identity_passes_and_untrusted_path_environment_is_ignored(self):
        value = self.valid_results()
        fake_bin = self.base / "fake-bin"
        fake_bin.mkdir()
        fake_git = fake_bin / "git"
        fake_git.write_text("#!/bin/sh\nprintf '%040d\\n' 0\n", encoding="utf-8")
        fake_git.chmod(0o755)
        with mock.patch.dict(
            os.environ,
            {"PATH": str(fake_bin), "PYTHONPATH": str(self.base / "injected")},
        ):
            self.assertEqual([], self.validate(value))
        codes = {item["code"] for item in self.validate(
            value, trusted_reviewer_id="reviewer:not-trusted"
        )}
        self.assertIn("attestation_invalid", codes)
        self.assertIn("outcome_recorder_not_trusted", codes)

    def test_key_anchor_length_mode_hardlink_and_symlink_parent_fail(self):
        value = self.valid_results()
        self.key_path.write_bytes(b"x")
        self.key_path.chmod(0o600)
        codes = {item["code"] for item in self.validate(
            value, trusted_reviewer_key_sha256=digest(self.key_path)
        )}
        self.assertIn("reviewer_key_invalid", codes)

        self.key_path.write_bytes(b"secure-key-material-restored-for-mode-test")
        self.key_path.chmod(0o644)
        codes = {item["code"] for item in self.validate(
            value, trusted_reviewer_key_sha256=digest(self.key_path)
        )}
        self.assertIn("reviewer_key_invalid", codes)

        self.key_path.chmod(0o600)
        hardlink = self.base / "reviewer-hardlink.key"
        os.link(str(self.key_path), str(hardlink))
        codes = {item["code"] for item in self.validate(
            value, trusted_reviewer_key_sha256=digest(self.key_path)
        )}
        self.assertIn("reviewer_key_invalid", codes)
        hardlink.unlink()

        real_parent = self.base / "real-key-parent"
        real_parent.mkdir()
        nested_key = real_parent / "key"
        nested_key.write_bytes(b"nested-secure-reviewer-key-material-32-bytes")
        nested_key.chmod(0o600)
        linked_parent = self.base / "linked-key-parent"
        linked_parent.symlink_to(real_parent.name)
        codes = {item["code"] for item in self.validate(
            value, reviewer_key_path=linked_parent / "key",
            trusted_reviewer_key_sha256=digest(nested_key),
        )}
        self.assertIn("reviewer_key_invalid", codes)

    def test_key_anchor_and_evidence_symlink_parent_fail(self):
        value = self.valid_results()
        codes = {item["code"] for item in self.validate(
            value, trusted_reviewer_key_sha256="sha256:" + "0" * 64
        )}
        self.assertIn("reviewer_key_anchor_mismatch", codes)

        real_evidence = self.base / "real-evidence"
        self.evidence_root.rename(real_evidence)
        linked_parent = self.base / "linked-parent"
        linked_parent.symlink_to(self.base)
        alias = linked_parent / "real-evidence"
        findings = VALIDATOR.validate_agent_eval_results(
            ROOT, SPEC_PATH, alias / "results.json", evidence_root=alias,
            reviewer_key_path=self.key_path, trusted_reviewer_id=self.reviewer,
            trusted_reviewer_key_sha256=self.key_digest, now=self.now,
        )
        self.assertIn("evidence_root_not_external", {item["code"] for item in findings})

    def test_results_path_rejects_an_internal_symlink_parent(self):
        value = self.valid_results()
        self.sign_and_write(value)
        real_parent = self.evidence_root / "real-results-parent"
        real_parent.mkdir()
        moved_results = real_parent / "results.json"
        self.results_path.replace(moved_results)
        linked_parent = self.evidence_root / "linked-results-parent"
        linked_parent.symlink_to(real_parent.name)
        findings = VALIDATOR.validate_agent_eval_results(
            ROOT, SPEC_PATH, linked_parent / "results.json",
            evidence_root=self.evidence_root,
            reviewer_key_path=self.key_path,
            trusted_reviewer_id=self.reviewer,
            trusted_reviewer_key_sha256=self.key_digest,
            now=self.now,
        )
        self.assertIn("agent_eval_results_missing", {
            item["code"] for item in findings
        })

    def test_recursive_duplicate_keys_and_evidence_hardlinks_fail(self):
        value = self.valid_results()
        transcript_ref = value["scenarios"][0]["transcript"]
        transcript = self.evidence_root / transcript_ref["path"]
        raw = transcript.read_text(encoding="utf-8")
        raw = raw.replace('"role": "user"', '"role": "user", "role": "user"', 1)
        transcript.write_text(raw, encoding="utf-8")
        transcript_ref["sha256"] = digest(transcript)
        codes = {item["code"] for item in self.validate(value)}
        self.assertIn("transcript_invalid", codes)

        value = self.valid_results()
        transcript = self.evidence_root / value["scenarios"][0]["transcript"]["path"]
        hardlink = self.evidence_root / "scenarios/hardlinked-transcript.json"
        os.link(str(transcript), str(hardlink))
        codes = {item["code"] for item in self.validate(value)}
        self.assertIn("evidence_inode_reused", codes)

        hardlink.unlink()
        self.sign_and_write(value)
        results_hardlink = self.evidence_root / "results-hardlink.json"
        os.link(str(self.results_path), str(results_hardlink))
        codes = {item["code"] for item in self.validate()}
        self.assertIn("agent_eval_results_invalid", codes)
        results_hardlink.unlink()

        self.results_path.write_text(
            '{"schema_version":1,"schema_version":1}', encoding="utf-8"
        )
        codes = {item["code"] for item in self.validate()}
        self.assertIn("agent_eval_results_invalid", codes)

    def test_stale_started_outcome_and_long_run_fail(self):
        value = self.valid_results()
        value["started_at"] = timestamp(self.now - timedelta(hours=200))
        value["scenarios"][0]["outcome"]["recorded_at"] = timestamp(
            self.now - timedelta(hours=190)
        )
        codes = {item["code"] for item in self.validate(value)}
        self.assertIn("evidence_stale", codes)
        self.assertIn("run_duration_exceeded", codes)

    def test_measured_identity_bytes_are_bound(self):
        value = self.valid_results()
        executable = self.evidence_root / value["runner"]["executable"]["path"]
        executable.write_bytes(b"different executable bytes")
        codes = {item["code"] for item in self.validate(value)}
        self.assertIn("evidence_digest_mismatch", codes)

    def test_boolean_schema_versions_fail_at_top_and_nested_boundaries(self):
        top_level = self.valid_results()
        top_level["schema_version"] = True
        codes = {item["code"] for item in self.validate(top_level)}
        self.assertIn("agent_eval_schema_invalid", codes)

        nested = self.valid_results()
        item = nested["scenarios"][0]
        transcript_path = self.evidence_root / item["transcript"]["path"]
        transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
        transcript["schema_version"] = True
        transcript_path.write_text(json.dumps(transcript), encoding="utf-8")
        item["transcript"]["sha256"] = digest(transcript_path)
        evidence_path = self.evidence_root / item["evidence"]["path"]
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["schema_version"] = True
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        item["evidence"]["sha256"] = digest(evidence_path)
        codes = {item["code"] for item in self.validate(nested)}
        self.assertIn("transcript_invalid", codes)
        self.assertIn("scenario_evidence_invalid", codes)

    def test_cli_reads_trusted_key_anchor_from_the_named_environment(self):
        with mock.patch.dict(
            os.environ,
            {"KEYSTONE_AGENT_EVAL_TRUSTED_REVIEWER_KEY_SHA256": self.key_digest},
        ), mock.patch("sys.argv", ["validate_agent_evals.py"]):
            arguments = VALIDATOR.parse_args()
        self.assertEqual(self.key_digest, arguments.trusted_reviewer_key_sha256)

    def test_cli_reexec_isolated_before_forged_argparse_can_run(self):
        forged_modules = self.base / "forged-modules"
        forged_modules.mkdir()
        marker = self.base / "forged-argparse-ran"
        (forged_modules / "argparse.py").write_text(
            "open(%r, 'w').write('executed')\n" % str(marker),
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(forged_modules)
        environment["UNTRUSTED_STARTUP_VALUE"] = "must-not-survive"
        process = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_agent_evals.py"), "--help"],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertIn("trusted-reviewer-key-sha256", process.stdout)
        self.assertFalse(marker.exists())

    def test_authoritative_isolated_launcher_blocks_sitecustomize(self):
        forged_modules = self.base / "forged-startup"
        forged_modules.mkdir()
        marker = self.base / "forged-sitecustomize-ran"
        (forged_modules / "sitecustomize.py").write_text(
            "open(%r, 'w').write('executed')\n" % str(marker),
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(forged_modules)
        process = subprocess.run(
            [
                sys.executable, "-I",
                str(ROOT / "scripts" / "validate_agent_evals.py"), "--help",
            ],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
