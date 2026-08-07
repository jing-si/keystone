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
)

echo "Repository: $REPO_ROOT"
echo "Install destination: $DEST_ROOT"

if [ ! -s "$PACKAGE_VERSION_FILE" ]; then
  echo "Missing Keystone package version: $PACKAGE_VERSION_FILE" >&2
  exit 1
fi
PACKAGE_VERSION="$(tr -d '[:space:]' < "$PACKAGE_VERSION_FILE")"

for skill in "${SKILLS[@]}"; do
  if [ ! -f "$REPO_ROOT/skills/$skill/SKILL.md" ]; then
    echo "Missing source skill: $REPO_ROOT/skills/$skill/SKILL.md" >&2
    exit 1
  fi
done

AUTHOR_VALIDATOR="$REPO_ROOT/skills/keystone-author/scripts/validate_finalization.py"
AUTHOR_VALIDATOR_RUNNER="$REPO_ROOT/skills/keystone-author/scripts/run_finalization_validation.py"
AUTHOR_VALIDATOR_HOOK="$REPO_ROOT/skills/keystone-author/scripts/check_finalization_hook.sh"
AUTHOR_FINALIZATION_GLOBAL="$REPO_ROOT/skills/keystone-author/scripts/finalization_global.py"
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
if [ ! -f "$AUTHOR_FINALIZATION_GLOBAL" ]; then
  echo "Missing Author global-state validator: $AUTHOR_FINALIZATION_GLOBAL" >&2
  exit 1
fi

LINKER_GRAPH_VALIDATOR="$REPO_ROOT/skills/keystone-linker/scripts/validate_graph.py"
LINKER_GRAPH_RUNNER="$REPO_ROOT/skills/keystone-linker/scripts/run_graph_validation.py"
LINKER_GRAPH_HOOK="$REPO_ROOT/skills/keystone-linker/scripts/check_graph_hook.sh"
LINKER_GRAPH_RUNTIME="$REPO_ROOT/skills/keystone-linker/scripts/graph_runtime/validator.py"
LINKER_REFERENCE_RUNTIME="$REPO_ROOT/skills/keystone-linker/scripts/graph_runtime/readiness.py"
LINKER_SOURCE_UNIT="$REPO_ROOT/skills/keystone-linker/scripts/graph_runtime/source_unit.py"
LINKER_GRAPH_REFERENCE="$REPO_ROOT/skills/keystone-linker/references/graph-runtime.md"
LINKER_REFERENCE_CONTRACT="$REPO_ROOT/skills/keystone-linker/references/reference-index-runtime.md"
LINKER_GRAPH_TEST="$REPO_ROOT/skills/keystone-linker/tests/test_validate_graph.py"
for source in "$LINKER_GRAPH_VALIDATOR" "$LINKER_GRAPH_RUNNER" "$LINKER_GRAPH_HOOK" \
  "$LINKER_GRAPH_RUNTIME" "$LINKER_REFERENCE_RUNTIME" "$LINKER_SOURCE_UNIT" \
  "$LINKER_GRAPH_REFERENCE" \
  "$LINKER_REFERENCE_CONTRACT" "$LINKER_GRAPH_TEST"; do
  if [ ! -f "$source" ]; then
    echo "Missing Linker graph validation package file: $source" >&2
    exit 1
  fi
done

COORDINATOR_SKILL="$REPO_ROOT/skills/keystone-coordinator/SKILL.md"
COORDINATOR_VALIDATOR="$REPO_ROOT/skills/keystone-coordinator/scripts/validate_closure.py"
COORDINATOR_ACTUAL_STATE="$REPO_ROOT/skills/keystone-coordinator/scripts/closure_actual_state.py"
COORDINATOR_V2="$REPO_ROOT/skills/keystone-coordinator/scripts/closure_v2.py"
COORDINATOR_REFERENCE="$REPO_ROOT/skills/keystone-coordinator/references/closure-validator.md"
COORDINATOR_TEST="$REPO_ROOT/skills/keystone-coordinator/tests/test_validate_closure.py"
COORDINATOR_V2_TEST="$REPO_ROOT/skills/keystone-coordinator/tests/test_validate_closure_v2.py"
for source in "$COORDINATOR_SKILL" "$COORDINATOR_VALIDATOR" "$COORDINATOR_REFERENCE" \
  "$COORDINATOR_ACTUAL_STATE" "$COORDINATOR_V2" "$COORDINATOR_TEST" \
  "$COORDINATOR_V2_TEST"; do
  if [ ! -f "$source" ]; then
    echo "Missing Coordinator closure package file: $source" >&2
    exit 1
  fi
done
python3 "$COORDINATOR_VALIDATOR" --help >/dev/null

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

