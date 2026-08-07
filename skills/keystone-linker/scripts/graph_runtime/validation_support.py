"""Shared diagnostic and path primitives for graph validation."""

from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable

from .model import Diagnostic, Severity


def diagnostic(code: str, message: str, path: str = None, *,
               severity=Severity.ERROR) -> Diagnostic:
    return Diagnostic(code=code, message=message, severity=severity, path=path)


def canonical_relative_path(relative: Any) -> str:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("source path must be a non-empty canonical POSIX path")
    candidate = PurePosixPath(relative)
    if (
        candidate.is_absolute()
        or candidate.as_posix() != relative
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise ValueError("source path must be a canonical repository-relative path")
    return candidate.as_posix()


def safe_path(root: Path, relative: str) -> Path:
    relative = canonical_relative_path(relative)
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError("source path escapes root: %s" % relative) from error
    return candidate


def diagnostic_dict(item: Diagnostic) -> Dict[str, Any]:
    result = {"code": item.code, "message": item.message, "severity": item.severity.value}
    if item.path is not None:
        result["path"] = item.path
    if item.locator is not None:
        result["locator"] = {
            key: value for key, value in asdict(item.locator).items() if value is not None
        }
    return result


def envelope(diagnostics: Iterable[Diagnostic], *,
             execution_error: bool = False, coverage=None) -> Dict[str, Any]:
    serialized = [diagnostic_dict(item) for item in diagnostics]
    errors = sum(item["severity"] == "error" for item in serialized)
    warnings = sum(item["severity"] == "warning" for item in serialized)
    result = {
        "schema_version": 1,
        "status": "error" if execution_error else ("fail" if errors else "pass"),
        "diagnostics": serialized,
        "summary": {"errors": errors, "warnings": warnings},
    }
    if coverage is not None:
        result["coverage"] = coverage
    return result
