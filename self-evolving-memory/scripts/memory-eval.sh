#!/usr/bin/env bash
set -euo pipefail

# memory-eval.sh — Run deterministic evals for self-evolving-memory.
#
# Usage:
#   ./scripts/memory-eval.sh               Run all evals.
#   ./scripts/memory-eval.sh --eval 2      Run a specific eval by ID.
#   ./scripts/memory-eval.sh --list        List available evals.
#   ./scripts/memory-eval.sh --help        Show this message.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
EVALS_DIR="$SKILL_DIR/evals"
FIXTURES_DIR="$EVALS_DIR/files"

source "$SCRIPT_DIR/lib/common.sh"

# ── CLI ───────────────────────────────────────────────────────────────────

EVAL_FILTER=""
LIST=0

usage() {
  cat <<EOF
Usage: memory-eval.sh [--eval <id>] [--list] [--keep-temp] [--help]

Run deterministic evals for self-evolving-memory.

Options:
  --eval <id>   Run only eval with given ID (1-6).
  --list        List available evals.
  --keep-temp   Keep temp directories after eval (for debugging).
  --help        Show this message.
EOF
  exit 0
}

KEEP_TEMP=0

while [ $# -gt 0 ]; do
  case "$1" in
    --eval) EVAL_FILTER="$2"; shift 2 ;;
    --list) LIST=1; shift ;;
    --keep-temp) KEEP_TEMP=1; shift ;;
    --help) usage ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

if [ "$LIST" -eq 1 ]; then
  echo "Available evals:"
  python3 -c "
import json
with open('$EVALS_DIR/evals.json') as f:
    data = json.load(f)
