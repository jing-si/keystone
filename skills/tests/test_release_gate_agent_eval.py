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


REPOSITORY_ROOT = Path(__file__).parents[2]
SCRIPTS = REPOSITORY_ROOT / "scripts"
SPEC_PATH = SCRIPTS / "agent_eval_scenarios.json"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AGENT_EVAL = load_module("validate_agent_evals", SCRIPTS / "validate_agent_evals.py")
RELEASE_GATE = load_module("run_release_gate", SCRIPTS / "run_release_gate.py")


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_time(value):
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(root, *arguments):
    return subprocess.run(
        ["git", "-C", str(root), *arguments], capture_output=True, text=True,
        check=False,
    )


class AgentEvalValidationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.root = REPOSITORY_ROOT
        self.evidence_root = self.base / "evidence"
        self.evidence_root.mkdir()
        self.results_path = self.evidence_root / "agent-eval-results.json"
        self.key_path = self.base / "reviewer.key"
        self.key_path.write_bytes(b"independent-reviewer-secret-material-r010")
        self.key_path.chmod(0o600)
        self.key_sha256 = digest(self.key_path)
        self.reviewer = "reviewer:r010-independent"
        self.spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        self.now = datetime.now(timezone.utc).replace(microsecond=0)

    def tearDown(self):
        self.temporary.cleanup()

    def _write_json(self, relative, value):
        path = self.evidence_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
        return path

    def _sign(self, value):
        unsigned = dict(value)
        unsigned.pop("attestation", None)
        body = json.dumps(
            unsigned, ensure_ascii=True, separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")
        signature = hmac.new(self.key_path.read_bytes(), body, hashlib.sha256).hexdigest()
        value["attestation"] = {
            "reviewer_id": self.reviewer,
            "algorithm": "hmac-sha256",
            "hmac_sha256": signature,
        }

    def valid_results(self):
        subject = AGENT_EVAL.expected_subject(self.root)
        started = self.now - timedelta(hours=2)
        recorded = self.now - timedelta(hours=1)
        completed = self.now - timedelta(minutes=30)
        scenarios = []
        for index, scenario in enumerate(self.spec["scenarios"]):
            transcript_value = {
                "schema_version": 1,
                "scenario_id": scenario["id"],
                "subject": subject,
                "turns": [
                    {"role": "user", "content": scenario["prompt"]},
                    {"role": "assistant", "content": "Observed outcome for %s." % scenario["id"]},
                ],
            }
            evidence_value = {
                "schema_version": 1,
                "scenario_id": scenario["id"],
                "subject": subject,
                "checks": [
                    {"id": check, "status": "pass", "evidence": "%s verified" % check}
                    for check in scenario["required_checks"]
                ],
            }
            transcript = self._write_json(
                "scenarios/%02d-transcript.json" % index, transcript_value
            )
            evidence = self._write_json(
                "scenarios/%02d-evidence.json" % index, evidence_value
            )
            scenarios.append({
                "id": scenario["id"],
                "transcript": {
                    "path": transcript.relative_to(self.evidence_root).as_posix(),
                    "sha256": digest(transcript),
                },
                "evidence": {
                    "path": evidence.relative_to(self.evidence_root).as_posix(),
                    "sha256": digest(evidence),
                },
                "outcome": {
                    "status": "pass",
                    "expected": scenario["expected_outcome"],
                    "observed": "All exact required checks passed.",
                    "recorded_by": self.reviewer,
                    "recorded_at": canonical_time(recorded),
                },
            })
        identity_files = {}
        for relative, content in (
            ("identity/runner-executable.bin", "runner executable r010\n"),
            ("identity/runner-config.json", '{"runner":"r010"}\n'),
            ("identity/model-executable.txt", "model runtime r010\n"),
            ("identity/model-config.json", '{"model":"fixture-1"}\n'),
        ):
            path = self.evidence_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            identity_files[relative] = {
                "path": relative,
                "sha256": digest(path),
            }
        value = {
            "schema_version": 1,
            "suite_id": self.spec["suite_id"],
            "spec": {
                "path": SPEC_PATH.relative_to(self.root).as_posix(),
                "sha256": digest(SPEC_PATH),
            },
            "subject": subject,
            "runner": {
                "name": "local-agent-eval-runner",
                "version": "1.0",
                "identity": "runner:r010-local",
                "executable": identity_files["identity/runner-executable.bin"],
                "config": identity_files["identity/runner-config.json"],
                "invocation_id": "runner-invocation-r010",
            },
            "model": {
                "name": "agent-model",
                "version": "fixture-1",
                "identity": "model:agent-fixture",
                "executable": identity_files["identity/model-executable.txt"],
                "config": identity_files["identity/model-config.json"],
                "invocation_id": "model-invocation-r010",
            },
            "started_at": canonical_time(started),
            "completed_at": canonical_time(completed),
            "scenarios": scenarios,
        }
        self._sign(value)
        return value

    def validate(self, value=None, **overrides):
        if value is not None:
            self.results_path.write_text(json.dumps(value), encoding="utf-8")
        arguments = {
            "evidence_root": self.evidence_root,
            "reviewer_key_path": self.key_path,
            "trusted_reviewer_id": self.reviewer,
            "trusted_reviewer_key_sha256": self.key_sha256,
            "now": self.now,
            "max_age_hours": 168,
        }
        arguments.update(overrides)
        return AGENT_EVAL.validate_agent_eval_results(
            self.root, SPEC_PATH, self.results_path, **arguments
        )

    def test_absent_results_and_repository_evidence_root_fail_closed(self):
        absent = self.validate()
        self.assertIn("agent_eval_results_missing", {item["code"] for item in absent})
        value = self.valid_results()
        findings = self.validate(value, evidence_root=self.root)
        self.assertIn("evidence_root_not_external", {item["code"] for item in findings})

    def test_valid_attested_results_pass_exact_scenarios(self):
        value = self.valid_results()
        self.assertEqual(12, len(value["scenarios"]))
        self.assertEqual([], self.validate(value))

    def test_empty_transcript_and_arbitrary_evidence_are_rejected(self):
        value = self.valid_results()
        transcript = self.evidence_root / value["scenarios"][0]["transcript"]["path"]
        transcript.write_text(json.dumps({"scenario": "uninitialized", "turns": []}), encoding="utf-8")
        value["scenarios"][0]["transcript"]["sha256"] = digest(transcript)
        evidence = self.evidence_root / value["scenarios"][0]["evidence"]["path"]
        evidence.write_text(json.dumps({"checks": ["bounded"]}), encoding="utf-8")
        value["scenarios"][0]["evidence"]["sha256"] = digest(evidence)
        self._sign(value)
        codes = {item["code"] for item in self.validate(value)}
        self.assertIn("transcript_invalid", codes)
        self.assertIn("scenario_evidence_invalid", codes)

    def test_malformed_results_and_symlinked_results_are_rejected(self):
        self.results_path.write_text("{not-json", encoding="utf-8")
        self.assertIn(
            "agent_eval_results_invalid",
            {item["code"] for item in self.validate()},
        )

        value = self.valid_results()
        self.results_path.write_text(json.dumps(value), encoding="utf-8")
        target = self.evidence_root / "real-results.json"
        self.results_path.replace(target)
        self.results_path.symlink_to(target.name)
        self.assertIn(
            "agent_eval_results_missing",
            {item["code"] for item in self.validate()},
        )

    def test_wrong_scenario_and_required_checks_are_rejected(self):
        value = self.valid_results()
        item = value["scenarios"][0]
        transcript = self.evidence_root / item["transcript"]["path"]
        transcript_value = json.loads(transcript.read_text(encoding="utf-8"))
        transcript_value["scenario_id"] = "partial_scaffold"
        transcript.write_text(json.dumps(transcript_value), encoding="utf-8")
        item["transcript"]["sha256"] = digest(transcript)
        evidence = self.evidence_root / item["evidence"]["path"]
        evidence_value = json.loads(evidence.read_text(encoding="utf-8"))
        evidence_value["checks"].pop()
        evidence.write_text(json.dumps(evidence_value), encoding="utf-8")
        item["evidence"]["sha256"] = digest(evidence)
        self._sign(value)
        codes = {finding["code"] for finding in self.validate(value)}
        self.assertIn("transcript_scenario_mismatch", codes)
        self.assertIn("required_checks_mismatch", codes)

    def test_digest_inode_and_symlink_reuse_are_rejected(self):
        same_bytes = self.valid_results()
        first = same_bytes["scenarios"][0]["transcript"]
        second = same_bytes["scenarios"][1]["transcript"]
        first_path = self.evidence_root / first["path"]
        second_path = self.evidence_root / second["path"]
        second_path.write_bytes(first_path.read_bytes())
        second["sha256"] = digest(second_path)
        self._sign(same_bytes)
        self.assertIn(
            "evidence_digest_reused", {item["code"] for item in self.validate(same_bytes)}
        )

        same_inode = self.valid_results()
        first = same_inode["scenarios"][0]["transcript"]
        second = same_inode["scenarios"][1]["transcript"]
        first_path = self.evidence_root / first["path"]
        second_path = self.evidence_root / second["path"]
        second_path.unlink()
        os.link(str(first_path), str(second_path))
        second["sha256"] = digest(second_path)
        self._sign(same_inode)
        self.assertIn(
            "evidence_inode_reused", {item["code"] for item in self.validate(same_inode)}
        )

        symlinked = self.valid_results()
        item = symlinked["scenarios"][0]["transcript"]
        target = self.evidence_root / item["path"]
        link = target.with_name("linked-transcript.json")
        link.symlink_to(target.name)
        item["path"] = link.relative_to(self.evidence_root).as_posix()
        item["sha256"] = digest(target)
        self._sign(symlinked)
        self.assertIn(
            "evidence_path_invalid", {item["code"] for item in self.validate(symlinked)}
        )

    def test_subject_hmac_stale_and_future_results_are_rejected(self):
        subject = self.valid_results()
        subject["subject"]["repository_head"] = "0" * 40
        self._sign(subject)
        self.assertIn("subject_mismatch", {item["code"] for item in self.validate(subject)})

        signature = self.valid_results()
        signature["attestation"]["hmac_sha256"] = "0" * 64
        self.assertIn("attestation_invalid", {item["code"] for item in self.validate(signature)})

        stale = self.valid_results()
        old = self.now - timedelta(hours=200)
        stale["started_at"] = canonical_time(old - timedelta(hours=1))
        stale["completed_at"] = canonical_time(old)
        for item in stale["scenarios"]:
            item["outcome"]["recorded_at"] = canonical_time(old)
        self._sign(stale)
        self.assertIn("evidence_stale", {item["code"] for item in self.validate(stale)})

        future = self.valid_results()
        later = self.now + timedelta(hours=1)
        future["completed_at"] = canonical_time(later)
        for item in future["scenarios"]:
            item["outcome"]["recorded_at"] = canonical_time(later)
        self._sign(future)
        self.assertIn("timestamp_in_future", {item["code"] for item in self.validate(future)})

    def test_runner_model_digest_invocation_and_key_identity_are_required(self):
        value = self.valid_results()
        value["runner"]["executable"]["sha256"] = "self-reported"
        value["model"]["invocation_id"] = value["runner"]["invocation_id"]
        self._sign(value)
        codes = {item["code"] for item in self.validate(value)}
        self.assertIn("evidence_digest_invalid", codes)
        self.assertIn("agent_eval_identity_conflict", codes)

        valid = self.valid_results()
        linked_key = self.base / "linked-reviewer.key"
        linked_key.symlink_to(self.key_path.name)
        self.assertIn(
            "reviewer_key_invalid",
            {item["code"] for item in self.validate(
                valid, reviewer_key_path=linked_key
            )},
        )


class ReleaseGateTest(unittest.TestCase):
    def _git_repository(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        self.assertEqual(0, run_git(root, "init", "-q").returncode)
        self.assertEqual(0, run_git(root, "config", "user.name", "Release Gate Test").returncode)
        self.assertEqual(0, run_git(root, "config", "user.email", "release@example.invalid").returncode)
        (root / "tracked.txt").write_text("clean\n", encoding="utf-8")
        self.assertEqual(0, run_git(root, "add", "tracked.txt").returncode)
        self.assertEqual(0, run_git(root, "commit", "-q", "-m", "fixture").returncode)
        return temporary, root

    def test_preflight_accepts_clean_and_rejects_dirty_tracked_staged_untracked(self):
        temporary, root = self._git_repository()
        with temporary:
            self.assertEqual(0, RELEASE_GATE._release_preflight_check(root).returncode)

        cases = ("tracked", "staged", "untracked")
        for case in cases:
            with self.subTest(case=case):
                temporary, root = self._git_repository()
                with temporary:
                    if case == "untracked":
                        (root / "new.txt").write_text("new\n", encoding="utf-8")
                    else:
                        (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
                        if case == "staged":
                            self.assertEqual(0, run_git(root, "add", "tracked.txt").returncode)
                    result = RELEASE_GATE._release_preflight_check(root)
                    self.assertEqual(1, result.returncode)
                    self.assertIn("not clean", result.stderr)

    def test_preflight_failure_is_fail_fast(self):
        steps = (
            RELEASE_GATE.GateStep("release_preflight", "release_preflight", ("<internal>",)),
            RELEASE_GATE.GateStep("must_not_run", "command", ("run",)),
        )
        payload, exit_code = RELEASE_GATE.run_plan(
            REPOSITORY_ROOT,
            steps,
            executor=lambda *_args: self.fail("later command must not run"),
            installer_checker=lambda _root: self.fail("installer must not run"),
            internal_checkers={
                "release_preflight": lambda _root: RELEASE_GATE.CommandResult(
                    1, "", "repository is not clean"
                )
            },
        )
        self.assertEqual(1, exit_code)
        self.assertEqual(1, payload["summary"]["total"])
        self.assertEqual("release_preflight", payload["steps"][0]["id"])

    def test_rc_and_production_plans_start_with_preflight_and_split_finalization(self):
        with tempfile.TemporaryDirectory() as temporary:
            evidence = Path(temporary) / "evidence"
            evidence.mkdir()
            key = Path(temporary) / "reviewer.key"
            key.write_bytes(b"key")
            common = {
                "evidence_root": evidence,
                "reviewer_key_path": key,
                "trusted_reviewer_id": "reviewer:test",
            }
            rc = RELEASE_GATE.build_plan(
                REPOSITORY_ROOT, evidence / "results.json", profile="rc", **common
            )
            production = RELEASE_GATE.build_plan(
                REPOSITORY_ROOT, evidence / "results.json", profile="production", **common
            )
        self.assertEqual("release_preflight", rc[0].identifier)
        self.assertEqual("release_preflight", production[0].identifier)
        self.assertNotIn("current_repository_finalization", {item.identifier for item in rc})
        self.assertIn("current_repository_finalization", {
            item.identifier for item in production
        })
        for identifier in (
            "historical_r008_r009_finalization", "agent_behavior_evidence",
            "installer_staging_parity_rollback",
        ):
            self.assertIn(identifier, {item.identifier for item in rc})
            self.assertIn(identifier, {item.identifier for item in production})

    def test_current_finalization_fails_closed_while_round_is_active(self):
        result = RELEASE_GATE._current_finalization_check(REPOSITORY_ROOT)
        self.assertEqual(1, result.returncode)
        self.assertIn("active_round: none", result.stderr)

    def test_actual_historical_r008_r009_compatibility(self):
        result = RELEASE_GATE._historical_finalization_check(REPOSITORY_ROOT)
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)
        self.assertIn("R008 stdout", result.stdout)
        self.assertIn("R009 stdout", result.stdout)

    def test_installer_manifest_and_symlink_tree_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "skills"
            destination.mkdir()
            manifest = destination / ".keystone-install.json"
            value = {
                "schema_version": 1,
                "package_version": (REPOSITORY_ROOT / "VERSION").read_text(
                    encoding="utf-8"
                ).strip(),
                "source_commit": RELEASE_GATE._canonical_head(REPOSITORY_ROOT),
                "source_dirty": True,
                "skills": list(RELEASE_GATE.SKILL_NAMES),
            }
            manifest.write_text(json.dumps(value), encoding="utf-8")
            self.assertIn(
                "source_dirty", RELEASE_GATE._validate_install_manifest(
                    REPOSITORY_ROOT, destination
                ) or ""
            )
            value["source_dirty"] = False
            manifest.write_text(json.dumps(value), encoding="utf-8")
            self.assertIsNone(RELEASE_GATE._validate_install_manifest(
                REPOSITORY_ROOT, destination
            ))

            tree = Path(temporary) / "tree"
            tree.mkdir()
            (tree / "target").write_text("target", encoding="utf-8")
            (tree / "link").symlink_to("target")
            with self.assertRaises(ValueError):
                RELEASE_GATE._tree_digest(tree)


if __name__ == "__main__":
    unittest.main()
