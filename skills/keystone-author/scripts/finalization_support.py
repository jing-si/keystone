"""Pure source-reading helpers for the finalization validator."""

import re
from pathlib import Path
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
    candidate = (root / value).resolve()
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
    match = re.search(
        rf"(?m)^{re.escape(field)}\s*:\s*['\"]?([^\n'\"]+)['\"]?\s*$",
        source,
    )
    return match.group(1).strip() if match else None


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
    block = re.search(
        rf"(?ms)^{re.escape(mapping)}:\s*\n((?:^[ \t]+.*\n?)*)",
        source,
    )
    if block:
        match = re.search(
            rf"(?m)^\s+{re.escape(field)}\s*:\s*['\"]?([^\n'\"]+)['\"]?\s*$",
            block.group(1),
        )
        return match.group(1).strip() if match else None
    return inline_mapping_scalar(source, mapping, field)


def frontmatter_mapping_list(content: str, mapping: str,
                             field: str) -> Optional[List[str]]:
    """Read a canonical inline string list from a frontmatter mapping."""
    frontmatter = frontmatter_from_text(content)
    source = frontmatter if frontmatter is not None else content
    block = re.search(
        rf"(?ms)^{re.escape(mapping)}:\s*\n((?:^[ \t]+.*\n?)*)",
        source,
    )
    if not block:
        return None
    match = re.search(
        rf"(?m)^\s+{re.escape(field)}\s*:\s*\[([^\]]*)\]\s*$",
        block.group(1),
    )
    if not match:
        return None
    raw = match.group(1).strip()
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
    outer = re.search(
        rf"(?m)^\s*{re.escape(mapping)}\s*:\s*\{{([^}}]*)\}}\s*$", content
    )
    if not outer:
        return None
    inner = re.search(
        rf"(?:^|,)\s*{re.escape(field)}\s*:\s*['\"]?([^,'\"]+)['\"]?\s*(?:,|$)",
        outer.group(1),
    )
    return inner.group(1).strip() if inner else None


def active_steps_from_text(content: str) -> Optional[List[str]]:
    match = re.search(
        r"(?im)^\s*(?:[-*]\s*)?(?:active[_ ]steps|현재\s*active[_ ]steps)\s*:\s*([^\n]+)$",
        content,
    )
    if not match:
        return None
    return re.findall(STEP_REF_PATTERN, match.group(1))
