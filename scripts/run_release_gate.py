#!/usr/bin/env python3
"""Run Keystone's canonical lean release verification plan."""

from __future__ import annotations

import argparse
import compileall
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Mapping, Optional, Sequence, Tuple


TRUSTED_PATH = "/usr/bin:/bin"
TRUSTED_GIT = Path("/usr/bin/git")
TRUSTED_BASH = Path("/bin/bash")
SKILL_NAMES = (
    "keystone-init",
    "keystone-reader",
    "keystone-author",
    "keystone-clarify",
    "keystone-linker",
    "keystone-coordinator",
    "keystone-ideas",
)


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class ReleaseStep:
    identifier: str
    kind: str
    command: Tuple[str, ...]


Executor = Callable[[Sequence[str], Path, Mapping[str, str]], CommandResult]
Checker = Callable[[Path], CommandResult]


def _clean_environment(home: Optional[Path] = None) -> Dict[str, str]:
    environment = {
        "PATH": TRUSTED_PATH,
        "LANG": "C",
        "LC_ALL": "C",
        "HOME": str(home if home is not None else Path("/var/empty")),
        "TMPDIR": tempfile.gettempdir(),
    }
    return environment


def _subprocess_executor(
    argv: Sequence[str], cwd: Path, environment: Mapping[str, str]
) -> CommandResult:
    process = subprocess.run(
        tuple(argv), cwd=str(cwd), env=dict(environment),
        capture_output=True, text=True, check=False,
    )
    return CommandResult(process.returncode, process.stdout, process.stderr)


