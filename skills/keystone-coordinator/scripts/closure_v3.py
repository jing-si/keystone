"""Phase-separated actual-state validation for Coordinator closure schema v3."""

import hashlib
import hmac
import json
import os
import re
import secrets
import stat
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

import closure_actual_state as actual_state
from closure_actual_state import (
    digest_json,
    normalize_relative_path,
    resolved_repository_root,
)
from closure_v2 import (
    diagnostic,
    package_runner_paths,
    validate_assignment_context_evidence,
    validate_finalization_evidence,
    validate_graph_sync_evidence,
    validate_sync_evidence,
)


Diagnostic = Dict[str, str]
EXECUTION_MODES = {"direct_execution", "orchestration"}
PURPOSES = {"investigate", "document_edit", "implement", "review", "verify"}
AUTHORITIES = {"read_only", "bounded_edit", "review_only", "verification"}
REPORT_STATUSES = {
    "DONE",
    "DONE_WITH_CONCERNS",
    "NEEDS_CONTEXT",
    "NEEDS_SCOPE_CHANGE",
    "BLOCKED",
}
PHASE_ACTORS = {"worker", "author", "repository_owner", "linker"}
WRITE_ACTORS = {"worker", "author", "repository_owner"}
CHANGE_KINDS = {"added", "modified", "deleted", "type_replaced"}
ABSENT_DIGEST = "absent"
PHASE_AUTHORITY_FIELDS = {"authority", "allowed_edit_scope", "excluded_scope"}
ACTOR_DELTA_FIELDS = {
    "actor",
    "authority",
    "allowed_edit_scope",
    "excluded_scope",
    "changed_paths",
    "artifact_deltas",
}
CHANGED_PATH_FIELDS = {
    "path",
    "change_kind",
    "before_entry_digest",
    "after_entry_digest",
}
ARTIFACT_DELTA_FIELDS = {
    "kind",
    "source_surface",
    "change_kind",
    "changed_locators",
    "semantic_summary",
    "baseline_digest",
    "resulting_digest",
    "graph_relevant",
}
LOCATOR_FIELDS = {
    "path",
    "heading",
    "symbol",
    "test_name",
    "config_key",
    "schema_name",
}
PHASE_CAPTURE_PRODUCER = "keystone-coordinator.phase-capture"
CAPTURE_REFERENCE_FIELDS = {"path", "digest"}
CAPTURE_ENVELOPE_FIELDS = {
    "schema_version",
    "producer",
    "phase_id",
    "parent_snapshot_digest",
    "snapshot_digest",
    "captured_at",
    "subject",
    "receipt",
}
CAPTURE_SUBJECT_FIELDS = {
    "repository_root_digest",
    "policy_digest",
    "assignment_id",
    "assignment_subject_digest",
    "context_digest",
}
ACCEPTANCE_EVENT_PRODUCER = "keystone-coordinator.acceptance-event"
ACCEPTANCE_EVENT_FIELDS = {
    "schema_version",
    "producer",
    "acceptance_ref",
    "accepted_steps",
    "accepted_at",
    "accepted_by",
    "subject",
    "receipt",
}
ACCEPTANCE_SUBJECT_FIELDS = {
    "repository_root_digest",
    "assignment_id",
    "assignment_digest",
    "context_digest",
    "policy_digest",
    "closure_target",
    "closure_step_ref",
    "pre_snapshot_digest",
    "observed_snapshot_digest",
}
HOST_RECEIPT_FIELDS = {
    "schema_version",
    "trust_model",
    "command_id",
    "executable_digest",
    "evidence_root_digest",
    "parent_evidence_digest",
    "nonce",
    "authority_key_fingerprint",
    "mac",
}
HOST_TRUST_MODEL = "trusted-host-hmac-sha256"
CAPTURE_COMMAND_ID = "keystone-coordinator.capture-assignment-snapshot"
ACCEPTANCE_COMMAND_ID = "keystone-coordinator.record-acceptance-event"
CAPTURE_EXECUTABLE_NAME = "capture_assignment_snapshot.py"
ACCEPTANCE_EXECUTABLE_NAME = "record_acceptance_event.py"
HMAC_PATTERN = re.compile(r"^hmac-sha256:[0-9a-f]{64}$")
NONCE_PATTERN = re.compile(r"^nonce:[0-9a-f]{64}$")
AUTHORITY_KEY_MIN_BYTES = 32
AUTHOR_EVIDENCE_BINDING_FIELDS = {
    "finalization_manifest_digest",
    "runner_envelope_digest",
    "source_snapshot_digest",
}
CAPTURE_TIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$"
)
DOCUMENT_ROOT_LINE_PATTERN = re.compile(r"^document_root[ ]*:[ ]*(.*)$")
DEFAULT_DOCUMENT_ROOT = "00_docs"
CLASSIFICATION_INPUT_FIELDS = {
    "schema_version",
    "delta_set_digest",
    "deltas",
    "source_context",
}
CLASSIFICATION_SOURCE_CONTEXT_FIELDS = {
    "repository_root_digest",
    "coverage",
    "sources",
}
CLASSIFICATION_COVERAGE_FIELDS = {
    "mode",
    "complete",
    "source_count",
    "source_path_digest",
}
CLASSIFICATION_OUTPUT_FIELDS = {
    "schema_version",
    "status",
    "disposition",
    "delta_set_digest",
    "source_generation_digest",
    "inspected_sources",
    "exclusion_evidence",
    "reason_codes",
    "diagnostics",
    "summary",
}
CLASSIFICATION_EXCLUSION_FIELDS = {
    "delta_index",
    "locator_index",
    "locator",
    "reason_code",
    "inspected_source_indexes",
}
CLASSIFICATION_DIAGNOSTIC_FIELDS = {"code", "message", "severity", "path"}
CLASSIFICATION_INSPECTED_FIELDS = {
    "regular_file": {"path", "type", "raw_byte_digest", "executable"},
    "absent": {"path", "type"},
    "symlink": {"path", "type", "symlink_target"},
    "directory": {"path", "type"},
    "special": {"path", "type"},
    "unreadable": {"path", "type"},
}
GRAPH_VALIDATION_MANIFEST_V2_FIELDS = {
    "schema_version",
    "sources",
    "transaction",
    "application_evidence",
}
GRAPH_VALIDATION_MANIFEST_V2_OPTIONAL_FIELDS = {"scope", "coverage"}
APPLICATION_EVIDENCE_FIELDS = {
    "schema_version",
    "transaction_id",
    "transaction_digest",
    "repository_root_digest",
    "assignment_id",
    "assignment_digest",
    "receipts",
}
APPLICATION_REFERENCE_FIELDS = {"path", "digest"}
APPLICATION_ENVELOPE_FIELDS = {
    "schema_version", "producer", "status", "subject", "receipt",
}
APPLICATION_SUBJECT_FIELDS = {
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
}
APPLICATION_RECEIPT_FIELDS = {
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
}
APPLICATION_PATCH_RECEIPT_FIELDS = {"patch", "result", "resulting_digest"}
APPLICATION_PLAN_FIELDS = (
    "schema_version",
    "transaction_id",
    "scope_ref",
    "input_deltas",
    "canonical_mutations",
    "surface_patches",
)


class DuplicateJsonKey(ValueError):
    pass


def _reject_duplicate_keys(pairs: Sequence[Any]) -> Dict[str, Any]:
    value: Dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJsonKey("duplicate JSON key: %s" % key)
        value[key] = item
    return value


def _reject_nonfinite_json(value: str) -> None:
    raise ValueError("non-finite JSON number is forbidden: %s" % value)


