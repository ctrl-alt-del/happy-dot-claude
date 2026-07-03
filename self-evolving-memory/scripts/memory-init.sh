#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"

usage() {
  cat <<EOF
Usage: memory-init.sh [--help]

Initialize self-evolving memory for the current project.

Handles three onboarding scenarios:
  1. Fresh project (no MEMORY.md, no memory/):   scaffolds from templates.
  2. Plain MEMORY.md (no frontmatter):           parses, enriches, creates memory/.
  3. Existing memory/ (may need migration):      reports version, offers migration.

Options:
  --dry-run   Show what would happen without making changes.
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

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

log() { echo "[memory-init] $*"; }
warn() { echo "[memory-init] WARNING: $*" >&2; }

# --- Scenario detection ---

if [ -f "$META_JSON" ]; then
  CURRENT_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$META_JSON" 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)".*/\1/' || echo "unknown")

  if [ "$CURRENT_VERSION" = "$VERSION" ]; then
    log "Memory already initialized at version $VERSION. Nothing to do."
    exit 0
  else
    log "Memory exists at version $CURRENT_VERSION. Target version: $VERSION."
    log "Run: scripts/memory-migrate.sh"
    exit 0
  fi
fi

# --- Scenario 1: Fresh project ---

init_fresh() {
  log "Scenario: Fresh project — scaffolding memory from templates."

  if [ -f "$MEMORY_MD" ]; then
    log "Existing MEMORY.md found. Will enrich it (Scenario 2)."
    init_from_plain_md
    return
  fi

  log "Creating MEMORY.md template..."
  cat > "$MEMORY_MD" <<'MEMORYEOF'
# MEMORY — Accumulated Project Knowledge

## 🧠 Tech Gotchas
<!-- Tagged: #api #ui #build #security #data #infra #auth -->
<!-- ⚡ = broke in production, non-negotiable guardrail -->

## 🔧 Patterns That Worked
<!-- Reusable patterns discovered across features -->

## 📐 Architecture Decisions
<!-- ADRs made during development -->

## 📂 Code Ownership Map
| File | Touched By | Why |
|------|-----------|-----|

## 🐛 Common Bugs Fixed

## 📋 Facts
<!-- Ownership, dependencies, constraints, and other durable facts about the project -->
MEMORYEOF
  log "Created: $MEMORY_MD"

  mkdir_memory_dir
}

# --- Scenario 2: Plain MEMORY.md ---

init_from_plain_md() {
  log "Scenario: Existing MEMORY.md — parsing and enriching."

  local backup_dir="$MEMORY_DIR/.backup/$(date -u +%Y-%m-%d)--pre-migration"
  run mkdir -p "$backup_dir"
  run cp "$MEMORY_MD" "$backup_dir/MEMORY.md"
  log "Backed up MEMORY.md to $backup_dir/MEMORY.md"

  local entry_count
  entry_count=$(grep -c '^## ' "$MEMORY_MD" 2>/dev/null || echo "0")
  log "Found approximately $entry_count potential entries."

  mkdir_memory_dir

  log "MEMORY.md entries will be enriched with frontmatter metadata on first evolution."
  log "Run 'scripts/memory-evolve.sh' to parse and assign IDs."
}

mkdir_memory_dir() {
  log "Creating memory/ directory structure..."
  run mkdir -p "$MEMORY_DIR/raw"
  run mkdir -p "$MEMORY_DIR/.backup"

  cat > "$META_JSON" <<METAEOF
{
  "version": "$VERSION",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "entries": []
}
METAEOF
  log "Created: $META_JSON"

  cat > "$MEMORY_DIR/graph.json" <<GRAPHEOF
{
  "version": "$VERSION",
  "nodes": [],
  "edges": [],
  "communities": {}
}
GRAPHEOF
  log "Created: $MEMORY_DIR/graph.json"

  cat > "$MEMORY_DIR/.backup/manifest.json" <<MANIFESTEOF
{
  "snapshots": [],
  "retention": {"max_snapshots": 7, "min_age_days": 0}
}
MANIFESTEOF
  log "Created: $MEMORY_DIR/.backup/manifest.json"

  add_gitignore
}

add_gitignore() {
  local gitignore="$PROJECT_DIR/.gitignore"
  local need_update=0

  if ! grep -q '^memory/raw/$' "$gitignore" 2>/dev/null; then
    need_update=1
  fi
  if ! grep -q '^memory/\.backup/$' "$gitignore" 2>/dev/null; then
    need_update=1
  fi

  if [ "$need_update" -eq 1 ]; then
    cat >> "$gitignore" <<'GITIGNOREEOF'

# Self-evolving memory — raw observations may contain residual PII
memory/raw/
memory/.backup/
GITIGNOREEOF
    log "Updated .gitignore with memory/ exclusions."
  else
    log ".gitignore already has memory/ exclusions."
  fi
}

# --- Main ---

if [ -f "$MEMORY_MD" ]; then
  init_from_plain_md
else
  init_fresh
fi

echo
log "Memory scaffolded at version $VERSION."
log "Next steps:"
log "  1. Collect observations:  scripts/memory-collect.sh --context all"
log "  2. Evolve the memory:     scripts/memory-evolve.sh"
log "  3. Query the memory:      scripts/memory-query.sh --topic <tag>"
log "  4. Open dashboard:        scripts/memory-graph.sh"
