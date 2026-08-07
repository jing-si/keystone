import importlib.util
import json
import os
import shutil
import stat
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
    spec = importlib.util.spec_from_file_location(
        "run_release_gate_security", RELEASE_GATE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RELEASE_GATE = load_release_gate()


def pass_envelope(kind="author"):
    payload = {
        "schema_version": 1,
        "status": "pass",
        "diagnostics": [],
        "summary": {"errors": 0, "warnings": 0},
    }
    if kind == "linker":
        payload["coverage"] = {
            "mode": "discovered",
            "complete": True,
            "path_digest": "sha256:" + "0" * 64,
            "discovered_sources": [],
            "parsed_sources": [],
            "omitted_sources": [],
            "declared_only_sources": [],
            "skipped_sources": [],
            "counts": {
                "discovered": 0,
                "parsed": 0,
                "omitted": 0,
                "declared_only": 0,
                "skipped": 0,
            },
        }
    elif kind == "agent":
        payload["suite_id"] = "r010-agent-behavior"
        payload["summary"] = {"errors": 0, "scenarios_required": 12}
    return json.dumps(payload)


class CleanReleaseRepository:
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="keystone release gate ")
        self.base = Path(self.temporary.name)
        self.root = self.base / "repository with spaces"
        self.evidence = self.base / "evidence with spaces"
        self.key = self.base / "trust" / "reviewer key"

    def __enter__(self):
        ignored = shutil.ignore_patterns("__pycache__", "*.pyc")
        self.root.mkdir()
        for name in ("VERSION", "reinstall-local-keystone-skills.sh"):
            shutil.copy2(str(REPOSITORY_ROOT / name), str(self.root / name))
        shutil.copytree(
            str(REPOSITORY_ROOT / "scripts"), str(self.root / "scripts"),
            ignore=ignored,
        )
        shutil.copytree(
            str(REPOSITORY_ROOT / "skills"), str(self.root / "skills"),
            ignore=ignored,
        )
        self.evidence.mkdir()
        self.key.parent.mkdir()
        self.key.write_bytes(b"independent-reviewer-test-key")
        git = str(RELEASE_GATE.TRUSTED_GIT)
        commands = (
            (git, "-C", str(self.root), "init", "-q"),
            (git, "-C", str(self.root), "config", "user.name", "Gate Test"),
            (git, "-C", str(self.root), "config", "user.email", "gate@example.invalid"),
            (git, "-C", str(self.root), "add", "."),
            (git, "-C", str(self.root), "commit", "-q", "-m", "fixture"),
        )
        for command in commands:
            process = subprocess.run(command, capture_output=True, text=True, check=False)
            if process.returncode != 0:
                raise AssertionError(process.stderr)
        return self

    def __exit__(self, *_args):
        self.temporary.cleanup()

    def plan(self, profile="production"):
        return RELEASE_GATE.build_plan(
            self.root,
            self.evidence / "agent-eval-results.json",
            profile=profile,
            evidence_root=self.evidence,
            reviewer_key_path=self.key,
            trusted_reviewer_id="reviewer:test",
            trusted_reviewer_key_sha256="sha256:" + "1" * 64,
        )


