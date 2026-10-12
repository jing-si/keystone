#!/usr/bin/env python3
"""Prepare native Codex title generation for a Keystone Reader session."""

# keystone: id=key.code.reader.keystone-session-title kind=output_artifact artifact_kind=code refs=key.standard.project.std-keystone-063 key.standard.skill.reader.round-session-focus locator.symbol=handle_user_prompt_submit

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable, Mapping, Optional, Sequence
import uuid


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from work_state_runtime import evaluate_repository, parse_frontmatter  # noqa: E402


REENTRY_MARKER = "[keystone-session-title-ready]"
READER_PROMPT = re.compile(r"^\s*\$keystone-reader(?:\s|$)", re.IGNORECASE)
ROUND_REF = re.compile(r"R\d{3,}(?:-[A-Z]+)?", re.IGNORECASE)
ASSIGNMENT_TERM = re.compile(
    r"진행|시작|계속|전환|착수|수행|처리|작업하|맡|proceed|start|continue|switch|resume|execute",
    re.IGNORECASE,
)
WORK_ORDER_TERM = re.compile(r"작업서|워크\s*오더|work\s*order", re.IGNORECASE)
WORK_AUTHORING_ACTION = re.compile(
    r"(?:생성|작성|수정|개정|보완|변경|업데이트)\s*(?:해|하|할|부터|진행|착수)"
    r"|만들(?:겠|어|어\s*주|겠습니다)"
    r"|\b(?:create|draft|write|edit|revise|update)\b",
    re.IGNORECASE,
)
NEW_ROUND_TERM = re.compile(
    r"(?:신규|새(?:로운)?)\s*(?:하위\s*)?라운드|new\s+(?:child\s+)?round",
    re.IGNORECASE,
)
CHILD_SCOPE_TERM = re.compile(r"하위|child|under", re.IGNORECASE)
TERMINAL_TITLE = re.compile(
    r"^terminal_title\s*=\s*\[[^\]]*['\"]thread-title['\"][^\]]*\]\s*(?:#.*)?$"
)


class PendingSelectionStore:
    """Keep a short-lived multi-Round choice outside the project repository."""

    def __init__(self, directory: Optional[Path] = None):
        self._directory = directory or (
            Path(tempfile.gettempdir()) / "keystone-session-title"
        )

    def _path(self, thread_id: str) -> Path:
        return self._directory / "{}.json".format(str(uuid.UUID(thread_id)))

    def load(self, thread_id: str) -> Optional[Mapping[str, Any]]:
        try:
            value = json.loads(self._path(thread_id).read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, UnicodeError, ValueError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def save(self, thread_id: str, value: Mapping[str, Any]) -> None:
        path = self._path(thread_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(dict(value), ensure_ascii=False), encoding="utf-8"
        )
        os.replace(str(temporary), str(path))

    def clear(self, thread_id: str) -> None:
        try:
            self._path(thread_id).unlink()
        except FileNotFoundError:
            pass


def is_project_opted_in(project_root: Path) -> bool:
    """Recognize the project-local terminal title setting emitted by Init."""
    config_path = project_root / ".codex" / "config.toml"
    try:
        text = config_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeError):
        return False
    in_tui_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_tui_table = stripped == "[tui]"
            continue
        if in_tui_table and TERMINAL_TITLE.fullmatch(stripped) is not None:
            return True
    return False


