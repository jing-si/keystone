import io
import re
import tokenize
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol, Tuple


_CPP_RAW_OPEN = re.compile(r'R"([^ ()\\\t\v\f\r\n]{0,16})\(')
_RUST_RAW_OPEN = re.compile(r'(?:b)?r(#{0,255})"')
_SQL_DOLLAR_OPEN = re.compile(r"\$(?:[A-Za-z_][A-Za-z0-9_]*)?\$")
_SWIFT_RAW_OPEN = re.compile(r'(#+)("""|")')
_TRIPLE_QUOTE_OPEN = re.compile(r'("{3,}|\'{3,})')
_RUST_LIFETIME = re.compile(r"'[A-Za-z_][A-Za-z0-9_]*")
_JS_IDENTIFIER = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
_JS_NUMBER = re.compile(r"[0-9A-Fa-f_xXoObBeE.+-]+")


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


def _line_comment_metadata(
    text: str,
    marker: str,
    *,
    allow_heredoc: bool = False,
    allow_dollar_strings: bool = False,
    nested_block_comments: bool = False,
    triple_backslash_escapes: bool = False,
    block_comments: bool = True,
    single_quote_backslash_escapes: bool = True,
    preserve_escaped_newline_token: bool = False,
    rust_lifetimes: bool = False,
    digit_separators: bool = False,
    plain_single_quote_apostrophes: bool = False,
    ambiguities=None,
):
    """Yield first-token line-comment metadata outside string/comment regions."""
    index = 0
    line_has_token = False
    state = None
    closer = None
    escaped = False
    block_depth = 0
    ambiguous_in_state = False
    while index < len(text):
        if state == "block_comment":
            if nested_block_comments and text.startswith("/*", index):
                block_depth += 1
                index += 2
                continue
            if text.startswith("*/", index):
                block_depth -= 1
                if block_depth == 0:
                    state = None
                    line_has_token = True
                    ambiguous_in_state = False
                index += 2
                continue
            if _metadata_marker_at(text, index, marker):
                ambiguous_in_state = True
            if text[index] == "\n":
                line_has_token = False
            index += 1
            continue
        if state is not None:
            if state == "verbatim" and text.startswith('""', index):
                index += 2
                continue
            character = text[index]
            if _metadata_marker_at(text, index, marker):
                ambiguous_in_state = True
            if escaped:
                escaped = False
                if character == "\n":
                    line_has_token = False
                index += 1
                continue
            if text.startswith(closer, index):
                index += len(closer)
                state = None
                closer = None
                line_has_token = True
                ambiguous_in_state = False
                continue
            if (
                state == "quoted"
                and (closer != "'" or single_quote_backslash_escapes)
                or (state == "triple" and triple_backslash_escapes)
            ) and character == "\\":
                escaped = True
                index += 1
                continue
            if character == "\n":
                line_has_token = False
            index += 1
            continue

        character = text[index]
        if index == 0 and character == "\ufeff":
            index += 1
            continue
        if character == "\n":
            line_has_token = False
            index += 1
            continue
        if (
            preserve_escaped_newline_token
            and character == "\\"
            and index + 1 < len(text)
            and text[index + 1] == "\n"
        ):
            line_has_token = True
            index += 2
            continue
        if character in " \t\r\f\v" and not line_has_token:
            index += 1
            continue
        if text.startswith(marker, index):
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            if not line_has_token:
                body = text[index + len(marker):end].strip()
                match = re.match(r"(?:keystone|key):\s*(.+)$", body)
                if match:
                    yield match.group(1).strip(), None, None
            index = end
            continue
        if block_comments and text.startswith("/*", index):
            state = "block_comment"
            block_depth = 1
            ambiguous_in_state = False
            line_has_token = True
            index += 2
            continue

        cpp_raw = _CPP_RAW_OPEN.match(text, index)
        if cpp_raw:
            state = "raw"
            closer = ")%s\"" % cpp_raw.group(1)
            line_has_token = True
            ambiguous_in_state = False
            index = cpp_raw.end()
            continue
        rust_raw = _RUST_RAW_OPEN.match(text, index)
        if rust_raw:
            state = "raw"
            closer = '"' + rust_raw.group(1)
            line_has_token = True
            ambiguous_in_state = False
            index = rust_raw.end()
            continue
        if allow_dollar_strings:
            dollar_string = _SQL_DOLLAR_OPEN.match(text, index)
            if dollar_string:
                state = "raw"
                closer = dollar_string.group(0)
                line_has_token = True
                ambiguous_in_state = False
                index = dollar_string.end()
                continue
        swift_raw = _SWIFT_RAW_OPEN.match(text, index)
        if swift_raw:
            state = "raw"
            closer = swift_raw.group(2) + swift_raw.group(1)
            line_has_token = True
            ambiguous_in_state = False
            index = swift_raw.end()
            continue
        if text.startswith('@"', index):
            state = "verbatim"
            closer = '"'
            line_has_token = True
            ambiguous_in_state = False
            index += 2
            continue
        quote_run = _TRIPLE_QUOTE_OPEN.match(text, index)
        if quote_run:
            state = "triple"
            closer = quote_run.group(1)
            line_has_token = True
            ambiguous_in_state = False
            index = quote_run.end()
            continue
        if character == "'" and rust_lifetimes:
            lifetime = _RUST_LIFETIME.match(text, index)
            if lifetime:
                following = lifetime.end()
                previous_index = index - 1
                while previous_index >= 0 and text[previous_index].isspace():
                    previous_index -= 1
                previous = text[previous_index] if previous_index >= 0 else None
                if (
                    (following >= len(text) or text[following] != "'")
                    and previous in {"<", "&", ",", "+", ":"}
                ):
                    line_has_token = True
                    index = following
                    continue
        if (
            character == "'"
            and digit_separators
            and index > 0
            and index + 1 < len(text)
            and re.match(r"[0-9A-Fa-f]", text[index - 1])
            and re.match(r"[0-9A-Fa-f]", text[index + 1])
        ):
            line_has_token = True
            index += 1
            continue
        if (
            character == "'"
            and plain_single_quote_apostrophes
            and index > 0
            and index + 1 < len(text)
            and re.match(r"[A-Za-z0-9_-]", text[index - 1])
            and re.match(r"[A-Za-z0-9_-]", text[index + 1])
        ):
            line_has_token = True
            index += 1
            continue
        if character in {'"', "'", "`"}:
            state = "quoted"
            closer = character
            escaped = False
            line_has_token = True
            ambiguous_in_state = False
            index += 1
            continue
        line_has_token = True
        index += 1
    if state is not None and ambiguous_in_state and ambiguities is not None:
        ambiguities.append((
            "ambiguous_metadata_anchor",
            "metadata-like text occurs inside an unterminated lexical construct",
        ))


