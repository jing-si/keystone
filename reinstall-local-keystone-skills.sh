#!/usr/bin/env bash
set -euo pipefail

# Reinstall Keystone skills from this local repository into Codex.
# Run from anywhere:
#   bash reinstall-local-keystone-skills.sh
#
# After this finishes, restart Codex so the updated skills are loaded.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
PACKAGE_VERSION_FILE="$REPO_ROOT/VERSION"

SKILLS=(
  keystone-init
  keystone-reader
  keystone-author
  keystone-clarify
  keystone-linker
  keystone-coordinator
  keystone-ideas
)

echo "Repository: $REPO_ROOT"
echo "Install destination: $DEST_ROOT"

if [ ! -s "$PACKAGE_VERSION_FILE" ]; then
  echo "Missing Keystone package version: $PACKAGE_VERSION_FILE" >&2
  exit 1
fi
PACKAGE_VERSION="$(tr -d '[:space:]' < "$PACKAGE_VERSION_FILE")"

PYTHON_ISOLATED_ARGS=()
if python3 -I -c 'pass' >/dev/null 2>&1; then
  PYTHON_ISOLATED_ARGS=(-I)
fi

run_python_help() {
  python3 "${PYTHON_ISOLATED_ARGS[@]}" "$1" --help >/dev/null
}

run_direct_help() {
  "$1" --help >/dev/null
}

require_file() {
  if [ ! -f "$1" ]; then
    echo "Missing Keystone package file: $1" >&2
    exit 1
  fi
}

require_executable() {
  if [ ! -x "$1" ]; then
    echo "Keystone package file is not executable: $1" >&2
    exit 1
  fi
}

require_absent() {
  if [ -e "$1" ]; then
    echo "Retired Keystone package file is still present: $1" >&2
    exit 1
  fi
}

require_file_parity() {
  local expected="$1"
  local candidate
  shift
  for candidate in "$@"; do
    if ! cmp -s "$expected" "$candidate"; then
      echo "Installer byte parity failed: $candidate" >&2
      exit 1
    fi
  done
}

verify_package_tree() {
  local base="$1"
  local skill
  for skill in "${SKILLS[@]}"; do
    require_file "$base/$skill/SKILL.md"
  done

  require_file "$base/keystone-ideas/scripts/ideas.py"

  require_executable "$base/keystone-reader/scripts/keystone_session_title.py"

  require_file "$base/keystone-author/scripts/validate_finalization.py"
  require_file "$base/keystone-author/scripts/run_finalization_validation.py"
  require_file "$base/keystone-author/scripts/check_finalization_hook.sh"
  require_file "$base/keystone-author/references/finalization-validator.md"

  require_file "$base/keystone-linker/scripts/validate_graph.py"
  require_file "$base/keystone-linker/scripts/run_graph_validation.py"
  require_file "$base/keystone-linker/scripts/run_graph_classification.py"
  require_file "$base/keystone-linker/scripts/check_graph_hook.sh"
  require_file "$base/keystone-linker/scripts/graph_runtime/validator.py"
  require_file "$base/keystone-linker/scripts/graph_runtime/source_unit.py"
  require_file "$base/keystone-linker/references/graph-runtime.md"

  require_file "$base/keystone-coordinator/scripts/validate_closure.py"
  require_file "$base/keystone-coordinator/scripts/closure_actual_state.py"
  require_file "$base/keystone-coordinator/scripts/closure_v2.py"
  require_file "$base/keystone-coordinator/scripts/closure_v3.py"
  require_file "$base/keystone-coordinator/references/closure-validator.md"

  require_absent "$base/keystone-author/scripts/owned_surface_apply_runtime.py"
  require_absent "$base/keystone-author/scripts/run_owned_surface_apply.py"
  require_absent "$base/keystone-coordinator/scripts/owned_surface_apply_runtime.py"
  require_absent "$base/keystone-coordinator/scripts/run_owned_surface_apply.py"
  require_absent "$base/keystone-coordinator/scripts/capture_assignment_snapshot.py"
  require_absent "$base/keystone-coordinator/scripts/record_acceptance_event.py"
}

