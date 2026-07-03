#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: memory-evolve.sh [--dry-run] [--rollback <hash>] [--dir <path>] [--phase-only <phase>] [--help]

Run the full memory evolution cycle:
  1. Distill       — Extract knowledge from raw observations.
  2. Consolidate   — Merge similar entries.
  3. Connect       — Build typed relationships.
  4. Forget        — Flag stale entries for deprecation (decay is deterministic).
  5. Promote       — Increase confidence on high-use entries.

Options:
  --dry-run            Show what would happen without making changes.
  --rollback <hash>    Restore memory state from a previous snapshot.
  --dir <path>         Path to project directory containing memory/.
  --phase-only <name>  Run only one phase: distill, consolidate, connect, forget, promote.
  --help               Show this message.

The evolution runs nightly (cron) or manually. An auto-snapshot is created
before mutations. Use --rollback to restore a previous state.
EOF
  exit 0
}

DRY_RUN=0
ROLLBACK=""
EVOLVE_ONLY=0
PHASE_ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)     DRY_RUN=1; shift ;;
    --evolve-only) EVOLVE_ONLY=1; shift ;;
    --dir)         PROJECT_DIR="$2"; shift 2 ;;
    --phase-only)  PHASE_ONLY="$2"; shift 2 ;;
    --rollback)    ROLLBACK="$2"; shift 2 ;;
    --help)        usage ;;
    *)
      if [ "${1#--}" != "$1" ]; then
        echo "Unknown argument: $1" >&2
        usage
      fi
      shift
      ;;
  esac
done

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
MEMORY_DIR="$PROJECT_DIR/memory"
META_JSON="$MEMORY_DIR/meta.json"
GRAPH_JSON="$MEMORY_DIR/graph.json"
RAW_DIR="$MEMORY_DIR/raw"
BACKUP_DIR="$MEMORY_DIR/.backup"

# Source common library
LIB_DIR="$(dirname "$0")/lib"
if [ -f "$LIB_DIR/common.sh" ]; then
  source "$LIB_DIR/common.sh"
fi

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

log() { echo "[memory-evolve] $*"; }
warn() { echo "[memory-evolve] WARNING: $*" >&2; }

# --- Rollback ---

if [ -n "$ROLLBACK" ]; then
  log "Rolling back to snapshot: $ROLLBACK"

  SNAPSHOT_DIR="$BACKUP_DIR"/*--"$ROLLBACK"
  if [ ! -d "$SNAPSHOT_DIR" ]; then
    echo "Snapshot not found: $ROLLBACK" >&2
    echo "Available snapshots:"
    ls -d "$BACKUP_DIR"/*/ 2>/dev/null | while read -r d; do basename "$d"; done
    exit 1
  fi

  log "Restoring from: $SNAPSHOT_DIR"

  run cp "$SNAPSHOT_DIR/meta.json" "$META_JSON"
  run cp "$SNAPSHOT_DIR/graph.json" "$GRAPH_JSON"
  if [ -d "$SNAPSHOT_DIR/raw" ]; then
    run rm -rf "$RAW_DIR"/*
    run cp -r "$SNAPSHOT_DIR/raw/"* "$RAW_DIR/"
  fi

  log "Rollback complete. MEMORY.md was NOT rolled back (human edits are preserved)."
  exit 0
fi

# --- Pre-flight ---

if [ ! -f "$META_JSON" ]; then
  log "No memory/meta.json found. Run memory-init.sh first."
  exit 1
fi

# --- Snapshot before evolution ---

create_snapshot() {
  local ts
  ts=$(date -u +%Y-%m-%dT%H%M%SZ)
  local version
  version=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$META_JSON" 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)".*/\1/' || echo "unknown")

  # Compute content hash from canonical serialization
  local hash_input
  hash_input=$( (grep -v 'last_accessed\|access_count\|updated_at' "$META_JSON" 2>/dev/null; cat "$GRAPH_JSON" 2>/dev/null) | sort | sha256sum | cut -c1-8)
  local snapshot_dir="$BACKUP_DIR/${ts}--v${version}--${hash_input}"

  # Deduplicate: skip if hash already exists
  if [ -d "$snapshot_dir" ]; then
    log "Snapshot $hash_input already exists (identical state). Skipping."
    return
  fi

  run mkdir -p "$snapshot_dir"
  run cp "$META_JSON" "$snapshot_dir/meta.json"
  run cp "$GRAPH_JSON" "$snapshot_dir/graph.json"
  ( cd "$snapshot_dir" && find . -type f -name '*.json' -exec sha256sum {} \; | sort -k2 > MANIFEST.sha256 )
  log "Snapshot created: $snapshot_dir"
}

