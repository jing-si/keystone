"""Structured repository-global finalization state validation."""

import re
from pathlib import Path
from typing import Any, Dict, List

from finalization_support import (
    diagnostic,
    frontmatter_mapping_list,
    frontmatter_mapping_scalar,
    read_scoped_file,
    resolve_scoped_path,
)


GLOBAL_SOURCE_CATEGORIES = {
    "work_index", "round_index", "root_index", "context_map",
}
ROUND_PATTERN = re.compile(r"^R\d+$")


def validate_global_state(root: Path, manifest: Dict[str, Any],
                          schema_version: Any) -> List[Dict[str, str]]:
    """Validate schema-v4 global state against four distinct typed sources."""
    if schema_version != 4:
        return []
    findings: List[Dict[str, str]] = []
    state = manifest.get("global_state")
    if not isinstance(state, dict):
        return [diagnostic(
            "global_state_missing",
            "schema_version 4 requires structured global_state.",
        )]

    active_round = state.get("active_round")
    latest_accepted = state.get("latest_accepted_round")
    active_steps = state.get("active_steps")
    active_round_valid = (
        isinstance(active_round, str)
        and (bool(ROUND_PATTERN.fullmatch(active_round)) or active_round == "none")
    )
    if not active_round_valid:
        findings.append(diagnostic(
            "global_state_active_round_invalid",
            "global_state.active_round must be a Round ref or none.",
        ))
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
    if active_round == "none" and active_steps:
        findings.append(diagnostic(
            "global_state_active_round_mismatch",
            "global_state.active_round may be none only when active_steps is empty.",
        ))

    sources = state.get("sources")
    if not isinstance(sources, list):
        findings.append(diagnostic(
            "global_state_sources_invalid",
            "global_state.sources must be an array.",
        ))
        return findings

    seen_categories = set()
    seen_paths = set()
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
    return findings
