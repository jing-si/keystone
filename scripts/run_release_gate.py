#!/usr/bin/env python3
"""Run the deterministic, fail-closed local Keystone release gate."""

import os
import sys


if __name__ == "__main__" and not sys.flags.isolated:
    _bootstrap_environment = {
        name: value for name, value in os.environ.items()
        if name.startswith("KEYSTONE_AGENT_EVAL_")
    }
    _bootstrap_environment.update({
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    })
    os.execve(
        os.path.abspath(sys.executable),
        [os.path.abspath(sys.executable), "-I", os.path.abspath(__file__)]
        + sys.argv[1:],
        _bootstrap_environment,
    )


import argparse
import hashlib
import json
import re
import stat
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SCHEMA_VERSION = 1
COMMAND_TIMEOUT_SECONDS = 600
REVIEW_BASELINE_COMMIT = "d36feb79666f53cacd44f01a79dda8f14d672bb6"
SKILL_NAMES = (
    "keystone-init",
    "keystone-reader",
    "keystone-author",
    "keystone-clarify",
    "keystone-linker",
    "keystone-coordinator",
)
HEAD_PATTERN = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_PATHS = ("VERSION", "reinstall-local-keystone-skills.sh", "scripts", "skills")
DEFAULT_MAX_AGE_HOURS = 168
DEFAULT_MAX_RUN_DURATION_HOURS = 24
MAX_MAX_RUN_DURATION_HOURS = 168
TRUSTED_GIT = Path("/usr/bin/git")
TRUSTED_BASH = Path("/bin/bash")
TRUSTED_PATH = "/usr/bin:/bin"
PASS_ENVELOPE_FIELDS = {
    "author": {"schema_version", "status", "diagnostics", "summary"},
    "linker": {"schema_version", "status", "diagnostics", "summary", "coverage"},
    "agent": {"schema_version", "status", "diagnostics", "summary", "suite_id"},
}
GRAPH_COVERAGE_FIELDS = {
    "mode", "complete", "path_digest", "discovered_sources", "parsed_sources",
    "omitted_sources", "declared_only_sources", "skipped_sources", "counts",
}
GRAPH_COVERAGE_COUNT_FIELDS = {
    "discovered", "parsed", "omitted", "declared_only", "skipped",
}
READINESS_FIELDS = {
    "schema_version", "status", "diagnostics", "summary", "cache_status",
    "scope", "freshness_digest", "complete", "coverage", "owners", "refs",
    "typed_edges", "dependency_evaluations", "trace",
}
READINESS_COVERAGE_FIELDS = {
    "path_digest", "discovered", "parsed", "skipped", "skipped_sources",
}


class DuplicateJsonKey(ValueError):
    pass


