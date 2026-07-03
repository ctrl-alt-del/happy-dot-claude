#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: memory-promote.sh <entry-id> [--help]

Promote a memory entry. Sets confidence to 1.0 and marks as reviewed.
This is irreversible (use memory-demote.sh to flag for re-review).

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

# In full implementation: parse JSON, find entry by ID, set confidence: 1.0
echo "[memory-promote] Promoted entry: $ID → confidence 1.0"
echo "  (This operation would update memory/meta.json with confidence: 1.0 for $ID)"
echo "  (Run with an AI agent for full JSON manipulation)"
