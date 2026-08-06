import re
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol, Tuple


class Adapter(Protocol):
    surface: str

    def metadata_blocks(self, text: str) -> Iterable[Tuple[str, Optional[str], Optional[str]]]:
        """Yield metadata text, following construct kind, and construct label."""


def _following_construct(text: str, end: int) -> Tuple[Optional[str], Optional[str]]:
    tail = text[end:]
    match = re.match(r"[ \t]*(?:\r?\n)[ \t]*(.*)", tail)
    if not match:
        return None, None
    line = match.group(1).strip()
    if line.startswith("#"):
        return "heading", line.lstrip("#").strip()
    if re.match(r"(?:[-+*]|\d+[.)])\s+", line):
        return "list", re.sub(r"^(?:[-+*]|\d+[.)])\s+", "", line).strip()
    return None, None


def _fenced_ranges(text: str):
    ranges = []
    opened = None
    for match in re.finditer(r"^[ \t]*(`{3,}|~{3,}).*$", text, re.MULTILINE):
        marker = match.group(1)[0]
        if opened is None:
            opened = (marker, match.start())
        elif opened[0] == marker:
            ranges.append((opened[1], match.end()))
            opened = None
    if opened is not None:
        ranges.append((opened[1], len(text)))
    return tuple(ranges)


def _in_ranges(position: int, ranges) -> bool:
    return any(start <= position < end for start, end in ranges)


def _inside_inline_code(text: str, position: int) -> bool:
    line_start = text.rfind("\n", 0, position) + 1
    return text[line_start:position].count("`") % 2 == 1


@dataclass(frozen=True)
class MarkdownAdapter:
    surface: str = "document_metadata"

    def metadata_blocks(self, text: str):
        fenced = _fenced_ranges(text)
        if text.startswith("---\n") or text.startswith("---\r\n"):
            match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
            if match:
                frontmatter = match.group(1)
                if re.search(r"^(?:key(?:\.|\s*:)|document_lifecycle\s*:|approval\s*:|authority\s*:|work_gates\s*:)",
                             frontmatter, re.MULTILINE):
                    yield frontmatter, "document", None
            else:
                yield "__malformed_frontmatter__", "document", None
        pending = None
        for match in re.finditer(r"<!--(.*?)-->", text, re.DOTALL):
            if _in_ranges(match.start(), fenced) or _inside_inline_code(text, match.start()):
                continue
            line_start = text.rfind("\n", 0, match.start()) + 1
            if text[line_start:match.start()].lstrip().startswith("|"):
                continue
            body = match.group(1).strip()
            if not re.match(r"^(?:key\s*:|key\.|keystone\s*:)", body):
                continue
            if "\n" not in body:
                if body.startswith("key:"):
                    body = body[4:].strip()
                elif body.startswith("keystone:"):
                    body = body[len("keystone:"):].strip()
            has_id = bool(re.search(r"(?:^|[\s,{])id\s*[:=]", body, re.MULTILINE))
            if (pending is not None and not has_id
                    and not text[pending[1]:match.start()].strip()):
                pending = (pending[0] + " " + body, match.end())
                continue
            if pending is not None:
                kind, label = _following_construct(text, pending[1])
                yield pending[0], kind, label
            pending = (body, match.end())
        if pending is not None:
            kind, label = _following_construct(text, pending[1])
            yield pending[0], kind, label
        for row in re.finditer(r"^\|\s*<!--(.*?)-->\s*([^|]*)\|", text, re.MULTILINE | re.DOTALL):
            if _in_ranges(row.start(), fenced):
                continue
            body = row.group(1).strip()
            if body.startswith("key:"):
                body = body[4:].strip()
            visible = re.sub(r"[`*_]", "", row.group(2)).strip()
            yield body, "table", visible


@dataclass(frozen=True)
class GenericLineCommentAdapter:
    surface: str = "code_anchor"
    marker: str = "//"

    def metadata_blocks(self, text: str):
        pattern = r"^\s*" + re.escape(self.marker) + r"\s*(?:keystone|key):\s*(.+)$"
        for match in re.finditer(pattern, text, re.MULTILINE):
            yield match.group(1).strip(), None, None


@dataclass(frozen=True)
class KotlinJavaAdapter(GenericLineCommentAdapter):
    pass


@dataclass(frozen=True)
class SqlAdapter(GenericLineCommentAdapter):
    surface: str = "schema_anchor"
    marker: str = "--"


@dataclass(frozen=True)
class YamlAdapter(GenericLineCommentAdapter):
    surface: str = "config_anchor"
    marker: str = "#"


@dataclass(frozen=True)
class XmlAdapter:
    surface: str = "config_anchor"

    def metadata_blocks(self, text: str):
        for match in re.finditer(r"<!--\s*(?:keystone|key):\s*(.*?)\s*-->", text, re.DOTALL):
            yield match.group(1).strip(), None, None


def adapter_for_path(path: str) -> Optional[Adapter]:
    suffix = path.lower().rsplit(".", 1)[-1] if "." in path else ""
    if suffix in {"md", "markdown"}:
        return MarkdownAdapter()
    if suffix in {"kt", "kts", "java"}:
        return KotlinJavaAdapter()
    if suffix == "sql":
        return SqlAdapter()
    if suffix in {"xml", "html", "xhtml"}:
        return XmlAdapter()
    if suffix in {"yaml", "yml"}:
        return YamlAdapter()
    if suffix in {"js", "jsx", "ts", "tsx", "c", "cc", "cpp", "h", "hpp", "swift",
                  "go", "rs", "cs"}:
        return GenericLineCommentAdapter()
    if suffix in {"py", "pyi", "sh", "bash", "zsh"}:
        return GenericLineCommentAdapter(marker="#")
    return None
