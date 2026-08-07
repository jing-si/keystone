import io
import re
import tokenize
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol, Tuple


class Adapter(Protocol):
    surface: str

    def metadata_blocks(self, text: str) -> Iterable[Tuple[str, Optional[str], Optional[str]]]:
        """Yield metadata text, following construct kind, and construct label."""


def _following_construct(text: str, end: int) -> Tuple[Optional[str], Optional[str]]:
    kind, label, _offset, _level = _following_construct_context(text, end)
    return kind, label


def _following_construct_context(text: str, end: int):
    tail = text[end:]
    match = re.match(r"[ \t]*(?:\r?\n)([ \t]*)([^\r\n]*)", tail)
    if not match:
        return None, None, end, None
    line = match.group(2).strip()
    target_offset = end + match.start(1)
    heading = re.match(r"^(#{1,6})(?:[ \t]+|$)(.*?)\s*#*\s*$", line)
    if heading:
        return "heading", heading.group(2).strip(), target_offset, len(heading.group(1))
    if re.match(r"(?:[-+*]|\d+[.)])\s+", line):
        label = re.sub(r"^(?:[-+*]|\d+[.)])\s+", "", line).strip()
        return "list", label, target_offset, None
    following_line = tail[match.end():]
    setext = re.match(r"\r?\n[ \t]{0,3}(=+|-+)[ \t]*(?:\r?\n|$)", following_line)
    if line and setext:
        return "heading", line, target_offset, 1 if setext.group(1)[0] == "=" else 2
    return None, None, target_offset, None


def _fenced_ranges(text: str):
    ranges = []
    opened = None
    pattern = r"^[ ]{0,3}(`{3,}|~{3,})([^\r\n]*)$"
    for match in re.finditer(pattern, text, re.MULTILINE):
        token = match.group(1)
        marker = token[0]
        if opened is None:
            if marker == "`" and "`" in match.group(2):
                continue
            opened = (marker, len(token), match.start())
        elif (opened[0] == marker and len(token) >= opened[1]
              and not match.group(2).strip()):
            ranges.append((opened[2], match.end()))
            opened = None
    if opened is not None:
        ranges.append((opened[2], len(text)))
    return tuple(ranges)


def _in_ranges(position: int, ranges) -> bool:
    return any(start <= position < end for start, end in ranges)


def _inside_inline_code(text: str, position: int) -> bool:
    line_start = text.rfind("\n", 0, position) + 1
    opener_length = None
    for delimiter in re.finditer(r"`+", text[line_start:position]):
        length = len(delimiter.group(0))
        if opener_length is None:
            opener_length = length
        elif length == opener_length:
            opener_length = None
    return opener_length is not None


def _inside_passive_markdown_line(text: str, position: int) -> bool:
    line_start = text.rfind("\n", 0, position) + 1
    prefix = text[line_start:position]
    return bool(prefix.startswith("\t") or re.match(r" {4,}", prefix)
                or re.match(r" {0,3}>", prefix))


@dataclass(frozen=True)
class MarkdownMetadataBlock:
    text: str
    construct: Optional[str]
    label: Optional[str]
    target_offset: int
    heading_level: Optional[int] = None
    enclosing_heading_offset: Optional[int] = None


