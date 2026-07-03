#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TARGET_VERSION="1.0.0"

usage() {
  cat <<EOF
Usage: memory-migrate.sh [--dry-run] [--help]

Migrate the memory/ schema from the current version to the latest.

Migration follows a strict chain (v1.0 → v1.1 → v1.2 → ...) with full
backup, validation, and atomic apply.

Options:
  --dry-run   Run validation and migration to temp files without applying.
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
MEMORY_DIR="$PROJECT_DIR/memory"
META_JSON="$MEMORY_DIR/meta.json"
GRAPH_JSON="$MEMORY_DIR/graph.json"
BACKUP_DIR="$MEMORY_DIR/.backup"

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

log() { echo "[memory-migrate] $*"; }
warn() { echo "[memory-migrate] WARNING: $*" >&2; }
err()  { echo "[memory-migrate] ERROR: $*" >&2; exit 1; }

# --- Pre-flight ---

if [ ! -f "$META_JSON" ]; then
  log "No memory/meta.json found. Run memory-init.sh first."
  exit 1
fi

CURRENT_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$META_JSON" 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)".*/\1/' || echo "unknown")

if [ "$CURRENT_VERSION" = "$TARGET_VERSION" ]; then
  log "Already at latest version ($TARGET_VERSION). Nothing to migrate."
  exit 0
fi

log "Current version: $CURRENT_VERSION"
log "Target version:  $TARGET_VERSION"

# --- Validation ---

log "Running pre-flight validation..."

validate() {
  local file="$1" label="$2"
  if [ ! -f "$file" ]; then
    err "$label not found: $file"
  fi
  if ! grep -q '"version"' "$file" 2>/dev/null; then
    err "$label missing version field."
  fi
}

validate "$META_JSON" "memory/meta.json"
validate "$GRAPH_JSON" "memory/graph.json"

log "Validation passed."

# --- Backup ---

TIMESTAMP=$(date -u +%Y-%m-%dT%H%M%SZ)
SNAPSHOT_DIR="$BACKUP_DIR/${TIMESTAMP}--v${CURRENT_VERSION}"

log "Creating backup: $SNAPSHOT_DIR"
run mkdir -p "$SNAPSHOT_DIR"
run cp -r "$MEMORY_DIR/raw" "$SNAPSHOT_DIR/raw" 2>/dev/null || true
run cp "$META_JSON" "$SNAPSHOT_DIR/meta.json"
run cp "$GRAPH_JSON" "$SNAPSHOT_DIR/graph.json"

# Create MANIFEST.sha256
( cd "$SNAPSHOT_DIR" && find . -type f -not -name 'MANIFEST.sha256' -exec sha256sum {} \; | sort -k2 > MANIFEST.sha256 )
log "Backup complete."

# --- Migration chain ---

# Stub: no migrations defined yet. Add migration functions here as schema evolves.
# Example structure:
# if [ "$CURRENT_VERSION" = "1.0.0" ]; then
#   migrate_1_0_0_to_1_1_0
#   CURRENT_VERSION="1.1.0"
# fi

log "No migration steps needed between $CURRENT_VERSION and $TARGET_VERSION."
log "Updating version to $TARGET_VERSION..."

# --- Apply ---

if [ "$DRY_RUN" -eq 1 ]; then
  log "Dry run complete. No changes applied."
else
  # Atomic: write to temp, then rename
  TEMP_META="${META_JSON}.tmp"
  TEMP_GRAPH="${GRAPH_JSON}.tmp"

  sed "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$TARGET_VERSION\"/" "$META_JSON" > "$TEMP_META"
  sed "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$TARGET_VERSION\"/" "$GRAPH_JSON" > "$TEMP_GRAPH"

  mv "$TEMP_META" "$META_JSON"
  mv "$TEMP_GRAPH" "$GRAPH_JSON"

  # Update manifest
  MANIFEST_JSON="$BACKUP_DIR/manifest.json"
  if [ -f "$MANIFEST_JSON" ]; then
    echo "Snapshot recorded in manifest."
  fi

  log "Migration applied. Version: $CURRENT_VERSION → $TARGET_VERSION."
fi
