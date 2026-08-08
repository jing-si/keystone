"""Surface patch, attestation, and application evidence validation."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, FrozenSet, Optional, Sequence, Tuple

from .model import (
    Diagnostic,
    PatchOwner,
    PatchSurface,
    patch_owner_matches_surface,
    patch_source_identity,
)
from .patch_replay import PATCH_FORMATS, digest_bytes, replay_patch
from .transaction_wire_validation import is_digest_wire
from .validation_support import canonical_relative_path, diagnostic, safe_path


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
    actual_state_root_available: bool = False


@dataclass(frozen=True)
class EvidenceValidationResult:
    diagnostics: Tuple[Diagnostic, ...]
    evidence: Optional[TransactionEvidence]


def _mutation_surfaces(
    value: Any,
) -> Tuple[Tuple[Optional[str], Optional[str]], ...]:
    if not isinstance(value, dict):
        return ()
    surfaces = []
    for entity in (value.get("before"), value.get("after")):
        if not isinstance(entity, dict):
            continue
        provenance = entity.get("provenance")
        surface = (
            provenance.get("surface") if isinstance(provenance, dict) else None
        )
        if value.get("entity") == "node":
            locator = entity.get("locator")
        else:
            locator = (
                provenance.get("locator") if isinstance(provenance, dict) else None
            )
        path = locator.get("path") if isinstance(locator, dict) else None
        candidate = path, surface
        if candidate not in surfaces:
            surfaces.append(candidate)
    return tuple(surfaces)


def _patch_links_surface(surface: Any, patch: Any) -> bool:
    if not isinstance(patch, dict):
        return False
    try:
        patch_surface = PatchSurface(patch.get("surface"))
    except (TypeError, ValueError):
        return False
    path, expected_surface = surface
    source_identity = patch_source_identity(
        patch_surface, patch.get("target_path")
    )
    return bool(
        path
        and source_identity == path
        and (
            expected_surface is None
            or patch.get("surface") == expected_surface
        )
    )


def _patch_links_mutation(mutation: Any, patch: Any) -> bool:
    return any(
        _patch_links_surface(surface, patch)
        for surface in _mutation_surfaces(mutation)
    )


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
    patch_by_target = {}
    schema_version = value.get("schema_version")
    for patch in patches:
        if not isinstance(patch, dict):
            findings.append(diagnostic("surface_patch_invalid", "surface patch must be an object"))
            continue
        patch_fields = {
            "patch_id", "owner", "surface", "target_path", "baseline_digest",
            "exact_patch", "required",
        }
        if schema_version == 2:
            patch_fields |= {
                "patch_format", "patch_body", "expected_after_digest",
                "baseline_content",
            }
        for field in sorted(set(patch) - patch_fields):
            findings.append(diagnostic(
                "surface_patch_unknown_field",
                "unknown surface patch field: %s" % field,
            ))
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
        physical_target = None
        if isinstance(patch.get("target_path"), str) and patch["target_path"]:
            try:
                physical_target = canonical_relative_path(patch["target_path"])
                if root is not None:
                    physical_target = str(safe_path(root, patch["target_path"]))
            except ValueError as error:
                findings.append(diagnostic(
                    "patch_target_invalid", str(error), patch["target_path"]
                ))
        target_path = patch.get("target_path")
        if physical_target is not None:
            if physical_target in patch_by_target:
                findings.append(diagnostic(
                    "patch_target_duplicate",
                    "physical patch target is duplicated: %s" % target_path,
                    target_path,
                ))
            else:
                patch_by_target[physical_target] = patch
        if not isinstance(patch.get("exact_patch"), str) or not patch["exact_patch"]:
            findings.append(diagnostic(
                "patch_exact_patch_invalid",
                "surface patch exact_patch must be non-empty",
            ))
        if schema_version == 2:
            patch_format = patch.get("patch_format")
            patch_body = patch.get("patch_body")
            expected_digest = patch.get("expected_after_digest")
            baseline_content = patch.get("baseline_content")
            if "baseline_content" not in patch:
                findings.append(diagnostic(
                    "patch_baseline_content_invalid",
                    "schema-v2 surface patch requires baseline_content",
                ))
            if patch_format not in PATCH_FORMATS:
                findings.append(diagnostic(
                    "patch_format_invalid",
                    "schema-v2 surface patch requires a supported patch_format",
                ))
            if not isinstance(patch_body, str):
                findings.append(diagnostic(
                    "patch_body_invalid",
                    "schema-v2 surface patch requires patch_body",
                ))
            elif patch.get("exact_patch") != patch_body:
                findings.append(diagnostic(
                    "patch_body_alias_mismatch",
                    "exact_patch must equal patch_body in schema-v2 compatibility wire",
                ))
            if not is_digest_wire(expected_digest or "") or expected_digest == "absent":
                findings.append(diagnostic(
                    "patch_expected_digest_invalid",
                    "schema-v2 surface patch requires an expected sha256 digest",
                ))
            baseline_digest = patch.get("baseline_digest")
            if baseline_digest == "absent":
                if baseline_content is not None:
                    findings.append(diagnostic(
                        "patch_baseline_content_invalid",
                        "absent baseline requires null baseline_content",
                    ))
                baseline = b""
            elif not isinstance(baseline_content, str):
                findings.append(diagnostic(
                    "patch_baseline_content_invalid",
                    "schema-v2 surface patch requires baseline_content",
                ))
                baseline = None
            else:
                baseline = baseline_content.encode("utf-8")
                if digest_bytes(baseline) != baseline_digest:
                    findings.append(diagnostic(
                        "patch_baseline_content_mismatch",
                        "baseline_content does not produce baseline_digest",
                        patch.get("target_path"),
                    ))
            if (
                baseline is not None
                and patch_format in PATCH_FORMATS
                and isinstance(patch_body, str)
                and is_digest_wire(expected_digest or "")
                and expected_digest != "absent"
            ):
                try:
                    replayed = replay_patch(baseline, patch_format, patch_body)
                except ValueError as error:
                    findings.append(diagnostic(
                        "patch_replay_invalid", str(error), patch.get("target_path")
                    ))
                else:
                    if digest_bytes(replayed) != expected_digest:
                        findings.append(diagnostic(
                            "patch_replay_mismatch",
                            "patch replay does not produce expected_after_digest",
                            patch.get("target_path"),
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
    if schema_version == 2:
        relevant_deltas = {
            delta.get("source_surface"): delta
            for delta in value.get("input_deltas", [])
            if isinstance(delta, dict) and delta.get("graph_relevant") is True
        }
        for patch in patch_by_id.values():
            delta = relevant_deltas.get(patch.get("target_path"))
            if delta is None:
                findings.append(diagnostic(
                    "patch_input_delta_missing",
                    "schema-v2 patch requires a graph-relevant input delta",
                    patch.get("target_path"),
                ))
            elif delta.get("baseline_digest") != patch.get("baseline_digest"):
                findings.append(diagnostic(
                    "patch_delta_baseline_mismatch",
                    "schema-v2 patch baseline differs from its input delta",
                    patch.get("target_path"),
                ))
        for index, mutation in enumerate(mutations):
            for surface in _mutation_surfaces(mutation):
                linked = tuple(
                    patch for patch in patch_by_id.values()
                    if _patch_links_surface(surface, patch)
                )
                if any(patch.get("required") is False for patch in linked):
                    findings.append(diagnostic(
                        "mutation_optional_patch_forbidden",
                        "schema-v2 mutation %d surface has an optional patch" % index,
                    ))
                if not any(patch.get("required") is True for patch in linked):
                    findings.append(diagnostic(
                        "mutation_required_patch_missing",
                        "schema-v2 mutation %d surface lacks a required owning patch"
                        % index,
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
        elif (
            item.get("result") == "applied"
            and schema_version == 2
            and resulting_digest != patch.get("expected_after_digest")
        ):
            findings.append(diagnostic(
                "resulting_digest_expected_mismatch",
                "applied resulting_digest does not match expected_after_digest",
                patch.get("target_path"),
            ))
        if (
            item.get("result") == "applied"
            and is_digest_wire(resulting_digest or "")
            and root is not None
        ):
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

    if schema_version == 2:
        for patch_id in sorted(applied - confirmed):
            findings.append(diagnostic(
                "applied_patch_confirmation_missing",
                "applied patch lacks owner confirmation: %s" % patch_id,
            ))

    if schema_version == 2:
        if root is None:
            for patch_id in sorted(applied):
                findings.append(diagnostic(
                    "actual_state_unverified",
                    "applied patch requires repository actual-state validation: %s"
                    % patch_id,
                ))
        else:
            for patch_id, patch in sorted(patch_by_id.items()):
                if patch_id in applied:
                    continue
                if (
                    patch.get("required") is False
                    and (
                        value.get("state") == "verified"
                        or patch_id not in confirmed
                    )
                ):
                    continue
                try:
                    target = safe_path(root, patch.get("target_path"))
                except ValueError:
                    continue
                actual = (
                    "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
                    if target.is_file()
                    else "absent"
                )
                if actual != patch.get("baseline_digest"):
                    findings.append(diagnostic(
                        "unapplied_patch_baseline_mismatch",
                        "unapplied patch source no longer matches its baseline",
                        patch.get("target_path"),
                    ))

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
            actual_state_root_available=root is not None,
        ),
    )
