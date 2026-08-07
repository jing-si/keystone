"""Deterministic executable surface-patch replay."""

import hashlib
import re
from typing import List


PATCH_FORMATS = frozenset({"unified_diff", "full_replacement"})
_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def replay_patch(baseline: bytes, patch_format: str, patch_body: str) -> bytes:
    """Apply one declared patch body to exact baseline bytes or raise ValueError."""
    if patch_format == "full_replacement":
        return patch_body.encode("utf-8")
    if patch_format != "unified_diff":
        raise ValueError("unsupported patch format")
    try:
        original = baseline.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise ValueError("unified_diff baseline must be UTF-8") from error
    lines = patch_body.splitlines(keepends=True)
    index = 0
    while index < len(lines) and not lines[index].startswith("@@ "):
        index += 1
    output: List[str] = []
    original_index = 0
    saw_hunk = False
    while index < len(lines):
        match = _HUNK.match(lines[index])
        if not match:
            raise ValueError("unified_diff hunk header is invalid")
        saw_hunk = True
        old_line = int(match.group(1))
        expected_old = int(match.group(2) or "1")
        expected_new = int(match.group(4) or "1")
        if old_line == 0:
            if expected_old != 0:
                raise ValueError("unified_diff zero start requires zero old lines")
            old_start = 0
        else:
            old_start = old_line - 1
        if old_start < original_index or old_start > len(original):
            raise ValueError("unified_diff hunk range is invalid")
        output.extend(original[original_index:old_start])
        original_index = old_start
        observed_old = 0
        observed_new = 0
        index += 1
        while index < len(lines) and not lines[index].startswith("@@ "):
            line = lines[index]
            if line.startswith("\\ No newline at end of file"):
                index += 1
                continue
            if not line or line[0] not in {" ", "+", "-"}:
                raise ValueError("unified_diff hunk line is invalid")
            body = line[1:]
            if line[0] in {" ", "-"}:
                if original_index >= len(original) or original[original_index] != body:
                    raise ValueError("unified_diff context does not match baseline")
                if line[0] == " ":
                    output.append(body)
                original_index += 1
                observed_old += 1
            else:
                output.append(body)
            if line[0] in {" ", "+"}:
                observed_new += 1
            index += 1
        if observed_old != expected_old or observed_new != expected_new:
            raise ValueError("unified_diff hunk counts do not match body")
    if not saw_hunk:
        raise ValueError("unified_diff requires at least one hunk")
    output.extend(original[original_index:])
    return "".join(output).encode("utf-8")
