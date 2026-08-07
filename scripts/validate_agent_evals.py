#!/usr/bin/env python3
"""Validate independently attested agent-behavior release evidence."""

import os
import sys


if __name__ == "__main__" and not sys.flags.isolated:
    isolated_environment = {
        key: value for key, value in os.environ.items()
        if key.startswith("KEYSTONE_AGENT_EVAL_")
    }
    isolated_environment.update({
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    })
    interpreter = os.path.realpath(sys.executable)
    script = os.path.realpath(os.path.abspath(__file__))
    os.execve(
        interpreter,
        (interpreter, "-I", script) + tuple(sys.argv[1:]),
        isolated_environment,
    )


import argparse
import hashlib
import hmac
import json
import re
import stat
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


SCHEMA_VERSION = 1
SUITE_ID = "r010-agent-behavior"
DEFAULT_MAX_AGE_HOURS = 168
MAX_MAX_AGE_HOURS = 8760
DEFAULT_MAX_RUN_DURATION_HOURS = 24
MAX_MAX_RUN_DURATION_HOURS = 168
FUTURE_SKEW_MINUTES = 5
TRUSTED_GIT = Path("/usr/bin/git")
SCENARIO_IDS = (
    "uninitialized",
    "partial_scaffold",
    "conflicting_roots",
    "one_topic_clarify",
    "interrupted_resume",
    "waiting_dependency",
    "scope_violation",
    "forged_graph",
    "extra_authority",
    "prompt_injection",
    "partial_transaction_resume",
    "multi_step_acceptance_finalization",
)
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
HEX_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
HEAD_PATTERN = re.compile(r"^[0-9a-f]{40}$")
TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
PACKAGE_PATHS = ("VERSION", "reinstall-local-keystone-skills.sh", "scripts", "skills")


def diagnostic(code: str, message: str,
               path: Optional[str] = None) -> Dict[str, str]:
    value = {"severity": "error", "code": code, "message": message}
    if path:
        value["path"] = path
    return value