def _valid_thread_id(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return None


def _round_refs(value: str) -> Sequence[str]:
    return tuple(dict.fromkeys(match.group(0).upper() for match in ROUND_REF.finditer(value)))


def _state(envelope: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    if envelope.get("status") != "pass":
        return None
    value = envelope.get("state")
    return value if isinstance(value, dict) else None


def _active_works(state: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    value = state.get("active_works")
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, dict))


def _round_sort_key(round_ref: str) -> Any:
    match = re.fullmatch(r"R(\d+)(?:-([A-Z]+))?", round_ref)
    if match is None:
        return (sys.maxsize, sys.maxsize)
    suffix = match.group(2)
    suffix_value = 0
    if suffix is not None:
        for character in suffix:
            suffix_value = suffix_value * 26 + ord(character) - ord("A") + 1
    return (int(match.group(1)), suffix_value)


def _round_hierarchy(state: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    hierarchy = state.get("round_hierarchy")
    if not isinstance(hierarchy, list):
        return ()
    return tuple(item for item in hierarchy if isinstance(item, dict))


def _all_round_refs(state: Mapping[str, Any]) -> Sequence[str]:
    values = []
    for parent in _round_hierarchy(state):
        parent_ref = parent.get("round_ref")
        if isinstance(parent_ref, str):
            values.append(parent_ref.upper())
        children = parent.get("child_rounds")
        if isinstance(children, list):
            values.extend(
                str(child["round_ref"]).upper()
                for child in children
                if isinstance(child, dict) and isinstance(child.get("round_ref"), str)
            )
    return tuple(dict.fromkeys(values))


def _excel_suffix_value(suffix: str) -> int:
    value = 0
    for character in suffix:
        value = value * 26 + ord(character) - ord("A") + 1
    return value


def _excel_suffix(value: int) -> str:
    characters = []
    while value > 0:
        value, remainder = divmod(value - 1, 26)
        characters.append(chr(ord("A") + remainder))
    return "".join(reversed(characters))


def _next_parent_round_ref(state: Mapping[str, Any]) -> Optional[str]:
    parent_numbers = []
    for parent in _round_hierarchy(state):
        match = re.fullmatch(r"R(\d+)", str(parent.get("round_ref", "")).upper())
        if match is not None:
            parent_numbers.append(int(match.group(1)))
    if not parent_numbers:
        return "R001"
    next_number = max(parent_numbers) + 1
    return "R{:0{}d}".format(next_number, max(3, len(str(next_number))))


def _next_child_round_ref(
    state: Mapping[str, Any], parent_ref: str
) -> Optional[str]:
    if re.fullmatch(r"R\d{3,}", parent_ref) is None:
        return None
    for parent in _round_hierarchy(state):
        if str(parent.get("round_ref", "")).upper() != parent_ref:
            continue
        suffix_values = []
        children = parent.get("child_rounds")
        if isinstance(children, list):
            prefix = parent_ref + "-"
            for child in children:
                if not isinstance(child, dict):
                    continue
                child_ref = str(child.get("round_ref", "")).upper()
                suffix = child_ref[len(prefix):] if child_ref.startswith(prefix) else ""
                if re.fullmatch(r"[A-Z]+", suffix) is not None:
                    suffix_values.append(_excel_suffix_value(suffix))
        return "{}-{}".format(
            parent_ref, _excel_suffix(max(suffix_values, default=0) + 1)
        )
    return None


def _incomplete_rounds(state: Mapping[str, Any]) -> Sequence[Mapping[str, str]]:
    values = []
    for parent in _round_hierarchy(state):
        parent_ref = parent.get("round_ref")
        entries = [(parent, parent_ref)]
        children = parent.get("child_rounds")
        if isinstance(children, list):
            entries.extend(
                (child, parent_ref) for child in children if isinstance(child, dict)
            )
        for entry, owning_parent_ref in entries:
            round_ref = entry.get("round_ref")
            status = entry.get("status")
            if not isinstance(round_ref, str) or not isinstance(status, str):
                continue
            if status in {"accepted", "cancelled"}:
                continue
            values.append({
                "round_ref": round_ref.upper(),
                "status": status,
                "path": str(entry.get("path") or ""),
                "parent_round_ref": str(owning_parent_ref or round_ref).upper(),
            })
    return tuple(sorted(
        values,
        key=lambda item: _round_sort_key(item["round_ref"]),
    ))


def _work_label(project_root: Path, state: Mapping[str, Any], round_ref: str) -> str:
    for work in _active_works(state):
        if str(work.get("round_ref", "")).upper() != round_ref:
            continue
        raw_path = work.get("path")
        if isinstance(raw_path, str):
            try:
                metadata = parse_frontmatter(
                    (project_root / raw_path).read_text(encoding="utf-8")
                )
            except (FileNotFoundError, OSError, UnicodeError, ValueError):
                metadata = {}
            title = metadata.get("title") if isinstance(metadata, dict) else None
            if isinstance(title, str) and title.strip():
                return title.strip()
        work_ref = work.get("work_ref")
        if isinstance(work_ref, str) and work_ref.strip():
            return work_ref.replace("-", " ")
    return round_ref


def _title_label(project_root: Path, state: Mapping[str, Any], round_ref: str) -> str:
    work_label = _work_label(project_root, state, round_ref)
    if work_label != round_ref:
        return work_label
    for candidate in _incomplete_rounds(state):
        if candidate["round_ref"] == round_ref:
            return _round_label(project_root, state, candidate)
    return round_ref


def _round_label(
    project_root: Path,
    state: Mapping[str, Any],
    candidate: Mapping[str, str],
) -> str:
    round_ref = candidate["round_ref"]
    work_label = _work_label(project_root, state, round_ref)
    if work_label != round_ref:
        return work_label
    raw_path = candidate.get("path")
    if raw_path:
        try:
            text = (project_root / raw_path).read_text(encoding="utf-8")
        except (FileNotFoundError, OSError, UnicodeError):
            text = ""
        metadata = parse_frontmatter(text) if text else {}
        title = metadata.get("title") if isinstance(metadata, dict) else None
        if isinstance(title, str) and title.strip():
            return title.strip()
        heading = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
        if heading is not None:
            value = re.sub(r"^{}\s+".format(re.escape(round_ref)), "", heading.group(1))
            value = re.sub(r"\s+(?:작업서|작업)\s*색인$", "", value)
            if value.strip():
                return value.strip()
    return round_ref


def _selection_reason(
    project_root: Path,
    state: Mapping[str, Any],
    candidates: Sequence[Mapping[str, str]],
) -> str:
    visible_refs = {candidate["round_ref"] for candidate in candidates}
    groups = []
    parent_groups = {}
    group_number = 0
    for candidate in candidates:
        round_ref = candidate["round_ref"]
        parent_ref = candidate.get("parent_round_ref", round_ref)
        status = candidate["status"]
        status_label = (
            "complete / pending · 수용 대기"
            if status == "complete"
            else status
        )
        label = _round_label(project_root, state, candidate)
        if round_ref == parent_ref or parent_ref not in visible_refs:
            group_number += 1
            group = ["│  {}. {} · {} · {}".format(
                group_number, round_ref, status_label, label
            )]
            groups.append(group)
            parent_groups[round_ref] = group
        else:
            parent_groups[parent_ref].append("│     └─ {} · {} · {}".format(
                round_ref, status_label, label
            ))
    lines = [
        "Keystone ready · 미완료 Round {}개".format(len(candidates)),
        "",
        "╭─ Round 선택 ─────────────────────────",
        "│",
    ]
    for index, group in enumerate(groups):
        if index:
            lines.append("│")
        lines.extend(group)
    lines.extend(("│", "╰─ 어느 Round에 집중할까요?"))
    return "\n".join(lines)


def _assigned_round(prompt: str, candidates: Sequence[str], pending: bool) -> Optional[str]:
    selected = []
    assignment_term = "(?:{})".format(ASSIGNMENT_TERM.pattern)
    for round_ref in candidates:
        escaped = re.escape(round_ref)
        round_token = "{}(?![A-Za-z0-9-])".format(escaped)
        exact_selection = re.fullmatch(
            r"\s*{}(?:\s*(?:으로|로|을|를))?\s*(?:하겠습니다|할게요?|진행)?\s*[.!]?\s*".format(round_token),
            prompt,
            re.IGNORECASE,
        )
        nearby = re.search(
            r"(?:{}.{{0,28}}{}|{}.{{0,20}}{})".format(
                round_token, assignment_term, assignment_term, round_token
            ),
            prompt,
            re.IGNORECASE,
        )
        if nearby is not None or (pending and exact_selection is not None):
            selected.append(round_ref)
    return selected[0] if len(selected) == 1 else None


def _has_work_authoring_intent(prompt: str) -> bool:
    has_scope = WORK_ORDER_TERM.search(prompt) is not None
    if not has_scope and NEW_ROUND_TERM.search(prompt) is None:
        return False
    if WORK_AUTHORING_ACTION.search(prompt) is not None:
        return True
    return (
        re.search(r"작업서\s*부터|work\s*order\s*first", prompt, re.IGNORECASE)
        is not None
        and ASSIGNMENT_TERM.search(prompt) is not None
    )


def _child_parent_refs(prompt: str, parent_refs: Sequence[str]) -> Sequence[str]:
    values = []
    for parent_ref in parent_refs:
        escaped = re.escape(parent_ref)
        if re.search(
            r"(?:{}.{{0,24}}(?:{})|(?:{}).{{0,24}}{})".format(
                escaped, CHILD_SCOPE_TERM.pattern, CHILD_SCOPE_TERM.pattern, escaped
            ),
            prompt,
            re.IGNORECASE,
        ) is not None:
            values.append(parent_ref)
    return tuple(values)


def _near_work_order_refs(prompt: str, round_refs: Sequence[str]) -> Sequence[str]:
    values = []
    for round_ref in round_refs:
        escaped = re.escape(round_ref)
        if re.search(
            r"(?:{}.{{0,28}}(?:{})|(?:{}).{{0,28}}{})".format(
                escaped, WORK_ORDER_TERM.pattern, WORK_ORDER_TERM.pattern, escaped
            ),
            prompt,
            re.IGNORECASE,
        ) is not None:
            values.append(round_ref)
    return tuple(values)


def _work_authoring_round(
    prompt: str, state: Mapping[str, Any]
) -> Optional[Mapping[str, Any]]:
    if not _has_work_authoring_intent(prompt):
        return None
    all_refs = tuple(_all_round_refs(state))
    parent_refs = tuple(ref for ref in all_refs if "-" not in ref)
    mentioned_refs = tuple(_round_refs(prompt))
    child_parents = _child_parent_refs(prompt, parent_refs)
    if len(child_parents) == 1:
        next_child = _next_child_round_ref(state, child_parents[0])
        if next_child is not None:
            return {"round_ref": next_child, "provisional": True}
    if len(child_parents) > 1:
        return None

    scoped_refs = _near_work_order_refs(prompt, mentioned_refs)
    if len(scoped_refs) == 1:
        target = scoped_refs[0]
    elif len(mentioned_refs) == 1:
        target = mentioned_refs[0]
    elif mentioned_refs:
        return None
    else:
        target = _next_parent_round_ref(state)
        return (
            {"round_ref": target, "provisional": True}
            if target is not None
            else None
        )

    if target in all_refs:
        return {"round_ref": target, "provisional": False}
    if "-" in target and target.split("-", 1)[0] not in parent_refs:
        return None
    return {"round_ref": target, "provisional": True}


def _title_prompt(
    original_prompt: str, round_ref: str, work_label: Optional[str]
) -> str:
    if work_label is None:
        phrase_instruction = (
            "대표문구는 아래 원래 요청이 어떤 작업인지 사용자의 주 언어로 "
            "5자 이내에 구분되게 요약하세요."
        )
    else:
        phrase_instruction = (
            "대표문구는 작업명 `{}`가 어떤 작업인지 사용자의 주 언어로 "
            "5자 이내에 구분되게 요약하세요."
        ).format(work_label)
    return "\n".join((
        REENTRY_MARKER,
        "이 세션의 제목은 반드시 `{}:{{대표문구}}` 형식으로 생성하세요.".format(round_ref),
        phrase_instruction,
        "위 두 문장은 네이티브 세션 제목 생성용 힌트입니다. 다음 원래 요청을 그대로 수행하세요.",
        original_prompt,
    ))


def queue_current_thread(thread_id: str, message: str, cwd: Path) -> bool:
    """Queue the rewritten first message back into the same Codex thread."""
    codex_bin = shutil.which("codex")
    if codex_bin is None:
        return False
    try:
        completed = subprocess.run(
            [codex_bin, "queue", "--thread", thread_id, "--message", message],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def _queue_result(
    thread_id: str,
    project_root: Path,
    prompt: str,
    selected: str,
    state: Mapping[str, Any],
    queue_message: Callable[[str, str, Path], bool],
    pending_store: Any,
) -> Mapping[str, Any]:
    message = _title_prompt(
        prompt, selected, _title_label(project_root, state, selected)
    )
    if queue_message(thread_id, message, project_root):
        pending_store.clear(thread_id)
        return {
            "decision": "block",
            "reason": "Keystone 세션 제목을 준비했습니다.",
            "suppressOutput": True,
        }
    pending_store.clear(thread_id)
    return {
        "systemMessage": (
            "Keystone 세션 제목 힌트를 적용하지 못했습니다. "
            "원래 Reader 요청을 계속 진행합니다."
        )
    }


def _queue_authoring_result(
    thread_id: str,
    project_root: Path,
    original_prompt: str,
    followup_prompt: Optional[str],
    authoring: Mapping[str, Any],
    queue_message: Callable[[str, str, Path], bool],
    pending_store: Any,
) -> Mapping[str, Any]:
    round_ref = str(authoring["round_ref"])
    provisional = bool(authoring.get("provisional"))
    context_label = "예정 라운드" if provisional else "기존 라운드"
    request_lines = [original_prompt]
    if followup_prompt is not None:
        request_lines.append("후속 요청: {}".format(followup_prompt))
    request_lines.extend((
        "{}: {}".format(context_label, round_ref),
        (
            "이 예정 ref는 source 예약이 아닙니다. Keystone Author는 작업서 write 직전에 "
            "현재 Round hierarchy와 충돌을 다시 확인하세요."
        ) if provisional else "기존 작업서 범위는 해당 exact Round ref를 사용하세요.",
    ))
    message = _title_prompt("\n".join(request_lines), round_ref, None)
    if queue_message(thread_id, message, project_root):
        pending_store.clear(thread_id)
        return {
            "decision": "block",
            "reason": "Keystone 작업서 세션 제목을 준비했습니다.",
            "suppressOutput": True,
        }
    pending_store.clear(thread_id)
    return {
        "systemMessage": (
            "Keystone 작업서 제목 힌트를 적용하지 못했습니다. "
            "원래 Reader 요청을 계속 진행합니다."
        )
    }


def _queue_freeform_result(
    thread_id: str,
    project_root: Path,
    original_prompt: str,
    followup_prompt: str,
    queue_message: Callable[[str, str, Path], bool],
    pending_store: Any,
) -> Mapping[str, Any]:
    message = "\n".join((
        REENTRY_MARKER,
        original_prompt,
        "후속 요청: {}".format(followup_prompt),
    ))
    if queue_message(thread_id, message, project_root):
        pending_store.clear(thread_id)
        return {
            "decision": "block",
            "reason": "Keystone Reader 요청을 준비했습니다.",
            "suppressOutput": True,
        }
    pending_store.clear(thread_id)
    return {
        "systemMessage": "후속 요청을 결합하지 못했습니다. 원래 Reader 요청을 계속 진행합니다."
    }


def handle_user_prompt_submit(
    payload: Mapping[str, Any],
    evaluator: Callable[[Path], Mapping[str, Any]] = evaluate_repository,
    queue_message: Callable[[str, str, Path], bool] = queue_current_thread,
    pending_store: Optional[Any] = None,
) -> Mapping[str, Any]:
    """Handle one UserPromptSubmit payload, failing open on runtime errors."""
    try:
        if payload.get("hook_event_name") != "UserPromptSubmit":
            return {}
        prompt = payload.get("prompt")
        cwd = payload.get("cwd")
        thread_id = _valid_thread_id(payload.get("session_id"))
        if not isinstance(prompt, str) or not isinstance(cwd, str) or thread_id is None:
            return {}
        project_root = Path(cwd).resolve(strict=True)
        store = pending_store or PendingSelectionStore()
        if REENTRY_MARKER in prompt:
            store.clear(thread_id)
            return {}
        if not is_project_opted_in(project_root):
            store.clear(thread_id)
            return {}

        pending = store.load(thread_id)
        if pending is None and READER_PROMPT.match(prompt) is None:
            return {}
        state = _state(evaluator(project_root))
        if state is None:
            return {}
        incomplete = _incomplete_rounds(state)
        candidate_refs = tuple(item["round_ref"] for item in incomplete)

        if pending is not None:
            raw_candidates = pending.get("candidates")
            candidates = tuple(
                candidate.upper()
                for candidate in raw_candidates
                if isinstance(candidate, str)
            ) if isinstance(raw_candidates, list) else candidate_refs
            original = pending.get("original_prompt")
            if not isinstance(original, str):
                original = "$keystone-reader"
            authoring = _work_authoring_round(prompt, state)
            if authoring is not None:
                return _queue_authoring_result(
                    thread_id,
                    project_root,
                    original,
                    prompt,
                    authoring,
                    queue_message,
                    store,
                )
            selected = _assigned_round(prompt, candidates, pending=True)
            if selected is None:
                return _queue_freeform_result(
                    thread_id, project_root, original, prompt, queue_message, store
                )
            return _queue_result(
                thread_id,
                project_root,
                "{}\n선택 라운드: {}".format(original, selected),
                selected,
                state,
                queue_message,
                store,
            )

        authoring = _work_authoring_round(prompt, state)
        if authoring is not None:
            return _queue_authoring_result(
                thread_id,
                project_root,
                prompt,
                None,
                authoring,
                queue_message,
                store,
            )
        selected = _assigned_round(prompt, candidate_refs, pending=False)
        if selected is None:
            if prompt.strip().lower() != "$keystone-reader":
                return {}
            if not incomplete:
                return {}
            store.save(thread_id, {
                "candidates": list(candidate_refs),
                "original_prompt": prompt,
            })
            return {
                "decision": "block",
                "reason": _selection_reason(project_root, state, incomplete),
                "suppressOutput": False,
            }
        return _queue_result(
            thread_id, project_root, prompt, selected, state, queue_message, store
        )
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, RuntimeError):
        return {}


def serialize_hook_output(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), ensure_ascii=False, separators=(",", ":"))


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare native Codex title generation for Keystone Reader."
    )
    parser.add_argument(
        "--hook", action="store_true", help="Read one UserPromptSubmit payload from stdin"
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if not args.hook:
        return 0
    try:
        payload = json.load(sys.stdin)
        result = handle_user_prompt_submit(payload if isinstance(payload, dict) else {})
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        result = {}
    sys.stdout.write(serialize_hook_output(result))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
