"""Owner-side atomic apply runtime for one canonical transaction-v2 patch."""

import argparse
import ctypes
from dataclasses import dataclass
import errno
import hashlib
import hmac
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import stat
import sys
from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Sequence, Tuple
import unicodedata


REQUEST_SCHEMA_VERSION = 1
RECEIPT_SCHEMA_VERSION = 1
PRODUCER = "keystone-owned-surface-apply"
COMMAND_ID = "keystone-owned-surface-apply-v1"
TRUST_MODEL = "trusted-host-hmac-sha256"
AUTHORITY_KEY_MIN_BYTES = 32
_KEY_DERIVATION_LABEL = b"keystone-owned-surface-apply-key-v1\0"
_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_HUNK_PATTERN = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_OWNERS = frozenset({"author", "main", "coordinator"})
_SURFACES = frozenset({
    "document_metadata",
    "code_anchor",
    "config_anchor",
    "schema_anchor",
    "api_anchor",
    "test_anchor",
    "companion_metadata",
})
_REPOSITORY_SURFACES = frozenset({
    "code_anchor",
    "config_anchor",
    "schema_anchor",
    "api_anchor",
    "test_anchor",
})
_REQUEST_FIELDS = frozenset({
    "schema_version",
    "transaction_id",
    "transaction_digest",
    "assignment_id",
    "assignment_digest",
    "phase_id",
    "phase_baseline_snapshot_digest",
    "phase_parent_evidence_digest",
    "repository_root_digest",
    "owner",
    "scope",
    "scope_digest",
    "prior_receipt_digest",
    "patch",
})
_SCOPE_FIELDS = frozenset({"allowed", "excluded"})
_PATCH_FIELDS = frozenset({
    "patch_id",
    "owner",
    "surface",
    "target_path",
    "baseline_digest",
    "baseline_content",
    "exact_patch",
    "patch_format",
    "patch_body",
    "expected_after_digest",
    "required",
})


