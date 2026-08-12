#!/bin/sh
set -eu

SCRIPT_DIRECTORY=$(
  CDPATH= cd "$(/usr/bin/dirname "$0")" && pwd -P
)

exec /usr/bin/env -i \
  PATH=/usr/bin:/bin \
  LANG=C \
  LC_ALL=C \
  HOME=/var/empty \
  TMPDIR=/tmp \
  /usr/bin/python3 -I "$SCRIPT_DIRECTORY/run_release_gate.py" "$@"
