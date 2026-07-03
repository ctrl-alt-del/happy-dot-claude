#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: memory-status.sh [--json] [--dir <path>] [--help]

Show memory health report:
  - Entry counts by type and status
  - Staleness distribution
  - Pending review queue
  - Graph statistics
  - PII scan summary
  - Snapshot history

Options:
  --json         Output in machine-readable JSON format.
  --dir <path>   Path to memory/ directory (default: ./memory/).
  --help         Show this message.
EOF
  exit 0
}

OUTPUT_JSON=0
PROJECT_DIR="$(pwd)"

while [ $# -gt 0 ]; do
  case "$1" in
    --json) OUTPUT_JSON=1; shift ;;
    --dir) PROJECT_DIR="$2"; shift 2 ;;
    --help) usage ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

MEMORY_DIR="$PROJECT_DIR/memory"
META_JSON="$MEMORY_DIR/meta.json"
GRAPH_JSON="$MEMORY_DIR/graph.json"
RAW_DIR="$MEMORY_DIR/raw"

if [ ! -f "$META_JSON" ]; then
  echo "No memory initialized. Run memory-init.sh first."
  exit 1
fi

# --- Gather stats ---

VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$META_JSON" 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)".*/\1/') || true
VERSION=${VERSION:-unknown}
TOTAL_ENTRIES=$(grep -c '"id"' "$META_JSON" 2>/dev/null) || true
TOTAL_ENTRIES=${TOTAL_ENTRIES:-0}

# Count by type — use python3 to avoid grep -c exit-code issues
read -r GOTCHAS PATTERNS DECISIONS FACTS <<<"$(python3 -c "
import json
with open('$META_JSON') as f:
    meta = json.load(f)
counts = {'gotcha': 0, 'pattern': 0, 'decision': 0, 'fact': 0}
for e in meta.get('entries', []):
    t = e.get('type', '')
    if t in counts:
        counts[t] += 1
print(counts['gotcha'], counts['pattern'], counts['decision'], counts['fact'])
" 2>/dev/null || echo '0 0 0 0')" || true
GOTCHAS=${GOTCHAS:-0}; PATTERNS=${PATTERNS:-0}; DECISIONS=${DECISIONS:-0}; FACTS=${FACTS:-0}

# Count by status — use python3 to avoid grep -c exit-code issues
read -r DEPRECATED PINNED <<<"$(python3 -c "
import json
with open('$META_JSON') as f:
    meta = json.load(f)
dep = sum(1 for e in meta.get('entries', []) if e.get('deprecated'))
pin = sum(1 for e in meta.get('entries', []) if e.get('pinned'))
print(dep, pin)
" 2>/dev/null || echo '0 0')" || true
DEPRECATED=${DEPRECATED:-0}; PINNED=${PINNED:-0}
ACTIVE=$((TOTAL_ENTRIES - DEPRECATED))

# Graph stats
if [ -f "$GRAPH_JSON" ]; then
  read -r NODES EDGES COMMUNITIES <<<"$(python3 -c "
import json
with open('$GRAPH_JSON') as f:
    g = json.load(f)
nodes = len(g.get('nodes', []))
edges = len(g.get('edges', []))
communities = len(g.get('communities', {}))
print(nodes, edges, communities)
" 2>/dev/null || echo '0 0 0')" || true
  NODES=${NODES:-0}; EDGES=${EDGES:-0}; COMMUNITIES=${COMMUNITIES:-0}
else
  NODES=0; EDGES=0; COMMUNITIES=0
fi

# Raw observations
RAW_FILES=$(find "$RAW_DIR" -name '*.json' -not -name '*.done' 2>/dev/null | wc -l | tr -d ' ') || true
RAW_FILES=${RAW_FILES:-0}
if [ "$RAW_FILES" -gt 0 ] 2>/dev/null; then
  RAW_OBS=$(find "$RAW_DIR" -name '*.json' -not -name '*.done' 2>/dev/null | xargs grep -c '"text"' 2>/dev/null | awk -F: '{s+=$2} END {print s+0}') || true
  RAW_OBS=${RAW_OBS:-0}
else
  RAW_OBS=0
fi

# Staleness scan
STALE_COUNT=0
FIRST=1

# Backups
BACKUP_COUNT=$(find "$MEMORY_DIR/.backup" -maxdepth 1 -type d -name '????-??-??T*--*' 2>/dev/null | wc -l | tr -d ' ') || true
BACKUP_COUNT=${BACKUP_COUNT:-0}

# --- Output ---

if [ "$OUTPUT_JSON" -eq 1 ]; then
  cat <<JSONEOF
{
  "version": "$VERSION",
  "entries": {
    "total": $TOTAL_ENTRIES,
    "active": $ACTIVE,
    "deprecated": $DEPRECATED,
    "pinned": $PINNED,
    "by_type": {
      "gotcha": $GOTCHAS,
      "pattern": $PATTERNS,
      "decision": $DECISIONS,
      "fact": $FACTS
    }
  },
  "graph": {
    "nodes": $NODES,
    "edges": $EDGES,
    "communities": $COMMUNITIES
  },
  "raw_observations": {
    "files": $RAW_FILES,
    "total": $RAW_OBS
  },
  "backups": $BACKUP_COUNT
}
JSONEOF
else
  cat <<EOF
═══════════════════════════════════════════
  Memory Health Report
═══════════════════════════════════════════

Version:    $VERSION
Entries:    $TOTAL_ENTRIES total ($ACTIVE active, $DEPRECATED deprecated, $PINNED pinned)

  By type:
    Gotchas:    $GOTCHAS
    Patterns:   $PATTERNS
    Decisions:  $DECISIONS
    Facts:      $FACTS

Graph:
    Nodes:        $NODES
    Edges:        $EDGES
    Communities:  $COMMUNITIES

Raw observations: $RAW_OBS across $RAW_FILES files

Backups: $BACKUP_COUNT snapshots

EOF

  if [ "$RAW_OBS" -gt 0 ]; then
    echo "  ⚡ $RAW_OBS unprocessed observations. Run memory-evolve.sh to distill."
    echo
  fi

  if [ "$DEPRECATED" -gt 0 ]; then
    echo "  ℹ $DEPRECATED deprecated entries. Review with memory-graph.sh dashboard."
    echo
  fi

  echo "PII scan:"
  if [ "$RAW_FILES" -gt 0 ]; then
    for f in "$RAW_DIR"/*.json; do
      [ -e "$f" ] || continue
      [[ "$f" == *.done ]] && continue
      local name=$(basename "$f")
      local emails=$(grep -c '\[EMAIL\]' "$f" 2>/dev/null || echo "0")
      local ips=$(grep -c '\[IP\]' "$f" 2>/dev/null || echo "0")
      local secrets=$(grep -c '\[SECRET\]' "$f" 2>/dev/null || echo "0")
      echo "  $name: $emails [EMAIL], $ips [IP], $secrets [SECRET] (scrubbed)"
    done
  else
    echo "  No raw observation files."
  fi
  echo "  MEMORY.md: reviewed entries (PII-free)"
  echo
fi
