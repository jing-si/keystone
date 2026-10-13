#!/usr/bin/env python3
"""One state-first current document (wire v2) and recoverable work-order events."""

import argparse
import base64
from contextlib import contextmanager
from datetime import date, datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from typing import Any, Dict, Iterator, Mapping, Optional, Sequence, Tuple


SCHEMA_VERSION = 2
EXECUTION = frozenset({"planned", "in_progress", "blocked", "complete", "cancelled", "superseded"})
APPROVAL = frozenset({"pending", "accepted", "rejected"})
FINALIZATION = frozenset({None, "pending", "in_progress", "complete", "waived"})
CLOSE_REASONS = frozenset({"complete", "skipped", "cancelled", "superseded"})
ROUND = re.compile(r"R[0-9]{3,}(?:-(?:[A-Z]+|[a-z]))?\Z")
WORK = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
STEP = re.compile(r"S[0-9]{2,}(?:-[A-Z]+)?\Z")
EVENT_PREFIX = "<!-- keystone-work-event "
EVENT = re.compile(r"^<!-- keystone-work-event (.+) -->$", re.MULTILINE)
ENTRY_FIELDS = frozenset({
    "ref", "kind", "parent", "order_path", "execution", "approval", "finalization",
})


class StateError(ValueError):
    """A source, transaction, or concurrency failure with a stable diagnostic code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def encode(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def digest(raw: Optional[bytes]) -> Optional[str]:
    return "sha256:" + hashlib.sha256(raw).hexdigest() if raw is not None else None


def _pairs(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StateError("state_json_duplicate_key", "Duplicate JSON key: " + key)
        result[key] = value
    return result


def decode(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise StateError("state_json_invalid", str(error)) from error


def _relative(value: Any) -> str:
    if (not isinstance(value, str) or not value or "\\" in value
            or ":" in value or "\x00" in value):
        raise StateError("state_path_invalid", "Expected a canonical relative path.")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) != value or value == ".":
        raise StateError("state_path_invalid", "Path must remain inside the repository.")
    return value


def _round_ref(ref: Any) -> str:
    if not isinstance(ref, str) or not ROUND.fullmatch(ref.split("/")[0]):
        raise StateError("state_ref_invalid", "Invalid work reference.")
    parts = ref.split("/")
    if len(parts) > 2 or (len(parts) == 2 and not (WORK.fullmatch(parts[1]) or STEP.fullmatch(parts[1]))):
        raise StateError("state_ref_invalid", "Invalid work or Step reference.")
    return parts[0]


def validate_entry(entry: Any) -> Dict[str, Any]:
    if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
        raise StateError("state_entry_invalid", "Entry fields differ from the v1 contract.")
    value = dict(entry)
    round_ref = _round_ref(value["ref"])
    parts = value["ref"].split("/")
    kind = value["kind"]
    if kind == "round":
        valid = len(parts) == 1 and value["parent"] is None
    elif kind == "work":
        valid = (len(parts) == 2 and bool(WORK.fullmatch(parts[1]))
                 and value["parent"] == round_ref)
    elif kind == "step":
        parent = value["parent"]
        valid = (len(parts) == 2 and bool(STEP.fullmatch(parts[1]))
                 and isinstance(parent, str) and (parent == round_ref or (parent.startswith(round_ref + "/")
                 and bool(WORK.fullmatch(parent[len(round_ref) + 1:])))))
    else:
        valid = False
    if not valid:
        raise StateError("state_identity_invalid", "Kind, ref and parent must agree.")
    _relative(value["order_path"])
    for field, allowed in (("execution", EXECUTION), ("approval", APPROVAL),
                           ("finalization", FINALIZATION)):
        item = value[field]
        if not isinstance(item, (str, type(None))) or item not in allowed:
            raise StateError("state_value_invalid", "Invalid " + field)
    return value


def group_entries(entries: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Encode execution in the group key, with no duplicate per-entry state."""
    groups: Dict[str, Any] = {}
    for entry in sorted(entries, key=lambda item: item["ref"]):
        row = dict(entry)
        execution = row.pop("execution")
        groups.setdefault(execution, []).append(row)
    return {"schema_version": SCHEMA_VERSION, "states": groups}


