#!/usr/bin/env python3
"""Read-only idea lookup, numbering and table rendering; Python standard library only."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Sequence, Tuple

# keystone: id=key.code.ideas.reader kind=output_artifact artifact_kind=code governed_by=key.standard.skill.ideas produced_from=key.work.idea-notes.order

HEADER = re.compile(r"^## IDEA-([0-9]{3,}) · (.+)$")
FILENAME = re.compile(r"key-ideas(?:-[a-z0-9]+(?:-[a-z0-9]+)*)?\.md\Z")
FIELDS = {"- 필요했던 이유: ": "reason", "- 기록일: ": "recorded_at"}
TABLE_HEADER = "| ID | 제목 | 필요했던 이유 | 기록일 |\n|---|---|---|---|"


class NotesError(ValueError):
    """An input or snapshot diagnostic, never an empty successful result."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Idea:
    number: int
    title: str
    reason: str
    recorded_at: str
    details: str
    path: str
    start_line: int
    end_line: int
    source_digest: str

    @property
    def identifier(self) -> str:
        return "IDEA-%03d" % self.number


@dataclass(frozen=True)
class Snapshot:
    ideas: Tuple[Idea, ...]
    generation: str
    files_read: int
    bytes_read: int


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def visible_lines(lines: Sequence[str]) -> List[Tuple[int, str]]:
    """Exclude fenced examples from structural parsing, preserving source line numbers."""
    result = []
    fence = ""
    for index, line in enumerate(lines):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence):
                if not match[2].strip():
                    fence = ""
            continue
        if match:
            fence = match[1]
            continue
        result.append((index, line))
    if fence:
        raise NotesError("unclosed_fence", "Close the fenced block before reading ideas.")
    return result


def parse_notes(text: str, path: str, source_digest: str) -> Tuple[Idea, ...]:
    lines = text.splitlines()
    visible = visible_lines(lines)
    headings = []
    for index, line in visible:
        if not re.match(r"^ {0,3}##\s", line):
            continue
        match = HEADER.fullmatch(line)
        if not match or int(match[1]) < 1 or match[1] != "%03d" % int(match[1]):
            raise NotesError("invalid_heading", "%s:%d" % (path, index + 1))
        headings.append((index, int(match[1]), match[2].strip()))
    ideas = []
    structural_lines = dict(visible)
    for position, (start, number, title) in enumerate(headings):
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        fields: Dict[str, str] = {}
        field_lines = set()
        for index in range(start + 1, end):
            if index not in structural_lines:
                continue
            line = structural_lines[index]
            for prefix, key in FIELDS.items():
                if line.startswith(prefix):
                    if key in fields:
                        raise NotesError("duplicate_field", "%s: IDEA-%03d %s" % (path, number, key))
                    fields[key] = line[len(prefix):].strip()
                    field_lines.add(index)
        if not title or not fields.get("reason") or not fields.get("recorded_at"):
            raise NotesError("missing_field", "%s: IDEA-%03d needs title, reason and date" % (path, number))
        recorded = fields["recorded_at"]
        try:
            parsed_date = date.fromisoformat(recorded)
        except ValueError as error:
            raise NotesError("invalid_date", "%s: %s" % (path, recorded)) from error
        if parsed_date.isoformat() != recorded:
            raise NotesError("invalid_date", "%s: use YYYY-MM-DD" % path)
        details = "\n".join(lines[i] for i in range(start + 1, end) if i not in field_lines).strip()
        ideas.append(Idea(number, title, fields["reason"], recorded, details, path,
                          start + 1, end, source_digest))
    return tuple(ideas)


def note_paths(directory: Path) -> Tuple[Path, ...]:
    if directory.is_symlink():
        raise NotesError("unsafe_path", "The ideas directory must not be a symlink.")
    if not directory.exists():
        return ()
    if not directory.is_dir():
        raise NotesError("unsafe_path", "The ideas path must be a directory.")
    paths = tuple(sorted(directory.glob("key-ideas*.md")))
    for path in paths:
        if not FILENAME.fullmatch(path.name):
            raise NotesError("invalid_filename", str(path))
        if path.is_symlink() or not path.is_file():
            raise NotesError("unsafe_path", str(path))
    return paths


