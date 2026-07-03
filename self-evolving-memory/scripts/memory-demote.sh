#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: memory-demote.sh <entry-id> [--help]

Flag a memory entry for review. Drops confidence and adds to the review
queue. Unlike purge, the entry is not deleted — it stays in memory but
with reduced confidence.

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

# In full implementation: parse JSON, find entry by ID, set confidence: 0.3
echo "[memory-demote] Demoted entry: $ID → flagged for review"
echo "  (This operation would update memory/meta.json with reduced confidence for $ID)"
echo "  (Run with an AI agent for full JSON manipulation)"
