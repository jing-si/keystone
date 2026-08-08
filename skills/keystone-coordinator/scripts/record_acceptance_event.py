#!/usr/bin/env python3
"""Record one Main acceptance event under an external authority key."""

import argparse
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from capture_assignment_snapshot import read_immutable_evidence, write_immutable_evidence
from closure_actual_state import (
    SnapshotCaptureError,
    capture_repository_snapshot_v3,
    digest_bytes,
    normalize_relative_path,
    parse_repository_snapshot_v3,
    resolved_repository_root,
)
from closure_v3 import build_acceptance_event_envelope


ENVELOPE_SCHEMA_VERSION = 1


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
    acceptance_event: Optional[Mapping[str, str]] = None,
    diagnostic: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    diagnostics = [dict(diagnostic)] if diagnostic is not None else []
    return {
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "status": status,
        "acceptance_event": (
            dict(acceptance_event) if acceptance_event is not None else None
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


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


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


def _load_pre_snapshot(evidence_root: Path, relative: str) -> Any:
    raw = read_immutable_evidence(evidence_root, relative)
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite,
    )
    snapshot = parse_repository_snapshot_v3(value)
    if raw != _canonical_json_bytes(snapshot.wire()):
        raise ValueError("pre snapshot must use canonical JSON bytes")
    return snapshot


def _disjoint_evidence_root(root: Path, evidence_root: Path) -> Path:
    resolved = evidence_root.resolve(strict=True)
    if not resolved.is_dir():
        raise NotADirectoryError(str(evidence_root))
    try:
        resolved.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("evidence root cannot be inside repository root")
    try:
        root.relative_to(resolved)
    except ValueError:
        pass
    else:
        raise ValueError("evidence root cannot contain repository root")
    return resolved


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _JsonArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--acceptance-event-path", required=True)
    parser.add_argument("--assignment-id", required=True)
    parser.add_argument("--assignment-digest", required=True)
    parser.add_argument("--context-digest", required=True)
    parser.add_argument("--policy-digest", required=True)
    parser.add_argument("--closure-target", required=True, choices=("step", "work"))
    parser.add_argument("--closure-step-ref")
    parser.add_argument("--pre-snapshot-path", required=True)
    parser.add_argument("--pre-snapshot-digest", required=True)
    parser.add_argument("--parent-evidence-digest", required=True)
    parser.add_argument("--acceptance-ref", required=True)
    parser.add_argument("--accepted-step", action="append", required=True)
    parser.add_argument("--accepted-by", default="main")
    parser.add_argument("--acceptance-authority-key", required=True, type=Path)
    parser.add_argument(
        "--trusted-acceptance-authority-key-sha256",
        required=True,
    )
    args = parser.parse_args(argv)

    try:
        repository_root = resolved_repository_root(args.root)
        evidence_root = _disjoint_evidence_root(
            repository_root,
            args.evidence_root,
        )
        relative = normalize_relative_path(args.acceptance_event_path)
        if relative is None:
            raise ValueError(
                "acceptance event path must be normalized repository-relative text"
            )
        pre_snapshot_relative = normalize_relative_path(args.pre_snapshot_path)
        if pre_snapshot_relative is None:
            raise ValueError(
                "pre snapshot path must be normalized repository-relative text"
            )
        pre_snapshot = _load_pre_snapshot(evidence_root, pre_snapshot_relative)
        if pre_snapshot.policy.digest != args.policy_digest:
            raise ValueError("policy digest does not match pre snapshot evidence")
        if pre_snapshot.snapshot_digest != args.pre_snapshot_digest:
            raise ValueError("pre snapshot digest does not match pre snapshot evidence")
        observed_snapshot = capture_repository_snapshot_v3(
            repository_root,
            pre_snapshot.policy,
            expected_absences=pre_snapshot.expected_absences,
        )
        if observed_snapshot.wire() != pre_snapshot.wire():
            raise ValueError(
                "live repository snapshot does not equal the pre-acceptance snapshot"
            )
        accepted_at = datetime.now(timezone.utc).isoformat(
            timespec="microseconds"
        ).replace("+00:00", "Z")
        event = build_acceptance_event_envelope(
            root=repository_root,
            evidence_root=evidence_root,
            assignment_id=args.assignment_id,
            assignment_digest=args.assignment_digest,
            context_digest=args.context_digest,
            policy_digest=args.policy_digest,
            closure_target=args.closure_target,
            closure_step_ref=args.closure_step_ref,
            pre_snapshot_digest=args.pre_snapshot_digest,
            observed_snapshot_digest=observed_snapshot.snapshot_digest,
            parent_evidence_digest=args.parent_evidence_digest,
            acceptance_ref=args.acceptance_ref,
            accepted_steps=args.accepted_step,
            accepted_at=accepted_at,
            accepted_by=args.accepted_by,
            acceptance_authority_key=args.acceptance_authority_key,
            acceptance_authority_key_digest=(
                args.trusted_acceptance_authority_key_sha256
            ),
        )
        raw = _canonical_json_bytes(event)
        write_immutable_evidence(evidence_root, relative, raw)
        reference = {"path": relative, "digest": digest_bytes(raw)}
    except (
        DuplicateJsonKey,
        json.JSONDecodeError,
        OSError,
        RuntimeError,
        SnapshotCaptureError,
        TypeError,
        UnicodeError,
        ValueError,
    ) as error:
        status = "error"
        payload = _envelope(
            status,
            diagnostic=_diagnostic(
                "acceptance_event_execution_failed",
                str(error),
                "--acceptance-event-path",
            ),
        )
    else:
        status = "pass"
        payload = _envelope(status, acceptance_event=reference)

    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return {"pass": 0, "fail": 1, "error": 2}[status]


if __name__ == "__main__":
    sys.exit(main())
