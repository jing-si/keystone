#!/usr/bin/env bash
set -euo pipefail

# Reinstall Keystone skills from this local repository into Codex.
# Run from anywhere:
#   bash reinstall-local-keystone-skills.sh
#
# After this finishes, restart Codex so the updated skills are loaded.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"

SKILLS=(
  keystone-init
  keystone-reader
  keystone-author
  keystone-clarify
  keystone-linker
  keystone-coordinator
)

echo "Repository: $REPO_ROOT"
echo "Install destination: $DEST_ROOT"

for skill in "${SKILLS[@]}"; do
  if [ ! -f "$REPO_ROOT/skills/$skill/SKILL.md" ]; then
    echo "Missing source skill: $REPO_ROOT/skills/$skill/SKILL.md" >&2
    exit 1
  fi
done

AUTHOR_VALIDATOR="$REPO_ROOT/skills/keystone-author/scripts/validate_finalization.py"
AUTHOR_VALIDATOR_RUNNER="$REPO_ROOT/skills/keystone-author/scripts/run_finalization_validation.py"
AUTHOR_VALIDATOR_HOOK="$REPO_ROOT/skills/keystone-author/scripts/check_finalization_hook.sh"
if [ ! -f "$AUTHOR_VALIDATOR" ]; then
  echo "Missing Author validator: $AUTHOR_VALIDATOR" >&2
  exit 1
fi
if [ ! -f "$AUTHOR_VALIDATOR_RUNNER" ]; then
  echo "Missing Author validator runner: $AUTHOR_VALIDATOR_RUNNER" >&2
  exit 1
fi
if [ ! -f "$AUTHOR_VALIDATOR_HOOK" ]; then
  echo "Missing Author validator hook wrapper: $AUTHOR_VALIDATOR_HOOK" >&2
  exit 1
fi

LINKER_GRAPH_VALIDATOR="$REPO_ROOT/skills/keystone-linker/scripts/validate_graph.py"
LINKER_GRAPH_RUNNER="$REPO_ROOT/skills/keystone-linker/scripts/run_graph_validation.py"
LINKER_GRAPH_HOOK="$REPO_ROOT/skills/keystone-linker/scripts/check_graph_hook.sh"
LINKER_GRAPH_RUNTIME="$REPO_ROOT/skills/keystone-linker/scripts/graph_runtime/validator.py"
LINKER_GRAPH_REFERENCE="$REPO_ROOT/skills/keystone-linker/references/graph-runtime.md"
LINKER_GRAPH_TEST="$REPO_ROOT/skills/keystone-linker/tests/test_validate_graph.py"
for source in "$LINKER_GRAPH_VALIDATOR" "$LINKER_GRAPH_RUNNER" "$LINKER_GRAPH_HOOK" \
  "$LINKER_GRAPH_RUNTIME" "$LINKER_GRAPH_REFERENCE" "$LINKER_GRAPH_TEST"; do
  if [ ! -f "$source" ]; then
    echo "Missing Linker graph validation package file: $source" >&2
    exit 1
  fi
done

mkdir -p "$DEST_ROOT"

echo "Removing existing Keystone skills..."
for skill in "${SKILLS[@]}"; do
  rm -rf "$DEST_ROOT/$skill"
done

echo "Installing local Keystone skills..."
for skill in "${SKILLS[@]}"; do
  cp -R "$REPO_ROOT/skills/$skill" "$DEST_ROOT/"
done

INSTALLED_AUTHOR_VALIDATOR="$DEST_ROOT/keystone-author/scripts/validate_finalization.py"
INSTALLED_AUTHOR_VALIDATOR_RUNNER="$DEST_ROOT/keystone-author/scripts/run_finalization_validation.py"
INSTALLED_AUTHOR_VALIDATOR_HOOK="$DEST_ROOT/keystone-author/scripts/check_finalization_hook.sh"
if [ ! -f "$INSTALLED_AUTHOR_VALIDATOR" ]; then
  echo "Install failed for Author validator: $INSTALLED_AUTHOR_VALIDATOR" >&2
  exit 1
fi
if [ ! -f "$INSTALLED_AUTHOR_VALIDATOR_RUNNER" ]; then
  echo "Install failed for Author validator runner: $INSTALLED_AUTHOR_VALIDATOR_RUNNER" >&2
  exit 1
fi
if [ ! -f "$INSTALLED_AUTHOR_VALIDATOR_HOOK" ]; then
  echo "Install failed for Author validator hook wrapper: $INSTALLED_AUTHOR_VALIDATOR_HOOK" >&2
  exit 1
fi
python3 "$INSTALLED_AUTHOR_VALIDATOR" --help >/dev/null
python3 "$INSTALLED_AUTHOR_VALIDATOR_RUNNER" --help >/dev/null
bash -n "$INSTALLED_AUTHOR_VALIDATOR_HOOK"

INSTALLED_LINKER_GRAPH_VALIDATOR="$DEST_ROOT/keystone-linker/scripts/validate_graph.py"
INSTALLED_LINKER_GRAPH_RUNNER="$DEST_ROOT/keystone-linker/scripts/run_graph_validation.py"
INSTALLED_LINKER_GRAPH_HOOK="$DEST_ROOT/keystone-linker/scripts/check_graph_hook.sh"
INSTALLED_LINKER_GRAPH_RUNTIME="$DEST_ROOT/keystone-linker/scripts/graph_runtime/validator.py"
INSTALLED_LINKER_GRAPH_REFERENCE="$DEST_ROOT/keystone-linker/references/graph-runtime.md"
INSTALLED_LINKER_GRAPH_TEST="$DEST_ROOT/keystone-linker/tests/test_validate_graph.py"
for installed in "$INSTALLED_LINKER_GRAPH_VALIDATOR" "$INSTALLED_LINKER_GRAPH_RUNNER" \
  "$INSTALLED_LINKER_GRAPH_HOOK" "$INSTALLED_LINKER_GRAPH_RUNTIME" \
  "$INSTALLED_LINKER_GRAPH_REFERENCE" "$INSTALLED_LINKER_GRAPH_TEST"; do
  if [ ! -f "$installed" ]; then
    echo "Install failed for Linker graph validation package file: $installed" >&2
    exit 1
  fi
done
python3 "$INSTALLED_LINKER_GRAPH_VALIDATOR" --help >/dev/null
python3 "$INSTALLED_LINKER_GRAPH_RUNNER" --help >/dev/null
bash -n "$INSTALLED_LINKER_GRAPH_HOOK"

echo "Installed:"
for skill in "${SKILLS[@]}"; do
  if [ -f "$DEST_ROOT/$skill/SKILL.md" ]; then
    echo "  - $DEST_ROOT/$skill/SKILL.md"
  else
    echo "Install failed for $skill" >&2
    exit 1
  fi
done

echo
echo "Done. Restart Codex to load the updated Keystone skills."