verify_python_entrypoints() {
  local base="$1"
  run_python_help "$base/keystone-ideas/scripts/ideas.py"
  run_direct_help "$base/keystone-reader/scripts/keystone_session_title.py"
  run_python_help "$base/keystone-author/scripts/validate_finalization.py"
  run_python_help "$base/keystone-author/scripts/run_finalization_validation.py"
  bash -n "$base/keystone-author/scripts/check_finalization_hook.sh"
  run_python_help "$base/keystone-linker/scripts/validate_graph.py"
  run_python_help "$base/keystone-linker/scripts/run_graph_validation.py"
  run_python_help "$base/keystone-linker/scripts/run_graph_classification.py"
  bash -n "$base/keystone-linker/scripts/check_graph_hook.sh"
  run_python_help "$base/keystone-coordinator/scripts/validate_closure.py"
}

verify_package_tree "$REPO_ROOT/skills"
verify_python_entrypoints "$REPO_ROOT/skills"

WORK_STATE_GENERATOR="$REPO_ROOT/scripts/generate_work_state_runtimes.py"
WORK_STATE_CANONICAL_RUNTIME="$REPO_ROOT/scripts/work_state_runtime.py"
WORK_STATE_CANONICAL_MANIFEST="$REPO_ROOT/scripts/work_state_runtime_manifest.json"
require_file "$WORK_STATE_GENERATOR"
require_file "$WORK_STATE_CANONICAL_RUNTIME"
require_file "$WORK_STATE_CANONICAL_MANIFEST"
python3 "${PYTHON_ISOLATED_ARGS[@]}" "$WORK_STATE_GENERATOR" --check

for skill in keystone-reader keystone-author keystone-coordinator; do
  require_file "$REPO_ROOT/skills/$skill/scripts/work_state_runtime.py"
  require_file "$REPO_ROOT/skills/$skill/scripts/work_state_runtime_manifest.json"
  require_file_parity "$WORK_STATE_CANONICAL_RUNTIME" \
    "$REPO_ROOT/skills/$skill/scripts/work_state_runtime.py"
  require_file_parity "$WORK_STATE_CANONICAL_MANIFEST" \
    "$REPO_ROOT/skills/$skill/scripts/work_state_runtime_manifest.json"
done

DEST_PARENT="$(dirname "$DEST_ROOT")"
mkdir -p "$DEST_PARENT" "$DEST_ROOT"
STAGING_ROOT="$(mktemp -d "$DEST_PARENT/.keystone-stage.XXXXXX")"
STAGED_SKILLS="$STAGING_ROOT/skills"
mkdir -p "$STAGED_SKILLS"

cleanup_staging() {
  rm -rf "$STAGING_ROOT"
}

INSTALL_SWITCH_STARTED=false
INSTALL_COMMITTED=false

echo "Staging local Keystone skills..."
for skill in "${SKILLS[@]}"; do
  cp -R "$REPO_ROOT/skills/$skill" "$STAGED_SKILLS/"
done

verify_package_tree "$STAGED_SKILLS"
verify_python_entrypoints "$STAGED_SKILLS"
for skill in keystone-reader keystone-author keystone-coordinator; do
  require_file_parity "$WORK_STATE_CANONICAL_RUNTIME" \
    "$STAGED_SKILLS/$skill/scripts/work_state_runtime.py"
  require_file_parity "$WORK_STATE_CANONICAL_MANIFEST" \
    "$STAGED_SKILLS/$skill/scripts/work_state_runtime_manifest.json"
done

SOURCE_REVISION="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || true)"
SOURCE_DIRTY=false
if [ -z "$SOURCE_REVISION" ]; then
  SOURCE_REVISION="unknown"
elif [ -n "$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null || true)" ]; then
  SOURCE_DIRTY=true
