"""Actual repository state primitives for Coordinator closure schemas.

``repository_snapshot`` remains the intentionally weak schema-v1/v2 adapter.  New
authority-bearing callers use the typed, self-validating schema-v3 APIs below.
"""

import base64
import binascii
import errno
import hashlib
import json
import os
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SNAPSHOT_SCHEMA_VERSION = 3
SNAPSHOT_PATH_TYPES = {"regular_file", "directory", "symlink"}
ABSENT_DIGEST = "absent"
_POLICY_FIELDS = {
    "schema_version", "include_paths", "exclusions", "entry_budget",
}
_EXCLUSION_FIELDS = {"path", "reason"}
_ENTRY_FIELDS = {
    "path", "path_type", "raw_byte_digest", "executable",
    "symlink_target_b64", "entry_digest",
}
_SNAPSHOT_FIELDS = {
    "schema_version", "policy", "policy_digest", "entries",
    "discovered_path_count", "path_set_digest", "expected_absences",
    "expected_absence_count", "expected_absence_path_set_digest",
    "expected_absences_complete", "complete", "truncated", "snapshot_digest",
}


class SnapshotCaptureError(RuntimeError):
    """Stable fail-closed error raised by schema-v3 snapshot APIs."""

    def __init__(self, code: str, message: str, path: str = "snapshot") -> None:
        super().__init__(message)
        self.code = code
        self.path = path


class _SnapshotDrift(RuntimeError):
    def __init__(self, message: str, path: str = "snapshot") -> None:
        super().__init__(message)
        self.path = path


_DRIFT_ERRNOS = {
    errno.ENOENT,
    errno.ELOOP,
    errno.ENOTDIR,
    errno.EISDIR,
    errno.EINVAL,
}


def _fail(code: str, message: str, path: str = "snapshot") -> None:
    raise SnapshotCaptureError(code, message, path)


def _raise_capture_os_error(error: OSError, path: str) -> None:
    if error.errno in _DRIFT_ERRNOS:
        raise _SnapshotDrift(str(error), path)
    _fail("snapshot_path_unreadable", str(error), path)


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, UnicodeEncodeError, ValueError) as error:
        _fail("snapshot_wire_not_canonical", str(error))
    raise AssertionError("unreachable")


def _digest_canonical(value: Any) -> str:
    return digest_bytes(_canonical_json_bytes(value))