class ApplyError(Exception):
    """Stable failure raised at the apply trust boundary."""

    def __init__(
        self,
        code: str,
        message: str,
        path: Optional[str] = None,
        exit_code: int = 1,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path
        self.exit_code = exit_code


class ApplyValidationError(ApplyError):
    def __init__(self, code: str, message: str, path: Optional[str] = None) -> None:
        super().__init__(code, message, path, 1)


class ApplySecurityError(ApplyError):
    def __init__(self, code: str, message: str, path: Optional[str] = None) -> None:
        super().__init__(code, message, path, 2)


class ApplyIOError(ApplyError):
    def __init__(self, code: str, message: str, path: Optional[str] = None) -> None:
        super().__init__(code, message, path, 2)


@dataclass(frozen=True)
class ValidatedApplyRequest:
    request: Dict[str, Any]
    patch: Dict[str, Any]
    target_path: str
    baseline_bytes: bytes
    expected_bytes: bytes


@dataclass
class ReservedOutput:
    directory_fd: int
    file_fd: int
    name: str
    identity: Tuple[int, ...]


@dataclass
class TargetState:
    root: Path
    relative: str
    directory_fd: int
    name: str
    parent_identity: Tuple[int, ...]
    existed: bool
    identity: Optional[Tuple[int, ...]]
    mode: int
    content: bytes
    published_by_runner: bool = False
    published_identity: Optional[Tuple[int, ...]] = None
    backup_name: Optional[str] = None
    backup_entry_identity: Optional[Tuple[int, ...]] = None
    backup_content: Optional[bytes] = None
    backup_mode: Optional[int] = None


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize one wire value using Keystone canonical JSON bytes."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_json(value: Any) -> str:
    return digest_bytes(canonical_json_bytes(value))


def replay_patch(baseline: bytes, patch_format: str, patch_body: str) -> bytes:
    """Replay the canonical transaction-v2 patch algorithms without Linker imports."""

    if patch_format == "full_replacement":
        return patch_body.encode("utf-8")
    if patch_format != "unified_diff":
        raise ValueError("unsupported patch format")
    try:
        original = baseline.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise ValueError("unified_diff baseline must be UTF-8") from error
    lines = patch_body.splitlines(keepends=True)
    index = 0
    while index < len(lines) and not lines[index].startswith("@@ "):
        index += 1
    output: List[str] = []
    original_index = 0
    saw_hunk = False
    while index < len(lines):
        match = _HUNK_PATTERN.match(lines[index])
        if not match:
            raise ValueError("unified_diff hunk header is invalid")
        saw_hunk = True
        old_line = int(match.group(1))
        expected_old = int(match.group(2) or "1")
        expected_new = int(match.group(4) or "1")
        if old_line == 0:
            if expected_old != 0:
                raise ValueError("unified_diff zero start requires zero old lines")
            old_start = 0
        else:
            old_start = old_line - 1
        if old_start < original_index or old_start > len(original):
            raise ValueError("unified_diff hunk range is invalid")
        output.extend(original[original_index:old_start])
        original_index = old_start
        observed_old = 0
        observed_new = 0
        index += 1
        while index < len(lines) and not lines[index].startswith("@@ "):
            line = lines[index]
            if line.startswith("\\ No newline at end of file"):
                index += 1
                continue
            if not line or line[0] not in {" ", "+", "-"}:
                raise ValueError("unified_diff hunk line is invalid")
            body = line[1:]
            if line[0] in {" ", "-"}:
                if original_index >= len(original) or original[original_index] != body:
                    raise ValueError("unified_diff context does not match baseline")
                if line[0] == " ":
                    output.append(body)
                original_index += 1
                observed_old += 1
            else:
                output.append(body)
            if line[0] in {" ", "+"}:
                observed_new += 1
            index += 1
        if observed_old != expected_old or observed_new != expected_new:
            raise ValueError("unified_diff hunk counts do not match body")
    if not saw_hunk:
        raise ValueError("unified_diff requires at least one hunk")
    output.extend(original[original_index:])
    return "".join(output).encode("utf-8")


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and _DIGEST_PATTERN.fullmatch(value) is not None


def _is_digest_or_absent(value: Any) -> bool:
    return value == "absent" or _is_digest(value)


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalized_relative_path(value: Any, *, selector: bool = False) -> Optional[str]:
    if selector and value == ".":
        return "."
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        return None
    if unicodedata.normalize("NFC", value) != value:
        return None
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        return None
    normalized = candidate.as_posix()
    if normalized != value or normalized == ".":
        return None
    return normalized


def _path_in_scope(path: str, selectors: Sequence[str]) -> bool:
    path_parts = PurePosixPath(path).parts
    for selector in selectors:
        selector_parts = () if selector == "." else PurePosixPath(selector).parts
        if not selector_parts or path_parts[:len(selector_parts)] == selector_parts:
            return True
    return False


def _portable_parts(value: str) -> Tuple[str, ...]:
    if value == ".":
        return ()
    return tuple(
        unicodedata.normalize(
            "NFC", unicodedata.normalize("NFC", part).casefold()
        )
        for part in PurePosixPath(value).parts
    )


def _portable_path_in_scope(path: str, selectors: Sequence[str]) -> bool:
    path_parts = _portable_parts(path)
    for selector in selectors:
        selector_parts = _portable_parts(selector)
        if not selector_parts or path_parts[:len(selector_parts)] == selector_parts:
            return True
    return False


def _owner_matches_surface(owner: str, surface: str, target_path: str) -> bool:
    lower_path = target_path.lower()
    if surface == "document_metadata":
        return owner == "author" and lower_path.endswith((".md", ".markdown"))
    if surface in _REPOSITORY_SURFACES:
        return owner in {"main", "coordinator"}
    if surface != "companion_metadata" or not target_path.endswith(".keystone.json"):
        return False
    source_path = lower_path[:-len(".keystone.json")]
    if not source_path:
        return False
    is_document = source_path.endswith((".md", ".markdown"))
    if is_document:
        return owner == "author"
    return owner in {"main", "coordinator"}


def _validate_scope(value: Any) -> Dict[str, List[str]]:
    if not isinstance(value, dict) or set(value) != _SCOPE_FIELDS:
        raise ApplyValidationError(
            "request_schema_invalid",
            "scope must contain exactly allowed and excluded",
            "scope",
        )
    result: Dict[str, List[str]] = {}
    portable_keys: Dict[Tuple[str, ...], str] = {}
    for field in ("allowed", "excluded"):
        items = value.get(field)
        if not isinstance(items, list) or any(
            _normalized_relative_path(item, selector=True) is None for item in items
        ):
            raise ApplyValidationError(
                "scope_invalid",
                "%s scope must contain normalized selectors" % field,
                "scope.%s" % field,
            )
        if items != sorted(set(items)):
            raise ApplyValidationError(
                "scope_invalid",
                "%s scope must be sorted and unique" % field,
                "scope.%s" % field,
            )
        for item in items:
            portable_key = _portable_parts(item)
            previous = portable_keys.get(portable_key)
            if previous is not None:
                raise ApplyValidationError(
                    "scope_invalid",
                    "scope selectors must have unique portable identities",
                    "scope.%s" % field,
                )
            portable_keys[portable_key] = field
        result[field] = list(items)
    if not result["allowed"]:
        raise ApplyValidationError(
            "scope_invalid", "allowed scope must not be empty", "scope.allowed"
        )
    return result


def _validate_patch(value: Any, owner: str) -> Tuple[Dict[str, Any], bytes, bytes]:
    if not isinstance(value, dict) or set(value) != _PATCH_FIELDS:
        raise ApplyValidationError(
            "request_schema_invalid",
            "patch must be the exact canonical transaction-v2 projection",
            "patch",
        )
    patch = dict(value)
    if not _has_text(patch.get("patch_id")):
        raise ApplyValidationError(
            "patch_invalid", "patch_id must be non-empty text", "patch.patch_id"
        )
    if patch.get("owner") not in _OWNERS or patch.get("owner") != owner:
        raise ApplyValidationError(
            "patch_owner_mismatch",
            "patch owner must equal request owner",
            "patch.owner",
        )
    surface = patch.get("surface")
    if surface not in _SURFACES:
        raise ApplyValidationError(
            "patch_invalid", "patch surface is invalid", "patch.surface"
        )
    target_path = _normalized_relative_path(patch.get("target_path"))
    if target_path is None:
        raise ApplyValidationError(
            "patch_invalid",
            "patch target_path must be normalized repository-relative text",
            "patch.target_path",
        )
    if not _owner_matches_surface(owner, surface, target_path):
        raise ApplyValidationError(
            "owner_surface_invalid",
            "request owner does not own the declared target surface",
            "patch.surface",
        )
    baseline_digest = patch.get("baseline_digest")
    if not _is_digest_or_absent(baseline_digest):
        raise ApplyValidationError(
            "patch_invalid",
            "baseline_digest must be absent or canonical SHA-256",
            "patch.baseline_digest",
        )
    baseline_content = patch.get("baseline_content")
    if baseline_digest == "absent":
        if baseline_content is not None:
            raise ApplyValidationError(
                "patch_baseline_mismatch",
                "absent baseline requires null baseline_content",
                "patch.baseline_content",
            )
        baseline_bytes = b""
    else:
        if not isinstance(baseline_content, str):
            raise ApplyValidationError(
                "patch_baseline_mismatch",
                "present baseline requires UTF-8 baseline_content",
                "patch.baseline_content",
            )
        baseline_bytes = baseline_content.encode("utf-8")
        if digest_bytes(baseline_bytes) != baseline_digest:
            raise ApplyValidationError(
                "patch_baseline_mismatch",
                "baseline_content does not produce baseline_digest",
                "patch.baseline_content",
            )
    exact_patch = patch.get("exact_patch")
    patch_body = patch.get("patch_body")
    if (
        not isinstance(exact_patch, str)
        or not exact_patch
        or not isinstance(patch_body, str)
        or exact_patch != patch_body
    ):
        raise ApplyValidationError(
            "patch_invalid",
            "exact_patch and patch_body must be the same non-empty text",
            "patch.patch_body",
        )
    patch_format = patch.get("patch_format")
    if patch_format not in {"unified_diff", "full_replacement"}:
        raise ApplyValidationError(
            "patch_invalid", "patch_format is unsupported", "patch.patch_format"
        )
    if not _is_digest(patch.get("expected_after_digest")):
        raise ApplyValidationError(
            "patch_invalid",
            "expected_after_digest must be canonical SHA-256",
            "patch.expected_after_digest",
        )
    if type(patch.get("required")) is not bool:
        raise ApplyValidationError(
            "patch_invalid", "required must be boolean", "patch.required"
        )
    try:
        expected_bytes = replay_patch(baseline_bytes, patch_format, patch_body)
    except ValueError as error:
        raise ApplyValidationError(
            "patch_replay_invalid", str(error), "patch.patch_body"
        ) from error
    if digest_bytes(expected_bytes) != patch["expected_after_digest"]:
        raise ApplyValidationError(
            "patch_replay_mismatch",
            "patch replay does not produce expected_after_digest",
            "patch.expected_after_digest",
        )
    return patch, baseline_bytes, expected_bytes


def validate_apply_request(
    value: Any,
    *,
    root: Path,
    allowed_owners: FrozenSet[str],
) -> ValidatedApplyRequest:
    """Validate and project one strict request without touching its target."""

    if not isinstance(value, dict) or set(value) != _REQUEST_FIELDS:
        raise ApplyValidationError(
            "request_schema_invalid",
            "request does not match the exact owner-apply schema-v1 field set",
            "request",
        )
    if (
        type(value.get("schema_version")) is not int
        or value.get("schema_version") != REQUEST_SCHEMA_VERSION
    ):
        raise ApplyValidationError(
            "request_schema_invalid",
            "request schema_version must be 1",
            "schema_version",
        )
    for field in ("transaction_id", "assignment_id", "phase_id"):
        if not _has_text(value.get(field)):
            raise ApplyValidationError(
                "request_binding_invalid",
                "%s must be non-empty text" % field,
                field,
            )
    for field in (
        "transaction_digest",
        "assignment_digest",
        "phase_baseline_snapshot_digest",
        "phase_parent_evidence_digest",
        "repository_root_digest",
        "scope_digest",
    ):
        if not _is_digest(value.get(field)):
            raise ApplyValidationError(
                "request_binding_invalid",
                "%s must be canonical SHA-256" % field,
                field,
            )
    if not _is_digest_or_absent(value.get("prior_receipt_digest")):
        raise ApplyValidationError(
            "request_binding_invalid",
            "prior_receipt_digest must be absent or canonical SHA-256",
            "prior_receipt_digest",
        )
    owner = value.get("owner")
    if owner not in _OWNERS:
        raise ApplyValidationError(
            "request_binding_invalid", "request owner is invalid", "owner"
        )
    if owner not in allowed_owners:
        raise ApplyValidationError(
            "owner_lane_invalid",
            "request owner is outside this package runner lane",
            "owner",
        )
    scope = _validate_scope(value.get("scope"))
    if digest_json(scope) != value["scope_digest"]:
        raise ApplyValidationError(
            "scope_digest_mismatch",
            "scope_digest does not authenticate the normalized scope",
            "scope_digest",
        )
    resolved_root = root.resolve(strict=True)
    expected_root_digest = digest_json({"repository_root": str(resolved_root)})
    if value["repository_root_digest"] != expected_root_digest:
        raise ApplyValidationError(
            "repository_root_digest_mismatch",
            "repository_root_digest does not bind the resolved --root",
            "repository_root_digest",
        )
    patch, baseline_bytes, expected_bytes = _validate_patch(value.get("patch"), owner)
    target_path = patch["target_path"]
    if not _path_in_scope(target_path, scope["allowed"]):
        raise ApplyValidationError(
            "target_scope_invalid",
            "patch target is outside the allowed scope",
            "patch.target_path",
        )
    if (
        _path_in_scope(target_path, scope["excluded"])
        or _portable_path_in_scope(target_path, scope["excluded"])
    ):
        raise ApplyValidationError(
            "target_excluded",
            "patch target is inside the excluded scope",
            "patch.target_path",
        )
    return ValidatedApplyRequest(
        request=dict(value),
        patch=patch,
        target_path=target_path,
        baseline_bytes=baseline_bytes,
        expected_bytes=expected_bytes,
    )


def _file_identity(value: os.stat_result) -> Tuple[int, ...]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
        value.st_nlink,
        stat.S_IFMT(value.st_mode),
        value.st_uid,
    )


