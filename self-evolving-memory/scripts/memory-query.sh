#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: memory-query.sh [--topic <tag>] [--search <terms>] [--traverse <id>] [--depth <n>] [--include-deprecated] [--json] [--help]

Query the memory for relevant knowledge.

Modes:
  --topic <tag>       Tag-based search with community context and related entries.
  --search <terms>    Free-text search against entry titles and bodies.
  --traverse <id>     BFS graph traversal from a specific entry.
  --depth <n>         Max traversal depth (default: 2).

Options:
  --include-deprecated  Include deprecated entries in results.
  --json                Output in machine-readable JSON format.
  --help                Show this message.

Examples:
  memory-query.sh --topic auth
  memory-query.sh --search "null pointer token"
  memory-query.sh --traverse mem-001 --depth 2
EOF
  exit 0
}

TOPIC=""
SEARCH=""
TRAVERSE=""
DEPTH=2
INCLUDE_DEPRECATED=0
OUTPUT_JSON=0

while [ $# -gt 0 ]; do
  case "$1" in
    --topic) TOPIC="$2"; shift 2 ;;
    --search) SEARCH="$2"; shift 2 ;;
    --traverse) TRAVERSE="$2"; shift 2 ;;
    --depth) DEPTH="$2"; shift 2 ;;
    --include-deprecated) INCLUDE_DEPRECATED=1; shift ;;
    --json) OUTPUT_JSON=1; shift ;;
    --help) usage ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

PROJECT_DIR="$(pwd)"
MEMORY_DIR="$PROJECT_DIR/memory"
META_JSON="$MEMORY_DIR/meta.json"
GRAPH_JSON="$MEMORY_DIR/graph.json"

if [ ! -f "$META_JSON" ]; then
  echo "No memory initialized. Run memory-init.sh first."
  exit 1
fi

log() { echo "[memory-query] $*"; }

# --- Query logic ---

if [ -n "$TOPIC" ]; then
  log "Querying memory for topic: $TOPIC"

  if [ "$OUTPUT_JSON" -eq 1 ]; then
    # Collect matching entries by tag
    python3 -c "
import json
with open('$META_JSON') as f:
    meta = json.load(f)
topic = '$TOPIC'.lower()
matches = [e for e in meta.get('entries', []) if topic in [t.lower() for t in e.get('tags', [])]]
print(json.dumps({'topic': topic, 'matches': len(matches), 'entries': matches}, indent=2))
" 2>/dev/null || echo '{"topic": "'"$TOPIC"'", "matches": 0, "entries": []}'
  else
    echo
    echo "=== Matching entries for topic: $TOPIC ==="
    echo
    echo "(Use with an AI agent for full results including community context"
    echo " and related entries. See references/graph-rag.md for details.)"
    echo
  fi

elif [ -n "$SEARCH" ]; then
  log "Searching memory for: $SEARCH"

  echo
  echo "=== Search results for: $SEARCH ==="
  echo
  echo "(Text similarity search. Run with an AI agent for full search"
  echo " with community context. See references/graph-rag.md for details.)"
  echo

elif [ -n "$TRAVERSE" ]; then
  log "Traversing graph from: $TRAVERSE (depth: $DEPTH)"

  echo
  echo "=== Graph traversal from $TRAVERSE (depth: $DEPTH) ==="
  echo
  echo "(BFS graph traversal. Run with an AI agent for full traversal"
  echo " results with edge types. See references/graph-rag.md for details.)"
  echo

else
  usage
fi
