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

mkdir -p "$DEST_ROOT"

echo "Removing existing Keystone skills..."
for skill in "${SKILLS[@]}"; do
  rm -rf "$DEST_ROOT/$skill"
done

echo "Installing local Keystone skills..."
for skill in "${SKILLS[@]}"; do
  cp -R "$REPO_ROOT/skills/$skill" "$DEST_ROOT/"
done

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
