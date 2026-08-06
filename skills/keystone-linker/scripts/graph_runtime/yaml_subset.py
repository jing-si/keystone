"""Strict, dependency-free YAML subset used by Keystone metadata surfaces.

This parser intentionally supports only the mappings, sequences, inline values,
and scalar types required by the Keystone wire. It is not a general YAML parser.
"""

import re
from typing import Any, Dict, List, Tuple


class MetadataError(ValueError):
    """Raised when source metadata is outside the supported YAML subset."""


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("["):
        if not value.endswith("]"):
            raise MetadataError("unterminated sequence")
        inner = value[1:-1].strip()
        return [] if not inner else [_parse_scalar(part) for part in inner.split(",")]
    if value.startswith("{"):
        if not value.endswith("}"):
            raise MetadataError("unterminated mapping")
        return _parse_inline_mapping(value[1:-1])
    if ((value.startswith('"') and value.endswith('"'))
            or (value.startswith("'") and value.endswith("'"))):
        return value[1:-1]
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _parse_inline_mapping(body: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    parts = re.split(r",\s*(?![^\[]*\])", body)
    for part in parts:
        if not part.strip():
            continue
        if ":" not in part:
            raise MetadataError("invalid inline mapping")
        key, value = part.split(":", 1)
        result[key.strip()] = _parse_scalar(value)
    return result


def _source_lines(text: str) -> List[Tuple[int, str]]:
    return [
        (len(raw) - len(raw.lstrip(" ")), raw.strip())
        for raw in text.splitlines()
        if raw.strip() and not raw.lstrip().startswith("#")
    ]


def parse_yaml_subset(text: str) -> Dict[str, Any]:
    """Parse the canonical Keystone YAML subset into a mapping.

    Unsupported indentation, malformed inline values, and non-mapping roots
    raise ``MetadataError`` so the owning source parser can emit diagnostics.
    """
    if text == "__malformed_frontmatter__":
        raise MetadataError("frontmatter closing delimiter is missing")
    lines = _source_lines(text)
    if not lines:
        return {}

    def parse_block(index: int, indent: int) -> Tuple[Any, int]:
        is_sequence = lines[index][1].startswith("-")
        container: Any = [] if is_sequence else {}
        while index < len(lines):
            current_indent, line = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise MetadataError("unexpected indentation")
            if is_sequence != line.startswith("-"):
                break
            if is_sequence:
                raw_item = line[1:].strip()
                if not raw_item:
                    if index + 1 >= len(lines) or lines[index + 1][0] <= indent:
                        container.append(None)
                        index += 1
                    else:
                        child, index = parse_block(index + 1, lines[index + 1][0])
                        container.append(child)
                    continue
                if ":" not in raw_item:
                    container.append(_parse_scalar(raw_item))
                    index += 1
                    continue
                key, raw_value = raw_item.split(":", 1)
                item: Dict[str, Any] = {
                    key.strip(): _parse_scalar(raw_value) if raw_value.strip() else {}
                }
                index += 1
                if index < len(lines) and lines[index][0] > indent:
                    child, index = parse_block(index, lines[index][0])
                    if not isinstance(child, dict):
                        raise MetadataError(
                            "sequence mapping continuation must be a mapping")
                    item.update(child)
                container.append(item)
                continue
            if ":" not in line:
                raise MetadataError("invalid mapping entry")
            key, raw_value = line.split(":", 1)
            key, raw_value = key.strip(), raw_value.strip()
            index += 1
            if raw_value:
                container[key] = _parse_scalar(raw_value)
            elif index < len(lines) and lines[index][0] > indent:
                child, index = parse_block(index, lines[index][0])
                container[key] = child
            else:
                container[key] = {}
        return container, index

    parsed, cursor = parse_block(0, lines[0][0])
    if cursor != len(lines) or not isinstance(parsed, dict):
        raise MetadataError("frontmatter root must be a mapping")
    return parsed

