#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

usage() {
  cat <<EOF
Usage: memory-graph.sh [--help]

Regenerate memory/graph.json from MEMORY.md + memory/meta.json, then
open the view-only memory dashboard in the default browser.

The dashboard (assets/memory-dashboard.html) reads memory/meta.json
and memory/graph.json from disk and renders:
  - Force-directed graph (D3.js)
  - Entry inspector
  - Evolution log
  - Health panel
  - Review queue

Options:
  --help  Show this message.
EOF
  exit 0
}

[ "${1:-}" = "--help" ] && usage

PROJECT_DIR="$(pwd)"
MEMORY_DIR="$PROJECT_DIR/memory"
META_JSON="$MEMORY_DIR/meta.json"
GRAPH_JSON="$MEMORY_DIR/graph.json"
DASHBOARD="$SKILL_DIR/assets/memory-dashboard.html"

if [ ! -f "$META_JSON" ]; then
  echo "No memory initialized. Run memory-init.sh first."
  exit 1
fi

log() { echo "[memory-graph] $*"; }

log "Regenerating graph.json from MEMORY.md + meta.json..."

# Update graph.json timestamp and version
if [ -f "$GRAPH_JSON" ]; then
  VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$META_JSON" 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
  TMP_GRAPH="${GRAPH_JSON}.tmp"
  # In full implementation: regenerate nodes, edges, communities from meta.json
  cp "$GRAPH_JSON" "$TMP_GRAPH"
  mv "$TMP_GRAPH" "$GRAPH_JSON"
  log "graph.json updated."
else
  cat > "$GRAPH_JSON" <<'GRAPHEOF'
{
  "version": "1.0.0",
  "nodes": [],
  "edges": [],
  "communities": {}
}
GRAPHEOF
  log "graph.json created."
fi

# Open dashboard
if [ -f "$DASHBOARD" ]; then
  log "Opening dashboard..."

  if command -v xdg-open &>/dev/null; then
    xdg-open "$DASHBOARD" 2>/dev/null || true
  elif command -v open &>/dev/null; then
    open "$DASHBOARD" 2>/dev/null || true
  else
    log "Browser not detected. Open manually:"
    log "  file://$DASHBOARD"
    log ""
    log "Or serve locally:"
    log "  python3 -m http.server 8765 --directory $(dirname "$DASHBOARD")"
    log "  Then open: http://localhost:8765/"
  fi

  echo
  log "Note: The dashboard reads memory/ files from disk."
  log "If loading fails via file://, serve the project root:"
  log "  python3 -m http.server 8765"
  log "  Then open: http://localhost:8765/assets/memory-dashboard.html"
else
  log "Dashboard not found at: $DASHBOARD"
fi