def _metadata_marker_at(text: str, index: int, marker: str) -> bool:
    if not text.startswith(marker, index):
        return False
    end = text.find("\n", index)
    end = len(text) if end < 0 else end
    return bool(re.match(
        r"[ \t]*(?:keystone|key):[ \t]*\S+",
        text[index + len(marker):end],
    ))


def _mask_yaml_block_scalars(text: str) -> str:
    """Mask YAML block-scalar content while preserving offsets and newlines."""
    masked = []
    parent_indent = None
    scalar = re.compile(
        r"^(?P<indent>[ ]*)(?:-[ \t]+)?"
        r"(?:(?:[^#\r\n][^:\r\n]*):[ \t]*)?"
        r"(?:[!&][^\s]+[ \t]+)*[|>][0-9+-]*[ \t]*"
        r"(?:#.*)?(?:\r?\n)?$"
    )
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if parent_indent is not None:
            if not content.strip():
                masked.append("".join(
                    character if character in "\r\n" else " "
                    for character in line
                ))
                continue
            indentation = len(content) - len(content.lstrip(" "))
            if indentation > parent_indent:
                masked.append("".join(
                    character if character in "\r\n" else " "
                    for character in line
                ))
                continue
            parent_indent = None
        masked.append(line)
        match = scalar.match(line)
        if match:
            parent_indent = len(match.group("indent"))
    return "".join(masked)