def _directory_identity(value: os.stat_result) -> Tuple[int, ...]:
    return (
        value.st_dev,
        value.st_ino,
        stat.S_IFMT(value.st_mode),
    )


def _require_descriptor_security() -> None:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ApplySecurityError(
            "filesystem_security_unavailable",
            "owned apply requires O_NOFOLLOW and O_DIRECTORY",
        )


def _directory_flags() -> int:
    return (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )


def _file_read_flags() -> int:
    return os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


def _open_absolute_parent(path: Path) -> Tuple[int, str]:
    if not path.is_absolute() or path.name in {"", ".", ".."}:
        raise OSError("path must be an absolute file path")
    parts = path.parts
    directory_fd = os.open(parts[0], _directory_flags())
    try:
        for component in parts[1:-1]:
            if component in {"", ".", ".."}:
                raise OSError("path must not contain dot components")
            next_fd = os.open(component, _directory_flags(), dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        return directory_fd, parts[-1]
    except BaseException:
        os.close(directory_fd)
        raise


def _read_single_link_file(
    path: Path,
    *,
    security_code: str,
    require_private_owner: bool = False,
) -> bytes:
    _require_descriptor_security()
    supplied = Path(path)
    if not supplied.is_absolute():
        raise ApplySecurityError(
            security_code, "protected file path must be absolute", str(path)
        )
    try:
        if supplied != supplied.resolve(strict=True):
            raise OSError("protected file path must not contain aliases or symlinks")
        directory_fd, name = _open_absolute_parent(supplied)
        try:
            before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise OSError("protected file must be a single-link regular file")
            if require_private_owner:
                if stat.S_IMODE(before.st_mode) & 0o077:
                    raise OSError("authority key grants group/world permissions")
                if hasattr(os, "geteuid") and before.st_uid != os.geteuid():
                    raise OSError("authority key is not owned by the current OS user")
            file_fd = os.open(name, _file_read_flags(), dir_fd=directory_fd)
            try:
                opened = os.fstat(file_fd)
                if _file_identity(opened) != _file_identity(before):
                    raise OSError("protected file identity changed before read")
                chunks: List[bytes] = []
                while True:
                    chunk = os.read(file_fd, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                after_fd = os.fstat(file_fd)
                if _file_identity(after_fd) != _file_identity(opened):
                    raise OSError("protected file changed during read")
            finally:
                os.close(file_fd)
            after_path = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if _file_identity(after_path) != _file_identity(before):
                raise OSError("protected file identity changed after read")
            raw = b"".join(chunks)
            if len(raw) != before.st_size:
                raise OSError("protected file size changed during read")
            return raw
        finally:
            os.close(directory_fd)
    except ApplyError:
        raise
    except (OSError, RuntimeError) as error:
        raise ApplySecurityError(security_code, str(error), str(path)) from error


def _parse_strict_request(raw: bytes) -> Dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ApplyValidationError(
            "request_json_invalid", "request must be UTF-8 JSON", "request"
        ) from error

    def reject_duplicate_pairs(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON object key: %s" % key)
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError("non-finite JSON number: %s" % value)

    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_constant,
        )
    except (TypeError, ValueError, RecursionError, json.JSONDecodeError) as error:
        raise ApplyValidationError(
            "request_json_invalid", str(error), "request"
        ) from error
    if not isinstance(value, dict):
        raise ApplyValidationError(
            "request_schema_invalid", "request must be a JSON object", "request"
        )
    try:
        canonical = canonical_json_bytes(value)
    except (UnicodeError, RecursionError) as error:
        raise ApplyValidationError(
            "request_json_invalid", str(error), "request"
        ) from error
    if raw != canonical:
        raise ApplyValidationError(
            "request_not_canonical",
            "request bytes must equal canonical JSON serialization",
            "request",
        )
    return value


def _resolved_directory(path: Path, code: str, label: str) -> Path:
    try:
        resolved = Path(path).resolve(strict=True)
        state = resolved.stat()
    except (OSError, RuntimeError) as error:
        raise ApplySecurityError(code, "%s is unavailable: %s" % (label, error)) from error
    if not stat.S_ISDIR(state.st_mode):
        raise ApplySecurityError(code, "%s must be a directory" % label, str(path))
    return resolved


def _paths_overlap(first: Path, second: Path) -> bool:
    for candidate, ancestor in ((first, second), (second, first)):
        try:
            candidate.relative_to(ancestor)
        except ValueError:
            continue
        return True
    first_parts = tuple(
        unicodedata.normalize("NFC", part.casefold()) for part in first.parts
    )
    second_parts = tuple(
        unicodedata.normalize("NFC", part.casefold()) for part in second.parts
    )
    return (
        first_parts[:len(second_parts)] == second_parts
        or second_parts[:len(first_parts)] == first_parts
    )


def _request_evidence_path(evidence_root: Path, request_path: Path) -> Path:
    supplied = Path(request_path)
    absolute = supplied if supplied.is_absolute() else evidence_root / supplied
    try:
        relative = absolute.relative_to(evidence_root)
    except ValueError as error:
        raise ApplySecurityError(
            "request_security_invalid",
            "request must be inside the evidence root",
            str(request_path),
        ) from error
    normalized = _normalized_relative_path(PurePosixPath(*relative.parts).as_posix())
    if normalized is None:
        raise ApplySecurityError(
            "request_security_invalid",
            "request must be a normalized descendant of the evidence root",
            str(request_path),
        )
    return evidence_root.joinpath(*PurePosixPath(normalized).parts)


def _validate_authority_key(
    path: Path,
    pinned_digest: str,
    *,
    root: Path,
    evidence_root: Path,
) -> bytes:
    if not _is_digest(pinned_digest):
        raise ApplyValidationError(
            "authority_key_fingerprint_invalid",
            "pinned key fingerprint must be canonical SHA-256",
            "pinned_key_sha256",
        )
    supplied = Path(path)
    if not supplied.is_absolute():
        raise ApplySecurityError(
            "authority_key_security_invalid",
            "authority key path must be absolute",
            str(path),
        )
    try:
        resolved = supplied.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ApplySecurityError(
            "authority_key_security_invalid", str(error), str(path)
        ) from error
    for forbidden, label in ((root, "repository"), (evidence_root, "evidence root")):
        try:
            resolved.relative_to(forbidden)
        except ValueError:
            pass
        else:
            raise ApplySecurityError(
                "authority_key_security_invalid",
                "authority key must be outside the %s" % label,
                str(path),
            )
    raw = _read_single_link_file(
        supplied,
        security_code="authority_key_security_invalid",
        require_private_owner=True,
    )
    if len(raw) < AUTHORITY_KEY_MIN_BYTES:
        raise ApplySecurityError(
            "authority_key_security_invalid",
            "authority key must contain at least 32 raw bytes",
            str(path),
        )
    if digest_bytes(raw) != pinned_digest:
        raise ApplyValidationError(
            "authority_key_fingerprint_mismatch",
            "authority key does not match the pinned fingerprint",
            "pinned_key_sha256",
        )
    return raw


def _output_relative_path(evidence_root: Path, output_path: Path) -> str:
    supplied = Path(output_path)
    absolute = supplied if supplied.is_absolute() else evidence_root / supplied
    try:
        relative = absolute.relative_to(evidence_root)
    except ValueError as error:
        raise ApplySecurityError(
            "output_security_invalid",
            "output must be inside the evidence root",
            str(output_path),
        ) from error
    normalized = _normalized_relative_path(PurePosixPath(*relative.parts).as_posix())
    if normalized is None:
        raise ApplySecurityError(
            "output_security_invalid",
            "output must be a normalized descendant of the evidence root",
            str(output_path),
        )
    return normalized


def _open_relative_parent(root: Path, relative: str) -> Tuple[int, str]:
    directory_fd = os.open(str(root), _directory_flags())
    parts = PurePosixPath(relative).parts
    try:
        for component in parts[:-1]:
            next_fd = os.open(component, _directory_flags(), dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        return directory_fd, parts[-1]
    except BaseException:
        os.close(directory_fd)
        raise


def _reserve_output(evidence_root: Path, output_path: Path) -> ReservedOutput:
    relative = _output_relative_path(evidence_root, output_path)
    directory_fd: Optional[int] = None
    file_fd: Optional[int] = None
    try:
        directory_fd, name = _open_relative_parent(evidence_root, relative)
        flags = (
            os.O_RDWR
            | os.O_CREAT
            | os.O_EXCL
            | os.O_NOFOLLOW
            | getattr(os, "O_CLOEXEC", 0)
        )
        file_fd = os.open(name, flags, 0o600, dir_fd=directory_fd)
        opened = os.fstat(file_fd)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise OSError("reserved output is not a single-link regular file")
        return ReservedOutput(
            directory_fd=directory_fd,
            file_fd=file_fd,
            name=name,
            identity=_file_identity(opened),
        )
    except FileExistsError as error:
        if file_fd is not None:
            os.close(file_fd)
        if directory_fd is not None:
            os.close(directory_fd)
        raise ApplySecurityError(
            "output_exists", "output already exists", str(output_path)
        ) from error
    except OSError as error:
        if file_fd is not None:
            os.close(file_fd)
        if directory_fd is not None:
            os.close(directory_fd)
        raise ApplySecurityError(
            "output_security_invalid", str(error), str(output_path)
        ) from error


def _cleanup_reserved_output(reserved: ReservedOutput) -> None:
    quarantine_name: Optional[str] = None
    try:
        opened = os.fstat(reserved.file_fd)
        try:
            quarantine_name = _move_to_private_quarantine(
                reserved.directory_fd,
                reserved.name,
                "receipt",
            )
        except FileNotFoundError:
            return
        moved = os.stat(
            quarantine_name,
            dir_fd=reserved.directory_fd,
            follow_symlinks=False,
        )
        if not _same_file_object(
            _file_identity(moved),
            _file_identity(opened),
        ):
            _restore_private_quarantine(
                reserved.directory_fd,
                quarantine_name,
                reserved.name,
            )
            quarantine_name = None
            raise OSError("reserved output name was replaced before cleanup")
        if not _unlink_if_identity_matches(
            reserved.directory_fd,
            quarantine_name,
            _file_identity(moved),
        ):
            _restore_private_quarantine(
                reserved.directory_fd,
                quarantine_name,
                reserved.name,
            )
            quarantine_name = None
            raise OSError("quarantined reserved output changed before cleanup")
        quarantine_name = None
        os.fsync(reserved.directory_fd)
    except FileNotFoundError:
        pass
    finally:
        try:
            os.close(reserved.file_fd)
        finally:
            os.close(reserved.directory_fd)


def _close_reserved_output(reserved: ReservedOutput) -> None:
    try:
        try:
            os.close(reserved.file_fd)
        except OSError:
            pass
    finally:
        try:
            os.close(reserved.directory_fd)
        except OSError:
            pass


def _read_open_leaf(directory_fd: int, name: str) -> Tuple[bytes, Tuple[int, ...], int]:
    before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise OSError("target must be a single-link regular file")
    file_fd = os.open(name, _file_read_flags(), dir_fd=directory_fd)
    try:
        opened = os.fstat(file_fd)
        if _file_identity(opened) != _file_identity(before):
            raise OSError("target identity changed before read")
        chunks: List[bytes] = []
        while True:
            chunk = os.read(file_fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after_fd = os.fstat(file_fd)
        if _file_identity(after_fd) != _file_identity(opened):
            raise OSError("target changed during read")
    finally:
        os.close(file_fd)
    after_path = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    if _file_identity(after_path) != _file_identity(before):
        raise OSError("target identity changed after read")
    raw = b"".join(chunks)
    if len(raw) != before.st_size:
        raise OSError("target size changed during read")
    return raw, _file_identity(before), stat.S_IMODE(before.st_mode)


def _read_target_state(root: Path, relative: str) -> TargetState:
    directory_fd: Optional[int] = None
    try:
        directory_fd, name = _open_relative_parent(root, relative)
        try:
            content, identity, mode = _read_open_leaf(directory_fd, name)
        except FileNotFoundError:
            content, identity, mode = b"", None, 0o600
        return TargetState(
            root=root,
            relative=relative,
            directory_fd=directory_fd,
            name=name,
            parent_identity=_directory_identity(os.fstat(directory_fd)),
            existed=identity is not None,
            identity=identity,
            mode=mode,
            content=content,
        )
    except OSError as error:
        if directory_fd is not None:
            os.close(directory_fd)
        raise ApplySecurityError(
            "target_security_invalid", str(error), relative
        ) from error


def _require_live_target_state(
    state: TargetState,
    *,
    expected_exists: bool,
    expected_content: bytes,
) -> None:
    live_directory_fd: Optional[int] = None
    try:
        live_directory_fd, live_name = _open_relative_parent(
            state.root, state.relative
        )
        live_parent = os.fstat(live_directory_fd)
        if (
            live_name != state.name
            or _directory_identity(live_parent) != state.parent_identity
        ):
            raise OSError("target parent chain no longer names the held directory")
        if expected_exists:
            live_content, _, _ = _read_open_leaf(live_directory_fd, live_name)
            if live_content != expected_content:
                raise OSError("live target bytes differ from the expected state")
        else:
            try:
                os.stat(
                    live_name,
                    dir_fd=live_directory_fd,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                pass
            else:
                raise OSError("live target is present for an absent expected state")
    except OSError as error:
        raise ApplyValidationError(
            "baseline_stale",
            "live target namespace changed during apply: %s" % error,
            state.relative,
        ) from error
    finally:
        if live_directory_fd is not None:
            os.close(live_directory_fd)


def _target_still_matches(state: TargetState) -> bool:
    try:
        current = os.stat(
            state.name,
            dir_fd=state.directory_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return not state.existed
    if not state.existed or state.identity is None:
        return False
    return _file_identity(current) == state.identity


def _same_file_object(
    first: Optional[Tuple[int, ...]],
    second: Optional[Tuple[int, ...]],
) -> bool:
    if first is None or second is None:
        return False
    return (
        first[0] == second[0]
        and first[1] == second[1]
        and first[6] == second[6]
    )


def _matches_exchange_identity(
    observed: Optional[Tuple[int, ...]],
    expected: Optional[Tuple[int, ...]],
) -> bool:
    if observed is None or expected is None:
        return False
    return all(
        observed[index] == expected[index]
        for index in (0, 1, 2, 3, 5, 6, 7)
    )


def _atomic_exchange(directory_fd: int, first: str, second: str) -> None:
    """Atomically exchange two names or fail closed when the host cannot do so."""

    first_bytes = os.fsencode(first)
    second_bytes = os.fsencode(second)
    library = ctypes.CDLL(None, use_errno=True)
    function = None
    if sys.platform == "darwin":
        function = getattr(library, "renameatx_np", None)
    elif sys.platform.startswith("linux"):
        function = getattr(library, "renameat2", None)
    if function is None:
        raise ApplySecurityError(
            "atomic_exchange_unavailable",
            "existing-target apply requires a host atomic rename-exchange primitive",
            second,
        )
    function.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    function.restype = ctypes.c_int
    ctypes.set_errno(0)
    result = function(
        directory_fd,
        first_bytes,
        directory_fd,
        second_bytes,
        0x00000002,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    unsupported = {
        errno.EINVAL,
        errno.ENOSYS,
        getattr(errno, "ENOTSUP", errno.EINVAL),
        getattr(errno, "EOPNOTSUPP", errno.EINVAL),
    }
    if error_number in unsupported:
        raise ApplySecurityError(
            "atomic_exchange_unavailable",
            "filesystem does not provide an atomic rename-exchange primitive",
            second,
        )
    raise OSError(error_number, os.strerror(error_number), second)


def _atomic_rename_noreplace(
    directory_fd: int,
    source: str,
    destination: str,
) -> None:
    """Atomically move one name only when the private destination is absent."""

    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    library = ctypes.CDLL(None, use_errno=True)
    function = None
    flag = 0
    if sys.platform == "darwin":
        function = getattr(library, "renameatx_np", None)
        flag = 0x00000004
    elif sys.platform.startswith("linux"):
        function = getattr(library, "renameat2", None)
        flag = 0x00000001
    if function is None:
        raise OSError(
            getattr(errno, "ENOTSUP", errno.EINVAL),
            "safe cleanup requires an atomic no-replace rename primitive",
            source,
        )
    function.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    function.restype = ctypes.c_int
    ctypes.set_errno(0)
    result = function(
        directory_fd,
        source_bytes,
        directory_fd,
        destination_bytes,
        flag,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number == errno.ENOENT:
        raise FileNotFoundError(error_number, os.strerror(error_number), source)
    if error_number == errno.EEXIST:
        raise FileExistsError(
            error_number,
            os.strerror(error_number),
            destination,
        )
    raise OSError(error_number, os.strerror(error_number), source)


def _move_to_private_quarantine(
    directory_fd: int,
    source: str,
    label: str,
) -> str:
    for _ in range(16):
        destination = ".keystone-owned-%s-%s-%s.quarantine" % (
            label,
            os.getpid(),
            secrets.token_hex(16),
        )
        try:
            _atomic_rename_noreplace(directory_fd, source, destination)
        except FileExistsError:
            continue
        return destination
    raise OSError("could not allocate a private quarantine name")


def _restore_private_quarantine(
    directory_fd: int,
    quarantine_name: str,
    public_name: str,
) -> None:
    try:
        _atomic_rename_noreplace(
            directory_fd,
            quarantine_name,
            public_name,
        )
    except FileExistsError as error:
        raise OSError(
            "public name was recreated; quarantined data was preserved as %s"
            % quarantine_name
        ) from error


def _discard_private_regular_entry(
    directory_fd: int,
    source_name: str,
    *,
    label: str,
    expected_content: bytes,
    expected_mode: int,
    expected_identity: Optional[Tuple[int, ...]],
) -> None:
    quarantine_name = _move_to_private_quarantine(
        directory_fd,
        source_name,
        label,
    )
    try:
        content, identity, mode = _read_open_leaf(
            directory_fd,
            quarantine_name,
        )
        if (
            content != expected_content
            or mode != expected_mode
            or not _matches_exchange_identity(identity, expected_identity)
        ):
            raise OSError("quarantined entry does not match the runner-owned file")
        if not _unlink_if_identity_matches(
            directory_fd,
            quarantine_name,
            identity,
        ):
            raise OSError("quarantined entry changed before private cleanup")
        os.fsync(directory_fd)
    except BaseException:
        try:
            os.stat(
                quarantine_name,
                dir_fd=directory_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            pass
        else:
            _restore_private_quarantine(
                directory_fd,
                quarantine_name,
                source_name,
            )
        raise


def _write_all(file_fd: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(file_fd, payload[offset:])
        if written <= 0:
            raise OSError("short write")
        offset += written


def _replace_target_bytes(
    state: TargetState,
    payload: bytes,
    mode: int,
    *,
    require_live_parent: bool = True,
) -> None:
    temp_name = ".keystone-owned-apply-%s-%s.tmp" % (
        os.getpid(),
        secrets.token_hex(16),
    )
    temp_fd: Optional[int] = None
    temp_exists = False
    try:
        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | os.O_NOFOLLOW
            | getattr(os, "O_CLOEXEC", 0)
        )
        temp_fd = os.open(temp_name, flags, 0o600, dir_fd=state.directory_fd)
        temp_exists = True
        os.fchmod(temp_fd, mode)
        _write_all(temp_fd, payload)
        os.fsync(temp_fd)
        created = os.fstat(temp_fd)
        if not stat.S_ISREG(created.st_mode) or created.st_nlink != 1:
            raise OSError("secure temporary target is not a single-link regular file")
        if require_live_parent:
            _require_live_target_state(
                state,
                expected_exists=state.existed,
                expected_content=state.content,
            )
        if not _target_still_matches(state):
            raise ApplyValidationError(
                "baseline_stale",
                "target changed after the apply-time baseline read",
                state.name,
            )
        if state.existed:
            temp_path_state = os.stat(
                temp_name,
                dir_fd=state.directory_fd,
                follow_symlinks=False,
            )
            if not _same_file_object(
                _file_identity(temp_path_state),
                _file_identity(created),
            ):
                raise OSError("secure temporary target identity changed before exchange")
            _atomic_exchange(state.directory_fd, temp_name, state.name)
            state.published_by_runner = True
            state.published_identity = _file_identity(created)
            state.backup_name = temp_name
            temp_exists = False
            displaced_path_state = os.stat(
                temp_name,
                dir_fd=state.directory_fd,
                follow_symlinks=False,
            )
            state.backup_entry_identity = _file_identity(displaced_path_state)
            displaced, displaced_identity, displaced_mode = _read_open_leaf(
                state.directory_fd,
                temp_name,
            )
            state.backup_content = displaced
            state.backup_mode = displaced_mode
            published, published_identity, published_mode = _read_open_leaf(
                state.directory_fd,
                state.name,
            )
            if (
                displaced != state.content
                or displaced_mode != state.mode
                or not _matches_exchange_identity(
                    displaced_identity,
                    state.identity,
                )
                or published != payload
                or published_mode != mode
                or not _matches_exchange_identity(
                    published_identity,
                    state.published_identity,
                )
            ):
                raise ApplyValidationError(
                    "baseline_stale",
                    "atomic publication displaced a target other than the planned baseline",
                    state.name,
                )
        else:
            os.close(temp_fd)
            temp_fd = None
            try:
                os.link(
                    temp_name,
                    state.name,
                    src_dir_fd=state.directory_fd,
                    dst_dir_fd=state.directory_fd,
                    follow_symlinks=False,
                )
            except FileExistsError as error:
                raise ApplyValidationError(
                    "baseline_stale",
                    "target appeared before absent-baseline publication",
                    state.name,
                ) from error
            state.published_by_runner = True
            os.unlink(temp_name, dir_fd=state.directory_fd)
            temp_exists = False
            _, state.published_identity, _ = _read_open_leaf(
                state.directory_fd,
                state.name,
            )
        os.fsync(state.directory_fd)
    finally:
        if temp_fd is not None:
            os.close(temp_fd)
        if temp_exists:
            try:
                os.unlink(temp_name, dir_fd=state.directory_fd)
            except FileNotFoundError:
                pass


def _unlink_if_identity_matches(
    directory_fd: int,
    name: str,
    expected_identity: Tuple[int, ...],
) -> bool:
    try:
        current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if _file_identity(current) != expected_identity:
        return False
    os.unlink(name, dir_fd=directory_fd)
    return True


def _rollback_existing_target(
    state: TargetState,
    expected_applied_digest: str,
) -> None:
    if state.backup_name is None or state.backup_entry_identity is None:
        raise OSError("atomic baseline backup is unavailable for rollback")
    backup_name = state.backup_name

    runner_live = False
    try:
        live, live_identity, live_mode = _read_open_leaf(
            state.directory_fd,
            state.name,
        )
        runner_live = (
            digest_bytes(live) == expected_applied_digest
            and live_mode == state.mode
            and _matches_exchange_identity(
                live_identity,
                state.published_identity,
            )
        )
    except OSError:
        runner_live = False

    if not runner_live:
        _discard_private_regular_entry(
            state.directory_fd,
            backup_name,
            label="concurrent-baseline",
            expected_content=state.content,
            expected_mode=state.mode,
            expected_identity=state.identity,
        )
        state.backup_name = None
        state.published_by_runner = False
        os.fsync(state.directory_fd)
        return

    backup_path_state = os.stat(
        backup_name,
        dir_fd=state.directory_fd,
        follow_symlinks=False,
    )
    if not _matches_exchange_identity(
        _file_identity(backup_path_state),
        state.backup_entry_identity,
    ):
        raise OSError("atomic rollback backup changed before exchange")
    if state.backup_content is not None:
        backup_content, backup_identity, backup_mode = _read_open_leaf(
            state.directory_fd,
            backup_name,
        )
        if (
            backup_content != state.backup_content
            or backup_mode != state.backup_mode
            or not _matches_exchange_identity(
                backup_identity,
                state.backup_entry_identity,
            )
        ):
            raise OSError("atomic rollback backup changed before exchange")

    _atomic_exchange(state.directory_fd, backup_name, state.name)
    try:
        restored_path_state = os.stat(
            state.name,
            dir_fd=state.directory_fd,
            follow_symlinks=False,
        )
        if not _matches_exchange_identity(
            _file_identity(restored_path_state),
            state.backup_entry_identity,
        ):
            raise OSError("atomic rollback restored a different live entry")
        if state.backup_content is not None:
            restored, restored_identity, restored_mode = _read_open_leaf(
                state.directory_fd,
                state.name,
            )
            if (
                restored != state.backup_content
                or restored_mode != state.backup_mode
                or not _matches_exchange_identity(
                    restored_identity,
                    state.backup_entry_identity,
                )
            ):
                raise OSError("atomic rollback restored altered live bytes")
        displaced, displaced_identity, displaced_mode = _read_open_leaf(
            state.directory_fd,
            backup_name,
        )
        if (
            digest_bytes(displaced) != expected_applied_digest
            or displaced_mode != state.mode
            or not _matches_exchange_identity(
                displaced_identity,
                state.published_identity,
            )
        ):
            raise OSError("atomic rollback displaced a non-runner entry")
    except BaseException as error:
        try:
            _atomic_exchange(state.directory_fd, backup_name, state.name)
            live_after = _file_identity(os.stat(
                state.name,
                dir_fd=state.directory_fd,
                follow_symlinks=False,
            ))
            backup_after = _file_identity(os.stat(
                backup_name,
                dir_fd=state.directory_fd,
                follow_symlinks=False,
            ))
            if not (
                _same_file_object(live_after, state.published_identity)
                and _same_file_object(
                    backup_after,
                    state.backup_entry_identity,
                )
            ):
                raise OSError(
                    "rollback recovery could not restore both exchanged names"
                )
        except BaseException as recovery_error:
            raise OSError(
                "atomic rollback validation failed and recovery was incomplete: %s"
                % recovery_error
            ) from error
        raise OSError(
            "atomic rollback validation failed; both entries were preserved"
        ) from error

    _discard_private_regular_entry(
        state.directory_fd,
        backup_name,
        label="rollback",
        expected_content=displaced,
        expected_mode=displaced_mode,
        expected_identity=displaced_identity,
    )
    state.backup_name = None
    state.published_by_runner = False
    os.fsync(state.directory_fd)


def _rollback_target(state: TargetState, expected_applied_digest: str) -> None:
    if state.existed:
        _rollback_existing_target(state, expected_applied_digest)
        return
    try:
        quarantine_name = _move_to_private_quarantine(
            state.directory_fd,
            state.name,
            "absent-rollback",
        )
    except FileNotFoundError:
        state.published_by_runner = False
        return
    try:
        current, identity, mode = _read_open_leaf(
            state.directory_fd,
            quarantine_name,
        )
        if (
            digest_bytes(current) != expected_applied_digest
            or mode != state.mode
            or not _matches_exchange_identity(identity, state.published_identity)
        ):
            raise OSError(
                "quarantined target does not match the runner-published file"
            )
        if not _unlink_if_identity_matches(
            state.directory_fd,
            quarantine_name,
            identity,
        ):
            raise OSError("quarantined target changed before private cleanup")
    except BaseException:
        try:
            os.stat(
                quarantine_name,
                dir_fd=state.directory_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            pass
        else:
            _restore_private_quarantine(
                state.directory_fd,
                quarantine_name,
                state.name,
            )
        raise
    state.published_by_runner = False
    os.fsync(state.directory_fd)


def _require_published_target_state(
    state: TargetState,
    expected_content: bytes,
) -> None:
    _require_live_target_state(
        state,
        expected_exists=True,
        expected_content=expected_content,
    )
    try:
        current, identity, mode = _read_open_leaf(
            state.directory_fd,
            state.name,
        )
    except OSError as error:
        raise ApplyValidationError(
            "baseline_stale",
            "published target changed before receipt: %s" % error,
            state.relative,
        ) from error
    if (
        current != expected_content
        or mode != state.mode
        or not _matches_exchange_identity(identity, state.published_identity)
    ):
        raise ApplyValidationError(
            "baseline_stale",
            "published target identity changed before receipt",
            state.relative,
        )


def _require_existing_backup_state(state: TargetState) -> None:
    if not state.existed:
        return
    if state.backup_name is None:
        raise ApplyIOError(
            "atomic_backup_missing",
            "existing-target apply lost its atomic baseline backup",
            state.relative,
        )
    try:
        content, identity, mode = _read_open_leaf(
            state.directory_fd,
            state.backup_name,
        )
    except OSError as error:
        raise ApplyValidationError(
            "baseline_stale",
            "atomic baseline backup changed before receipt: %s" % error,
            state.relative,
        ) from error
    if (
        content != state.content
        or mode != state.mode
        or not _matches_exchange_identity(identity, state.identity)
    ):
        raise ApplyValidationError(
            "baseline_stale",
            "atomic baseline backup changed before receipt",
            state.relative,
        )


def _discard_existing_backup(
    state: TargetState,
    expected_content: bytes,
) -> None:
    if not state.existed:
        return
    _require_published_target_state(state, expected_content)
    _require_existing_backup_state(state)
    if state.backup_name is None:
        raise OSError("atomic baseline backup disappeared before cleanup")
    backup_name = state.backup_name
    _discard_private_regular_entry(
        state.directory_fd,
        backup_name,
        label="baseline",
        expected_content=state.content,
        expected_mode=state.mode,
        expected_identity=state.identity,
    )
    state.backup_name = None


def _write_receipt_to_reserved_output(
    reserved: ReservedOutput,
    payload: bytes,
) -> None:
    opened = os.fstat(reserved.file_fd)
    if _file_identity(opened) != reserved.identity:
        raise OSError("reserved output identity changed before receipt write")
    _write_all(reserved.file_fd, payload)
    os.fsync(reserved.file_fd)
    after = os.fstat(reserved.file_fd)
    if not stat.S_ISREG(after.st_mode) or after.st_nlink != 1:
        raise OSError("receipt output is not a single-link regular file")
    os.lseek(reserved.file_fd, 0, os.SEEK_SET)
    chunks: List[bytes] = []
    while True:
        chunk = os.read(reserved.file_fd, 1024 * 1024)
        if not chunk:
            break
        chunks.append(chunk)
    if b"".join(chunks) != payload:
        raise OSError("receipt output reread does not match canonical bytes")
    path_state = os.stat(
        reserved.name,
        dir_fd=reserved.directory_fd,
        follow_symlinks=False,
    )
    if _file_identity(path_state) != _file_identity(after):
        raise OSError("receipt output identity changed after write")
    os.fsync(reserved.directory_fd)


def _build_envelope(
    *,
    validated: ValidatedApplyRequest,
    request_digest: str,
    resulting_digest: str,
    runner_digest: str,
    runtime_digest: str,
    evidence_root_digest: str,
    key: bytes,
    key_fingerprint: str,
    nonce: str,
) -> Dict[str, Any]:
    request = validated.request
    subject = {
        field: request[field]
        for field in (
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
        )
    }
    envelope: Dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "producer": PRODUCER,
        "status": "applied",
        "subject": subject,
    }
    receipt: Dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "trust_model": TRUST_MODEL,
        "command_id": COMMAND_ID,
        "runner_executable_digest": runner_digest,
        "runtime_digest": runtime_digest,
        "evidence_root_digest": evidence_root_digest,
        "request_digest": request_digest,
        "prior_receipt_digest": request["prior_receipt_digest"],
        "nonce": nonce,
        "authority_key_fingerprint": key_fingerprint,
        "patch_receipt": {
            "patch": validated.patch,
            "result": "applied",
            "resulting_digest": resulting_digest,
        },
    }
    derived_key = hashlib.sha256(_KEY_DERIVATION_LABEL + key).digest()
    payload = canonical_json_bytes({"envelope": envelope, "receipt": receipt})
    receipt["mac"] = "hmac-sha256:" + hmac.new(
        derived_key, payload, hashlib.sha256
    ).hexdigest()
    envelope["receipt"] = receipt
    return envelope


def apply_owned_surface_patch(
    *,
    root: Path,
    request_path: Path,
    evidence_root: Path,
    output_path: Path,
    authority_key: Path,
    pinned_key_sha256: str,
    allowed_owners: FrozenSet[str],
    runner_path: Path,
) -> Dict[str, Any]:
    """Apply exactly one validated owner patch and write its authority receipt."""

    _require_descriptor_security()
    if not isinstance(allowed_owners, frozenset) or not allowed_owners:
        raise ApplyValidationError(
            "owner_lane_invalid", "allowed_owners must be a non-empty frozenset"
        )
    if not allowed_owners <= _OWNERS:
        raise ApplyValidationError(
            "owner_lane_invalid", "allowed_owners contains an unknown owner"
        )
    resolved_root = _resolved_directory(
        Path(root), "repository_security_invalid", "repository root"
    )
    resolved_evidence_root = _resolved_directory(
        Path(evidence_root), "evidence_root_security_invalid", "evidence root"
    )
    if _paths_overlap(resolved_root, resolved_evidence_root):
        raise ApplySecurityError(
            "evidence_root_security_invalid",
            "repository root and evidence root must be disjoint",
            str(evidence_root),
        )
    secured_request_path = _request_evidence_path(
        resolved_evidence_root, Path(request_path)
    )
    request_raw = _read_single_link_file(
        secured_request_path, security_code="request_security_invalid"
    )
    request = _parse_strict_request(request_raw)
    validated = validate_apply_request(
        request,
        root=resolved_root,
        allowed_owners=allowed_owners,
    )
    key = _validate_authority_key(
        Path(authority_key),
        pinned_key_sha256,
        root=resolved_root,
        evidence_root=resolved_evidence_root,
    )
    runner_raw = _read_single_link_file(
        Path(runner_path),
        security_code="runner_security_invalid",
    )
    runtime_raw = _read_single_link_file(
        Path(__file__),
        security_code="runtime_security_invalid",
    )
    request_digest = digest_bytes(request_raw)
    runner_digest = digest_bytes(runner_raw)
    runtime_digest = digest_bytes(runtime_raw)
    evidence_digest = digest_json({
        "evidence_root": str(resolved_evidence_root),
    })
    nonce = "nonce:" + secrets.token_hex(32)

    reserved = _reserve_output(resolved_evidence_root, Path(output_path))
    target_state: Optional[TargetState] = None
    try:
        target_state = _read_target_state(resolved_root, validated.target_path)
        expected_presence = validated.patch["baseline_digest"] != "absent"
        if target_state.existed != expected_presence:
            raise ApplyValidationError(
                "baseline_stale",
                "target presence does not match the planned baseline",
                validated.target_path,
            )
        if expected_presence and digest_bytes(target_state.content) != validated.patch[
            "baseline_digest"
        ]:
            raise ApplyValidationError(
                "baseline_stale",
                "current target bytes do not match the planned baseline",
                validated.target_path,
            )
        _replace_target_bytes(
            target_state,
            validated.expected_bytes,
            target_state.mode,
        )
        resulting_bytes, _, _ = _read_open_leaf(
            target_state.directory_fd,
            target_state.name,
        )
        resulting_digest = digest_bytes(resulting_bytes)
        if resulting_digest != validated.patch["expected_after_digest"]:
            raise ApplyIOError(
                "resulting_digest_mismatch",
                "reread target bytes do not match expected_after_digest",
                validated.target_path,
            )
        envelope = _build_envelope(
            validated=validated,
            request_digest=request_digest,
            resulting_digest=resulting_digest,
            runner_digest=runner_digest,
            runtime_digest=runtime_digest,
            evidence_root_digest=evidence_digest,
            key=key,
            key_fingerprint=pinned_key_sha256,
            nonce=nonce,
        )
        _require_published_target_state(
            target_state,
            validated.expected_bytes,
        )
        _require_existing_backup_state(target_state)
        _write_receipt_to_reserved_output(reserved, canonical_json_bytes(envelope))
        _require_published_target_state(
            target_state,
            validated.expected_bytes,
        )
        _require_existing_backup_state(target_state)
        _discard_existing_backup(
            target_state,
            validated.expected_bytes,
        )
    except BaseException as error:
        rollback_error: Optional[BaseException] = None
        if target_state is not None and target_state.published_by_runner:
            try:
                _rollback_target(
                    target_state,
                    validated.patch["expected_after_digest"],
                )
            except BaseException as caught:
                rollback_error = caught
        try:
            _cleanup_reserved_output(reserved)
        except OSError as cleanup_error:
            if rollback_error is None:
                rollback_error = cleanup_error
        if target_state is not None:
            try:
                os.close(target_state.directory_fd)
            except OSError as close_error:
                if rollback_error is None:
                    rollback_error = close_error
        if rollback_error is not None:
            raise ApplyIOError(
                "rollback_failed",
                "apply failed and safe rollback was incomplete: %s" % rollback_error,
                validated.target_path,
            ) from error
        if isinstance(error, ApplyError):
            raise
        if isinstance(error, OSError):
            raise ApplyIOError(
                "apply_io_failed", str(error), validated.target_path
            ) from error
        raise
    _close_reserved_output(reserved)
    if target_state is not None:
        try:
            os.close(target_state.directory_fd)
        except OSError:
            pass
    return envelope


class _ApplyArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ApplySecurityError("invocation_invalid", message, "arguments")


def _diagnostic_envelope(
    status: str,
    diagnostic: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    diagnostics = [] if diagnostic is None else [dict(diagnostic)]
    return {
        "schema_version": 1,
        "status": status,
        "diagnostics": diagnostics,
        "summary": {
            "errors": len(diagnostics),
            "warnings": 0,
        },
    }


def _write_stdout_envelope(value: Mapping[str, Any]) -> None:
    sys.stdout.write(canonical_json_bytes(value).decode("utf-8") + "\n")


def run_cli(
    *,
    allowed_owners: FrozenSet[str],
    runner_path: Path,
    argv: Optional[Sequence[str]] = None,
) -> int:
    parser = _ApplyArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--authority-key", type=Path, required=True)
    parser.add_argument("--pinned-key-sha256", required=True)
    try:
        args = parser.parse_args(argv)
        apply_owned_surface_patch(
            root=args.root,
            request_path=args.request,
            evidence_root=args.evidence_root,
            output_path=args.output,
            authority_key=args.authority_key,
            pinned_key_sha256=args.pinned_key_sha256,
            allowed_owners=allowed_owners,
            runner_path=runner_path,
        )
    except ApplyError as error:
        diagnostic: Dict[str, Any] = {
            "code": error.code,
            "message": error.message,
            "severity": "error",
        }
        if error.path is not None:
            diagnostic["path"] = error.path
        status = "fail" if error.exit_code == 1 else "error"
        _write_stdout_envelope(_diagnostic_envelope(status, diagnostic))
        return error.exit_code
    _write_stdout_envelope(_diagnostic_envelope("pass"))
    return 0


__all__ = [
    "ApplyError",
    "ApplyIOError",
    "ApplySecurityError",
    "ApplyValidationError",
    "ValidatedApplyRequest",
    "apply_owned_surface_patch",
    "canonical_json_bytes",
    "digest_bytes",
    "digest_json",
    "replay_patch",
    "run_cli",
    "validate_apply_request",
]