def load_snapshot(doc_root: Path) -> Snapshot:
    directory = doc_root / "ideas"
    paths = note_paths(directory)
    sources = []
    ideas: List[Idea] = []
    for path in paths:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        relative = "ideas/" + path.name
        sources.append((path, raw))
        ideas.extend(parse_notes(text, relative, digest(raw)))
    if note_paths(directory) != paths or any(path.read_bytes() != raw for path, raw in sources):
        raise NotesError("changed_during_read", "Notes changed; reread before choosing an action.")
    numbers = [idea.number for idea in ideas]
    if len(set(numbers)) != len(numbers):
        raise NotesError("duplicate_id", "Duplicate idea IDs across the notes; do not renumber automatically.")
    generation = digest(json.dumps([(p.name, digest(raw)) for p, raw in sources]).encode("utf-8"))
    return Snapshot(tuple(sorted(ideas, key=lambda item: item.number)), generation,
                    len(paths), sum(len(raw) for _, raw in sources))


def next_id(ideas: Sequence[Idea]) -> str:
    return "IDEA-%03d" % (max((idea.number for idea in ideas), default=0) + 1)


def table_cell(value: str) -> str:
    return html.escape(value, quote=False).replace("|", "&#124;").replace("`", "&#96;").replace("\n", "<br>")


def render_table(ideas: Sequence[Idea]) -> str:
    rows = [TABLE_HEADER]
    for idea in ideas:
        cells = (idea.identifier, idea.title, idea.reason, idea.recorded_at)
        rows.append("| " + " | ".join(table_cell(cell) for cell in cells) + " |")
    return "\n".join(rows)


def select_ideas(ideas: Sequence[Idea], identifiers: Sequence[str], terms: Sequence[str]) -> Tuple[Idea, ...]:
    for identifier in identifiers:
        if not re.fullmatch(r"IDEA-[0-9]{3,}", identifier):
            raise NotesError("invalid_id", identifier)
    if identifiers and terms:
        raise NotesError("invalid_query", "Use exact IDs or search terms, not both.")
    if any(not term.strip() for term in terms):
        raise NotesError("invalid_query", "Search terms must not be empty.")
    if identifiers:
        return tuple(idea for idea in ideas if idea.identifier in identifiers)
    if terms:
        return tuple(idea for idea in ideas if any(
            term.casefold() in "\n".join((idea.title, idea.reason, idea.details)).casefold()
            for term in terms
        ))
    return tuple(ideas)


def result_payload(snapshot: Snapshot, identifiers: Sequence[str], terms: Sequence[str],
                   limit: int, offset: int, details: bool) -> dict:
    matches = select_ideas(snapshot.ideas, identifiers, terms)
    selected = matches[offset:offset + limit]
    records = []
    for idea in selected:
        record = {"id": idea.identifier, "title": idea.title, "reason": idea.reason,
                  "recorded_at": idea.recorded_at, "path": idea.path,
                  "start_line": idea.start_line, "end_line": idea.end_line,
                  "source_digest": idea.source_digest}
        if details:
            record["details"] = idea.details
        records.append(record)
    return {"schema_version": 1, "status": "pass", "diagnostics": [],
            "summary": {"total": len(snapshot.ideas), "matched": len(matches),
                        "returned": len(selected), "offset": offset,
                        "has_more": offset + len(selected) < len(matches),
                        "files_read": snapshot.files_read,
                        "source_bytes": snapshot.bytes_read,
                        "read_passes": 2, "bytes_read": snapshot.bytes_read * 2},
            "generation": snapshot.generation, "next_id": next_id(snapshot.ideas),
            "table": render_table(selected), "ideas": records}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc-root", type=Path, required=True,
                        help="Resolved document root; only its ideas/key-ideas*.md files are read")
    parser.add_argument("--id", action="append", default=[], dest="identifiers")
    parser.add_argument("--query", action="append", default=[], help="Literal OR terms; AI expands meanings")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.limit <= 200 or args.offset < 0:
            raise NotesError("invalid_page", "limit must be 1..200 and offset nonnegative")
        result = result_payload(load_snapshot(args.doc_root), args.identifiers, args.query,
                                args.limit, args.offset, args.details)
    except (NotesError, OSError, UnicodeError) as error:
        code = error.code if isinstance(error, NotesError) else "read_error"
        result = {"schema_version": 1, "status": "fail",
                  "diagnostics": [{"code": code, "message": str(error)}], "summary": {}}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
