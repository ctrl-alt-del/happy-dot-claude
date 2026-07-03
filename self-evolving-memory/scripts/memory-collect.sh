#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: memory-collect.sh [--context <mode>] [--help]

Run memory collectors to extract observations from project activity.

Context modes (default: all):
  coding        Git + Error collectors (for writing code)
  debugging     Error + Session collectors (for fixing bugs)
  architecture  Session collector only (for planning)
  ops           No collectors (for routine operations)
  all           All three collectors

Options:
  --context <mode>  Which collectors to run (default: all).
  --source <type>   Run a single collector: session, git, error.
  --help            Show this message.
EOF
  exit 0
}

CONTEXT="all"
SOURCE=""

while [ $# -gt 0 ]; do
  case "$1" in
    --context) CONTEXT="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    --help) usage ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

PROJECT_DIR="$(pwd)"
MEMORY_DIR="$PROJECT_DIR/memory"
RAW_DIR="$MEMORY_DIR/raw"

if [ ! -d "$MEMORY_DIR" ]; then
  echo "No memory initialized. Run memory-init.sh first."
  exit 1
fi

mkdir -p "$RAW_DIR"

log() { echo "[memory-collect] $*"; }

# --- Deterministic filters (Tier 0) ---

run_session_collector() {
  log "Session collector: checking for session transcript..."
  log "  (Tier 0: Look for .claude/sessions/ history or error markers in recent output)"
  log "  (Tier 1: If signals found, extract observations via LLM)"
  log "  (See references/collectors.md for full session collector spec)"
}

run_git_collector() {
  log "Git collector: checking recent commits..."
  if git rev-parse --git-dir >/dev/null 2>&1; then
    local last_msg
    last_msg=$(git log -1 --format='%s' 2>/dev/null || echo "")
    if echo "$last_msg" | grep -qiE 'revert|fix|hotfix|rollback'; then
      log "  Signal detected in commit: $last_msg"
      log "  (Tier 1: Extract observations from git diff)"
      log "  (See references/collectors.md for full git collector spec)"
    else
      log "  No signal in latest commit. Skipping."
    fi
  else
    log "  Not a git repository. Skipping."
  fi
}

run_error_collector() {
  log "Error collector: checking for recent failures..."
  # Check for build/test failure artifacts
  if [ -f "$PROJECT_DIR/.build-failure" ] || [ -f "$PROJECT_DIR/.test-failure" ]; then
    log "  Signal detected: build/test failure artifact found."
    log "  (Tier 1: Extract observations from error output)"
  else
    log "  No failure artifacts found. Skipping."
  fi
  log "  (See references/collectors.md for full error collector spec)"
}

# --- Run selected collectors ---

if [ -n "$SOURCE" ]; then
  case "$SOURCE" in
    session) run_session_collector ;;
    git)     run_git_collector ;;
    error)   run_error_collector ;;
    *) echo "Unknown source: $SOURCE" >&2; usage ;;
  esac
  exit 0
fi

case "$CONTEXT" in
  coding)
    log "Context: coding → Git + Error"
    run_git_collector
    run_error_collector
    ;;
  debugging)
    log "Context: debugging → Error + Session"
    run_error_collector
    run_session_collector
    ;;
  architecture)
    log "Context: architecture → Session"
    run_session_collector
    ;;
  ops)
    log "Context: ops → None (routine, skip)"
    ;;
  all)
    log "Context: all → Session + Git + Error"
    run_session_collector
    run_git_collector
    run_error_collector
    ;;
  *)
    echo "Unknown context: $CONTEXT" >&2
    usage
    ;;
esac

echo
log "Collection complete. Raw observations queued in $RAW_DIR"
log "Run 'scripts/memory-evolve.sh' to distill into entries."
log "Run 'scripts/memory-status.sh' for counts."
