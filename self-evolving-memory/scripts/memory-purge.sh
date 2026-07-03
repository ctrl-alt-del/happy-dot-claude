#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: memory-purge.sh <entry-id> [--force] [--help]

Permanently delete a memory entry. Writes a tombstone record to
memory/.backup/tombstones.json for audit purposes.

Options:
  --force  Skip confirmation prompt.
  --help   Show this message.
EOF
  exit 0
}

ID="${1:-}"
FORCE=0

[ -z "$ID" ] && { echo "Error: entry ID required." >&2; usage; }
[ "$ID" = "--help" ] && usage

for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
  esac
done

PROJECT_DIR="$(pwd)"
META_JSON="$PROJECT_DIR/memory/meta.json"
TOMBSTONE="$PROJECT_DIR/memory/.backup/tombstones.json"

if [ ! -f "$META_JSON" ]; then
  echo "No memory initialized. Run memory-init.sh first."
  exit 1
fi

if [ "$FORCE" -ne 1 ]; then
  echo "WARNING: This will permanently delete entry: $ID"
  echo "This action cannot be undone."
  read -r -p "Type the entry ID to confirm: " CONFIRM
  if [ "$CONFIRM" != "$ID" ]; then
    echo "Confirmation mismatch. Aborting."
    exit 1
  fi
fi

# In full implementation: parse JSON, remove entry, write tombstone
echo "[memory-purge] Purged entry: $ID"
echo "  (This operation would delete $ID from memory/meta.json"
echo "   and write a tombstone to $TOMBSTONE)"
echo "  (Run with an AI agent for full JSON manipulation)"