def _scan_shell_heredoc_line(
    line: str,
    quote=None,
    escaped: bool = False,
    arithmetic_depth: int = 0,
):
    """Return heredocs and lexical state after one physical shell line."""
    result = []
    index = 0
    while index < len(line):
        character = line[index]
        if quote is not None:
            if quote != "'" and character == "\\" and not escaped:
                escaped = True
                index += 1
                continue
            if not escaped and character == quote:
                quote = None
            escaped = False
            index += 1
            continue
        if line.startswith("$((", index):
            arithmetic_depth += 2
            index += 3
            continue
        if line.startswith("((", index):
            arithmetic_depth += 2
            index += 2
            continue
        if arithmetic_depth:
            if character == "(":
                arithmetic_depth += 1
            elif character == ")":
                arithmetic_depth -= 1
            index += 1
            continue
        if character in {'"', "'", "`"}:
            quote = character
            index += 1
            continue
        if character == "#" and (
            index == 0
            or line[index - 1].isspace()
            or line[index - 1] in ";|&()"
        ):
            break
        if line.startswith("<<<", index):
            index += 3
            continue
        if not line.startswith("<<", index):
            index += 1
            continue
        cursor = index + 2
        strip_tabs = cursor < len(line) and line[cursor] == "-"
        if strip_tabs:
            cursor += 1
        while cursor < len(line) and line[cursor] in " \t":
            cursor += 1
        delimiter = []
        delimiter_quote = None
        while cursor < len(line):
            value = line[cursor]
            if delimiter_quote is not None:
                if value == delimiter_quote:
                    delimiter_quote = None
                elif value == "\\" and delimiter_quote == '"' and cursor + 1 < len(line):
                    cursor += 1
                    delimiter.append(line[cursor])
                else:
                    delimiter.append(value)
                cursor += 1
                continue
            if value in {'"', "'"}:
                delimiter_quote = value
                cursor += 1
                continue
            if value == "\\" and cursor + 1 < len(line):
                cursor += 1
                delimiter.append(line[cursor])
                cursor += 1
                continue
            if value.isspace() or value in ";|&<>(){}":
                break
            delimiter.append(value)
            cursor += 1
        if delimiter and delimiter_quote is None:
            result.append(("".join(delimiter), strip_tabs))
        index = max(cursor, index + 2)
    return tuple(result), quote, escaped, arithmetic_depth


def _shell_heredoc_delimiters(line: str):
    """Return ordered shell heredoc delimiters outside quotes and arithmetic."""
    return _scan_shell_heredoc_line(line)[0]


def _mask_shell_heredocs(text: str, ambiguities=None) -> str:
    """Mask every queued shell heredoc body while preserving newlines."""
    masked = []
    pending = []
    ambiguous_pending = False
    quote = None
    escaped = False
    arithmetic_depth = 0
    for line in text.splitlines(keepends=True):
        if pending:
            delimiter, strip_tabs = pending[0]
            content = line.rstrip("\r\n")
            candidate = content.lstrip("\t") if strip_tabs else content
            if re.match(r"^[ \t]*#[ \t]*(?:keystone|key):[ \t]*\S+", content):
                ambiguous_pending = True
            masked.append("".join(
                character if character in "\r\n" else " "
                for character in line
            ))
            if candidate == delimiter:
                pending.pop(0)
                ambiguous_pending = False
            continue
        masked.append(line)
        delimiters, quote, escaped, arithmetic_depth = _scan_shell_heredoc_line(
            line,
            quote,
            escaped,
            arithmetic_depth,
        )
        pending.extend(delimiters)
    if pending and ambiguous_pending and ambiguities is not None:
        ambiguities.append((
            "ambiguous_metadata_anchor",
            "metadata-like text occurs inside an unterminated shell heredoc",
        ))
    return "".join(masked)