def validate_document(value: Any) -> Dict[str, Any]:
    """Validate the singleton wire and return normalized entries for consumers."""
    if (not isinstance(value, dict) or set(value) not in ({"schema_version", "states"}, {"schema_version", "states", "review"})
            or type(value["schema_version"]) is not int
            or value["schema_version"] != SCHEMA_VERSION
            or not isinstance(value["states"], dict)):
        raise StateError("state_document_invalid", "Expected a v2 state-first document.")
    if "review" in value:
        _validate_review(value["review"])
    entries = []
    for execution, rows in value["states"].items():
        if execution not in EXECUTION or not isinstance(rows, list):
            raise StateError("state_document_invalid", "Invalid execution-state group.")
        for row in rows:
            if not isinstance(row, dict) or "execution" in row:
                raise StateError("state_entry_invalid", "The group owns execution state.")
            entries.append(validate_entry(dict(row, execution=execution)))
    by_ref = {entry["ref"]: entry for entry in entries}
    if len(by_ref) != len(entries):
        raise StateError("state_duplicate_ref", "Duplicate managed work reference.")
    for entry in entries:
        parent = entry["parent"]
        if entry["kind"] == "round" and "-" in entry["ref"]:
            parent = entry["ref"].split("-")[0]
        if parent is not None and parent not in by_ref:
            raise StateError("state_parent_missing", "Managed parent is missing: " + parent)
    return {"schema_version": SCHEMA_VERSION,
            "items": sorted(entries, key=lambda entry: entry["ref"]),
            **({"review": value["review"]} if "review" in value else {})}


def _review_refs(value: Any) -> None:
    if (not isinstance(value, list) or any(not isinstance(ref, str) or not ROUND.fullmatch(ref)
                                          for ref in value) or len(set(value)) != len(value)):
        raise StateError("review_refs_invalid", "Expected unique Round references.")


def _validate_review(value: Any) -> None:
    fields = {"mode", "closed_list", "full_check_wait_for", "closed_tokens", "wait_tokens"}
    if (not isinstance(value, dict) or set(value) != fields or not isinstance(value["mode"], str)
            or value["mode"] not in {"general", "sprint"}):
        raise StateError("review_state_invalid", "Invalid review configuration.")
    for field, tokens in (("closed_list", "closed_tokens"), ("full_check_wait_for", "wait_tokens")):
        _review_refs(value[field])
        _review_tokens(value[tokens])
        if set(value[tokens]) != set(value[field]):
            raise StateError("review_state_invalid", "Occurrence tokens must match the list.")


