"""Surface patch, attestation, and application evidence validation."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, FrozenSet, Optional, Sequence, Tuple

from .model import Diagnostic, PatchOwner, PatchSurface, patch_owner_matches_surface
from .transaction_wire_validation import is_digest_wire
from .validation_support import diagnostic, safe_path


@dataclass(frozen=True)
class TransactionEvidence:
    patches: Tuple[Any, ...]
    attestations: Tuple[Any, ...]
    results: Tuple[Any, ...]
    required_patch_ids: FrozenSet[str]
    confirmed_patch_ids: FrozenSet[str]
    rejected_patch_ids: FrozenSet[str]
    revision_patch_ids: FrozenSet[str]
    applied_patch_ids: FrozenSet[str]
    stale_baseline_patch_ids: FrozenSet[str]
    failed_patch_ids: FrozenSet[str]


@dataclass(frozen=True)
class EvidenceValidationResult:
    diagnostics: Tuple[Diagnostic, ...]
    evidence: Optional[TransactionEvidence]


def validate_transaction_evidence(
    value: Any,
    root: Optional[Path],
    mutations: Sequence[Any],
) -> EvidenceValidationResult:
    findings = []
    patches = value.get("surface_patches", [])
    attestations = value.get("attestations", [])
    results = value.get("apply_results", [])
    if not all(isinstance(items, list) for items in (patches, attestations, results)):
        return EvidenceValidationResult(
            diagnostics=(diagnostic(
                "transaction_collection_invalid",
                "patch, attestation, and result fields must be arrays",
            ),),
            evidence=None,
        )

    patch_by_id = {}
    for patch in patches:
        if not isinstance(patch, dict):
            findings.append(diagnostic("surface_patch_invalid", "surface patch must be an object"))
            continue
        patch_id = patch.get("patch_id")
        if not isinstance(patch_id, str) or not patch_id:
            findings.append(diagnostic("patch_id_missing", "surface patch requires patch_id"))
        elif patch_id in patch_by_id:
            findings.append(diagnostic(
                "patch_id_duplicate",
                "surface patch ID is duplicated: %s" % patch_id,
            ))
        else:
            patch_by_id[patch_id] = patch
        if patch.get("owner") not in {"author", "main", "coordinator"}:
            findings.append(diagnostic("patch_owner_invalid", "surface patch owner is invalid"))
        if patch.get("surface") not in {
            "document_metadata", "code_anchor", "config_anchor", "schema_anchor",
            "api_anchor", "test_anchor", "companion_metadata",
        }:
            findings.append(diagnostic("patch_surface_invalid", "surface patch surface is invalid"))
        elif (
            patch.get("owner") in {"author", "main", "coordinator"}
            and not patch_owner_matches_surface(
                PatchOwner(patch["owner"]),
                PatchSurface(patch["surface"]),
                patch.get("target_path"),
            )
        ):
            findings.append(diagnostic(
                "patch_owner_surface_invalid",
                "patch owner does not own the described surface",
            ))
        if not isinstance(patch.get("target_path"), str) or not patch["target_path"]:
            findings.append(diagnostic(
                "patch_target_missing",
                "surface patch target_path is required",
            ))
        elif root is not None:
            try:
                safe_path(root, patch["target_path"])
            except ValueError as error:
                findings.append(diagnostic(
                    "patch_target_invalid", str(error), patch["target_path"]
                ))
        if not isinstance(patch.get("exact_patch"), str) or not patch["exact_patch"]:
            findings.append(diagnostic(
                "patch_exact_patch_invalid",
                "surface patch exact_patch must be non-empty",
            ))
        if not isinstance(patch.get("required"), bool):
            findings.append(diagnostic(
                "patch_required_invalid",
                "surface patch required must be boolean",
            ))
        if not is_digest_wire(patch.get("baseline_digest", "")):
            findings.append(diagnostic(
                "patch_baseline_invalid", "patch baseline_digest is invalid"
            ))

    required = {
        patch_id for patch_id, patch in patch_by_id.items()
        if patch.get("required") is True
    }
    if mutations and not required:
        findings.append(diagnostic(
            "graph_change_required_patch_missing",
            "graph-changing transaction requires at least one required patch",
        ))

    confirmed = set()
    rejected = set()
    needs_revision = set()
    seen_attestations = set()
    for item in attestations:
        if not isinstance(item, dict):
            findings.append(diagnostic("attestation_invalid", "attestation must be an object"))
            continue
        shape_valid = (
            set(item) == {"patch_id", "owner", "decision", "evidence"}
            and isinstance(item.get("patch_id"), str)
            and bool(item["patch_id"])
            and item.get("owner") in {"author", "main", "coordinator"}
            and item.get("decision") in {"confirm", "reject", "needs_revision"}
            and isinstance(item.get("evidence"), str)
            and bool(item["evidence"].strip())
        )
        if not shape_valid:
            findings.append(diagnostic(
                "attestation_invalid", "attestation does not match canonical wire"
            ))
        attestation_key = item.get("patch_id")
        if attestation_key in seen_attestations:
            findings.append(diagnostic("attestation_duplicate", "patch has duplicate attestations"))
        seen_attestations.add(attestation_key)
        patch = patch_by_id.get(item.get("patch_id"))
        if patch is None:
            findings.append(diagnostic(
                "attestation_patch_unknown",
                "attestation references an unknown patch",
            ))
        elif item.get("owner") != patch.get("owner"):
            findings.append(diagnostic(
                "attestation_owner_mismatch",
                "attestation owner does not own patch",
            ))
        if item.get("decision") not in {"confirm", "reject", "needs_revision"}:
            findings.append(diagnostic(
                "attestation_decision_invalid", "attestation decision is invalid"
            ))
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
            findings.append(diagnostic(
                "attestation_evidence_missing", "attestation evidence is required"
            ))
        if shape_valid and patch is not None and item["owner"] == patch.get("owner"):
            {
                "confirm": confirmed,
                "reject": rejected,
                "needs_revision": needs_revision,
            }[item["decision"]].add(item["patch_id"])

    applied = set()
    stale_baselines = set()
    failed_results = set()
    seen_results = set()
    for item in results:
        if not isinstance(item, dict):
            findings.append(diagnostic("apply_result_invalid", "apply result must be an object"))
            continue
        shape_valid = (
            set(item) == {"patch_id", "result", "resulting_digest", "evidence"}
            and isinstance(item.get("patch_id"), str)
            and bool(item["patch_id"])
            and item.get("result") in {"applied", "failed", "stale_baseline"}
            and (
                item.get("resulting_digest") is None
                or isinstance(item.get("resulting_digest"), str)
            )
            and isinstance(item.get("evidence"), str)
            and bool(item["evidence"].strip())
        )
        if not shape_valid:
            findings.append(diagnostic(
                "application_result_invalid",
                "application result does not match canonical wire",
            ))
        result_key = item.get("patch_id")
        if result_key in seen_results:
            findings.append(diagnostic(
                "apply_result_duplicate", "patch has duplicate application results"
            ))
        seen_results.add(result_key)
        patch = patch_by_id.get(item.get("patch_id"))
        if patch is None:
            findings.append(diagnostic(
                "apply_result_patch_unknown",
                "apply result references an unknown patch",
            ))
            continue
        if item.get("result") not in {"applied", "failed", "stale_baseline"}:
            findings.append(diagnostic(
                "application_status_invalid", "application result status is invalid"
            ))
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
            findings.append(diagnostic(
                "application_evidence_missing",
                "application result evidence is required",
            ))
        resulting_digest = item.get("resulting_digest")
        if item.get("result") == "applied" and not is_digest_wire(resulting_digest or ""):
            findings.append(diagnostic(
                "resulting_digest_invalid",
                "applied result requires a sha256 digest",
            ))
        elif item.get("result") == "applied" and root is not None:
            try:
                target = safe_path(root, patch.get("target_path"))
            except ValueError as error:
                findings.append(diagnostic(
                    "patch_target_invalid", str(error), patch.get("target_path")
                ))
            else:
                actual = (
                    "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
                    if target.is_file()
                    else "absent"
                )
                if resulting_digest != actual:
                    findings.append(diagnostic(
                        "resulting_digest_mismatch",
                        "resulting digest does not match current source bytes",
                        patch.get("target_path"),
                    ))
        if shape_valid:
            {
                "applied": applied,
                "stale_baseline": stale_baselines,
                "failed": failed_results,
            }[item["result"]].add(item["patch_id"])

    return EvidenceValidationResult(
        diagnostics=tuple(findings),
        evidence=TransactionEvidence(
            patches=tuple(patches),
            attestations=tuple(attestations),
            results=tuple(results),
            required_patch_ids=frozenset(required),
            confirmed_patch_ids=frozenset(confirmed),
            rejected_patch_ids=frozenset(rejected),
            revision_patch_ids=frozenset(needs_revision),
            applied_patch_ids=frozenset(applied),
            stale_baseline_patch_ids=frozenset(stale_baselines),
            failed_patch_ids=frozenset(failed_results),
        ),
    )
