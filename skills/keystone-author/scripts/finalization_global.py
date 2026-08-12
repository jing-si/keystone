"""Structured repository-global finalization state validation."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from finalization_support import (
    diagnostic,
    frontmatter_mapping_list,
    frontmatter_mapping_scalar,
    read_scoped_file,
    resolve_scoped_path,
    scalar_from_text,
)


GLOBAL_SOURCE_CATEGORIES = {
    "work_index", "round_index", "root_index", "context_map",
}
ROUND_PATTERN = re.compile(r"^R\d+$")
STEP_PATTERN = re.compile(r"^(R\d+)/S\d+(?:-[A-Z0-9]+)*$")
ACTIVE_STEP_PATTERN = re.compile(
    r"^(R\d+)(?:-[a-z])?/S\d+(?:-[A-Z0-9]+)*$"
)
ACTIVE_WORK_STATUSES = {"planned", "in_progress", "blocked"}
V5_SOURCE_TYPES = {
    "work_index": ("work", "event_round"),
    "round_index": ("work_round", "event_round"),
    "root_index": ("work_round_index", "global"),
    "context_map": ("context_map", "global"),
}


def validate_global_state(root: Path, manifest: Dict[str, Any],
                          schema_version: Any) -> List[Dict[str, str]]:
    """Validate current global state against four distinct typed sources."""
    if schema_version not in {4, 5, 6}:
        return []
    findings: List[Dict[str, str]] = []
    state = manifest.get("global_state")
    if not isinstance(state, dict):
        return [diagnostic(
            "global_state_missing",
            "schema_version 4, 5, or 6 requires structured global_state.",
        )]

    state_schema_version = state.get("schema_version", 1)
    if type(state_schema_version) is not int or state_schema_version not in {1, 2}:
        findings.append(diagnostic(
            "global_state_schema_version_invalid",
            "global_state.schema_version must be 1 or 2.",
        ))
        state_schema_version = 1
    if state_schema_version == 2 and schema_version != 6:
        findings.append(diagnostic(
            "global_state_schema_version_unsupported",
            "global_state schema_version 2 requires finalization schema_version 6.",
        ))

    active_round = state.get("active_round")
    active_rounds: List[str] = []
    latest_accepted = state.get("latest_accepted_round")
    active_steps = state.get("active_steps")
    if state_schema_version == 2:
        raw_active_rounds = state.get("active_rounds")
        active_rounds_valid = (
            isinstance(raw_active_rounds, list)
            and all(
                isinstance(ref, str) and bool(ROUND_PATTERN.fullmatch(ref))
                for ref in raw_active_rounds
            )
            and raw_active_rounds == sorted(set(raw_active_rounds))
        )
        if not active_rounds_valid:
            findings.append(diagnostic(
                "global_state_active_rounds_invalid",
                "global_state.active_rounds must be a sorted unique array of Round refs.",
            ))
        else:
            active_rounds = raw_active_rounds
    else:
        active_round_valid = (
            isinstance(active_round, str)
            and (bool(ROUND_PATTERN.fullmatch(active_round)) or active_round == "none")
        )
        if not active_round_valid:
            findings.append(diagnostic(
                "global_state_active_round_invalid",
                "global_state.active_round must be a Round ref or none.",
            ))
        elif active_round != "none":
            active_rounds = [active_round]
    if (not isinstance(latest_accepted, str)
            or not ROUND_PATTERN.fullmatch(latest_accepted)):
        findings.append(diagnostic(
            "global_state_latest_accepted_round_invalid",
            "global_state.latest_accepted_round must be a Round ref.",
        ))
    if (not isinstance(active_steps, list)
            or not all(isinstance(ref, str) for ref in active_steps)):
        findings.append(diagnostic(
            "global_state_active_steps_invalid",
            "global_state.active_steps must be an array of Step refs.",
        ))
        active_steps = []
    if active_steps != manifest.get("active_steps"):
        findings.append(diagnostic(
            "global_state_active_steps_mismatch",
            "global_state.active_steps differs from manifest active_steps.",
        ))
    if not active_rounds and active_steps:
        findings.append(diagnostic(
            "global_state_active_round_mismatch",
            "Global state may have no active Rounds only when active_steps is empty.",
        ))
    if schema_version in {5, 6}:
        for ref in active_steps:
            match = ACTIVE_STEP_PATTERN.fullmatch(ref)
            if match is None:
                findings.append(diagnostic(
                    "active_step_ref_invalid",
                    f"Active Step ref is not canonical: {ref}.",
                ))
            elif match.group(1) not in active_rounds:
                findings.append(diagnostic(
                    "active_step_round_mismatch",
                    f"Active Step {ref} is outside active Rounds {active_rounds}.",
                ))
        event_round = _v5_event_round(manifest, findings)
        event_is_active = event_round in active_rounds
        if not event_is_active:
            if event_round is not None and latest_accepted != event_round:
                findings.append(diagnostic(
                    "latest_accepted_round_event_mismatch",
                    "Finalization of an inactive event Round must make it latest accepted.",
                ))
    else:
        event_round = None
        event_is_active = False

    sources = state.get("sources")
    if not isinstance(sources, list):
        findings.append(diagnostic(
            "global_state_sources_invalid",
            "global_state.sources must be an array.",
        ))
        return findings

    seen_categories = set()
    seen_paths = set()
    root_index_path: Optional[Path] = None
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            findings.append(diagnostic(
                "global_state_source_invalid",
                f"global_state.sources[{index}] must be an object.",
            ))
            continue
        category = source.get("category")
        if category not in GLOBAL_SOURCE_CATEGORIES:
            findings.append(diagnostic(
                "global_state_source_category_invalid",
                f"global_state.sources[{index}] has an invalid category.",
            ))
        elif category in seen_categories:
            findings.append(diagnostic(
                "global_state_source_category_duplicate",
                f"Global-state source category is duplicated: {category}.",
            ))
        else:
            seen_categories.add(category)

        resolved, path_error = resolve_scoped_path(root, source.get("path"))
        if path_error:
            findings.append(diagnostic(
                "global_state_source_unavailable",
                f"Cannot resolve global-state source: {path_error}.",
                str(source.get("path")),
            ))
            continue
        normalized = str(resolved)
        if normalized in seen_paths:
            findings.append(diagnostic(
                "global_state_source_path_duplicate",
                "Each global-state category requires a distinct source path.",
                str(source.get("path")),
            ))
        else:
            seen_paths.add(normalized)
        resolved_relative = resolved.relative_to(root.resolve()).as_posix()

        content, error, source_path = read_scoped_file(root, source.get("path"))
        if error:
            findings.append(diagnostic(
                "global_state_source_unavailable",
                f"Cannot read global-state source: {error}.",
                str(source.get("path")),
            ))
            continue
        text = content or ""
        expected_key = source.get("key_id")
        actual_key = frontmatter_mapping_scalar(text, "key", "id")
        if (not isinstance(expected_key, str) or not expected_key.strip()
                or actual_key != expected_key):
            findings.append(diagnostic(
                "global_state_source_key_mismatch",
                f"Global-state source key {actual_key} differs from {expected_key}.",
                source_path,
            ))
        if schema_version in {5, 6} and category in V5_SOURCE_TYPES:
            expected_doc_type, expected_round_role = V5_SOURCE_TYPES[category]
            actual_doc_type = scalar_from_text(text, "doc_type")
            if actual_doc_type != expected_doc_type:
                findings.append(diagnostic(
                    "global_state_source_doc_type_mismatch",
                    f"{category} requires doc_type {expected_doc_type}, not "
                    f"{actual_doc_type}.",
                    source_path,
                ))
            if not _v5_path_matches_round(
                    resolved_relative, expected_round_role, event_round):
                findings.append(diagnostic(
                    "global_state_source_round_role_invalid",
                    f"{category} path does not satisfy round_role "
                    f"{expected_round_role} for {event_round}.",
                    source_path,
                ))
            if not _v5_key_matches_category(category, actual_key, event_round):
                findings.append(diagnostic(
                    "global_state_source_key_semantics_invalid",
                    f"Key {actual_key} does not identify category {category} "
                    f"for Round {event_round}.",
                    source_path,
                ))
            if (category == "root_index"
                    and actual_doc_type == "work_round_index"
                    and actual_key == "key.work.index"):
                root_index_path = resolved
            if category == "round_index":
                expected_status = (
                    "active" if event_is_active else "accepted"
                )
                actual_status = scalar_from_text(text, "round_status")
                if actual_status != expected_status:
                    findings.append(diagnostic(
                        "round_status_semantics_invalid",
                        f"Event Round requires round_status {expected_status}, not "
                        f"{actual_status}.",
                        source_path,
                    ))
            if category == "work_index" and not event_is_active:
                actual_status = scalar_from_text(text, "work_status")
                if actual_status != "complete":
                    findings.append(diagnostic(
                        "terminal_work_status_invalid",
                        "An inactive event Round requires the event Work to be complete.",
                        source_path,
                    ))
        if state_schema_version == 2:
            observed = {
                "schema_version": frontmatter_mapping_scalar(
                    text, "global_state", "schema_version"
                ),
                "active_rounds": frontmatter_mapping_list(
                    text, "global_state", "active_rounds"
                ),
                "latest_accepted_round": frontmatter_mapping_scalar(
                    text, "global_state", "latest_accepted_round"
                ),
                "active_steps": frontmatter_mapping_list(
                    text, "global_state", "active_steps"
                ),
            }
            expected = {
                "schema_version": "2",
                "active_rounds": active_rounds,
                "latest_accepted_round": latest_accepted,
                "active_steps": active_steps,
            }
        else:
            observed = {
                "active_round": frontmatter_mapping_scalar(
                    text, "global_state", "active_round"
                ),
                "latest_accepted_round": frontmatter_mapping_scalar(
                    text, "global_state", "latest_accepted_round"
                ),
                "active_steps": frontmatter_mapping_list(
                    text, "global_state", "active_steps"
                ),
            }
            expected = {
                "active_round": active_round,
                "latest_accepted_round": latest_accepted,
                "active_steps": active_steps,
            }
        if observed != expected:
            findings.append(diagnostic(
                "global_state_source_mismatch",
                f"Global-state source {observed} differs from manifest {expected}.",
                source_path,
            ))

    for missing in sorted(GLOBAL_SOURCE_CATEGORIES - seen_categories):
        findings.append(diagnostic(
            "global_state_source_category_missing",
            f"Required global-state source category is missing: {missing}.",
        ))
    if schema_version in {5, 6}:
        indexes = _v5_works_tree_indexes(root, root_index_path, findings)
        _validate_latest_accepted_round_index(latest_accepted, indexes, findings)
        if not active_rounds:
            _validate_terminal_work_indexes(indexes, findings)
    return findings


def _v5_works_tree_indexes(
    root: Path, root_index_path: Optional[Path], findings: List[Dict[str, str]],
) -> List[Tuple[Path, Path, str, Any, Any]]:
    if root_index_path is None:
        findings.append(diagnostic(
            "works_tree_root_unavailable",
            "Cannot resolve the canonical root works index directory.",
        ))
        return []
    directory = root_index_path.parent
    try:
        entries = sorted(directory.rglob("*"), key=lambda item: item.as_posix())
    except OSError as error:
        findings.append(diagnostic(
            "works_tree_index_unreadable",
            f"Cannot enumerate the works index tree: {error}.",
            directory.as_posix(),
        ))
        return []
    indexes: List[Tuple[Path, Path, str, Any, Any]] = []
    for candidate in entries:
        if candidate.is_symlink():
            findings.append(diagnostic(
                "works_tree_index_noncanonical",
                "The works index tree must not contain symlink entries.",
                candidate.as_posix(),
            ))
            continue
        if candidate.name != "00_key-index.md" or candidate == root_index_path:
            continue
        if not _v5_canonical_scoped_file(root, candidate):
            findings.append(diagnostic(
                "works_tree_index_noncanonical",
                "Discovered works indexes must be canonical non-symlink scoped files.",
                candidate.as_posix(),
            ))
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            findings.append(diagnostic(
                "works_tree_index_unreadable",
                f"Cannot read discovered works index: {error}.",
                candidate.as_posix(),
            ))
            continue
        indexes.append((
            candidate,
            candidate.relative_to(directory),
            text,
            scalar_from_text(text, "doc_type"),
            frontmatter_mapping_scalar(text, "key", "id"),
        ))
    return indexes


def _v5_canonical_scoped_file(root: Path, candidate: Path) -> bool:
    root_resolved = root.resolve()
    try:
        relative = candidate.relative_to(root_resolved)
    except ValueError:
        return False
    current = root_resolved
    try:
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                return False
        return candidate.is_file() and candidate.resolve().relative_to(root_resolved) == relative
    except (OSError, RuntimeError, ValueError):
        return False


def _validate_latest_accepted_round_index(
    latest_accepted: Any, indexes: List[Tuple[Path, Path, str, Any, Any]],
    findings: List[Dict[str, str]],
) -> None:
    if not isinstance(latest_accepted, str) or not ROUND_PATTERN.fullmatch(latest_accepted):
        return
    matches = []
    for path, relative, text, doc_type, key_id in indexes:
        if (doc_type == "work_round"
                and _v5_round_index_path_matches(relative, latest_accepted)
                and _v5_key_matches_category("round_index", key_id, latest_accepted)):
            matches.append((path, text))
    if len(matches) != 1:
        findings.append(diagnostic(
            "latest_accepted_round_index_ambiguous"
            if len(matches) > 1 else "latest_accepted_round_index_unresolved",
            "latest_accepted_round must resolve to exactly one canonical work_round index.",
        ))
        return
    path, text = matches[0]
    status = scalar_from_text(text, "round_status")
    if status != "accepted":
        findings.append(diagnostic(
            "latest_accepted_round_status_invalid",
            f"latest_accepted_round index must have round_status accepted, not {status}.",
            path.as_posix(),
        ))


def _validate_terminal_work_indexes(
    indexes: List[Tuple[Path, Path, str, Any, Any]],
    findings: List[Dict[str, str]],
) -> None:
    for path, relative, text, doc_type, key_id in indexes:
        if (doc_type != "work"
                or not _v5_key_matches_category("work_index", key_id, "R000")
                or not _v5_work_index_path_matches(relative)):
            continue
        status = scalar_from_text(text, "work_status")
        if status in ACTIVE_WORK_STATUSES:
            findings.append(diagnostic(
                "terminal_active_work_remaining",
                f"Terminal active_round none is invalid while Work status is {status}.",
                path.as_posix(),
            ))


def _v5_round_index_path_matches(path: Path, round_ref: str) -> bool:
    parts = path.parts
    token = round_ref.lower()
    return (
        len(parts) == 2
        and (parts[0].lower() == token or parts[0].lower().startswith(token + "-"))
        and parts[1] == "00_key-index.md"
    )


def _v5_work_index_path_matches(path: Path) -> bool:
    parts = path.parts
    return (
        len(parts) == 3
        and bool(re.fullmatch(r"r\d+(?:-.+)?", parts[0].lower()))
        and bool(parts[1])
        and parts[2] == "00_key-index.md"
    )


def _v5_key_matches_category(category: str, key_id: Any,
                             active_round: Any) -> bool:
    if not isinstance(key_id, str):
        return False
    if category == "root_index":
        return key_id == "key.work.index"
    if category == "context_map":
        return key_id == "key.context-map"
    if not isinstance(active_round, str) or not ROUND_PATTERN.fullmatch(active_round):
        return False
    round_token = active_round.lower()
    if category == "round_index":
        return bool(re.fullmatch(
            rf"key\.work\.round\.{re.escape(round_token)}(?:[.-].+)?\.index",
            key_id,
        ))
    if category == "work_index":
        return bool(
            re.fullmatch(r"key\.work\.(?!round\.).+\.index", key_id)
        )
    return False


def _v5_event_round(manifest: Dict[str, Any],
                    findings: List[Dict[str, str]]) -> Any:
    raw_steps = manifest.get("steps")
    steps = {
        step.get("ref"): step
        for step in raw_steps if isinstance(step, dict)
        and isinstance(step.get("ref"), str)
    } if isinstance(raw_steps, list) else {}
    accepted = manifest.get("accepted_steps")
    rounds = set()
    if not isinstance(accepted, list):
        return None
    for ref in accepted:
        match = STEP_PATTERN.fullmatch(ref) if isinstance(ref, str) else None
        if match is None:
            findings.append(diagnostic(
                "accepted_step_ref_invalid",
                f"Accepted Step ref is not canonical: {ref}.",
            ))
            continue
        if ref not in steps:
            findings.append(diagnostic(
                "accepted_step_event_unresolved",
                f"Accepted Step is absent from finalization steps: {ref}.",
            ))
            continue
        rounds.add(match.group(1))
    if len(rounds) != 1:
        findings.append(diagnostic(
            "accepted_step_event_round_invalid",
            "Accepted Steps must identify exactly one finalization event Round.",
        ))
        return None
    return next(iter(rounds))


def _v5_path_matches_round(path: Any, round_role: str,
                           event_round: Any) -> bool:
    if not isinstance(path, str):
        return False
    if not isinstance(event_round, str) or not ROUND_PATTERN.fullmatch(event_round):
        return False
    token = event_round.lower()
    has_round_segment = any(
        part.lower() == token or part.lower().startswith(token + "-")
        for part in Path(path).parts
    )
    return has_round_segment if round_role == "event_round" else not has_round_segment
