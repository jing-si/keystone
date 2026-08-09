#!/usr/bin/env python3
"""Generate or verify package-local deterministic Work State runtimes."""

import argparse
import importlib.util
import json
from pathlib import Path
import stat
import sys
from typing import Any, Dict, Optional, Sequence, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RUNTIME = REPOSITORY_ROOT / "scripts" / "work_state_runtime.py"
CANONICAL_MANIFEST = REPOSITORY_ROOT / "scripts" / "work_state_runtime_manifest.json"
PACKAGE_DIRECTORIES = (
    REPOSITORY_ROOT / "skills" / "keystone-reader" / "scripts",
    REPOSITORY_ROOT / "skills" / "keystone-coordinator" / "scripts",
    REPOSITORY_ROOT / "skills" / "keystone-author" / "scripts",
)


def _digest(raw: bytes) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _load_runtime():
    spec = importlib.util.spec_from_file_location(
        "keystone_canonical_work_state_runtime", CANONICAL_RUNTIME
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("canonical Work State Runtime cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _manifest(runtime_bytes: bytes) -> Dict[str, Any]:
    runtime = _load_runtime()
    return {
        "schema_version": 1,
        "policy_version": runtime.POLICY_VERSION,
        "policy_digest": runtime.policy_digest(),
        "public_api": list(runtime.PUBLIC_API),
        "public_api_digest": runtime.public_api_digest(),
        "runtime_digest": _digest(runtime_bytes),
    }


def _targets() -> Tuple[Tuple[Path, Path], ...]:
    return tuple(
        (directory / "work_state_runtime.py", directory / "work_state_runtime_manifest.json")
        for directory in PACKAGE_DIRECTORIES
    )


def _regular_single_link(path: Path) -> bool:
    if not path.exists() or path.is_symlink():
        return False
    state = path.stat()
    return stat.S_ISREG(state.st_mode) and state.st_nlink == 1


def generate(*, check: bool) -> int:
    runtime_bytes = CANONICAL_RUNTIME.read_bytes()
    manifest_bytes = _canonical_json(_manifest(runtime_bytes))
    mismatches = []
    outputs = ((CANONICAL_MANIFEST, manifest_bytes),) + tuple(
        output
        for runtime_path, manifest_path in _targets()
        for output in ((runtime_path, runtime_bytes), (manifest_path, manifest_bytes))
    )
    for target, expected in outputs:
        if target.exists() and not _regular_single_link(target):
            raise OSError("generated output must be a single-link regular file: %s" % target)
        current = target.read_bytes() if target.exists() else None
        if current == expected:
            continue
        if check:
            mismatches.append(target.relative_to(REPOSITORY_ROOT).as_posix())
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
    if mismatches:
        for relative in mismatches:
            print("generated Work State output differs: %s" % relative)
        return 1
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return generate(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
