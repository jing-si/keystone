"""Actual repository state primitives for Coordinator closure schema v2."""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_json(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return digest_bytes(payload)


def normalize_relative_path(value: Any) -> Optional[str]:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or value != candidate.as_posix():
        return None
    if any(part in {"", ".", ".."} for part in candidate.parts):
        return None
    return candidate.as_posix()


def safe_path(root: Path, relative: str) -> Optional[Path]:
    normalized = normalize_relative_path(relative)
    if normalized is None:
        return None
    root_resolved = root.resolve()
    candidate = root_resolved.joinpath(*PurePosixPath(normalized).parts)
    try:
        candidate.parent.resolve().relative_to(root_resolved)
    except (OSError, RuntimeError, ValueError):
        return None
    return candidate


def resolved_repository_root(root: Path) -> Path:
    """Resolve one existing repository directory or fail explicitly."""

    resolved = root.resolve(strict=True)
    if not resolved.is_dir():
        raise NotADirectoryError(str(root))
    return resolved


def _raise_walk_error(error: OSError) -> None:
    raise error


def repository_snapshot(root: Path) -> Dict[str, str]:
    """Return a deterministic raw-byte snapshot without following symlinks."""

    root = resolved_repository_root(root)
    snapshot: Dict[str, str] = {}
    for current, directory_names, file_names in os.walk(
        root, followlinks=False, onerror=_raise_walk_error
    ):
        current_path = Path(current)
        relative_directory = current_path.relative_to(root)
        if relative_directory == Path(".") and ".git" in directory_names:
            directory_names.remove(".git")

        symlink_directories = []
        for name in list(directory_names):
            path = current_path / name
            if path.is_symlink():
                directory_names.remove(name)
                symlink_directories.append(name)

        for name in sorted(file_names + symlink_directories):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                target = os.readlink(path).encode("utf-8", errors="surrogateescape")
                snapshot[relative] = digest_bytes(b"symlink\0" + target)
            else:
                snapshot[relative] = digest_file(path)
    return dict(sorted(snapshot.items()))


def repository_symlinks(root: Path) -> Dict[str, Tuple[str, bool]]:
    """Return symlink targets and whether their resolved target escapes root."""

    root = resolved_repository_root(root)
    result: Dict[str, Tuple[str, bool]] = {}
    for current, directory_names, file_names in os.walk(
        root, followlinks=False, onerror=_raise_walk_error
    ):
        current_path = Path(current)
        if current_path == root and ".git" in directory_names:
            directory_names.remove(".git")
        names = list(file_names) + list(directory_names)
        for name in names:
            path = current_path / name
            if not path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            target = os.readlink(path)
            try:
                path.resolve().relative_to(root)
                escapes = False
            except (OSError, RuntimeError, ValueError):
                escapes = True
            result[relative] = (target, escapes)
    return dict(sorted(result.items()))


def changed_paths(
    baseline: Mapping[str, str], current: Mapping[str, str]
) -> Dict[str, str]:
    changes: Dict[str, str] = {}
    for path in sorted(set(baseline) | set(current)):
        before = baseline.get(path)
        after = current.get(path)
        if before == after:
            continue
        if before is None:
            changes[path] = "added"
        elif after is None:
            changes[path] = "deleted"
        else:
            changes[path] = "modified"
    return changes


def path_in_scope(path: str, selectors: Iterable[str]) -> bool:
    for selector in selectors:
        normalized = normalize_relative_path(selector)
        if normalized is None:
            continue
        if normalized == ".":
            return True
        if path == normalized or path.startswith(normalized.rstrip("/") + "/"):
            return True
    return False


def path_overlaps_scope(path: str, selectors: Iterable[str]) -> bool:
    """Return whether a path is an ancestor or descendant of any selector."""

    normalized_path = normalize_relative_path(path)
    if normalized_path is None:
        return False
    for selector in selectors:
        normalized = normalize_relative_path(selector)
        if normalized is None:
            continue
        if normalized == ".":
            return True
        if (
            normalized_path == normalized
            or normalized_path.startswith(normalized.rstrip("/") + "/")
            or normalized.startswith(normalized_path.rstrip("/") + "/")
        ):
            return True
    return False
