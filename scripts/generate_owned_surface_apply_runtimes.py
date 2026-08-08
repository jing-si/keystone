"""Generate or verify package-local owner apply runtime copies."""

import argparse
from pathlib import Path
import stat
import sys
from typing import Optional, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RUNTIME = REPOSITORY_ROOT / "scripts" / "owned_surface_apply_runtime.py"
GENERATED_RUNTIMES = (
    REPOSITORY_ROOT
    / "skills"
    / "keystone-author"
    / "scripts"
    / "owned_surface_apply_runtime.py",
    REPOSITORY_ROOT
    / "skills"
    / "keystone-coordinator"
    / "scripts"
    / "owned_surface_apply_runtime.py",
)


def generate(*, check: bool) -> int:
    canonical = CANONICAL_RUNTIME.read_bytes()
    mismatches = []
    for target in GENERATED_RUNTIMES:
        if target.is_symlink():
            raise OSError("generated runtime must not be a symlink: %s" % target)
        if target.exists():
            state = target.stat()
            if not stat.S_ISREG(state.st_mode) or state.st_nlink != 1:
                raise OSError(
                    "generated runtime must be a single-link regular file: %s" % target
                )
            current = target.read_bytes()
        else:
            current = None
        if current == canonical:
            continue
        if check:
            mismatches.append(str(target.relative_to(REPOSITORY_ROOT)))
        else:
            target.write_bytes(canonical)
    if mismatches:
        for relative in mismatches:
            print("generated runtime differs: %s" % relative)
        return 1
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return generate(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