fi
printf '{"schema_version":1,"package_version":"%s","source_commit":"%s","source_dirty":%s,"skills":["keystone-init","keystone-reader","keystone-author","keystone-clarify","keystone-linker","keystone-coordinator","keystone-ideas"]}\n' \
  "$PACKAGE_VERSION" "$SOURCE_REVISION" "$SOURCE_DIRTY" > "$STAGED_SKILLS/.keystone-install.json"

BACKUP_ROOT="$DEST_ROOT/.keystone-backups/$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir -p "$BACKUP_ROOT"
MOVED_OLD=()
MOVED_NEW=()
MANIFEST_BACKED_UP=false

rollback_install() {
  local skill
  if [ "$INSTALL_SWITCH_STARTED" != true ]; then
    return
  fi
  for skill in "${MOVED_NEW[@]}"; do
    rm -rf "$DEST_ROOT/$skill"
  done
  for skill in "${MOVED_OLD[@]}"; do
    if [ -e "$BACKUP_ROOT/$skill" ]; then
      mv "$BACKUP_ROOT/$skill" "$DEST_ROOT/$skill"
    fi
  done
  rm -f "$DEST_ROOT/.keystone-install.json"
  if [ "$MANIFEST_BACKED_UP" = true ]; then
    mv "$BACKUP_ROOT/.keystone-install.json" "$DEST_ROOT/.keystone-install.json"
  fi
}

finish_install() {
  local status=$?
  trap - EXIT ERR
  if [ "$status" -ne 0 ] || [ "$INSTALL_COMMITTED" != true ]; then
    if [ "$status" -eq 0 ]; then
      status=1
    fi
    set +e
    rollback_install
  fi
  cleanup_staging
  exit "$status"
}
trap finish_install EXIT

echo "Installing staged Keystone skills..."
INSTALL_SWITCH_STARTED=true
if [ -e "$DEST_ROOT/.keystone-install.json" ]; then
  mv "$DEST_ROOT/.keystone-install.json" "$BACKUP_ROOT/.keystone-install.json"
  MANIFEST_BACKED_UP=true
fi
for skill in "${SKILLS[@]}"; do
  if [ -e "$DEST_ROOT/$skill" ]; then
    mv "$DEST_ROOT/$skill" "$BACKUP_ROOT/$skill"
    MOVED_OLD+=("$skill")
  fi
  mv "$STAGED_SKILLS/$skill" "$DEST_ROOT/$skill"
  MOVED_NEW+=("$skill")
done
mv "$STAGED_SKILLS/.keystone-install.json" "$DEST_ROOT/.keystone-install.json"

if [ -n "${_KEYSTONE_TEST_BREAK_AFTER_SWAP:-}" ]; then
  rm -f "$DEST_ROOT/$_KEYSTONE_TEST_BREAK_AFTER_SWAP/SKILL.md"
fi
if [ "${_KEYSTONE_TEST_BREAK_COORDINATOR_VALIDATOR_AFTER_SWAP:-}" = true ]; then
  rm -f "$DEST_ROOT/keystone-coordinator/scripts/validate_closure.py"
fi

verify_package_tree "$DEST_ROOT"
verify_python_entrypoints "$DEST_ROOT"
require_file "$DEST_ROOT/.keystone-install.json"
for skill in keystone-reader keystone-author keystone-coordinator; do
  require_file_parity "$WORK_STATE_CANONICAL_RUNTIME" \
    "$DEST_ROOT/$skill/scripts/work_state_runtime.py"
  require_file_parity "$WORK_STATE_CANONICAL_MANIFEST" \
    "$DEST_ROOT/$skill/scripts/work_state_runtime_manifest.json"
done
PYTHONPATH="$DEST_ROOT/keystone-linker/scripts" python3 -c \
  'from graph_runtime.readiness import context_readiness; assert callable(context_readiness)'

INSTALL_COMMITTED=true

echo "Installed:"
for skill in "${SKILLS[@]}"; do
  echo "  - $DEST_ROOT/$skill/SKILL.md"
done
echo
echo "Done. Restart Codex to load the updated Keystone skills."