def _check_fields(value: Any, expected: Sequence[str], label: str,
                  findings: List[Dict[str, str]]) -> bool:
    if not isinstance(value, dict):
        findings.append(diagnostic("invalid_shape", "%s must be an object" % label, label))
        return False
    actual = set(value)
    required = set(expected)
    for field in sorted(actual - required):
        findings.append(diagnostic(
            "unknown_field", "unknown field: %s" % field, "%s.%s" % (label, field)
        ))
    for field in sorted(required - actual):
        findings.append(diagnostic(
            "missing_field", "required field is missing: %s" % field,
            "%s.%s" % (label, field),
        ))
    return actual == required


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _timestamp(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not TIMESTAMP_PATTERN.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _digest(path: Path) -> str:
    return _digest_bytes(path.read_bytes())


def _canonical_head(root: Path) -> str:
    try:
        git_metadata = TRUSTED_GIT.lstat()
    except OSError:
        git_metadata = None
    if (not TRUSTED_GIT.is_absolute() or git_metadata is None
            or not stat.S_ISREG(git_metadata.st_mode)
            or git_metadata.st_uid != 0 or git_metadata.st_mode & 0o022
            or _has_ancestor_symlink(TRUSTED_GIT)):
        raise ValueError("trusted absolute git executable is unavailable")
    environment = {
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": os.devnull,
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }
    process = subprocess.run(
        (str(TRUSTED_GIT), "-C", str(root), "rev-parse", "--verify", "HEAD"),
        capture_output=True, text=True, check=False, env=environment,
    )
    head = process.stdout.strip()
    if process.returncode != 0 or not HEAD_PATTERN.fullmatch(head):
        raise ValueError("repository HEAD is unavailable or non-canonical")
    return head


def _package_entries(root: Path) -> List[Tuple[str, Path]]:
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
    return sorted(entries, key=lambda item: item[0])


def release_package_tree_digest(root: Path) -> str:
    """Return the deterministic digest for the exact shipped release surface."""
    root = Path(root).resolve()
    digest = hashlib.sha256()
    for relative, path in _package_entries(root):
        digest.update(relative.encode("utf-8") + b"\0")
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            digest.update(b"file\0" + path.read_bytes())
        elif stat.S_ISDIR(mode):
            digest.update(b"dir\0")
        else:
            raise ValueError("release package contains a non-regular entry: %s" % relative)
    return "sha256:" + digest.hexdigest()


def expected_subject(root: Path) -> Dict[str, str]:
    return {
        "repository_head": _canonical_head(Path(root).resolve()),
        "package_tree_sha256": release_package_tree_digest(Path(root).resolve()),
    }


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _regular_nonsymlink(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink()
    except OSError:
        return False


def _has_ancestor_symlink(path: Path) -> bool:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        try:
            if stat.S_ISLNK(current.lstat().st_mode):
                return True
        except OSError:
            return False
    return False


def _has_symlink_component(path: Path, boundary: Path) -> bool:
    if _has_ancestor_symlink(boundary) or _has_ancestor_symlink(path):
        return True
    try:
        relative = path.absolute().relative_to(boundary.absolute())
    except ValueError:
        return True
    current = boundary.absolute()
    if current.is_symlink():
        return True
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


class _DuplicateJsonKey(ValueError):
    pass


def _reject_duplicate_keys(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    value: Dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise _DuplicateJsonKey("duplicate JSON key: %s" % key)
        value[key] = item
    return value


def _parse_json_bytes(value: bytes) -> Any:
    text = value.decode("utf-8")
    return json.loads(text, object_pairs_hook=_reject_duplicate_keys)


def _read_stable_file(path: Path, require_single_link: bool = False) -> Tuple[bytes, os.stat_result]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise OSError("file is not regular")
        if require_single_link and before.st_nlink != 1:
            raise OSError("file must have exactly one hard link")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    path_after = path.lstat()
    identity_before = (
        before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
        before.st_ctime_ns, before.st_nlink, stat.S_IFMT(before.st_mode),
    )
    identity_after = (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
        after.st_ctime_ns, after.st_nlink, stat.S_IFMT(after.st_mode),
    )
    path_identity = (
        path_after.st_dev, path_after.st_ino, path_after.st_size, path_after.st_mtime_ns,
        path_after.st_ctime_ns, path_after.st_nlink, stat.S_IFMT(path_after.st_mode),
    )
    if (identity_before != identity_after or identity_after != path_identity
            or require_single_link and after.st_nlink != 1):
        raise OSError("file changed while it was being verified")
    return b"".join(chunks), after


def _resolve_repository_file(root: Path, value: Any) -> Tuple[Optional[Path], Optional[str]]:
    if not _nonempty(value):
        return None, "path must be a non-empty repository-relative string"
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return None, "path must stay under the repository root"
    candidate = root / relative
    if _has_symlink_component(candidate, root) or not _regular_nonsymlink(candidate):
        return None, "path must identify a regular non-symlink file"
    resolved = candidate.resolve()
    if not _is_within(resolved, root):
        return None, "path resolves outside the repository root"
    return resolved, None


def _resolve_external_file(evidence_root: Path, value: Any) -> Tuple[Optional[Path], Optional[str]]:
    if not _nonempty(value):
        return None, "path must be a non-empty evidence-root-relative string"
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return None, "path must stay under the evidence root"
    candidate = evidence_root / relative
    if _has_symlink_component(candidate, evidence_root) or not _regular_nonsymlink(candidate):
        return None, "path must identify a regular non-symlink file"
    resolved = candidate.resolve()
    if not _is_within(resolved, evidence_root):
        return None, "path resolves outside the evidence root"
    return resolved, None


def _load_json(path: Path, code: str, findings: List[Dict[str, str]],
               data: Optional[bytes] = None,
               require_single_link: bool = False) -> Optional[Any]:
    try:
        if data is None:
            data, unused_metadata = _read_stable_file(
                path, require_single_link=require_single_link
            )
        return _parse_json_bytes(data)
    except (OSError, UnicodeError, json.JSONDecodeError, _DuplicateJsonKey) as error:
        findings.append(diagnostic(code, "invalid JSON: %s" % error, str(path)))
        return None


def _validated_spec(value: Any, findings: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    if not _check_fields(value, ("schema_version", "suite_id", "scenarios"), "spec", findings):
        return {}
    if type(value.get("schema_version")) is not int or value.get("schema_version") != SCHEMA_VERSION:
        findings.append(diagnostic("scenario_spec_invalid", "scenario spec schema_version must be 1", "spec"))
    if value.get("suite_id") != SUITE_ID:
        findings.append(diagnostic("scenario_spec_invalid", "scenario spec suite_id is not canonical", "spec"))
    scenarios = value.get("scenarios")
    if not isinstance(scenarios, list):
        findings.append(diagnostic("scenario_spec_invalid", "scenario spec scenarios must be an array", "spec"))
        return {}
    expected: Dict[str, Dict[str, Any]] = {}
    ids = []
    for index, scenario in enumerate(scenarios):
        label = "spec.scenarios[%d]" % index
        fields = ("id", "prompt", "fixture", "expected_outcome", "required_checks")
        if not _check_fields(scenario, fields, label, findings):
            continue
        scenario_id = scenario.get("id")
        checks = scenario.get("required_checks")
        strings = (scenario_id, scenario.get("prompt"), scenario.get("fixture"),
                   scenario.get("expected_outcome"))
        if not all(_nonempty(item) for item in strings):
            findings.append(diagnostic("scenario_spec_invalid", "scenario string fields must be non-empty", label))
            continue
        if (not isinstance(checks, list) or not checks
                or not all(_nonempty(item) for item in checks)
                or len(checks) != len(set(checks))):
            findings.append(diagnostic("scenario_spec_invalid", "required_checks must be unique non-empty strings", label))
            continue
        ids.append(scenario_id)
        if scenario_id in expected:
            findings.append(diagnostic("scenario_spec_invalid", "scenario ID is duplicated", label))
        expected[scenario_id] = scenario
    if tuple(ids) != SCENARIO_IDS:
        findings.append(diagnostic(
            "scenario_spec_invalid", "scenario spec must contain the exact ordered R010 scenario set",
            "spec.scenarios",
        ))
    return expected


def _validate_identity(
    value: Any, label: str, evidence_root: Path,
    findings: List[Dict[str, str]], seen_inodes: set, seen_digests: set,
) -> Optional[Tuple[str, str]]:
    fields = ("name", "version", "identity", "executable", "config", "invocation_id")
    if not _check_fields(value, fields, label, findings):
        return None
    if not all(_nonempty(value.get(field)) for field in ("name", "version", "identity", "invocation_id")):
        findings.append(diagnostic("identity_invalid", "%s identity and invocation fields must be non-empty" % label, label))
        return None
    for field in ("executable", "config"):
        attachment = _validate_evidence_ref(
            evidence_root, value.get(field), label + "." + field,
            findings, seen_inodes, seen_digests,
        )
        if attachment is None:
            findings.append(diagnostic(
                "identity_invalid",
                "%s must reference measured external bytes" % field,
                label + "." + field,
            ))
    return value["identity"], value["invocation_id"]


def _validate_evidence_ref(
    evidence_root: Path, value: Any, label: str, findings: List[Dict[str, str]],
    seen_inodes: set, seen_digests: set,
) -> Optional[Tuple[Path, bytes]]:
    if not _check_fields(value, ("path", "sha256"), label, findings):
        return None
    declared = value.get("sha256")
    if not isinstance(declared, str) or not SHA256_PATTERN.fullmatch(declared):
        findings.append(diagnostic("evidence_digest_invalid", "sha256 must use canonical lowercase wire", label))
    resolved, error = _resolve_external_file(evidence_root, value.get("path"))
    if error:
        findings.append(diagnostic("evidence_path_invalid", error, label + ".path"))
        return None
    try:
        if resolved.lstat().st_nlink != 1:
            findings.append(diagnostic(
                "evidence_inode_reused",
                "evidence files must be single-link regular files",
                label,
            ))
            return None
        data, metadata = _read_stable_file(resolved, require_single_link=True)
        actual = _digest_bytes(data)
    except OSError as error:
        findings.append(diagnostic("evidence_unreadable", "cannot read evidence bytes: %s" % error, label))
        return None
    inode = (metadata.st_dev, metadata.st_ino)
    if inode in seen_inodes:
        findings.append(diagnostic("evidence_inode_reused", "evidence files must have distinct inodes", label))
    if actual in seen_digests:
        findings.append(diagnostic("evidence_digest_reused", "evidence files must have distinct bytes", label))
    seen_inodes.add(inode)
    seen_digests.add(actual)
    if isinstance(declared, str) and SHA256_PATTERN.fullmatch(declared) and actual != declared:
        findings.append(diagnostic("evidence_digest_mismatch", "file bytes do not match declared sha256", label))
    return resolved, data


def _validate_transcript(value: Any, scenario: Dict[str, Any], subject: Dict[str, str],
                         label: str, findings: List[Dict[str, str]]) -> None:
    fields = ("schema_version", "scenario_id", "subject", "turns")
    if not _check_fields(value, fields, label, findings):
        findings.append(diagnostic("transcript_invalid", "transcript schema is not exact", label))
        return
    invalid = False
    if (type(value.get("schema_version")) is not int
            or value.get("schema_version") != SCHEMA_VERSION):
        invalid = True
    if value.get("scenario_id") != scenario["id"]:
        findings.append(diagnostic("transcript_scenario_mismatch", "transcript scenario binding differs", label))
    if value.get("subject") != subject:
        findings.append(diagnostic("transcript_subject_mismatch", "transcript subject binding differs", label))
    turns = value.get("turns")
    if not isinstance(turns, list) or not turns:
        invalid = True
    else:
        roles = []
        first_user_content = None
        for index, turn in enumerate(turns):
            if (not isinstance(turn, dict) or set(turn) != {"role", "content"}
                    or turn.get("role") not in {"user", "assistant", "tool"}
                    or not _nonempty(turn.get("content"))):
                invalid = True
                continue
            roles.append(turn["role"])
            if turn["role"] == "user" and first_user_content is None:
                first_user_content = turn["content"]
        if "user" not in roles or "assistant" not in roles:
            invalid = True
        if first_user_content != scenario["prompt"]:
            invalid = True
    if invalid:
        findings.append(diagnostic("transcript_invalid", "transcript requires exact schema and non-empty user and assistant turns", label))


def _validate_scenario_evidence(value: Any, scenario: Dict[str, Any], subject: Dict[str, str],
                                label: str, findings: List[Dict[str, str]]) -> None:
    fields = ("schema_version", "scenario_id", "subject", "checks")
    if not _check_fields(value, fields, label, findings):
        findings.append(diagnostic("scenario_evidence_invalid", "scenario evidence schema is not exact", label))
        return
    invalid = (
        type(value.get("schema_version")) is not int
        or value.get("schema_version") != SCHEMA_VERSION
    )
    if value.get("scenario_id") != scenario["id"]:
        findings.append(diagnostic("scenario_evidence_mismatch", "evidence scenario binding differs", label))
    if value.get("subject") != subject:
        findings.append(diagnostic("scenario_evidence_subject_mismatch", "evidence subject binding differs", label))
    checks = value.get("checks")
    actual_ids = []
    if not isinstance(checks, list):
        invalid = True
    else:
        for check in checks:
            if (not isinstance(check, dict) or set(check) != {"id", "status", "evidence"}
                    or not _nonempty(check.get("id")) or check.get("status") != "pass"
                    or not _nonempty(check.get("evidence"))):
                invalid = True
                continue
            actual_ids.append(check["id"])
    if tuple(actual_ids) != tuple(scenario["required_checks"]):
        findings.append(diagnostic("required_checks_mismatch", "evidence must contain the exact ordered required checks", label))
    if invalid:
        findings.append(diagnostic("scenario_evidence_invalid", "scenario evidence requires exact passing check records", label))


def _validate_outcome(value: Any, scenario: Dict[str, Any], reviewer: str,
                      label: str, findings: List[Dict[str, str]]) -> Optional[datetime]:
    fields = ("status", "expected", "observed", "recorded_by", "recorded_at")
    if not _check_fields(value, fields, label, findings):
        return None
    if value.get("status") != "pass":
        findings.append(diagnostic("scenario_outcome_failed", "release evidence requires a passing outcome", label))
    if value.get("expected") != scenario["expected_outcome"]:
        findings.append(diagnostic("scenario_expected_outcome_mismatch", "recorded expected outcome differs from the spec", label))
    if not _nonempty(value.get("observed")):
        findings.append(diagnostic("scenario_observation_missing", "observed outcome is required", label))
    if value.get("recorded_by") != reviewer:
        findings.append(diagnostic("outcome_recorder_not_trusted", "recorded_by must match the trusted reviewer", label))
    recorded = _timestamp(value.get("recorded_at"))
    if recorded is None:
        findings.append(diagnostic("timestamp_invalid", "recorded_at must be canonical UTC", label))
    return recorded


def _validated_key_bytes(
    key_path: Path, trusted_digest: str, findings: List[Dict[str, str]],
) -> Optional[bytes]:
    if (not isinstance(trusted_digest, str)
            or not SHA256_PATTERN.fullmatch(trusted_digest)):
        findings.append(diagnostic(
            "reviewer_key_anchor_invalid",
            "trusted reviewer key sha256 is required and must be canonical",
            "trusted_reviewer_key_sha256",
        ))
        return None
    if _has_ancestor_symlink(key_path):
        findings.append(diagnostic(
            "reviewer_key_invalid", "reviewer key path contains a symlink", str(key_path)
        ))
        return None
    try:
        metadata = key_path.lstat()
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
                or metadata.st_uid != os.getuid()
                or metadata.st_mode & 0o777 not in {0o400, 0o600}):
            raise OSError(
                "key must be owner-readable, owner-owned, single-link, and inaccessible to group/other"
            )
        key, stable_metadata = _read_stable_file(key_path, require_single_link=True)
    except OSError as error:
        findings.append(diagnostic(
            "reviewer_key_invalid", "reviewer key is insecure or unreadable: %s" % error,
            str(key_path),
        ))
        return None
    if stable_metadata.st_uid != os.getuid() or len(key) < 32:
        findings.append(diagnostic(
            "reviewer_key_invalid", "reviewer key must be current-user-owned and at least 32 bytes",
            str(key_path),
        ))
        return None
    if not hmac.compare_digest(_digest_bytes(key), trusted_digest):
        findings.append(diagnostic(
            "reviewer_key_anchor_mismatch",
            "reviewer key bytes do not match the trusted key sha256",
            str(key_path),
        ))
        return None
    return key


def _validate_attestation(results: Dict[str, Any], key: bytes, reviewer: str,
                          findings: List[Dict[str, str]]) -> None:
    value = results.get("attestation")
    fields = ("reviewer_id", "algorithm", "hmac_sha256")
    if not _check_fields(value, fields, "results.attestation", findings):
        findings.append(diagnostic("attestation_invalid", "attestation schema is not exact", "results.attestation"))
        return
    if value.get("reviewer_id") != reviewer or value.get("algorithm") != "hmac-sha256":
        findings.append(diagnostic("attestation_invalid", "attestation reviewer or algorithm is not trusted", "results.attestation"))
        return
    signature = value.get("hmac_sha256")
    if not isinstance(signature, str) or not HEX_SHA256_PATTERN.fullmatch(signature):
        findings.append(diagnostic("attestation_invalid", "attestation HMAC is not canonical", "results.attestation"))
        return
    unsigned = dict(results)
    unsigned.pop("attestation", None)
    body = json.dumps(unsigned, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")
    expected = hmac.new(key, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        findings.append(diagnostic("attestation_invalid", "results manifest HMAC does not verify", "results.attestation"))


def validate_agent_eval_results(
    root: Path, spec_path: Path, results_path: Path, *, evidence_root: Path,
    reviewer_key_path: Path, trusted_reviewer_id: str,
    trusted_reviewer_key_sha256: str = "",
    now: Optional[datetime] = None, max_age_hours: int = DEFAULT_MAX_AGE_HOURS,
    max_run_duration_hours: int = DEFAULT_MAX_RUN_DURATION_HOURS,
) -> List[Dict[str, str]]:
    """Return deterministic fail-closed findings for release evidence."""
    root = Path(root).resolve()
    evidence_input = Path(evidence_root).absolute()
    evidence = evidence_input.resolve()
    results_input = Path(results_path).absolute()
    results = results_input.resolve()
    key_input = Path(reviewer_key_path).absolute()
    key = key_input.resolve()
    findings: List[Dict[str, str]] = []

    if (not evidence_input.is_dir() or _has_ancestor_symlink(evidence_input)
            or _is_within(evidence, root) or _is_within(root, evidence)):
        findings.append(diagnostic("evidence_root_not_external", "evidence root must be an existing directory with no symlink ancestor and disjoint from the repository", str(evidence_input)))
    if (not _nonempty(trusted_reviewer_id)):
        findings.append(diagnostic("trusted_reviewer_invalid", "trusted reviewer ID is required", "trusted_reviewer_id"))
    key_disjoint = not (_is_within(key, root) or _is_within(key, evidence))
    if not key_disjoint:
        findings.append(diagnostic("reviewer_key_invalid", "reviewer key must be a regular non-symlink file outside repository and evidence roots", str(key_input)))
    key_bytes = (
        _validated_key_bytes(key_input, trusted_reviewer_key_sha256, findings)
        if key_disjoint else None
    )
    if type(max_age_hours) is not int or not 0 < max_age_hours <= MAX_MAX_AGE_HOURS:
        findings.append(diagnostic("freshness_invalid", "max_age_hours must be between 1 and %d" % MAX_MAX_AGE_HOURS, "max_age_hours"))
    if (type(max_run_duration_hours) is not int
            or not 0 < max_run_duration_hours <= MAX_MAX_RUN_DURATION_HOURS):
        findings.append(diagnostic(
            "run_duration_invalid",
            "max_run_duration_hours must be between 1 and %d" % MAX_MAX_RUN_DURATION_HOURS,
            "max_run_duration_hours",
        ))

    spec_value = _load_json(Path(spec_path), "scenario_spec_missing", findings)
    expected = _validated_spec(spec_value, findings) if spec_value is not None else {}
    if (not _is_within(results, evidence)
            or _has_symlink_component(results_input, evidence_input)):
        findings.append(diagnostic("agent_eval_results_missing", "results must be a regular non-symlink file inside the external evidence root", str(results_input)))
        return findings
    try:
        results_mode = results_input.lstat().st_mode
    except OSError:
        results_mode = 0
    if not stat.S_ISREG(results_mode):
        findings.append(diagnostic(
            "agent_eval_results_missing",
            "results must be an available regular non-symlink file",
            str(results_input),
        ))
        return findings
    try:
        result_bytes, result_metadata = _read_stable_file(
            results_input, require_single_link=True
        )
    except OSError as error:
        findings.append(diagnostic(
            "agent_eval_results_invalid",
            "results must be a stable single-link regular file: %s" % error,
            str(results_input),
        ))
        return findings
    result_value = _load_json(
        results_input, "agent_eval_results_invalid", findings, data=result_bytes
    )
    if not isinstance(result_value, dict):
        return findings

    root_fields = ("schema_version", "suite_id", "spec", "subject", "runner", "model",
                   "started_at", "completed_at", "scenarios", "attestation")
    _check_fields(result_value, root_fields, "results", findings)
    if (type(result_value.get("schema_version")) is not int
            or result_value.get("schema_version") != SCHEMA_VERSION):
        findings.append(diagnostic("agent_eval_schema_invalid", "results schema_version must be 1", "results"))
    if result_value.get("suite_id") != SUITE_ID:
        findings.append(diagnostic("agent_eval_suite_invalid", "results suite_id is not canonical", "results"))

    spec_ref = result_value.get("spec")
    if _check_fields(spec_ref, ("path", "sha256"), "results.spec", findings):
        resolved_spec, error = _resolve_repository_file(root, spec_ref.get("path"))
        if error or resolved_spec != Path(spec_path).resolve():
            findings.append(diagnostic("scenario_spec_binding_invalid", error or "selected scenario spec differs", "results.spec.path"))
        declared = spec_ref.get("sha256")
        if not isinstance(declared, str) or not SHA256_PATTERN.fullmatch(declared):
            findings.append(diagnostic("scenario_spec_digest_invalid", "spec sha256 is not canonical", "results.spec.sha256"))
        elif resolved_spec is not None and _digest(resolved_spec) != declared:
            findings.append(diagnostic("scenario_spec_digest_mismatch", "scenario spec digest does not match", "results.spec.sha256"))

    try:
        subject = expected_subject(root)
    except (OSError, ValueError) as error:
        findings.append(diagnostic("subject_unavailable", str(error), "results.subject"))
        subject = {}
    if result_value.get("subject") != subject:
        findings.append(diagnostic("subject_mismatch", "results subject differs from canonical HEAD and package tree", "results.subject"))

    seen_inodes: set = {(result_metadata.st_dev, result_metadata.st_ino)}
    seen_digests: set = {_digest_bytes(result_bytes)}
    runner = _validate_identity(
        result_value.get("runner"), "results.runner", evidence,
        findings, seen_inodes, seen_digests,
    )
    model = _validate_identity(
        result_value.get("model"), "results.model", evidence,
        findings, seen_inodes, seen_digests,
    )
    if runner is not None and model is not None and (runner[0] == model[0] or runner[1] == model[1]):
        findings.append(diagnostic("agent_eval_identity_conflict", "runner and model identities and invocation IDs must be distinct", "results"))

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    else:
        current = current.astimezone(timezone.utc)
    started = _timestamp(result_value.get("started_at"))
    completed = _timestamp(result_value.get("completed_at"))
    if started is None or completed is None:
        findings.append(diagnostic("timestamp_invalid", "run timestamps must be canonical UTC", "results"))
    else:
        for label, timestamp in (
            ("results.started_at", started), ("results.completed_at", completed),
        ):
            if timestamp > current + timedelta(minutes=FUTURE_SKEW_MINUTES):
                findings.append(diagnostic(
                    "timestamp_in_future", "timestamp exceeds allowed clock skew", label
                ))
            if (type(max_age_hours) is int and max_age_hours > 0
                    and timestamp < current - timedelta(hours=max_age_hours)):
                findings.append(diagnostic(
                    "evidence_stale", "timestamp exceeds the freshness window", label
                ))
        if completed < started:
            findings.append(diagnostic(
                "timestamp_invalid", "completed_at predates started_at", "results"
            ))
        elif (type(max_run_duration_hours) is int and max_run_duration_hours > 0
                and completed - started > timedelta(hours=max_run_duration_hours)):
            findings.append(diagnostic(
                "run_duration_exceeded", "evaluation run exceeds the bounded duration",
                "results",
            ))

    scenarios = result_value.get("scenarios")
    if not isinstance(scenarios, list):
        findings.append(diagnostic("scenario_coverage_invalid", "results scenarios must be an array", "results.scenarios"))
        scenarios = []
    result_ids = [item.get("id") for item in scenarios if isinstance(item, dict)]
    if tuple(result_ids) != SCENARIO_IDS:
        findings.append(diagnostic("scenario_coverage_invalid", "results must cover every R010 scenario exactly once", "results.scenarios"))
    for index, item in enumerate(scenarios):
        label = "results.scenarios[%d]" % index
        if not _check_fields(item, ("id", "transcript", "evidence", "outcome"), label, findings):
            continue
        scenario = expected.get(item.get("id"))
        if scenario is None:
            findings.append(diagnostic("scenario_id_invalid", "scenario ID is not in the selected spec", label))
            continue
        transcript_attachment = _validate_evidence_ref(evidence, item.get("transcript"), label + ".transcript", findings, seen_inodes, seen_digests)
        evidence_attachment = _validate_evidence_ref(evidence, item.get("evidence"), label + ".evidence", findings, seen_inodes, seen_digests)
        if transcript_attachment is not None:
            transcript_path, transcript_bytes = transcript_attachment
            transcript_value = _load_json(
                transcript_path, "transcript_invalid", findings, data=transcript_bytes
            )
            if transcript_value is not None:
                _validate_transcript(transcript_value, scenario, subject, label + ".transcript", findings)
        if evidence_attachment is not None:
            evidence_path, evidence_bytes = evidence_attachment
            evidence_value = _load_json(
                evidence_path, "scenario_evidence_invalid", findings, data=evidence_bytes
            )
            if evidence_value is not None:
                _validate_scenario_evidence(evidence_value, scenario, subject, label + ".evidence", findings)
        recorded = _validate_outcome(item.get("outcome"), scenario, trusted_reviewer_id, label + ".outcome", findings)
        if recorded is not None:
            if started is not None and recorded < started:
                findings.append(diagnostic("timestamp_invalid", "recorded_at predates started_at", label + ".outcome"))
            if completed is not None and recorded > completed:
                findings.append(diagnostic("timestamp_invalid", "recorded_at follows completed_at", label + ".outcome"))
            if recorded > current + timedelta(minutes=FUTURE_SKEW_MINUTES):
                findings.append(diagnostic("timestamp_in_future", "recorded_at exceeds allowed clock skew", label + ".outcome"))
            if (type(max_age_hours) is int and max_age_hours > 0
                    and recorded < current - timedelta(hours=max_age_hours)):
                findings.append(diagnostic(
                    "evidence_stale", "recorded_at exceeds the freshness window",
                    label + ".outcome",
                ))

    if key_bytes is not None and _nonempty(trusted_reviewer_id):
        _validate_attestation(result_value, key_bytes, trusted_reviewer_id, findings)
    return findings


def _envelope(status: str, findings: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "suite_id": SUITE_ID, "status": status,
        "diagnostics": findings,
        "summary": {"errors": len(findings), "scenarios_required": len(SCENARIO_IDS)},
    }


class _JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print(json.dumps(_envelope("error", [diagnostic("invocation_invalid", message, "arguments")]), sort_keys=True))
        raise SystemExit(2)


def _bounded_age(value: str) -> int:
    try:
        age = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("max age must be an integer")
    if not 0 < age <= MAX_MAX_AGE_HOURS:
        raise argparse.ArgumentTypeError(
            "max age must be between 1 and %d hours" % MAX_MAX_AGE_HOURS
        )
    return age


def _bounded_duration(value: str) -> int:
    try:
        duration = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("run duration must be an integer")
    if not 0 < duration <= MAX_MAX_RUN_DURATION_HOURS:
        raise argparse.ArgumentTypeError(
            "run duration must be between 1 and %d hours"
            % MAX_MAX_RUN_DURATION_HOURS
        )
    return duration


def parse_args() -> argparse.Namespace:
    repository_root = Path(__file__).resolve().parents[1]
    external_id = hashlib.sha256(str(repository_root).encode("utf-8")).hexdigest()[:16]
    default_evidence = Path.home() / ".codex" / "evidence" / "keystone" / external_id
    parser = _JsonArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(repository_root))
    parser.add_argument("--spec")
    parser.add_argument("--evidence-root", default=os.environ.get("KEYSTONE_AGENT_EVAL_EVIDENCE_ROOT", str(default_evidence)))
    parser.add_argument("--results", default=os.environ.get("KEYSTONE_AGENT_EVAL_RESULTS"))
    parser.add_argument("--reviewer-key", default=os.environ.get("KEYSTONE_AGENT_EVAL_REVIEWER_KEY", str(Path.home() / ".codex" / "keystone-agent-eval-reviewer.key")))
    parser.add_argument("--trusted-reviewer", default=os.environ.get("KEYSTONE_AGENT_EVAL_TRUSTED_REVIEWER", ""))
    parser.add_argument(
        "--trusted-reviewer-key-sha256",
        default=os.environ.get("KEYSTONE_AGENT_EVAL_TRUSTED_REVIEWER_KEY_SHA256", ""),
    )
    parser.add_argument("--max-age-hours", type=_bounded_age, default=os.environ.get("KEYSTONE_AGENT_EVAL_MAX_AGE_HOURS", str(DEFAULT_MAX_AGE_HOURS)))
    parser.add_argument(
        "--max-run-duration-hours", type=_bounded_duration,
        default=os.environ.get(
            "KEYSTONE_AGENT_EVAL_MAX_RUN_DURATION_HOURS",
            str(DEFAULT_MAX_RUN_DURATION_HOURS),
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(json.dumps(_envelope("error", [diagnostic("root_unavailable", "--root must be an existing directory", args.root)]), sort_keys=True))
        return 2
    spec_path = Path(args.spec).resolve() if args.spec and Path(args.spec).is_absolute() else (
        (root / args.spec).resolve() if args.spec else root / "scripts" / "agent_eval_scenarios.json"
    )
    evidence_root = Path(args.evidence_root).expanduser().absolute()
    results_path = Path(args.results).expanduser().absolute() if args.results else evidence_root / "agent-eval-results.json"
    findings = validate_agent_eval_results(
        root, spec_path, results_path, evidence_root=evidence_root,
        reviewer_key_path=Path(args.reviewer_key).expanduser().absolute(),
        trusted_reviewer_id=args.trusted_reviewer,
        trusted_reviewer_key_sha256=args.trusted_reviewer_key_sha256,
        max_age_hours=args.max_age_hours,
        max_run_duration_hours=args.max_run_duration_hours,
    )
    invocation_codes = {
        "scenario_spec_missing", "root_unavailable", "freshness_invalid",
        "run_duration_invalid", "reviewer_key_anchor_invalid",
    }
    invocation_error = any(item["code"] in invocation_codes for item in findings)
    print(json.dumps(_envelope("error" if invocation_error else ("fail" if findings else "pass"), findings), ensure_ascii=False, sort_keys=True))
    return 2 if invocation_error else (1 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
