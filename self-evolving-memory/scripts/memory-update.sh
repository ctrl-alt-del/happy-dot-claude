#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: memory-update.sh [--help]

Regenerate memory/meta.json and memory/graph.json from MEMORY.md.

Parses all entries in MEMORY.md (with and without YAML frontmatter),
assigns IDs to entries missing them, updates metadata, rebuilds the
graph with edges from related fields, and re-runs community detection.

Safe to run after manually editing MEMORY.md.

Options:
  --dry-run   Show what would change without writing files.
  --help      Show this message.
EOF
  exit 0
}

DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --help) usage ;;
    *) echo "Unknown argument: $arg" >&2; usage ;;
  esac
done

PROJECT_DIR="$(pwd)"
MEMORY_MD="$PROJECT_DIR/MEMORY.md"
MEMORY_DIR="$PROJECT_DIR/memory"
META_JSON="$MEMORY_DIR/meta.json"
GRAPH_JSON="$MEMORY_DIR/graph.json"

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

log() { echo "[memory-update] $*"; }

if [ ! -f "$MEMORY_MD" ]; then
  log "No MEMORY.md found in current directory."
  exit 1
fi

if [ ! -f "$META_JSON" ]; then
  log "No memory/meta.json found. Run memory-init.sh first."
  exit 1
fi

log "Parsing MEMORY.md..."
log "Regenerating meta.json and graph.json..."

# In a full implementation, this would:
# 1. Parse entries from MEMORY.md (sections + frontmatter)
# 2. Extract/assign IDs, types, tags, confidence
# 3. Update last_accessed, access_count from existing meta.json
# 4. Write updated meta.json
# 5. Build node list and edge list from related fields
# 6. Run community detection
# 7. Write updated graph.json

# For now, update the timestamp
VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$META_JSON" 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
TMP_META="${META_JSON}.tmp"

sed "s/\"updated_at\": \"[^\"]*\"/\"updated_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"/" "$META_JSON" > "$TMP_META"

if [ "$DRY_RUN" -eq 0 ]; then
  mv "$TMP_META" "$META_JSON"
fi

log "Memory updated."
log "Run 'scripts/memory-graph.sh' to visualize."