for e in data['evals']:
    print(f\"  {e['id']}: {e['prompt']}\")
"
  exit 0
fi

# ── Eval Runner ────────────────────────────────────────────────────────────

TOTAL_PASSED=0
TOTAL_FAILED=0
EVALS_RUN=0

run_eval() {
  local eval_id="$1"
  local prompt="$2"

  echo
  echo "═══════════════════════════════════════════"
  echo "  Eval $eval_id: $prompt"
  echo "═══════════════════════════════════════════"
  echo

  reset_asserts
}

finish_eval() {
  print_assert_summary
  TOTAL_PASSED=$((TOTAL_PASSED + ASSERT_PASSED))
  TOTAL_FAILED=$((TOTAL_FAILED + ASSERT_FAILED))
  EVALS_RUN=$((EVALS_RUN + 1))
}

# ── Eval 2: Status Report ─────────────────────────────────────────────────

eval_2() {
  run_eval 2 "Status report accuracy"

  setup_temp
  trap cleanup_temp EXIT

  mkdir -p "$TEMP_DIR/memory"

  cp "$FIXTURES_DIR/meta-sample.json" "$TEMP_DIR/memory/meta.json"
  cp "$FIXTURES_DIR/graph-sample.json" "$TEMP_DIR/memory/graph.json"

  local output
  output=$(bash "$SCRIPT_DIR/memory-status.sh" --dir "$TEMP_DIR" --json 2>&1)
  local exit_code=$?

  assert_exit_code "$exit_code" 0 "memory-status.sh should exit 0"

  echo "  JSON output: ${output:0:200}..."
  echo ""

  # Parse all JSON fields in one python call
  local parsed
  parsed=$(echo "$output" | python3 -c "
import json, sys
d = json.load(sys.stdin)
e = d['entries']
g = d['graph']
print(e['total'])
print(e['active'])
print(e['deprecated'])
print(e['pinned'])
print(e['by_type']['gotcha'])
print(e['by_type']['pattern'])
print(e['by_type']['decision'])
print(e['by_type']['fact'])
print(g['nodes'])
print(g['edges'])
print(g['communities'])
" 2>/dev/null || echo -e "0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0")

  IFS=$'\n' read -r -d '' total active deprecated pinned gotchas patterns decisions facts nodes edges communities <<<"$parsed" 2>/dev/null || true
  total=${total:-0}; active=${active:-0}; deprecated=${deprecated:-0}; pinned=${pinned:-0}
  gotchas=${gotchas:-0}; patterns=${patterns:-0}; decisions=${decisions:-0}; facts=${facts:-0}
  nodes=${nodes:-0}; edges=${edges:-0}; communities=${communities:-0}

  [ "$total" = "5" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: total=$total, expected 5" >&2; }
  [ "$active" = "3" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: active=$active, expected 3" >&2; }
  [ "$deprecated" = "2" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: deprecated=$deprecated, expected 2" >&2; }
  [ "$pinned" = "2" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: pinned=$pinned, expected 2" >&2; }
  [ "$gotchas" = "3" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: gotchas=$gotchas, expected 3" >&2; }
  [ "$patterns" = "1" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: patterns=$patterns, expected 1" >&2; }
  [ "$decisions" = "1" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: decisions=$decisions, expected 1" >&2; }
  [ "$facts" = "0" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: facts=$facts, expected 0" >&2; }
  [ "$nodes" = "5" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: nodes=$nodes, expected 5" >&2; }
  [ "$edges" = "3" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: edges=$edges, expected 3" >&2; }
  [ "$communities" = "2" ] && ASSERT_PASSED=$((ASSERT_PASSED + 1)) || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: communities=$communities, expected 2" >&2; }

  cleanup_temp
  trap - EXIT
  finish_eval
}

# ── Eval 5: Decay ─────────────────────────────────────────────────────────

eval_5() {
  run_eval 5 "Decay function correctness"

  setup_temp
  trap cleanup_temp EXIT

  mkdir -p "$TEMP_DIR/memory"

  cp "$FIXTURES_DIR/decay-input.json" "$TEMP_DIR/memory/meta.json"
  echo '{"version":"1.0.0","nodes":[],"edges":[],"communities":{}}' > "$TEMP_DIR/memory/graph.json"

  local output
  output=$(bash "$SCRIPT_DIR/memory-evolve.sh" --dir "$TEMP_DIR" --phase-only forget 2>&1)
  local exit_code=$?

  assert_exit_code "$exit_code" 0 "memory-evolve.sh forget should exit 0"

  echo "$output"

  # Check classifications
  assert_contains "$output" "mem-020" "frequently accessed entry"
  assert_contains "$output" "mem-021" "rarely accessed entry"
  assert_contains "$output" "mem-022" "pinned entry"
  assert_contains "$output" "mem-023" "new entry"

  # mem-020 (access_count=20, 2 days, conf=0.9): score = 0.9*20/(2+1) = 6.0 → keep
  assert_contains "$output" "mem-020" && echo "$output" | grep "mem-020" | grep -q "keep" \
    && ASSERT_PASSED=$((ASSERT_PASSED + 1)) \
    || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: mem-020 should be kept (high access)" >&2; }

  # mem-021 (access_count=2, 90 days, conf=0.6): score = 0.6*2/(90+1) = 0.013 → deprecate
  echo "$output" | grep "mem-021" | grep -qE "deprecate|flag" \
    && ASSERT_PASSED=$((ASSERT_PASSED + 1)) \
    || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: mem-021 should be flagged/deprecated (rarely accessed)" >&2; }

  # mem-022 (pinned, access_count=1, 150 days): pinned → keep regardless
  echo "$output" | grep "mem-022" | grep -q "keep" \
    && ASSERT_PASSED=$((ASSERT_PASSED + 1)) \
    || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: mem-022 should be kept (pinned)" >&2; }

  # mem-023 (0 accesses, 1 day): created within 7 days → keep
  echo "$output" | grep "mem-023" | grep -q "keep" \
    && ASSERT_PASSED=$((ASSERT_PASSED + 1)) \
    || { ASSERT_FAILED=$((ASSERT_FAILED + 1)); echo "  FAIL: mem-023 should be kept (grace period)" >&2; }

  cleanup_temp
  trap - EXIT
  finish_eval
}

# ── Eval 6: PII Scrubbing ─────────────────────────────────────────────────

eval_6() {
  run_eval 6 "PII redaction correctness"

  local input
  input=$(cat "$FIXTURES_DIR/pii-input.txt")

  local scrubbed
  scrubbed=$(scrub_pii "$input")

  echo "  Scrubbed output:"
  echo "$scrubbed" | head -20
  echo ""

  # Check replacements
  assert_not_contains "$scrubbed" "john@example.com" "email should be scrubbed"
  assert_contains "$scrubbed" "[EMAIL]" "email placeholder present"

  assert_not_contains "$scrubbed" "192.168.1.42" "IP should be scrubbed"
  assert_contains "$scrubbed" "[IP]" "IP placeholder present"

  assert_contains "$scrubbed" "[TOKEN]" "JWT token should be scrubbed"

  assert_contains "$scrubbed" "[PHONE]" "phone number should be scrubbed"

  assert_not_contains "$scrubbed" "/home/alice/" "username path should be scrubbed"
  assert_contains "$scrubbed" "[PATH]" "path placeholder present"

  assert_contains "$scrubbed" "auth" "non-PII text preserved"
  assert_contains "$scrubbed" "middleware" "non-PII text preserved"

  finish_eval
}

# ── Eval 1: Init from plain MEMORY.md ─────────────────────────────────────

eval_1() {
  run_eval 1 "Init from plain MEMORY.md"

  setup_temp
  trap cleanup_temp EXIT

  cp "$FIXTURES_DIR/plain-memory.md" "$TEMP_DIR/MEMORY.md"

  local output
  output=$(cd "$TEMP_DIR" && bash "$SCRIPT_DIR/memory-init.sh" 2>&1)
  local exit_code=$?

  echo "$output"

  assert_exit_code "$exit_code" 0 "memory-init.sh should exit 0"

  assert_file_exists "$TEMP_DIR/memory/meta.json" "meta.json"
  assert_file_exists "$TEMP_DIR/memory/graph.json" "graph.json"
  assert_file_exists "$TEMP_DIR/memory/.backup/$(date -u +%Y-%m-%d)--pre-migration/MEMORY.md" "backup of MEMORY.md"

  # Check gitignore
  assert_file_exists "$TEMP_DIR/.gitignore" ".gitignore"
  local gitignore
  gitignore=$(cat "$TEMP_DIR/.gitignore" 2>/dev/null || echo "")
  assert_contains "$gitignore" "memory/raw/" "gitignore excludes raw/"
  assert_contains "$gitignore" "memory/.backup/" "gitignore excludes .backup/"

  # Check meta.json has version
  if [ -f "$TEMP_DIR/memory/meta.json" ]; then
    assert_contains "$(cat "$TEMP_DIR/memory/meta.json")" '"version"' "meta.json has version field"
  fi

  cleanup_temp
  trap - EXIT
  finish_eval
}

# ── Main ───────────────────────────────────────────────────────────────────

main() {
  echo "Self-Evolving Memory — Eval Runner"
  echo "=================================="
  echo

  if [ -n "$EVAL_FILTER" ]; then
    case "$EVAL_FILTER" in
      1) eval_1 ;;
      2) eval_2 ;;
      5) eval_5 ;;
      6) eval_6 ;;
      *) echo "Eval $EVAL_FILTER not available deterministically (evals 3-4 require LLM)." >&2; exit 1 ;;
    esac
  else
    eval_1
    eval_2
    eval_5
    eval_6
  fi

  echo
  echo "═══════════════════════════════════════════"
  echo "  Summary: $EVALS_RUN evals, $TOTAL_PASSED passed, $TOTAL_FAILED failed"
  echo "═══════════════════════════════════════════"

  if [ "$TOTAL_FAILED" -gt 0 ]; then
    exit 1
  fi
}

main