def _is_digest(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    payload = value[len("sha256:"):]
    return len(payload) == 64 and all(character in "0123456789abcdef" for character in payload)


def _normalized_path(value: Any, path: str, *, allow_root: bool = True) -> str:
    normalized = "." if allow_root and value == "." else normalize_relative_path(value)
    if normalized is None or (not allow_root and normalized == "."):
        _fail(
            "snapshot_path_invalid",
            "Snapshot paths must be normalized repository-relative paths.",
            path,
        )
    try:
        normalized.encode("utf-8")
    except UnicodeEncodeError:
        _fail("snapshot_path_not_utf8", "Snapshot wire paths must be valid UTF-8.", path)
    return normalized


def _casefold_key(path: str) -> str:
    return unicodedata.normalize("NFC", path).casefold()


def _ensure_no_casefold_collisions(paths: Iterable[str], field: str) -> None:
    seen: Dict[str, str] = {}
    for path in paths:
        key = _casefold_key(path)
        prior = seen.get(key)
        if prior is not None and prior != path:
            _fail(
                "snapshot_path_casefold_collision",
                "Unicode-normalized case-fold paths collide: %s and %s." % (prior, path),
                field,
            )
        seen[key] = path


def _normalized_path_sequence(
    value: Any, field: str, *, allow_root: bool = True
) -> Tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        _fail("snapshot_policy_invalid", "%s must be an array." % field, field)
    result = tuple(
        _normalized_path(item, "%s[%d]" % (field, index), allow_root=allow_root)
        for index, item in enumerate(value)
    )
    if len(set(result)) != len(result):
        _fail("snapshot_path_duplicate", "%s paths must be unique." % field, field)
    _ensure_no_casefold_collisions(result, field)
    return tuple(sorted(result))


def _path_selected(path: str, selectors: Sequence[str]) -> bool:
    return any(
        selector == "."
        or path == selector
        or path.startswith(selector.rstrip("/") + "/")
        for selector in selectors
    )


def _path_needed_for_include(path: str, selectors: Sequence[str]) -> bool:
    return _path_selected(path, selectors) or any(
        selector.startswith(path.rstrip("/") + "/") for selector in selectors
    )


@dataclass(frozen=True)
class SnapshotExclusionV3:
    path: str
    reason: str

    def to_wire(self) -> Dict[str, Any]:
        return {"path": self.path, "reason": self.reason}


@dataclass(frozen=True)
class SnapshotPolicyV3:
    include_paths: Tuple[str, ...]
    exclusions: Tuple[SnapshotExclusionV3, ...]
    entry_budget: int

    def to_wire(self) -> Dict[str, Any]:
        return {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "include_paths": list(self.include_paths),
            "exclusions": [item.to_wire() for item in self.exclusions],
            "entry_budget": self.entry_budget,
        }

    def wire(self) -> Dict[str, Any]:
        return self.to_wire()

    @property
    def digest(self) -> str:
        return _digest_canonical(self.to_wire())


@dataclass(frozen=True)
class SnapshotEntryV3:
    path: str
    path_type: str
    raw_byte_digest: Optional[str]
    executable: Optional[bool]
    symlink_target_b64: Optional[str]

    def _payload_wire(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "path_type": self.path_type,
            "raw_byte_digest": self.raw_byte_digest,
            "executable": self.executable,
            "symlink_target_b64": self.symlink_target_b64,
        }

    @property
    def entry_digest(self) -> str:
        return _digest_canonical(self._payload_wire())

    def to_wire(self) -> Dict[str, Any]:
        value = self._payload_wire()
        value["entry_digest"] = self.entry_digest
        return value

    def wire(self) -> Dict[str, Any]:
        return self.to_wire()


@dataclass(frozen=True)
class ExpectedAbsenceEvidenceV3:
    paths: Tuple[str, ...]
    count: int
    path_set_digest: str
    complete: bool = True


@dataclass(frozen=True)
class RepositorySnapshotV3:
    policy: SnapshotPolicyV3
    entries: Tuple[SnapshotEntryV3, ...]
    expected_absences: Tuple[str, ...]
    complete: bool = True
    truncated: bool = False

    @property
    def entry_map(self) -> Dict[str, SnapshotEntryV3]:
        return {entry.path: entry for entry in self.entries}

    def _payload_wire(self) -> Dict[str, Any]:
        paths = tuple(entry.path for entry in self.entries)
        return {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "policy": self.policy.to_wire(),
            "policy_digest": self.policy.digest,
            "entries": [entry.to_wire() for entry in self.entries],
            "discovered_path_count": len(paths),
            "path_set_digest": _digest_canonical(list(paths)),
            "expected_absences": list(self.expected_absences),
            "expected_absence_count": len(self.expected_absences),
            "expected_absence_path_set_digest": _digest_canonical(
                list(self.expected_absences)
            ),
            "expected_absences_complete": True,
            "complete": self.complete,
            "truncated": self.truncated,
        }

    @property
    def snapshot_digest(self) -> str:
        return _digest_canonical(self._payload_wire())

    def to_wire(self) -> Dict[str, Any]:
        value = self._payload_wire()
        value["snapshot_digest"] = self.snapshot_digest
        return value

    def wire(self) -> Dict[str, Any]:
        return self.to_wire()


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_json(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return digest_bytes(payload)


def normalize_relative_path(value: Any) -> Optional[str]:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or value != candidate.as_posix():
        return None
    if any(part in {"", ".", ".."} for part in candidate.parts):
        return None
    return candidate.as_posix()


def safe_path(root: Path, relative: str) -> Optional[Path]:
    normalized = normalize_relative_path(relative)
    if normalized is None:
        return None
    root_resolved = root.resolve()
    candidate = root_resolved.joinpath(*PurePosixPath(normalized).parts)
    try:
        candidate.parent.resolve().relative_to(root_resolved)
    except (OSError, RuntimeError, ValueError):
        return None
    return candidate


def resolved_repository_root(root: Path) -> Path:
    """Resolve one existing repository directory or fail explicitly."""

    resolved = root.resolve(strict=True)
    if not resolved.is_dir():
        raise NotADirectoryError(str(root))
    return resolved


def normalize_snapshot_policy_v3(value: Any) -> SnapshotPolicyV3:
    """Return the one canonical schema-v3 snapshot policy or fail closed."""

    if isinstance(value, SnapshotPolicyV3):
        value = value.to_wire()
    if not isinstance(value, Mapping) or set(value) != _POLICY_FIELDS:
        _fail(
            "snapshot_policy_invalid",
            "Snapshot policy must contain exactly schema_version, include_paths, "
            "exclusions, and entry_budget.",
            "snapshot.policy",
        )
    schema_version = value.get("schema_version")
    if type(schema_version) is not int or schema_version != SNAPSHOT_SCHEMA_VERSION:
        _fail(
            "snapshot_policy_schema_invalid",
            "Snapshot policy schema_version must be 3.",
            "snapshot.policy.schema_version",
        )
    includes = _normalized_path_sequence(
        value.get("include_paths"), "snapshot.policy.include_paths"
    )
    if not includes:
        _fail(
            "snapshot_policy_invalid",
            "Snapshot policy requires at least one include path.",
            "snapshot.policy.include_paths",
        )

    raw_exclusions = value.get("exclusions")
    if not isinstance(raw_exclusions, (list, tuple)):
        _fail(
            "snapshot_policy_invalid",
            "snapshot.policy.exclusions must be an array.",
            "snapshot.policy.exclusions",
        )
    exclusions: List[SnapshotExclusionV3] = []
    for index, raw in enumerate(raw_exclusions):
        field = "snapshot.policy.exclusions[%d]" % index
        if not isinstance(raw, Mapping) or set(raw) != _EXCLUSION_FIELDS:
            _fail(
                "snapshot_policy_invalid",
                "Each exclusion must contain exactly path and reason.",
                field,
            )
        exclusion_path = _normalized_path(raw.get("path"), field + ".path")
        reason = raw.get("reason")
        if (
            not isinstance(reason, str)
            or not reason.strip()
            or reason != reason.strip()
        ):
            _fail(
                "snapshot_exclusion_reason_invalid",
                "Exclusion reason must be non-blank canonical text.",
                field + ".reason",
            )
        exclusions.append(SnapshotExclusionV3(exclusion_path, reason))
    exclusion_paths = tuple(item.path for item in exclusions)
    if len(set(exclusion_paths)) != len(exclusion_paths):
        _fail(
            "snapshot_path_duplicate",
            "Snapshot exclusion paths must be unique.",
            "snapshot.policy.exclusions",
        )
    _ensure_no_casefold_collisions(exclusion_paths, "snapshot.policy.exclusions")
    exclusions = sorted(exclusions, key=lambda item: item.path)

    for include in includes:
        if any(_path_selected(include, (excluded.path,)) for excluded in exclusions):
            _fail(
                "snapshot_policy_conflict",
                "An include path cannot be equal to or below an excluded path.",
                "snapshot.policy.include_paths",
            )
    _ensure_no_casefold_collisions(
        tuple(includes) + tuple(item.path for item in exclusions),
        "snapshot.policy",
    )

    entry_budget = value.get("entry_budget")
    if type(entry_budget) is not int or entry_budget <= 0:
        _fail(
            "snapshot_entry_budget_invalid",
            "Snapshot policy entry_budget must be a positive integer.",
            "snapshot.policy.entry_budget",
        )
    return SnapshotPolicyV3(includes, tuple(exclusions), entry_budget)


def _normalize_expected_absences(
    value: Any, policy: SnapshotPolicyV3
) -> Tuple[str, ...]:
    paths = _normalized_path_sequence(
        value, "snapshot.expected_absences", allow_root=False
    )
    excluded = tuple(item.path for item in policy.exclusions)
    for path in paths:
        if not _path_selected(path, policy.include_paths):
            _fail(
                "expected_absence_out_of_policy",
                "Expected absence must be inside the snapshot include policy.",
                "snapshot.expected_absences",
            )
        if _path_selected(path, excluded):
            _fail(
                "expected_absence_excluded",
                "Expected absence cannot be hidden by an exclusion.",
                "snapshot.expected_absences",
            )
    _ensure_no_casefold_collisions(
        tuple(policy.include_paths)
        + tuple(item.path for item in policy.exclusions)
        + paths,
        "snapshot.expected_absences",
    )
    return paths


def _require_no_follow_support() -> None:
    required_flags = ("O_NOFOLLOW", "O_DIRECTORY")
    if any(not hasattr(os, name) for name in required_flags):
        _fail(
            "snapshot_no_follow_unavailable",
            "Schema-v3 capture requires O_NOFOLLOW and O_DIRECTORY.",
        )
    if (
        os.open not in os.supports_dir_fd
        or os.stat not in os.supports_dir_fd
        or os.readlink not in os.supports_dir_fd
        or os.scandir not in os.supports_fd
    ):
        _fail(
            "snapshot_no_follow_unavailable",
            "Schema-v3 capture requires descriptor-relative filesystem APIs.",
        )


def _directory_open_flags() -> int:
    return (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )


def _file_open_flags() -> int:
    return os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


def _open_root_fd(root: Path) -> int:
    _require_no_follow_support()
    try:
        return os.open(str(root), _directory_open_flags())
    except OSError as error:
        _fail("snapshot_root_unreadable", str(error), "snapshot.root")
    raise AssertionError("unreachable")


def _resolved_snapshot_root(root: Path) -> Path:
    try:
        return resolved_repository_root(Path(root))
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        _fail("snapshot_root_unreadable", str(error), "snapshot.root")
    raise AssertionError("unreachable")


def _stat_identity(value: os.stat_result) -> Tuple[int, int, int, int]:
    return (
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
        value.st_ino,
    )


def _path_type(value: os.stat_result) -> Optional[str]:
    if stat.S_ISREG(value.st_mode):
        return "regular_file"
    if stat.S_ISDIR(value.st_mode):
        return "directory"
    if stat.S_ISLNK(value.st_mode):
        return "symlink"
    return None


def _open_parent_fd(root_fd: int, relative: str) -> Tuple[int, str]:
    parts = PurePosixPath(relative).parts
    parent_fd = os.dup(root_fd)
    try:
        for component in parts[:-1]:
            next_fd = os.open(
                component,
                _directory_open_flags(),
                dir_fd=parent_fd,
            )
            os.close(parent_fd)
            parent_fd = next_fd
        return parent_fd, parts[-1]
    except FileNotFoundError as error:
        os.close(parent_fd)
        raise _SnapshotDrift(str(error), relative)
    except OSError as error:
        os.close(parent_fd)
        _raise_capture_os_error(error, relative)
    raise AssertionError("unreachable")


def _stat_at(parent_fd: int, name: str, relative: str) -> os.stat_result:
    try:
        return os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError as error:
        raise _SnapshotDrift(str(error), relative)
    except OSError as error:
        _raise_capture_os_error(error, relative)
    raise AssertionError("unreachable")


def _classify_supported(value: os.stat_result, relative: str) -> str:
    path_type = _path_type(value)
    if path_type is None:
        _fail(
            "snapshot_path_type_unsupported",
            "Schema-v3 snapshots support only regular_file, directory, and symlink.",
            relative,
        )
    return path_type


def _discover_paths_v3(root: Path, policy: SnapshotPolicyV3) -> Tuple[str, ...]:
    root_fd = _open_root_fd(root)
    found: List[str] = []
    excluded = tuple(item.path for item in policy.exclusions)

    def visit(directory_fd: int, relative_directory: str) -> None:
        try:
            with os.scandir(directory_fd) as iterator:
                names = sorted(entry.name for entry in iterator)
        except OSError as error:
            _fail(
                "snapshot_discovery_failed",
                str(error),
                relative_directory or ".",
            )
        for name in names:
            relative = name if not relative_directory else relative_directory + "/" + name
            relative = _normalized_path(relative, "snapshot.discovery", allow_root=False)
            if _path_selected(relative, excluded):
                continue
            if not _path_needed_for_include(relative, policy.include_paths):
                continue
            current = _stat_at(directory_fd, name, relative)
            current_type = _classify_supported(current, relative)
            if _path_selected(relative, policy.include_paths):
                found.append(relative)
                if len(found) > policy.entry_budget:
                    _fail(
                        "snapshot_entry_budget_exceeded",
                        "Discovered path count exceeds the policy entry budget.",
                        "snapshot.policy.entry_budget",
                    )
            if current_type != "directory":
                continue
            try:
                child_fd = os.open(name, _directory_open_flags(), dir_fd=directory_fd)
            except FileNotFoundError as error:
                raise _SnapshotDrift(str(error), relative)
            except OSError as error:
                _raise_capture_os_error(error, relative)
            try:
                opened = os.fstat(child_fd)
                if _stat_identity(opened) != _stat_identity(current):
                    raise _SnapshotDrift("Directory identity changed during discovery.", relative)
                visit(child_fd, relative)
                after = _stat_at(directory_fd, name, relative)
                if (
                    _path_type(after) != "directory"
                    or _stat_identity(after) != _stat_identity(opened)
                ):
                    raise _SnapshotDrift("Directory identity changed during discovery.", relative)
            finally:
                os.close(child_fd)

    try:
        visit(root_fd, "")
    finally:
        os.close(root_fd)

    discovered = tuple(sorted(found))
    for include in policy.include_paths:
        if include != "." and include not in discovered:
            _fail(
                "snapshot_include_missing",
                "An explicit include path was not discovered: %s." % include,
                "snapshot.policy.include_paths",
            )
    _ensure_no_casefold_collisions(discovered, "snapshot.entries")
    return discovered


def _digest_open_file(file_fd: int, relative: str) -> str:
    digest = hashlib.sha256()
    while True:
        try:
            chunk = os.read(file_fd, 1024 * 1024)
        except OSError as error:
            _raise_capture_os_error(error, relative)
        if not chunk:
            break
        digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _capture_entry_v3(root_fd: int, relative: str) -> SnapshotEntryV3:
    parent_fd, name = _open_parent_fd(root_fd, relative)
    try:
        before = _stat_at(parent_fd, name, relative)
        path_type = _classify_supported(before, relative)
        identity = _stat_identity(before)
        if path_type == "regular_file":
            try:
                file_fd = os.open(name, _file_open_flags(), dir_fd=parent_fd)
            except FileNotFoundError as error:
                raise _SnapshotDrift(str(error), relative)
            except OSError as error:
                _raise_capture_os_error(error, relative)
            try:
                opened = os.fstat(file_fd)
                if (
                    _path_type(opened) != "regular_file"
                    or _stat_identity(opened) != identity
                ):
                    raise _SnapshotDrift("File identity changed before capture.", relative)
                raw_digest = _digest_open_file(file_fd, relative)
                captured = os.fstat(file_fd)
                if _stat_identity(captured) != identity:
                    raise _SnapshotDrift("File identity changed during capture.", relative)
                executable = bool(captured.st_mode & 0o111)
            finally:
                os.close(file_fd)
            after = _stat_at(parent_fd, name, relative)
            if (
                _path_type(after) != "regular_file"
                or _stat_identity(after) != identity
            ):
                raise _SnapshotDrift("File identity changed after capture.", relative)
            return SnapshotEntryV3(relative, path_type, raw_digest, executable, None)

        if path_type == "directory":
            try:
                directory_fd = os.open(name, _directory_open_flags(), dir_fd=parent_fd)
            except FileNotFoundError as error:
                raise _SnapshotDrift(str(error), relative)
            except OSError as error:
                _raise_capture_os_error(error, relative)
            try:
                opened = os.fstat(directory_fd)
                if (
                    _path_type(opened) != "directory"
                    or _stat_identity(opened) != identity
                ):
                    raise _SnapshotDrift("Directory identity changed during capture.", relative)
            finally:
                os.close(directory_fd)
            after = _stat_at(parent_fd, name, relative)
            if (
                _path_type(after) != "directory"
                or _stat_identity(after) != identity
            ):
                raise _SnapshotDrift("Directory identity changed after capture.", relative)
            return SnapshotEntryV3(relative, path_type, None, None, None)

        try:
            target = os.readlink(os.fsencode(name), dir_fd=parent_fd)
        except FileNotFoundError as error:
            raise _SnapshotDrift(str(error), relative)
        except OSError as error:
            _raise_capture_os_error(error, relative)
        if isinstance(target, str):
            target_bytes = os.fsencode(target)
        else:
            target_bytes = target
        after = _stat_at(parent_fd, name, relative)
        if _path_type(after) != "symlink" or _stat_identity(after) != identity:
            raise _SnapshotDrift("Symlink identity changed during capture.", relative)
        return SnapshotEntryV3(
            relative,
            path_type,
            digest_bytes(target_bytes),
            None,
            base64.b64encode(target_bytes).decode("ascii"),
        )
    finally:
        os.close(parent_fd)


def _expected_absence_evidence(
    root: Path,
    expected_absences: Tuple[str, ...],
) -> ExpectedAbsenceEvidenceV3:
    root_fd = _open_root_fd(root)
    try:
        for relative in expected_absences:
            parts = PurePosixPath(relative).parts
            parent_fd = os.dup(root_fd)
            try:
                missing_parent = False
                for component in parts[:-1]:
                    try:
                        child_fd = os.open(
                            component,
                            _directory_open_flags(),
                            dir_fd=parent_fd,
                        )
                    except FileNotFoundError:
                        missing_parent = True
                        break
                    except OSError as error:
                        try:
                            parent_state = os.stat(
                                component,
                                dir_fd=parent_fd,
                                follow_symlinks=False,
                            )
                        except FileNotFoundError:
                            missing_parent = True
                            break
                        except OSError:
                            parent_state = None
                        if parent_state is not None and _path_type(parent_state) == "symlink":
                            _fail(
                                "expected_absence_parent_symlink",
                                "Expected absence has a symlink parent.",
                                relative,
                            )
                        if error.errno == errno.ENOTDIR:
                            missing_parent = True
                            break
                        _fail("expected_absence_check_failed", str(error), relative)
                    os.close(parent_fd)
                    parent_fd = child_fd
                if missing_parent:
                    continue
                try:
                    os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                except OSError as error:
                    _fail("expected_absence_check_failed", str(error), relative)
                _fail(
                    "expected_absence_present",
                    "An assignment-owned expected absence exists.",
                    relative,
                )
            finally:
                os.close(parent_fd)
    finally:
        os.close(root_fd)
    return ExpectedAbsenceEvidenceV3(
        expected_absences,
        len(expected_absences),
        _digest_canonical(list(expected_absences)),
        True,
    )


def validate_expected_absences(
    root: Path,
    expected_absences: Sequence[str],
    *,
    policy: Any,
) -> ExpectedAbsenceEvidenceV3:
    """Validate one assignment-owned absence set against the current root."""

    normalized_policy = normalize_snapshot_policy_v3(policy)
    normalized_absences = _normalize_expected_absences(
        expected_absences, normalized_policy
    )
    resolved_root = _resolved_snapshot_root(root)
    return _expected_absence_evidence(resolved_root, normalized_absences)


def capture_repository_snapshot_v3(
    root: Path,
    policy: Any,
    expected_absences: Sequence[str] = (),
    *,
    max_attempts: int = 3,
) -> RepositorySnapshotV3:
    """Capture one complete, stable, no-follow schema-v3 repository snapshot."""

    normalized_policy = normalize_snapshot_policy_v3(policy)
    normalized_absences = _normalize_expected_absences(
        expected_absences, normalized_policy
    )
    if type(max_attempts) is not int or max_attempts <= 0:
        _fail(
            "snapshot_retry_limit_invalid",
            "max_attempts must be a positive integer.",
            "snapshot.max_attempts",
        )
    resolved_root = _resolved_snapshot_root(root)
    last_drift: Optional[_SnapshotDrift] = None
    for _ in range(max_attempts):
        try:
            before_paths = _discover_paths_v3(resolved_root, normalized_policy)
            _ensure_no_casefold_collisions(
                before_paths + normalized_absences,
                "snapshot.entries",
            )
            _expected_absence_evidence(resolved_root, normalized_absences)
            root_fd = _open_root_fd(resolved_root)
            try:
                first_entries = tuple(
                    _capture_entry_v3(root_fd, path) for path in before_paths
                )
            finally:
                os.close(root_fd)
            middle_paths = _discover_paths_v3(resolved_root, normalized_policy)
            if before_paths != middle_paths:
                raise _SnapshotDrift(
                    "Discovered path set changed during snapshot capture.",
                    "snapshot.entries",
                )
            _expected_absence_evidence(resolved_root, normalized_absences)
            root_fd = _open_root_fd(resolved_root)
            try:
                entries = tuple(
                    _capture_entry_v3(root_fd, path) for path in middle_paths
                )
            finally:
                os.close(root_fd)
            after_paths = _discover_paths_v3(resolved_root, normalized_policy)
            if middle_paths != after_paths:
                raise _SnapshotDrift(
                    "Discovered path set changed during snapshot verification.",
                    "snapshot.entries",
                )
            _expected_absence_evidence(resolved_root, normalized_absences)
            if tuple(entry.path for entry in entries) != before_paths:
                raise _SnapshotDrift(
                    "Captured entries do not match the discovered path set.",
                    "snapshot.entries",
                )
            if tuple(entry.to_wire() for entry in first_entries) != tuple(
                entry.to_wire() for entry in entries
            ):
                raise _SnapshotDrift(
                    "Repository entries changed across stable capture passes.",
                    "snapshot.entries",
                )
            snapshot = RepositorySnapshotV3(
                normalized_policy,
                entries,
                normalized_absences,
            )
            return parse_repository_snapshot_v3(snapshot.to_wire())
        except _SnapshotDrift as error:
            last_drift = error
    assert last_drift is not None
    _fail(
        "snapshot_generation_unstable",
        "Stable snapshot capture failed after %d attempts: %s"
        % (max_attempts, last_drift),
        last_drift.path,
    )
    raise AssertionError("unreachable")


def _parse_snapshot_entry_v3(value: Any, index: int) -> SnapshotEntryV3:
    field = "snapshot.entries[%d]" % index
    if not isinstance(value, Mapping) or set(value) != _ENTRY_FIELDS:
        _fail(
            "snapshot_entry_invalid",
            "Snapshot entry fields do not match schema v3.",
            field,
        )
    path = _normalized_path(value.get("path"), field + ".path", allow_root=False)
    path_type = value.get("path_type")
    if not isinstance(path_type, str) or path_type not in SNAPSHOT_PATH_TYPES:
        _fail(
            "snapshot_entry_type_invalid",
            "Snapshot entry path_type is invalid.",
            field + ".path_type",
        )
    raw_digest = value.get("raw_byte_digest")
    executable = value.get("executable")
    target_b64 = value.get("symlink_target_b64")
    if path_type == "regular_file":
        if not _is_digest(raw_digest):
            _fail(
                "snapshot_entry_digest_invalid",
                "Regular file raw_byte_digest must be canonical SHA-256.",
                field + ".raw_byte_digest",
            )
        if type(executable) is not bool or target_b64 is not None:
            _fail(
                "snapshot_entry_shape_invalid",
                "Regular file requires executable boolean and no symlink target.",
                field,
            )
    elif path_type == "directory":
        if raw_digest is not None or executable is not None or target_b64 is not None:
            _fail(
                "snapshot_entry_shape_invalid",
                "Directory entry must not carry bytes, executable, or symlink target.",
                field,
            )
    else:
        if not _is_digest(raw_digest) or executable is not None or not isinstance(target_b64, str):
            _fail(
                "snapshot_entry_shape_invalid",
                "Symlink requires target bytes digest and canonical base64 target.",
                field,
            )
        try:
            target_bytes = base64.b64decode(target_b64.encode("ascii"), validate=True)
        except (UnicodeEncodeError, ValueError, binascii.Error) as error:
            _fail("snapshot_symlink_target_invalid", str(error), field + ".symlink_target_b64")
        if base64.b64encode(target_bytes).decode("ascii") != target_b64:
            _fail(
                "snapshot_symlink_target_invalid",
                "Symlink target must use canonical base64.",
                field + ".symlink_target_b64",
            )
        if digest_bytes(target_bytes) != raw_digest:
            _fail(
                "snapshot_symlink_target_digest_mismatch",
                "Symlink target bytes do not match raw_byte_digest.",
                field + ".raw_byte_digest",
            )
    entry = SnapshotEntryV3(path, path_type, raw_digest, executable, target_b64)
    if value.get("entry_digest") != entry.entry_digest:
        _fail(
            "snapshot_entry_digest_mismatch",
            "Snapshot entry_digest does not match the typed entry.",
            field + ".entry_digest",
        )
    if dict(value) != entry.to_wire():
        _fail(
            "snapshot_entry_not_canonical",
            "Snapshot entry is not canonical schema-v3 wire.",
            field,
        )
    return entry


def parse_repository_snapshot_v3(value: Any) -> RepositorySnapshotV3:
    """Parse and fully validate one immutable schema-v3 snapshot wire."""

    if not isinstance(value, Mapping) or set(value) != _SNAPSHOT_FIELDS:
        _fail(
            "snapshot_wire_invalid",
            "Snapshot fields do not match schema v3.",
            "snapshot",
        )
    schema_version = value.get("schema_version")
    if type(schema_version) is not int or schema_version != SNAPSHOT_SCHEMA_VERSION:
        _fail(
            "snapshot_schema_invalid",
            "Repository snapshot schema_version must be 3.",
            "snapshot.schema_version",
        )
    policy = normalize_snapshot_policy_v3(value.get("policy"))
    if value.get("policy") != policy.to_wire():
        _fail(
            "snapshot_policy_not_canonical",
            "Snapshot policy arrays must be in canonical order.",
            "snapshot.policy",
        )
    if value.get("policy_digest") != policy.digest:
        _fail(
            "snapshot_policy_digest_mismatch",
            "Snapshot policy_digest does not match the normalized policy.",
            "snapshot.policy_digest",
        )

    raw_entries = value.get("entries")
    if not isinstance(raw_entries, list):
        _fail("snapshot_entries_invalid", "Snapshot entries must be an array.", "snapshot.entries")
    entries = tuple(
        _parse_snapshot_entry_v3(entry, index)
        for index, entry in enumerate(raw_entries)
    )
    paths = tuple(entry.path for entry in entries)
    if paths != tuple(sorted(paths)):
        _fail(
            "snapshot_entries_not_canonical",
            "Snapshot entries must be sorted by path.",
            "snapshot.entries",
        )
    if len(set(paths)) != len(paths):
        _fail("snapshot_path_duplicate", "Snapshot entry paths must be unique.", "snapshot.entries")
    _ensure_no_casefold_collisions(paths, "snapshot.entries")
    excluded_paths = tuple(item.path for item in policy.exclusions)
    for path in paths:
        if not _path_selected(path, policy.include_paths):
            _fail(
                "snapshot_entry_out_of_policy",
                "Snapshot entry is outside the declared include policy.",
                "snapshot.entries",
            )
        if _path_selected(path, excluded_paths):
            _fail(
                "snapshot_entry_excluded",
                "Snapshot entry is hidden by the declared exclusion policy.",
                "snapshot.entries",
            )
    if len(entries) > policy.entry_budget:
        _fail(
            "snapshot_entry_budget_exceeded",
            "Snapshot entry count exceeds policy entry_budget.",
            "snapshot.discovered_path_count",
        )

    expected_absences = _normalize_expected_absences(
        value.get("expected_absences"), policy
    )
    if value.get("expected_absences") != list(expected_absences):
        _fail(
            "expected_absences_not_canonical",
            "Expected absences must be in canonical order.",
            "snapshot.expected_absences",
        )
    _ensure_no_casefold_collisions(
        paths + expected_absences,
        "snapshot.expected_absences",
    )
    if set(paths) & set(expected_absences):
        _fail(
            "expected_absence_present",
            "Snapshot entries overlap assignment-owned expected absences.",
            "snapshot.expected_absences",
        )

    count = value.get("discovered_path_count")
    absence_count = value.get("expected_absence_count")
    if type(count) is not int or count != len(entries):
        _fail(
            "snapshot_path_count_mismatch",
            "discovered_path_count does not match entries.",
            "snapshot.discovered_path_count",
        )
    if type(absence_count) is not int or absence_count != len(expected_absences):
        _fail(
            "expected_absence_count_mismatch",
            "expected_absence_count does not match expected_absences.",
            "snapshot.expected_absence_count",
        )
    if value.get("path_set_digest") != _digest_canonical(list(paths)):
        _fail(
            "snapshot_path_set_digest_mismatch",
            "path_set_digest does not match the complete entry path set.",
            "snapshot.path_set_digest",
        )
    if value.get("expected_absence_path_set_digest") != _digest_canonical(
        list(expected_absences)
    ):
        _fail(
            "expected_absence_path_set_digest_mismatch",
            "Expected absence path-set digest does not match.",
            "snapshot.expected_absence_path_set_digest",
        )
    if value.get("expected_absences_complete") is not True:
        _fail(
            "expected_absences_incomplete",
            "Expected absence evidence must be complete.",
            "snapshot.expected_absences_complete",
        )
    if value.get("complete") is not True or value.get("truncated") is not False:
        _fail(
            "snapshot_incomplete",
            "Authority-bearing snapshot must be complete and not truncated.",
            "snapshot.complete",
        )

    snapshot = RepositorySnapshotV3(policy, entries, expected_absences)
    if value.get("snapshot_digest") != snapshot.snapshot_digest:
        _fail(
            "snapshot_digest_mismatch",
            "snapshot_digest does not match the complete snapshot envelope.",
            "snapshot.snapshot_digest",
        )
    if dict(value) != snapshot.to_wire():
        _fail(
            "snapshot_wire_not_canonical",
            "Snapshot is not canonical schema-v3 wire.",
            "snapshot",
        )
    return snapshot


def snapshot_from_wire_v3(value: Any) -> RepositorySnapshotV3:
    """Compatibility spelling for schema-v3 snapshot parsing."""

    return parse_repository_snapshot_v3(value)


def validate_snapshot_wire_v3(value: Any) -> RepositorySnapshotV3:
    """Validate schema-v3 wire and return the parsed immutable snapshot."""

    return parse_repository_snapshot_v3(value)


def changed_paths_v3(
    before: Any,
    after: Any,
) -> List[Mapping[str, str]]:
    """Return deterministic typed deltas between two complete v3 snapshots."""

    before = parse_repository_snapshot_v3(
        before.wire() if isinstance(before, RepositorySnapshotV3) else before
    )
    after = parse_repository_snapshot_v3(
        after.wire() if isinstance(after, RepositorySnapshotV3) else after
    )
    if before.policy.digest != after.policy.digest:
        _fail(
            "snapshot_policy_mismatch",
            "Baseline and result snapshots must use the same policy.",
            "snapshot.policy_digest",
        )
    if before.expected_absences != after.expected_absences:
        _fail(
            "expected_absence_set_mismatch",
            "Baseline and result snapshots must use the same expected absence set.",
            "snapshot.expected_absences",
        )
    before_entries = before.entry_map
    after_entries = after.entry_map
    changes: List[Mapping[str, str]] = []
    for path in sorted(set(before_entries) | set(after_entries)):
        before_entry = before_entries.get(path)
        after_entry = after_entries.get(path)
        before_digest = (
            before_entry.entry_digest if before_entry is not None else ABSENT_DIGEST
        )
        after_digest = (
            after_entry.entry_digest if after_entry is not None else ABSENT_DIGEST
        )
        if before_digest == after_digest:
            continue
        if before_entry is None:
            change_kind = "added"
        elif after_entry is None:
            change_kind = "deleted"
        elif before_entry.path_type != after_entry.path_type:
            change_kind = "type_replaced"
        else:
            change_kind = "modified"
        changes.append({
            "path": path,
            "change_kind": change_kind,
            "before_entry_digest": before_digest,
            "after_entry_digest": after_digest,
        })
    return changes


def _decoded_symlink_target(entry: SnapshotEntryV3) -> str:
    assert entry.symlink_target_b64 is not None
    try:
        target_bytes = base64.b64decode(
            entry.symlink_target_b64.encode("ascii"),
            validate=True,
        )
        target = target_bytes.decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError, ValueError, binascii.Error):
        _fail(
            "snapshot_symlink_target_invalid",
            "Symlink target is not canonical UTF-8 path text.",
            entry.path,
        )
    if not target or "\x00" in target or "\\" in target:
        _fail(
            "snapshot_symlink_target_invalid",
            "Symlink target is empty or uses invalid path bytes.",
            entry.path,
        )
    return target


def _symlink_chain_resolution(
    origin: SnapshotEntryV3,
    symlinks_by_key: Mapping[str, SnapshotEntryV3],
) -> Tuple[Optional[str], Optional[str]]:
    try:
        target = _decoded_symlink_target(origin)
    except SnapshotCaptureError:
        return "invalid_target", None
    if PurePosixPath(target).is_absolute():
        return "absolute_target", None

    resolved = list(PurePosixPath(origin.path).parent.parts)
    if resolved == ["."]:
        resolved = []
    pending = target.split("/")
    visited = {origin.path}
    while pending:
        component = pending.pop(0)
        if component in {"", "."}:
            continue
        if component == "..":
            if not resolved:
                return "escapes_root", None
            resolved.pop()
            continue
        resolved.append(component)
        candidate = "/".join(resolved)
        chained = symlinks_by_key.get(_casefold_key(candidate))
        if chained is None:
            continue
        if chained.path in visited:
            return "target_cycle", None
        visited.add(chained.path)
        try:
            chained_target = _decoded_symlink_target(chained)
        except SnapshotCaptureError:
            return "invalid_target", None
        if PurePosixPath(chained_target).is_absolute():
            return "absolute_target", None
        resolved = list(PurePosixPath(chained.path).parent.parts)
        if resolved == ["."]:
            resolved = []
        pending = chained_target.split("/") + pending
    return None, "/".join(resolved) or "."


def snapshot_symlink_violations_v3(
    snapshot: Any,
) -> List[Mapping[str, str]]:
    """Resolve recorded symlink chains lexically without filesystem access."""

    parsed = parse_repository_snapshot_v3(
        snapshot.wire() if isinstance(snapshot, RepositorySnapshotV3) else snapshot
    )
    symlinks = {
        entry.path: entry
        for entry in parsed.entries
        if entry.path_type == "symlink"
    }
    symlinks_by_key = {_casefold_key(path): entry for path, entry in symlinks.items()}
    violations: List[Mapping[str, str]] = []
    excluded = tuple(item.path for item in parsed.policy.exclusions)
    for path in sorted(symlinks):
        reason, resolved_target = _symlink_chain_resolution(
            symlinks[path], symlinks_by_key
        )
        if reason is None and resolved_target is not None:
            if not _path_selected(resolved_target, parsed.policy.include_paths):
                reason = "target_outside_policy"
            elif _path_selected(resolved_target, excluded):
                reason = "target_excluded"
        if reason is not None:
            violations.append({"path": path, "reason": reason})
    return violations


def _raise_walk_error(error: OSError) -> None:
    raise error


def repository_snapshot(root: Path) -> Dict[str, str]:
    """Return a deterministic raw-byte snapshot without following symlinks."""

    root = resolved_repository_root(root)
    snapshot: Dict[str, str] = {}
    for current, directory_names, file_names in os.walk(
        root, followlinks=False, onerror=_raise_walk_error
    ):
        current_path = Path(current)
        relative_directory = current_path.relative_to(root)
        if relative_directory == Path(".") and ".git" in directory_names:
            directory_names.remove(".git")

        symlink_directories = []
        for name in list(directory_names):
            path = current_path / name
            if path.is_symlink():
                directory_names.remove(name)
                symlink_directories.append(name)

        for name in sorted(file_names + symlink_directories):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                target = os.readlink(path).encode("utf-8", errors="surrogateescape")
                snapshot[relative] = digest_bytes(b"symlink\0" + target)
            else:
                snapshot[relative] = digest_file(path)
    return dict(sorted(snapshot.items()))


def repository_symlinks(root: Path) -> Dict[str, Tuple[str, bool]]:
    """Return symlink targets and whether their resolved target escapes root."""

    root = resolved_repository_root(root)
    result: Dict[str, Tuple[str, bool]] = {}
    for current, directory_names, file_names in os.walk(
        root, followlinks=False, onerror=_raise_walk_error
    ):
        current_path = Path(current)
        if current_path == root and ".git" in directory_names:
            directory_names.remove(".git")
        names = list(file_names) + list(directory_names)
        for name in names:
            path = current_path / name
            if not path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            target = os.readlink(path)
            try:
                path.resolve().relative_to(root)
                escapes = False
            except (OSError, RuntimeError, ValueError):
                escapes = True
            result[relative] = (target, escapes)
    return dict(sorted(result.items()))


def changed_paths(
    baseline: Mapping[str, str], current: Mapping[str, str]
) -> Dict[str, str]:
    changes: Dict[str, str] = {}
    for path in sorted(set(baseline) | set(current)):
        before = baseline.get(path)
        after = current.get(path)
        if before == after:
            continue
        if before is None:
            changes[path] = "added"
        elif after is None:
            changes[path] = "deleted"
        else:
            changes[path] = "modified"
    return changes


def path_in_scope(path: str, selectors: Iterable[str]) -> bool:
    for selector in selectors:
        normalized = normalize_relative_path(selector)
        if normalized is None:
            continue
        if normalized == ".":
            return True
        if path == normalized or path.startswith(normalized.rstrip("/") + "/"):
            return True
    return False


def path_overlaps_scope(path: str, selectors: Iterable[str]) -> bool:
    """Return whether a path is an ancestor or descendant of any selector."""

    normalized_path = normalize_relative_path(path)
    if normalized_path is None:
        return False
    for selector in selectors:
        normalized = normalize_relative_path(selector)
        if normalized is None:
            continue
        if normalized == ".":
            return True
        if (
            normalized_path == normalized
            or normalized_path.startswith(normalized.rstrip("/") + "/")
            or normalized.startswith(normalized_path.rstrip("/") + "/")
        ):
            return True
    return False