def _strict_json_loads(value: str):
    def object_pairs(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise DuplicateJsonKey("duplicate JSON key: %s" % key)
            result[key] = item
        return result

    def reject_constant(value):
        raise ValueError("non-canonical JSON constant: %s" % value)

    return json.loads(
        value, object_pairs_hook=object_pairs, parse_constant=reject_constant
    )


@dataclass(frozen=True)
class GateStep:
    identifier: str
    kind: str
    command: Tuple[str, ...]
    environment: Tuple[Tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


Executor = Callable[[Sequence[str], Path, Mapping[str, str]], CommandResult]
InstallerChecker = Callable[[Path], Optional[CommandResult]]
InternalChecker = Callable[[Path], CommandResult]


def _controlled_python_path(root: Path) -> str:
    return os.pathsep.join(
        str(path) for path in sorted((root / "skills").glob("keystone-*/scripts"))
    )


def _sanitized_environment(
    root: Path, *, cache_root: Optional[Path] = None,
    python_path: Optional[str] = None,
) -> Dict[str, str]:
    environment = {
        "HOME": "/var/empty",
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": TRUSTED_PATH,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": (
            _controlled_python_path(root) if python_path is None else python_path
        ),
        "PYTHONUTF8": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    if cache_root is not None:
        environment["PYTHONPYCACHEPREFIX"] = str(cache_root / "pycache")
    return environment


def _trusted_tool(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_file() or not os.access(str(path), os.X_OK):
        raise ValueError("trusted %s executable is unavailable" % label)
    return path.resolve()


def _subprocess_executor(
    argv: Sequence[str], cwd: Path, env: Mapping[str, str]
) -> CommandResult:
    try:
        process = subprocess.run(
            list(argv), cwd=str(cwd), env=dict(env), capture_output=True, text=True,
            check=False, timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""
        return CommandResult(2, stdout, stderr + "command timed out")
    return CommandResult(process.returncode, process.stdout, process.stderr)


def _validated_pass_envelope(
    result: CommandResult, label: str, envelope_kind: str = "author"
) -> CommandResult:
    if result.returncode != 0:
        return result
    try:
        payload = _strict_json_loads(result.stdout)
    except (TypeError, ValueError, json.JSONDecodeError):
        return CommandResult(2, result.stdout, "%s output is not JSON" % label)
    if not isinstance(payload, dict):
        return CommandResult(2, result.stdout, "%s output is not an object" % label)
    expected_fields = PASS_ENVELOPE_FIELDS.get(envelope_kind)
    if expected_fields is None or set(payload) != expected_fields:
        return CommandResult(2, result.stdout, "%s top-level fields are invalid" % label)
    diagnostics = payload.get("diagnostics")
    summary = payload.get("summary")
    diagnostics_valid = (
        isinstance(diagnostics, list)
        and all(
            isinstance(item, dict)
            and {"severity", "code", "message"}.issubset(item)
            and set(item).issubset({"severity", "code", "message", "path"})
            and item.get("severity") in {"error", "warning"}
            and isinstance(item.get("code"), str)
            and isinstance(item.get("message"), str)
            and ("path" not in item or isinstance(item["path"], str))
            for item in diagnostics
        )
    )
    error_count = (
        sum(item["severity"] == "error" for item in diagnostics)
        if diagnostics_valid else -1
    )
    expected_summary = (
        {"errors", "scenarios_required"}
        if envelope_kind == "agent" else {"errors", "warnings"}
    )
    counts_valid = (
        isinstance(summary, dict)
        and set(summary) == expected_summary
        and all(type(summary.get(field)) is int for field in expected_summary)
        and summary.get("errors") == 0
        and (
            summary.get("scenarios_required") == 12
            if envelope_kind == "agent" else summary.get("warnings") == 0
        )
    )
    if (type(payload.get("schema_version")) is not int
            or payload.get("schema_version") != SCHEMA_VERSION
            or payload.get("status") != "pass"
            or not diagnostics_valid
            or diagnostics
            or not counts_valid
            or error_count != 0
            or (envelope_kind == "linker"
                and not _valid_repository_graph_coverage(payload.get("coverage")))
            or (envelope_kind == "agent"
                and payload.get("suite_id") != "r010-agent-behavior")):
        return CommandResult(2, result.stdout, "%s pass envelope is invalid" % label)
    return result


def _canonical_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and bool(item) for item in value)
        and value == sorted(set(value))
    )


def _valid_repository_graph_coverage(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != GRAPH_COVERAGE_FIELDS:
        return False
    counts = value.get("counts")
    if (
        not isinstance(counts, dict)
        or set(counts) != GRAPH_COVERAGE_COUNT_FIELDS
        or not all(type(counts.get(field)) is int and counts[field] >= 0
                   for field in GRAPH_COVERAGE_COUNT_FIELDS)
    ):
        return False
    list_fields = {
        "discovered_sources": "discovered",
        "parsed_sources": "parsed",
        "omitted_sources": "omitted",
        "declared_only_sources": "declared_only",
        "skipped_sources": "skipped",
    }
    if any(
        not _canonical_string_list(value.get(field))
        or len(value[field]) != counts[count_field]
        for field, count_field in list_fields.items()
    ):
        return False
    return (
        value.get("mode") == "discovered"
        and value.get("complete") is True
        and isinstance(value.get("path_digest"), str)
        and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", value["path_digest"]))
        and counts["discovered"] == counts["parsed"]
        and value["discovered_sources"] == value["parsed_sources"]
        and counts["omitted"] == 0
        and counts["declared_only"] == 0
        and counts["skipped"] == 0
    )


def _valid_diagnostics_and_summary(payload: Mapping[str, object]) -> bool:
    diagnostics = payload.get("diagnostics")
    summary = payload.get("summary")
    if not isinstance(diagnostics, list) or not all(
        isinstance(item, dict)
        and {"severity", "code", "message"}.issubset(item)
        and set(item).issubset({"severity", "code", "message", "path"})
        and item.get("severity") in {"error", "warning"}
        and isinstance(item.get("code"), str)
        and isinstance(item.get("message"), str)
        and ("path" not in item or isinstance(item["path"], str))
        for item in diagnostics
    ):
        return False
    if (
        not isinstance(summary, dict)
        or set(summary) != {"errors", "warnings"}
        or any(type(summary.get(field)) is not int for field in summary)
    ):
        return False
    return summary == {
        "errors": sum(item["severity"] == "error" for item in diagnostics),
        "warnings": sum(item["severity"] == "warning" for item in diagnostics),
    }


def _valid_readiness_records(payload: Mapping[str, object]) -> bool:
    owners = payload.get("owners")
    refs = payload.get("refs")
    typed_edges = payload.get("typed_edges")
    dependency_evaluations = payload.get("dependency_evaluations")
    trace = payload.get("trace")
    owner_valid = isinstance(owners, list) and all(
        isinstance(item, dict)
        and set(item) == {"id", "path", "locator"}
        and isinstance(item.get("id"), str)
        and isinstance(item.get("path"), str)
        and (item.get("locator") is None or isinstance(item.get("locator"), str))
        for item in owners
    )
    ref_valid = isinstance(refs, list) and all(
        isinstance(item, dict)
        and set(item) == {"source_id", "target_id", "path", "locator"}
        and all(isinstance(item.get(field), str)
                for field in ("source_id", "target_id", "path"))
        and (item.get("locator") is None or isinstance(item.get("locator"), str))
        for item in refs
    )
    edge_valid = typed_edges is None or (
        isinstance(typed_edges, list)
        and all(
            isinstance(item, dict)
            and set(item) == {"source_id", "relation", "target_id"}
            and all(isinstance(item.get(field), str)
                    for field in ("source_id", "relation", "target_id"))
            for item in typed_edges
        )
    )
    trace_valid = isinstance(trace, list) and bool(trace) and all(
        isinstance(item, dict)
        and set(item) == {"lane", "operation"}
        and isinstance(item.get("lane"), str)
        and isinstance(item.get("operation"), str)
        for item in trace
    )
    dependency_fields = {
        "gate_id", "source", "dependency", "scope", "target_state", "result",
        "blocking", "optional", "origin", "reason", "cycle_events",
    }
    dependency_valid = isinstance(dependency_evaluations, list) and all(
        isinstance(item, dict)
        and set(item) == dependency_fields
        and all(isinstance(item.get(field), str) for field in (
            "gate_id", "source", "dependency", "result", "origin", "reason",
        ))
        and isinstance(item.get("blocking"), bool)
        and isinstance(item.get("optional"), bool)
        and isinstance(item.get("scope"), dict)
        and set(item["scope"]) == {"steps", "work_completion"}
        and isinstance(item["scope"].get("steps"), list)
        and all(isinstance(step, str) for step in item["scope"]["steps"])
        and isinstance(item["scope"].get("work_completion"), bool)
        and isinstance(item.get("target_state"), dict)
        and set(item["target_state"]) == {"work_status", "approval_state"}
        and all(
            item["target_state"].get(field) is None
            or isinstance(item["target_state"].get(field), str)
            for field in ("work_status", "approval_state")
        )
        and isinstance(item.get("cycle_events"), list)
        and all(isinstance(event, str) for event in item["cycle_events"])
        for item in dependency_evaluations
    )
    return owner_valid and ref_valid and edge_valid and trace_valid and dependency_valid


def _readiness_envelope_valid(payload: object) -> bool:
    if not isinstance(payload, dict) or set(payload) != READINESS_FIELDS:
        return False
    coverage = payload.get("coverage")
    if (
        not isinstance(coverage, dict)
        or set(coverage) != READINESS_COVERAGE_FIELDS
        or type(coverage.get("discovered")) is not int
        or type(coverage.get("parsed")) is not int
        or type(coverage.get("skipped")) is not int
        or min(coverage["discovered"], coverage["parsed"], coverage["skipped"]) < 0
        or not isinstance(coverage.get("path_digest"), str)
        or not re.fullmatch(r"sha256:[0-9a-f]{64}", coverage["path_digest"])
        or not isinstance(coverage.get("skipped_sources"), list)
        or len(coverage["skipped_sources"]) != coverage["skipped"]
        or not all(
            isinstance(item, dict)
            and set(item) == {"path", "reason"}
            and isinstance(item.get("path"), str)
            and isinstance(item.get("reason"), str)
            for item in coverage["skipped_sources"]
        )
    ):
        return False
    return (
        type(payload.get("schema_version")) is int
        and payload.get("schema_version") == 2
        and payload.get("status") in {"pass", "fail", "error"}
        and payload.get("cache_status") in {"refreshed", "reused", "source_fallback"}
        and payload.get("scope") in {"docs", "repository"}
        and isinstance(payload.get("freshness_digest"), str)
        and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", payload["freshness_digest"]))
        and isinstance(payload.get("complete"), bool)
        and _valid_diagnostics_and_summary(payload)
        and _valid_readiness_records(payload)
    )


def _stream_digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _tree_digest(path: Path) -> str:
    if path.is_symlink() or not path.is_dir():
        raise ValueError("tree must be a regular non-symlink directory: %s" % path)
    digest = hashlib.sha256()
    entries: List[Path] = []
    for candidate in path.rglob("*"):
        relative = candidate.relative_to(path)
        if "__pycache__" in relative.parts or candidate.suffix == ".pyc":
            continue
        if candidate.is_symlink():
            raise ValueError("tree contains a symlink: %s" % relative)
        entries.append(candidate)
    for candidate in sorted(entries, key=lambda item: item.as_posix()):
        relative = candidate.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        if candidate.is_file():
            digest.update(b"file\0" + candidate.read_bytes())
        elif candidate.is_dir():
            digest.update(b"dir\0")
        else:
            raise ValueError("tree contains a non-regular entry: %s" % relative)
    return "sha256:" + digest.hexdigest()


def _canonical_head(root: Path) -> str:
    git = _trusted_tool(TRUSTED_GIT, "git")
    result = _subprocess_executor(
        (str(git), "-C", str(root), "rev-parse", "--verify", "HEAD"), root,
        _sanitized_environment(root),
    )
    head = result.stdout.strip()
    if result.returncode != 0 or not HEAD_PATTERN.fullmatch(head):
        raise ValueError("repository HEAD is unavailable or non-canonical")
    return head


def _canonical_tree(root: Path) -> str:
    git = _trusted_tool(TRUSTED_GIT, "git")
    result = _subprocess_executor(
        (str(git), "-C", str(root), "rev-parse", "--verify", "HEAD^{tree}"),
        root, _sanitized_environment(root),
    )
    tree = result.stdout.strip()
    if result.returncode != 0 or not HEAD_PATTERN.fullmatch(tree):
        raise ValueError("repository tree is unavailable or non-canonical")
    return tree


def _release_package_digest(root: Path) -> str:
    digest = hashlib.sha256()
    entries: List[Tuple[str, Path]] = []
    for name in PACKAGE_PATHS:
        path = root / name
        if path.is_symlink() or not path.exists():
            raise ValueError("release package path is missing or a symlink: %s" % name)
        entries.append((name, path))
        if path.is_dir():
            for child in path.rglob("*"):
                relative = child.relative_to(root)
                if "__pycache__" in relative.parts or child.suffix == ".pyc":
                    continue
                if child.is_symlink():
                    raise ValueError("release package contains a symlink: %s" % relative)
                entries.append((relative.as_posix(), child))
    for relative, path in sorted(entries, key=lambda item: item[0]):
        digest.update(relative.encode("utf-8") + b"\0")
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            digest.update(b"file\0" + path.read_bytes())
        elif stat.S_ISDIR(mode):
            digest.update(b"dir\0")
        else:
            raise ValueError("release package contains a non-regular entry: %s" % relative)
    return "sha256:" + digest.hexdigest()


def _release_preflight_check(root: Path) -> CommandResult:
    try:
        git = _trusted_tool(TRUSTED_GIT, "git")
    except ValueError as error:
        return CommandResult(2, "", str(error))
    environment = _sanitized_environment(root)
    commands = (
        ("top-level", (str(git), "-C", str(root), "rev-parse", "--show-toplevel")),
        ("HEAD", (str(git), "-C", str(root), "rev-parse", "--verify", "HEAD")),
        ("status", (str(git), "-C", str(root), "status", "--porcelain", "--untracked-files=all")),
        ("unstaged diff", (str(git), "-C", str(root), "diff", "--check")),
        ("staged diff", (str(git), "-C", str(root), "diff", "--cached", "--check")),
    )
    outputs = []
    for label, command in commands:
        result = _subprocess_executor(command, root, environment)
        if result.returncode != 0:
            code = 1 if (
                label in {"unstaged diff", "staged diff"}
                and result.returncode == 1
            ) else 2
            return CommandResult(code, result.stdout, "%s preflight failed: %s" % (label, result.stderr))
        outputs.append((label, result.stdout))
    top_level = outputs[0][1].strip()
    try:
        canonical_top = Path(top_level).resolve()
    except (OSError, ValueError):
        return CommandResult(1, "", "git top-level is not canonical")
    if canonical_top != root.resolve():
        return CommandResult(1, "", "git top-level does not equal release root")
    if not HEAD_PATTERN.fullmatch(outputs[1][1].strip()):
        return CommandResult(1, "", "repository HEAD is not a canonical 40-character commit")
    if outputs[2][1]:
        return CommandResult(1, outputs[2][1], "repository is not clean")
    try:
        state = {
            "repository_head": _canonical_head(root),
            "repository_tree": _canonical_tree(root),
        }
    except (OSError, ValueError) as error:
        return CommandResult(2, "", "release state cannot be captured: %s" % error)
    return CommandResult(0, json.dumps(state, sort_keys=True), "")


def _release_state_from_result(result: CommandResult) -> Optional[Dict[str, str]]:
    try:
        value = _strict_json_loads(result.stdout)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    fields = {"repository_head", "repository_tree"}
    if (not isinstance(value, dict) or set(value) != fields
            or not HEAD_PATTERN.fullmatch(str(value.get("repository_head")))
            or not HEAD_PATTERN.fullmatch(str(value.get("repository_tree")))):
        return None
    return value


def _release_postflight_check(
    root: Path, expected_state: Mapping[str, str]
) -> CommandResult:
    result = _release_preflight_check(root)
    if result.returncode != 0:
        return result
    actual = _release_state_from_result(result)
    if actual is None:
        return CommandResult(2, result.stdout, "postflight state is malformed")
    if actual != dict(expected_state):
        return CommandResult(1, result.stdout, "release HEAD or repository tree changed")
    return result


def _isolated_environment(root: Path, cache_root: Path) -> Dict[str, str]:
    return _sanitized_environment(root, cache_root=cache_root)


def _safe_extract_archive(archive_path: Path, destination: Path) -> None:
    with tarfile.open(str(archive_path), "r:") as archive:
        members = archive.getmembers()
        for member in members:
            relative = Path(member.name)
            if (relative.is_absolute() or ".." in relative.parts
                    or not (member.isdir() or member.isfile())):
                raise ValueError("git archive contains an unsafe member")
            target = (destination / relative).resolve()
            target.relative_to(destination.resolve())
        archive.extractall(str(destination), members=members)


def _historical_finalization_check(root: Path) -> CommandResult:
    runner = root / "skills" / "keystone-author" / "scripts" / "run_finalization_validation.py"
    if not runner.is_file():
        return CommandResult(2, "", "current Author package runner is unavailable")
    with tempfile.TemporaryDirectory(prefix="keystone-history-gate-") as temporary:
        temporary_root = Path(temporary)
        archive_path = temporary_root / "baseline.tar"
        archived_root = temporary_root / "repository"
        archived_root.mkdir()
        try:
            git = _trusted_tool(TRUSTED_GIT, "git")
        except ValueError as error:
            return CommandResult(2, "", str(error))
        archive_result = _subprocess_executor(
            (str(git), "-C", str(root),
             "archive", "--format=tar", "--output",
             str(archive_path), REVIEW_BASELINE_COMMIT),
            root,
            _isolated_environment(root, temporary_root),
        )
        if archive_result.returncode != 0:
            return CommandResult(2, archive_result.stdout, archive_result.stderr)
        try:
            _safe_extract_archive(archive_path, archived_root)
        except (OSError, tarfile.TarError, ValueError) as error:
            return CommandResult(2, "", "baseline archive extraction failed: %s" % error)
        outputs = []
        returncodes = []
        for round_id, directory in (
            ("R008", "r008-skill-graph-traceability"),
            ("R009", "r009-coordinator-keystone-closure"),
        ):
            manifest = (archived_root / "00_docs" / "works" / directory
                        / "key-finalization-manifest.json")
            result = _subprocess_executor(
                (sys.executable, str(runner), "--root", str(archived_root),
                 "--manifest", str(manifest)),
                root,
                _isolated_environment(root, temporary_root),
            )
            result = _validated_pass_envelope(
                result, "%s Author finalization" % round_id
            )
            outputs.append("%s stdout:\n%s\n%s stderr:\n%s" % (
                round_id, result.stdout, round_id, result.stderr
            ))
            returncodes.append(result.returncode)
        returncode = 2 if any(code not in {0, 1} for code in returncodes) else (
            1 if any(code == 1 for code in returncodes) else 0
        )
        return CommandResult(returncode, "\n".join(outputs), "")


def _context_rounds(root: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    path = root / "00_docs" / "key-context-map.md"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return None, None, "Context Map is unreadable: %s" % error
    parts = text.split("---", 2)
    if len(parts) != 3:
        return None, None, "Context Map frontmatter is unavailable"
    frontmatter = parts[1]
    active = re.findall(r"(?m)^  active_round:\s*([^\s#]+)\s*$", frontmatter)
    accepted = re.findall(
        r"(?m)^  latest_accepted_round:\s*([^\s#]+)\s*$", frontmatter
    )
    if len(active) != 1 or len(accepted) != 1:
        return None, None, "Context Map round state must be unique and canonical"
    return active[0], accepted[0], None


def _current_finalization_check(root: Path) -> CommandResult:
    active_round, accepted_round, error = _context_rounds(root)
    if error:
        return CommandResult(1, "", error)
    if active_round != "none":
        return CommandResult(
            1, "", "current finalization requires Context Map active_round: none"
        )
    if not isinstance(accepted_round, str) or not re.fullmatch(r"R[0-9]{3}", accepted_round):
        return CommandResult(1, "", "latest_accepted_round is not canonical")
    manifests = sorted((root / "00_docs" / "works").glob(
        "%s-*/key-finalization-manifest.json" % accepted_round.lower()
    ))
    safe_manifests = []
    for path in manifests:
        if path.is_symlink() or not path.is_file():
            continue
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            continue
        safe_manifests.append(path)
    manifests = safe_manifests
    if len(manifests) != 1:
        return CommandResult(
            1, "", "latest_accepted_round must resolve to exactly one finalization manifest"
        )
    runner = root / "skills" / "keystone-author" / "scripts" / "run_finalization_validation.py"
    if not runner.is_file():
        return CommandResult(2, "", "current Author package runner is unavailable")
    with tempfile.TemporaryDirectory(prefix="keystone-current-finalization-") as temporary:
        result = _subprocess_executor(
            (sys.executable, str(runner), "--root", str(root),
             "--manifest", str(manifests[0])),
            root,
            _isolated_environment(root, Path(temporary)),
        )
        return _validated_pass_envelope(result, "current Author finalization")


def _readiness_check(root: Path, repository_scope: bool) -> CommandResult:
    with tempfile.TemporaryDirectory(prefix="keystone-readiness-gate-") as temporary:
        temporary_root = Path(temporary)
        request = {
            "repository_root": str(root),
            "cache_path": str(temporary_root / "reference-index.sqlite3"),
            "initiator": "linker" if repository_scope else "reader",
            "artifact_context": repository_scope,
        }
        result = _subprocess_executor(
            (sys.executable, "-m", "graph_runtime.readiness_cli",
             "--request-json", json.dumps(request, sort_keys=True),
             "--response-json", "-"),
            root,
            _isolated_environment(root, temporary_root),
        )
        if result.returncode != 0:
            return result
        try:
            payload = _strict_json_loads(result.stdout)
        except (TypeError, ValueError, json.JSONDecodeError):
            return CommandResult(2, result.stdout, "readiness output is not JSON")
        if not isinstance(payload, dict):
            return CommandResult(2, result.stdout, "readiness output is not an object")
        if not _readiness_envelope_valid(payload):
            return CommandResult(2, result.stdout, "readiness output schema is invalid")
        coverage = payload.get("coverage")
        expected_scope = "repository" if repository_scope else "docs"
        if (payload.get("status") != "pass"
                or payload.get("scope") != expected_scope
                or payload.get("complete") is not True
                or payload["summary"]["errors"] != 0
                or coverage.get("skipped") != 0
                or coverage.get("discovered") != coverage.get("parsed")):
            return CommandResult(
                1, result.stdout,
                "%s readiness is incomplete or skipped sources" % expected_scope,
            )
        return result


def _docs_readiness_check(root: Path) -> CommandResult:
    return _readiness_check(root, False)


def _repository_readiness_check(root: Path) -> CommandResult:
    return _readiness_check(root, True)


def _compileall_check(root: Path) -> CommandResult:
    with tempfile.TemporaryDirectory(prefix="keystone-compile-gate-") as temporary:
        environment = _sanitized_environment(root, cache_root=Path(temporary))
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        return _subprocess_executor(
            (sys.executable, "-m", "compileall", "-q", "-f",
             str(root / "skills"), str(root / "scripts")),
            root,
            environment,
        )


def _validate_install_manifest(root: Path, destination: Path) -> Optional[str]:
    if destination.is_symlink() or not destination.is_dir():
        return "installed skills root must be a regular non-symlink directory"
    manifest = destination / ".keystone-install.json"
    if manifest.is_symlink() or not manifest.is_file():
        return "installed .keystone-install.json must be a regular non-symlink file"
    try:
        value = _strict_json_loads(manifest.read_text(encoding="utf-8"))
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        head = _canonical_head(root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return "installed manifest cannot be verified: %s" % error
    fields = {
        "schema_version", "package_version", "source_commit", "source_dirty", "skills"
    }
    if not isinstance(value, dict) or set(value) != fields:
        return "installed manifest schema is not exact"
    if type(value.get("schema_version")) is not int or value["schema_version"] != SCHEMA_VERSION:
        return "installed manifest schema_version is invalid"
    if value.get("package_version") != version:
        return "installed manifest package_version differs from VERSION"
    if value.get("source_commit") != head:
        return "installed manifest source_commit differs from current HEAD"
    if value.get("source_dirty") is not False:
        return "installed manifest source_dirty must be false"
    if value.get("skills") != list(SKILL_NAMES):
        return "installed manifest skills must exactly match the release package"
    return None


def _installer_check(root: Path) -> CommandResult:
    installer = root / "reinstall-local-keystone-skills.sh"
    if installer.is_symlink() or not installer.is_file():
        return CommandResult(1, "", "installer is unavailable")
    if (root / "skills").is_symlink() or not (root / "skills").is_dir():
        return CommandResult(1, "", "source skills root must be a regular non-symlink directory")
    try:
        for skill in SKILL_NAMES:
            _tree_digest(root / "skills" / skill)
    except (OSError, ValueError) as error:
        return CommandResult(1, "", "source skill tree is unsafe: %s" % error)
    with tempfile.TemporaryDirectory(prefix="keystone-release-gate-") as temporary:
        codex_home = Path(temporary) / "codex"
        try:
            bash = _trusted_tool(TRUSTED_BASH, "bash")
        except ValueError as error:
            return CommandResult(2, "", str(error))
        environment = _sanitized_environment(root)
        environment["CODEX_HOME"] = str(codex_home)
        first = _subprocess_executor((str(bash), str(installer)), root, environment)
        if first.returncode != 0:
            return first
        destination = codex_home / "skills"
        manifest_error = _validate_install_manifest(root, destination)
        if manifest_error:
            return CommandResult(1, "", manifest_error)
        try:
            for skill in SKILL_NAMES:
                source = root / "skills" / skill
                installed = destination / skill
                if _tree_digest(source) != _tree_digest(installed):
                    return CommandResult(1, "", "installed skill parity failed: %s" % skill)
            before = {skill: _tree_digest(destination / skill) for skill in SKILL_NAMES}
            before[".keystone-install.json"] = _stream_digest(
                (destination / ".keystone-install.json").read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, ValueError) as error:
            return CommandResult(1, "", "installed skill tree is unsafe: %s" % error)
        broken_environment = environment.copy()
        broken_environment["_KEYSTONE_TEST_BREAK_AFTER_SWAP"] = "keystone-linker"
        broken = _subprocess_executor((str(bash), str(installer)), root, broken_environment)
        if broken.returncode == 0:
            return CommandResult(1, broken.stdout, "forced installer failure was not detected")
        try:
            after = {skill: _tree_digest(destination / skill) for skill in SKILL_NAMES}
            after[".keystone-install.json"] = _stream_digest(
                (destination / ".keystone-install.json").read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, ValueError) as error:
            return CommandResult(1, broken.stdout, "installer rollback produced an unsafe tree: %s" % error)
        if after != before:
            return CommandResult(1, broken.stdout, "installer rollback changed installed bytes")
        manifest_error = _validate_install_manifest(root, destination)
        if manifest_error:
            return CommandResult(1, broken.stdout, manifest_error)
        return CommandResult(0, "installer staging, manifest, parity, and rollback verified", "")


def _python_path(root: Path) -> str:
    return _controlled_python_path(root)


def build_plan(
    root: Path, results_path: Path, *, profile: str = "production",
    evidence_root: Optional[Path] = None, reviewer_key_path: Optional[Path] = None,
    trusted_reviewer_id: str = "", trusted_reviewer_key_sha256: str = "",
    max_age_hours: int = DEFAULT_MAX_AGE_HOURS,
    max_run_duration_hours: int = DEFAULT_MAX_RUN_DURATION_HOURS,
) -> Tuple[GateStep, ...]:
    root = Path(root).resolve()
    if profile not in {"rc", "production"}:
        raise ValueError("profile must be rc or production")
    if type(max_age_hours) is not int or not 0 < max_age_hours <= 8760:
        raise ValueError("max_age_hours must be between 1 and 8760")
    if (type(max_run_duration_hours) is not int
            or not 0 < max_run_duration_hours <= MAX_MAX_RUN_DURATION_HOURS):
        raise ValueError(
            "max_run_duration_hours must be between 1 and %d"
            % MAX_MAX_RUN_DURATION_HOURS
        )
    if (trusted_reviewer_key_sha256
            and not re.fullmatch(
                r"sha256:[0-9a-f]{64}", trusted_reviewer_key_sha256
            )):
        raise ValueError("trusted reviewer key digest must be canonical sha256")
    evidence_root = Path(evidence_root) if evidence_root is not None else Path(results_path).parent
    reviewer_key_path = (
        Path(reviewer_key_path) if reviewer_key_path is not None
        else Path.home() / ".codex" / "keystone-agent-eval-reviewer.key"
    )
    python = sys.executable
    steps = [GateStep(
        "release_preflight", "release_preflight",
        ("<internal>", "git-root-head-status-diff-preflight"),
    )]
    for directory in sorted((root / "skills").glob("keystone-*/tests")):
        steps.append(GateStep(
            "package_tests_%s" % directory.parent.name.replace("-", "_"),
            "command",
            (python, "-m", "unittest", "discover", "-s", str(directory),
             "-p", "test_*.py"),
        ))
    steps.append(GateStep(
        "skills_tests", "command",
        (python, "-m", "unittest", "discover", "-s", str(root / "skills" / "tests"),
         "-p", "test_*.py"),
    ))
    linker = root / "skills" / "keystone-linker" / "scripts" / "validate_graph.py"
    coordinator_tests = root / "skills" / "keystone-coordinator" / "tests"
    coordinator_scripts = root / "skills" / "keystone-coordinator" / "scripts"
    steps.extend((
        GateStep(
            "compileall_external_cache", "compileall",
            ("<internal>", "compileall", "--pycache-outside-repository"),
        ),
        GateStep(
            "docs_readiness", "docs_readiness",
            ("<internal>", "graph_runtime.readiness_cli", "--scope", "docs"),
        ),
        GateStep(
            "repository_readiness", "repository_readiness",
            ("<internal>", "graph_runtime.readiness_cli", "--scope", "repository"),
        ),
        GateStep(
            "linker_repository_validation", "json_command",
            (python, str(linker), "--root", str(root), "--scope", "repository"),
        ),
        GateStep(
            "historical_r008_r009_finalization", "historical_finalization",
            ("<internal>", "git-archive", REVIEW_BASELINE_COMMIT,
             "run-current-author-package", "R008", "R009"),
        ),
    ))
    if profile == "production":
        steps.append(GateStep(
            "current_repository_finalization", "current_finalization",
            ("<internal>", "require-active-round-none",
             "run-current-author-package", "latest-accepted-round"),
        ))
    steps.extend((
        GateStep(
            "coordinator_actual_state_v2", "command",
            (python, "-m", "unittest", "discover", "-s", str(coordinator_tests),
             "-p", "test_validate_closure_v2.py"),
        ),
        GateStep(
            "coordinator_actual_state_self_check", "command",
            (python, "-c", (
                "from pathlib import Path; "
                "from closure_actual_state import normalize_relative_path, repository_snapshot; "
                "from closure_v2 import validate_v2; "
                "assert normalize_relative_path('skills/x') == 'skills/x'; "
                "assert normalize_relative_path('../x') is None; "
                "assert callable(validate_v2); "
                "assert isinstance(repository_snapshot(Path('.')), dict)"
            )),
            (("PYTHONPATH", str(coordinator_scripts)),),
        ),
        GateStep(
            "installer_staging_parity_rollback", "installer",
            ("<internal>", "installer-staging-parity-rollback"),
        ),
        GateStep(
            "agent_behavior_evidence", "json_command",
            (python, "-I", str(root / "scripts" / "validate_agent_evals.py"),
             "--root", str(root), "--spec", str(
                 root / "scripts" / "agent_eval_scenarios.json"
             ), "--evidence-root", str(evidence_root),
             "--results", str(results_path),
             "--reviewer-key", str(reviewer_key_path),
             "--trusted-reviewer", trusted_reviewer_id,
             "--trusted-reviewer-key-sha256", trusted_reviewer_key_sha256,
             "--max-age-hours", str(max_age_hours),
             "--max-run-duration-hours", str(max_run_duration_hours)),
        ),
        GateStep(
            "release_postflight", "release_postflight",
            ("<internal>", "git-root-head-status-tree-postflight"),
        ),
    ))
    return tuple(steps)


def _agent_command_shape(root: Path, command: Tuple[str, ...]) -> Optional[str]:
    expected_tokens = (
        sys.executable,
        "-I",
        str(root / "scripts" / "validate_agent_evals.py"),
        "--root", str(root),
        "--spec", str(root / "scripts" / "agent_eval_scenarios.json"),
        "--evidence-root", None,
        "--results", None,
        "--reviewer-key", None,
        "--trusted-reviewer", None,
        "--trusted-reviewer-key-sha256", None,
        "--max-age-hours", None,
        "--max-run-duration-hours", None,
    )
    if len(command) != len(expected_tokens):
        return "agent evidence command length is not canonical"
    for actual, expected in zip(command, expected_tokens):
        if expected is not None and actual != expected:
            return "agent evidence command tokens are not canonical"
    for index in (8, 10, 12):
        if not Path(command[index]).is_absolute():
            return "agent evidence paths must be absolute"
    digest = command[16]
    if digest and not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        return "trusted reviewer key digest is not canonical"
    try:
        age = int(command[18])
    except ValueError:
        return "agent evidence max age is not canonical"
    if not 0 < age <= 8760 or str(age) != command[18]:
        return "agent evidence max age is not canonical"
    try:
        duration = int(command[20])
    except ValueError:
        return "agent evidence max run duration is not canonical"
    if (not 0 < duration <= MAX_MAX_RUN_DURATION_HOURS
            or str(duration) != command[20]):
        return "agent evidence max run duration is not canonical"
    return None


def _canonical_plan_error(
    root: Path, steps: Tuple[GateStep, ...], profile: str
) -> Optional[str]:
    try:
        expected = build_plan(
            root, Path("/__keystone_evidence__/results.json"), profile=profile,
            evidence_root=Path("/__keystone_evidence__"),
            reviewer_key_path=Path("/__keystone_trust__/reviewer.key"),
            trusted_reviewer_id="canonical-reviewer",
            trusted_reviewer_key_sha256="sha256:" + "0" * 64,
            max_age_hours=1, max_run_duration_hours=1,
        )
    except ValueError as error:
        return str(error)
    if len(steps) != len(expected):
        return "release plan length differs from the canonical %s plan" % profile
    for actual, canonical in zip(steps, expected):
        if (actual.identifier != canonical.identifier or actual.kind != canonical.kind
                or actual.environment != canonical.environment):
            return "release plan step identity, kind, or environment is not canonical"
        if actual.identifier == "agent_behavior_evidence":
            error = _agent_command_shape(root, actual.command)
            if error:
                return error
        elif actual.command != canonical.command:
            return "release plan command is not canonical: %s" % actual.identifier
    return None


def _step_listing(step: GateStep) -> Dict[str, object]:
    return {"id": step.identifier, "kind": step.kind, "command": list(step.command)}


def _step_result(step: GateStep, result: CommandResult, status: str) -> Dict[str, object]:
    return {
        "id": step.identifier,
        "kind": step.kind,
        "status": status,
        "returncode": result.returncode,
        "stdout_sha256": _stream_digest(result.stdout),
        "stderr_sha256": _stream_digest(result.stderr),
    }


def run_plan(
    root: Path,
    steps: Iterable[GateStep],
    executor: Executor = _subprocess_executor,
    installer_checker: InstallerChecker = _installer_check,
    profile: str = "production",
    internal_checkers: Optional[Mapping[str, InternalChecker]] = None,
) -> Tuple[Dict[str, object], int]:
    root = Path(root).resolve()
    planned_steps = tuple(steps)
    results: List[Dict[str, object]] = []
    diagnostics: List[Dict[str, str]] = []
    counts = {"total": 0, "passed": 0, "failed": 0, "errors": 0}
    base_environment = _sanitized_environment(root)
    baseline_state: Optional[Dict[str, str]] = None
    checkers: Dict[str, InternalChecker] = {
        "release_preflight": _release_preflight_check,
        "compileall": _compileall_check,
        "docs_readiness": _docs_readiness_check,
        "repository_readiness": _repository_readiness_check,
        "historical_finalization": _historical_finalization_check,
        "current_finalization": _current_finalization_check,
    }
    if internal_checkers is not None:
        checkers.update(internal_checkers)
    if (not planned_steps or planned_steps[0].identifier != "release_preflight"
            or planned_steps[0].kind != "release_preflight"):
        planned_steps = (GateStep(
            "release_preflight", "invalid_preflight_order", ("<internal>",),
        ),)
    for step in planned_steps:
        counts["total"] += 1
        try:
            if step.kind == "installer":
                result = installer_checker(root)
                if result is None:
                    result = CommandResult(0, "", "")
            elif step.kind in {"command", "json_command"}:
                environment = base_environment.copy()
                environment.update(dict(step.environment))
                result = executor(step.command, root, environment)
                if step.kind == "json_command":
                    envelope_kind = (
                        "linker" if step.identifier == "linker_repository_validation"
                        else "agent" if step.identifier == "agent_behavior_evidence"
                        else "author"
                    )
                    result = _validated_pass_envelope(
                        result, step.identifier, envelope_kind
                    )
            elif step.kind == "release_postflight":
                if step.kind in checkers:
                    result = checkers[step.kind](root)
                elif baseline_state is None:
                    result = CommandResult(2, "", "preflight release state is unavailable")
                else:
                    result = _release_postflight_check(root, baseline_state)
            elif step.kind in checkers:
                result = checkers[step.kind](root)
            else:
                raise ValueError("unknown release gate step kind: %s" % step.kind)
            if not isinstance(result, CommandResult):
                raise ValueError("release gate checker returned an invalid result")
        except Exception as error:
            result = CommandResult(2, "", str(error))
        if step.identifier == "release_preflight" and result.returncode == 0:
            baseline_state = _release_state_from_result(result)
            if baseline_state is None:
                result = CommandResult(2, result.stdout, "preflight state is malformed")
        if result.returncode == 0:
            status = "pass"
            counts["passed"] += 1
        elif result.returncode == 1:
            status = "fail"
            counts["failed"] += 1
            diagnostics.append({
                "severity": "error", "code": "release_gate_step_failed",
                "message": "release gate step reported findings", "path": step.identifier,
            })
        else:
            status = "error"
            counts["errors"] += 1
            diagnostics.append({
                "severity": "error", "code": "release_gate_step_error",
                "message": "release gate step could not execute", "path": step.identifier,
            })
        results.append(_step_result(step, result, status))
        if step.identifier == "release_preflight" and result.returncode != 0:
            break
        if step.identifier == "release_preflight":
            plan_error = _canonical_plan_error(root, planned_steps, profile)
            if plan_error:
                counts["total"] += 1
                counts["errors"] += 1
                plan_result = CommandResult(2, "", plan_error)
                plan_step = GateStep(
                    "canonical_plan_validation", "plan_validation", ("<internal>",)
                )
                results.append(_step_result(plan_step, plan_result, "error"))
                diagnostics.append({
                    "severity": "error", "code": "release_plan_invalid",
                    "message": plan_error, "path": "release_plan",
                })
                break
    exit_code = 2 if counts["errors"] else (1 if counts["failed"] else 0)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "error" if exit_code == 2 else ("fail" if exit_code == 1 else "pass"),
        "profile": profile,
        "steps": results,
        "diagnostics": diagnostics,
        "summary": counts,
    }
    return payload, exit_code


def _argument_path(root: Path, value: Optional[str], default: Path) -> Path:
    if value is None:
        return default.resolve()
    candidate = Path(value)
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


class _JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = {
            "schema_version": SCHEMA_VERSION, "status": "error", "profile": "production",
            "steps": [],
            "diagnostics": [{
                "severity": "error", "code": "invocation_invalid",
                "message": message, "path": "arguments",
            }],
            "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 1},
        }
        print(json.dumps(payload, sort_keys=True))
        raise SystemExit(2)


def _bounded_age(value: str) -> int:
    try:
        age = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("max age must be an integer")
    if not 0 < age <= 8760:
        raise argparse.ArgumentTypeError("max age must be between 1 and 8760 hours")
    return age


def _bounded_run_duration(value: str) -> int:
    try:
        duration = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("max run duration must be an integer")
    if not 0 < duration <= MAX_MAX_RUN_DURATION_HOURS:
        raise argparse.ArgumentTypeError(
            "max run duration must be between 1 and %d hours"
            % MAX_MAX_RUN_DURATION_HOURS
        )
    return duration


def _optional_sha256(value: str) -> str:
    if value and not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise argparse.ArgumentTypeError(
            "trusted reviewer key digest must be canonical sha256"
        )
    return value


def parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[1]
    parser = _JsonArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(default_root))
    parser.add_argument(
        "--agent-eval-evidence-root",
        default=os.environ.get("KEYSTONE_AGENT_EVAL_EVIDENCE_ROOT"),
    )
    parser.add_argument(
        "--agent-eval-results", default=os.environ.get("KEYSTONE_AGENT_EVAL_RESULTS")
    )
    parser.add_argument(
        "--agent-eval-reviewer-key",
        default=os.environ.get("KEYSTONE_AGENT_EVAL_REVIEWER_KEY"),
    )
    parser.add_argument(
        "--agent-eval-trusted-reviewer",
        default=os.environ.get("KEYSTONE_AGENT_EVAL_TRUSTED_REVIEWER", ""),
    )
    parser.add_argument(
        "--agent-eval-trusted-reviewer-key-sha256",
        type=_optional_sha256,
        default=os.environ.get("KEYSTONE_AGENT_EVAL_TRUSTED_REVIEWER_KEY_SHA256", ""),
    )
    parser.add_argument(
        "--agent-eval-max-age-hours", type=_bounded_age,
        default=os.environ.get("KEYSTONE_AGENT_EVAL_MAX_AGE_HOURS", str(DEFAULT_MAX_AGE_HOURS)),
    )
    parser.add_argument(
        "--agent-eval-max-run-duration-hours", type=_bounded_run_duration,
        default=os.environ.get(
            "KEYSTONE_AGENT_EVAL_MAX_RUN_DURATION_HOURS",
            str(DEFAULT_MAX_RUN_DURATION_HOURS),
        ),
    )
    parser.add_argument("--profile", choices=("production", "rc"), default="production")
    parser.add_argument("--list", action="store_true", help="List steps without executing them")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        payload = {
            "schema_version": SCHEMA_VERSION, "status": "error", "profile": args.profile,
            "steps": [],
            "diagnostics": [{
                "severity": "error", "code": "root_unavailable",
                "message": "--root must be an existing directory", "path": args.root,
            }],
            "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 1},
        }
        print(json.dumps(payload, sort_keys=True))
        return 2
    external_id = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]
    default_evidence = Path.home() / ".codex" / "evidence" / "keystone" / external_id
    evidence_root = (
        Path(args.agent_eval_evidence_root).expanduser().absolute()
        if args.agent_eval_evidence_root else default_evidence.absolute()
    )
    if args.agent_eval_results:
        results_candidate = Path(args.agent_eval_results).expanduser()
        results_path = (
            results_candidate.absolute() if results_candidate.is_absolute()
            else (evidence_root / results_candidate).absolute()
        )
    else:
        results_path = evidence_root / "agent-eval-results.json"
    reviewer_key = (
        Path(args.agent_eval_reviewer_key).expanduser().absolute()
        if args.agent_eval_reviewer_key
        else (Path.home() / ".codex" / "keystone-agent-eval-reviewer.key").absolute()
    )
    steps = build_plan(
        root, results_path, profile=args.profile, evidence_root=evidence_root,
        reviewer_key_path=reviewer_key,
        trusted_reviewer_id=args.agent_eval_trusted_reviewer,
        trusted_reviewer_key_sha256=args.agent_eval_trusted_reviewer_key_sha256,
        max_age_hours=args.agent_eval_max_age_hours,
        max_run_duration_hours=args.agent_eval_max_run_duration_hours,
    )
    if args.list:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "listed",
            "profile": args.profile,
            "steps": [_step_listing(step) for step in steps],
            "diagnostics": [],
            "summary": {"total": len(steps), "passed": 0, "failed": 0, "errors": 0},
        }
        print(json.dumps(payload, sort_keys=True))
        return 0
    payload, exit_code = run_plan(root, steps, profile=args.profile)
    print(json.dumps(payload, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