def _loads_json_strict(value: str) -> Any:
    return json.loads(
        value,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite_json,
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _digest(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    suffix = value[len("sha256:"):]
    return len(suffix) == 64 and all(character in "0123456789abcdef" for character in suffix)


def _evidence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_text(item) for item in value)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def _normalize_selector(value: Any) -> Optional[str]:
    if value == ".":
        return "."
    normalized = normalize_relative_path(value)
    if normalized is None or unicodedata.normalize("NFC", normalized) != normalized:
        return None
    return normalized


def _portable_path_parts(value: str) -> Tuple[str, ...]:
    if value == ".":
        return ()
    return tuple(
        unicodedata.normalize("NFC", part).casefold()
        for part in PurePosixPath(value).parts
    )


def _canonical_path_in_scope(path: str, selectors: Sequence[str]) -> bool:
    normalized = _normalize_selector(path)
    if normalized is None:
        return False
    path_parts = () if normalized == "." else PurePosixPath(normalized).parts
    for selector in selectors:
        normalized_selector = _normalize_selector(selector)
        if normalized_selector is None:
            continue
        selector_parts = (
            () if normalized_selector == "." else PurePosixPath(normalized_selector).parts
        )
        if not selector_parts or path_parts[:len(selector_parts)] == selector_parts:
            return True
    return False


def _portable_path_in_scope(path: str, selectors: Sequence[str]) -> bool:
    normalized = _normalize_selector(path)
    if normalized is None:
        return False
    path_parts = _portable_path_parts(normalized)
    for selector in selectors:
        normalized_selector = _normalize_selector(selector)
        if normalized_selector is None:
            continue
        selector_parts = _portable_path_parts(normalized_selector)
        if not selector_parts or path_parts[:len(selector_parts)] == selector_parts:
            return True
    return False


def _portable_path_overlaps_scope(path: str, selectors: Sequence[str]) -> bool:
    normalized = _normalize_selector(path)
    if normalized is None:
        return False
    path_parts = _portable_path_parts(normalized)
    for selector in selectors:
        normalized_selector = _normalize_selector(selector)
        if normalized_selector is None:
            continue
        selector_parts = _portable_path_parts(normalized_selector)
        if (
            not path_parts
            or not selector_parts
            or path_parts[:len(selector_parts)] == selector_parts
            or selector_parts[:len(path_parts)] == path_parts
        ):
            return True
    return False


def _unknown_fields(
    value: Mapping[str, Any], allowed: Set[str], path: str,
    diagnostics: List[Diagnostic],
) -> None:
    for field in sorted(set(value) - allowed):
        diagnostics.append(diagnostic(
            "unknown_field",
            "Unknown authority-bearing field %r is not allowed in schema v3." % field,
            "%s.%s" % (path, field) if path else field,
        ))


def _missing_fields(
    value: Mapping[str, Any], required: Set[str], path: str,
    diagnostics: List[Diagnostic],
) -> None:
    for field in sorted(required - set(value)):
        diagnostics.append(diagnostic(
            "required_field_missing",
            "Authoritative schema v3 field %r is required." % field,
            "%s.%s" % (path, field) if path else field,
        ))


def _validate_paths(
    value: Any, path: str, diagnostics: List[Diagnostic], *, allow_empty: bool = True,
) -> List[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        diagnostics.append(diagnostic(
            "path_list_invalid", "Expected an explicit normalized path array.", path,
        ))
        return []
    result: List[str] = []
    for index, raw in enumerate(value):
        normalized = _normalize_selector(raw)
        if normalized is None:
            diagnostics.append(diagnostic(
                "path_invalid",
                "Paths must be normalized repository-relative POSIX paths.",
                "%s[%d]" % (path, index),
            ))
        elif normalized in result:
            diagnostics.append(diagnostic(
                "path_duplicate", "Path entries must be unique.",
                "%s[%d]" % (path, index),
            ))
        elif any(
            _portable_path_parts(normalized) == _portable_path_parts(existing)
            for existing in result
        ):
            diagnostics.append(diagnostic(
                "path_casefold_collision",
                "Path entries must be unique under portable NFC case-fold comparison.",
                "%s[%d]" % (path, index),
            ))
        else:
            result.append(normalized)
    if result != sorted(result):
        diagnostics.append(diagnostic(
            "path_order_invalid", "Authority-bearing paths must use canonical sort order.", path,
        ))
    return result


def _snapshot_error(error: BaseException, path: str) -> Diagnostic:
    code = getattr(error, "code", "snapshot_invalid")
    error_path = getattr(error, "path", path) or path
    return diagnostic(str(code), str(error), str(error_path))


def _normalize_policy(value: Any) -> Any:
    normalizer = getattr(actual_state, "normalize_snapshot_policy_v3", None)
    if normalizer is None:
        raise RuntimeError("snapshot policy v3 runtime is unavailable")
    return normalizer(value)


def _parse_snapshot(value: Any) -> Any:
    parser = getattr(actual_state, "parse_repository_snapshot_v3", None)
    if parser is None:
        raise RuntimeError("snapshot wire v3 parser is unavailable")
    return parser(value)


def _capture_snapshot(
    root: Path, policy: Any, expected_absences: Sequence[str],
) -> Any:
    capture = getattr(actual_state, "capture_repository_snapshot_v3", None)
    if capture is None:
        raise RuntimeError("snapshot capture v3 runtime is unavailable")
    return capture(root, policy, expected_absences=expected_absences)


def _snapshot_wire(snapshot: Any) -> Mapping[str, Any]:
    serializer = getattr(snapshot, "to_wire", None)
    if serializer is None:
        serializer = getattr(snapshot, "wire", None)
    if serializer is None:
        raise TypeError("RepositorySnapshotV3 must expose to_wire()")
    wire = serializer()
    if not isinstance(wire, Mapping):
        raise TypeError("RepositorySnapshotV3.wire() must return an object")
    return wire


def _policy_wire(policy: Any) -> Mapping[str, Any]:
    serializer = getattr(policy, "to_wire", None)
    if serializer is None:
        serializer = getattr(policy, "wire", None)
    if serializer is None:
        raise TypeError("SnapshotPolicyV3 must expose to_wire()")
    wire = serializer()
    if not isinstance(wire, Mapping):
        raise TypeError("SnapshotPolicyV3.wire() must return an object")
    return wire


def phase_capture_root_digest(root: Path) -> str:
    """Return the canonical subject digest for one resolved repository root."""

    return digest_json({"repository_root": str(resolved_repository_root(root))})


def assignment_subject_digest(assignment: Mapping[str, Any]) -> str:
    """Digest the non-circular, authority-bearing schema-v3 assignment core."""

    fields = (
        "schema_version",
        "assignment_id",
        "execution_mode",
        "purpose",
        "authority",
        "goal",
        "context_pack",
        "injected_skills",
        "scope",
        "document_root",
        "snapshot_policy",
        "phase_authorities",
    )
    return digest_json({field: assignment.get(field) for field in fields})


def build_phase_capture_envelope(
    *, root: Path, phase_id: str, parent_snapshot_digest: str,
    snapshot: Any, captured_at: str, assignment_id: str, context_digest: str,
    assignment_subject_digest: str,
    evidence_root: Path, parent_evidence_digest: str,
    capture_authority_key: Path, capture_authority_key_digest: str,
) -> Dict[str, Any]:
    """Build a capture envelope attested by a protected Coordinator-host key."""

    if phase_id not in {
        "assignment", "worker", "pre_acceptance_closure", "post_acceptance",
    }:
        raise ValueError("phase_id is not a package-owned closure phase")
    if phase_id == "assignment":
        if parent_snapshot_digest != ABSENT_DIGEST:
            raise ValueError("assignment capture parent must be absent")
    elif not _digest(parent_snapshot_digest):
        raise ValueError("non-assignment capture parent must be a snapshot digest")
    if not _text(assignment_id):
        raise ValueError("assignment_id is required")
    if not _digest(assignment_subject_digest):
        raise ValueError("assignment_subject_digest must be canonical SHA-256")
    if not _digest(context_digest):
        raise ValueError("context_digest must be canonical SHA-256")
    captured_time = _parse_capture_time(captured_at)
    if captured_time is None:
        raise ValueError("captured_at must be canonical UTC RFC3339 text")
    wire = snapshot if isinstance(snapshot, Mapping) else _snapshot_wire(snapshot)
    snapshot_digest = getattr(snapshot, "snapshot_digest", None)
    if not _digest(snapshot_digest):
        snapshot_digest = wire.get("snapshot_digest")
    if not _digest(snapshot_digest) or not _digest(wire.get("policy_digest")):
        raise ValueError("snapshot wire lacks canonical snapshot/policy digests")
    root = resolved_repository_root(root)
    evidence_root = evidence_root.resolve(strict=True)
    key = validate_authority_key(
        capture_authority_key,
        capture_authority_key_digest,
        root=root,
        evidence_root=evidence_root,
    )
    envelope = {
        "schema_version": 1,
        "producer": PHASE_CAPTURE_PRODUCER,
        "phase_id": phase_id,
        "parent_snapshot_digest": parent_snapshot_digest,
        "snapshot_digest": snapshot_digest,
        "captured_at": captured_at,
        "subject": {
            "repository_root_digest": phase_capture_root_digest(root),
            "policy_digest": wire.get("policy_digest"),
            "assignment_id": assignment_id,
            "assignment_subject_digest": assignment_subject_digest,
            "context_digest": context_digest,
        },
    }
    envelope["receipt"] = _build_host_receipt(
        key=key,
        key_fingerprint=capture_authority_key_digest,
        command_id=CAPTURE_COMMAND_ID,
        evidence_root=evidence_root,
        parent_evidence_digest=parent_evidence_digest,
        envelope_without_receipt=envelope,
    )
    return envelope


def _parse_capture_time(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or CAPTURE_TIME_PATTERN.fullmatch(value) is None:
        return None
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None


def _evidence_file_identity(value: os.stat_result) -> Tuple[int, ...]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
        value.st_nlink,
        stat.S_IFMT(value.st_mode),
    )


def validate_authority_key(
    path: Path, pinned_digest: str, *, root: Path, evidence_root: Path,
) -> bytes:
    """Read one caller-provisioned host key through a strict external boundary."""

    if not _digest(pinned_digest):
        raise ValueError("authority key fingerprint must be canonical SHA-256")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise OSError("authority keys require no-follow descriptor APIs")
    supplied = Path(path)
    if not supplied.is_absolute():
        raise ValueError("authority key path must be absolute")
    resolved = supplied.resolve(strict=True)
    if supplied != resolved:
        raise ValueError("authority key path must not contain symlink aliases")
    for forbidden_root, label in (
        (root, "repository"),
        (evidence_root, "evidence root"),
    ):
        try:
            resolved.relative_to(forbidden_root)
        except ValueError:
            pass
        else:
            raise ValueError("authority key must be outside the %s" % label)

    directory_flags = (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    parts = resolved.parts
    directory_fd: Optional[int] = os.open(parts[0], directory_flags)
    try:
        for component in parts[1:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        before = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise OSError("authority key must be a single-link regular file")
        if stat.S_IMODE(before.st_mode) & 0o077:
            raise OSError("authority key must not grant group/world permissions")
        if hasattr(os, "geteuid") and before.st_uid != os.geteuid():
            raise OSError("authority key must be owned by the validating OS user")
        file_fd = os.open(parts[-1], file_flags, dir_fd=directory_fd)
        try:
            opened = os.fstat(file_fd)
            if _evidence_file_identity(opened) != _evidence_file_identity(before):
                raise OSError("authority key identity changed before read")
            chunks: List[bytes] = []
            while True:
                chunk = os.read(file_fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_fd = os.fstat(file_fd)
            if _evidence_file_identity(after_fd) != _evidence_file_identity(opened):
                raise OSError("authority key changed during read")
        finally:
            os.close(file_fd)
        after_path = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if _evidence_file_identity(after_path) != _evidence_file_identity(before):
            raise OSError("authority key changed after read")
        raw = b"".join(chunks)
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
    if len(raw) < AUTHORITY_KEY_MIN_BYTES:
        raise ValueError("authority key must contain at least 32 raw bytes")
    if actual_state.digest_bytes(raw) != pinned_digest:
        raise ValueError("authority key fingerprint mismatch")
    return raw


def _command_executable_digest(command_id: str) -> str:
    name = {
        CAPTURE_COMMAND_ID: CAPTURE_EXECUTABLE_NAME,
        ACCEPTANCE_COMMAND_ID: ACCEPTANCE_EXECUTABLE_NAME,
    }.get(command_id)
    if name is None:
        raise ValueError("unknown package command identity")
    path = Path(__file__).resolve().with_name(name)
    if not path.is_file() or path.is_symlink():
        raise OSError("package command executable is unavailable: %s" % name)
    return actual_state.digest_file(path)


def phase_evidence_root_digest(evidence_root: Path) -> str:
    return digest_json({"evidence_root": str(evidence_root.resolve(strict=True))})


def _derive_authority_hmac_key(key: bytes) -> bytes:
    return hashlib.sha256(b"keystone-host-key-v1\0" + key).digest()


def _receipt_mac(
    key: bytes, envelope_without_receipt: Mapping[str, Any],
    receipt_without_mac: Mapping[str, Any],
) -> str:
    payload = _canonical_json_bytes({
        "envelope": envelope_without_receipt,
        "receipt": receipt_without_mac,
    })
    derived_key = _derive_authority_hmac_key(key)
    return "hmac-sha256:" + hmac.new(
        derived_key, payload, hashlib.sha256,
    ).hexdigest()


def _build_host_receipt(
    *, key: bytes, key_fingerprint: str, command_id: str,
    evidence_root: Path, parent_evidence_digest: str,
    envelope_without_receipt: Mapping[str, Any],
) -> Dict[str, Any]:
    if parent_evidence_digest != ABSENT_DIGEST and not _digest(parent_evidence_digest):
        raise ValueError("parent_evidence_digest is invalid")
    receipt = {
        "schema_version": 1,
        "trust_model": HOST_TRUST_MODEL,
        "command_id": command_id,
        "executable_digest": _command_executable_digest(command_id),
        "evidence_root_digest": phase_evidence_root_digest(evidence_root),
        "parent_evidence_digest": parent_evidence_digest,
        "nonce": "nonce:" + secrets.token_hex(32),
        "authority_key_fingerprint": key_fingerprint,
    }
    receipt["mac"] = _receipt_mac(key, envelope_without_receipt, receipt)
    return receipt


def build_acceptance_event_envelope(
    *, root: Path, evidence_root: Path, assignment_id: str,
    assignment_digest: str, context_digest: str, policy_digest: str,
    closure_target: str, closure_step_ref: Optional[str],
    pre_snapshot_digest: str, observed_snapshot_digest: str,
    parent_evidence_digest: str, acceptance_ref: str,
    accepted_steps: Sequence[str], accepted_at: str, accepted_by: str,
    acceptance_authority_key: Path, acceptance_authority_key_digest: str,
) -> Dict[str, Any]:
    """Build one Main-owned acceptance event under a distinct protected key."""

    if (
        not _text(assignment_id)
        or not _digest(assignment_digest)
        or not _digest(context_digest)
        or not _digest(policy_digest)
    ):
        raise ValueError("acceptance assignment/context binding is invalid")
    if closure_target not in {"step", "work"}:
        raise ValueError("acceptance closure_target is invalid")
    if (
        (closure_target == "step" and not _text(closure_step_ref))
        or (closure_target == "work" and closure_step_ref is not None)
    ):
        raise ValueError("acceptance closure_step_ref is invalid")
    if not _digest(pre_snapshot_digest):
        raise ValueError("acceptance pre_snapshot_digest is invalid")
    if not _digest(observed_snapshot_digest):
        raise ValueError("acceptance observed_snapshot_digest is invalid")
    if observed_snapshot_digest != pre_snapshot_digest:
        raise ValueError(
            "Main acceptance requires an observed live snapshot equal to the pre snapshot"
        )
    if (
        not isinstance(accepted_steps, (list, tuple))
        or not accepted_steps
        or not all(_text(item) for item in accepted_steps)
        or list(accepted_steps) != sorted(set(accepted_steps))
    ):
        raise ValueError("accepted_steps must be a canonical unique Step array")
    if not _text(acceptance_ref) or accepted_by != "main":
        raise ValueError("acceptance_ref is required and accepted_by must be main")
    if _parse_capture_time(accepted_at) is None:
        raise ValueError("accepted_at must be canonical UTC RFC3339 text")
    root = resolved_repository_root(root)
    evidence_root = evidence_root.resolve(strict=True)
    key = validate_authority_key(
        acceptance_authority_key,
        acceptance_authority_key_digest,
        root=root,
        evidence_root=evidence_root,
    )
    envelope = {
        "schema_version": 1,
        "producer": ACCEPTANCE_EVENT_PRODUCER,
        "acceptance_ref": acceptance_ref,
        "accepted_steps": list(accepted_steps),
        "accepted_at": accepted_at,
        "accepted_by": accepted_by,
        "subject": {
            "repository_root_digest": phase_capture_root_digest(root),
            "assignment_id": assignment_id,
            "assignment_digest": assignment_digest,
            "context_digest": context_digest,
            "policy_digest": policy_digest,
            "closure_target": closure_target,
            "closure_step_ref": closure_step_ref,
            "pre_snapshot_digest": pre_snapshot_digest,
            "observed_snapshot_digest": observed_snapshot_digest,
        },
    }
    envelope["receipt"] = _build_host_receipt(
        key=key,
        key_fingerprint=acceptance_authority_key_digest,
        command_id=ACCEPTANCE_COMMAND_ID,
        evidence_root=evidence_root,
        parent_evidence_digest=parent_evidence_digest,
        envelope_without_receipt=envelope,
    )
    return envelope


def _validate_host_receipt(
    envelope: Mapping[str, Any], *, key: Optional[bytes],
    key_fingerprint: Any, command_id: str, evidence_root: Path,
    parent_evidence_digest: Any, seen_nonces: Set[str],
    diagnostics: List[Diagnostic], path: str,
) -> None:
    receipt = _mapping(envelope.get("receipt"))
    _unknown_fields(receipt, HOST_RECEIPT_FIELDS, path, diagnostics)
    _missing_fields(receipt, HOST_RECEIPT_FIELDS, path, diagnostics)
    if type(receipt.get("schema_version")) is not int or receipt.get("schema_version") != 1:
        diagnostics.append(diagnostic(
            "host_receipt_invalid", "Host receipt schema_version must be 1.",
            path + ".schema_version",
        ))
    if receipt.get("trust_model") != HOST_TRUST_MODEL:
        diagnostics.append(diagnostic(
            "host_receipt_invalid", "Host receipt trust model is invalid.",
            path + ".trust_model",
        ))
    if receipt.get("command_id") != command_id:
        diagnostics.append(diagnostic(
            "host_receipt_command_mismatch",
            "Host receipt command identity does not match the evidence type.",
            path + ".command_id",
        ))
    try:
        executable_digest = _command_executable_digest(command_id)
    except (OSError, RuntimeError, ValueError) as error:
        diagnostics.append(diagnostic(
            "host_receipt_executable_unavailable", str(error),
            path + ".executable_digest",
        ))
        executable_digest = None
    if receipt.get("executable_digest") != executable_digest:
        diagnostics.append(diagnostic(
            "host_receipt_executable_mismatch",
            "Host receipt is not bound to the current package command bytes.",
            path + ".executable_digest",
        ))
    try:
        expected_evidence_root_digest = phase_evidence_root_digest(evidence_root)
    except (OSError, RuntimeError, ValueError) as error:
        diagnostics.append(diagnostic(
            "host_receipt_evidence_root_invalid", str(error),
            path + ".evidence_root_digest",
        ))
        expected_evidence_root_digest = None
    if receipt.get("evidence_root_digest") != expected_evidence_root_digest:
        diagnostics.append(diagnostic(
            "host_receipt_evidence_root_mismatch",
            "Host receipt belongs to a different evidence root.",
            path + ".evidence_root_digest",
        ))
    if receipt.get("parent_evidence_digest") != parent_evidence_digest:
        diagnostics.append(diagnostic(
            "host_receipt_parent_mismatch",
            "Host receipt does not continue the immutable evidence chain.",
            path + ".parent_evidence_digest",
        ))
    if (
        receipt.get("authority_key_fingerprint") != key_fingerprint
        or not _digest(receipt.get("authority_key_fingerprint"))
    ):
        diagnostics.append(diagnostic(
            "host_receipt_key_mismatch",
            "Host receipt is not bound to the pinned authority key.",
            path + ".authority_key_fingerprint",
        ))
    nonce = receipt.get("nonce")
    if not isinstance(nonce, str) or NONCE_PATTERN.fullmatch(nonce) is None:
        diagnostics.append(diagnostic(
            "host_receipt_nonce_invalid", "Host receipt nonce is invalid.",
            path + ".nonce",
        ))
    elif nonce in seen_nonces:
        diagnostics.append(diagnostic(
            "host_receipt_nonce_reused",
            "Each trusted-host evidence event requires a fresh nonce.",
            path + ".nonce",
        ))
    else:
        seen_nonces.add(nonce)
    mac = receipt.get("mac")
    if not isinstance(mac, str) or HMAC_PATTERN.fullmatch(mac) is None:
        diagnostics.append(diagnostic(
            "host_receipt_mac_invalid", "Host receipt MAC is invalid.", path + ".mac",
        ))
        return
    if key is None:
        diagnostics.append(diagnostic(
            "host_receipt_key_unavailable",
            "Pinned host authority key is unavailable for receipt verification.", path,
        ))
        return
    unsigned_envelope = dict(envelope)
    unsigned_envelope.pop("receipt", None)
    unsigned_receipt = dict(receipt)
    unsigned_receipt.pop("mac", None)
    expected_mac = _receipt_mac(key, unsigned_envelope, unsigned_receipt)
    if not hmac.compare_digest(mac, expected_mac):
        diagnostics.append(diagnostic(
            "host_receipt_mac_invalid",
            "Host receipt MAC does not authenticate the exact evidence envelope.",
            path + ".mac",
        ))


def _read_immutable_evidence_bytes(
    evidence_root: Path, relative: str, path: str,
    diagnostics: List[Diagnostic],
) -> Optional[bytes]:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        diagnostics.append(diagnostic(
            "phase_capture_evidence_security_unavailable",
            "Immutable phase evidence requires no-follow descriptor APIs.", path,
        ))
        return None
    directory_flags = (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    parts = PurePosixPath(relative).parts
    directory_fd: Optional[int] = None
    try:
        directory_fd = os.open(str(evidence_root), directory_flags)
        for component in parts[:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
            directory_stat = os.fstat(directory_fd)
            if not stat.S_ISDIR(directory_stat.st_mode):
                raise OSError("phase capture evidence ancestor is not a directory")

        before = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode):
            raise OSError("phase capture evidence must be a regular file")
        if before.st_nlink != 1:
            raise OSError("phase capture evidence must have exactly one hard link")
        file_fd = os.open(parts[-1], file_flags, dir_fd=directory_fd)
        try:
            opened = os.fstat(file_fd)
            if _evidence_file_identity(opened) != _evidence_file_identity(before):
                raise OSError("phase capture evidence identity changed before read")
            chunks: List[bytes] = []
            while True:
                chunk = os.read(file_fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_fd = os.fstat(file_fd)
            if _evidence_file_identity(after_fd) != _evidence_file_identity(opened):
                raise OSError("phase capture evidence changed during read")
        finally:
            os.close(file_fd)
        after_path = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if _evidence_file_identity(after_path) != _evidence_file_identity(before):
            raise OSError("phase capture evidence changed after read")
        raw = b"".join(chunks)
        if len(raw) != before.st_size:
            raise OSError("phase capture evidence size changed during read")
        return raw
    except OSError as error:
        diagnostics.append(diagnostic(
            "phase_capture_evidence_unreadable", str(error), path,
        ))
        return None
    finally:
        if directory_fd is not None:
            os.close(directory_fd)


def package_classification_runner_path() -> Path:
    """Return the canonical package-owned Linker classification entrypoint."""

    package_skills = Path(__file__).resolve().parents[2]
    return (
        package_skills
        / "keystone-linker"
        / "scripts"
        / "run_graph_classification.py"
    )


def _classification_input(
    root: Path, deltas: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    projected = [dict(item) for item in deltas]
    sources = sorted({str(item.get("source_surface")) for item in projected})
    return {
        "schema_version": 1,
        "delta_set_digest": digest_json(projected),
        "deltas": projected,
        "source_context": {
            "repository_root_digest": digest_json(
                str(resolved_repository_root(root))
            ),
            "coverage": {
                "mode": "delta_set",
                "complete": True,
                "source_count": len(sources),
                "source_path_digest": digest_json(sources),
            },
            "sources": sources,
        },
    }


def _read_classification_evidence(
    evidence_root: Path, relative: Any, expected_digest: Any, path: str,
    diagnostics: List[Diagnostic],
) -> Tuple[Optional[Mapping[str, Any]], Optional[bytes]]:
    normalized = normalize_relative_path(relative)
    if normalized is None or normalized == ".":
        diagnostics.append(diagnostic(
            "evidence_path_invalid",
            "Classification evidence path must be repository-independent relative evidence.",
            path,
        ))
        return None, None
    if not _digest(expected_digest):
        diagnostics.append(diagnostic(
            "evidence_digest_invalid",
            "Classification evidence requires a canonical raw-byte digest.",
            path,
        ))
        return None, None
    raw = _read_immutable_evidence_bytes(
        evidence_root, normalized, path, diagnostics,
    )
    if raw is None:
        return None, None
    if actual_state.digest_bytes(raw) != expected_digest:
        diagnostics.append(diagnostic(
            "evidence_digest_mismatch",
            "Classification evidence raw bytes do not match the recorded digest.",
            path,
        ))
    try:
        payload = _loads_json_strict(raw.decode("utf-8"))
    except (
        UnicodeError,
        json.JSONDecodeError,
        DuplicateJsonKey,
        TypeError,
        ValueError,
    ) as error:
        diagnostics.append(diagnostic(
            "evidence_unreadable", str(error), path,
        ))
        return None, raw
    if not isinstance(payload, Mapping):
        diagnostics.append(diagnostic(
            "evidence_invalid", "Classification evidence must be a JSON object.", path,
        ))
        return None, raw
    if raw != _canonical_json_bytes(payload):
        diagnostics.append(diagnostic(
            "classification_evidence_noncanonical",
            "Classification evidence must use canonical JSON bytes.",
            path,
        ))
    return payload, raw


def _valid_classification_input_shape(value: Any) -> bool:
    if not isinstance(value, Mapping) or set(value) != CLASSIFICATION_INPUT_FIELDS:
        return False
    if type(value.get("schema_version")) is not int or value.get("schema_version") != 1:
        return False
    if not _digest(value.get("delta_set_digest")) or not isinstance(value.get("deltas"), list):
        return False
    context = value.get("source_context")
    if not isinstance(context, Mapping) or set(context) != CLASSIFICATION_SOURCE_CONTEXT_FIELDS:
        return False
    if not _digest(context.get("repository_root_digest")):
        return False
    sources = context.get("sources")
    if (
        not isinstance(sources, list)
        or not all(normalize_relative_path(item) is not None for item in sources)
        or sources != sorted(set(sources))
    ):
        return False
    coverage = context.get("coverage")
    return bool(
        isinstance(coverage, Mapping)
        and set(coverage) == CLASSIFICATION_COVERAGE_FIELDS
        and coverage.get("mode") == "delta_set"
        and type(coverage.get("complete")) is bool
        and type(coverage.get("source_count")) is int
        and coverage.get("source_count") == len(sources)
        and _digest(coverage.get("source_path_digest"))
        and coverage.get("source_path_digest") == digest_json(sources)
    )


def _valid_inspected_sources(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    paths: List[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            return False
        source_type = item.get("type")
        expected_fields = CLASSIFICATION_INSPECTED_FIELDS.get(source_type)
        if expected_fields is None or set(item) != expected_fields:
            return False
        path = normalize_relative_path(item.get("path"))
        if path is None:
            return False
        paths.append(path)
        if source_type == "regular_file" and (
            not _digest(item.get("raw_byte_digest"))
            or type(item.get("executable")) is not bool
        ):
            return False
        if source_type == "symlink" and not _text(item.get("symlink_target")):
            return False
    return paths == sorted(set(paths))


def _valid_classification_output(
    value: Any, returncode: int,
    classification_input: Optional[Mapping[str, Any]] = None,
) -> bool:
    if not isinstance(value, Mapping) or set(value) != CLASSIFICATION_OUTPUT_FIELDS:
        return False
    if type(value.get("schema_version")) is not int or value.get("schema_version") != 1:
        return False
    expected_status = {0: "pass", 1: "fail", 2: "error"}.get(returncode)
    if value.get("status") != expected_status:
        return False
    if value.get("disposition") not in {"required", "not_applicable", "deferred"}:
        return False
    if value.get("delta_set_digest") != "absent" and not _digest(
        value.get("delta_set_digest")
    ):
        return False
    if value.get("source_generation_digest") != "absent" and not _digest(
        value.get("source_generation_digest")
    ):
        return False
    if not _valid_inspected_sources(value.get("inspected_sources")):
        return False
    exclusion_evidence = value.get("exclusion_evidence")
    if not isinstance(exclusion_evidence, list):
        return False
    inspected_sources = value["inspected_sources"]
    covered_locators = []
    for item in exclusion_evidence:
        if not isinstance(item, Mapping) or set(item) != CLASSIFICATION_EXCLUSION_FIELDS:
            return False
        delta_index = item.get("delta_index")
        locator_index = item.get("locator_index")
        source_indexes = item.get("inspected_source_indexes")
        locator = item.get("locator")
        if (
            type(delta_index) is not int
            or delta_index < 0
            or type(locator_index) is not int
            or locator_index < 0
            or not isinstance(locator, Mapping)
            or "path" not in locator
            or set(locator) - LOCATOR_FIELDS
            or normalize_relative_path(locator.get("path")) is None
            or any(not _text(field) for field in locator.values())
            or item.get("reason_code") != "added_plain_unowned_source"
            or not isinstance(source_indexes, list)
            or not source_indexes
            or source_indexes != sorted(set(source_indexes))
            or any(
                type(index) is not int
                or index < 0
                or index >= len(inspected_sources)
                for index in source_indexes
            )
        ):
            return False
        if classification_input is not None:
            deltas = classification_input.get("deltas")
            if not isinstance(deltas, list) or delta_index >= len(deltas):
                return False
            delta = deltas[delta_index]
            locators = delta.get("changed_locators") if isinstance(delta, Mapping) else None
            if (
                not isinstance(locators, list)
                or locator_index >= len(locators)
                or locator != locators[locator_index]
            ):
                return False
            source = delta.get("source_surface")
            expected_paths = {source, str(source) + ".keystone.json"}
            if any(
                inspected_sources[index].get("path") not in expected_paths
                for index in source_indexes
            ):
                return False
        covered_locators.append((delta_index, locator_index))
    reason_codes = value.get("reason_codes")
    if (
        not isinstance(reason_codes, list)
        or not reason_codes
        or not all(_text(item) for item in reason_codes)
        or reason_codes != sorted(set(reason_codes))
    ):
        return False
    diagnostics = value.get("diagnostics")
    if not isinstance(diagnostics, list) or not all(
        isinstance(item, Mapping)
        and set(item) == CLASSIFICATION_DIAGNOSTIC_FIELDS
        and _text(item.get("code"))
        and _text(item.get("message"))
        and item.get("severity") in {"error", "warning"}
        and _text(item.get("path"))
        for item in diagnostics
    ):
        return False
    summary = value.get("summary")
    if (
        not isinstance(summary, Mapping)
        or set(summary) != {"errors", "warnings"}
        or type(summary.get("errors")) is not int
        or type(summary.get("warnings")) is not int
    ):
        return False
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    if summary != {"errors": errors, "warnings": warnings}:
        return False
    if value.get("status") == "pass":
        if diagnostics or value.get("disposition") not in {
            "required", "not_applicable",
        }:
            return False
        if value.get("disposition") == "required":
            return not exclusion_evidence
        if reason_codes == ["empty_delta_set"]:
            return not exclusion_evidence and bool(
                classification_input is None
                or classification_input.get("deltas") == []
            )
        if reason_codes != ["added_plain_unowned_source"]:
            return False
        if classification_input is None:
            return bool(exclusion_evidence)
        expected_coverage = [
            (delta_index, locator_index)
            for delta_index, delta in enumerate(classification_input["deltas"])
            for locator_index, _locator in enumerate(delta["changed_locators"])
        ]
        return covered_locators == expected_coverage
    if exclusion_evidence:
        return False
    return value.get("disposition") == "deferred"


def _run_classification(
    runner: Path, root: Path, manifest: Mapping[str, Any], timeout_seconds: float,
    diagnostics: List[Diagnostic], path: str,
) -> Optional[Mapping[str, Any]]:
    try:
        runner_identity = runner.lstat()
        resolved_runner = runner.resolve(strict=True)
    except OSError:
        runner_identity = None
        resolved_runner = None
    if (
        runner_identity is None
        or resolved_runner != runner
        or not stat.S_ISREG(runner_identity.st_mode)
        or runner_identity.st_nlink != 1
    ):
        diagnostics.append(diagnostic(
            "linker_runner_unavailable",
            "Package-owned Linker classification runner must be a single-link regular file "
            "without symlink aliases.",
            path,
        ))
        return None
    with tempfile.TemporaryDirectory(
        prefix="keystone-coordinator-classification-"
    ) as directory:
        manifest_path = Path(directory) / "classification-input.json"
        manifest_path.write_bytes(_canonical_json_bytes(manifest))
        runner_environment = {"PATH": os.defpath}
        for name in ("SYSTEMROOT", "WINDIR"):
            if name in os.environ:
                runner_environment[name] = os.environ[name]
        try:
            process = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(runner),
                    "--root",
                    str(root),
                    "--manifest",
                    str(manifest_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=runner_environment,
            )
        except subprocess.TimeoutExpired:
            diagnostics.append(diagnostic(
                "runner_timeout", "Linker classification runner timed out.", path,
            ))
            return None
        except (OSError, subprocess.SubprocessError) as error:
            diagnostics.append(diagnostic(
                "runner_execution_failed", str(error), path,
            ))
            return None
    try:
        payload = _loads_json_strict(process.stdout)
    except (
        json.JSONDecodeError,
        DuplicateJsonKey,
        TypeError,
        ValueError,
    ):
        diagnostics.append(diagnostic(
            "runner_output_malformed",
            "Linker classification runner output is not strict JSON.",
            path,
        ))
        return None
    if not _valid_classification_output(payload, process.returncode, manifest):
        diagnostics.append(diagnostic(
            "runner_output_malformed",
            "Linker classification runner envelope and exit code are inconsistent.",
            path,
        ))
        return None
    if payload.get("status") == "error":
        diagnostics.append(diagnostic(
            "runner_reported_error",
            "Linker classification runner reported an execution error.",
            path,
        ))
    return payload


def _application_plan_digest(transaction: Mapping[str, Any]) -> str:
    projection = {
        field: transaction.get(field) for field in APPLICATION_PLAN_FIELDS
    }
    return digest_json(projection)


def _graph_delta_projection(delta: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "kind": delta.get("kind"),
        "source_surface": delta.get("source_surface"),
        "changed_locators": delta.get("changed_locators"),
        "semantic_summary": delta.get("semantic_summary"),
        "baseline_digest": delta.get("baseline_digest"),
        "graph_relevant": delta.get("graph_relevant"),
    }


def _read_graph_validation_manifest_v3(
    evidence_root: Path, relative: Any, expected_digest: Any,
    diagnostics: List[Diagnostic], path: str, *, require_canonical: bool = False,
) -> Tuple[Optional[Mapping[str, Any]], Optional[bytes]]:
    normalized = normalize_relative_path(relative)
    if normalized is None or normalized == ".":
        diagnostics.append(diagnostic(
            "evidence_path_invalid",
            "Graph validation evidence path must be normalized and relative.",
            path,
        ))
        return None, None
    if not _digest(expected_digest):
        diagnostics.append(diagnostic(
            "evidence_digest_invalid",
            "Graph validation evidence requires a canonical raw digest.",
            path,
        ))
        return None, None
    raw = _read_immutable_evidence_bytes(
        evidence_root, normalized, path, diagnostics,
    )
    if raw is None:
        return None, None
    if actual_state.digest_bytes(raw) != expected_digest:
        diagnostics.append(diagnostic(
            "evidence_digest_mismatch",
            "Graph validation manifest raw bytes do not match the recorded digest.",
            path,
        ))
    try:
        payload = _loads_json_strict(raw.decode("utf-8"))
    except (
        UnicodeError,
        json.JSONDecodeError,
        DuplicateJsonKey,
        TypeError,
        ValueError,
    ) as error:
        diagnostics.append(diagnostic(
            "evidence_unreadable", str(error), path,
        ))
        return None, raw
    if not isinstance(payload, Mapping):
        diagnostics.append(diagnostic(
            "evidence_invalid",
            "Graph validation manifest must be a JSON object.",
            path,
        ))
        return None, raw
    if require_canonical and raw != _canonical_json_bytes(payload):
        diagnostics.append(diagnostic(
            "graph_validation_manifest_noncanonical",
            "Graph validation manifest must use canonical JSON bytes.",
            path,
        ))
    return payload, raw


def _valid_graph_runner_output(value: Any, returncode: int) -> bool:
    if not isinstance(value, Mapping):
        return False
    fields = {"schema_version", "status", "diagnostics", "summary"}
    if "coverage" in value:
        fields.add("coverage")
        if not isinstance(value.get("coverage"), Mapping):
            return False
    if set(value) != fields:
        return False
    if type(value.get("schema_version")) is not int or value.get(
        "schema_version"
    ) != 1:
        return False
    expected_status = {0: "pass", 1: "fail", 2: "error"}.get(returncode)
    if value.get("status") != expected_status:
        return False
    runner_diagnostics = value.get("diagnostics")
    summary = value.get("summary")
    if not isinstance(runner_diagnostics, list) or not isinstance(summary, Mapping):
        return False
    for item in runner_diagnostics:
        if (
            not isinstance(item, Mapping)
            or not {"code", "message", "severity"} <= set(item)
            or set(item) - {"code", "message", "severity", "path", "locator"}
            or not _text(item.get("code"))
            or not _text(item.get("message"))
            or item.get("severity") not in {"error", "warning"}
        ):
            return False
    errors = sum(item["severity"] == "error" for item in runner_diagnostics)
    warnings = sum(item["severity"] == "warning" for item in runner_diagnostics)
    return summary == {"errors": errors, "warnings": warnings}


def _run_graph_validation_v3(
    runner: Path, root: Path, manifest_bytes: bytes, evidence_root: Path,
    owner_keys: Mapping[str, Path], owner_key_digests: Mapping[str, str],
    timeout_seconds: float, diagnostics: List[Diagnostic], path: str,
) -> Optional[Mapping[str, Any]]:
    try:
        identity = runner.lstat()
        resolved = runner.resolve(strict=True)
    except OSError:
        identity = None
        resolved = None
    if (
        identity is None
        or resolved != runner
        or not stat.S_ISREG(identity.st_mode)
        or identity.st_nlink != 1
    ):
        diagnostics.append(diagnostic(
            "linker_runner_unavailable",
            "Package-owned Linker runner must be a single-link regular file.",
            path,
        ))
        return None
    with tempfile.TemporaryDirectory(
        prefix="keystone-coordinator-graph-validation-"
    ) as directory:
        manifest_path = Path(directory) / "graph-validation.json"
        manifest_path.write_bytes(manifest_bytes)
        command = [
            sys.executable,
            "-I",
            str(runner),
            "--root",
            str(root),
            "--manifest",
            str(manifest_path),
            "--evidence-root",
            str(evidence_root),
        ]
        for owner in sorted(owner_keys):
            command.extend((
                "--owner-key", "%s=%s" % (owner, owner_keys[owner]),
            ))
        for owner in sorted(owner_key_digests):
            command.extend((
                "--owner-key-sha256",
                "%s=%s" % (owner, owner_key_digests[owner]),
            ))
        environment = {"PATH": os.defpath}
        for name in ("SYSTEMROOT", "WINDIR"):
            if name in os.environ:
                environment[name] = os.environ[name]
        try:
            process = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            diagnostics.append(diagnostic(
                "runner_timeout", "Linker graph validation timed out.", path,
            ))
            return None
        except (OSError, subprocess.SubprocessError) as error:
            diagnostics.append(diagnostic(
                "runner_execution_failed", str(error), path,
            ))
            return None
    try:
        payload = _loads_json_strict(process.stdout)
    except (
        json.JSONDecodeError,
        DuplicateJsonKey,
        TypeError,
        ValueError,
    ):
        diagnostics.append(diagnostic(
            "runner_output_malformed",
            "Linker graph validation output is not strict JSON.",
            path,
        ))
        return None
    if not _valid_graph_runner_output(payload, process.returncode):
        diagnostics.append(diagnostic(
            "runner_output_malformed",
            "Linker graph validation envelope and exit code are inconsistent.",
            path,
        ))
        return None
    if payload.get("status") == "error":
        diagnostics.append(diagnostic(
            "runner_reported_error",
            "Linker graph validation reported an execution error.",
            path,
        ))
    elif payload.get("status") != "pass":
        diagnostics.append(diagnostic(
            "linker_runner_failed",
            "Required Linker application-evidence validation did not pass.",
            path,
        ))
    return payload


def _read_application_receipts_for_binding(
    graph_manifest: Mapping[str, Any], evidence_root: Path,
    diagnostics: List[Diagnostic], path: str,
) -> Tuple[
    Optional[Mapping[str, Any]],
    List[Tuple[Mapping[str, Any], str]],
]:
    reference = graph_manifest.get("application_evidence")
    if not isinstance(reference, Mapping) or set(reference) != APPLICATION_REFERENCE_FIELDS:
        diagnostics.append(diagnostic(
            "graph_application_evidence_missing",
            "Schema-v2 graph validation requires aggregate application evidence.",
            path,
        ))
        return None, []
    aggregate, raw = _read_graph_validation_manifest_v3(
        evidence_root,
        reference.get("path"),
        reference.get("digest"),
        diagnostics,
        path,
    )
    if aggregate is None or raw is None:
        return None, []
    if raw != _canonical_json_bytes(aggregate):
        diagnostics.append(diagnostic(
            "graph_application_evidence_noncanonical",
            "Aggregate application evidence must use canonical JSON bytes.",
            path,
        ))
    if (
        set(aggregate) != APPLICATION_EVIDENCE_FIELDS
        or type(aggregate.get("schema_version")) is not int
        or aggregate.get("schema_version") != 1
        or not isinstance(aggregate.get("receipts"), list)
    ):
        diagnostics.append(diagnostic(
            "graph_application_evidence_invalid",
            "Aggregate application evidence does not match exact schema v1.",
            path,
        ))
        return aggregate, []
    envelopes: List[Tuple[Mapping[str, Any], str]] = []
    for index, receipt_reference in enumerate(aggregate["receipts"]):
        receipt_path = "%s.receipts[%d]" % (path, index)
        if (
            not isinstance(receipt_reference, Mapping)
            or set(receipt_reference) != APPLICATION_REFERENCE_FIELDS
        ):
            diagnostics.append(diagnostic(
                "graph_application_receipt_invalid",
                "Application receipt reference is invalid.",
                receipt_path,
            ))
            continue
        envelope, receipt_raw = _read_graph_validation_manifest_v3(
            evidence_root,
            receipt_reference.get("path"),
            receipt_reference.get("digest"),
            diagnostics,
            receipt_path,
        )
        if envelope is None or receipt_raw is None:
            continue
        if receipt_raw != _canonical_json_bytes(envelope):
            diagnostics.append(diagnostic(
                "graph_application_receipt_noncanonical",
                "Application receipt must use canonical JSON bytes.",
                receipt_path,
            ))
        subject = envelope.get("subject")
        receipt = envelope.get("receipt")
        patch_receipt = (
            receipt.get("patch_receipt")
            if isinstance(receipt, Mapping) else None
        )
        if (
            set(envelope) != APPLICATION_ENVELOPE_FIELDS
            or not isinstance(subject, Mapping)
            or set(subject) != APPLICATION_SUBJECT_FIELDS
            or not isinstance(receipt, Mapping)
            or set(receipt) != APPLICATION_RECEIPT_FIELDS
            or not isinstance(patch_receipt, Mapping)
            or set(patch_receipt) != APPLICATION_PATCH_RECEIPT_FIELDS
        ):
            diagnostics.append(diagnostic(
                "graph_application_receipt_invalid",
                "Application receipt does not match the trusted schema.",
                receipt_path,
            ))
            continue
        envelopes.append((envelope, actual_state.digest_bytes(receipt_raw)))
    return aggregate, envelopes


def _logical_patch_source(patch: Mapping[str, Any]) -> Any:
    target = patch.get("target_path")
    if (
        patch.get("surface") == "companion_metadata"
        and isinstance(target, str)
        and target.endswith(".keystone.json")
    ):
        return target[:-len(".keystone.json")]
    return target


def _phase_actor_artifacts(
    phase: Mapping[str, Any], actor: str,
) -> List[Mapping[str, Any]]:
    artifacts: List[Mapping[str, Any]] = []
    for raw_delta in _list(phase.get("actor_deltas")):
        actor_delta = _mapping(raw_delta)
        if actor_delta.get("actor") != actor:
            continue
        artifacts.extend(
            item for item in _list(actor_delta.get("artifact_deltas"))
            if isinstance(item, Mapping)
        )
    return artifacts


def _validate_application_authority_bindings(
    *,
    aggregate: Mapping[str, Any],
    envelopes: Sequence[Tuple[Mapping[str, Any], str]],
    transaction: Mapping[str, Any],
    root: Path,
    assignment_id: Any,
    assignment_digest: Any,
    authorities: Mapping[str, Mapping[str, Any]],
    worker_phase: Mapping[str, Any],
    pre_phase: Mapping[str, Any],
    post_phase: Mapping[str, Any],
    diagnostics: List[Diagnostic],
) -> None:
    path = "keystone_closure.graph_sync.application_evidence"
    if (
        aggregate.get("assignment_id") != assignment_id
        or aggregate.get("assignment_digest") != assignment_digest
    ):
        diagnostics.append(diagnostic(
            "graph_application_assignment_mismatch",
            "Application evidence does not bind the authoritative assignment.",
            path,
        ))
    if (
        aggregate.get("transaction_id") != transaction.get("transaction_id")
        or aggregate.get("transaction_digest") != _application_plan_digest(
            transaction
        )
    ):
        diagnostics.append(diagnostic(
            "graph_application_transaction_mismatch",
            "Application evidence does not bind the immutable transaction plan.",
            path,
        ))
    phase_bindings = {
        "pre_acceptance_closure": (
            pre_phase,
            pre_phase.get("baseline_snapshot_digest"),
            _mapping(worker_phase.get("capture_evidence")).get("digest"),
        ),
        "post_acceptance": (
            post_phase,
            post_phase.get("baseline_snapshot_digest"),
            _mapping(post_phase.get("acceptance_event")).get("digest"),
        ),
    }
    seen_post = False
    prior_receipt_digest = ABSENT_DIGEST
    for index, receipt_item in enumerate(envelopes):
        envelope, raw_receipt_digest = receipt_item
        receipt_path = "%s.receipts[%d]" % (path, index)
        subject = _mapping(envelope.get("subject"))
        receipt = _mapping(envelope.get("receipt"))
        patch_receipt = _mapping(receipt.get("patch_receipt"))
        patch = _mapping(patch_receipt.get("patch"))
        owner = subject.get("owner")
        actor = "author" if owner == "author" else "repository_owner"
        if owner not in {"author", "main", "coordinator"}:
            diagnostics.append(diagnostic(
                "graph_application_owner_invalid",
                "Application receipt owner is not authoritative.",
                receipt_path,
            ))
            continue
        phase_id = subject.get("phase_id")
        binding = phase_bindings.get(str(phase_id))
        if binding is None or not binding[0]:
            diagnostics.append(diagnostic(
                "graph_application_phase_mismatch",
                "Application receipt does not name an available closure phase.",
                receipt_path,
            ))
            continue
        if phase_id == "post_acceptance":
            seen_post = True
        elif seen_post:
            diagnostics.append(diagnostic(
                "graph_application_phase_order_invalid",
                "Pre-acceptance receipts cannot follow post-acceptance receipts.",
                receipt_path,
            ))
        phase, baseline_digest, parent_evidence_digest = binding
        if (
            subject.get("phase_baseline_snapshot_digest") != baseline_digest
            or subject.get("phase_parent_evidence_digest")
            != parent_evidence_digest
        ):
            diagnostics.append(diagnostic(
                "graph_application_phase_mismatch",
                "Receipt phase baseline and result-parent evidence must match exactly.",
                receipt_path,
            ))
        authority = authorities.get(actor, {})
        scope = {
            "allowed": authority.get("allowed_edit_scope"),
            "excluded": authority.get("excluded_scope"),
        }
        if subject.get("scope_digest") != digest_json(scope):
            diagnostics.append(diagnostic(
                "graph_application_scope_mismatch",
                "Signed owner scope must equal authoritative phase scope.",
                receipt_path,
            ))
        request = {
            "schema_version": 1,
            "transaction_id": transaction.get("transaction_id"),
            "transaction_digest": _application_plan_digest(transaction),
            "assignment_id": assignment_id,
            "assignment_digest": assignment_digest,
            "phase_id": phase_id,
            "phase_baseline_snapshot_digest": baseline_digest,
            "phase_parent_evidence_digest": parent_evidence_digest,
            "repository_root_digest": phase_capture_root_digest(root),
            "owner": owner,
            "scope": scope,
            "scope_digest": digest_json(scope),
            "prior_receipt_digest": prior_receipt_digest,
            "patch": dict(patch),
        }
        if receipt.get("request_digest") != digest_json(request):
            diagnostics.append(diagnostic(
                "graph_application_request_mismatch",
                "Signed request digest does not bind the exact Coordinator authority request.",
                receipt_path,
            ))
        if (
            subject.get("assignment_id") != assignment_id
            or subject.get("assignment_digest") != assignment_digest
        ):
            diagnostics.append(diagnostic(
                "graph_application_assignment_mismatch",
                "Receipt assignment binding is stale or substituted.",
                receipt_path,
            ))
        prior_receipt_digest = raw_receipt_digest
        source = _logical_patch_source(patch)
        matches = [
            item for item in _phase_actor_artifacts(phase, actor)
            if item.get("source_surface") == source
        ]
        if len(matches) != 1:
            diagnostics.append(diagnostic(
                "graph_application_actor_delta_mismatch",
                "Receipt requires one exact actor artifact delta in its signed phase.",
                receipt_path,
            ))
            continue
        delta = matches[0]
        if (
            delta.get("baseline_digest") != patch.get("baseline_digest")
            or delta.get("resulting_digest")
            != patch_receipt.get("resulting_digest")
            or delta.get("resulting_digest")
            != patch.get("expected_after_digest")
            or delta.get("graph_relevant") is not True
        ):
            diagnostics.append(diagnostic(
                "graph_application_actor_delta_mismatch",
                "Receipt patch and result must equal the exact graph-relevant actor delta.",
                receipt_path,
            ))


def _validate_required_graph_sync_evidence_v3(
    value: Mapping[str, Any], deltas: List[Mapping[str, Any]], root: Path,
    evidence_root: Path, linker_runner: Path, timeout_seconds: float,
    diagnostics: List[Diagnostic], *, assignment_id: Any,
    assignment_digest: Any, authorities: Mapping[str, Mapping[str, Any]],
    worker_phase: Mapping[str, Any], pre_phase: Mapping[str, Any],
    post_phase: Mapping[str, Any], owner_keys: Mapping[str, Path],
    owner_key_digests: Mapping[str, str],
) -> None:
    path = "keystone_closure.graph_sync"
    fields = {
        "disposition", "state", "reason", "validation_manifest_path",
        "validation_manifest_digest", "transaction_id", "delta_set_digest",
        "envelope_digest",
    }
    _unknown_fields(value, fields, path, diagnostics)
    _missing_fields(value, fields, path, diagnostics)
    if value.get("state") != "verified":
        diagnostics.append(diagnostic(
            "graph_sync_incomplete",
            "Required graph sync must be verified.",
            path + ".state",
        ))
    if not _text(value.get("reason")):
        diagnostics.append(diagnostic(
            "graph_sync_reason_missing", "Graph sync requires a concrete reason.",
            path + ".reason",
        ))
    if value.get("delta_set_digest") != digest_json(deltas):
        diagnostics.append(diagnostic(
            "graph_delta_set_mismatch",
            "Graph evidence is not bound to the exact phase delta set.",
            path + ".delta_set_digest",
        ))
    graph_manifest, raw_manifest = _read_graph_validation_manifest_v3(
        evidence_root,
        value.get("validation_manifest_path"),
        value.get("validation_manifest_digest"),
        diagnostics,
        path + ".validation_manifest_path",
        require_canonical=True,
    )
    if graph_manifest is None or raw_manifest is None:
        return
    manifest_fields = set(graph_manifest)
    if (
        type(graph_manifest.get("schema_version")) is not int
        or graph_manifest.get("schema_version") != 2
        or not GRAPH_VALIDATION_MANIFEST_V2_FIELDS <= manifest_fields
        or manifest_fields - (
            GRAPH_VALIDATION_MANIFEST_V2_FIELDS
            | GRAPH_VALIDATION_MANIFEST_V2_OPTIONAL_FIELDS
        )
    ):
        diagnostics.append(diagnostic(
            "graph_validation_manifest_schema_not_authoritative",
            "Coordinator v3 requires exact Linker validation manifest schema 2.",
            path + ".validation_manifest_path",
        ))
    transaction = _mapping(graph_manifest.get("transaction"))
    if (
        type(transaction.get("schema_version")) is not int
        or transaction.get("schema_version") != 2
    ):
        diagnostics.append(diagnostic(
            "graph_transaction_schema_not_authoritative",
            "Coordinator v3 requires a canonical transaction schema v2.",
            path + ".validation_manifest_path",
        ))
    if (
        transaction.get("transaction_id") != value.get("transaction_id")
        or transaction.get("state") != "verified"
    ):
        diagnostics.append(diagnostic(
            "graph_transaction_mismatch",
            "Graph evidence must reference the same verified transaction.",
            path + ".transaction_id",
        ))
    expected_inputs = sorted(
        (_graph_delta_projection(delta) for delta in deltas),
        key=lambda item: str(item.get("source_surface")),
    )
    actual_inputs = sorted(
        _list(transaction.get("input_deltas")),
        key=lambda item: str(_mapping(item).get("source_surface")),
    )
    if actual_inputs != expected_inputs:
        diagnostics.append(diagnostic(
            "graph_transaction_delta_mismatch",
            "Graph transaction inputs must equal every phase artifact delta.",
            path + ".validation_manifest_path",
        ))
    payload = _run_graph_validation_v3(
        linker_runner,
        root,
        raw_manifest,
        evidence_root,
        owner_keys,
        owner_key_digests,
        timeout_seconds,
        diagnostics,
        path + ".envelope_digest",
    )
    if payload is not None and value.get("envelope_digest") != digest_json(payload):
        diagnostics.append(diagnostic(
            "runner_envelope_digest_mismatch",
            "Fresh Linker output is not bound to the recorded envelope digest.",
            path + ".envelope_digest",
        ))
    if payload is None or payload.get("status") != "pass":
        return
    aggregate, envelopes = _read_application_receipts_for_binding(
        graph_manifest,
        evidence_root,
        diagnostics,
        path + ".application_evidence",
    )
    if aggregate is None:
        return
    _validate_application_authority_bindings(
        aggregate=aggregate,
        envelopes=envelopes,
        transaction=transaction,
        root=root,
        assignment_id=assignment_id,
        assignment_digest=assignment_digest,
        authorities=authorities,
        worker_phase=worker_phase,
        pre_phase=pre_phase,
        post_phase=post_phase,
        diagnostics=diagnostics,
    )


def validate_graph_sync_evidence_v3(
    value: Mapping[str, Any], deltas: List[Mapping[str, Any]], root: Path,
    evidence_root: Path, linker_runner: Path, timeout_seconds: float,
    diagnostics: List[Diagnostic], *, assignment_id: Any = None,
    assignment_digest: Any = None,
    authorities: Optional[Mapping[str, Mapping[str, Any]]] = None,
    worker_phase: Optional[Mapping[str, Any]] = None,
    pre_phase: Optional[Mapping[str, Any]] = None,
    post_phase: Optional[Mapping[str, Any]] = None,
    owner_keys: Optional[Mapping[str, Path]] = None,
    owner_key_digests: Optional[Mapping[str, str]] = None,
) -> None:
    """Validate schema-v3 graph evidence with package-owned classification."""

    if value.get("disposition") == "required":
        _validate_required_graph_sync_evidence_v3(
            value,
            deltas,
            root,
            evidence_root,
            linker_runner,
            timeout_seconds,
            diagnostics,
            assignment_id=assignment_id,
            assignment_digest=assignment_digest,
            authorities=authorities or {},
            worker_phase=worker_phase or {},
            pre_phase=pre_phase or {},
            post_phase=post_phase or {},
            owner_keys=owner_keys or {},
            owner_key_digests=owner_key_digests or {},
        )
        return
    if value.get("disposition") != "not_applicable":
        validate_graph_sync_evidence(
            value, deltas, root, evidence_root, linker_runner,
            timeout_seconds, diagnostics,
        )
        return
    path = "keystone_closure.graph_sync"
    fields = {
        "disposition",
        "state",
        "reason",
        "classification_input_path",
        "classification_input_digest",
        "classification_path",
        "classification_digest",
        "delta_set_digest",
        "source_generation_digest",
        "envelope_digest",
    }
    _unknown_fields(value, fields, path, diagnostics)
    _missing_fields(value, fields, path, diagnostics)
    if value.get("state") != "not_applicable":
        diagnostics.append(diagnostic(
            "graph_sync_incomplete",
            "Not-applicable graph sync requires not_applicable state.",
            path + ".state",
        ))
    if not _text(value.get("reason")):
        diagnostics.append(diagnostic(
            "graph_sync_reason_missing",
            "Graph sync requires a concrete reason.",
            path + ".reason",
        ))
    expected_input = _classification_input(root, deltas)
    expected_delta_digest = expected_input["delta_set_digest"]
    if value.get("delta_set_digest") != expected_delta_digest:
        diagnostics.append(diagnostic(
            "graph_delta_set_mismatch",
            "Graph classification is not bound to the exact phase delta set.",
            path + ".delta_set_digest",
        ))
    recorded_input, _ = _read_classification_evidence(
        evidence_root,
        value.get("classification_input_path"),
        value.get("classification_input_digest"),
        path + ".classification_input_path",
        diagnostics,
    )
    if recorded_input is not None:
        if not _valid_classification_input_shape(recorded_input):
            diagnostics.append(diagnostic(
                "graph_classification_input_invalid",
                "Recorded Linker classification input is not canonical schema v1.",
                path + ".classification_input_path",
            ))
        if recorded_input != expected_input:
            diagnostics.append(diagnostic(
                "graph_classification_delta_mismatch",
                "Recorded classification input must equal every phase artifact/document delta.",
                path + ".classification_input_path",
            ))

    recorded_output, _ = _read_classification_evidence(
        evidence_root,
        value.get("classification_path"),
        value.get("classification_digest"),
        path + ".classification_path",
        diagnostics,
    )
    if recorded_output is not None and not _valid_classification_output(
        recorded_output, 0, expected_input,
    ):
        diagnostics.append(diagnostic(
            "graph_classification_output_invalid",
            "Recorded Linker classification output is not a passing schema-v1 envelope.",
            path + ".classification_path",
        ))

    fresh = _run_classification(
        package_classification_runner_path(),
        root,
        expected_input,
        timeout_seconds,
        diagnostics,
        path + ".classification_path",
    )
    if fresh is None:
        return
    if fresh.get("status") != "pass":
        diagnostics.append(diagnostic(
            "linker_classification_failed",
            "Fresh package-owned graph classification did not pass.",
            path + ".classification_path",
        ))
    if fresh.get("disposition") != "not_applicable":
        diagnostics.append(diagnostic(
            "graph_classification_disposition_mismatch",
            "Fresh Linker classification does not permit not_applicable graph sync.",
            path + ".disposition",
        ))
    if fresh.get("delta_set_digest") != expected_delta_digest:
        diagnostics.append(diagnostic(
            "graph_classification_delta_mismatch",
            "Fresh Linker classification omitted or changed a phase delta.",
            path + ".delta_set_digest",
        ))
    if fresh.get("source_generation_digest") != value.get(
        "source_generation_digest"
    ):
        diagnostics.append(diagnostic(
            "graph_classification_source_stale",
            "Recorded graph classification belongs to a different source generation.",
            path + ".source_generation_digest",
        ))
    if recorded_output is not None and recorded_output != fresh:
        diagnostics.append(diagnostic(
            "graph_classification_output_mismatch",
            "Recorded classification does not equal a fresh package-owned runner result.",
            path + ".classification_path",
        ))
    if value.get("envelope_digest") != digest_json(fresh):
        diagnostics.append(diagnostic(
            "runner_envelope_digest_mismatch",
            "Fresh classification output is not bound to the recorded envelope digest.",
            path + ".envelope_digest",
        ))


def _read_project_config_bytes(root: Path) -> Optional[bytes]:
    """Read the shared config without following a mutable path component."""

    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise OSError("document-root configuration requires no-follow descriptor APIs")
    directory_flags = (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    root_fd: Optional[int] = None
    config_fd: Optional[int] = None
    keystone_fd: Optional[int] = None
    try:
        root_fd = os.open(str(root), directory_flags)
        try:
            keystone_fd = os.open(".keystone", directory_flags, dir_fd=root_fd)
        except FileNotFoundError:
            return None
        try:
            before = os.stat(
                "config.yaml", dir_fd=keystone_fd, follow_symlinks=False,
            )
        except FileNotFoundError:
            return None
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise OSError(".keystone/config.yaml must be a single-link regular file")
        config_fd = os.open("config.yaml", file_flags, dir_fd=keystone_fd)
        opened = os.fstat(config_fd)
        if _evidence_file_identity(opened) != _evidence_file_identity(before):
            raise OSError(".keystone/config.yaml identity changed before read")
        chunks: List[bytes] = []
        while True:
            chunk = os.read(config_fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after_fd = os.fstat(config_fd)
        after_path = os.stat(
            "config.yaml", dir_fd=keystone_fd, follow_symlinks=False,
        )
        if (
            _evidence_file_identity(after_fd) != _evidence_file_identity(opened)
            or _evidence_file_identity(after_path) != _evidence_file_identity(before)
        ):
            raise OSError(".keystone/config.yaml changed during read")
        raw = b"".join(chunks)
        if len(raw) != before.st_size:
            raise OSError(".keystone/config.yaml size changed during read")
        return raw
    finally:
        if config_fd is not None:
            os.close(config_fd)
        if keystone_fd is not None:
            os.close(keystone_fd)
        if root_fd is not None:
            os.close(root_fd)


def _parse_document_root_scalar(raw: str) -> Optional[str]:
    scalar = raw.strip()
    if not scalar:
        return None
    if scalar.startswith('"'):
        try:
            value = json.loads(scalar)
        except (json.JSONDecodeError, TypeError, ValueError):
            return None
        return value if isinstance(value, str) else None
    if scalar.startswith("'"):
        if len(scalar) < 2 or not scalar.endswith("'"):
            return None
        return scalar[1:-1].replace("''", "'")
    scalar = scalar.split("#", 1)[0].strip()
    if not scalar or any(character in scalar for character in "{}[]&*!|>@`\t"):
        return None
    return scalar


def _configured_document_root(
    root: Path, diagnostics: List[Diagnostic],
) -> Optional[str]:
    path = "assignment.document_root"
    try:
        raw = _read_project_config_bytes(root)
        if raw is None:
            configured = DEFAULT_DOCUMENT_ROOT
        else:
            text = raw.decode("utf-8")
            matches: List[str] = []
            for line in text.splitlines():
                match = DOCUMENT_ROOT_LINE_PATTERN.fullmatch(line)
                if match is not None:
                    value = _parse_document_root_scalar(match.group(1))
                    if value is None:
                        raise ValueError("document_root must be one plain scalar")
                    matches.append(value)
            if len(matches) != 1:
                raise ValueError(
                    ".keystone/config.yaml must declare document_root exactly once"
                )
            configured = matches[0]
        normalized = _normalize_selector(configured)
        if normalized is None:
            raise ValueError("configured document_root is not a canonical selector")
        candidate = root if normalized == "." else root.joinpath(
            *PurePosixPath(normalized).parts
        )
        resolved = candidate.resolve(strict=True)
        if not resolved.is_dir():
            raise ValueError("configured document_root is not a directory")
        resolved.relative_to(root)
        return normalized
    except (OSError, RuntimeError, UnicodeError, ValueError) as error:
        diagnostics.append(diagnostic(
            "document_root_configuration_invalid", str(error), path,
        ))
        return None


def _read_phase_capture_evidence(
    reference: Any, *, evidence_root: Path, root: Path, phase_id: str,
    parent_snapshot_digest: Optional[str], snapshot: Any,
    assignment_id: Any, assignment_subject_digest: Any, context_digest: Any,
    authority_key: Optional[bytes], authority_key_digest: Any,
    parent_evidence_digest: Any, seen_nonces: Set[str],
    diagnostics: List[Diagnostic], path: str,
) -> Optional[datetime]:
    value = _mapping(reference)
    _unknown_fields(value, CAPTURE_REFERENCE_FIELDS, path, diagnostics)
    _missing_fields(value, CAPTURE_REFERENCE_FIELDS, path, diagnostics)
    relative = normalize_relative_path(value.get("path"))
    if relative is None:
        diagnostics.append(diagnostic(
            "phase_capture_path_invalid",
            "Phase capture evidence path must be repository-relative POSIX text.",
            path + ".path",
        ))
        return None
    if not _digest(value.get("digest")):
        diagnostics.append(diagnostic(
            "phase_capture_reference_digest_invalid",
            "Phase capture reference digest must be canonical SHA-256.",
            path + ".digest",
        ))
    raw = _read_immutable_evidence_bytes(
        evidence_root, relative, path + ".path", diagnostics,
    )
    if raw is None:
        return None
    try:
        envelope = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_json,
        )
    except (
        UnicodeError,
        json.JSONDecodeError,
        DuplicateJsonKey,
        ValueError,
    ) as error:
        diagnostics.append(diagnostic(
            "phase_capture_evidence_unreadable", str(error), path + ".path",
        ))
        return None
    actual_digest = actual_state.digest_bytes(raw)
    if value.get("digest") != actual_digest:
        diagnostics.append(diagnostic(
            "phase_capture_evidence_digest_mismatch",
            "Phase capture raw-byte digest does not match the immutable evidence file.",
            path + ".digest",
        ))
    if not isinstance(envelope, Mapping):
        diagnostics.append(diagnostic(
            "phase_capture_envelope_invalid",
            "Phase capture envelope must be an object.", path,
        ))
        return None
    if raw != json.dumps(
        envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8"):
        diagnostics.append(diagnostic(
            "phase_capture_envelope_not_canonical",
            "Phase capture evidence must use canonical JSON bytes.", path + ".path",
        ))
    _unknown_fields(envelope, CAPTURE_ENVELOPE_FIELDS, path + ".envelope", diagnostics)
    _missing_fields(envelope, CAPTURE_ENVELOPE_FIELDS, path + ".envelope", diagnostics)
    _validate_host_receipt(
        envelope,
        key=authority_key,
        key_fingerprint=authority_key_digest,
        command_id=CAPTURE_COMMAND_ID,
        evidence_root=evidence_root,
        parent_evidence_digest=parent_evidence_digest,
        seen_nonces=seen_nonces,
        diagnostics=diagnostics,
        path=path + ".envelope.receipt",
    )
    if type(envelope.get("schema_version")) is not int or envelope.get("schema_version") != 1:
        diagnostics.append(diagnostic(
            "phase_capture_schema_invalid",
            "Phase capture schema_version must be 1.",
            path + ".envelope.schema_version",
        ))
    if envelope.get("producer") != PHASE_CAPTURE_PRODUCER:
        diagnostics.append(diagnostic(
            "phase_capture_producer_invalid",
            "Phase capture evidence is not package-owned.",
            path + ".envelope.producer",
        ))
    if envelope.get("phase_id") != phase_id:
        diagnostics.append(diagnostic(
            "phase_capture_phase_mismatch",
            "Phase capture phase_id does not match the closure phase.",
            path + ".envelope.phase_id",
        ))
    if envelope.get("parent_snapshot_digest") != parent_snapshot_digest:
        diagnostics.append(diagnostic(
            "phase_capture_parent_mismatch",
            "Phase capture parent does not match the preceding snapshot.",
            path + ".envelope.parent_snapshot_digest",
        ))
    try:
        expected_snapshot_digest = _snapshot_digest(snapshot)
        snapshot_wire = _snapshot_wire(snapshot)
    except (TypeError, ValueError) as error:
        diagnostics.append(_snapshot_error(error, path + ".envelope.snapshot_digest"))
        expected_snapshot_digest = None
        snapshot_wire = {}
    if envelope.get("snapshot_digest") != expected_snapshot_digest:
        diagnostics.append(diagnostic(
            "phase_capture_snapshot_mismatch",
            "Phase capture snapshot_digest does not match embedded result_snapshot.",
            path + ".envelope.snapshot_digest",
        ))
    subject = _mapping(envelope.get("subject"))
    _unknown_fields(subject, CAPTURE_SUBJECT_FIELDS, path + ".envelope.subject", diagnostics)
    _missing_fields(subject, CAPTURE_SUBJECT_FIELDS, path + ".envelope.subject", diagnostics)
    if subject.get("repository_root_digest") != phase_capture_root_digest(root):
        diagnostics.append(diagnostic(
            "phase_capture_root_mismatch",
            "Phase capture evidence belongs to a different repository root.",
            path + ".envelope.subject.repository_root_digest",
        ))
    if subject.get("policy_digest") != snapshot_wire.get("policy_digest"):
        diagnostics.append(diagnostic(
            "phase_capture_policy_mismatch",
            "Phase capture policy does not match the result snapshot.",
            path + ".envelope.subject.policy_digest",
        ))
    if subject.get("assignment_id") != assignment_id or not _text(
        subject.get("assignment_id")
    ):
        diagnostics.append(diagnostic(
            "phase_capture_assignment_mismatch",
            "Phase capture evidence belongs to a different assignment.",
            path + ".envelope.subject.assignment_id",
        ))
    if subject.get("assignment_subject_digest") != assignment_subject_digest or not _digest(
        subject.get("assignment_subject_digest")
    ):
        diagnostics.append(diagnostic(
            "phase_capture_assignment_subject_mismatch",
            "Phase capture evidence is not bound to the current assignment authority core.",
            path + ".envelope.subject.assignment_subject_digest",
        ))
    if subject.get("context_digest") != context_digest or not _digest(
        subject.get("context_digest")
    ):
        diagnostics.append(diagnostic(
            "phase_capture_context_mismatch",
            "Phase capture evidence belongs to a different Context Pack.",
            path + ".envelope.subject.context_digest",
        ))
    captured_at = _parse_capture_time(envelope.get("captured_at"))
    if captured_at is None:
        diagnostics.append(diagnostic(
            "phase_capture_time_invalid",
            "captured_at must be canonical UTC RFC3339 text.",
            path + ".envelope.captured_at",
        ))
    return captured_at


def _read_acceptance_event(
    reference: Any, *, evidence_root: Path, root: Path,
    assignment_id: Any, assignment_digest: Any, context_digest: Any,
    policy_digest: Any, closure_target: Any, closure_step_ref: Any,
    pre_snapshot_digest: Any,
    acceptance_ref: Any, accepted_steps: Any,
    authority_key: Optional[bytes], authority_key_digest: Any,
    parent_evidence_digest: Any, seen_nonces: Set[str],
    diagnostics: List[Diagnostic], path: str,
) -> Optional[datetime]:
    value = _mapping(reference)
    _unknown_fields(value, CAPTURE_REFERENCE_FIELDS, path, diagnostics)
    _missing_fields(value, CAPTURE_REFERENCE_FIELDS, path, diagnostics)
    relative = normalize_relative_path(value.get("path"))
    if relative is None:
        diagnostics.append(diagnostic(
            "acceptance_event_path_invalid",
            "Acceptance event path must be normalized repository-relative text.",
            path + ".path",
        ))
        return None
    if not _digest(value.get("digest")):
        diagnostics.append(diagnostic(
            "acceptance_event_reference_digest_invalid",
            "Acceptance event reference digest must be canonical SHA-256.",
            path + ".digest",
        ))
    raw = _read_immutable_evidence_bytes(
        evidence_root, relative, path + ".path", diagnostics,
    )
    if raw is None:
        return None
    try:
        envelope = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_json,
        )
    except (
        UnicodeError,
        json.JSONDecodeError,
        DuplicateJsonKey,
        ValueError,
    ) as error:
        diagnostics.append(diagnostic(
            "acceptance_event_unreadable", str(error), path + ".path",
        ))
        return None
    if value.get("digest") != actual_state.digest_bytes(raw):
        diagnostics.append(diagnostic(
            "acceptance_event_digest_mismatch",
            "Acceptance event raw-byte digest does not match its reference.",
            path + ".digest",
        ))
    if not isinstance(envelope, Mapping):
        diagnostics.append(diagnostic(
            "acceptance_event_invalid", "Acceptance event must be an object.", path,
        ))
        return None
    if raw != _canonical_json_bytes(envelope):
        diagnostics.append(diagnostic(
            "acceptance_event_not_canonical",
            "Acceptance event must use canonical JSON bytes.", path + ".path",
        ))
    _unknown_fields(envelope, ACCEPTANCE_EVENT_FIELDS, path + ".envelope", diagnostics)
    _missing_fields(envelope, ACCEPTANCE_EVENT_FIELDS, path + ".envelope", diagnostics)
    _validate_host_receipt(
        envelope,
        key=authority_key,
        key_fingerprint=authority_key_digest,
        command_id=ACCEPTANCE_COMMAND_ID,
        evidence_root=evidence_root,
        parent_evidence_digest=parent_evidence_digest,
        seen_nonces=seen_nonces,
        diagnostics=diagnostics,
        path=path + ".envelope.receipt",
    )
    if type(envelope.get("schema_version")) is not int or envelope.get("schema_version") != 1:
        diagnostics.append(diagnostic(
            "acceptance_event_schema_invalid",
            "Acceptance event schema_version must be 1.",
            path + ".envelope.schema_version",
        ))
    if envelope.get("producer") != ACCEPTANCE_EVENT_PRODUCER:
        diagnostics.append(diagnostic(
            "acceptance_event_producer_invalid",
            "Acceptance event is not Main-owned package evidence.",
            path + ".envelope.producer",
        ))
    if envelope.get("acceptance_ref") != acceptance_ref or not _text(
        envelope.get("acceptance_ref")
    ):
        diagnostics.append(diagnostic(
            "acceptance_event_ref_mismatch",
            "Acceptance event ref does not match the post-acceptance phase.",
            path + ".envelope.acceptance_ref",
        ))
    if envelope.get("accepted_steps") != accepted_steps:
        diagnostics.append(diagnostic(
            "acceptance_event_steps_mismatch",
            "Acceptance event Steps do not match the closure target.",
            path + ".envelope.accepted_steps",
        ))
    if envelope.get("accepted_by") != "main":
        diagnostics.append(diagnostic(
            "acceptance_event_actor_invalid", "accepted_by must be main.",
            path + ".envelope.accepted_by",
        ))
    subject = _mapping(envelope.get("subject"))
    _unknown_fields(subject, ACCEPTANCE_SUBJECT_FIELDS, path + ".envelope.subject", diagnostics)
    _missing_fields(subject, ACCEPTANCE_SUBJECT_FIELDS, path + ".envelope.subject", diagnostics)
    expected_subject = {
        "repository_root_digest": phase_capture_root_digest(root),
        "assignment_id": assignment_id,
        "assignment_digest": assignment_digest,
        "context_digest": context_digest,
        "policy_digest": policy_digest,
        "closure_target": closure_target,
        "closure_step_ref": closure_step_ref,
        "pre_snapshot_digest": pre_snapshot_digest,
        "observed_snapshot_digest": pre_snapshot_digest,
    }
    for field, expected in expected_subject.items():
        if subject.get(field) != expected:
            diagnostics.append(diagnostic(
                "acceptance_event_subject_mismatch",
                "Acceptance event subject does not match the immutable closure chain.",
                path + ".envelope.subject." + field,
            ))
    accepted_at = _parse_capture_time(envelope.get("accepted_at"))
    if accepted_at is None:
        diagnostics.append(diagnostic(
            "acceptance_event_time_invalid",
            "accepted_at must be canonical UTC RFC3339 text.",
            path + ".envelope.accepted_at",
        ))
    return accepted_at


def _read_finalization_manifest_for_phase(
    finalization: Mapping[str, Any], evidence_root: Path,
    diagnostics: List[Diagnostic],
) -> Optional[Mapping[str, Any]]:
    path = "post_acceptance_phase.author_evidence_binding"
    relative = normalize_relative_path(finalization.get("manifest_path"))
    if relative is None:
        diagnostics.append(diagnostic(
            "post_finalization_manifest_path_invalid",
            "Post-acceptance Author manifest path is invalid.", path,
        ))
        return None
    read_diagnostics: List[Diagnostic] = []
    raw = _read_immutable_evidence_bytes(
        evidence_root, relative, path, read_diagnostics,
    )
    if raw is None:
        detail = read_diagnostics[0]["message"] if read_diagnostics else "unreadable"
        diagnostics.append(diagnostic(
            "post_finalization_manifest_unreadable", detail, path,
        ))
        return None
    try:
        manifest = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_json,
        )
    except (
        UnicodeError,
        json.JSONDecodeError,
        DuplicateJsonKey,
        ValueError,
    ) as error:
        diagnostics.append(diagnostic(
            "post_finalization_manifest_unreadable", str(error), path,
        ))
        return None
    if actual_state.digest_bytes(raw) != finalization.get("manifest_digest"):
        diagnostics.append(diagnostic(
            "post_finalization_manifest_digest_mismatch",
            "Author finalization manifest digest changed after phase binding.", path,
        ))
    if not isinstance(manifest, Mapping):
        diagnostics.append(diagnostic(
            "post_finalization_manifest_invalid",
            "Author finalization manifest must be an object.", path,
        ))
        return None
    return manifest


def _manifest_path(value: Any) -> Optional[str]:
    normalized = normalize_relative_path(value)
    return normalized


def _finalization_source_paths(
    manifest: Mapping[str, Any], diagnostics: List[Diagnostic],
) -> Tuple[Set[str], Set[str]]:
    """Return required core sources and every declared path-bearing source."""

    required: Set[str] = set()
    declared: Set[str] = set()

    def add(raw: Any, *, core: bool) -> None:
        normalized = _manifest_path(raw)
        if normalized is None:
            diagnostics.append(diagnostic(
                "post_finalization_source_path_invalid",
                "Author finalization source paths must be normalized repository paths.",
                "post_acceptance_phase.author_evidence_binding",
            ))
            return
        declared.add(normalized)
        if core:
            required.add(normalized)

    accepted_steps = {
        str(item) for item in _list(manifest.get("accepted_steps")) if _text(item)
    }
    for step in _list(manifest.get("steps")):
        if (
            isinstance(step, Mapping)
            and step.get("ref") in accepted_steps
            and "progress_path" in step
        ):
            add(step.get("progress_path"), core=True)
    for source in _list(manifest.get("active_step_sources")):
        if isinstance(source, Mapping):
            add(source.get("path"), core=False)
    global_state = _mapping(manifest.get("global_state"))
    for source in _list(global_state.get("sources")):
        if isinstance(source, Mapping):
            add(source.get("path"), core=False)
    finalization = _mapping(manifest.get("finalization"))
    if "progress_path" in finalization:
        add(finalization.get("progress_path"), core=True)
    for candidate in _list(manifest.get("impact_candidates")):
        if isinstance(candidate, Mapping) and "path" in candidate:
            add(candidate.get("path"), core=False)
    for entry in _list(manifest.get("namespace_entries")):
        if isinstance(entry, Mapping) and "path" in entry:
            add(entry.get("path"), core=False)
    return required, declared


def _validate_post_finalization_binding(
    post_phase: Mapping[str, Any], finalization: Mapping[str, Any],
    post_snapshot: Any, post_changes: Sequence[Mapping[str, Any]],
    evidence_root: Path, diagnostics: List[Diagnostic],
) -> None:
    path = "post_acceptance_phase.author_evidence_binding"
    binding = _mapping(post_phase.get("author_evidence_binding"))
    _unknown_fields(binding, AUTHOR_EVIDENCE_BINDING_FIELDS, path, diagnostics)
    _missing_fields(binding, AUTHOR_EVIDENCE_BINDING_FIELDS, path, diagnostics)
    expected = {
        "finalization_manifest_digest": finalization.get("manifest_digest"),
        "runner_envelope_digest": finalization.get("envelope_digest"),
        "source_snapshot_digest": _snapshot_digest(post_snapshot),
    }
    for field, expected_value in expected.items():
        if binding.get(field) != expected_value or not _digest(binding.get(field)):
            diagnostics.append(diagnostic(
                "post_author_evidence_binding_mismatch",
                "Post-acceptance Author evidence is not bound to source generation.",
                path + "." + field,
            ))

    author_deltas = [
        _mapping(item) for item in _list(post_phase.get("actor_deltas"))
        if _mapping(item).get("actor") == "author"
    ]
    if (
        not post_changes
        or len(author_deltas) != 1
        or not _list(author_deltas[0].get("changed_paths"))
    ):
        diagnostics.append(diagnostic(
            "post_acceptance_author_delta_missing",
            "Closure completion requires a non-empty Author finalization delta after acceptance.",
            "post_acceptance_phase.actor_deltas",
        ))

    manifest = _read_finalization_manifest_for_phase(
        finalization, evidence_root, diagnostics,
    )
    if manifest is None:
        return
    required_sources, declared_sources = _finalization_source_paths(manifest, diagnostics)
    changed = {str(item.get("path")) for item in post_changes}
    if not required_sources or not required_sources <= changed:
        diagnostics.append(diagnostic(
            "post_finalization_sources_not_changed",
            "Every core Author finalization source must change after Main acceptance.",
            "post_acceptance_phase.actor_deltas",
        ))
    if not changed <= declared_sources:
        diagnostics.append(diagnostic(
            "post_author_delta_source_unbound",
            "Every post-acceptance Author delta must be declared by finalization evidence.",
            "post_acceptance_phase.actor_deltas",
        ))


def _snapshot_digest(snapshot: Any) -> str:
    value = getattr(snapshot, "snapshot_digest", None)
    if not _digest(value):
        value = _snapshot_wire(snapshot).get("snapshot_digest")
    if not _digest(value):
        raise ValueError("snapshot_digest is not a canonical SHA-256 value")
    return value


def _changed_paths(before: Any, after: Any) -> List[Mapping[str, Any]]:
    differ = getattr(actual_state, "changed_paths_v3", None)
    if differ is None:
        raise RuntimeError("snapshot delta v3 runtime is unavailable")
    value = differ(before, after)
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise TypeError("changed_paths_v3 must return an array of objects")
    return value


def _validate_snapshot_symlink_scopes(
    snapshot: Any, authorities: Mapping[str, Mapping[str, Any]], path: str,
    diagnostics: List[Diagnostic],
) -> None:
    checker = getattr(actual_state, "snapshot_symlink_violations_v3", None)
    if checker is None:
        diagnostics.append(diagnostic(
            "snapshot_symlink_validator_unavailable",
            "Recorded-snapshot symlink validation is unavailable.", path,
        ))
        return
    try:
        violations = checker(_snapshot_wire(snapshot))
    except (RuntimeError, TypeError, ValueError, OSError) as error:
        diagnostics.append(_snapshot_error(error, path))
        return
    for violation in violations:
        symlink_path = _mapping(violation).get("path")
        reason = _mapping(violation).get("reason")
        if normalize_relative_path(symlink_path) is None or not _text(reason):
            diagnostics.append(diagnostic(
                "snapshot_symlink_evidence_invalid",
                "Recorded-snapshot symlink evidence is malformed.", path,
            ))
            continue
        for actor in sorted(WRITE_ACTORS):
            authority = authorities.get(actor, {})
            if _portable_path_overlaps_scope(
                str(symlink_path), authority.get("allowed_edit_scope", [])
            ):
                diagnostics.append(diagnostic(
                    "symlink_scope_escape",
                    "Actor %s scope overlaps unsafe symlink %s (%s)."
                    % (actor, symlink_path, reason),
                    "assignment.phase_authorities.%s.allowed_edit_scope" % actor,
                ))


def _validate_actor_scopes_against_policy(
    policy: Any, authorities: Mapping[str, Mapping[str, Any]],
    diagnostics: List[Diagnostic],
) -> None:
    wire = _policy_wire(policy)
    includes = _list(wire.get("include_paths"))
    exclusions = [
        _mapping(item).get("path") for item in _list(wire.get("exclusions"))
    ]
    for actor in sorted(WRITE_ACTORS):
        scopes = authorities.get(actor, {}).get("allowed_edit_scope", [])
        for index, selector in enumerate(scopes):
            path = "assignment.phase_authorities.%s.allowed_edit_scope[%d]" % (
                actor, index,
            )
            if not _canonical_path_in_scope(selector, includes):
                diagnostics.append(diagnostic(
                    "actor_scope_outside_snapshot_policy",
                    "Actor write scope must be fully covered by snapshot include_paths.",
                    path,
                ))
            if any(
                _normalize_selector(exclusion) is not None
                and _portable_path_overlaps_scope(str(exclusion), [selector])
                for exclusion in exclusions
            ):
                diagnostics.append(diagnostic(
                    "actor_scope_excluded_from_snapshot",
                    "Snapshot exclusions must not overlap an actor write scope.",
                    path,
                ))


def _expected_absences(snapshot: Any) -> Tuple[str, ...]:
    value = getattr(snapshot, "expected_absences", None)
    if value is None:
        value = _snapshot_wire(snapshot).get("expected_absences")
    if not isinstance(value, (list, tuple)) or not all(
        normalize_relative_path(item) is not None for item in value
    ):
        raise ValueError("snapshot expected_absences are invalid")
    return tuple(value)


def _entry(snapshot: Any, path: str) -> Optional[Any]:
    entry_map = getattr(snapshot, "entry_map", None)
    if isinstance(entry_map, Mapping):
        return entry_map.get(path)
    return None


def _entry_path_type(entry: Any) -> Optional[str]:
    if entry is None:
        return None
    if isinstance(entry, Mapping):
        return entry.get("path_type")
    return getattr(entry, "path_type", None)


def _entry_raw_digest(entry: Any) -> Any:
    if entry is None:
        return ABSENT_DIGEST
    if isinstance(entry, Mapping):
        value = entry.get("raw_byte_digest")
    else:
        value = getattr(entry, "raw_byte_digest", None)
    return value if _digest(value) else ABSENT_DIGEST


def _validate_artifact_bindings(
    before: Any, after: Any, changes: Sequence[Mapping[str, Any]],
    artifacts: Sequence[Mapping[str, Any]], path: str,
    diagnostics: List[Diagnostic],
) -> None:
    changes_by_path = {str(item.get("path")): item for item in changes}
    artifacts_by_path: Dict[str, List[Mapping[str, Any]]] = {}
    for delta in artifacts:
        artifacts_by_path.setdefault(str(delta.get("source_surface")), []).append(delta)

    expected_artifact_paths: Set[str] = set()
    for changed, change in changes_by_path.items():
        before_entry = _entry(before, changed)
        after_entry = _entry(after, changed)
        before_type = _entry_path_type(before_entry)
        after_type = _entry_path_type(after_entry)
        byte_surface = (
            before_type in {"regular_file", "symlink"}
            or after_type in {"regular_file", "symlink"}
        )
        if byte_surface:
            expected_artifact_paths.add(changed)
        for delta in artifacts_by_path.get(changed, []):
            if delta.get("change_kind") != change.get("change_kind"):
                diagnostics.append(diagnostic(
                    "artifact_delta_change_kind_mismatch",
                    "Artifact change_kind must equal the adjacent snapshot delta.",
                    path + ".artifact_deltas",
                ))
            if delta.get("baseline_digest") != _entry_raw_digest(before_entry):
                diagnostics.append(diagnostic(
                    "artifact_baseline_digest_mismatch",
                    "Artifact baseline_digest must equal adjacent snapshot raw bytes.",
                    path + ".artifact_deltas",
                ))
            if delta.get("resulting_digest") != _entry_raw_digest(after_entry):
                diagnostics.append(diagnostic(
                    "artifact_resulting_digest_mismatch",
                    "Artifact resulting_digest must equal adjacent snapshot raw bytes.",
                    path + ".artifact_deltas",
                ))

    if set(artifacts_by_path) != expected_artifact_paths or any(
        len(values) != 1 for values in artifacts_by_path.values()
    ):
        diagnostics.append(diagnostic(
            "artifact_delta_cardinality_invalid",
            "Each changed byte-bearing surface requires exactly one adjacent artifact delta.",
            path + ".artifact_deltas",
        ))


def _validate_scope(
    value: Any, path: str, diagnostics: List[Diagnostic],
) -> Mapping[str, List[str]]:
    scope = _mapping(value)
    fields = {"read_scope", "allowed_edit_scope", "excluded_scope"}
    _unknown_fields(scope, fields, path, diagnostics)
    _missing_fields(scope, fields, path, diagnostics)
    return {
        name: _validate_paths(
            scope.get(name), path + "." + name, diagnostics,
            allow_empty=name != "read_scope",
        )
        for name in ("read_scope", "allowed_edit_scope", "excluded_scope")
    }


def _validate_phase_authorities(
    value: Any, assignment_authority: Any, assignment_scope: Mapping[str, List[str]],
    diagnostics: List[Diagnostic],
) -> Mapping[str, Mapping[str, Any]]:
    authorities = _mapping(value)
    path = "assignment.phase_authorities"
    _unknown_fields(authorities, PHASE_ACTORS, path, diagnostics)
    _missing_fields(authorities, PHASE_ACTORS, path, diagnostics)
    result: Dict[str, Mapping[str, Any]] = {}
    expected_authority = {
        "worker": assignment_authority,
        "author": "document_edit",
        "repository_owner": "bounded_edit",
        "linker": "read_only",
    }
    for actor in sorted(PHASE_ACTORS):
        actor_path = path + "." + actor
        item = _mapping(authorities.get(actor))
        _unknown_fields(item, PHASE_AUTHORITY_FIELDS, actor_path, diagnostics)
        _missing_fields(item, PHASE_AUTHORITY_FIELDS, actor_path, diagnostics)
        normalized = {
            "authority": item.get("authority"),
            "allowed_edit_scope": _validate_paths(
                item.get("allowed_edit_scope"), actor_path + ".allowed_edit_scope", diagnostics,
            ),
            "excluded_scope": _validate_paths(
                item.get("excluded_scope"), actor_path + ".excluded_scope", diagnostics,
            ),
        }
        if normalized["authority"] != expected_authority[actor]:
            diagnostics.append(diagnostic(
                "actor_authority_invalid", "%s authority does not match the v3 authority matrix." % actor,
                actor_path + ".authority",
            ))
        if actor == "worker" and (
            normalized["allowed_edit_scope"] != assignment_scope.get("allowed_edit_scope")
            or normalized["excluded_scope"] != assignment_scope.get("excluded_scope")
        ):
            diagnostics.append(diagnostic(
                "worker_scope_binding_mismatch",
                "Worker phase authority must exactly match assignment scope.", actor_path,
            ))
        if actor == "linker" and normalized["allowed_edit_scope"]:
            diagnostics.append(diagnostic(
                "linker_write_authority_forbidden",
                "Linker must have an empty write scope.", actor_path + ".allowed_edit_scope",
            ))
        result[actor] = normalized
    return result


def _validate_assignment(
    assignment: Mapping[str, Any], closure_target: Any, closure_step_ref: Any,
    root: Path, diagnostics: List[Diagnostic],
) -> Tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]], Any, Any]:
    fields = {
        "schema_version",
        "assignment_id",
        "execution_mode",
        "purpose",
        "authority",
        "goal",
        "context_pack",
        "injected_skills",
        "scope",
        "document_root",
        "snapshot_policy",
        "assignment_phase",
        "phase_authorities",
    }
    _unknown_fields(assignment, fields, "assignment", diagnostics)
    _missing_fields(assignment, fields, "assignment", diagnostics)
    if type(assignment.get("schema_version")) is not int or assignment.get("schema_version") != 3:
        diagnostics.append(diagnostic(
            "assignment_schema_invalid", "Assignment schema_version must be 3.",
            "assignment.schema_version",
        ))
    for field in ("assignment_id", "goal"):
        if not _text(assignment.get(field)):
            diagnostics.append(diagnostic(
                "required_field_missing", "%s is required." % field, "assignment." + field,
            ))
    if assignment.get("execution_mode") not in EXECUTION_MODES:
        diagnostics.append(diagnostic(
            "execution_mode_invalid", "Invalid execution mode.", "assignment.execution_mode",
        ))
    if assignment.get("purpose") not in PURPOSES:
        diagnostics.append(diagnostic(
            "purpose_invalid", "Invalid assignment purpose.", "assignment.purpose",
        ))
    if assignment.get("authority") not in AUTHORITIES:
        diagnostics.append(diagnostic(
            "authority_invalid", "Invalid assignment authority.", "assignment.authority",
        ))
    context = _mapping(assignment.get("context_pack"))
    if not isinstance(assignment.get("context_pack"), Mapping):
        diagnostics.append(diagnostic(
            "authoritative_field_type_invalid",
            "assignment.context_pack must be an object.",
            "assignment.context_pack",
        ))
    validate_assignment_context_evidence(
        context, closure_target, closure_step_ref, diagnostics,
    )
    assignment_steps = _list(_mapping(context.get("work_context")).get("step_refs"))
    if (
        closure_target == "step"
        and _text(closure_step_ref)
        and closure_step_ref not in assignment_steps
    ):
        diagnostics.append(diagnostic(
            "closure_step_ref_out_of_scope",
            "closure_step_ref must be present in assignment work context.",
            "closure_step_ref",
        ))
    scope = _validate_scope(assignment.get("scope"), "assignment.scope", diagnostics)
    context_scope = _mapping(context.get("scope_boundaries"))
    if context_scope != assignment.get("scope"):
        diagnostics.append(diagnostic(
            "assignment_scope_context_mismatch",
            "Assignment scope must exactly match Context Pack scope boundaries.",
            "assignment.scope",
        ))

    raw_skills = assignment.get("injected_skills")
    if not isinstance(raw_skills, list) or not raw_skills:
        diagnostics.append(diagnostic(
            "injected_skills_missing", "At least one injected skill is required.",
            "assignment.injected_skills",
        ))
    skill_keys: Set[Tuple[str, str]] = set()
    for index, raw in enumerate(_list(raw_skills)):
        item = _mapping(raw)
        item_path = "assignment.injected_skills[%d]" % index
        _unknown_fields(item, {"skill_id", "mode"}, item_path, diagnostics)
        if not _text(item.get("skill_id")) or not _text(item.get("mode")):
            diagnostics.append(diagnostic(
                "injected_skill_invalid", "Skill ID and mode are required.", item_path,
            ))
        else:
            key = (item["skill_id"], item["mode"])
            if key in skill_keys:
                diagnostics.append(diagnostic(
                    "injected_skill_duplicate", "Injected skills must be unique.", item_path,
                ))
            skill_keys.add(key)

    try:
        policy = _normalize_policy(assignment.get("snapshot_policy"))
        if _policy_wire(policy) != assignment.get("snapshot_policy"):
            diagnostics.append(diagnostic(
                "snapshot_policy_not_canonical",
                "snapshot_policy must equal its normalized canonical wire.",
                "assignment.snapshot_policy",
            ))
    except (RuntimeError, TypeError, ValueError, OSError) as error:
        diagnostics.append(_snapshot_error(error, "assignment.snapshot_policy"))
        policy = None

    phase = _mapping(assignment.get("assignment_phase"))
    phase_fields = {
        "phase_id", "actor", "authority", "result_snapshot", "capture_evidence",
    }
    _unknown_fields(phase, phase_fields, "assignment.assignment_phase", diagnostics)
    _missing_fields(phase, phase_fields, "assignment.assignment_phase", diagnostics)
    if (
        phase.get("phase_id") != "assignment"
        or phase.get("actor") != "coordinator"
        or phase.get("authority") != "verification"
    ):
        diagnostics.append(diagnostic(
            "assignment_phase_identity_invalid",
            "Assignment phase must be coordinator-owned verification evidence.",
            "assignment.assignment_phase",
        ))
    try:
        assignment_snapshot = _parse_snapshot(phase.get("result_snapshot"))
    except (RuntimeError, TypeError, ValueError, OSError) as error:
        diagnostics.append(_snapshot_error(error, "assignment.assignment_phase.result_snapshot"))
        assignment_snapshot = None
    if assignment_snapshot is not None:
        if policy is not None:
            recorded_policy = _snapshot_wire(assignment_snapshot).get("policy")
            if recorded_policy is not None and recorded_policy != _policy_wire(policy):
                diagnostics.append(diagnostic(
                    "snapshot_policy_binding_mismatch",
                    "Assignment snapshot is not bound to snapshot_policy.",
                    "assignment.assignment_phase.result_snapshot",
                ))
    authorities = _validate_phase_authorities(
        assignment.get("phase_authorities"), assignment.get("authority"), scope, diagnostics,
    )
    document_root = _normalize_selector(assignment.get("document_root"))
    if document_root is None:
        diagnostics.append(diagnostic(
            "document_root_invalid",
            "Schema-v3 assignment requires one normalized document_root.",
            "assignment.document_root",
        ))
    else:
        configured_document_root = _configured_document_root(root, diagnostics)
        if (
            configured_document_root is not None
            and document_root != configured_document_root
        ):
            diagnostics.append(diagnostic(
                "document_root_mismatch",
                "Assignment document_root must equal the repository configuration.",
                "assignment.document_root",
            ))
        for index, selector in enumerate(
            authorities.get("author", {}).get("allowed_edit_scope", [])
        ):
            if not _canonical_path_in_scope(selector, [document_root]):
                diagnostics.append(diagnostic(
                    "author_scope_outside_document_root",
                    "Author write scope must remain at or below document_root.",
                    "assignment.phase_authorities.author.allowed_edit_scope[%d]"
                    % index,
                ))
        for actor in ("worker", "repository_owner"):
            for index, selector in enumerate(
                authorities.get(actor, {}).get("allowed_edit_scope", [])
            ):
                if _portable_path_overlaps_scope(selector, [document_root]):
                    diagnostics.append(diagnostic(
                        "source_actor_scope_overlaps_document_root",
                        "Worker and repository-owner write scopes must not overlap "
                        "the configured document_root.",
                        "assignment.phase_authorities.%s.allowed_edit_scope[%d]"
                        % (actor, index),
                    ))
        if document_root == ".":
            for actor in sorted(WRITE_ACTORS):
                if authorities.get(actor, {}).get("allowed_edit_scope"):
                    diagnostics.append(diagnostic(
                        "repository_root_document_write_ambiguous",
                        "A repository-root document boundary cannot safely distinguish "
                        "document writes from code writes; every actor write scope must "
                        "remain empty until deterministic surface classification exists.",
                        "assignment.phase_authorities.%s.allowed_edit_scope" % actor,
                    ))
    if policy is not None:
        _validate_actor_scopes_against_policy(policy, authorities, diagnostics)
    if assignment_snapshot is not None:
        _validate_snapshot_symlink_scopes(
            assignment_snapshot,
            authorities,
            "assignment.assignment_phase.result_snapshot",
            diagnostics,
        )
    return context, authorities, policy, assignment_snapshot


def _validate_changed_path(
    value: Any, path: str, diagnostics: List[Diagnostic],
) -> Optional[Mapping[str, Any]]:
    item = _mapping(value)
    _unknown_fields(item, CHANGED_PATH_FIELDS, path, diagnostics)
    _missing_fields(item, CHANGED_PATH_FIELDS, path, diagnostics)
    normalized = normalize_relative_path(item.get("path"))
    if normalized is None:
        diagnostics.append(diagnostic("path_invalid", "Changed path is invalid.", path + ".path"))
        return None
    if item.get("change_kind") not in CHANGE_KINDS:
        diagnostics.append(diagnostic(
            "change_kind_invalid", "Changed path has an invalid change_kind.",
            path + ".change_kind",
        ))
    for name in ("before_entry_digest", "after_entry_digest"):
        value_digest = item.get(name)
        if value_digest != ABSENT_DIGEST and not _digest(value_digest):
            diagnostics.append(diagnostic(
                "entry_digest_invalid", "%s must be absent or canonical SHA-256." % name,
                path + "." + name,
            ))
    return {
        "path": normalized,
        "change_kind": item.get("change_kind"),
        "before_entry_digest": item.get("before_entry_digest"),
        "after_entry_digest": item.get("after_entry_digest"),
    }


def _validate_artifact_deltas(
    value: Any, path: str, diagnostics: List[Diagnostic],
) -> List[Mapping[str, Any]]:
    if not isinstance(value, list):
        diagnostics.append(diagnostic(
            "artifact_deltas_invalid", "artifact_deltas must be an array.", path,
        ))
        return []
    result: List[Mapping[str, Any]] = []
    surfaces: Set[str] = set()
    for index, raw in enumerate(value):
        item_path = "%s[%d]" % (path, index)
        delta = _mapping(raw)
        _unknown_fields(delta, ARTIFACT_DELTA_FIELDS, item_path, diagnostics)
        _missing_fields(delta, ARTIFACT_DELTA_FIELDS, item_path, diagnostics)
        surface = normalize_relative_path(delta.get("source_surface"))
        if surface is None:
            diagnostics.append(diagnostic(
                "artifact_delta_surface_invalid", "Invalid delta surface.",
                item_path + ".source_surface",
            ))
            continue
        if surface in surfaces:
            diagnostics.append(diagnostic(
                "artifact_delta_duplicate", "Artifact delta surfaces must be unique.", item_path,
            ))
        surfaces.add(surface)
        if delta.get("kind") not in {"artifact_delta", "document_delta"}:
            diagnostics.append(diagnostic(
                "artifact_delta_kind_invalid",
                "kind must be artifact_delta or document_delta.",
                item_path + ".kind",
            ))
        if delta.get("change_kind") not in CHANGE_KINDS:
            diagnostics.append(diagnostic(
                "artifact_delta_change_kind_invalid", "Invalid artifact change_kind.",
                item_path + ".change_kind",
            ))
        locators = delta.get("changed_locators")
        if not isinstance(locators, list) or not locators:
            diagnostics.append(diagnostic(
                "artifact_delta_evidence_missing", "Changed locators are required.",
                item_path + ".changed_locators",
            ))
        else:
            for locator_index, raw_locator in enumerate(locators):
                locator = _mapping(raw_locator)
                locator_path = "%s.changed_locators[%d]" % (item_path, locator_index)
                _unknown_fields(locator, LOCATOR_FIELDS, locator_path, diagnostics)
                _missing_fields(locator, {"path"}, locator_path, diagnostics)
                normalized_locator_path = normalize_relative_path(locator.get("path"))
                if normalized_locator_path is None:
                    diagnostics.append(diagnostic(
                        "artifact_delta_locator_invalid",
                        "Locator path must be a normalized repository-relative path.",
                        locator_path + ".path",
                    ))
                elif normalized_locator_path != surface:
                    diagnostics.append(diagnostic(
                        "artifact_delta_locator_surface_mismatch",
                        "Locator path must equal its source_surface.",
                        locator_path + ".path",
                    ))
                for field in sorted(LOCATOR_FIELDS - {"path"}):
                    locator_value = locator.get(field)
                    if locator_value is not None and not _text(locator_value):
                        diagnostics.append(diagnostic(
                            "artifact_delta_locator_invalid",
                            "Optional locator fields must be non-blank strings or null.",
                            locator_path + "." + field,
                        ))
        if not _text(delta.get("semantic_summary")):
            diagnostics.append(diagnostic(
                "artifact_delta_evidence_missing", "A semantic summary is required.", item_path,
            ))
        for name in ("baseline_digest", "resulting_digest"):
            if delta.get(name) != ABSENT_DIGEST and not _digest(delta.get(name)):
                diagnostics.append(diagnostic(
                    "artifact_delta_digest_invalid", "%s is invalid." % name,
                    item_path + "." + name,
                ))
        if not isinstance(delta.get("graph_relevant"), bool):
            diagnostics.append(diagnostic(
                "artifact_delta_graph_relevance_invalid", "graph_relevant must be boolean.",
                item_path + ".graph_relevant",
            ))
        result.append(dict(delta))
    return result


def _validate_actor_delta(
    raw: Any, path: str, allowed_actors: Set[str],
    authorities: Mapping[str, Mapping[str, Any]], diagnostics: List[Diagnostic],
) -> Tuple[Optional[str], List[Mapping[str, Any]], List[Mapping[str, Any]]]:
    value = _mapping(raw)
    _unknown_fields(value, ACTOR_DELTA_FIELDS, path, diagnostics)
    _missing_fields(value, ACTOR_DELTA_FIELDS, path, diagnostics)
    actor = value.get("actor")
    if actor not in allowed_actors:
        diagnostics.append(diagnostic(
            "phase_actor_invalid", "Actor is not permitted in this phase.", path + ".actor",
        ))
        actor = None
    authority = authorities.get(str(actor), {})
    for field in ("authority", "allowed_edit_scope", "excluded_scope"):
        if value.get(field) != authority.get(field):
            diagnostics.append(diagnostic(
                "actor_authority_binding_mismatch",
                "Actor %s does not match assignment phase authority." % (actor or "<invalid>"),
                path + "." + field,
            ))
    raw_changes = value.get("changed_paths")
    if not isinstance(raw_changes, list):
        diagnostics.append(diagnostic(
            "changed_paths_invalid", "changed_paths must be an array.", path + ".changed_paths",
        ))
    changes: List[Mapping[str, Any]] = []
    seen: Set[str] = set()
    for index, raw_change in enumerate(_list(raw_changes)):
        change = _validate_changed_path(
            raw_change, "%s.changed_paths[%d]" % (path, index), diagnostics,
        )
        if change is None:
            continue
        changed = str(change["path"])
        if changed in seen:
            diagnostics.append(diagnostic(
                "actor_change_duplicate", "An actor may attribute a path only once.",
                path + ".changed_paths",
            ))
        seen.add(changed)
        if actor == "linker":
            diagnostics.append(diagnostic(
                "linker_source_write_forbidden", "Linker must not own repository source writes.",
                path + ".changed_paths",
            ))
        elif actor in WRITE_ACTORS and (
            not _canonical_path_in_scope(
                changed, authority.get("allowed_edit_scope", [])
            )
            or _portable_path_in_scope(
                changed, authority.get("excluded_scope", [])
            )
        ):
            diagnostics.append(diagnostic(
                "actor_change_out_of_scope",
                "Actor %s changed an out-of-scope path %s." % (actor, changed),
                path + ".changed_paths",
            ))
        changes.append(change)
    if [item["path"] for item in changes] != sorted(item["path"] for item in changes):
        diagnostics.append(diagnostic(
            "changed_path_order_invalid",
            "Actor changed_paths must use canonical path order.",
            path + ".changed_paths",
        ))
    if changes and value.get("authority") in {"read_only", "review_only", "verification"}:
        diagnostics.append(diagnostic(
            "authority_change_forbidden",
            "This actor authority cannot own repository source writes.",
            path + ".authority",
        ))
    artifacts = _validate_artifact_deltas(
        value.get("artifact_deltas"), path + ".artifact_deltas", diagnostics,
    )
    expected_delta_kind = {
        "worker": "artifact_delta",
        "repository_owner": "artifact_delta",
        "author": "document_delta",
    }.get(str(actor))
    for delta in artifacts:
        if expected_delta_kind is not None and delta.get("kind") != expected_delta_kind:
            diagnostics.append(diagnostic(
                "actor_delta_domain_mismatch",
                "Actor %s must emit %s evidence." % (actor, expected_delta_kind),
                path + ".artifact_deltas",
            ))
    if [item.get("source_surface") for item in artifacts] != sorted(
        item.get("source_surface") for item in artifacts
    ):
        diagnostics.append(diagnostic(
            "artifact_delta_order_invalid",
            "Actor artifact_deltas must use canonical source-surface order.",
            path + ".artifact_deltas",
        ))
    if actor == "linker" and artifacts:
        diagnostics.append(diagnostic(
            "linker_artifact_delta_forbidden", "Linker must not report source artifact deltas.",
            path + ".artifact_deltas",
        ))
    changed_set = {str(item["path"]) for item in changes}
    for delta in artifacts:
        if delta.get("source_surface") not in changed_set:
            diagnostics.append(diagnostic(
                "artifact_delta_unattributed",
                "Artifact deltas must refer to a path attributed to the same actor.",
                path + ".artifact_deltas",
            ))
    return actor, changes, artifacts


def _canonical_changes(changes: Sequence[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return sorted((dict(item) for item in changes), key=lambda item: str(item.get("path")))


def _validate_phase_changes(
    before: Any, after: Any, actor_deltas: Sequence[Any], path: str,
    allowed_actors: Set[str], authorities: Mapping[str, Mapping[str, Any]],
    diagnostics: List[Diagnostic],
) -> Tuple[List[Mapping[str, Any]], List[Mapping[str, Any]]]:
    try:
        expected = _canonical_changes(_changed_paths(before, after))
    except (RuntimeError, TypeError, ValueError, OSError) as error:
        diagnostics.append(_snapshot_error(error, path + ".result_snapshot"))
        expected = []
    attributed: List[Mapping[str, Any]] = []
    all_artifacts: List[Mapping[str, Any]] = []
    actors: Set[str] = set()
    owners: Dict[str, str] = {}
    for index, raw in enumerate(actor_deltas):
        actor, changes, artifacts = _validate_actor_delta(
            raw, "%s.actor_deltas[%d]" % (path, index), allowed_actors,
            authorities, diagnostics,
        )
        if actor is not None:
            if actor in actors:
                diagnostics.append(diagnostic(
                    "phase_actor_duplicate", "Each actor may appear only once per phase.",
                    "%s.actor_deltas[%d].actor" % (path, index),
                ))
            actors.add(actor)
        for change in changes:
            changed = str(change["path"])
            if changed in owners:
                diagnostics.append(diagnostic(
                    "phase_change_duplicate_attribution",
                    "Path %s is attributed to more than one actor." % changed,
                    "%s.actor_deltas[%d].changed_paths" % (path, index),
                ))
            elif actor is not None:
                owners[changed] = actor
            attributed.append(change)
        all_artifacts.extend(artifacts)
    declared_actors = [
        _mapping(raw).get("actor") for raw in actor_deltas
        if isinstance(raw, Mapping)
    ]
    if declared_actors != sorted(declared_actors):
        diagnostics.append(diagnostic(
            "phase_actor_order_invalid",
            "Phase actor_deltas must use canonical actor order.",
            path + ".actor_deltas",
        ))
    if _canonical_changes(attributed) != expected:
        diagnostics.append(diagnostic(
            "phase_change_attribution_mismatch",
            "Actor deltas must partition the exact phase snapshot delta.",
            path + ".actor_deltas",
        ))
    _validate_artifact_bindings(
        before, after, expected, all_artifacts, path, diagnostics,
    )
    return expected, all_artifacts


def _validate_worker_report(
    report: Mapping[str, Any], assignment: Mapping[str, Any], assignment_digest: str,
    context: Mapping[str, Any], worker_changes: Sequence[Mapping[str, Any]],
    worker_artifacts: Sequence[Mapping[str, Any]], diagnostics: List[Diagnostic],
) -> None:
    fields = {
        "assignment_id", "assignment_digest", "context_digest", "execution_mode",
        "status", "purpose", "authority", "goal", "skill_usage", "changed_files",
        "artifact_deltas", "scope_check", "forbidden_change_check", "verification",
    }
    _unknown_fields(report, fields, "worker_report", diagnostics)
    _missing_fields(report, fields, "worker_report", diagnostics)
    bindings = {
        "assignment_id": assignment.get("assignment_id"),
        "assignment_digest": assignment_digest,
        "context_digest": digest_json(context),
        "execution_mode": assignment.get("execution_mode"),
        "purpose": assignment.get("purpose"),
        "authority": assignment.get("authority"),
        "goal": assignment.get("goal"),
    }
    for field, expected in bindings.items():
        if report.get(field) != expected:
            diagnostics.append(diagnostic(
                field + "_mismatch", "Worker report is not bound to the assignment.",
                "worker_report." + field,
            ))
    if report.get("status") not in REPORT_STATUSES:
        diagnostics.append(diagnostic(
            "worker_report_status_invalid", "Invalid worker report status.",
            "worker_report.status",
        ))
    expected_skills = sorted(
        (item.get("skill_id"), item.get("mode"))
        for item in _list(assignment.get("injected_skills"))
        if isinstance(item, Mapping)
    )
    actual_skills: List[Tuple[Any, Any]] = []
    raw_usage = report.get("skill_usage")
    if not isinstance(raw_usage, list):
        diagnostics.append(diagnostic(
            "skill_usage_invalid", "skill_usage must be an array.", "worker_report.skill_usage",
        ))
    for index, raw in enumerate(_list(raw_usage)):
        item = _mapping(raw)
        path = "worker_report.skill_usage[%d]" % index
        _unknown_fields(item, {"skill_id", "mode", "outputs_used", "limits_hit"}, path, diagnostics)
        _missing_fields(item, {"skill_id", "mode", "outputs_used", "limits_hit"}, path, diagnostics)
        actual_skills.append((item.get("skill_id"), item.get("mode")))
        if not _evidence(item.get("outputs_used")) or not isinstance(item.get("limits_hit"), list):
            diagnostics.append(diagnostic(
                "skill_usage_evidence_invalid", "Skill usage requires outputs and limits arrays.", path,
            ))
    if sorted(actual_skills) != expected_skills:
        diagnostics.append(diagnostic(
            "skill_usage_mismatch", "Worker skill usage must equal injected skills.",
            "worker_report.skill_usage",
        ))
    changed_files = sorted(str(item["path"]) for item in worker_changes)
    if report.get("changed_files") != changed_files:
        diagnostics.append(diagnostic(
            "worker_phase_changed_files_mismatch",
            "Worker report changed_files must equal only worker-phase changes.",
            "worker_report.changed_files",
        ))
    report_artifacts = _validate_artifact_deltas(
        report.get("artifact_deltas"), "worker_report.artifact_deltas", diagnostics,
    )
    if report_artifacts != list(worker_artifacts):
        diagnostics.append(diagnostic(
            "worker_phase_artifact_deltas_mismatch",
            "Worker report artifact_deltas must equal worker-phase attribution.",
            "worker_report.artifact_deltas",
        ))
    if report.get("scope_check") != "within_scope":
        diagnostics.append(diagnostic(
            "scope_check_mismatch", "A closed worker phase must be within scope.",
            "worker_report.scope_check",
        ))
    if report.get("forbidden_change_check") != "none":
        diagnostics.append(diagnostic(
            "forbidden_change_claim_invalid", "Forbidden changes prevent closure.",
            "worker_report.forbidden_change_check",
        ))
    verification = _mapping(report.get("verification"))
    _unknown_fields(verification, {"status", "evidence"}, "worker_report.verification", diagnostics)
    if verification.get("status") != "pass" or not _evidence(verification.get("evidence")):
        diagnostics.append(diagnostic(
            "verification_incomplete", "Worker verification must pass with evidence.",
            "worker_report.verification",
        ))


def _parse_phase_snapshot(
    phase: Mapping[str, Any], path: str, diagnostics: List[Diagnostic],
) -> Optional[Any]:
    try:
        return _parse_snapshot(phase.get("result_snapshot"))
    except (RuntimeError, TypeError, ValueError, OSError) as error:
        diagnostics.append(_snapshot_error(error, path + ".result_snapshot"))
        return None


def _validate_phase_parent(
    value: Any, expected: Optional[str], path: str, diagnostics: List[Diagnostic],
) -> None:
    if value != expected:
        diagnostics.append(diagnostic(
            "phase_parent_snapshot_mismatch",
            "Phase baseline_snapshot_digest must equal the preceding result snapshot digest.",
            path + ".baseline_snapshot_digest",
        ))


def _validate_review(
    review: Mapping[str, Any], stage: Any, report: Mapping[str, Any],
    assignment: Mapping[str, Any], assignment_digest: str, author_status: Optional[str],
    finalization: Mapping[str, Any], diagnostics: List[Diagnostic],
) -> None:
    fields = {
        "assignment_id", "assignment_digest", "decision",
        "main_acceptance_allowed", "evidence",
    }
    _unknown_fields(review, fields, "coordinator_review", diagnostics)
    _missing_fields(review, fields, "coordinator_review", diagnostics)
    if review.get("assignment_id") != assignment.get("assignment_id"):
        diagnostics.append(diagnostic(
            "review_assignment_id_mismatch", "Review is not bound to assignment identity.",
            "coordinator_review.assignment_id",
        ))
    if review.get("assignment_digest") != assignment_digest:
        diagnostics.append(diagnostic(
            "review_assignment_digest_mismatch", "Review is not bound to assignment bytes.",
            "coordinator_review.assignment_digest",
        ))
    if not _evidence(review.get("evidence")):
        diagnostics.append(diagnostic(
            "coordinator_review_evidence_missing", "Coordinator review requires evidence.",
            "coordinator_review.evidence",
        ))
    decision = review.get("decision")
    if stage == "pre_acceptance":
        if decision not in {"accept_candidate", "repair", "review", "verify", "escalate", "block"}:
            diagnostics.append(diagnostic(
                "coordinator_decision_invalid", "Invalid pre-acceptance decision.",
                "coordinator_review.decision",
            ))
        if decision == "accept_candidate" and (
            report.get("status") != "DONE" or review.get("main_acceptance_allowed") is not True
        ):
            diagnostics.append(diagnostic(
                "accept_candidate_not_ready", "accept_candidate requires DONE and a Main gate.",
                "coordinator_review.decision",
            ))
        elif decision != "accept_candidate" and review.get("main_acceptance_allowed") is not False:
            diagnostics.append(diagnostic(
                "main_acceptance_gate_invalid", "Non-candidate decisions cannot allow acceptance.",
                "coordinator_review.main_acceptance_allowed",
            ))
    else:
        if decision not in {"closure_complete", "repair", "escalate", "block"}:
            diagnostics.append(diagnostic(
                "coordinator_decision_invalid", "Invalid post-acceptance decision.",
                "coordinator_review.decision",
            ))
        if review.get("main_acceptance_allowed") is not False:
            diagnostics.append(diagnostic(
                "main_acceptance_gate_invalid", "Post-acceptance closure cannot reopen acceptance.",
                "coordinator_review.main_acceptance_allowed",
            ))
        if decision == "closure_complete" and (
            report.get("status") != "DONE"
            or finalization.get("state") not in {"complete", "waived"}
            or author_status != "pass"
        ):
            diagnostics.append(diagnostic(
                "post_acceptance_closure_incomplete",
                "closure_complete requires passing Author finalization evidence.",
                "coordinator_review.decision",
            ))


def validate_v3(
    manifest: Mapping[str, Any], *, root: Path, assignment: Mapping[str, Any],
    assignment_digest: str, evidence_root: Path, linker_runner: Path,
    author_runner: Path, timeout_seconds: float,
    capture_authority_key: Path, capture_authority_key_digest: str,
    acceptance_authority_key: Optional[Path] = None,
    acceptance_authority_key_digest: Optional[str] = None,
    owner_keys: Optional[Mapping[str, Path]] = None,
    owner_key_digests: Optional[Mapping[str, str]] = None,
) -> List[Diagnostic]:
    """Validate schema-v3 closure against immutable phases and live repository state."""

    diagnostics: List[Diagnostic] = []
    canonical_linker, canonical_author = package_runner_paths()
    for name, supplied, canonical in (
        ("linker_runner", linker_runner, canonical_linker),
        ("author_runner", author_runner, canonical_author),
    ):
        try:
            resolved = Path(supplied).resolve()
        except (OSError, TypeError, ValueError):
            resolved = None
        if resolved != canonical:
            diagnostics.append(diagnostic(
                "v3_runner_override_forbidden",
                "Schema v3 evidence runners must be package-owned sibling runners.", name,
            ))
    linker_runner = canonical_linker
    author_runner = canonical_author

    manifest_fields = {
        "schema_version",
        "closure_stage",
        "closure_target",
        "closure_step_ref",
        "worker_report",
        "worker_phase",
        "pre_acceptance_closure_phase",
        "post_acceptance_phase",
        "keystone_closure",
        "coordinator_review",
    }
    _unknown_fields(manifest, manifest_fields, "", diagnostics)
    _missing_fields(manifest, manifest_fields, "", diagnostics)
    if type(manifest.get("schema_version")) is not int or manifest.get("schema_version") != 3:
        diagnostics.append(diagnostic(
            "schema_version_invalid", "Manifest schema_version must be 3.", "schema_version",
        ))
    stage = manifest.get("closure_stage")
    if stage not in {"pre_acceptance", "post_acceptance"}:
        diagnostics.append(diagnostic(
            "closure_stage_invalid", "closure_stage must be pre_acceptance or post_acceptance.",
            "closure_stage",
        ))
    target = manifest.get("closure_target")
    step_ref = manifest.get("closure_step_ref")
    if target not in {"step", "work"}:
        diagnostics.append(diagnostic(
            "closure_target_invalid", "closure_target must be step or work.", "closure_target",
        ))
    if target == "step" and not _text(step_ref):
        diagnostics.append(diagnostic(
            "closure_step_ref_missing", "Step closure requires closure_step_ref.",
            "closure_step_ref",
        ))
    if target == "work" and step_ref is not None:
        diagnostics.append(diagnostic(
            "closure_step_ref_unexpected", "Work closure cannot declare closure_step_ref.",
            "closure_step_ref",
        ))
    if not _digest(assignment_digest):
        diagnostics.append(diagnostic(
            "assignment_digest_invalid", "Assignment digest must be canonical SHA-256.",
            "worker_report.assignment_digest",
        ))

    try:
        root = resolved_repository_root(root)
    except (OSError, RuntimeError) as error:
        diagnostics.append(diagnostic("repository_root_unavailable", str(error), "--root"))
        return diagnostics
    context, authorities, policy, assignment_snapshot = _validate_assignment(
        assignment, target, step_ref, root, diagnostics,
    )
    try:
        evidence_root = evidence_root.resolve(strict=True)
        if not evidence_root.is_dir():
            raise NotADirectoryError(str(evidence_root))
    except (OSError, RuntimeError) as error:
        diagnostics.append(diagnostic("evidence_root_unavailable", str(error), "--evidence-root"))
        return diagnostics
    try:
        evidence_root.relative_to(root)
    except ValueError:
        pass
    else:
        diagnostics.append(diagnostic(
            "evidence_root_inside_repository",
            "Authority evidence must be outside the repository snapshot.", "--evidence-root",
        ))
    try:
        root.relative_to(evidence_root)
    except ValueError:
        pass
    else:
        diagnostics.append(diagnostic(
            "evidence_root_contains_repository",
            "Authority evidence root must not contain the repository tree.",
            "--evidence-root",
        ))

    capture_key: Optional[bytes] = None
    acceptance_key: Optional[bytes] = None
    try:
        capture_key = validate_authority_key(
            capture_authority_key,
            capture_authority_key_digest,
            root=root,
            evidence_root=evidence_root,
        )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        diagnostics.append(diagnostic(
            "capture_authority_key_invalid", str(error), "--capture-authority-key",
        ))
    if stage == "post_acceptance":
        if acceptance_authority_key is None or acceptance_authority_key_digest is None:
            diagnostics.append(diagnostic(
                "acceptance_authority_key_invalid",
                "Post-acceptance validation requires a pinned Main authority key.",
                "--acceptance-authority-key",
            ))
        else:
            try:
                acceptance_key = validate_authority_key(
                    acceptance_authority_key,
                    acceptance_authority_key_digest,
                    root=root,
                    evidence_root=evidence_root,
                )
            except (OSError, RuntimeError, TypeError, ValueError) as error:
                diagnostics.append(diagnostic(
                    "acceptance_authority_key_invalid", str(error),
                    "--acceptance-authority-key",
                ))
        if (
            capture_authority_key_digest == acceptance_authority_key_digest
            or (
                capture_key is not None
                and acceptance_key is not None
                and hmac.compare_digest(
                    _derive_authority_hmac_key(capture_key),
                    _derive_authority_hmac_key(acceptance_key),
                )
            )
        ):
            diagnostics.append(diagnostic(
                "authority_key_separation_required",
                "Coordinator capture and Main acceptance must use distinct authority keys.",
                "--acceptance-authority-key",
            ))
    authority_fingerprints = [capture_authority_key_digest]
    if acceptance_authority_key_digest is not None:
        authority_fingerprints.append(acceptance_authority_key_digest)
    authority_fingerprints.extend((owner_key_digests or {}).values())
    canonical_fingerprints = [
        value for value in authority_fingerprints if _digest(value)
    ]
    if len(canonical_fingerprints) != len(set(canonical_fingerprints)):
        diagnostics.append(diagnostic(
            "application_authority_key_separation_required",
            "Capture, acceptance, and each owner-apply command lane require distinct keys.",
            "--owner-key-sha256",
        ))

    seen_receipt_nonces: Set[str] = set()
    assignment_digest_value: Optional[str] = None
    assignment_capture_time: Optional[datetime] = None
    capture_assignment_id = assignment.get("assignment_id")
    capture_assignment_subject_digest = assignment_subject_digest(assignment)
    capture_context_digest = digest_json(context)
    if assignment_snapshot is not None:
        try:
            assignment_digest_value = _snapshot_digest(assignment_snapshot)
        except (TypeError, ValueError) as error:
            diagnostics.append(_snapshot_error(
                error, "assignment.assignment_phase.result_snapshot",
            ))
        assignment_phase = _mapping(assignment.get("assignment_phase"))
        assignment_capture_reference = _mapping(
            assignment_phase.get("capture_evidence")
        )
        assignment_capture_time = _read_phase_capture_evidence(
            assignment_capture_reference,
            evidence_root=evidence_root,
            root=root,
            phase_id="assignment",
            parent_snapshot_digest=ABSENT_DIGEST,
            snapshot=assignment_snapshot,
            assignment_id=capture_assignment_id,
            assignment_subject_digest=capture_assignment_subject_digest,
            context_digest=capture_context_digest,
            authority_key=capture_key,
            authority_key_digest=capture_authority_key_digest,
            parent_evidence_digest=ABSENT_DIGEST,
            seen_nonces=seen_receipt_nonces,
            diagnostics=diagnostics,
            path="assignment.assignment_phase.capture_evidence",
        )

    worker_phase = _mapping(manifest.get("worker_phase"))
    worker_fields = {
        "phase_id",
        "baseline_snapshot_digest",
        "result_snapshot",
        "capture_evidence",
        "actor_delta",
    }
    _unknown_fields(worker_phase, worker_fields, "worker_phase", diagnostics)
    _missing_fields(worker_phase, worker_fields, "worker_phase", diagnostics)
    if worker_phase.get("phase_id") != "worker":
        diagnostics.append(diagnostic(
            "phase_identity_invalid", "worker_phase.phase_id must be worker.",
            "worker_phase.phase_id",
        ))
    _validate_phase_parent(
        worker_phase.get("baseline_snapshot_digest"), assignment_digest_value,
        "worker_phase", diagnostics,
    )
    worker_snapshot = _parse_phase_snapshot(worker_phase, "worker_phase", diagnostics)
    worker_capture_time: Optional[datetime] = None
    if worker_snapshot is not None:
        worker_capture_reference = _mapping(worker_phase.get("capture_evidence"))
        worker_capture_time = _read_phase_capture_evidence(
            worker_capture_reference,
            evidence_root=evidence_root,
            root=root,
            phase_id="worker",
            parent_snapshot_digest=assignment_digest_value,
            snapshot=worker_snapshot,
            assignment_id=capture_assignment_id,
            assignment_subject_digest=capture_assignment_subject_digest,
            context_digest=capture_context_digest,
            authority_key=capture_key,
            authority_key_digest=capture_authority_key_digest,
            parent_evidence_digest=_mapping(
                _mapping(assignment.get("assignment_phase")).get("capture_evidence")
            ).get("digest"),
            seen_nonces=seen_receipt_nonces,
            diagnostics=diagnostics,
            path="worker_phase.capture_evidence",
        )
        if (
            assignment_capture_time is not None
            and worker_capture_time is not None
            and worker_capture_time <= assignment_capture_time
        ):
            diagnostics.append(diagnostic(
                "phase_capture_order_invalid",
                "Worker capture must occur after assignment capture.",
                "worker_phase.capture_evidence",
            ))
        _validate_snapshot_symlink_scopes(
            worker_snapshot, authorities, "worker_phase.result_snapshot", diagnostics,
        )
    worker_changes: List[Mapping[str, Any]] = []
    worker_artifacts: List[Mapping[str, Any]] = []
    if assignment_snapshot is not None and worker_snapshot is not None:
        actor, declared_changes, worker_artifacts = _validate_actor_delta(
            worker_phase.get("actor_delta"), "worker_phase.actor_delta", {"worker"},
            authorities, diagnostics,
        )
        try:
            worker_changes = _canonical_changes(_changed_paths(assignment_snapshot, worker_snapshot))
        except (RuntimeError, TypeError, ValueError, OSError) as error:
            diagnostics.append(_snapshot_error(error, "worker_phase.result_snapshot"))
        if _canonical_changes(declared_changes) != worker_changes:
            diagnostics.append(diagnostic(
                "phase_change_attribution_mismatch",
                "Worker actor delta must equal the exact worker-phase snapshot delta.",
                "worker_phase.actor_delta.changed_paths",
            ))
        _validate_artifact_bindings(
            assignment_snapshot, worker_snapshot, worker_changes,
            worker_artifacts, "worker_phase.actor_delta", diagnostics,
        )
        if actor != "worker":
            worker_artifacts = []
    report = _mapping(manifest.get("worker_report"))
    _validate_worker_report(
        report, assignment, assignment_digest, context, worker_changes,
        worker_artifacts, diagnostics,
    )

    pre_phase = _mapping(manifest.get("pre_acceptance_closure_phase"))
    pre_fields = {
        "phase_id",
        "baseline_snapshot_digest",
        "result_snapshot",
        "capture_evidence",
        "actor_deltas",
    }
    _unknown_fields(pre_phase, pre_fields, "pre_acceptance_closure_phase", diagnostics)
    _missing_fields(pre_phase, pre_fields, "pre_acceptance_closure_phase", diagnostics)
    if pre_phase.get("phase_id") != "pre_acceptance_closure":
        diagnostics.append(diagnostic(
            "phase_identity_invalid", "Pre-acceptance phase_id is invalid.",
            "pre_acceptance_closure_phase.phase_id",
        ))
    worker_digest_value: Optional[str] = None
    if worker_snapshot is not None:
        try:
            worker_digest_value = _snapshot_digest(worker_snapshot)
        except (TypeError, ValueError) as error:
            diagnostics.append(_snapshot_error(error, "worker_phase.result_snapshot"))
    _validate_phase_parent(
        pre_phase.get("baseline_snapshot_digest"), worker_digest_value,
        "pre_acceptance_closure_phase", diagnostics,
    )
    pre_snapshot = _parse_phase_snapshot(pre_phase, "pre_acceptance_closure_phase", diagnostics)
    pre_capture_time: Optional[datetime] = None
    if pre_snapshot is not None:
        pre_capture_reference = _mapping(pre_phase.get("capture_evidence"))
        pre_capture_time = _read_phase_capture_evidence(
            pre_capture_reference,
            evidence_root=evidence_root,
            root=root,
            phase_id="pre_acceptance_closure",
            parent_snapshot_digest=worker_digest_value,
            snapshot=pre_snapshot,
            assignment_id=capture_assignment_id,
            assignment_subject_digest=capture_assignment_subject_digest,
            context_digest=capture_context_digest,
            authority_key=capture_key,
            authority_key_digest=capture_authority_key_digest,
            parent_evidence_digest=_mapping(
                worker_phase.get("capture_evidence")
            ).get("digest"),
            seen_nonces=seen_receipt_nonces,
            diagnostics=diagnostics,
            path="pre_acceptance_closure_phase.capture_evidence",
        )
        if (
            worker_capture_time is not None
            and pre_capture_time is not None
            and pre_capture_time <= worker_capture_time
        ):
            diagnostics.append(diagnostic(
                "phase_capture_order_invalid",
                "Pre-acceptance capture must occur after worker capture.",
                "pre_acceptance_closure_phase.capture_evidence",
            ))
        _validate_snapshot_symlink_scopes(
            pre_snapshot,
            authorities,
            "pre_acceptance_closure_phase.result_snapshot",
            diagnostics,
        )
    pre_artifacts: List[Mapping[str, Any]] = []
    if worker_snapshot is not None and pre_snapshot is not None:
        raw_actor_deltas = pre_phase.get("actor_deltas")
        if not isinstance(raw_actor_deltas, list):
            diagnostics.append(diagnostic(
                "actor_deltas_invalid", "actor_deltas must be an array.",
                "pre_acceptance_closure_phase.actor_deltas",
            ))
            raw_actor_deltas = []
        _, pre_artifacts = _validate_phase_changes(
            worker_snapshot, pre_snapshot, raw_actor_deltas,
            "pre_acceptance_closure_phase", {"author", "repository_owner", "linker"},
            authorities, diagnostics,
        )
    raw_post_phase = manifest.get("post_acceptance_phase")
    post_phase: Mapping[str, Any] = {}
    post_snapshot: Optional[Any] = None
    post_changes: List[Mapping[str, Any]] = []
    post_artifacts: List[Mapping[str, Any]] = []
    if stage == "pre_acceptance":
        if raw_post_phase is not None:
            diagnostics.append(diagnostic(
                "post_acceptance_phase_premature",
                "Pre-acceptance manifests must use null post_acceptance_phase.",
                "post_acceptance_phase",
            ))
    else:
        if not isinstance(raw_post_phase, Mapping):
            diagnostics.append(diagnostic(
                "post_acceptance_phase_missing",
                "Post-acceptance closure requires an immutable post phase.",
                "post_acceptance_phase",
            ))
        post_phase = _mapping(raw_post_phase)
        post_fields = {
            "phase_id", "baseline_snapshot_digest", "result_snapshot", "acceptance_ref",
            "acceptance_event", "accepted_steps", "capture_evidence",
            "author_evidence_binding", "actor_deltas",
        }
        _unknown_fields(post_phase, post_fields, "post_acceptance_phase", diagnostics)
        _missing_fields(post_phase, post_fields, "post_acceptance_phase", diagnostics)
        if post_phase.get("phase_id") != "post_acceptance":
            diagnostics.append(diagnostic(
                "phase_identity_invalid", "Post-acceptance phase_id is invalid.",
                "post_acceptance_phase.phase_id",
            ))
        pre_digest_value: Optional[str] = None
        if pre_snapshot is not None:
            try:
                pre_digest_value = _snapshot_digest(pre_snapshot)
            except (TypeError, ValueError) as error:
                diagnostics.append(_snapshot_error(error, "pre_acceptance_closure_phase.result_snapshot"))
        _validate_phase_parent(
            post_phase.get("baseline_snapshot_digest"), pre_digest_value,
            "post_acceptance_phase", diagnostics,
        )
        if not _text(post_phase.get("acceptance_ref")):
            diagnostics.append(diagnostic(
                "acceptance_evidence_missing",
                "Post-acceptance phase requires one Main acceptance ref.",
                "post_acceptance_phase.acceptance_ref",
            ))
        accepted_steps = post_phase.get("accepted_steps")
        if (
            not isinstance(accepted_steps, list)
            or not accepted_steps
            or not all(_text(item) for item in accepted_steps)
            or len(accepted_steps) != len(set(accepted_steps))
        ):
            diagnostics.append(diagnostic(
                "accepted_steps_invalid", "accepted_steps must contain unique Step refs.",
                "post_acceptance_phase.accepted_steps",
            ))
        else:
            assignment_steps = _list(
                _mapping(context.get("work_context")).get("step_refs")
            )
            expected_accepted_steps = (
                [step_ref] if target == "step" else assignment_steps
            )
            if accepted_steps != expected_accepted_steps:
                diagnostics.append(diagnostic(
                    "accepted_steps_scope_mismatch",
                    "accepted_steps must exactly match the closure target within "
                    "assignment work context.",
                    "post_acceptance_phase.accepted_steps",
                ))
        acceptance_event_time: Optional[datetime] = None
        acceptance_event_reference = _mapping(post_phase.get("acceptance_event"))
        if pre_snapshot is not None:
            acceptance_event_time = _read_acceptance_event(
                acceptance_event_reference,
                evidence_root=evidence_root,
                root=root,
                assignment_id=capture_assignment_id,
                assignment_digest=assignment_digest,
                context_digest=capture_context_digest,
                policy_digest=_snapshot_wire(pre_snapshot).get("policy_digest"),
                closure_target=target,
                closure_step_ref=step_ref,
                pre_snapshot_digest=pre_digest_value,
                acceptance_ref=post_phase.get("acceptance_ref"),
                accepted_steps=accepted_steps,
                authority_key=acceptance_key,
                authority_key_digest=acceptance_authority_key_digest,
                parent_evidence_digest=_mapping(
                    pre_phase.get("capture_evidence")
                ).get("digest"),
                seen_nonces=seen_receipt_nonces,
                diagnostics=diagnostics,
                path="post_acceptance_phase.acceptance_event",
            )
            if (
                pre_capture_time is not None
                and acceptance_event_time is not None
                and acceptance_event_time <= pre_capture_time
            ):
                diagnostics.append(diagnostic(
                    "acceptance_event_order_invalid",
                    "Main acceptance must occur after pre-acceptance capture.",
                    "post_acceptance_phase.acceptance_event",
                ))
        post_snapshot = _parse_phase_snapshot(post_phase, "post_acceptance_phase", diagnostics)
        if post_snapshot is not None:
            post_capture_time = _read_phase_capture_evidence(
                post_phase.get("capture_evidence"),
                evidence_root=evidence_root,
                root=root,
                phase_id="post_acceptance",
                parent_snapshot_digest=pre_digest_value,
                snapshot=post_snapshot,
                assignment_id=capture_assignment_id,
                assignment_subject_digest=capture_assignment_subject_digest,
                context_digest=capture_context_digest,
                authority_key=capture_key,
                authority_key_digest=capture_authority_key_digest,
                parent_evidence_digest=acceptance_event_reference.get("digest"),
                seen_nonces=seen_receipt_nonces,
                diagnostics=diagnostics,
                path="post_acceptance_phase.capture_evidence",
            )
            if (
                pre_capture_time is not None
                and post_capture_time is not None
                and post_capture_time <= pre_capture_time
            ):
                diagnostics.append(diagnostic(
                    "phase_capture_order_invalid",
                    "Post-acceptance capture must occur after pre-acceptance capture.",
                    "post_acceptance_phase.capture_evidence",
                ))
            if (
                acceptance_event_time is not None
                and post_capture_time is not None
                and post_capture_time <= acceptance_event_time
            ):
                diagnostics.append(diagnostic(
                    "acceptance_event_order_invalid",
                    "Post-acceptance capture must occur after Main acceptance.",
                    "post_acceptance_phase.capture_evidence",
                ))
            _validate_snapshot_symlink_scopes(
                post_snapshot,
                authorities,
                "post_acceptance_phase.result_snapshot",
                diagnostics,
            )
        if pre_snapshot is not None and post_snapshot is not None:
            raw_actor_deltas = post_phase.get("actor_deltas")
            if not isinstance(raw_actor_deltas, list):
                diagnostics.append(diagnostic(
                    "actor_deltas_invalid", "actor_deltas must be an array.",
                    "post_acceptance_phase.actor_deltas",
                ))
                raw_actor_deltas = []
            post_changes, post_artifacts = _validate_phase_changes(
                pre_snapshot, post_snapshot, raw_actor_deltas,
                "post_acceptance_phase", {"author", "linker"},
                authorities, diagnostics,
            )

    closure = _mapping(manifest.get("keystone_closure"))
    closure_fields = {"document_sync", "metadata_sync", "graph_sync", "finalization"}
    if stage == "post_acceptance":
        closure_fields |= {"acceptance_ref", "acceptance_event", "accepted_steps"}
    _unknown_fields(closure, closure_fields, "keystone_closure", diagnostics)
    _missing_fields(closure, closure_fields, "keystone_closure", diagnostics)
    for name in ("document_sync", "metadata_sync"):
        validate_sync_evidence(name, _mapping(closure.get(name)), diagnostics)
    all_artifacts = list(worker_artifacts) + pre_artifacts + post_artifacts
    validate_graph_sync_evidence_v3(
        _mapping(closure.get("graph_sync")), all_artifacts, root, evidence_root,
        linker_runner, timeout_seconds, diagnostics,
        assignment_id=assignment.get("assignment_id"),
        assignment_digest=assignment_digest,
        authorities=authorities,
        worker_phase=worker_phase,
        pre_phase=pre_phase,
        post_phase=post_phase,
        owner_keys=owner_keys or {},
        owner_key_digests=owner_key_digests or {},
    )
    if stage == "post_acceptance":
        if (
            closure.get("acceptance_ref") != post_phase.get("acceptance_ref")
            or closure.get("acceptance_event") != post_phase.get("acceptance_event")
            or closure.get("accepted_steps") != post_phase.get("accepted_steps")
        ):
            diagnostics.append(diagnostic(
                "acceptance_phase_binding_mismatch",
                "Keystone closure acceptance must equal post-acceptance phase evidence.",
                "keystone_closure.acceptance_ref",
            ))
    author_runner_arguments: List[str] = []
    if stage == "post_acceptance":
        author_runner_arguments.extend((
            "--graph-evidence-root",
            str(evidence_root),
        ))
        for owner in sorted(owner_keys or {}):
            author_runner_arguments.extend((
                "--graph-owner-key",
                "%s=%s" % (owner, (owner_keys or {})[owner]),
            ))
        for owner in sorted(owner_key_digests or {}):
            author_runner_arguments.extend((
                "--graph-owner-key-sha256",
                "%s=%s" % (owner, (owner_key_digests or {})[owner]),
            ))
    author_status = validate_finalization_evidence(
        stage, closure, _mapping(closure.get("finalization")),
        _list(_mapping(context.get("work_context")).get("step_refs")),
        evidence_root, root, author_runner, timeout_seconds, diagnostics,
        runner_arguments=author_runner_arguments,
        isolated=(stage == "post_acceptance"),
    )

    finalization = _mapping(closure.get("finalization"))
    if stage == "pre_acceptance" and finalization.get("state") != "not_started":
        diagnostics.append(diagnostic(
            "finalization_before_acceptance",
            "Finalization cannot start before Main acceptance.",
            "keystone_closure.finalization.state",
        ))
    if stage == "post_acceptance" and (
        finalization.get("acceptance_ref") != post_phase.get("acceptance_ref")
    ):
        diagnostics.append(diagnostic(
            "finalization_acceptance_ref_mismatch",
            "Finalization must bind the post-acceptance Main acceptance ref.",
            "keystone_closure.finalization.acceptance_ref",
        ))
    if stage == "post_acceptance" and post_snapshot is not None:
        _validate_post_finalization_binding(
            post_phase,
            finalization,
            post_snapshot,
            post_changes,
            evidence_root,
            diagnostics,
        )

    terminal_snapshot = post_snapshot if stage == "post_acceptance" else pre_snapshot
    if policy is not None and terminal_snapshot is not None:
        try:
            live_snapshot = _capture_snapshot(
                root, policy, _expected_absences(terminal_snapshot),
            )
            if _snapshot_wire(live_snapshot) != _snapshot_wire(terminal_snapshot):
                diagnostics.append(diagnostic(
                    "live_terminal_snapshot_mismatch",
                    "Live repository snapshot must equal the terminal phase result.", "--root",
                ))
        except (RuntimeError, TypeError, ValueError, OSError) as error:
            diagnostics.append(_snapshot_error(error, "--root"))

    review = _mapping(manifest.get("coordinator_review"))
    _validate_review(
        review, stage, report, assignment, assignment_digest, author_status,
        finalization, diagnostics,
    )
    return diagnostics
