"""Apply one Main- or Coordinator-owned canonical transaction-v2 patch."""

from pathlib import Path
import sys

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from owned_surface_apply_runtime import run_cli


if __name__ == "__main__":
    sys.exit(
        run_cli(
            allowed_owners=frozenset({"main", "coordinator"}),
            runner_path=Path(__file__).absolute(),
        )
    )