INSTALLED_AUTHOR_VALIDATOR="$STAGED_SKILLS/keystone-author/scripts/validate_finalization.py"
INSTALLED_AUTHOR_VALIDATOR_RUNNER="$STAGED_SKILLS/keystone-author/scripts/run_finalization_validation.py"
INSTALLED_AUTHOR_VALIDATOR_HOOK="$STAGED_SKILLS/keystone-author/scripts/check_finalization_hook.sh"
INSTALLED_AUTHOR_FINALIZATION_GLOBAL="$STAGED_SKILLS/keystone-author/scripts/finalization_global.py"
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
if [ ! -f "$INSTALLED_AUTHOR_FINALIZATION_GLOBAL" ]; then
  echo "Install failed for Author global-state validator: $INSTALLED_AUTHOR_FINALIZATION_GLOBAL" >&2
  exit 1
fi
python3 "$INSTALLED_AUTHOR_VALIDATOR" --help >/dev/null
python3 "$INSTALLED_AUTHOR_VALIDATOR_RUNNER" --help >/dev/null
bash -n "$INSTALLED_AUTHOR_VALIDATOR_HOOK"

INSTALLED_LINKER_GRAPH_VALIDATOR="$STAGED_SKILLS/keystone-linker/scripts/validate_graph.py"
INSTALLED_LINKER_GRAPH_RUNNER="$STAGED_SKILLS/keystone-linker/scripts/run_graph_validation.py"
INSTALLED_LINKER_GRAPH_HOOK="$STAGED_SKILLS/keystone-linker/scripts/check_graph_hook.sh"
INSTALLED_LINKER_GRAPH_RUNTIME="$STAGED_SKILLS/keystone-linker/scripts/graph_runtime/validator.py"
INSTALLED_LINKER_REFERENCE_RUNTIME="$STAGED_SKILLS/keystone-linker/scripts/graph_runtime/readiness.py"
INSTALLED_LINKER_SOURCE_UNIT="$STAGED_SKILLS/keystone-linker/scripts/graph_runtime/source_unit.py"
INSTALLED_LINKER_GRAPH_REFERENCE="$STAGED_SKILLS/keystone-linker/references/graph-runtime.md"
INSTALLED_LINKER_REFERENCE_CONTRACT="$STAGED_SKILLS/keystone-linker/references/reference-index-runtime.md"
INSTALLED_LINKER_GRAPH_TEST="$STAGED_SKILLS/keystone-linker/tests/test_validate_graph.py"
for installed in "$INSTALLED_LINKER_GRAPH_VALIDATOR" "$INSTALLED_LINKER_GRAPH_RUNNER" \
  "$INSTALLED_LINKER_GRAPH_HOOK" "$INSTALLED_LINKER_GRAPH_RUNTIME" \
  "$INSTALLED_LINKER_REFERENCE_RUNTIME" "$INSTALLED_LINKER_SOURCE_UNIT" \
  "$INSTALLED_LINKER_GRAPH_REFERENCE" \
  "$INSTALLED_LINKER_REFERENCE_CONTRACT" "$INSTALLED_LINKER_GRAPH_TEST"; do
  if [ ! -f "$installed" ]; then
    echo "Install failed for Linker graph validation package file: $installed" >&2
    exit 1
  fi
done
python3 "$INSTALLED_LINKER_GRAPH_VALIDATOR" --help >/dev/null
python3 "$INSTALLED_LINKER_GRAPH_RUNNER" --help >/dev/null
bash -n "$INSTALLED_LINKER_GRAPH_HOOK"

INSTALLED_COORDINATOR_SKILL="$STAGED_SKILLS/keystone-coordinator/SKILL.md"
INSTALLED_COORDINATOR_VALIDATOR="$STAGED_SKILLS/keystone-coordinator/scripts/validate_closure.py"
INSTALLED_COORDINATOR_ACTUAL_STATE="$STAGED_SKILLS/keystone-coordinator/scripts/closure_actual_state.py"
INSTALLED_COORDINATOR_V2="$STAGED_SKILLS/keystone-coordinator/scripts/closure_v2.py"
INSTALLED_COORDINATOR_REFERENCE="$STAGED_SKILLS/keystone-coordinator/references/closure-validator.md"
INSTALLED_COORDINATOR_TEST="$STAGED_SKILLS/keystone-coordinator/tests/test_validate_closure.py"
INSTALLED_COORDINATOR_V2_TEST="$STAGED_SKILLS/keystone-coordinator/tests/test_validate_closure_v2.py"
for installed in "$INSTALLED_COORDINATOR_SKILL" "$INSTALLED_COORDINATOR_VALIDATOR" \
  "$INSTALLED_COORDINATOR_ACTUAL_STATE" "$INSTALLED_COORDINATOR_V2" \
  "$INSTALLED_COORDINATOR_REFERENCE" "$INSTALLED_COORDINATOR_TEST" \
  "$INSTALLED_COORDINATOR_V2_TEST"; do
  if [ ! -f "$installed" ]; then
    echo "Install failed for Coordinator closure package file: $installed" >&2
    exit 1
  fi
done
python3 "$INSTALLED_COORDINATOR_VALIDATOR" --help >/dev/null

