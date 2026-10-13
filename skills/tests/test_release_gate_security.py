import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).parents[2]
RELEASE_GATE_PATH = REPOSITORY_ROOT / "scripts" / "run_release_gate.py"


def load_release_gate():
    spec = importlib.util.spec_from_file_location("run_release_gate_security", RELEASE_GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RELEASE_GATE = load_release_gate()


def pass_envelope(kind="diagnostic"):
    payload = {
        "schema_version": 1,
        "status": "pass",
        "diagnostics": [],
        "summary": {"errors": 0, "warnings": 0},
    }
    if kind == "linker":
        payload["coverage"] = {"complete": True}
    return json.dumps(payload)


class CleanReleaseRepository:
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="keystone lean release ")
        self.base = Path(self.temporary.name)
        self.root = self.base / "repository with spaces"

    def __enter__(self):
        ignored = shutil.ignore_patterns("__pycache__", "*.pyc")
        self.root.mkdir()
        for name in ("VERSION", "reinstall-local-keystone-skills.sh"):
            shutil.copy2(REPOSITORY_ROOT / name, self.root / name)
        shutil.copytree(REPOSITORY_ROOT / "scripts", self.root / "scripts", ignore=ignored)
        shutil.copytree(REPOSITORY_ROOT / "skills", self.root / "skills", ignore=ignored)
        git = str(RELEASE_GATE.TRUSTED_GIT)
        for command in (
            (git, "-C", str(self.root), "init", "-q"),
            (git, "-C", str(self.root), "config", "user.name", "Gate Test"),
            (git, "-C", str(self.root), "config", "user.email", "gate@example.invalid"),
            (git, "-C", str(self.root), "add", "."),
            (git, "-C", str(self.root), "commit", "-q", "-m", "fixture"),
        ):
            process = subprocess.run(command, capture_output=True, text=True, check=False)
            if process.returncode != 0:
                raise AssertionError(process.stderr)
        return self

    def __exit__(self, *_args):
        self.temporary.cleanup()


class ReleaseGateSecurityTest(unittest.TestCase):
    def test_canonical_plan_is_lean_and_has_no_retired_gate(self):
        expected_ids = [
            "release_preflight",
            "author_package_tests",
            "coordinator_package_tests",
            "linker_package_tests",
            "ideas_package_tests",
            "shared_skills_tests",
            "compileall",
            "docs_readiness",
            "repository_readiness",
            "work_state_runtime",
            "linker_repository_validation",
            "installer_staging_parity_rollback",
            "release_postflight",
        ]
        for profile in ("rc", "production"):
            plan = RELEASE_GATE.build_plan(REPOSITORY_ROOT, profile=profile)
            self.assertEqual(expected_ids, [step.identifier for step in plan])
            command_text = " ".join(part for step in plan for part in step.command)
            self.assertNotIn("agent_eval", command_text)
            self.assertNotIn("finalization-manifest", command_text)
            self.assertNotIn("capture_assignment_snapshot", command_text)
            self.assertNotIn("record_acceptance_event", command_text)

    def test_shell_launcher_ignores_hostile_python_and_shell_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            hostile = Path(temporary)
            marker = hostile / "startup-ran"
            (hostile / "sitecustomize.py").write_text(
                "from pathlib import Path\nPath(%r).write_text('site')\n" % str(marker),
                encoding="utf-8",
            )
            startup = hostile / "shell-startup"
            startup.write_text("touch %s\n" % marker, encoding="utf-8")
            environment = os.environ.copy()
            environment.update({
                "PYTHONPATH": str(hostile),
                "PYTHONHOME": str(hostile),
                "BASH_ENV": str(startup),
                "ENV": str(startup),
            })
            process = subprocess.run(
                ["/bin/sh", str(REPOSITORY_ROOT / "scripts" / "run_release_gate.sh"),
                 "--list", "--profile", "rc"],
                cwd=str(REPOSITORY_ROOT), env=environment,
                capture_output=True, text=True, check=False,
            )
            payload = json.loads(process.stdout)
            self.assertEqual(0, process.returncode, process.stderr)
            self.assertEqual("listed", payload["status"])
            self.assertFalse(marker.exists())

    def test_plan_substitution_or_truncation_is_rejected(self):
        plan = RELEASE_GATE.build_plan(REPOSITORY_ROOT)
        cases = (
            plan[:-1],
            tuple(
                replace(step, command=(sys.executable, "-c", "raise SystemExit(0)"))
                if step.identifier == "linker_repository_validation" else step
                for step in plan
            ),
        )
        for candidate in cases:
            payload, returncode = RELEASE_GATE.run_plan(REPOSITORY_ROOT, candidate)
            self.assertEqual(2, returncode)
            self.assertEqual("release_plan_invalid", payload["diagnostics"][0]["code"])

    def test_json_validator_rejects_duplicate_keys_and_incomplete_linker_coverage(self):
        duplicate = RELEASE_GATE.CommandResult(
            0,
            '{"schema_version":1,"status":"pass","status":"pass",'
            '"diagnostics":[],"summary":{"errors":0,"warnings":0}}',
            "",
        )
        self.assertEqual(2, RELEASE_GATE._validated_pass_envelope(
            duplicate, "validator"
        ).returncode)
        incomplete = json.loads(pass_envelope())
        incomplete["coverage"] = {"complete": False}
        self.assertEqual(2, RELEASE_GATE._validated_pass_envelope(
            RELEASE_GATE.CommandResult(0, json.dumps(incomplete), ""),
            "linker", "linker",
        ).returncode)
        self.assertEqual(0, RELEASE_GATE._validated_pass_envelope(
            RELEASE_GATE.CommandResult(0, pass_envelope("linker"), ""),
            "linker", "linker",
        ).returncode)

    def test_preflight_and_postflight_bind_one_clean_repository_generation(self):
        with CleanReleaseRepository() as repository:
            preflight = RELEASE_GATE._release_preflight_check(repository.root)
            state = RELEASE_GATE._release_state_from_result(preflight)
            self.assertEqual(0, preflight.returncode, preflight.stderr)
            self.assertIsNotNone(state)
            (repository.root / "VERSION").write_text("changed\n", encoding="utf-8")
            postflight = RELEASE_GATE._release_postflight_check(repository.root, state)
            self.assertEqual(1, postflight.returncode)

    def test_installer_stages_parity_and_rolls_back_failed_swap(self):
        with CleanReleaseRepository() as repository:
            result = RELEASE_GATE._installer_check(repository.root)
            self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_run_plan_stops_on_failure_without_running_release_only_extras(self):
        with CleanReleaseRepository() as repository:
            plan = RELEASE_GATE.build_plan(repository.root)
            calls = []

            def executor(argv, _cwd, environment):
                calls.append(tuple(argv))
                self.assertEqual(RELEASE_GATE.TRUSTED_PATH, environment["PATH"])
                self.assertNotIn("PYTHONPATH", environment)
                if "author_package_tests" not in calls:
                    return RELEASE_GATE.CommandResult(1, "", "test failure")
                return RELEASE_GATE.CommandResult(0, pass_envelope("linker"), "")

            payload, returncode = RELEASE_GATE.run_plan(
                repository.root, plan, executor=executor,
            )
            self.assertEqual(1, returncode)
            self.assertEqual("fail", payload["status"])
            self.assertEqual(2, len(payload["steps"]))


if __name__ == "__main__":
    unittest.main()
