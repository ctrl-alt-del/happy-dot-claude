#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: memory-pin.sh <entry-id> [--help]

Pin a memory entry. Pinned entries are never deprecated by the forget phase.

Options:
  --help  Show this message.
EOF
  exit 0
}

ID="${1:-}"

[ -z "$ID" ] && { echo "Error: entry ID required." >&2; usage; }
[ "$ID" = "--help" ] && usage

PROJECT_DIR="$(pwd)"
META_JSON="$PROJECT_DIR/memory/meta.json"

if [ ! -f "$META_JSON" ]; then
  echo "No memory initialized. Run memory-init.sh first."
  exit 1
fi

# In full implementation: parse JSON, find entry by ID, set pinned: true
echo "[memory-pin] Pinned entry: $ID"
echo "  (This operation would update memory/meta.json with pinned: true for $ID)"
echo "  (Run with an AI agent for full JSON manipulation)"