def _mask_js_template_literals(text: str, ambiguities=None) -> str:
    """Mask template text; metadata-like interpolations require a companion."""
    masked = list(text)

    def mask_span(start: int, end: int) -> None:
        for position in range(start, min(end, len(masked))):
            if masked[position] not in "\r\n":
                masked[position] = " "

    def metadata_like_comment(start: int, end: int) -> bool:
        return bool(re.search(
            r"//[ \t]*(?:keystone|key):[ \t]*\S+",
            text[start:end],
        ))

    def quoted_end(start: int, quote: str):
        index = start + 1
        escaped = False
        while index < len(text):
            character = text[index]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                return index + 1, True
            elif character in "\r\n":
                return index, False
            index += 1
        return len(text), False

    def regex_end(start: int):
        index = start + 1
        escaped = False
        in_character_class = False
        while index < len(text):
            character = text[index]
            if character in "\r\n":
                return index, False
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == "[":
                in_character_class = True
            elif character == "]" and in_character_class:
                in_character_class = False
            elif character == "/" and not in_character_class:
                index += 1
                while index < len(text) and re.match(
                    r"[A-Za-z]", text[index]
                ):
                    index += 1
                return index, True
            index += 1
        return len(text), False

    def template_end(start: int):
        index = start + 1
        interpolated = False
        mask_span(start, index)
        while index < len(text):
            if text[index] == "\\":
                mask_span(index, min(index + 2, len(text)))
                index += 2
                continue
            if text[index] == "`":
                mask_span(index, index + 1)
                end = index + 1
                if (
                    interpolated
                    and metadata_like_comment(start, end)
                    and ambiguities is not None
                ):
                    mask_span(start, end)
                    ambiguities.append((
                        "ambiguous_metadata_anchor",
                        "metadata-like text inside JavaScript template "
                        "interpolation requires companion metadata",
                    ))
                return end, True
            if text.startswith("${", index):
                interpolated = True
                mask_span(index, index + 2)
                expression_end, complete = expression_body_end(index + 2)
                if not complete:
                    mask_span(start, len(text))
                    if metadata_like_comment(start, len(text)) and ambiguities is not None:
                        ambiguities.append((
                            "ambiguous_metadata_anchor",
                            "metadata-like text occurs inside an unterminated "
                            "JavaScript template interpolation",
                        ))
                    return len(text), False
                index = expression_end
                continue
            mask_span(index, index + 1)
            index += 1
        if metadata_like_comment(start, len(text)) and ambiguities is not None:
            ambiguities.append((
                "ambiguous_metadata_anchor",
                "metadata-like text occurs inside an unterminated JavaScript "
                "template literal",
            ))
        mask_span(start, len(text))
        return len(text), False

    def expression_body_end(start: int):
        index = start
        brace_depth = 1
        expect_operand = True
        pending_control = False
        control_parentheses = []
        while index < len(text):
            character = text[index]
            if character.isspace():
                index += 1
                continue
            if text.startswith("//", index):
                newline = text.find("\n", index + 2)
                index = len(text) if newline < 0 else newline + 1
                continue
            if text.startswith("/*", index):
                closer = text.find("*/", index + 2)
                if closer < 0:
                    return len(text), False
                index = closer + 2
                continue
            if character == "/":
                if expect_operand:
                    index, complete = regex_end(index)
                    if not complete:
                        return len(text), False
                    expect_operand = False
                else:
                    index += 2 if text.startswith("/=", index) else 1
                    expect_operand = True
                continue
            if character in {'"', "'"}:
                index, complete = quoted_end(index, character)
                if not complete:
                    return len(text), False
                expect_operand = False
                continue
            if character == "`":
                index, complete = template_end(index)
                if not complete:
                    return len(text), False
                expect_operand = False
                continue
            identifier = _JS_IDENTIFIER.match(text, index)
            if identifier:
                word = identifier.group(0)
                index += len(word)
                pending_control = word in {"catch", "for", "if", "switch", "while", "with"}
                expect_operand = word in {
                    "await", "case", "delete", "in", "instanceof", "new", "of",
                    "return", "throw", "typeof", "void", "yield",
                } or pending_control
                continue
            if character.isdigit():
                number = _JS_NUMBER.match(text, index)
                index += len(number.group(0)) if number else 1
                expect_operand = False
                pending_control = False
                continue
            if text.startswith(("++", "--"), index):
                index += 2
                pending_control = False
                continue
            if text.startswith(("=>", "==", "!=", "<=", ">=", "&&", "||", "??", "**"), index):
                index += 2
                expect_operand = True
                pending_control = False
                continue
            if character == "(":
                control_parentheses.append(pending_control)
                pending_control = False
                expect_operand = True
                index += 1
                continue
            if character == ")":
                expect_operand = (
                    control_parentheses.pop() if control_parentheses else False
                )
                pending_control = False
                index += 1
                continue
            if character == "[":
                expect_operand = True
                pending_control = False
                index += 1
                continue
            if character == "]":
                expect_operand = False
                pending_control = False
                index += 1
                continue
            if character == "{":
                brace_depth += 1
                expect_operand = True
                pending_control = False
            elif character == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    mask_span(index, index + 1)
                    return index + 1, True
                expect_operand = False
                pending_control = False
            elif character in ",:;=!?&|+-*%^~<>":
                expect_operand = True
                pending_control = False
            elif character == ".":
                expect_operand = False
                pending_control = False
            else:
                expect_operand = False
                pending_control = False
            index += 1
        return len(text), False

    index = 0
    while index < len(text):
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            index = len(text) if newline < 0 else newline + 1
            continue
        if text.startswith("/*", index):
            closer = text.find("*/", index + 2)
            index = len(text) if closer < 0 else closer + 2
            continue
        character = text[index]
        if character in {'"', "'"}:
            index, _complete = quoted_end(index, character)
            continue
        if character == "`":
            index, _complete = template_end(index)
            continue
        index += 1
    return "".join(masked)


