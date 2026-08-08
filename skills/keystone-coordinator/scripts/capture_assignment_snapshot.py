#!/usr/bin/env python3
"""Capture one package-owned immutable Coordinator assignment snapshot."""

import argparse
from datetime import datetime, timezone
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Sequence

from closure_actual_state import (
    SnapshotCaptureError,
    capture_repository_snapshot_v3,
    digest_bytes,
    normalize_relative_path,
    resolved_repository_root,
)
from closure_v3 import build_phase_capture_envelope


ENVELOPE_SCHEMA_VERSION = 1
EXECUTION_ERROR_CODES = {
    "snapshot_root_unreadable",
    "snapshot_no_follow_unavailable",
    "snapshot_discovery_failed",
    "snapshot_path_unreadable",
    "snapshot_generation_unstable",
    "expected_absence_check_failed",
}


class DuplicateJsonKey(ValueError):
    pass


def _reject_duplicate_keys(pairs: Sequence[Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKey("duplicate JSON key: %s" % key)
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError("non-finite JSON value: %s" % value)


def _load_policy(path: Path) -> Mapping[str, Any]:
    raw = path.read_text(encoding="utf-8")
    value = json.loads(
        raw,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite,
    )
    if not isinstance(value, Mapping):
        raise ValueError("snapshot policy root must be an object")
    return value


def _diagnostic(code: str, message: str, path: str) -> Dict[str, str]:
    return {
        "severity": "error",
        "code": code,
        "message": message,
        "path": path,
    }


def _envelope(
    status: str,
    *,
    snapshot: Optional[Mapping[str, Any]] = None,
    capture_evidence: Optional[Mapping[str, str]] = None,
    diagnostic: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    diagnostics = [dict(diagnostic)] if diagnostic is not None else []
    return {
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "status": status,
        "snapshot": dict(snapshot) if snapshot is not None else None,
        "capture_evidence": (
            dict(capture_evidence) if capture_evidence is not None else None
        ),
        "diagnostics": diagnostics,
        "summary": {"errors": len(diagnostics), "warnings": 0},
    }


class _JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        payload = _envelope(
            "error",
            diagnostic=_diagnostic("invocation_invalid", message, "arguments"),
        )
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        raise SystemExit(2)


def _positive_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if not 0 < parsed <= 10:
        raise argparse.ArgumentTypeError("must be between 1 and 10")
    return parsed


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def write_immutable_evidence(
    evidence_root: Path,
    relative: str,
    payload: bytes,
) -> None:
    normalized = normalize_relative_path(relative)
    if normalized is None:
        raise ValueError("capture evidence path must be normalized repository-relative text")
    root = evidence_root.resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(str(evidence_root))
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise OSError("phase capture evidence requires no-follow descriptor APIs")
    directory_flags = (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    directory_fd = os.open(str(root), directory_flags)
    try:
        parts = PurePosixPath(normalized).parts
        for component in parts[:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        file_fd = os.open(parts[-1], file_flags, 0o600, dir_fd=directory_fd)
        try:
            offset = 0
            while offset < len(payload):
                offset += os.write(file_fd, payload[offset:])
            os.fsync(file_fd)
            state = os.fstat(file_fd)
            if not stat.S_ISREG(state.st_mode) or state.st_nlink != 1:
                raise OSError("authority evidence is not an immutable regular file")
        finally:
            os.close(file_fd)
    finally:
        os.close(directory_fd)


def _evidence_file_identity(value: os.stat_result) -> tuple[int, ...]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
        value.st_nlink,
        stat.S_IFMT(value.st_mode),
    )


def read_immutable_evidence(evidence_root: Path, relative: str) -> bytes:
    """Read one single-link evidence file without following path components."""

    normalized = normalize_relative_path(relative)
    if normalized is None:
        raise ValueError("evidence path must be normalized repository-relative text")
    root = evidence_root.resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(str(evidence_root))
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise OSError("authority evidence requires no-follow descriptor APIs")
    directory_flags = (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    directory_fd = os.open(str(root), directory_flags)
    try:
        parts = PurePosixPath(normalized).parts
        for component in parts[:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        before = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise OSError("authority evidence must be a single-link regular file")
        file_fd = os.open(parts[-1], file_flags, dir_fd=directory_fd)
        try:
            opened = os.fstat(file_fd)
            if _evidence_file_identity(opened) != _evidence_file_identity(before):
                raise OSError("authority evidence identity changed before read")
            chunks: List[bytes] = []
            while True:
                chunk = os.read(file_fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_fd = os.fstat(file_fd)
            if _evidence_file_identity(after_fd) != _evidence_file_identity(opened):
                raise OSError("authority evidence changed during read")
        finally:
            os.close(file_fd)
        after_path = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if _evidence_file_identity(after_path) != _evidence_file_identity(before):
            raise OSError("authority evidence changed after read")
        raw = b"".join(chunks)
        if len(raw) != before.st_size:
            raise OSError("authority evidence size changed during read")
        return raw
    finally:
        os.close(directory_fd)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _JsonArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--expected-absence", action="append", default=[])
    parser.add_argument("--max-attempts", type=_positive_integer, default=3)
    parser.add_argument(
        "--phase-id",
        choices=(
            "assignment",
            "worker",
            "pre_acceptance_closure",
            "post_acceptance",
        ),
    )
    parser.add_argument("--parent-snapshot-digest")
    parser.add_argument("--parent-evidence-digest")
    parser.add_argument("--assignment-id")
    parser.add_argument("--assignment-subject-digest")
    parser.add_argument("--context-digest")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--capture-evidence-path")
    parser.add_argument("--capture-authority-key", type=Path)
    parser.add_argument("--trusted-capture-authority-key-sha256")
    args = parser.parse_args(argv)

    phase_values = (
        args.phase_id,
        args.parent_snapshot_digest,
        args.parent_evidence_digest,
        args.assignment_id,
        args.assignment_subject_digest,
        args.context_digest,
        args.evidence_root,
        args.capture_evidence_path,
        args.capture_authority_key,
        args.trusted_capture_authority_key_sha256,
    )
    if any(value is not None for value in phase_values) and not all(
        value is not None for value in phase_values
    ):
        parser.error(
            "--phase-id, --parent-snapshot-digest, --parent-evidence-digest, "
            "--assignment-id, --assignment-subject-digest, --context-digest, "
            "--evidence-root, "
            "--capture-evidence-path, --capture-authority-key, and "
            "--trusted-capture-authority-key-sha256 must be supplied together"
        )

    try:
        policy = _load_policy(args.policy)
        repository_root = resolved_repository_root(args.root)
        if args.evidence_root is not None:
            evidence_root = args.evidence_root.resolve(strict=True)
            try:
                evidence_root.relative_to(repository_root)
            except ValueError:
                pass
            else:
                raise ValueError("evidence root cannot be inside repository root")
            try:
                repository_root.relative_to(evidence_root)
            except ValueError:
                pass
            else:
                raise ValueError("evidence root cannot contain repository root")
        snapshot = capture_repository_snapshot_v3(
            repository_root,
            policy,
            expected_absences=args.expected_absence,
            max_attempts=args.max_attempts,
        )
        capture_reference = None
        if args.phase_id is not None:
            captured_at = datetime.now(timezone.utc).isoformat(
                timespec="microseconds"
            ).replace("+00:00", "Z")
            phase_envelope = build_phase_capture_envelope(
                root=repository_root,
                phase_id=args.phase_id,
                parent_snapshot_digest=args.parent_snapshot_digest,
                snapshot=snapshot,
                captured_at=captured_at,
                assignment_id=args.assignment_id,
                assignment_subject_digest=args.assignment_subject_digest,
                context_digest=args.context_digest,
                evidence_root=evidence_root,
                parent_evidence_digest=args.parent_evidence_digest,
                capture_authority_key=args.capture_authority_key,
                capture_authority_key_digest=(
                    args.trusted_capture_authority_key_sha256
                ),
            )
            phase_bytes = _canonical_json_bytes(phase_envelope)
            write_immutable_evidence(
                evidence_root,
                args.capture_evidence_path,
                phase_bytes,
            )
            capture_reference = {
                "path": normalize_relative_path(args.capture_evidence_path),
                "digest": digest_bytes(phase_bytes),
            }
    except SnapshotCaptureError as error:
        status = "error" if error.code in EXECUTION_ERROR_CODES else "fail"
        payload = _envelope(
            status,
            diagnostic=_diagnostic(error.code, str(error), error.path),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJsonKey, ValueError) as error:
        status = "error"
        code = (
            "phase_capture_execution_failed"
            if args.phase_id is not None
            else "snapshot_policy_unreadable"
        )
        payload = _envelope(
            status,
            diagnostic=_diagnostic(
                code,
                str(error),
                "--capture-evidence-path" if args.phase_id is not None else "--policy",
            ),
        )
    else:
        status = "pass"
        payload = _envelope(
            status,
            snapshot=snapshot.wire(),
            capture_evidence=capture_reference,
        )

    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return {"pass": 0, "fail": 1, "error": 2}[status]


if __name__ == "__main__":
    sys.exit(main())
