"""Pure source-reading helpers for the finalization validator."""

import re
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Tuple


STEP_REF_PATTERN = r"R\d+/S\d+(?:-[A-Z0-9]+)*"


def diagnostic(code: str, message: str,
               path: Optional[str] = None) -> Dict[str, str]:
    item = {"severity": "error", "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def resolve_scoped_path(root: Path,
                        value: Any) -> Tuple[Optional[Path], Optional[str]]:
    if not isinstance(value, str) or not value.strip():
        return None, "missing"
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        return None, "outside"
    if (
        "\\" in value
        or relative.as_posix() != value
        or any(part in {"", "."} for part in relative.parts)
    ):
        return None, "noncanonical"
    root = root.resolve()
    candidate = root.joinpath(*relative.parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, "outside"
    return candidate, None


def read_scoped_file(root: Path, value: Any) -> Tuple[
        Optional[str], Optional[str], Optional[str]]:
    path, path_error = resolve_scoped_path(root, value)
    if path_error:
        return None, path_error, None
    if path is None or not path.is_file():
        return None, "unavailable", None
    try:
        return path.read_text(encoding="utf-8"), None, str(value)
    except (OSError, UnicodeError):
        return None, "unreadable", str(value)


def scalar_from_text(content: str, field: str) -> Optional[str]:
    """Read a scalar from frontmatter, or from a standalone mapping fixture."""
    frontmatter = frontmatter_from_text(content)
    source = frontmatter if frontmatter is not None else content
    matches = re.findall(
        rf"(?m)^{re.escape(field)}\s*:\s*['\"]?([^\n'\"]+)['\"]?\s*$",
        source,
    )
    return matches[0].strip() if len(matches) == 1 else None


def finalization_scalar(content: str, field: str) -> Optional[str]:
    return frontmatter_mapping_scalar(content, "finalization", field)


def approval_scalar(content: str, field: str) -> Optional[str]:
    return frontmatter_mapping_scalar(content, "approval", field)


def frontmatter_from_text(content: str) -> Optional[str]:
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", content, re.DOTALL)
    return match.group(1) if match else None


def frontmatter_mapping_scalar(content: str, mapping: str,
                               field: str) -> Optional[str]:
    frontmatter = frontmatter_from_text(content)
    source = frontmatter if frontmatter is not None else content
    blocks = re.findall(
        rf"(?m)^{re.escape(mapping)}:\s*\n((?:^[ \t]+.*\n?)*)",
        source,
    )
    inline = re.findall(
        rf"(?m)^{re.escape(mapping)}\s*:\s*\{{([^}}]*)\}}\s*$",
        source,
    )
    if len(blocks) + len(inline) != 1:
        return None
    if blocks:
        matches = re.findall(
            rf"(?m)^\s+{re.escape(field)}\s*:\s*['\"]?([^\n'\"]+)['\"]?\s*$",
            blocks[0],
        )
        return matches[0].strip() if len(matches) == 1 else None
    return inline_mapping_field(inline[0], field)


def frontmatter_mapping_list(content: str, mapping: str,
                             field: str) -> Optional[List[str]]:
    """Read a canonical inline string list from a frontmatter mapping."""
    frontmatter = frontmatter_from_text(content)
    source = frontmatter if frontmatter is not None else content
    blocks = re.findall(
        rf"(?m)^{re.escape(mapping)}:\s*\n((?:^[ \t]+.*\n?)*)",
        source,
    )
    inline = re.findall(
        rf"(?m)^{re.escape(mapping)}\s*:\s*\{{([^}}]*)\}}\s*$",
        source,
    )
    if len(blocks) != 1 or inline:
        return None
    matches = re.findall(
        rf"(?m)^\s+{re.escape(field)}\s*:\s*\[([^\]]*)\]\s*$",
        blocks[0],
    )
    if len(matches) != 1:
        return None
    raw = matches[0].strip()
    if not raw:
        return []
    values = []
    for item in raw.split(","):
        value = item.strip().strip("'\"")
        if not value:
            return None
        values.append(value)
    return values


def inline_mapping_scalar(content: str, mapping: str,
                          field: str) -> Optional[str]:
    outer = re.findall(
        rf"(?m)^\s*{re.escape(mapping)}\s*:\s*\{{([^}}]*)\}}\s*$", content
    )
    if len(outer) != 1:
        return None
    return inline_mapping_field(outer[0], field)


def inline_mapping_field(content: str, field: str) -> Optional[str]:
    values = []
    for part in content.split(","):
        match = re.fullmatch(
            rf"\s*{re.escape(field)}\s*:\s*['\"]?([^'\"]+)['\"]?\s*",
            part,
        )
        if match:
            values.append(match.group(1).strip())
    return values[0] if len(values) == 1 else None


def active_steps_from_text(content: str) -> Optional[List[str]]:
    frontmatter = re.match(
        r"\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)", content, re.DOTALL
    )
    source = content[frontmatter.end():] if frontmatter else content
    matches = re.findall(
        r"(?im)^\s*(?:[-*]\s*)?(?:active[_ ]steps|현재\s*active[_ ]steps)\s*:\s*([^\n]+)$",
        source,
    )
    structured = frontmatter_mapping_list(content, "global_state", "active_steps")
    if not matches:
        return structured
    if len(matches) != 1:
        return None
    body = re.findall(STEP_REF_PATTERN, matches[0])
    if structured is not None and structured != body:
        return None
    return body