def _mask_js_literals_and_comments(text: str) -> str:
    """Mask JavaScript string/comment bytes for conservative JSX tag discovery."""
    values = list(text)
    index = 0
    state = None
    closer = None
    escaped = False
    while index < len(text):
        if state == "line":
            if text[index] == "\n":
                state = None
            else:
                values[index] = " "
            index += 1
            continue
        if state == "block":
            values[index] = " " if text[index] not in "\r\n" else text[index]
            if text.startswith("*/", index):
                if index + 1 < len(values):
                    values[index + 1] = " "
                state = None
                index += 2
            else:
                index += 1
            continue
        if state == "quoted":
            values[index] = " " if text[index] not in "\r\n" else text[index]
            if escaped:
                escaped = False
            elif text[index] == "\\":
                escaped = True
            elif text[index] == closer:
                state = None
            index += 1
            continue
        if text.startswith("//", index):
            values[index:index + 2] = [" ", " "]
            state = "line"
            index += 2
            continue
        if text.startswith("/*", index):
            values[index:index + 2] = [" ", " "]
            state = "block"
            index += 2
            continue
        if text[index] in {'"', "'", "`"}:
            values[index] = " "
            state = "quoted"
            closer = text[index]
            index += 1
            continue
        index += 1
    return "".join(values)


def _looks_like_tsx_generic_arrow(text: str, tag_match) -> bool:
    """Recognize the TSX-required trailing-comma generic arrow form."""
    if tag_match.group("closing") or not tag_match.group("body").strip().endswith(","):
        return False
    return bool(re.match(
        r"[ \t\r\n]*\([^()\r\n]*\)[ \t\r\n]*=>",
        text[tag_match.end():],
    ))


