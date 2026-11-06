#!/usr/bin/env bash
set -Eeuo pipefail

NS_BIN="${1:-ns}"
if ! command -v "$NS_BIN" >/dev/null 2>&1; then
  echo "NS-2 executable not found: $NS_BIN" >&2
  exit 1
fi

echo "NS-2 executable: $(command -v "$NS_BIN")"
"$NS_BIN" --version 2>&1 || true
echo
echo "Note: the custom Agent/TCP/Reno/BBR class must be compiled into this NS-2 build."