SOURCE_REVISION="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || true)"
SOURCE_DIRTY=false
if [ -z "$SOURCE_REVISION" ]; then
  SOURCE_REVISION="unknown"
elif [ -n "$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null || true)" ]; then
  SOURCE_DIRTY=true
fi
printf '{"schema_version":1,"package_version":"%s","source_commit":"%s","source_dirty":%s,"skills":["keystone-init","keystone-reader","keystone-author","keystone-clarify","keystone-linker","keystone-coordinator"]}\n' \
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

echo "Installed:"
for skill in "${SKILLS[@]}"; do
  if [ -f "$DEST_ROOT/$skill/SKILL.md" ]; then
    echo "  - $DEST_ROOT/$skill/SKILL.md"
  else
    echo "Install failed for $skill" >&2
    exit 1
  fi
done

FINAL_AUTHOR_VALIDATOR="$DEST_ROOT/keystone-author/scripts/validate_finalization.py"
FINAL_AUTHOR_RUNNER="$DEST_ROOT/keystone-author/scripts/run_finalization_validation.py"
FINAL_AUTHOR_HOOK="$DEST_ROOT/keystone-author/scripts/check_finalization_hook.sh"
FINAL_AUTHOR_FINALIZATION_GLOBAL="$DEST_ROOT/keystone-author/scripts/finalization_global.py"
FINAL_LINKER_VALIDATOR="$DEST_ROOT/keystone-linker/scripts/validate_graph.py"
FINAL_LINKER_RUNNER="$DEST_ROOT/keystone-linker/scripts/run_graph_validation.py"
FINAL_LINKER_HOOK="$DEST_ROOT/keystone-linker/scripts/check_graph_hook.sh"
FINAL_REFERENCE_RUNTIME="$DEST_ROOT/keystone-linker/scripts/graph_runtime/readiness.py"
FINAL_LINKER_SOURCE_UNIT="$DEST_ROOT/keystone-linker/scripts/graph_runtime/source_unit.py"
FINAL_REFERENCE_CONTRACT="$DEST_ROOT/keystone-linker/references/reference-index-runtime.md"
FINAL_COORDINATOR_SKILL="$DEST_ROOT/keystone-coordinator/SKILL.md"
FINAL_COORDINATOR_VALIDATOR="$DEST_ROOT/keystone-coordinator/scripts/validate_closure.py"
FINAL_COORDINATOR_ACTUAL_STATE="$DEST_ROOT/keystone-coordinator/scripts/closure_actual_state.py"
FINAL_COORDINATOR_V2="$DEST_ROOT/keystone-coordinator/scripts/closure_v2.py"
FINAL_COORDINATOR_REFERENCE="$DEST_ROOT/keystone-coordinator/references/closure-validator.md"
FINAL_COORDINATOR_TEST="$DEST_ROOT/keystone-coordinator/tests/test_validate_closure.py"
FINAL_COORDINATOR_V2_TEST="$DEST_ROOT/keystone-coordinator/tests/test_validate_closure_v2.py"
for installed in "$FINAL_AUTHOR_VALIDATOR" "$FINAL_AUTHOR_RUNNER" "$FINAL_AUTHOR_HOOK" \
  "$FINAL_AUTHOR_FINALIZATION_GLOBAL" \
  "$FINAL_LINKER_VALIDATOR" "$FINAL_LINKER_RUNNER" "$FINAL_LINKER_HOOK" \
  "$FINAL_REFERENCE_RUNTIME" "$FINAL_LINKER_SOURCE_UNIT" "$FINAL_REFERENCE_CONTRACT" \
  "$FINAL_COORDINATOR_SKILL" "$FINAL_COORDINATOR_VALIDATOR" \
  "$FINAL_COORDINATOR_ACTUAL_STATE" "$FINAL_COORDINATOR_V2" \
  "$FINAL_COORDINATOR_REFERENCE" "$FINAL_COORDINATOR_TEST" "$FINAL_COORDINATOR_V2_TEST" \
  "$DEST_ROOT/.keystone-install.json"; do
  if [ ! -f "$installed" ]; then
    echo "Final installed-package verification failed: $installed" >&2
    exit 1
  fi
done
python3 "$FINAL_AUTHOR_VALIDATOR" --help >/dev/null
python3 "$FINAL_AUTHOR_RUNNER" --help >/dev/null
bash -n "$FINAL_AUTHOR_HOOK"
python3 "$FINAL_LINKER_VALIDATOR" --help >/dev/null
python3 "$FINAL_LINKER_RUNNER" --help >/dev/null
bash -n "$FINAL_LINKER_HOOK"
python3 "$FINAL_COORDINATOR_VALIDATOR" --help >/dev/null
PYTHONPATH="$DEST_ROOT/keystone-linker/scripts" python3 -c \
  'from graph_runtime.readiness import context_readiness; assert callable(context_readiness)'

INSTALL_COMMITTED=true

echo
echo "Done. Restart Codex to load the updated Keystone skills."