def _mask_jsx_text(text: str, ambiguities=None) -> str:
    """Mask JSX tag/text regions while leaving braced JavaScript expressions."""
    neutral = _mask_js_literals_and_comments(text)
    masked = list(text)
    depth = 0
    expression_depth = 0
    ambiguous_text = False
    index = 0
    tag = re.compile(r"<(?P<closing>/)?(?P<name>[A-Za-z][A-Za-z0-9_.:-]*|)(?P<body>[^>]*)>")
    while index < len(text):
        if depth and expression_depth:
            if neutral[index] == "{":
                expression_depth += 1
            elif neutral[index] == "}":
                expression_depth -= 1
                if expression_depth == 0:
                    masked[index] = " "
            index += 1
            continue
        if depth:
            if _metadata_marker_at(text, index, "//"):
                ambiguous_text = True
            if neutral[index] == "{":
                expression_depth = 1
                masked[index] = " "
                index += 1
                continue
            match = tag.match(neutral, index)
            if match:
                for position in range(match.start(), match.end()):
                    if masked[position] not in "\r\n":
                        masked[position] = " "
                if match.group("closing"):
                    depth = max(0, depth - 1)
                    if depth == 0:
                        ambiguous_text = False
                elif not match.group("body").rstrip().endswith("/"):
                    depth += 1
                index = match.end()
                continue
            if masked[index] not in "\r\n":
                masked[index] = " "
            index += 1
            continue
        if neutral[index] == "<":
            match = tag.match(neutral, index)
            previous = neutral[:index].rstrip()
            prior = previous[-1:] or None
            after_return = bool(re.search(r"\breturn$", previous))
            if match and not _looks_like_tsx_generic_arrow(neutral, match) and (
                prior is None
                or prior in "=(:,[!&|?>{;"
                or after_return
            ):
                for position in range(match.start(), match.end()):
                    if masked[position] not in "\r\n":
                        masked[position] = " "
                if not match.group("closing") and not match.group("body").rstrip().endswith("/"):
                    depth = 1
                index = match.end()
                continue
        index += 1
    if depth and ambiguous_text and ambiguities is not None:
        ambiguities.append((
            "ambiguous_metadata_anchor",
            "metadata-like text occurs inside an unterminated JSX region",
        ))
    return "".join(masked)


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
        frontmatter_source = text[1:] if text.startswith("\ufeff") else text
        if (frontmatter_source.startswith("---\n")
                or frontmatter_source.startswith("---\r\n")):
            match = re.match(
                r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)",
                frontmatter_source,
                re.DOTALL,
            )
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
    frontmatter_offset = 1 if text.startswith("\ufeff") else 0
    frontmatter = re.match(
        r"^---\r?\n.*?\r?\n---(?:\r?\n|$)",
        text[frontmatter_offset:],
        re.DOTALL,
    )
    ignored = fenced + comment_ranges + (
        ((
            frontmatter_offset + frontmatter.start(),
            frontmatter_offset + frontmatter.end(),
        ),) if frontmatter else ()
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
    allow_heredoc: bool = False
    allow_dollar_strings: bool = False
    nested_block_comments: bool = False
    jsx_text: bool = False
    template_interpolation: bool = False
    triple_backslash_escapes: bool = False
    block_comments: bool = True
    single_quote_backslash_escapes: bool = True
    preserve_escaped_newline_token: bool = False
    rust_lifetimes: bool = False
    digit_separators: bool = False
    plain_single_quote_apostrophes: bool = False

    def _scan(self, text: str):
        ambiguities = []
        if (
            self.template_interpolation
            and "${" in text
            and re.search(
                r"(?m)^[ \t]*//[ \t]*(?:keystone|key):[ \t]*\S+",
                text,
            )
        ):
            return (), ((
                "ambiguous_metadata_anchor",
                "JavaScript/TypeScript source containing template interpolation "
                "and metadata-like text requires companion metadata",
            ),)
        source = (
            _mask_shell_heredocs(text, ambiguities)
            if self.allow_heredoc else text
        )
        source = (
            _mask_js_template_literals(source, ambiguities)
            if self.template_interpolation else source
        )
        source = (
            _mask_jsx_text(source, ambiguities)
            if self.jsx_text else source
        )
        blocks = tuple(_line_comment_metadata(
            source,
            self.marker,
            allow_dollar_strings=self.allow_dollar_strings,
            nested_block_comments=self.nested_block_comments,
            triple_backslash_escapes=self.triple_backslash_escapes,
            block_comments=self.block_comments,
            single_quote_backslash_escapes=self.single_quote_backslash_escapes,
            preserve_escaped_newline_token=self.preserve_escaped_newline_token,
            rust_lifetimes=self.rust_lifetimes,
            digit_separators=self.digit_separators,
            plain_single_quote_apostrophes=self.plain_single_quote_apostrophes,
            ambiguities=ambiguities,
        ))
        return blocks, tuple(dict.fromkeys(ambiguities))

    def scan_metadata(self, text: str):
        """Return blocks and lexical diagnostics from one scan."""
        return self._scan(text)

    def metadata_blocks(self, text: str):
        yield from self.scan_metadata(text)[0]

    def metadata_diagnostics(self, text: str):
        return self.scan_metadata(text)[1]


@dataclass(frozen=True)
class KotlinJavaAdapter(GenericLineCommentAdapter):
    pass


@dataclass(frozen=True)
class SqlAdapter(GenericLineCommentAdapter):
    surface: str = "schema_anchor"
    marker: str = "--"
    allow_dollar_strings: bool = True
    single_quote_backslash_escapes: bool = False


@dataclass(frozen=True)
class YamlAdapter(GenericLineCommentAdapter):
    surface: str = "config_anchor"
    marker: str = "#"

    def _scan(self, text: str):
        ambiguities = []
        blocks = tuple(_line_comment_metadata(
            _mask_yaml_block_scalars(text),
            self.marker,
            block_comments=False,
            single_quote_backslash_escapes=False,
            plain_single_quote_apostrophes=True,
            ambiguities=ambiguities,
        ))
        return blocks, tuple(dict.fromkeys(ambiguities))


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
    if suffix in {"kt", "kts"}:
        return KotlinJavaAdapter(nested_block_comments=True)
    if suffix == "java":
        return KotlinJavaAdapter(triple_backslash_escapes=True)
    if suffix == "sql":
        return SqlAdapter()
    if suffix in {"xml", "html", "xhtml"}:
        return XmlAdapter()
    if suffix in {"yaml", "yml"}:
        return YamlAdapter()
    if suffix in {"jsx", "tsx"}:
        return GenericLineCommentAdapter(
            jsx_text=True,
            template_interpolation=True,
        )
    if suffix in {"swift", "rs"}:
        return GenericLineCommentAdapter(
            nested_block_comments=True,
            triple_backslash_escapes=suffix == "swift",
            rust_lifetimes=suffix == "rs",
        )
    if suffix in {"c", "cc", "cpp", "h", "hpp"}:
        return GenericLineCommentAdapter(
            preserve_escaped_newline_token=True,
            digit_separators=suffix in {"cc", "cpp", "hpp"},
        )
    if suffix in {"js", "ts"}:
        return GenericLineCommentAdapter(template_interpolation=True)
    if suffix in {"go", "cs"}:
        return GenericLineCommentAdapter()
    if suffix in {"py", "pyi"}:
        return PythonAdapter()
    if suffix in {"sh", "bash", "zsh"}:
        return GenericLineCommentAdapter(
            marker="#",
            allow_heredoc=True,
            block_comments=False,
            single_quote_backslash_escapes=False,
            preserve_escaped_newline_token=True,
        )
    return None


@dataclass(frozen=True)
class PreparedAdapter:
    """Request-local immutable lexical result shared by admission and parsing."""
    surface: str
    blocks: tuple
    diagnostics: tuple = ()
    contextual_blocks: tuple = ()

    def metadata_blocks(self, text: str):
        return iter(self.blocks)

    def metadata_diagnostics(self, text: str):
        return self.diagnostics

    def metadata_blocks_with_context(self, text: str):
        return iter(self.contextual_blocks or self.blocks)


def prepare_adapter(adapter: Adapter, text: str) -> PreparedAdapter:
    if isinstance(adapter, PreparedAdapter):
        return adapter
    if hasattr(adapter, "scan_metadata"):
        blocks, diagnostics = adapter.scan_metadata(text)
        return PreparedAdapter(adapter.surface, tuple(blocks), tuple(diagnostics))
    if (adapter.surface == "document_metadata"
            and hasattr(adapter, "metadata_blocks_with_context")):
        contextual = tuple(adapter.metadata_blocks_with_context(text))
        blocks = tuple((block.text, block.construct, block.label) for block in contextual)
        return PreparedAdapter(adapter.surface, blocks, contextual_blocks=contextual)
    return PreparedAdapter(adapter.surface, tuple(adapter.metadata_blocks(text)))
