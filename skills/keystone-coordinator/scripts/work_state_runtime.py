#!/usr/bin/env python3
"""Derive deterministic Keystone work state from repository-owned sources."""

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SCHEMA_VERSION = 1
POLICY_VERSION = "keystone-work-state-v1"
ACCEPTANCE_EVENT_PATH = "00_docs/works/key-acceptance-events.json"
ACTIVE_WORK_STATUSES = frozenset({"in_progress", "blocked"})
TERMINAL_RESIDUAL_STATUSES = frozenset({"planned", "in_progress", "blocked"})
PUBLIC_API = (
    "build_next_acceptance_event",
    "canonical_json_bytes",
    "derive_work_state",
    "evaluate_repository",
    "historical_projection_digest",
    "parse_frontmatter",
    "policy_digest",
    "public_api_digest",
    "validate_acceptance_event_chain",
    "validate_prerequisite_closures",
)
_ROUND_DIRECTORY = re.compile(r"^r(?P<number>\d+)(?:-.+)?$")
_ROUND_REF = re.compile(r"^R(?P<number>\d+)$")
_STEP_REF = re.compile(r"^(?P<round>R\d+)/S\d+(?:-[A-Z0-9]+)*$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_WORK_INDEX = re.compile(r"^00_docs/works/r\d+(?:-[^/]+)?/[^/]+/00_key-index\.md$")
_ROUND_INDEX = re.compile(r"^00_docs/works/r\d+(?:-[^/]+)?/00_key-index\.md$")
_PROGRESS = re.compile(r"^00_docs/works/r\d+(?:-[^/]+)?/[^/]+/key-progress\.md$")
_WORK_ORDER = re.compile(r"^00_docs/works/r\d+(?:-[^/]+)?/[^/]+/key-work-[^/]+\.md$")
_FINALIZATION_MANIFEST = re.compile(
    r"^00_docs/works/r\d+(?:-[^/]+)?/key-finalization-manifest\.json$"
)


class WorkStateError(ValueError):
    """Raised when one source cannot be interpreted deterministically."""


@dataclass(frozen=True)
class SourceRecord:
    path: str
    raw_bytes: bytes
    digest: str
    kind: str
    frontmatter: Mapping[str, Any]
    json_value: Optional[Any] = None


def canonical_json_bytes(value: Any) -> bytes:
    """Return canonical UTF-8 JSON bytes used by every runtime digest."""
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _diagnostic(code: str, message: str, path: Optional[str] = None) -> Dict[str, str]:
    value = {"severity": "error", "code": code, "message": message}
    if path is not None:
        value["path"] = path
    return value


def policy_digest() -> str:
    """Return the stable digest of policy-bearing constants and wire rules."""
    policy = {
        "policy_version": POLICY_VERSION,
        "schema_version": SCHEMA_VERSION,
        "acceptance_event_path": ACCEPTANCE_EVENT_PATH,
        "active_work_statuses": sorted(ACTIVE_WORK_STATUSES),
        "terminal_residual_statuses": sorted(TERMINAL_RESIDUAL_STATUSES),
        "event_fields": [
            "id", "sequence", "previous_event_ref", "round_ref",
            "accepted_steps", "acceptance_ref", "subject_digest",
            "accepted_at", "accepted_by",
        ],
        "ordering": "unique-forward-chain-with-sequence-zero-genesis",
        "migration_genesis": "R009",
        "historical_projection": "accepted-round-step-semantic-v1",
        "early_work_projection": "finalization-manifest-path-order-v1",
        "prerequisite_closure_fields": [
            "work_ref", "result", "waiver_reason", "follow_up",
            "acceptance_ref", "manifest_digest", "envelope_digest",
            "author_runner_status",
        ],
        "schema_v6_finalization_digest": "binding-neutral-canonical-json-v1",
    }
    return _digest_bytes(canonical_json_bytes(policy))


def public_api_digest() -> str:
    """Return the digest of the package-stable callable surface."""
    return _digest_bytes(canonical_json_bytes(list(PUBLIC_API)))


def _split_top_level(value: str, delimiter: str) -> List[str]:
    parts: List[str] = []
    start = 0
    depth = 0
    quote: Optional[str] = None
    escaped = False
    for index, character in enumerate(value):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\" and quote == '"':
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
        elif character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
        elif character == delimiter and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return parts


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise WorkStateError("invalid quoted scalar: %s" % error) from error
        if not isinstance(parsed, str):
            raise WorkStateError("quoted scalar must be a string")
        return parsed
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [_parse_scalar(item) for item in _split_top_level(body, ",")]
    if value.startswith("{") and value.endswith("}"):
        body = value[1:-1].strip()
        result: Dict[str, Any] = {}
        if not body:
            return result
        for item in _split_top_level(body, ","):
            pair = _split_top_level(item, ":")
            if len(pair) < 2:
                raise WorkStateError("inline mapping entry is invalid")
            key = pair[0].strip().strip("'\"")
            if not key or key in result:
                raise WorkStateError("inline mapping key is missing or duplicated")
            result[key] = _parse_scalar(":".join(pair[1:]))
        return result
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none", "~"}:
        return None
    if re.fullmatch(r"-?(?:0|[1-9]\d*)", value):
        return int(value)
    return value


def _yaml_lines(text: str) -> List[Tuple[int, str]]:
    lines: List[Tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indentation = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw[:indentation]:
            raise WorkStateError("frontmatter indentation cannot contain tabs")
        lines.append((indentation, raw[indentation:].rstrip()))
    return lines


def _mapping_entry(content: str) -> Tuple[str, str]:
    parts = _split_top_level(content, ":")
    if len(parts) < 2:
        raise WorkStateError("frontmatter mapping entry has no colon")
    key = parts[0].strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", key):
        raise WorkStateError("frontmatter mapping key is invalid: %s" % key)
    return key, ":".join(parts[1:]).strip()


def _parse_yaml_block(
    lines: Sequence[Tuple[int, str]], index: int, indentation: int,
) -> Tuple[Any, int]:
    if index >= len(lines) or lines[index][0] < indentation:
        return {}, index
    is_list = lines[index][0] == indentation and lines[index][1].startswith("- ")
    if is_list:
        values: List[Any] = []
        while index < len(lines):
            current_indent, content = lines[index]
            if current_indent < indentation:
                break
            if current_indent != indentation or not content.startswith("- "):
                break
            item = content[2:].strip()
            index += 1
            if not item:
                if index < len(lines) and lines[index][0] > indentation:
                    nested, index = _parse_yaml_block(lines, index, lines[index][0])
                    values.append(nested)
                else:
                    values.append(None)
                continue
            if ":" not in item:
                values.append(_parse_scalar(item))
                continue
            key, raw = _mapping_entry(item)
            mapping: Dict[str, Any] = {}
            if raw:
                mapping[key] = _parse_scalar(raw)
            elif index < len(lines) and lines[index][0] > indentation:
                mapping[key], index = _parse_yaml_block(lines, index, lines[index][0])
            else:
                mapping[key] = {}
            if index < len(lines) and lines[index][0] > indentation:
                continuation, index = _parse_yaml_block(lines, index, lines[index][0])
                if not isinstance(continuation, dict):
                    raise WorkStateError("list mapping continuation must be a mapping")
                for nested_key, nested_value in continuation.items():
                    if nested_key in mapping:
                        raise WorkStateError("frontmatter mapping key is duplicated")
                    mapping[nested_key] = nested_value
            values.append(mapping)
        return values, index

    mapping = {}
    while index < len(lines):
        current_indent, content = lines[index]
        if current_indent < indentation:
            break
        if current_indent != indentation or content.startswith("- "):
            break
        key, raw = _mapping_entry(content)
        if key in mapping:
            raise WorkStateError("frontmatter mapping key is duplicated: %s" % key)
        index += 1
        if raw:
            mapping[key] = _parse_scalar(raw)
        elif index < len(lines) and lines[index][0] > indentation:
            mapping[key], index = _parse_yaml_block(lines, index, lines[index][0])
        else:
            mapping[key] = {}
    return mapping, index


def parse_frontmatter(text: str) -> Mapping[str, Any]:
    """Parse the deterministic YAML subset used by Keystone frontmatter."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return {}
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    if match is None:
        raise WorkStateError("frontmatter closing delimiter is missing")
    lines = _yaml_lines(match.group(1))
    if not lines:
        return {}
    value, consumed = _parse_yaml_block(lines, 0, lines[0][0])
    if consumed != len(lines) or not isinstance(value, dict):
        raise WorkStateError("frontmatter root must be one complete mapping")
    return value


def _strict_json(raw: bytes, path: str) -> Any:
    def reject_pairs(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        value: Dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise WorkStateError("duplicate JSON key in %s: %s" % (path, key))
            value[key] = item
        return value

    def reject_constant(value: str) -> None:
        raise WorkStateError("non-finite JSON value in %s: %s" % (path, value))

    try:
        return json.loads(
            raw.decode("utf-8"), object_pairs_hook=reject_pairs,
            parse_constant=reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise WorkStateError("invalid JSON in %s: %s" % (path, error)) from error


def _round_from_path(path: str) -> Optional[str]:
    parts = PurePosixPath(path).parts
    try:
        index = parts.index("works")
    except ValueError:
        return None
    if index + 1 >= len(parts):
        return None
    match = _ROUND_DIRECTORY.fullmatch(parts[index + 1])
    if match is None:
        return None
    return "R" + match.group("number").zfill(3)


def _source_kind(path: str) -> Optional[str]:
    if path == "00_docs/works/00_key-index.md":
        return "root_index"
    if path == "00_docs/key-context-map.md":
        return "context_map"
    if path == ACCEPTANCE_EVENT_PATH:
        return "acceptance_events"
    if _ROUND_INDEX.fullmatch(path):
        return "round_index"
    if _WORK_INDEX.fullmatch(path):
        return "work_index"
    if _PROGRESS.fullmatch(path):
        return "progress"
    if _WORK_ORDER.fullmatch(path):
        return "work_order"
    if _FINALIZATION_MANIFEST.fullmatch(path):
        return "finalization_manifest"
    return None


def _records_from_sources(
    sources: Mapping[str, bytes], diagnostics: List[Dict[str, str]],
) -> Tuple[SourceRecord, ...]:
    records: List[SourceRecord] = []
    for path in sorted(sources):
        kind = _source_kind(path)
        if kind is None:
            continue
        raw = sources[path]
        try:
            if kind in {"acceptance_events", "finalization_manifest"}:
                json_value = _strict_json(raw, path)
                frontmatter: Mapping[str, Any] = {}
            else:
                json_value = None
                frontmatter = parse_frontmatter(raw.decode("utf-8"))
        except (UnicodeError, WorkStateError) as error:
            diagnostics.append(_diagnostic("work_state_source_invalid", str(error), path))
            continue
        digest_bytes = raw
        if (
            kind == "finalization_manifest"
            and isinstance(json_value, Mapping)
            and json_value.get("schema_version") == 6
            and "work_state_runtime" in json_value
        ):
            normalized = dict(json_value)
            normalized["work_state_runtime"] = {
                "binding_neutral": "keystone-work-state-v1"
            }
            digest_bytes = canonical_json_bytes(normalized)
        records.append(SourceRecord(
            path, raw, _digest_bytes(digest_bytes), kind, frontmatter, json_value
        ))
    return tuple(records)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _state_scalar(record: SourceRecord, key: str) -> Any:
    return record.frontmatter.get(key)


def _approval(record: SourceRecord) -> Any:
    return _mapping(record.frontmatter.get("approval")).get("state")


def _finalization(record: SourceRecord) -> Mapping[str, Any]:
    return _mapping(record.frontmatter.get("finalization"))


def _historical_projection(records: Sequence[SourceRecord], through_round: str) -> Dict[str, Any]:
    match = _ROUND_REF.fullmatch(through_round)
    if match is None:
        raise WorkStateError("historical projection boundary must be a Round ref")
    boundary = int(match.group("number"))
    rounds: List[Dict[str, Any]] = []
    steps: List[Dict[str, Any]] = []
    for record in records:
        round_ref = _round_from_path(record.path)
        if round_ref is None or int(round_ref[1:]) > boundary:
            continue
        if record.kind == "round_index":
            rounds.append({
                "round_ref": round_ref,
                "round_status": _state_scalar(record, "round_status"),
                "approval_state": _approval(record),
            })
        elif record.kind == "progress":
            step_ref = _state_scalar(record, "step_ref")
            steps.append({
                "step_ref": step_ref,
                "work_status": _state_scalar(record, "work_status"),
                "approval_state": _approval(record),
                "finalization_state": _finalization(record).get("state"),
                "acceptance_ref": _finalization(record).get("acceptance_ref"),
            })
    return {
        "schema_version": 1,
        "through_round": through_round,
        "rounds": sorted(rounds, key=lambda item: str(item["round_ref"])),
        "steps": sorted(steps, key=lambda item: str(item["step_ref"])),
    }


def historical_projection_digest(
    sources: Mapping[str, bytes], through_round: str = "R009",
) -> str:
    """Digest the accepted-history semantic projection through one Round."""
    diagnostics: List[Dict[str, str]] = []
    records = _records_from_sources(sources, diagnostics)
    if diagnostics:
        raise WorkStateError(diagnostics[0]["message"])
    return _digest_bytes(canonical_json_bytes(
        _historical_projection(records, through_round)
    ))


def validate_acceptance_event_chain(
    raw_events: Any, historical_digest: str,
) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, str]]]:
    """Validate the forward-only accepted-Round chain and return its head."""
    diagnostics: List[Dict[str, str]] = []
    if not isinstance(raw_events, Mapping) or raw_events.get("schema_version") != 1:
        return None, [_diagnostic(
            "acceptance_event_source_invalid",
            "acceptance event source must be a schema-version 1 object.",
            ACCEPTANCE_EVENT_PATH,
        )]
    events = raw_events.get("events")
    if not isinstance(events, list) or not events:
        return None, [_diagnostic(
            "acceptance_event_chain_missing",
            "acceptance event source requires at least the R009 migration genesis.",
            ACCEPTANCE_EVENT_PATH,
        )]
    required = {
        "id", "sequence", "previous_event_ref", "round_ref", "accepted_steps",
        "acceptance_ref", "subject_digest", "accepted_at", "accepted_by",
    }
    by_id: Dict[str, Mapping[str, Any]] = {}
    by_sequence: Dict[int, Mapping[str, Any]] = {}
    children: Dict[Optional[str], List[str]] = {}
    for index, event in enumerate(events):
        path = "%s#events[%d]" % (ACCEPTANCE_EVENT_PATH, index)
        if not isinstance(event, Mapping) or set(event) != required:
            diagnostics.append(_diagnostic(
                "acceptance_event_schema_invalid",
                "acceptance event fields must match the canonical schema exactly.", path,
            ))
            continue
        event_id = event.get("id")
        sequence = event.get("sequence")
        predecessor = event.get("previous_event_ref")
        round_ref = event.get("round_ref")
        steps = event.get("accepted_steps")
        if not isinstance(event_id, str) or not event_id:
            diagnostics.append(_diagnostic("acceptance_event_id_invalid", "Event id is invalid.", path))
        elif event_id in by_id:
            diagnostics.append(_diagnostic("acceptance_event_id_duplicate", "Event id is duplicated.", path))
        else:
            by_id[event_id] = event
        if type(sequence) is not int or sequence < 0:
            diagnostics.append(_diagnostic("acceptance_event_sequence_invalid", "Event sequence is invalid.", path))
        elif sequence in by_sequence:
            diagnostics.append(_diagnostic("acceptance_event_sequence_duplicate", "Event sequence is duplicated.", path))
        else:
            by_sequence[sequence] = event
        if predecessor is not None and (not isinstance(predecessor, str) or not predecessor):
            diagnostics.append(_diagnostic("acceptance_event_predecessor_invalid", "Event predecessor is invalid.", path))
        if not isinstance(round_ref, str) or _ROUND_REF.fullmatch(round_ref) is None:
            diagnostics.append(_diagnostic("acceptance_event_round_invalid", "Event round_ref is invalid.", path))
        if (not isinstance(steps, list) or not steps
                or not all(isinstance(step, str) and _STEP_REF.fullmatch(step) for step in steps)
                or len(set(steps)) != len(steps)):
            diagnostics.append(_diagnostic("acceptance_event_steps_invalid", "accepted_steps must be unique canonical Step refs.", path))
        elif isinstance(round_ref, str) and any(
            step.split("/", 1)[0] != round_ref for step in steps
        ):
            diagnostics.append(_diagnostic(
                "acceptance_event_step_round_mismatch",
                "Every accepted Step must belong to the event Round.", path,
            ))
        if not isinstance(event.get("acceptance_ref"), str) or not event["acceptance_ref"]:
            diagnostics.append(_diagnostic("acceptance_event_ref_invalid", "acceptance_ref is required.", path))
        if not isinstance(event.get("subject_digest"), str) or _DIGEST.fullmatch(event["subject_digest"]) is None:
            diagnostics.append(_diagnostic("acceptance_event_subject_invalid", "subject_digest is invalid.", path))
        if not isinstance(event.get("accepted_at"), str) or not event["accepted_at"]:
            diagnostics.append(_diagnostic("acceptance_event_time_invalid", "accepted_at is required.", path))
        if event.get("accepted_by") != "main":
            diagnostics.append(_diagnostic("acceptance_event_actor_invalid", "accepted_by must be main.", path))
        if isinstance(event_id, str):
            children.setdefault(predecessor, []).append(event_id)

    if diagnostics:
        return None, diagnostics
    genesis = by_sequence.get(0)
    if genesis is None:
        diagnostics.append(_diagnostic("acceptance_event_genesis_missing", "Sequence zero genesis is missing."))
        return None, diagnostics
    if (genesis.get("previous_event_ref") is not None
            or genesis.get("round_ref") != "R009"
            or genesis.get("subject_digest") != historical_digest):
        diagnostics.append(_diagnostic(
            "acceptance_event_genesis_invalid",
            "Genesis must bind the R009 migration boundary and historical projection digest.",
            ACCEPTANCE_EVENT_PATH,
        ))
    if children.get(None) != [genesis.get("id")]:
        diagnostics.append(_diagnostic(
            "acceptance_event_genesis_ambiguous", "The chain must have exactly one genesis."
        ))
    visited = set()
    current: Optional[Mapping[str, Any]] = genesis
    expected_sequence = 0
    while current is not None:
        current_id = str(current.get("id"))
        if current_id in visited:
            diagnostics.append(_diagnostic("acceptance_event_cycle", "Acceptance event chain contains a cycle."))
            break
        visited.add(current_id)
        if current.get("sequence") != expected_sequence:
            diagnostics.append(_diagnostic("acceptance_event_sequence_gap", "Acceptance event sequence must advance by exactly one."))
            break
        successors = children.get(current_id, [])
        if len(successors) > 1:
            diagnostics.append(_diagnostic("acceptance_event_fork", "Acceptance event predecessor has multiple successors."))
            break
        if not successors:
            break
        successor = by_id.get(successors[0])
        if successor is None:
            diagnostics.append(_diagnostic("acceptance_event_successor_missing", "Acceptance event successor is missing."))
            break
        current = successor
        expected_sequence += 1
    if len(visited) != len(by_id):
        diagnostics.append(_diagnostic(
            "acceptance_event_chain_disconnected",
            "Every acceptance event must belong to the unique genesis chain.",
        ))
    return (dict(current) if current is not None and not diagnostics else None), diagnostics


def build_next_acceptance_event(
    raw_events: Mapping[str, Any], historical_digest: str, *, event_id: str,
    round_ref: str, accepted_steps: Sequence[str], acceptance_ref: str,
    subject_digest: str, accepted_at: str, accepted_by: str = "main",
) -> Dict[str, Any]:
    """Build one successor event from the unique valid chain head."""
    head, diagnostics = validate_acceptance_event_chain(raw_events, historical_digest)
    if diagnostics or head is None:
        raise WorkStateError(
            "cannot extend invalid acceptance chain: %s"
            % ", ".join(item["code"] for item in diagnostics)
        )
    event = {
        "id": event_id,
        "sequence": head["sequence"] + 1,
        "previous_event_ref": head["id"],
        "round_ref": round_ref,
        "accepted_steps": list(accepted_steps),
        "acceptance_ref": acceptance_ref,
        "subject_digest": subject_digest,
        "accepted_at": accepted_at,
        "accepted_by": accepted_by,
    }
    candidate = {
        "schema_version": 1,
        "events": [dict(item) for item in raw_events.get("events", [])] + [event],
    }
    candidate_head, candidate_diagnostics = validate_acceptance_event_chain(
        candidate, historical_digest
    )
    if candidate_diagnostics or candidate_head != event:
        raise WorkStateError(
            "new acceptance event is invalid: %s"
            % ", ".join(item["code"] for item in candidate_diagnostics)
        )
    return event


def validate_prerequisite_closures(
    raw_closures: Any,
    observed_evidence: Optional[Mapping[str, Mapping[str, Any]]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """Validate complete or explicitly waived prerequisite finalization records."""
    diagnostics: List[Dict[str, str]] = []
    if raw_closures is None:
        return [], diagnostics
    if not isinstance(raw_closures, list):
        return [], [_diagnostic(
            "prerequisite_closures_invalid", "prerequisite_closures must be an array."
        )]
    closures: List[Dict[str, Any]] = []
    seen = set()
    fields = {
        "work_ref", "result", "waiver_reason", "follow_up", "acceptance_ref",
        "manifest_digest", "envelope_digest", "author_runner_status",
    }
    for index, raw in enumerate(raw_closures):
        path = "prerequisite_closures[%d]" % index
        if not isinstance(raw, Mapping) or set(raw) != fields:
            diagnostics.append(_diagnostic(
                "prerequisite_closure_schema_invalid",
                "Prerequisite closure fields must match the canonical schema exactly.", path,
            ))
            continue
        work_ref = raw.get("work_ref")
        if not isinstance(work_ref, str) or not work_ref or work_ref in seen:
            diagnostics.append(_diagnostic(
                "prerequisite_closure_work_invalid", "work_ref is missing or duplicated.", path
            ))
        else:
            seen.add(work_ref)
        result = raw.get("result")
        if result not in {"complete", "waived"}:
            diagnostics.append(_diagnostic(
                "prerequisite_closure_result_invalid", "result must be complete or waived.", path
            ))
        if result == "waived" and (
            not isinstance(raw.get("waiver_reason"), str) or not raw["waiver_reason"].strip()
            or not isinstance(raw.get("follow_up"), str) or not raw["follow_up"].strip()
        ):
            diagnostics.append(_diagnostic(
                "prerequisite_closure_waiver_incomplete",
                "Waived closure requires non-empty waiver_reason and follow_up.", path,
            ))
        if result == "complete" and (raw.get("waiver_reason") not in {None, ""}
                                      or raw.get("follow_up") not in {None, ""}):
            diagnostics.append(_diagnostic(
                "prerequisite_closure_complete_has_waiver",
                "Complete closure cannot carry waiver fields.", path,
            ))
        for field in ("acceptance_ref", "manifest_digest", "envelope_digest"):
            value = raw.get(field)
            if not isinstance(value, str) or not value:
                diagnostics.append(_diagnostic(
                    "prerequisite_closure_evidence_missing",
                    "%s is required." % field, path,
                ))
            elif field.endswith("digest") and _DIGEST.fullmatch(value) is None:
                diagnostics.append(_diagnostic(
                    "prerequisite_closure_digest_invalid",
                    "%s must be a canonical sha256 digest." % field, path,
                ))
        if raw.get("author_runner_status") != "pass":
            diagnostics.append(_diagnostic(
                "prerequisite_closure_author_runner_failed",
                "Package-owned Author runner status must be pass.", path,
            ))
        if observed_evidence is not None and isinstance(work_ref, str):
            observed = observed_evidence.get(work_ref)
            expected_evidence = {
                "manifest_digest": raw.get("manifest_digest"),
                "envelope_digest": raw.get("envelope_digest"),
                "author_runner_status": raw.get("author_runner_status"),
            }
            if not isinstance(observed, Mapping):
                diagnostics.append(_diagnostic(
                    "prerequisite_closure_evidence_unavailable",
                    "Observed prerequisite finalization evidence is unavailable.", path,
                ))
            elif {key: observed.get(key) for key in expected_evidence} != expected_evidence:
                diagnostics.append(_diagnostic(
                    "prerequisite_closure_evidence_stale",
                    "Prerequisite manifest, envelope, or Author runner evidence is stale.", path,
                ))
        closures.append(dict(raw))
    return sorted(closures, key=lambda item: str(item.get("work_ref"))), diagnostics


def _pointer_claim(record: SourceRecord) -> Optional[Dict[str, Any]]:
    state = record.frontmatter.get("global_state")
    if not isinstance(state, Mapping):
        return None
    return {
        "path": record.path,
        "active_round": state.get("active_round"),
        "latest_accepted_round": state.get("latest_accepted_round"),
        "active_steps": state.get("active_steps"),
    }


def _dependency_evaluations(records: Sequence[SourceRecord]) -> List[Dict[str, Any]]:
    by_key: Dict[str, SourceRecord] = {}
    by_directory: Dict[str, SourceRecord] = {}
    for record in records:
        key_id = _mapping(record.frontmatter.get("key")).get("id")
        if isinstance(key_id, str):
            by_key[key_id] = record
        if record.kind == "work_index":
            by_directory[str(PurePosixPath(record.path).parent)] = record
    evaluations: List[Dict[str, Any]] = []
    for record in records:
        if record.kind != "work_order":
            continue
        gates = record.frontmatter.get("work_gates")
        if not isinstance(gates, list):
            continue
        for index, gate in enumerate(gates):
            if not isinstance(gate, Mapping):
                continue
            dependency = gate.get("dependency")
            target = by_key.get(dependency) if isinstance(dependency, str) else None
            target_index = (
                by_directory.get(str(PurePosixPath(target.path).parent))
                if target is not None else None
            )
            condition = _mapping(gate.get("condition"))
            target_status = _state_scalar(target_index, "work_status") if target_index else None
            target_approval = _approval(target_index) if target_index else None
            satisfied = (
                target_index is not None
                and target_status == condition.get("work_status")
                and target_approval == condition.get("approval_state")
            )
            evaluations.append({
                "gate_id": "%s#work_gates[%d]" % (record.path, index),
                "source_path": record.path,
                "dependency": dependency,
                "applies_to": dict(_mapping(gate.get("applies_to"))),
                "target_state": {
                    "work_status": target_status,
                    "approval_state": target_approval,
                },
                "result": "satisfied" if satisfied else "waiting",
                "blocking": not bool(gate.get("optional")),
            })
    return sorted(evaluations, key=lambda item: item["gate_id"])


def _early_work_projection(records: Sequence[SourceRecord]) -> List[Dict[str, Any]]:
    projected: List[Dict[str, Any]] = []
    for record in records:
        if record.kind != "finalization_manifest" or not isinstance(
            record.json_value, Mapping
        ):
            continue
        early_work = record.json_value.get("early_work")
        if not isinstance(early_work, list):
            continue
        for index, item in enumerate(early_work):
            if not isinstance(item, Mapping):
                continue
            projected.append({
                "source_path": record.path,
                "source_index": index,
                "record": dict(item),
            })
    return sorted(
        projected,
        key=lambda item: (str(item["source_path"]), int(item["source_index"])),
    )


def derive_work_state(
    sources: Mapping[str, bytes], *, complete: bool = True,
    discovery_diagnostics: Sequence[Mapping[str, str]] = (),
    prerequisite_closures: Any = None,
) -> Dict[str, Any]:
    """Derive the canonical work-state envelope from captured source bytes."""
    diagnostics = [dict(item) for item in discovery_diagnostics]
    records = _records_from_sources(sources, diagnostics)
    root_index = next((item for item in records if item.kind == "root_index"), None)
    context_map = next((item for item in records if item.kind == "context_map"), None)
    if root_index is None and context_map is None and not any(
        item.path.startswith("00_docs/") for item in records
    ):
        initialization = "uninitialized"
    elif root_index is None or context_map is None:
        initialization = "partial"
        diagnostics.append(_diagnostic(
            "work_state_initialization_partial",
            "Initialized Keystone state requires Context Map and root works index.",
        ))
    else:
        initialization = "initialized"

    rounds: Dict[str, SourceRecord] = {}
    active_rounds: List[str] = []
    accepted_rounds: List[str] = []
    for record in records:
        if record.kind != "round_index":
            continue
        round_ref = _round_from_path(record.path)
        if round_ref is None or round_ref in rounds:
            diagnostics.append(_diagnostic(
                "work_state_round_identity_invalid",
                "Round index path must resolve to one unique Round ref.", record.path,
            ))
            continue
        rounds[round_ref] = record
        status = _state_scalar(record, "round_status")
        if status == "active":
            active_rounds.append(round_ref)
        elif status == "accepted":
            accepted_rounds.append(round_ref)
    active_rounds.sort()
    accepted_rounds.sort()
    if len(active_rounds) > 1:
        diagnostics.append(_diagnostic(
            "work_state_multiple_active_rounds",
            "Repository work state may contain at most one active Round.",
        ))
    active_round = active_rounds[0] if len(active_rounds) == 1 else "none"

    active_works: List[Dict[str, str]] = []
    active_work_directories = set()
    all_work_records: List[SourceRecord] = []
    for record in records:
        if record.kind != "work_index":
            continue
        all_work_records.append(record)
        status = _state_scalar(record, "work_status")
        if status not in ACTIVE_WORK_STATUSES:
            if active_round == "none" and status in TERMINAL_RESIDUAL_STATUSES:
                diagnostics.append(_diagnostic(
                    "work_state_terminal_residual_work",
                    "Terminal work state cannot contain planned, in-progress, or blocked Work.",
                    record.path,
                ))
            continue
        round_ref = _round_from_path(record.path)
        work_ref = _state_scalar(record, "work_id")
        active_works.append({
            "round_ref": str(round_ref),
            "work_ref": str(work_ref),
            "status": str(status),
            "path": record.path,
        })
        active_work_directories.add(str(PurePosixPath(record.path).parent))
        if round_ref != active_round:
            diagnostics.append(_diagnostic(
                "work_state_active_work_outside_round",
                "Active Work must belong to the unique active Round.", record.path,
            ))

    active_steps: List[str] = []
    active_progress: List[SourceRecord] = []
    for record in records:
        if record.kind != "progress" or _state_scalar(record, "work_status") not in ACTIVE_WORK_STATUSES:
            continue
        step_ref = _state_scalar(record, "step_ref")
        if not isinstance(step_ref, str) or _STEP_REF.fullmatch(step_ref) is None:
            diagnostics.append(_diagnostic(
                "work_state_active_step_invalid", "Active progress requires a canonical Step ref.", record.path,
            ))
            continue
        active_steps.append(step_ref)
        active_progress.append(record)
        if step_ref.split("/", 1)[0] != active_round:
            diagnostics.append(_diagnostic(
                "work_state_active_step_outside_round",
                "Active Step must belong to the unique active Round.", record.path,
            ))
        if str(PurePosixPath(record.path).parent) not in active_work_directories:
            diagnostics.append(_diagnostic(
                "work_state_active_step_without_work",
                "Active Step requires an active Work index in the same directory.", record.path,
            ))
    active_steps.sort()
    if len(active_steps) != len(set(active_steps)):
        diagnostics.append(_diagnostic(
            "work_state_active_step_duplicate", "Active Step refs must be unique."
        ))

    historical_digest = _digest_bytes(canonical_json_bytes(
        _historical_projection(records, "R009")
    ))
    event_record = next((item for item in records if item.kind == "acceptance_events"), None)
    if initialization == "uninitialized":
        event_head = None
        event_findings: List[Dict[str, str]] = []
    elif event_record is None:
        event_head = None
        event_findings = [_diagnostic(
            "acceptance_event_source_missing",
            "Initialized state requires the canonical acceptance event source.",
            ACCEPTANCE_EVENT_PATH,
        )]
    else:
        event_head, event_findings = validate_acceptance_event_chain(
            event_record.json_value, historical_digest
        )
    diagnostics.extend(event_findings)
    latest_accepted = event_head.get("round_ref") if event_head is not None else None
    progress_by_step = {
        _state_scalar(record, "step_ref"): record
        for record in records if record.kind == "progress"
        and isinstance(_state_scalar(record, "step_ref"), str)
    }
    if event_record is not None and isinstance(event_record.json_value, Mapping):
        raw_events = event_record.json_value.get("events")
        if isinstance(raw_events, list):
            for event in raw_events:
                if not isinstance(event, Mapping) or not isinstance(event.get("accepted_steps"), list):
                    continue
                for step_ref in event["accepted_steps"]:
                    progress = progress_by_step.get(step_ref)
                    if (progress is None
                            or _state_scalar(progress, "work_status") != "complete"
                            or _approval(progress) != "accepted"
                            or _finalization(progress).get("state") != "complete"
                            or _finalization(progress).get("acceptance_ref") != event.get("acceptance_ref")):
                        diagnostics.append(_diagnostic(
                            "acceptance_event_step_source_mismatch",
                            "Accepted event Step must resolve to matching complete, accepted, finalized Progress.",
                            str(step_ref),
                        ))
    if latest_accepted is not None:
        latest_index = rounds.get(str(latest_accepted))
        if latest_index is None or _state_scalar(latest_index, "round_status") != "accepted":
            diagnostics.append(_diagnostic(
                "work_state_latest_accepted_unresolved",
                "Acceptance chain head must resolve to one accepted Round index.",
            ))

    pointer_sources: List[SourceRecord] = []
    if root_index is not None:
        pointer_sources.append(root_index)
    if context_map is not None:
        pointer_sources.append(context_map)
    pointer_sources.extend(
        record for record in rounds.values() if _round_from_path(record.path) == active_round
    )
    pointer_sources.extend(record for record in all_work_records if record.path.rsplit("/", 1)[0] in active_work_directories)
    claims = [claim for claim in (_pointer_claim(item) for item in pointer_sources) if claim]
    expected_claim = {
        "active_round": active_round,
        "latest_accepted_round": latest_accepted,
        "active_steps": active_steps,
    }
    for claim in claims:
        observed = {key: claim.get(key) for key in expected_claim}
        if observed != expected_claim:
            diagnostics.append(_diagnostic(
                "work_state_pointer_stale",
                "Global-state pointer claim differs from repository-derived state.",
                str(claim["path"]),
            ))

    dependencies = _dependency_evaluations(records)
    closures, closure_findings = validate_prerequisite_closures(prerequisite_closures)
    diagnostics.extend(closure_findings)
    if not complete:
        diagnostics.append(_diagnostic(
            "work_state_discovery_incomplete",
            "Incomplete source discovery cannot produce authority-bearing work state.",
        ))

    path_digests = [{"path": item.path, "digest": item.digest} for item in records]
    path_set = [item["path"] for item in path_digests]
    generation = {
        "complete": bool(complete),
        "source_count": len(path_digests),
        "source_generation": _digest_bytes(canonical_json_bytes(path_digests)),
        "path_set_digest": _digest_bytes(canonical_json_bytes(path_set)),
        "snapshot_digest": _digest_bytes(canonical_json_bytes({
            "sources": path_digests,
            "complete": bool(complete),
        })),
    }
    state = {
        "initialization": initialization,
        "active_round": active_round,
        "active_rounds": active_rounds,
        "accepted_rounds": accepted_rounds,
        "active_works": sorted(active_works, key=lambda item: item["path"]),
        "active_steps": active_steps,
        "latest_accepted_round": latest_accepted,
        "acceptance_event_head": event_head,
        "historical_projection_digest": historical_digest,
        "pointer_claims": sorted(claims, key=lambda item: str(item["path"])),
        "dependency_evaluations": dependencies,
        "finalization_gates": [
            item for item in dependencies
            if _mapping(item.get("applies_to")).get("work_completion") is True
        ],
        "prerequisite_closures": closures,
        "early_work": _early_work_projection(records),
    }
    envelope_subject = {
        "policy_digest": policy_digest(),
        "generation": generation,
        "state": state,
        "diagnostics": diagnostics,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "fail" if diagnostics else "pass",
        "policy_digest": policy_digest(),
        "public_api_digest": public_api_digest(),
        "generation": generation,
        "state": state,
        "result_digest": _digest_bytes(canonical_json_bytes(envelope_subject)),
        "diagnostics": diagnostics,
        "summary": {
            "errors": len(diagnostics),
            "warnings": 0,
        },
    }


def _safe_relative(path: Path, root: Path) -> Optional[str]:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return None
    pure = PurePosixPath(relative.as_posix())
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        return None
    return pure.as_posix()


def _discover_sources(root: Path, document_root: str) -> Tuple[Dict[str, bytes], bool, List[Dict[str, str]]]:
    diagnostics: List[Dict[str, str]] = []
    repository = root.resolve()
    declared = PurePosixPath(document_root)
    if declared.is_absolute() or not declared.parts or ".." in declared.parts:
        raise WorkStateError("document_root must be repository-relative")
    docs = repository.joinpath(*declared.parts)
    if not docs.exists():
        return {}, True, diagnostics
    if docs.is_symlink() or not docs.is_dir():
        return {}, False, [_diagnostic(
            "work_state_document_root_invalid",
            "Document root must be a regular non-symlink directory.", document_root,
        )]
    paths: List[Path] = []
    for fixed in (docs / "key-context-map.md", docs / "works" / "00_key-index.md",
                  docs / "works" / "key-acceptance-events.json"):
        if fixed.exists():
            paths.append(fixed)
    works = docs / "works"
    if works.is_dir() and not works.is_symlink():
        try:
            for candidate in works.rglob("*"):
                relative = _safe_relative(candidate, repository)
                if relative is not None and _source_kind(relative) is not None:
                    paths.append(candidate)
        except OSError as error:
            diagnostics.append(_diagnostic(
                "work_state_discovery_failed", str(error), _safe_relative(works, repository)
            ))
    sources: Dict[str, bytes] = {}
    complete = not diagnostics
    for candidate in sorted(set(paths), key=lambda item: item.as_posix()):
        relative = _safe_relative(candidate, repository)
        if relative is None:
            complete = False
            diagnostics.append(_diagnostic(
                "work_state_source_path_invalid", "Discovered source escapes repository scope."
            ))
            continue
        try:
            state = candidate.lstat()
            if stat.S_ISLNK(state.st_mode) or not stat.S_ISREG(state.st_mode) or state.st_nlink != 1:
                raise OSError("source must be a single-link regular file")
            descriptor = os.open(candidate, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            try:
                raw = os.read(descriptor, state.st_size + 1)
                after = os.fstat(descriptor)
            finally:
                os.close(descriptor)
            if len(raw) != state.st_size or (after.st_dev, after.st_ino, after.st_size) != (
                state.st_dev, state.st_ino, state.st_size
            ):
                raise OSError("source changed during capture")
        except OSError as error:
            complete = False
            diagnostics.append(_diagnostic(
                "work_state_source_unreadable", str(error), relative
            ))
            continue
        sources[relative] = raw
    return sources, complete, diagnostics


def evaluate_repository(
    repository_root: Path, document_root: str = "00_docs", *,
    prerequisite_closures: Any = None,
) -> Dict[str, Any]:
    """Discover repository sources and return one canonical work-state envelope."""
    sources, complete, diagnostics = _discover_sources(
        Path(repository_root), document_root
    )
    return derive_work_state(
        sources, complete=complete, discovery_diagnostics=diagnostics,
        prerequisite_closures=prerequisite_closures,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--document-root", default="00_docs")
    args = parser.parse_args(argv)
    try:
        result = evaluate_repository(args.root, args.document_root)
    except (OSError, WorkStateError, ValueError) as error:
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "diagnostics": [_diagnostic("work_state_execution_failed", str(error))],
            "summary": {"errors": 1, "warnings": 0},
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {"pass": 0, "fail": 1, "error": 2}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