create_snapshot

# --- Phase Guard ---

should_run_phase() {
  local phase="$1"
  if [ -z "$PHASE_ONLY" ]; then
    return 0
  fi
  [ "$PHASE_ONLY" = "$phase" ]
}

# --- Phase 1: Distill ---

if should_run_phase "distill"; then
log "Phase 1/5: Distill"

RAW_COUNT=$(find "$RAW_DIR" -name '*.json' -not -name '*.done' 2>/dev/null | wc -l)

if [ "$RAW_COUNT" -eq 0 ]; then
  log "  No raw observations to distill. Skipping."
else
  RAW_TOTAL=$(find "$RAW_DIR" -name '*.json' -not -name '*.done' 2>/dev/null | xargs grep -c '"text"' 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
  log "  Found $RAW_TOTAL raw observations across $RAW_COUNT files."
  log "  Send to LLM for distillation (see references/evolution-engine.md)."
  log "  (This is an LLM step — run with an AI agent for full distillation.)"
fi
fi  # phase distill

# --- Phase 2: Consolidate ---

if should_run_phase "consolidate"; then
log "Phase 2/5: Consolidate"

if [ -f "$META_JSON" ]; then
  ENTRY_COUNT=$(grep -c '"id"' "$META_JSON" 2>/dev/null || echo "0")
  log "  $ENTRY_COUNT entries in memory."
  log "  Run similarity analysis and merge overlapping entries."
  log "  (This is an LLM step — run with an AI agent for full consolidation.)"
fi
fi  # phase consolidate

# --- Phase 3: Connect ---

if should_run_phase "connect"; then
log "Phase 3/5: Connect"
log "  Build typed relationships between entries."
log "  (This is an LLM step — run with an AI agent for graph building.)"
fi  # phase connect

# --- Phase 4: Forget ---

if should_run_phase "forget"; then

log "Phase 4/5: Forget"

if [ -f "$META_JSON" ]; then
  log "  Computing decay scores..."

  NOW_EPOCH=$(date -u +%s)
  KEPT=0; FLAGGED=0; DEPRECATED=0; PINNED_SKIP=0; NEW_SKIP=0

  # Write decay script to temp file to avoid quoting issues
  DECAY_SCRIPT=$(mktemp)
  cat > "$DECAY_SCRIPT" << 'PYEOF'
import json, sys, os
from datetime import datetime, timezone

meta_file = sys.argv[1]
memory_dir = sys.argv[2]

now = datetime.now(timezone.utc)
with open(meta_file) as f:
    meta = json.load(f)

entries = meta.get('entries', [])
results = []
for e in entries:
    eid = e.get('id', '?')
    pinned = e.get('pinned', False)
    confidence = float(e.get('confidence', 0.5))
    access_count = int(e.get('access_count', 0))
    last_accessed = e.get('last_accessed', '')

    try:
        la = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
        days_since = (now - la).days
    except:
        days_since = 0
    if days_since < 0:
        days_since = 0

    created_str = e.get('created', '')
    try:
        cr = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
        created_days = (now - cr).days
    except:
        created_days = 999

    score = confidence * access_count / (days_since + 1)

    classification = 'keep'
    if pinned:
        classification = 'keep'
    elif created_days < 7:
        classification = 'keep'
    elif score < 0.2 and days_since >= 7:
        classification = 'deprecate'
    elif score < 0.5:
        classification = 'flag'
    else:
        classification = 'keep'

    results.append({
        'id': eid,
        'score': round(score, 4),
        'days_since': days_since,
        'confidence': confidence,
        'access_count': access_count,
        'pinned': pinned,
        'classification': classification
    })

for r in results:
    cls = r['classification']
    pin = ' [pinned]' if r['pinned'] else ''
    print(f"  {r['id']:12s} score={r['score']:.4f}  days={r['days_since']:3d}  conf={r['confidence']:.2f}  accesses={r['access_count']:3d}  -> {cls}{pin}")

kept = sum(1 for r in results if r['classification'] == 'keep')
flagged = sum(1 for r in results if r['classification'] == 'flag')
deprecated = sum(1 for r in results if r['classification'] == 'deprecate')
print()
print(f"  Results: {kept} kept, {flagged} flagged, {deprecated} deprecated")

with open(os.path.join(memory_dir, '.decay-results.json'), 'w') as out:
    json.dump(results, out, indent=2)
PYEOF

  python3 "$DECAY_SCRIPT" "$META_JSON" "$MEMORY_DIR" 2>&1
  rm -f "$DECAY_SCRIPT"

  if [ -f "$MEMORY_DIR/.decay-results.json" ]; then
    DEPRECATED_IDS=$(python3 -c "
import json
with open('$MEMORY_DIR/.decay-results.json') as f:
    results = json.load(f)
ids = [r['id'] for r in results if r['classification'] == 'deprecate']
print(','.join(ids))
" 2>/dev/null) || true

    if [ -n "$DEPRECATED_IDS" ]; then
      log "  Auto-deprecating entries: $DEPRECATED_IDS"
      if [ "$DRY_RUN" -eq 0 ]; then
        python3 -c "
import json
with open('$META_JSON') as f:
    meta = json.load(f)
deprecated = set('$DEPRECATED_IDS'.split(','))
for e in meta.get('entries', []):
    if e.get('id') in deprecated:
        e['deprecated'] = True
with open('$META_JSON', 'w') as f:
    json.dump(meta, f, indent=2)
"
      fi
    fi
  fi
  fi  # close META_JSON check
fi  # phase forget

# --- Phase 5: Promote ---

if should_run_phase "promote"; then
log "Phase 5/5: Promote"

if [ -f "$META_JSON" ]; then
  HIGH_ACCESS=$(grep -c '"access_count": [1-9][0-9]' "$META_JSON" 2>/dev/null || echo "0")
  if [ "$HIGH_ACCESS" -gt 0 ]; then
    log "  Found entries with high access counts eligible for promotion."
  fi
  log "  (This is an LLM step — run with an AI agent for full promotion.)"
fi
fi  # phase promote

# --- Cleanup old raw files ---

log "Cleaning up raw/ directory..."
find "$RAW_DIR" -name '*.json' -mtime +30 -not -name '*.done' 2>/dev/null | while read -r f; do
  log "  Removing stale observation: $(basename "$f")"
  run rm "$f"
done || true

# --- Garbage collect snapshots ---

MAX_SNAPSHOTS=7
SNAPSHOT_COUNT=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name '????-??-??T*--*' 2>/dev/null | wc -l | tr -d ' ') || true
SNAPSHOT_COUNT=${SNAPSHOT_COUNT:-0}
if [ "$SNAPSHOT_COUNT" -gt "$MAX_SNAPSHOTS" ] 2>/dev/null; then
  TO_DELETE=$((SNAPSHOT_COUNT - MAX_SNAPSHOTS))
  log "Garbage collecting $TO_DELETE old snapshot(s)..."
  find "$BACKUP_DIR" -maxdepth 1 -type d -name '????-??-??T*--*' 2>/dev/null | sort | head -n "$TO_DELETE" | while read -r d; do
    log "  Removing: $(basename "$d")"
    run rm -rf "$d"
  done
fi

echo
log "Evolution cycle complete."
log "Run 'scripts/memory-status.sh' for a health report."
log "Run 'scripts/memory-graph.sh' to visualize the updated graph."
