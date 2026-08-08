"""Read-only validation of trusted owner patch-application receipts."""

from dataclasses import dataclass
import hashlib
import hmac
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple
import unicodedata

from .model import Diagnostic
from .validation_support import diagnostic


APPLICATION_PLAN_FIELDS = (
    "schema_version",
    "transaction_id",
    "scope_ref",
    "input_deltas",
    "canonical_mutations",
    "surface_patches",
)
APPLICATION_EVIDENCE_FIELDS = {
    "schema_version",
    "transaction_id",
    "transaction_digest",
    "repository_root_digest",
    "assignment_id",
    "assignment_digest",
    "receipts",
}
EVIDENCE_REFERENCE_FIELDS = {"path", "digest"}
ENVELOPE_FIELDS = {"schema_version", "producer", "status", "subject", "receipt"}
SUBJECT_FIELDS = {
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
RECEIPT_FIELDS = {
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
PATCH_RECEIPT_FIELDS = {"patch", "result", "resulting_digest"}
PATCH_FIELDS = {
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
}
OWNERS = frozenset({"author", "main", "coordinator"})
PRODUCER = "keystone-owned-surface-apply"
TRUST_MODEL = "trusted-host-hmac-sha256"
COMMAND_ID = "keystone-owned-surface-apply-v1"
ABSENT_DIGEST = "absent"
AUTHORITY_KEY_MIN_BYTES = 32
KEY_DERIVATION_LABEL = b"keystone-owned-surface-apply-key-v1\0"
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
HMAC_PATTERN = re.compile(r"^hmac-sha256:[0-9a-f]{64}$")
NONCE_PATTERN = re.compile(r"^nonce:[0-9a-f]{64}$")


class DuplicateJsonKey(ValueError):
    pass


@dataclass(frozen=True)
class VerifiedApplicationReceipt:
    path: str
    digest: str
    raw_bytes: bytes
    envelope: Mapping[str, Any]
    patch_id: str
    owner: str
    phase_id: str


@dataclass(frozen=True)
class VerifiedApplicationEvidence:
    aggregate: Mapping[str, Any]
    raw_bytes: bytes
    receipts: Tuple[VerifiedApplicationReceipt, ...]


@dataclass(frozen=True)
class ApplicationEvidenceValidationResult:
    diagnostics: Tuple[Diagnostic, ...]
    evidence: Optional[VerifiedApplicationEvidence]


def canonical_json_bytes(value: Any) -> bytes:
    """Return the canonical bytes used by owner requests and receipts."""

    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_json(value: Any) -> str:
    return digest_bytes(canonical_json_bytes(value))


def application_plan_projection(transaction: Mapping[str, Any]) -> Dict[str, Any]:
    """Project the immutable pre-application portion of transaction schema v2."""

    if not isinstance(transaction, Mapping):
        raise TypeError("application plan transaction must be an object")
    return {field: transaction.get(field) for field in APPLICATION_PLAN_FIELDS}


def application_plan_digest(transaction: Mapping[str, Any]) -> str:
    """Digest the non-circular ready-to-apply transaction plan projection."""

    return digest_json(application_plan_projection(transaction))


def repository_root_digest(root: Path) -> str:
    return digest_json({"repository_root": str(root.resolve(strict=True))})


def evidence_root_digest(evidence_root: Path) -> str:
    return digest_json({"evidence_root": str(evidence_root.resolve(strict=True))})


def _reject_duplicate_keys(pairs: Sequence[Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKey("duplicate JSON key: %s" % key)
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError("non-finite JSON number is forbidden: %s" % value)


def _load_canonical_json(raw: bytes) -> Any:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
        canonical = canonical_json_bytes(value)
    except RecursionError as error:
        raise ValueError("JSON nesting exceeds supported depth") from error
    if raw != canonical:
        raise ValueError("JSON bytes are not canonical")
    return value


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and DIGEST_PATTERN.fullmatch(value) is not None


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalize_evidence_path(value: Any) -> Optional[str]:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        return None
    if unicodedata.normalize("NFC", value) != value:
        return None
    candidate = PurePosixPath(value)
    if (
        candidate.is_absolute()
        or candidate.as_posix() != value
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        return None
    return candidate.as_posix()


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


def _directory_flags() -> int:
    return (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )


def _file_flags() -> int:
    return os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


def _require_descriptor_security() -> None:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise OSError("application evidence requires no-follow descriptor APIs")


def _read_relative_single_link(
    root: Path, relative: str, *, require_private_owner: bool = False,
) -> bytes:
    _require_descriptor_security()
    parts = PurePosixPath(relative).parts
    directory_fds = [os.open(str(root), _directory_flags())]
    try:
        directory_identities = [_file_identity(os.fstat(directory_fds[0]))]
        for component in parts[:-1]:
            next_fd = os.open(
                component, _directory_flags(), dir_fd=directory_fds[-1]
            )
            directory_fds.append(next_fd)
            directory_identities.append(_file_identity(os.fstat(next_fd)))
        before = os.stat(
            parts[-1], dir_fd=directory_fds[-1], follow_symlinks=False
        )
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise OSError("protected evidence must be a single-link regular file")
        if require_private_owner:
            if stat.S_IMODE(before.st_mode) & 0o077:
                raise OSError("authority key grants group/world permissions")
            if hasattr(os, "geteuid") and before.st_uid != os.geteuid():
                raise OSError("authority key is not owned by the current OS user")
        file_fd = os.open(parts[-1], _file_flags(), dir_fd=directory_fds[-1])
        try:
            opened = os.fstat(file_fd)
            if _file_identity(opened) != _file_identity(before):
                raise OSError("protected evidence identity changed before read")
            chunks = []
            while True:
                chunk = os.read(file_fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_fd = os.fstat(file_fd)
            if _file_identity(after_fd) != _file_identity(opened):
                raise OSError("protected evidence changed during read")
        finally:
            os.close(file_fd)
        after_path = os.stat(
            parts[-1], dir_fd=directory_fds[-1], follow_symlinks=False
        )
        if _file_identity(after_path) != _file_identity(before):
            raise OSError("protected evidence changed after read")
        raw = b"".join(chunks)
        if len(raw) != before.st_size:
            raise OSError("protected evidence size changed during read")

        reopened_fd: Optional[int] = os.open(str(root), _directory_flags())
        try:
            if _file_identity(os.fstat(reopened_fd)) != directory_identities[0]:
                raise OSError("protected evidence ancestor chain changed during read")
            for index, component in enumerate(parts[:-1], start=1):
                next_fd = os.open(
                    component, _directory_flags(), dir_fd=reopened_fd
                )
                os.close(reopened_fd)
                reopened_fd = next_fd
                if (
                    _file_identity(os.fstat(reopened_fd))
                    != directory_identities[index]
                ):
                    raise OSError(
                        "protected evidence ancestor chain changed during read"
                    )
            live_leaf = os.stat(
                parts[-1], dir_fd=reopened_fd, follow_symlinks=False
            )
            if _file_identity(live_leaf) != _file_identity(before):
                raise OSError("protected evidence path changed during read")
        finally:
            if reopened_fd is not None:
                os.close(reopened_fd)
        return raw
    finally:
        for directory_fd in reversed(directory_fds):
            os.close(directory_fd)


def _read_absolute_single_link(
    path: Path, *, require_private_owner: bool = False,
) -> bytes:
    _require_descriptor_security()
    supplied = Path(path)
    if not supplied.is_absolute():
        raise OSError("protected file path must be absolute")
    resolved = supplied.resolve(strict=True)
    if supplied != resolved:
        raise OSError("protected file path must not contain aliases or symlinks")
    parts = resolved.parts
    return _read_relative_single_link(
        Path(parts[0]),
        PurePosixPath(*parts[1:]).as_posix(),
        require_private_owner=require_private_owner,
    )


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _load_owner_keys(
    *,
    owners: Sequence[str],
    owner_keys: Mapping[str, Path],
    owner_key_digests: Mapping[str, str],
    root: Path,
    evidence_root: Path,
    findings: list,
) -> Dict[str, bytes]:
    expected = set(owners)
    supplied_paths = set(owner_keys)
    supplied_digests = set(owner_key_digests)
    for owner in sorted(expected - supplied_paths):
        findings.append(diagnostic(
            "application_owner_key_missing",
            "Applied owner %s requires an external authority key." % owner,
            "--owner-key",
        ))
    for owner in sorted(expected - supplied_digests):
        findings.append(diagnostic(
            "application_owner_key_digest_missing",
            "Applied owner %s requires a pinned authority key digest." % owner,
            "--owner-key-sha256",
        ))
    for owner in sorted((supplied_paths | supplied_digests) - expected):
        findings.append(diagnostic(
            "application_owner_key_unexpected",
            "Owner key binding has no applied patch: %s" % owner,
            "--owner-key",
        ))
    fingerprints = [
        owner_key_digests[owner]
        for owner in sorted(expected & supplied_digests)
    ]
    if len(fingerprints) != len(set(fingerprints)):
        findings.append(diagnostic(
            "application_owner_key_separation_required",
            "Distinct applied owners require distinct pinned authority keys.",
            "--owner-key-sha256",
        ))
    result: Dict[str, bytes] = {}
    for owner in sorted(expected & supplied_paths & supplied_digests):
        path = Path(owner_keys[owner])
        pinned = owner_key_digests[owner]
        try:
            resolved = path.resolve(strict=True)
            if _path_is_within(resolved, root) or _path_is_within(
                resolved, evidence_root
            ):
                raise OSError(
                    "authority key must be outside repository and evidence roots"
                )
            raw = _read_absolute_single_link(path, require_private_owner=True)
            if len(raw) < AUTHORITY_KEY_MIN_BYTES:
                raise OSError("authority key must contain at least 32 raw bytes")
        except (OSError, RuntimeError, ValueError) as error:
            findings.append(diagnostic(
                "application_owner_key_invalid", str(error), "--owner-key",
            ))
            continue
        if not _is_digest(pinned) or digest_bytes(raw) != pinned:
            findings.append(diagnostic(
                "application_owner_key_mismatch",
                "Owner key does not match its pinned SHA-256 digest.",
                "--owner-key-sha256",
            ))
            continue
        result[owner] = raw
    return result


def _package_identity(owner: str) -> Tuple[str, str]:
    skills_root = Path(__file__).resolve().parents[3]
    package = "keystone-author" if owner == "author" else "keystone-coordinator"
    scripts = skills_root / package / "scripts"
    runner = scripts / "run_owned_surface_apply.py"
    runtime = scripts / "owned_surface_apply_runtime.py"
    return (
        digest_bytes(_read_absolute_single_link(runner)),
        digest_bytes(_read_absolute_single_link(runtime)),
    )


def _receipt_mac(
    key: bytes, envelope: Mapping[str, Any], receipt: Mapping[str, Any],
) -> str:
    unsigned_envelope = dict(envelope)
    unsigned_envelope.pop("receipt", None)
    unsigned_receipt = dict(receipt)
    unsigned_receipt.pop("mac", None)
    payload = canonical_json_bytes({
        "envelope": unsigned_envelope,
        "receipt": unsigned_receipt,
    })
    derived = hashlib.sha256(KEY_DERIVATION_LABEL + key).digest()
    return "hmac-sha256:" + hmac.new(
        derived, payload, hashlib.sha256,
    ).hexdigest()


def _transaction_application_sequence(
    transaction: Mapping[str, Any], findings: list,
) -> Tuple[Tuple[Mapping[str, Any], Mapping[str, Any]], ...]:
    patches = transaction.get("surface_patches")
    results = transaction.get("apply_results")
    attestations = transaction.get("attestations")
    if not all(isinstance(value, list) for value in (patches, results, attestations)):
        findings.append(diagnostic(
            "application_transaction_invalid",
            "Application verification requires patch, attestation, and result arrays.",
        ))
        return ()
    patch_by_id = {
        item.get("patch_id"): item
        for item in patches
        if isinstance(item, Mapping) and _has_text(item.get("patch_id"))
    }
    sequence = []
    seen = set()
    for index, result in enumerate(results):
        if not isinstance(result, Mapping) or result.get("result") != "applied":
            continue
        patch_id = result.get("patch_id")
        patch = patch_by_id.get(patch_id)
        if patch is None or patch_id in seen:
            findings.append(diagnostic(
                "application_transaction_invalid",
                "Applied results must uniquely reference a declared patch.",
                "apply_results[%d]" % index,
            ))
            continue
        seen.add(patch_id)
        confirmations = [
            item for item in attestations
            if isinstance(item, Mapping)
            and item.get("patch_id") == patch_id
            and item.get("owner") == patch.get("owner")
            and item.get("decision") == "confirm"
        ]
        if len(confirmations) != 1:
            findings.append(diagnostic(
                "application_receipt_attestation_missing",
                "Applied patch requires exactly one confirmed owner attestation.",
                "apply_results[%d]" % index,
            ))
        sequence.append((patch, result))
    return tuple(sequence)


def _append_schema_diagnostic(
    findings: list, code: str, message: str, path: str,
) -> None:
    findings.append(diagnostic(code, message, path))


def validate_application_evidence(
    *,
    transaction: Mapping[str, Any],
    application_evidence: Mapping[str, Any],
    root: Path,
    evidence_root: Path,
    owner_keys: Mapping[str, Path],
    owner_key_digests: Mapping[str, str],
) -> ApplicationEvidenceValidationResult:
    """Validate aggregate evidence and every signed owner receipt without writing."""

    findings = []
    if (
        not isinstance(transaction, Mapping)
        or type(transaction.get("schema_version")) is not int
        or transaction.get("schema_version") != 2
    ):
        findings.append(diagnostic(
            "application_transaction_schema_invalid",
            "Application receipts require a canonical transaction schema v2.",
        ))
        return ApplicationEvidenceValidationResult(tuple(findings), None)
    try:
        root = Path(root).resolve(strict=True)
        evidence_root = Path(evidence_root).resolve(strict=True)
        if not root.is_dir() or not evidence_root.is_dir():
            raise NotADirectoryError("root inputs must be directories")
    except (OSError, RuntimeError, ValueError) as error:
        findings.append(diagnostic(
            "application_evidence_context_invalid", str(error), "--evidence-root",
        ))
        return ApplicationEvidenceValidationResult(tuple(findings), None)
    if _path_is_within(evidence_root, root) or _path_is_within(root, evidence_root):
        findings.append(diagnostic(
            "application_evidence_context_invalid",
            "Repository and evidence roots must be disjoint in both directions.",
            "--evidence-root",
        ))
        return ApplicationEvidenceValidationResult(tuple(findings), None)
    if not isinstance(application_evidence, Mapping) or set(
        application_evidence
    ) != EVIDENCE_REFERENCE_FIELDS:
        findings.append(diagnostic(
            "application_evidence_reference_invalid",
            "application_evidence must contain exactly path and digest.",
            "application_evidence",
        ))
        return ApplicationEvidenceValidationResult(tuple(findings), None)
    aggregate_relative = normalize_evidence_path(application_evidence.get("path"))
    if aggregate_relative is None or not _is_digest(application_evidence.get("digest")):
        findings.append(diagnostic(
            "application_evidence_reference_invalid",
            "Application evidence requires a normalized path and SHA-256 digest.",
            "application_evidence",
        ))
        return ApplicationEvidenceValidationResult(tuple(findings), None)
    try:
        aggregate_raw = _read_relative_single_link(
            evidence_root, aggregate_relative
        )
    except (OSError, RuntimeError, ValueError) as error:
        findings.append(diagnostic(
            "application_evidence_unreadable", str(error), aggregate_relative,
        ))
        return ApplicationEvidenceValidationResult(tuple(findings), None)
    if digest_bytes(aggregate_raw) != application_evidence["digest"]:
        findings.append(diagnostic(
            "application_evidence_digest_mismatch",
            "Aggregate raw bytes do not match the manifest digest.",
            aggregate_relative,
        ))
    try:
        aggregate = _load_canonical_json(aggregate_raw)
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        code = (
            "application_evidence_noncanonical"
            if str(error) == "JSON bytes are not canonical"
            else "application_evidence_invalid"
        )
        findings.append(diagnostic(code, str(error), aggregate_relative))
        return ApplicationEvidenceValidationResult(tuple(findings), None)
    if not isinstance(aggregate, Mapping) or set(aggregate) != APPLICATION_EVIDENCE_FIELDS:
        findings.append(diagnostic(
            "application_evidence_schema_invalid",
            "Aggregate application evidence does not match exact schema v1.",
            aggregate_relative,
        ))
        return ApplicationEvidenceValidationResult(tuple(findings), None)
    if type(aggregate.get("schema_version")) is not int or aggregate.get(
        "schema_version"
    ) != 1:
        _append_schema_diagnostic(
            findings,
            "application_evidence_schema_invalid",
            "Aggregate application evidence schema_version must be 1.",
            aggregate_relative,
        )
    expected_plan_digest = application_plan_digest(transaction)
    expected_root_digest = repository_root_digest(root)
    if (
        aggregate.get("transaction_id") != transaction.get("transaction_id")
        or aggregate.get("transaction_digest") != expected_plan_digest
    ):
        findings.append(diagnostic(
            "application_transaction_mismatch",
            "Aggregate evidence is not bound to the immutable transaction plan.",
            aggregate_relative,
        ))
    if aggregate.get("repository_root_digest") != expected_root_digest:
        findings.append(diagnostic(
            "application_repository_root_mismatch",
            "Aggregate evidence belongs to a different repository root.",
            aggregate_relative,
        ))
    if not _has_text(aggregate.get("assignment_id")) or not _is_digest(
        aggregate.get("assignment_digest")
    ):
        findings.append(diagnostic(
            "application_assignment_binding_invalid",
            "Aggregate evidence requires assignment identity and digest.",
            aggregate_relative,
        ))
    references = aggregate.get("receipts")
    if not isinstance(references, list):
        findings.append(diagnostic(
            "application_evidence_schema_invalid",
            "Aggregate receipts must be an ordered array.",
            aggregate_relative,
        ))
        references = []
    sequence = _transaction_application_sequence(transaction, findings)
    if len(references) != len(sequence):
        findings.append(diagnostic(
            "application_receipt_cardinality_mismatch",
            "Every applied patch requires exactly one receipt and no extra receipts.",
            aggregate_relative,
        ))
    applied_owners = [
        str(patch.get("owner")) for patch, _result in sequence
        if patch.get("owner") in OWNERS
    ]
    keys = _load_owner_keys(
        owners=applied_owners,
        owner_keys=owner_keys,
        owner_key_digests=owner_key_digests,
        root=root,
        evidence_root=evidence_root,
        findings=findings,
    )
    try:
        expected_evidence_root_digest = evidence_root_digest(evidence_root)
    except (OSError, RuntimeError, ValueError) as error:
        findings.append(diagnostic(
            "application_evidence_context_invalid", str(error), "--evidence-root",
        ))
        expected_evidence_root_digest = None
    verified = []
    seen_paths = set()
    seen_patch_ids = set()
    seen_nonces = set()
    prior_digest = ABSENT_DIGEST
    package_identities: Dict[str, Tuple[str, str]] = {}
    for index, reference in enumerate(references):
        ref_path = "%s.receipts[%d]" % (aggregate_relative, index)
        if not isinstance(reference, Mapping) or set(reference) != EVIDENCE_REFERENCE_FIELDS:
            findings.append(diagnostic(
                "application_receipt_reference_invalid",
                "Receipt reference must contain exactly path and digest.",
                ref_path,
            ))
            continue
        relative = normalize_evidence_path(reference.get("path"))
        recorded_digest = reference.get("digest")
        if relative is None or not _is_digest(recorded_digest):
            findings.append(diagnostic(
                "application_receipt_reference_invalid",
                "Receipt requires a normalized path and SHA-256 digest.",
                ref_path,
            ))
            continue
        if relative in seen_paths:
            findings.append(diagnostic(
                "application_receipt_duplicate",
                "Receipt paths must be unique.",
                ref_path,
            ))
        seen_paths.add(relative)
        try:
            raw = _read_relative_single_link(evidence_root, relative)
        except (OSError, RuntimeError, ValueError) as error:
            findings.append(diagnostic(
                "application_receipt_unreadable", str(error), ref_path,
            ))
            continue
        raw_digest = digest_bytes(raw)
        if raw_digest != recorded_digest:
            findings.append(diagnostic(
                "application_receipt_digest_mismatch",
                "Receipt raw bytes do not match the aggregate digest.",
                ref_path,
            ))
        try:
            envelope = _load_canonical_json(raw)
        except (UnicodeError, ValueError, json.JSONDecodeError) as error:
            code = (
                "application_receipt_noncanonical"
                if str(error) == "JSON bytes are not canonical"
                else "application_receipt_invalid"
            )
            findings.append(diagnostic(code, str(error), ref_path))
            prior_digest = raw_digest
            continue
        if not isinstance(envelope, Mapping) or set(envelope) != ENVELOPE_FIELDS:
            findings.append(diagnostic(
                "application_receipt_schema_invalid",
                "Owner receipt does not match the exact envelope schema.",
                ref_path,
            ))
            prior_digest = raw_digest
            continue
        subject = envelope.get("subject")
        receipt = envelope.get("receipt")
        if (
            type(envelope.get("schema_version")) is not int
            or envelope.get("schema_version") != 1
            or envelope.get("producer") != PRODUCER
            or envelope.get("status") != "applied"
            or not isinstance(subject, Mapping)
            or set(subject) != SUBJECT_FIELDS
            or not isinstance(receipt, Mapping)
            or set(receipt) != RECEIPT_FIELDS
        ):
            findings.append(diagnostic(
                "application_receipt_schema_invalid",
                "Owner receipt envelope fields or fixed identities are invalid.",
                ref_path,
            ))
            prior_digest = raw_digest
            continue
        owner = subject.get("owner")
        expected_item = sequence[index] if index < len(sequence) else None
        expected_patch = expected_item[0] if expected_item is not None else None
        expected_result = expected_item[1] if expected_item is not None else None
        patch_receipt = receipt.get("patch_receipt")
        if (
            type(receipt.get("schema_version")) is not int
            or receipt.get("schema_version") != 1
            or receipt.get("trust_model") != TRUST_MODEL
            or receipt.get("command_id") != COMMAND_ID
            or not isinstance(patch_receipt, Mapping)
            or set(patch_receipt) != PATCH_RECEIPT_FIELDS
        ):
            findings.append(diagnostic(
                "application_receipt_schema_invalid",
                "Owner receipt body does not match exact schema v1.",
                ref_path,
            ))
            prior_digest = raw_digest
            continue
        patch = patch_receipt.get("patch")
        patch_id = patch.get("patch_id") if isinstance(patch, Mapping) else None
        if not isinstance(patch, Mapping) or set(patch) != PATCH_FIELDS:
            findings.append(diagnostic(
                "application_receipt_patch_mismatch",
                "Receipt patch is not the exact transaction-v2 patch projection.",
                ref_path,
            ))
        if patch_id in seen_patch_ids:
            findings.append(diagnostic(
                "application_receipt_duplicate",
                "A patch may have only one application receipt.",
                ref_path,
            ))
        seen_patch_ids.add(patch_id)
        if expected_patch is None or patch != expected_patch:
            findings.append(diagnostic(
                "application_receipt_order_mismatch",
                "Receipt order and patch must equal applied-result order.",
                ref_path,
            ))
        expected_resulting = (
            expected_result.get("resulting_digest")
            if isinstance(expected_result, Mapping) else None
        )
        planned_resulting = (
            expected_patch.get("expected_after_digest")
            if isinstance(expected_patch, Mapping) else None
        )
        receipt_resulting = patch_receipt.get("resulting_digest")
        if (
            patch_receipt.get("result") != "applied"
            or not _is_digest(receipt_resulting)
            or receipt_resulting != planned_resulting
            or receipt_resulting != expected_resulting
        ):
            findings.append(diagnostic(
                "application_receipt_result_mismatch",
                "Planned, applied-result, and signed receipt digests must be equal.",
                ref_path,
            ))
        expected_subject = {
            "transaction_id": transaction.get("transaction_id"),
            "transaction_digest": expected_plan_digest,
            "assignment_id": aggregate.get("assignment_id"),
            "assignment_digest": aggregate.get("assignment_digest"),
            "repository_root_digest": expected_root_digest,
            "owner": expected_patch.get("owner")
            if isinstance(expected_patch, Mapping) else None,
        }
        if any(subject.get(field) != value for field, value in expected_subject.items()):
            findings.append(diagnostic(
                "application_receipt_subject_mismatch",
                "Receipt subject does not match transaction, assignment, root, or owner.",
                ref_path,
            ))
        for field in (
            "phase_baseline_snapshot_digest",
            "phase_parent_evidence_digest",
            "scope_digest",
        ):
            if not _is_digest(subject.get(field)):
                findings.append(diagnostic(
                    "application_receipt_subject_invalid",
                    "Signed receipt subject digest is invalid: %s" % field,
                    ref_path,
                ))
        if not _has_text(subject.get("phase_id")) or owner not in OWNERS:
            findings.append(diagnostic(
                "application_receipt_subject_invalid",
                "Receipt phase and owner identities are invalid.",
                ref_path,
            ))
        if receipt.get("evidence_root_digest") != expected_evidence_root_digest:
            findings.append(diagnostic(
                "application_receipt_evidence_root_mismatch",
                "Receipt belongs to a different evidence root.",
                ref_path,
            ))
        if not _is_digest(receipt.get("request_digest")):
            findings.append(diagnostic(
                "application_receipt_request_invalid",
                "Receipt request digest must be canonical SHA-256.",
                ref_path,
            ))
        if receipt.get("prior_receipt_digest") != prior_digest:
            findings.append(diagnostic(
                "application_receipt_chain_mismatch",
                "Receipt does not continue the raw receipt digest chain.",
                ref_path,
            ))
        nonce = receipt.get("nonce")
        if not isinstance(nonce, str) or NONCE_PATTERN.fullmatch(nonce) is None:
            findings.append(diagnostic(
                "application_receipt_nonce_invalid", "Receipt nonce is invalid.", ref_path,
            ))
        elif nonce in seen_nonces:
            findings.append(diagnostic(
                "application_receipt_nonce_reused", "Receipt nonce is reused.", ref_path,
            ))
        else:
            seen_nonces.add(nonce)
        if owner in OWNERS:
            lane = "author" if owner == "author" else "repository_owner"
            if lane not in package_identities:
                try:
                    package_identities[lane] = _package_identity(str(owner))
                except (OSError, RuntimeError, ValueError) as error:
                    findings.append(diagnostic(
                        "application_receipt_package_unavailable", str(error), ref_path,
                    ))
            identity = package_identities.get(lane)
            if identity is not None:
                if receipt.get("runner_executable_digest") != identity[0]:
                    findings.append(diagnostic(
                        "application_receipt_runner_mismatch",
                        "Receipt is not bound to the current package runner bytes.",
                        ref_path,
                    ))
                if receipt.get("runtime_digest") != identity[1]:
                    findings.append(diagnostic(
                        "application_receipt_runtime_mismatch",
                        "Receipt is not bound to the current generated runtime bytes.",
                        ref_path,
                    ))
            pinned = owner_key_digests.get(str(owner))
            if receipt.get("authority_key_fingerprint") != pinned:
                findings.append(diagnostic(
                    "application_receipt_key_mismatch",
                    "Receipt is not bound to the externally pinned owner key.",
                    ref_path,
                ))
            mac = receipt.get("mac")
            key = keys.get(str(owner))
            if not isinstance(mac, str) or HMAC_PATTERN.fullmatch(mac) is None:
                findings.append(diagnostic(
                    "application_receipt_mac_invalid", "Receipt MAC is invalid.", ref_path,
                ))
            elif key is not None and not hmac.compare_digest(
                mac, _receipt_mac(key, envelope, receipt)
            ):
                findings.append(diagnostic(
                    "application_receipt_mac_invalid",
                    "Receipt MAC does not authenticate the exact envelope.",
                    ref_path,
                ))
        target_path = (
            expected_patch.get("target_path")
            if isinstance(expected_patch, Mapping) else None
        )
        normalized_target = normalize_evidence_path(target_path)
        if normalized_target is None:
            findings.append(diagnostic(
                "application_receipt_current_mismatch",
                "Applied patch target path is invalid.",
                ref_path,
            ))
        else:
            try:
                current = _read_relative_single_link(root, normalized_target)
            except (OSError, RuntimeError, ValueError) as error:
                findings.append(diagnostic(
                    "application_receipt_current_mismatch", str(error), ref_path,
                ))
            else:
                if digest_bytes(current) != receipt_resulting:
                    findings.append(diagnostic(
                        "application_receipt_current_mismatch",
                        "Current target bytes differ from the signed applied result.",
                        ref_path,
                    ))
        verified.append(VerifiedApplicationReceipt(
            path=relative,
            digest=raw_digest,
            raw_bytes=raw,
            envelope=envelope,
            patch_id=str(patch_id or ""),
            owner=str(owner or ""),
            phase_id=str(subject.get("phase_id") or ""),
        ))
        prior_digest = raw_digest
    evidence = None
    if not findings:
        evidence = VerifiedApplicationEvidence(
            aggregate=aggregate,
            raw_bytes=aggregate_raw,
            receipts=tuple(verified),
        )
    return ApplicationEvidenceValidationResult(tuple(findings), evidence)