def _json_loads_strict(value: str):
    def object_pairs(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: %s" % key)
            result[key] = item
        return result

    return json.loads(value, object_pairs_hook=object_pairs)


def _diagnostic(code: str, message: str) -> Dict[str, str]:
    return {"severity": "error", "code": code, "message": message}


def _validated_pass_envelope(
    result: CommandResult, label: str, kind: str = "diagnostic"
) -> CommandResult:
    if result.returncode != 0:
        return result
    try:
        payload = _json_loads_strict(result.stdout)
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        return CommandResult(2, result.stdout, "%s output is not valid JSON: %s" % (label, error))
    if not isinstance(payload, dict):
        return CommandResult(2, result.stdout, "%s output is not an object" % label)
    required = {"schema_version", "status", "diagnostics", "summary"}
    if not required.issubset(payload):
        return CommandResult(2, result.stdout, "%s output is missing diagnostic fields" % label)
    if payload.get("schema_version") != 1 or payload.get("status") != "pass":
        return CommandResult(2, result.stdout, "%s did not emit a pass envelope" % label)
    diagnostics = payload.get("diagnostics")
    summary = payload.get("summary")
    if not isinstance(diagnostics, list) or not isinstance(summary, dict):
        return CommandResult(2, result.stdout, "%s diagnostic envelope is malformed" % label)
    if summary.get("errors") != 0:
        return CommandResult(2, result.stdout, "%s pass envelope reports errors" % label)
    if kind == "linker":
        coverage = payload.get("coverage")
        if not isinstance(coverage, dict) or coverage.get("complete") is not True:
            return CommandResult(2, result.stdout, "%s coverage is incomplete" % label)
    return result


def _git(root: Path, *args: str) -> CommandResult:
    return _subprocess_executor(
        (str(TRUSTED_GIT), "-C", str(root), *args), root, _clean_environment()
    )


def _canonical_head(root: Path) -> str:
    result = _git(root, "rev-parse", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else ""


def _repository_state(root: Path) -> CommandResult:
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return top
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode != 0:
        return head
    tree = _git(root, "write-tree")
    if tree.returncode != 0:
        return tree
    status = _git(root, "status", "--porcelain")
    if status.returncode != 0:
        return status
    payload = {
        "repository_root": top.stdout.strip(),
        "repository_head": head.stdout.strip(),
        "repository_tree": tree.stdout.strip(),
        "clean": not bool(status.stdout.strip()),
    }
    return CommandResult(0, json.dumps(payload, sort_keys=True), "")


def _release_state_from_result(result: CommandResult):
    if result.returncode != 0:
        return None
    try:
        payload = _json_loads_strict(result.stdout)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    required = {"repository_root", "repository_head", "repository_tree", "clean"}
    if set(payload) != required or payload.get("clean") is not True:
        return None
    return payload


def _release_preflight_check(root: Path) -> CommandResult:
    result = _repository_state(root)
    state = _release_state_from_result(result)
    if state is None:
        if result.returncode != 0:
            return CommandResult(2, result.stdout, result.stderr or "release state unavailable")
        return CommandResult(1, result.stdout, "release requires a clean canonical repository state")
    return result


def _release_postflight_check(root: Path, expected: Mapping[str, object]) -> CommandResult:
    result = _repository_state(root)
    current = _release_state_from_result(result)
    if current is None:
        return CommandResult(1 if result.returncode == 0 else 2, result.stdout, result.stderr)
    if dict(current) != dict(expected):
        return CommandResult(1, result.stdout, "repository state changed during release verification")
    return result


def _compileall_check(root: Path) -> CommandResult:
    with tempfile.TemporaryDirectory(prefix="keystone-compileall-") as temporary:
        previous_prefix = sys.pycache_prefix
        sys.pycache_prefix = temporary
        try:
            ok = compileall.compile_dir(
                str(root / "scripts"), quiet=1, force=True,
                legacy=False, optimize=0, workers=1,
            )
            for package in ("keystone-author", "keystone-coordinator", "keystone-linker", "keystone-ideas"):
                ok = compileall.compile_dir(
                    str(root / "skills" / package / "scripts"), quiet=1,
                    force=True, legacy=False, optimize=0, workers=1,
                ) and ok
        finally:
            sys.pycache_prefix = previous_prefix
    return CommandResult(0 if ok else 1, "", "" if ok else "compileall failed")


def _readiness_check(root: Path, scope: str) -> CommandResult:
    scripts = root / "skills" / "keystone-linker" / "scripts"
    with tempfile.TemporaryDirectory(prefix="keystone-readiness-gate-") as temporary:
        request = {
            "repository_root": str(root),
            "cache_path": str(Path(temporary) / "reference-index.sqlite3"),
            "initiator": "linker" if scope == "repository" else "reader",
            "artifact_context": scope == "repository",
        }
        result = _subprocess_executor(
            (sys.executable, "-m", "graph_runtime.readiness_cli",
             "--request-json", json.dumps(request, sort_keys=True),
             "--response-json", "-"),
            scripts, _clean_environment(),
        )
    if result.returncode != 0:
        return result
    try:
        payload = _json_loads_strict(result.stdout)
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        return CommandResult(2, result.stdout, "readiness output is invalid: %s" % error)
    if (
        not isinstance(payload, dict)
        or payload.get("status") != "pass"
        or payload.get("scope") != scope
        or payload.get("complete") is not True
    ):
        return CommandResult(1, result.stdout, "readiness did not pass")
    coverage = payload.get("coverage")
    if (
        not isinstance(coverage, dict)
        or coverage.get("skipped") != 0
        or coverage.get("discovered") != coverage.get("parsed")
    ):
        return CommandResult(1, result.stdout, "readiness coverage is incomplete")
    return result


def _docs_readiness_check(root: Path) -> CommandResult:
    return _readiness_check(root, "docs")


def _repository_readiness_check(root: Path) -> CommandResult:
    return _readiness_check(root, "repository")


def _work_state_check(root: Path) -> CommandResult:
    result = _subprocess_executor(
        (sys.executable, "-I", str(root / "scripts" / "work_state_runtime.py"),
         "--root", str(root)), root, _clean_environment(),
    )
    return _validated_pass_envelope(result, "Work State")


def _validate_install_manifest(root: Path, destination: Path) -> Optional[str]:
    path = destination / ".keystone-install.json"
    try:
        payload = _json_loads_strict(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return str(error)
    expected = {
        "schema_version": 1,
        "package_version": (root / "VERSION").read_text(encoding="utf-8").strip(),
        "source_commit": _canonical_head(root),
        "source_dirty": False,
        "skills": list(SKILL_NAMES),
    }
    if payload != expected:
        return "installed manifest does not match release source"
    return None


def _installer_check(root: Path) -> CommandResult:
    with tempfile.TemporaryDirectory(prefix="keystone-installer-gate-") as temporary:
        home = Path(temporary) / "codex-home"
        environment = _clean_environment(Path(temporary))
        environment["CODEX_HOME"] = str(home)
        command = (str(TRUSTED_BASH), str(root / "reinstall-local-keystone-skills.sh"))
        first = _subprocess_executor(command, root, environment)
        if first.returncode != 0:
            return first
        error = _validate_install_manifest(root, home / "skills")
        if error:
            return CommandResult(1, first.stdout, error)

        manifest_before = (home / "skills" / ".keystone-install.json").read_bytes()
        rollback_environment = dict(environment)
        rollback_environment["_KEYSTONE_TEST_BREAK_AFTER_SWAP"] = "keystone-linker"
        rollback = _subprocess_executor(command, root, rollback_environment)
        if rollback.returncode == 0:
            return CommandResult(1, rollback.stdout, "installer rollback probe unexpectedly passed")
        if (home / "skills" / ".keystone-install.json").read_bytes() != manifest_before:
            return CommandResult(1, rollback.stdout, "installer rollback did not restore manifest")
        error = _validate_install_manifest(root, home / "skills")
        if error:
            return CommandResult(1, rollback.stdout, "installer rollback invalid: %s" % error)
        return CommandResult(0, first.stdout, "")


def _python() -> str:
    return sys.executable


def build_plan(root: Path, *, profile: str = "production") -> Tuple[ReleaseStep, ...]:
    root = Path(root).resolve()
    if profile not in {"rc", "production"}:
        raise ValueError("profile must be rc or production")
    python = _python()
    return (
        ReleaseStep("release_preflight", "preflight", ("<internal>", "preflight")),
        ReleaseStep("author_package_tests", "command", (python, "-m", "unittest", "discover", "-s", "skills/keystone-author/tests", "-p", "test_*.py")),
        ReleaseStep("coordinator_package_tests", "command", (python, "-m", "unittest", "discover", "-s", "skills/keystone-coordinator/tests", "-p", "test_*.py")),
        ReleaseStep("linker_package_tests", "command", (python, "-m", "unittest", "discover", "-s", "skills/keystone-linker/tests", "-p", "test_*.py")),
        ReleaseStep("ideas_package_tests", "command", (python, "-m", "unittest", "discover", "-s", "skills/keystone-ideas/tests", "-p", "test_*.py")),
        ReleaseStep("shared_skills_tests", "command", (python, "-m", "unittest", "discover", "-s", "skills/tests", "-p", "test_*.py")),
        ReleaseStep("compileall", "compileall", ("<internal>", "compileall")),
        ReleaseStep("docs_readiness", "docs_readiness", ("<internal>", "readiness", "docs")),
        ReleaseStep("repository_readiness", "repository_readiness", ("<internal>", "readiness", "repository")),
        ReleaseStep("work_state_runtime", "work_state", ("<internal>", "work_state")),
        ReleaseStep("linker_repository_validation", "json_command", (python, "-I", str(root / "skills/keystone-linker/scripts/validate_graph.py"), "--root", str(root), "--scope", "repository")),
        ReleaseStep("installer_staging_parity_rollback", "installer", ("<internal>", "installer")),
        ReleaseStep("release_postflight", "postflight", ("<internal>", "postflight")),
    )


def _canonical_plan_error(root: Path, steps: Sequence[ReleaseStep], profile: str) -> Optional[str]:
    try:
        expected = build_plan(root, profile=profile)
    except ValueError as error:
        return str(error)
    if tuple(steps) != expected:
        return "release plan differs from the canonical %s plan" % profile
    return None


def _step_record(step: ReleaseStep, result: CommandResult) -> Dict[str, object]:
    return {
        "id": step.identifier,
        "kind": step.kind,
        "command": list(step.command),
        "status": "pass" if result.returncode == 0 else ("fail" if result.returncode == 1 else "error"),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_plan(
    root: Path,
    steps: Sequence[ReleaseStep],
    *,
    profile: str = "production",
    executor: Executor = _subprocess_executor,
    installer_checker: Checker = _installer_check,
    internal_checkers: Optional[Mapping[str, Checker]] = None,
):
    root = Path(root).resolve()
    error = _canonical_plan_error(root, steps, profile)
    if error:
        return ({
            "schema_version": 1,
            "status": "error",
            "profile": profile,
            "steps": [],
            "diagnostics": [_diagnostic("release_plan_invalid", error)],
        }, 2)

    checkers: Dict[str, Checker] = {
        "compileall": _compileall_check,
        "docs_readiness": _docs_readiness_check,
        "repository_readiness": _repository_readiness_check,
        "work_state": _work_state_check,
    }
    if internal_checkers:
        checkers.update(internal_checkers)

    records = []
    preflight_state = None
    final_code = 0
    environment = _clean_environment()
    for step in steps:
        if step.kind == "preflight":
            result = _release_preflight_check(root)
            preflight_state = _release_state_from_result(result)
        elif step.kind == "postflight":
            result = (
                _release_postflight_check(root, preflight_state)
                if preflight_state is not None
                else CommandResult(2, "", "preflight state is unavailable")
            )
        elif step.kind == "installer":
            result = installer_checker(root)
        elif step.kind in checkers:
            result = checkers[step.kind](root)
        else:
            result = executor(step.command, root, environment)
            if step.kind == "json_command":
                result = _validated_pass_envelope(result, step.identifier, "linker")
        records.append(_step_record(step, result))
        if result.returncode != 0:
            final_code = 2 if result.returncode not in {0, 1} else max(final_code, 1)
            break

    status = "pass" if final_code == 0 else ("fail" if final_code == 1 else "error")
    payload = {
        "schema_version": 1,
        "status": status,
        "profile": profile,
        "steps": records,
        "diagnostics": [],
    }
    return payload, final_code


def _listed_payload(root: Path, profile: str) -> Dict[str, object]:
    return {
        "schema_version": 1,
        "status": "listed",
        "profile": profile,
        "steps": [
            {"id": step.identifier, "kind": step.kind, "command": list(step.command)}
            for step in build_plan(root, profile=profile)
        ],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--profile", choices=("rc", "production"), default="production")
    parser.add_argument("--list", action="store_true", help="List the canonical plan without running it")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.list:
        print(json.dumps(_listed_payload(root, args.profile), sort_keys=True))
        return 0
    payload, returncode = run_plan(root, build_plan(root, profile=args.profile), profile=args.profile)
    print(json.dumps(payload, sort_keys=True))
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