@dataclass(frozen=True)
class MarkdownAdapter:
    surface: str = "document_metadata"

    def metadata_blocks(self, text: str):
        for block in self.metadata_blocks_with_context(text):
            yield block.text, block.construct, block.label

    def metadata_blocks_with_context(self, text: str):
        fenced = _fenced_ranges(text)
        blocks = []
        if text.startswith("---\n") or text.startswith("---\r\n"):
            match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
            if match:
                frontmatter = match.group(1)
                if re.search(r"^(?:key(?:\.|\s*:)|document_lifecycle\s*:|approval\s*:|authority\s*:|work_gates\s*:)",
                             frontmatter, re.MULTILINE):
                    blocks.append(MarkdownMetadataBlock(
                        frontmatter, "document", None, -1,
                    ))
            else:
                blocks.append(MarkdownMetadataBlock(
                    "__malformed_frontmatter__", "document", None, -1,
                ))
        pending = None
        for match in re.finditer(r"<!--(.*?)-->", text, re.DOTALL):
            if (_in_ranges(match.start(), fenced)
                    or _inside_inline_code(text, match.start())
                    or _inside_passive_markdown_line(text, match.start())):
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
                kind, label, target_offset, level = _following_construct_context(
                    text, pending[1],
                )
                blocks.append(MarkdownMetadataBlock(
                    pending[0], kind, label, target_offset, level,
                ))
            pending = (body, match.end())
        if pending is not None:
            kind, label, target_offset, level = _following_construct_context(
                text, pending[1],
            )
            blocks.append(MarkdownMetadataBlock(
                pending[0], kind, label, target_offset, level,
            ))
        for row in re.finditer(r"^\|\s*<!--(.*?)-->\s*([^|]*)\|", text, re.MULTILINE | re.DOTALL):
            if _in_ranges(row.start(), fenced):
                continue
            body = row.group(1).strip()
            if body.startswith("key:"):
                body = body[4:].strip()
            visible = re.sub(r"[`*_]", "", row.group(2)).strip()
            blocks.append(MarkdownMetadataBlock(
                body, "table", visible, row.start(),
            ))

        annotated_headings = {
            block.target_offset
            for block in blocks
            if block.construct == "heading"
        }
        headings = _markdown_headings(text, fenced)
        for block in sorted(blocks, key=lambda item: item.target_offset):
            stack = []
            for offset, level in headings:
                if offset >= block.target_offset:
                    break
                while stack and stack[-1][1] >= level:
                    stack.pop()
                stack.append((offset, level))
            enclosing = next(
                (offset for offset, _level in reversed(stack)
                 if offset in annotated_headings),
                None,
            )
            yield MarkdownMetadataBlock(
                block.text,
                block.construct,
                block.label,
                block.target_offset,
                block.heading_level,
                enclosing,
            )


def _markdown_headings(text: str, fenced):
    comment_ranges = tuple(
        (match.start(), match.end())
        for match in re.finditer(r"<!--.*?-->", text, re.DOTALL)
    )
    frontmatter = re.match(r"^---\r?\n.*?\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    ignored = fenced + comment_ranges + (
        ((frontmatter.start(), frontmatter.end()),) if frontmatter else ()
    )
    headings = []
    pattern = r"^[ \t]{0,3}(#{1,6})(?:[ \t]+|$).*?$"
    for match in re.finditer(pattern, text, re.MULTILINE):
        if _in_ranges(match.start(), ignored):
            continue
        headings.append((match.start(), len(match.group(1))))
    setext_pattern = r"^([^\r\n]+)\r?\n[ \t]{0,3}(=+|-+)[ \t]*$"
    for match in re.finditer(setext_pattern, text, re.MULTILINE):
        label = match.group(1).strip()
        if (_in_ranges(match.start(), ignored)
                or not label
                or label.startswith(("#", "<!--", "```", "~~~"))
                or re.match(r"(?:[-+*]|\d+[.)])\s+", label)):
            continue
        headings.append((
            match.start(),
            1 if match.group(2)[0] == "=" else 2,
        ))
    return tuple(sorted(set(headings)))


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
class PythonAdapter:
    surface: str = "code_anchor"

    def metadata_blocks(self, text: str):
        try:
            tokens = tokenize.generate_tokens(io.StringIO(text).readline)
            for token in tokens:
                if token.type != tokenize.COMMENT:
                    continue
                match = re.match(r"#\s*(?:keystone|key):\s*(.+)$", token.string)
                if match:
                    yield match.group(1).strip(), None, None
        except (IndentationError, tokenize.TokenError):
            return


@dataclass(frozen=True)
class XmlAdapter:
    surface: str = "config_anchor"

    def metadata_blocks(self, text: str):
        cdata = tuple(
            (match.start(), match.end())
            for match in re.finditer(r"<!\[CDATA\[.*?\]\]>", text, re.DOTALL)
        )
        for match in re.finditer(r"<!--\s*(?:keystone|key):\s*(.*?)\s*-->", text, re.DOTALL):
            if _in_ranges(match.start(), cdata):
                continue
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
    if suffix in {"py", "pyi"}:
        return PythonAdapter()
    if suffix in {"sh", "bash", "zsh"}:
        return GenericLineCommentAdapter(marker="#")
    return None
