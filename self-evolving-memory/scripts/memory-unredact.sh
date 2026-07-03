#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: memory-unredact.sh <entry-id> [--help]

Expand PII redaction markers in a memory entry using a local secrets file.
Requires .memory-secrets.local in the project root (never committed).

Format of .memory-secrets.local:
  [EMAIL] user@example.com
  [IP] 192.168.1.100

Without a secrets file, outputs a warning.

Options:
  --help  Show this message.
EOF
  exit 0
}

ID="${1:-}"

[ -z "$ID" ] && { echo "Error: entry ID required." >&2; usage; }
[ "$ID" = "--help" ] && usage

PROJECT_DIR="$(pwd)"
SECRETS_FILE="$PROJECT_DIR/.memory-secrets.local"

if [ ! -f "$SECRETS_FILE" ]; then
  echo "WARNING: No .memory-secrets.local found in project root."
  echo "Create this file with marker → value mappings to enable unredaction."
  echo
  echo "Format:"
  echo "  [EMAIL] user@example.com"
  echo "  [IP] 192.168.1.100"
  echo
  echo "This file MUST be gitignored. Do not commit."
  exit 1
fi

echo "[memory-unredact] Expanding markers for entry: $ID"
echo "  Using secrets from: $SECRETS_FILE"

# In full implementation: load entry, load secrets, replace markers
echo "  (Run with an AI agent for full expansion)"