class ReleaseGateSecurityTest(unittest.TestCase):
    def test_shell_launcher_blocks_sitecustomize_and_forged_argparse(self):
        with tempfile.TemporaryDirectory() as temporary:
            hostile = Path(temporary)
            marker = hostile / "python-startup-ran"
            shell_marker = hostile / "shell-startup-ran"
            (hostile / "sitecustomize.py").write_text(
                "from pathlib import Path\nPath(%r).write_text('site')\n"
                % str(marker),
                encoding="utf-8",
            )
            (hostile / "argparse.py").write_text(
                "from pathlib import Path\nPath(%r).write_text('argparse')\n"
                % str(marker),
                encoding="utf-8",
            )
            startup = hostile / "shell-startup"
            startup.write_text(
                "printf shell > %s\n" % json.dumps(str(shell_marker)),
                encoding="utf-8",
            )
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
            agent = next(
                step for step in payload["steps"]
                if step["id"] == "agent_behavior_evidence"
            )
            duration_index = agent["command"].index("--max-run-duration-hours")
            self.assertEqual("24", agent["command"][duration_index + 1])
            self.assertFalse(marker.exists())
            self.assertFalse(shell_marker.exists())

        maximum_plan = RELEASE_GATE.build_plan(
            REPOSITORY_ROOT, Path("/tmp/agent-eval-results.json"),
            max_run_duration_hours=168,
        )
        maximum_agent = next(
            step for step in maximum_plan
            if step.identifier == "agent_behavior_evidence"
        )
        maximum_index = maximum_agent.command.index("--max-run-duration-hours")
        self.assertEqual("168", maximum_agent.command[maximum_index + 1])
        with self.assertRaises(ValueError):
            RELEASE_GATE.build_plan(
                REPOSITORY_ROOT, Path("/tmp/agent-eval-results.json"),
                max_run_duration_hours=169,
            )

    def test_actual_installer_ignores_fake_path_bash_env_and_supports_spaces(self):
        with CleanReleaseRepository() as repository:
            fake_bin = repository.base / "fake bin"
            fake_bin.mkdir()
            marker = repository.base / "environment-was-executed"
            fake_tool = fake_bin / "git"
            fake_tool.write_text(
                "#!/bin/sh\nprintf fake > %s\nexit 99\n" % json.dumps(str(marker)),
                encoding="utf-8",
            )
            fake_tool.chmod(fake_tool.stat().st_mode | stat.S_IXUSR)
            shutil.copy2(str(fake_tool), str(fake_bin / "bash"))
            bash_env = repository.base / "bash env"
            bash_env.write_text(
                "printf bash-env > %s\n" % json.dumps(str(marker)), encoding="utf-8"
            )
            hostile = {
                "PATH": str(fake_bin),
                "PYTHONPATH": str(fake_bin),
                "PYTHONHOME": str(fake_bin),
                "BASH_ENV": str(bash_env),
                "ENV": str(bash_env),
                "GIT_DIR": str(fake_bin),
            }
            with mock.patch.dict(os.environ, hostile, clear=False):
                preflight = RELEASE_GATE._release_preflight_check(repository.root)
                result = RELEASE_GATE._installer_check(repository.root)

            self.assertEqual(0, preflight.returncode, preflight.stderr)
            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            self.assertFalse(marker.exists())

    def test_truncated_rc_as_production_and_substituted_commands_are_rejected(self):
        with CleanReleaseRepository() as repository:
            production = repository.plan("production")
            rc = repository.plan("rc")
            cases = {
                "truncated": production[:1],
                "rc_as_production": rc,
                "substituted": tuple(
                    replace(step, command=(sys.executable, "-c", "raise SystemExit(0)"))
                    if step.identifier == "linker_repository_validation" else step
                    for step in production
                ),
            }
            for name, steps in cases.items():
                with self.subTest(name=name):
                    payload, exit_code = RELEASE_GATE.run_plan(
                        repository.root, steps, profile="production"
                    )
                    self.assertEqual(2, exit_code, payload)
                    self.assertIn(
                        "release_plan_invalid",
                        {item["code"] for item in payload["diagnostics"]},
                    )

    def test_rc_zero_requires_valid_pass_json_envelope(self):
        for stdout in ("", "not-json", json.dumps({
            "schema_version": 1, "status": "fail", "diagnostics": [],
            "summary": {"errors": 0},
        })):
            with self.subTest(stdout=stdout):
                result = RELEASE_GATE._validated_pass_envelope(
                    RELEASE_GATE.CommandResult(0, stdout, ""), "validator"
                )
                self.assertEqual(2, result.returncode)

        valid = RELEASE_GATE._validated_pass_envelope(
            RELEASE_GATE.CommandResult(0, pass_envelope(), ""), "validator"
        )
        self.assertEqual(0, valid.returncode)

        with CleanReleaseRepository() as repository:
            plan = repository.plan("production")
            kinds = {
                item.identifier: item.kind for item in plan
                if item.identifier in {
                    "linker_repository_validation", "agent_behavior_evidence"
                }
            }
        self.assertEqual({
            "linker_repository_validation": "json_command",
            "agent_behavior_evidence": "json_command",
        }, kinds)

    def test_envelopes_reject_duplicates_unknown_fields_and_wrong_contracts(self):
        author = json.loads(pass_envelope())
        cases = (
            ('{"schema_version":1,"status":"fail","status":"pass",'
             '"diagnostics":[],"summary":{"errors":0,"warnings":0}}', "author"),
            ('{"schema_version":1,"status":"pass","diagnostics":[],'
             '"summary":{"errors":1,"errors":0,"warnings":0}}', "author"),
            (json.dumps(dict(author, unknown=True)), "author"),
            (json.dumps(dict(author, schema_version=True)), "author"),
            (pass_envelope(), "linker"),
            (pass_envelope(), "agent"),
        )
        for stdout, kind in cases:
            with self.subTest(kind=kind, stdout=stdout):
                result = RELEASE_GATE._validated_pass_envelope(
                    RELEASE_GATE.CommandResult(0, stdout, ""), "validator", kind
                )
                self.assertEqual(2, result.returncode)

        self.assertEqual(0, RELEASE_GATE._validated_pass_envelope(
            RELEASE_GATE.CommandResult(0, pass_envelope("linker"), ""),
            "linker", "linker",
        ).returncode)
        self.assertEqual(0, RELEASE_GATE._validated_pass_envelope(
            RELEASE_GATE.CommandResult(0, pass_envelope("agent"), ""),
            "agent", "agent",
        ).returncode)

    def test_readiness_state_and_install_manifest_reject_duplicate_keys(self):
        readiness = (
            '{"schema_version":2,"status":"pass","diagnostics":[],'
            '"summary":{"errors":0,"warnings":0},"cache_status":"refreshed",'
            '"scope":"docs","freshness_digest":"sha256:x","complete":true,'
            '"coverage":{"path_digest":"sha256:x","discovered":1,"parsed":1,'
            '"skipped":1,"skipped":0,"skipped_sources":[]},"owners":[],"refs":[],'
            '"typed_edges":null,"dependency_evaluations":[],"trace":[]}'
        )
        with mock.patch.object(
            RELEASE_GATE, "_subprocess_executor",
            return_value=RELEASE_GATE.CommandResult(0, readiness, ""),
        ):
            result = RELEASE_GATE._docs_readiness_check(REPOSITORY_ROOT)
        self.assertEqual(2, result.returncode)

        malformed_readiness = {
            "schema_version": 2,
            "status": "pass",
            "diagnostics": [],
            "summary": {"errors": 9, "warnings": 0},
            "cache_status": "refreshed",
            "scope": "docs",
            "freshness_digest": "sha256:" + "0" * 64,
            "complete": True,
            "coverage": {
                "path_digest": "sha256:" + "0" * 64,
                "discovered": 1,
                "parsed": 1,
                "skipped": 0,
                "skipped_sources": [],
            },
            "owners": [],
            "refs": [],
            "typed_edges": None,
            "dependency_evaluations": [],
            "trace": [{"lane": "reader", "operation": "context_readiness"}],
            "unexpected": True,
        }
        with mock.patch.object(
            RELEASE_GATE, "_subprocess_executor",
            return_value=RELEASE_GATE.CommandResult(
                0, json.dumps(malformed_readiness), ""
            ),
        ):
            result = RELEASE_GATE._docs_readiness_check(REPOSITORY_ROOT)
        self.assertEqual(2, result.returncode)

        malformed_linker = json.loads(pass_envelope("linker"))
        malformed_linker["coverage"]["counts"]["skipped"] = 1
        malformed_linker["coverage"]["skipped_sources"] = ["not-a-path-record"]
        result = RELEASE_GATE._validated_pass_envelope(
            RELEASE_GATE.CommandResult(0, json.dumps(malformed_linker), ""),
            "linker", "linker",
        )
        self.assertEqual(2, result.returncode)

        duplicate_state = RELEASE_GATE.CommandResult(
            0,
            '{"repository_head":"%s","repository_head":"%s",'
            '"repository_tree":"%s"}' % ("a" * 40, "b" * 40, "c" * 40),
            "",
        )
        self.assertIsNone(RELEASE_GATE._release_state_from_result(duplicate_state))

        with CleanReleaseRepository() as repository:
            destination = repository.base / "installed skills"
            destination.mkdir()
            version = (repository.root / "VERSION").read_text(encoding="utf-8").strip()
            head = RELEASE_GATE._canonical_head(repository.root)
            manifest = (
                '{"schema_version":1,"package_version":%s,"source_commit":%s,'
                '"source_dirty":true,"source_dirty":false,"skills":%s}'
                % (json.dumps(version), json.dumps(head),
                   json.dumps(list(RELEASE_GATE.SKILL_NAMES)))
            )
            (destination / ".keystone-install.json").write_text(
                manifest, encoding="utf-8"
            )
            error = RELEASE_GATE._validate_install_manifest(
                repository.root, destination
            )
        self.assertIn("duplicate JSON key", error or "")

    def test_current_and_historical_finalization_reject_malformed_rc_zero(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            context = root / "00_docs" / "key-context-map.md"
            manifest = (
                root / "00_docs" / "works" / "r010-release"
                / "key-finalization-manifest.json"
            )
            runner = (
                root / "skills" / "keystone-author" / "scripts"
                / "run_finalization_validation.py"
            )
            for path in (context, manifest, runner):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}", encoding="utf-8")
            context.write_text(
                "---\nglobal_state:\n  active_round: none\n"
                "  latest_accepted_round: R010\n---\n",
                encoding="utf-8",
            )
            malformed = RELEASE_GATE.CommandResult(0, "not-json", "")
            with mock.patch.object(
                RELEASE_GATE, "_subprocess_executor", return_value=malformed
            ):
                current = RELEASE_GATE._current_finalization_check(root)
            self.assertEqual(2, current.returncode)

            def extract(_archive, destination):
                for directory in (
                    "r008-skill-graph-traceability",
                    "r009-coordinator-keystone-closure",
                ):
                    path = (
                        destination / "00_docs" / "works" / directory
                        / "key-finalization-manifest.json"
                    )
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("{}", encoding="utf-8")

            archive_ok = RELEASE_GATE.CommandResult(0, "", "")
            responses = iter((archive_ok, malformed, malformed))
            with mock.patch.object(
                RELEASE_GATE, "_subprocess_executor",
                side_effect=lambda *_args: next(responses),
            ), mock.patch.object(
                RELEASE_GATE, "_safe_extract_archive", side_effect=extract,
            ), mock.patch.object(
                RELEASE_GATE, "_trusted_tool", return_value=RELEASE_GATE.TRUSTED_GIT,
            ):
                historical = RELEASE_GATE._historical_finalization_check(root)
            self.assertEqual(2, historical.returncode)

    def test_postflight_detects_worktree_or_subject_generation_change(self):
        with CleanReleaseRepository() as repository:
            plan = repository.plan("rc")
            mutated = []

            def executor(_argv, _cwd, environment):
                self.assertEqual(RELEASE_GATE.TRUSTED_PATH, environment["PATH"])
                for name in ("PYTHONHOME", "BASH_ENV", "ENV", "GIT_DIR"):
                    self.assertNotIn(name, environment)
                if not mutated:
                    (repository.root / "VERSION").write_text("changed\n", encoding="utf-8")
                    mutated.append(True)
                kind = (
                    "linker" if "validate_graph.py" in " ".join(_argv)
                    else "agent" if "validate_agent_evals.py" in " ".join(_argv)
                    else "author"
                )
                return RELEASE_GATE.CommandResult(0, pass_envelope(kind), "")

            passing_checker = lambda _root: RELEASE_GATE.CommandResult(0, "", "")
            payload, exit_code = RELEASE_GATE.run_plan(
                repository.root,
                plan,
                profile="rc",
                executor=executor,
                installer_checker=lambda _root: RELEASE_GATE.CommandResult(0, "", ""),
                internal_checkers={
                    "compileall": passing_checker,
                    "docs_readiness": passing_checker,
                    "repository_readiness": passing_checker,
                    "historical_finalization": passing_checker,
                },
            )

            self.assertEqual(1, exit_code, payload)
            postflight = next(
                item for item in payload["steps"]
                if item["id"] == "release_postflight"
            )
            self.assertEqual("fail", postflight["status"])

    def test_git_diff_return_codes_distinguish_findings_from_execution_errors(self):
        root = Path("/tmp/release-gate-return-code-fixture")

        def responses(diff_returncode):
            return iter((
                RELEASE_GATE.CommandResult(0, str(root) + "\n", ""),
                RELEASE_GATE.CommandResult(0, "a" * 40 + "\n", ""),
                RELEASE_GATE.CommandResult(0, "", ""),
                RELEASE_GATE.CommandResult(diff_returncode, "", "diff failed"),
            ))

        for child_code, expected in ((1, 1), (2, 2), (128, 2)):
            with self.subTest(child_code=child_code):
                values = responses(child_code)
                with mock.patch.object(
                    RELEASE_GATE, "_subprocess_executor",
                    side_effect=lambda *_args: next(values),
                ), mock.patch.object(
                    RELEASE_GATE, "_trusted_tool",
                    return_value=RELEASE_GATE.TRUSTED_GIT,
                ):
                    result = RELEASE_GATE._release_preflight_check(root)
                self.assertEqual(expected, result.returncode)


if __name__ == "__main__":
    unittest.main()