def _review_tokens(value: Any) -> None:
    if (not isinstance(value, dict)
            or any(not isinstance(ref, str) or not ROUND.fullmatch(ref)
                   or not isinstance(token, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", token)
                   for ref, token in value.items())):
        raise StateError("review_state_invalid", "Invalid occurrence tokens.")


def _validate_review_ticket(ticket: Mapping[str, Any]) -> None:
    _review_tokens(ticket.get("closed_tokens"))
    _review_tokens(ticket.get("wait_tokens"))
    if not isinstance(ticket.get("commit"), str) or not re.fullmatch(
            r"[a-f0-9]{40}|[a-f0-9]{64}", ticket["commit"]):
        raise StateError("review_commit_invalid", "Invalid snapshot commit.")
    sprint = ticket.get("sprint")
    if sprint is not None:
        if (not isinstance(sprint, dict) or set(sprint) != {"ref", "order_path", "event_count", "history_digest"}
                or not isinstance(sprint["ref"], str) or not ROUND.fullmatch(sprint["ref"])
                or "-" in sprint["ref"] or type(sprint["event_count"]) is not int
                or sprint["event_count"] < 1):
            raise StateError("review_sprint_invalid", "Invalid sprint ticket.")
        _relative(sprint["order_path"])


def review_advice(review: Optional[Mapping[str, Any]], *, closed_event: bool) -> Dict[str, Any]:
    """Only a fresh Round Closed event can generate an automatic prompt."""
    if review is None:
        return {"prompt": False, "reason": "not_configured"}
    waiting = review["full_check_wait_for"]
    ready = set(waiting) <= set(review["closed_list"])
    count = len(review["closed_list"])
    due = ready if waiting else review["mode"] == "general" and count > 0 and count % 5 == 0
    return {"prompt": bool(closed_event and due),
            "reason": "waiting" if waiting and not ready else "wait_satisfied" if waiting else "periodic"}


def _validate_time(value: Any) -> None:
    if not isinstance(value, str):
        raise StateError("state_event_time_invalid", "Event date is required.")
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            date.fromisoformat(value)
        else:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("Timestamp must include a timezone.")
    except ValueError as error:
        raise StateError("state_event_time_invalid", str(error)) from error


def events(raw: bytes, ref: str) -> Tuple[Dict[str, Any], ...]:
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise StateError("state_order_encoding", str(error)) from error
    records = []
    # Only full standalone comments are events, never quoted/indented examples.
    fenced = False
    fence_char = ""
    fence_length = 0
    for line in text.splitlines():
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            token, tail = fence.groups()
            if not fenced:
                fenced, fence_char, fence_length = True, token[0], len(token)
            elif token[0] == fence_char and len(token) >= fence_length and not tail.strip():
                fenced = False
            continue
        if fenced or not line.startswith(EVENT_PREFIX):
            continue
        match = EVENT.fullmatch(line)
        if match is None:
            raise StateError("state_event_invalid", "Malformed work event comment.")
        item = decode(match.group(1).encode("utf-8"))
        if (not isinstance(item, dict) or not isinstance(item.get("event"), str)
                or item["event"] not in {"created", "updated", "closed", "reopened"}
                or not isinstance(item.get("note"), str) or not item["note"].strip()):
            raise StateError("state_event_invalid", "Invalid work event.")
        _round_ref(item.get("ref"))
        _validate_time(item.get("at"))
        if "result" in item or item["event"] == "updated":
            validate_entry(item.get("result"))
            if item["result"]["ref"] != item["ref"]:
                raise StateError("state_event_invalid", "Event result ref mismatch.")
        if item["event"] == "updated":
            before = validate_entry(item.get("before"))
            if (before == item["result"] or any(before[key] != item["result"][key]
                    for key in ("ref", "kind", "parent", "order_path"))):
                raise StateError("state_event_invalid", "Invalid state-change history.")
        if item["event"] == "closed":
            if not isinstance(item.get("reason"), str) or item["reason"] not in CLOSE_REASONS:
                raise StateError("state_event_invalid", "Invalid closing reason.")
            validate_entry(item.get("result"))
            if item["result"]["ref"] != item["ref"]:
                raise StateError("state_event_invalid", "Event result ref mismatch.")
            _validate_close(item["result"], item["reason"])
        if item["ref"] == ref:
            previous = records[-1]["event"] if records else None
            expected = {None: {"created"}, "created": {"updated", "closed"},
                        "updated": {"updated", "closed"}, "closed": {"reopened"},
                        "reopened": {"updated", "closed"}}
            if item["event"] not in expected[previous]:
                raise StateError("state_event_sequence_invalid", "Invalid management event order.")
            if (item["event"] == "updated" and records[-1].get("result") is not None
                    and item["before"] != records[-1]["result"]):
                raise StateError("state_event_conflict", "History state snapshots disagree.")
            records.append(item)
    return tuple(records)


class StateStore:
    """One repository's current facade. Reads never write or scan work history."""

    def __init__(self, root: Path, document_root: str = "00_docs"):
        self.root = Path(root).resolve()
        self.document_root = _relative(document_root)
        self.state_path = self.document_root + "/state"
        self.source_path = self.state_path + "/current.json"
        self.lock_path = self.state_path + "/.writer.lock"
        self.pending_path = self.state_path + "/.pending.json"

    def path(self, relative: str) -> Path:
        _relative(relative)
        current = self.root
        for part in PurePosixPath(relative).parts:
            current = current / part
            if current.is_symlink():
                raise StateError("state_path_unsafe", "Symlink in source path: " + relative)
        if current.exists():
            info = current.stat()
            if not stat.S_ISDIR(info.st_mode) and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
                raise StateError("state_path_unsafe", "Expected a single-link regular file.")
        return current

    def read(self, relative: str) -> Optional[bytes]:
        path = self.path(relative)
        try:
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        except FileNotFoundError:
            return None
        with os.fdopen(descriptor, "rb") as source:
            before = os.fstat(source.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise StateError("state_path_unsafe", "Expected a single-link regular file.")
            raw = source.read()
            after = os.fstat(source.fileno())
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise StateError("state_source_changed", "Source changed during capture.")
        return raw

    def _idle(self) -> None:
        if self.path(self.lock_path).exists():
            raise StateError("state_busy", "Another state writer owns the lock.")
        if self.path(self.pending_path).exists():
            raise StateError("state_recovery_required", "A partially applied transition needs recovery.")

    def _document(self) -> Tuple[Dict[str, Any], Optional[bytes]]:
        legacy = self.path(self.state_path + "/rounds")
        if legacy.exists() and any(legacy.iterdir()):
            raise StateError("state_layout_legacy", "Convert per-Round v1 data before using v2.")
        raw = self.read(self.source_path)
        value = (validate_document(decode(raw)) if raw is not None else
                 {"schema_version": SCHEMA_VERSION, "items": []})
        return value, raw

    def current(self) -> Dict[str, Any]:
        self._idle()
        value, raw = self._document()
        if self.read(self.source_path) != raw:
            raise StateError("state_source_changed", "Current state changed during capture.")
        self._idle()
        return dict(value, states=group_entries(value["items"])["states"],
                    sources={self.source_path: digest(raw)} if raw is not None else {})

    def inspect(self, ref: str, order_path: str) -> Dict[str, Any]:
        self._idle()
        _round_ref(ref)
        value, raw = self._document()
        entry = next((item for item in value["items"] if item["ref"] == ref), None)
        if entry is not None and entry["order_path"] != order_path:
            raise StateError("state_order_mismatch", "Wrong work-order path for this reference.")
        order = self.read(_relative(order_path))
        history = events(order, ref) if order is not None else ()
        last = history[-1] if history else None
        if entry is not None:
            result = "managed" if last and last["event"] != "closed" else "conflict"
            if last and "result" in last and last["result"] != entry:
                result = "conflict"
        elif last and last["event"] == "closed":
            result = "closed"
        else:
            result = "missing" if last else "unknown"
        self._idle()
        if self.read(self.source_path) != raw or self.read(order_path) != order:
            raise StateError("state_source_changed", "Sources changed during inspection.")
        return {"ref": ref, "status": result, "entry": entry, "last_event": last,
                "expected_digest": digest(raw)}

    @contextmanager
    def _writer(self, *, recovering: bool = False) -> Iterator[None]:
        directory = self.path(self.state_path)
        directory.mkdir(parents=True, exist_ok=True)
        lock = self.path(self.lock_path)
        try:
            descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as error:
            raise StateError("state_busy", "Another state writer owns the lock.") from error
        try:
            with os.fdopen(descriptor, "w") as stream:
                stream.write(str(os.getpid()))
            if not recovering and self.path(self.pending_path).exists():
                raise StateError("state_recovery_required", "Recover the pending transition first.")
            yield
        finally:
            lock.unlink()

    def _replace(self, relative: str, raw: Optional[bytes]) -> None:
        path = self.path(relative)
        if raw is None:
            if path.exists():
                path.unlink()
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".state-write-", dir=str(path.parent))
        try:
            with os.fdopen(descriptor, "wb") as stream:
                if path.exists():
                    os.fchmod(stream.fileno(), stat.S_IMODE(path.stat().st_mode))
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def _transaction(self, changes: Sequence[Tuple[str, Optional[bytes], Optional[bytes]]]) -> None:
        for path, before, _after in changes:
            if self.read(path) != before:
                raise StateError("state_stale", "Source changed before transaction: " + path)
        packed = [{"path": path, "before": _pack(before), "after": _pack(after)}
                  for path, before, after in changes]
        self._replace(self.pending_path, encode({"schema_version": 1, "changes": packed}))
        for path, before, after in changes:
            if self.read(path) != before:
                raise StateError("state_recovery_conflict", "Source changed during transaction: " + path)
            self._replace(path, after)
        self._replace(self.pending_path, None)

    def _close_dependencies(self, item: Mapping[str, Any], reason: Optional[str]) -> Dict[str, Any]:
        """Use the packaged execution policy before a completed managed Work leaves the tree."""
        marker = self.path(self.state_path + "/manifest.json")
        if reason != "complete" or item["kind"] not in {"round", "work", "step"} or not marker.exists():
            return {}
        path = Path(__file__).with_name("work_state_runtime.py")
        name = "keystone_close_work_state_runtime"
        spec = importlib.util.spec_from_file_location(name, path)
        runtime = importlib.util.module_from_spec(spec)
        sys.modules[name] = runtime
        spec.loader.exec_module(runtime)
        result = runtime.evaluate_repository(self.root, self.document_root)
        if result["status"] != "pass":
            raise StateError("state_close_dependency_invalid", "Resolve Work State diagnostics before closure.")
        if any(gate["blocking"] and (
                (gate["source_ref"] == item["ref"] and gate["work_completion"])
                or (item["kind"] == "step" and gate["source_ref"] == item["parent"]
                    and item["ref"].split("/")[1] in gate["steps"]))
               for gate in result["state"]["dependency_evaluations"]):
            raise StateError("state_close_dependency_blocked", "Required work-completion dependency is unresolved.")
        return {source["path"]: source["digest"] for source in result["sources"]}

    def change(self, action: str, entry: Mapping[str, Any], *, expected_digest: Optional[str],
               at: Optional[str] = None, note: str = "", reason: Optional[str] = None) -> Dict[str, Any]:
        """Create/update/reopen an entry or close it; caller supplies acceptance evidence."""
        item = validate_entry(entry)
        ref = item["ref"]
        if action not in {"create", "update", "close", "reopen"}:
            raise StateError("state_action_invalid", "Unknown state action.")
        _validate_time(at)
        if not isinstance(note, str) or not note.strip():
            raise StateError("state_event_note_required", "Explain this management event.")
        dependencies = self._close_dependencies(item, reason) if action == "close" else {}
        with self._writer():
            if any(digest(self.read(path)) != expected for path, expected in dependencies.items()):
                raise StateError("state_stale", "Dependency evidence changed before closure.")
            document, before = self._document()
            if digest(before) != expected_digest:
                raise StateError("state_stale", "Current state digest differs from expected_digest.")
            items = {value["ref"]: value for value in document["items"]}
            existing = items.get(ref)
            if (action in {"create", "reopen"}) != (existing is None):
                raise StateError("state_action_conflict", "Action disagrees with managed membership.")
            if existing and any(existing[key] != item[key]
                                for key in ("kind", "parent", "order_path")):
                raise StateError("state_identity_change", "State updates cannot move work identity.")
            if action == "close":
                if item != existing:
                    raise StateError("state_close_changed", "Close must use the current state.")
                _validate_close(item, reason)
                if any(value["parent"] == ref for value in items.values()):
                    raise StateError("state_children_managed", "Close managed children first.")
                if item["kind"] == "round" and any(
                        value["kind"] == "round" and value["ref"].startswith(ref + "-")
                        for value in items.values()):
                    raise StateError("state_children_managed", "Close child Rounds first.")
                del items[ref]
            else:
                items[ref] = item
            after_value = group_entries(list(items.values()))
            if "review" in document:
                after_value["review"] = document["review"]
            path = item["order_path"]
            if not path.startswith(self.document_root + "/works/") or not path.endswith(".md"):
                raise StateError("state_order_path_invalid", "Events must belong to a work-order Markdown file.")
            order = self.read(path)
            if order is None:
                raise StateError("state_order_missing", "Work order must exist before registration.")
            history = events(order, ref)
            last = history[-1]["event"] if history else None
            if ((action == "create" and last is not None)
                    or (action == "reopen" and last != "closed")
                    or (action in {"close", "update"}
                        and last not in {"created", "reopened", "updated"})):
                raise StateError("state_event_conflict", "Action disagrees with recorded work events.")
            if (existing is not None and history and "result" in history[-1]
                    and history[-1]["result"] != existing):
                raise StateError("state_event_conflict", "Current state disagrees with its last event.")
            if action == "update" and existing == item:
                return review_advice(document.get("review"), closed_event=False)
            event = {"ref": ref, "event": {"create": "created", "close": "closed",
                     "reopen": "reopened", "update": "updated"}[action],
                     "at": at, "note": note, "result": item}
            if action == "close":
                event["reason"] = reason
            if action == "update":
                event["before"] = existing
            serialized = json.dumps(event, ensure_ascii=False, sort_keys=True)
            serialized = serialized.replace("<", "\\u003c").replace(">", "\\u003e")
            label = event["event"] + ((":" + reason) if action == "close" else "")
            if action == "update":
                label += " · " + ", ".join(
                    key + ": " + str(existing[key]) + " → " + str(item[key])
                    for key in ("execution", "approval", "finalization")
                    if existing[key] != item[key])
            visible_note = " ".join(note.splitlines())
            addition = ("\n\n- " + str(at) + " · " + ref + " · " + label + " — "
                        + visible_note + "\n" + EVENT_PREFIX + serialized + " -->\n").encode("utf-8")
            if item["kind"] == "round" and "review" in after_value:
                review = after_value["review"]
                if action == "close":
                    if ref not in review["closed_list"]:
                        review["closed_list"].append(ref)
                    review["closed_tokens"][ref] = digest(order + addition)
                elif action == "reopen":
                    review["closed_list"] = [key for key in review["closed_list"] if key != ref]
                    review["closed_tokens"].pop(ref, None)
            validate_document(after_value)
            after = encode(after_value)
            changes = [(path, order, order + addition), (self.source_path, before, after)]
            self._transaction(changes)
            return review_advice(after_value.get("review"),
                                 closed_event=action == "close" and item["kind"] == "round")

    def review(self, action: str, payload: Mapping[str, Any], *,
               expected_digest: Optional[str]) -> Dict[str, Any]:
        """Apply explicit review decisions; semantic verification remains the caller's job."""
        if not isinstance(payload, dict):
            raise StateError("review_payload_invalid", "Expected a review payload object.")
        with self._writer():
            document, before = self._document()
            if digest(before) != expected_digest:
                raise StateError("state_stale", "Review state changed; capture the current file again.")
            review = document.get("review")
            if action == "configure":
                mode = payload.get("mode")
                if not isinstance(mode, str) or mode not in {"general", "sprint"}:
                    raise StateError("review_mode_invalid", "Choose general or sprint explicitly.")
                review = dict(review or {"closed_list": [], "full_check_wait_for": [],
                                        "closed_tokens": {}, "wait_tokens": {}}, mode=mode)
            elif review is None:
                raise StateError("review_not_configured", "Choose the project review mode first.")
            elif action == "defer":
                refs = payload.get("rounds")
                _review_refs(refs)
                if (not refs or not isinstance(payload.get("reason"), str)
                        or not payload["reason"].strip()):
                    raise StateError("review_wait_invalid", "Name blocking Rounds and explain deferral.")
                if payload.get("sprint_round") in refs:
                    raise StateError("review_self_wait", "A sprint cannot wait for its own closure.")
                known = {item["ref"] for item in document["items"] if item["kind"] == "round"}
                if not set(refs) <= known | set(review["closed_list"]):
                    raise StateError("review_wait_unknown", "Wait only for known managed or closed Rounds.")
                for ref in refs:
                    if ref not in review["full_check_wait_for"]:
                        review["full_check_wait_for"].append(ref)
                    review["wait_tokens"][ref] = digest(encode([before.hex() if before else "", ref]))
            elif action == "finish":
                ticket = payload.get("ticket")
                if (not isinstance(ticket, dict) or ticket.get("document_root") != self.document_root
                        or ticket.get("root") != str(self.root)
                        or payload.get("outcome") != "complete"
                        or payload.get("results_applied") is not True):
                    raise StateError("review_incomplete", "Complete review and apply/record results first.")
                _validate_review_ticket(ticket)
                reviewed = ticket["closed_tokens"]
                sprint = ticket.get("sprint")
                if sprint:
                    ref, path = sprint["ref"], sprint["order_path"]
                    raw = self.read(path)
                    if raw is None:
                        raise StateError("review_sprint_changed", "Sprint order is unavailable.")
                    history = events(raw, ref)
                    count = sprint["event_count"]
                    if (len(history) <= count or digest(encode(history[:count])) != sprint["history_digest"]
                            or history[-1]["event"] != "closed"
                            or any(event["event"] != "updated" for event in history[count:-1])
                            or ref not in review["closed_tokens"]):
                        raise StateError("review_sprint_changed", "Sprint was reopened or did not close after review.")
                    reviewed = dict(reviewed, **{ref: review["closed_tokens"][ref]})
                removable = {ref for ref, token in reviewed.items()
                             if review["closed_tokens"].get(ref) == token}
                # A newly registered wait must retain its closed evidence as well.
                removable -= {ref for ref in review["full_check_wait_for"]
                              if review["wait_tokens"].get(ref) != ticket["wait_tokens"].get(ref)}
                # Retain waiting conditions if a reviewed closure was replaced or is not closed yet.
                for ref, token in ticket["wait_tokens"].items():
                    if review["wait_tokens"].get(ref) == token and ref in removable:
                        review["full_check_wait_for"].remove(ref)
                        del review["wait_tokens"][ref]
                review["closed_list"] = [ref for ref in review["closed_list"] if ref not in removable]
                review["closed_tokens"] = {ref: token for ref, token in review["closed_tokens"].items()
                                           if ref not in removable}
            else:
                raise StateError("review_action_invalid", "Unknown review action.")
            _validate_review(review)
            after_value = group_entries(document["items"])
            after_value["review"] = review
            after = encode(after_value)
            self._transaction([(self.source_path, before, after)])
            return {"review": review, "expected_digest": digest(after)}

    def review_ticket(self, commit: str, *, sprint_round: Optional[str] = None) -> Dict[str, Any]:
        """Capture occurrences from this snapshot; never marks a review as completed."""
        if not isinstance(commit, str) or not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", commit):
            raise StateError("review_commit_invalid", "Provide the full snapshot commit hash.")
        current = self.current()
        review = current.get("review")
        if review is None:
            raise StateError("review_not_configured", "Choose the project review mode first.")
        if not set(review["full_check_wait_for"]) <= set(review["closed_list"]):
            raise StateError("review_waiting", "Blocking Rounds are not closed yet.")
        ticket = {"root": str(self.root), "document_root": self.document_root, "commit": commit,
                  "closed_tokens": dict(review["closed_tokens"]),
                  "wait_tokens": dict(review["wait_tokens"])}
        if sprint_round is not None:
            item = next((item for item in current["items"]
                         if item["ref"] == sprint_round and item["kind"] == "round"), None)
            if item is None or "-" in sprint_round or review["mode"] != "sprint":
                raise StateError("review_sprint_invalid", "Select an open top-level sprint Round.")
            raw = self.read(item["order_path"])
            history = events(raw, sprint_round) if raw is not None else ()
            if not history or history[-1]["event"] == "closed":
                raise StateError("review_sprint_invalid", "Sprint history does not match open state.")
            ticket["sprint"] = {"ref": sprint_round, "order_path": item["order_path"],
                                "event_count": len(history), "history_digest": digest(encode(history))}
        if self.current() != current:
            raise StateError("state_stale", "State changed while capturing review scope.")
        return ticket

    def recover(self) -> bool:
        """Finish an interrupted write only if all targets still match before or after."""
        with self._writer(recovering=True):
            raw = self.read(self.pending_path)
            if raw is None:
                return False
            value = decode(raw)
            if (not isinstance(value, dict) or set(value) != {"schema_version", "changes"}
                    or type(value["schema_version"]) is not int or value["schema_version"] != 1
                    or not isinstance(value["changes"], list) or not 1 <= len(value["changes"]) <= 2):
                raise StateError("state_transaction_invalid", "Invalid pending transaction.")
            changes = []
            for change in value["changes"]:
                if not isinstance(change, dict) or set(change) != {"path", "before", "after"}:
                    raise StateError("state_transaction_invalid", "Invalid pending change.")
                path = _relative(change["path"])
                is_state = path == self.source_path
                is_order = path.startswith(self.document_root + "/works/") and path.endswith(".md")
                if not is_state and not is_order:
                    raise StateError("state_transaction_invalid", "Pending target is outside state/work scope.")
                before, after = _unpack(change["before"]), _unpack(change["after"])
                if is_state:
                    if after is None:
                        raise StateError("state_transaction_invalid", "Current file must remain present.")
                    validate_document(decode(after))
                if is_order and (before is None or after is None or not after.startswith(before)):
                    raise StateError("state_transaction_invalid", "Work history must be append-only.")
                if self.read(path) not in (before, after):
                    raise StateError("state_recovery_conflict", "Edited transaction target: " + path)
                changes.append((path, before, after))
            if len({path for path, _, _ in changes}) != len(changes):
                raise StateError("state_transaction_invalid", "Duplicate pending target.")
            for path, before, after in changes:
                if self.read(path) not in (before, after):
                    raise StateError("state_recovery_conflict", "Target changed during recovery.")
                self._replace(path, after)
            self._replace(self.pending_path, None)
            return True


def _pack(raw: Optional[bytes]) -> Optional[str]:
    return base64.b64encode(raw).decode("ascii") if raw is not None else None


def _unpack(value: Any) -> Optional[bytes]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise StateError("state_transaction_invalid", "Invalid transaction bytes.")
    try:
        return base64.b64decode(value, validate=True)
    except ValueError as error:
        raise StateError("state_transaction_invalid", "Invalid transaction encoding.") from error


def _validate_close(item: Mapping[str, Any], reason: Any) -> None:
    if not isinstance(reason, str) or reason not in CLOSE_REASONS:
        raise StateError("state_close_reason_invalid", "Unknown closure reason.")
    if item["finalization"] not in {None, "complete", "waived"}:
        raise StateError("state_close_unfinished", "Finalization still needs management.")
    if reason == "complete" and (item["execution"] != "complete" or item["approval"] != "accepted"):
        raise StateError("state_close_unfinished", "Completion requires finished work and acceptance.")
    if reason in {"cancelled", "superseded"} and item["execution"] != reason:
        raise StateError("state_close_unfinished", "Execution does not match the closing reason.")


def work_state_projection(store: StateStore, *,
                          current: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Expose only managed work in a v6 Work State view, without loading old work orders."""
    current = store.current() if current is None else current
    items = current["items"]
    rounds = [item for item in items if item["kind"] == "round"]
    by_ref = {item["ref"]: item for item in items}
    active = {item["ref"] for item in items if item["execution"] in {"in_progress", "blocked"}}
    active_rounds = sorted({_round_ref(ref).split("-")[0] for ref in active})
    active_children = sorted({_round_ref(ref) for ref in active if "-" in _round_ref(ref)})
    active_steps = sorted(ref for ref in active if by_ref[ref]["kind"] == "step")
    active_works = []
    for item in items:
        direct_round = (item["kind"] == "round" and any(
            child["kind"] == "step" and child["parent"] == item["ref"] for child in items))
        if item["kind"] != "work" and not direct_round:
            continue
        steps = [child["ref"] for child in items if child["parent"] == item["ref"]
                 and child["ref"] in active]
        if item["ref"] not in active and not steps:
            continue
        round_ref = _round_ref(item["ref"])
        active_works.append({
            "work_ref": item["ref"].split("/", 1)[1] if "/" in item["ref"] else None,
            "execution_ref": item["ref"], "round_ref": round_ref,
            "parent_round_ref": round_ref.split("-")[0], "path": item["order_path"],
            "status": item["execution"], "active_step_refs": sorted(steps),
            "active_step_resolution": "resolved", "unresolved_reason": None,
            "active_step_candidates": [{"step_ref": ref, "path": by_ref[ref]["order_path"],
                                        "work_status": by_ref[ref]["execution"]} for ref in sorted(steps)],
            "state_source": {"mode": "managed_state", "path": store.source_path},
        })
    def round_view(item):
        related_active = any(_round_ref(ref) == item["ref"] for ref in active)
        return {"round_ref": item["ref"], "path": item["order_path"], "management": "open",
                "status": "active" if related_active else item["execution"],
                "approval": item["approval"], "finalization": item["finalization"]}
    hierarchy = []
    for item in rounds:
        if "-" in item["ref"]:
            continue
        children = [round_view(child) for child in rounds if child["ref"].startswith(item["ref"] + "-")]
        hierarchy.append(dict(round_view(item), child_rounds=children,
                              unresolved_child_rounds=[], undeclared_child_rounds=[]))
    sources = [{"path": path, "digest": token} for path, token in sorted(current["sources"].items())]
    generation = {"complete": True, "source_count": len(sources),
                  "source_generation": digest(encode(sources)),
                  "path_set_digest": digest(encode([item["path"] for item in sources])),
                  "snapshot_digest": digest(encode(current))}
    state = {"schema_version": 6, "mode": "managed_state",
             "initialization": "initialized" if store.path(store.state_path).exists() else "uninitialized",
             "managed_items": items, "status_groups": group_entries(items)["states"],
             "review": current.get("review"),
             "active_rounds": active_rounds,
             "active_round": active_rounds[0] if len(active_rounds) == 1 else None,
             "open_rounds": sorted(item["ref"] for item in rounds),
             "active_child_rounds": active_children,
             "round_hierarchy": sorted(hierarchy, key=lambda item: item["round_ref"]),
             "active_steps": active_steps, "active_works": active_works,
             "accepted_rounds": [], "historical_acceptance": {"status": "not_loaded"},
             "dependency_evaluations": [], "dependency_coverage": "not_evaluated",
             "execution_ready": False,
             "finalization_gates": [], "pointer_claims": [], "prerequisite_closures": [],
             "early_work": []}
    return {"schema_version": 1, "status": "pass", "state": state, "generation": generation,
            "result_digest": digest(encode({"state": state, "generation": generation})),
            "diagnostics": [], "summary": {"errors": 0, "warnings": 0}}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--document-root", default="00_docs")
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("list")
    inspect_parser = commands.add_parser("inspect")
    inspect_parser.add_argument("--ref", required=True)
    inspect_parser.add_argument("--order-path", required=True)
    commands.add_parser("recover")
    review_parser = commands.add_parser("review")
    review_parser.add_argument("--operation", choices=("configure", "defer", "finish"), required=True)
    review_parser.add_argument("--payload-json", type=Path, required=True)
    review_parser.add_argument("--expected-digest", required=True)
    ticket_parser = commands.add_parser("review-ticket")
    ticket_parser.add_argument("--commit", required=True)
    ticket_parser.add_argument("--sprint-round")
    for name in ("create", "update", "close", "reopen"):
        command = commands.add_parser(name)
        command.add_argument("--entry-json", required=True, type=Path)
        command.add_argument("--expected-digest", required=True, help="SHA-256 or 'none' for no file")
        command.add_argument("--at", required=True)
        command.add_argument("--note", required=True)
        if name == "close":
            command.add_argument("--reason", choices=sorted(CLOSE_REASONS), required=True)
    args = parser.parse_args(argv)
    try:
        store = StateStore(args.root, args.document_root)
        if args.action == "list":
            result = store.current()
        elif args.action == "inspect":
            result = store.inspect(args.ref, args.order_path)
        elif args.action == "review":
            result = store.review(args.operation, decode(args.payload_json.read_bytes()),
                                  expected_digest=None if args.expected_digest == "none" else args.expected_digest)
        elif args.action == "review-ticket":
            result = store.review_ticket(args.commit, sprint_round=args.sprint_round)
        elif args.action == "recover":
            result = {"recovered": store.recover()}
        else:
            entry = decode(args.entry_json.read_bytes())
            advice = store.change(args.action, entry, expected_digest=(None if args.expected_digest == "none"
                         else args.expected_digest), at=getattr(args, "at", None),
                         note=getattr(args, "note", ""), reason=getattr(args, "reason", None))
            result = dict(store.current(), review_advice=advice)
        output = {"schema_version": 1, "status": "pass", "result": result,
                  "diagnostics": [], "summary": {"errors": 0, "warnings": 0}}
        code = 0
    except (StateError, OSError) as error:
        output = {"schema_version": 1, "status": "fail",
                  "diagnostics": [{"severity": "error", "code": getattr(error, "code", "state_io_error"),
                                   "message": str(error)}], "summary": {"errors": 1, "warnings": 0}}
        code = 1
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
