#!/usr/bin/env bash
# common.sh — Shared utilities for self-evolving-memory scripts.
# Source this file: source "$(dirname "$0")/lib/common.sh"

set -euo pipefail

# ── PII Scrubbing ──────────────────────────────────────────────────────────

scrub_pii() {
  local input="$1"
  printf '%s' "$input" | sed -E \
    -e 's|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[EMAIL]|g' \
    -e 's|([0-9]{1,3}\.){3}[0-9]{1,3}|[IP]|g' \
    -e 's/(sk|pk|api|token|key|secret)[-_][a-zA-Z0-9]{20,}/[SECRET]/g' \
    -e 's|AKIA[0-9A-Z]{16}|[SECRET]|g' \
    -e 's|ghp_[0-9a-zA-Z]{36}|[SECRET]|g' \
    -e 's|eyJ[a-zA-Z0-9_=+-]+\.[a-zA-Z0-9_=+-]+\.[a-zA-Z0-9_=+-]+|[TOKEN]|g' \
    -e 's|\+?[0-9][0-9 ()-]{7,}[0-9]|[PHONE]|g' \
    -e 's|/home/[a-zA-Z0-9._-]+/|[PATH]/|g' \
    -e 's|/Users/[a-zA-Z0-9._-]+/|[PATH]/|g'
}

# ── Decay Computation ─────────────────────────────────────────────────────

# score = confidence * access_count / (days_since_last_access + 1)
# Thresholds: ≥0.5 keep, 0.2-0.5 flag, <0.2 for ≥7d deprecate
compute_decay() {
  local confidence="$1"
  local access_count="$2"
  local last_accessed="$3"

  local now_epoch
  now_epoch=$(date -u +%s)
  local access_epoch
  access_epoch=$(date -u -d "$last_accessed" +%s 2>/dev/null || echo "$now_epoch")

  local days_since=$(( (now_epoch - access_epoch) / 86400 ))
  if [ "$days_since" -lt 0 ]; then days_since=0; fi

  python3 -c "
confidence = float('$confidence')
access_count = int('$access_count')
days = int('$days_since')
score = confidence * access_count / (days + 1)
print(round(score, 4))
"
}

# Usage: classify_decay <score> <days_since_last_access> <pinned> <created_days_ago>
# Returns: keep | flag | deprecate
classify_decay() {
  local score="$1"
  local days_since="$2"
  local pinned="$3"
  local created_days_ago="$4"

  if [ "$pinned" = "true" ]; then
    echo "keep"
    return
  fi

  if [ "$created_days_ago" -lt 7 ]; then
    echo "keep"
    return
  fi

  local cmp
  cmp=$(python3 -c "
s = float('$score')
d = int('$days_since')
if s < 0.2 and d >= 7:
    print('deprecate')
elif s < 0.5:
    print('flag')
else:
    print('keep')
")
  echo "$cmp"
}

# ── JSON Helpers ───────────────────────────────────────────────────────────

# Extract a field value from a JSON object (simple grep-based, works for
# string, number, bool fields at the top level of a single object).
# Usage: json_field <json-string> <field-name>
json_field() {
  local json="$1" field="$2"
  echo "$json" | grep -o "\"$field\"[[:space:]]*:[[:space:]]*[^,}]*" | head -1 | sed 's/.*:[[:space:]]*//' | sed 's/^"//;s/"$//' | xargs
}

# Check if jq or python3 is available for JSON operations.
has_json_tool() {
  command -v jq >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1
}

# Parse JSON entries array into a list of entry JSON strings.
# Uses python3 to split the entries array.
# Returns newline-separated entry JSON objects.
parse_entries() {
  local file="$1"
  python3 -c "
import json, sys
with open('$file') as f:
    data = json.load(f)
entries = data.get('entries', [])
for e in entries:
    print(json.dumps(e))
"
}

# ── File Helpers ───────────────────────────────────────────────────────────

# Create a temp directory and clean up on exit.
# Usage: setup_temp && trap cleanup_temp EXIT
TEMP_DIR=""
setup_temp() {
  TEMP_DIR=$(mktemp -d -t mem-eval-XXXXXX)
  export TEMP_DIR
}

cleanup_temp() {
  if [ -n "${TEMP_DIR:-}" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
  fi
}

# ── Assert Helpers (for eval runner) ──────────────────────────────────────

ASSERT_PASSED=0
ASSERT_FAILED=0

assert_contains() {
  local haystack="$1" needle="$2" label="${3:-}"
  if echo "$haystack" | grep -qF "$needle"; then
    ASSERT_PASSED=$((ASSERT_PASSED + 1))
  else
    ASSERT_FAILED=$((ASSERT_FAILED + 1))
    echo "  FAIL: expected '$label$needle' in output" >&2
    return 1
  fi
}

assert_not_contains() {
  local haystack="$1" needle="$2" label="${3:-}"
  if echo "$haystack" | grep -qF "$needle"; then
    ASSERT_FAILED=$((ASSERT_FAILED + 1))
    echo "  FAIL: found unexpected '$label$needle' in output" >&2
    return 1
  else
    ASSERT_PASSED=$((ASSERT_PASSED + 1))
  fi
}

assert_exit_code() {
  local actual="$1" expected="${2:-0}" label="${3:-}"
  if [ "$actual" -eq "$expected" ]; then
    ASSERT_PASSED=$((ASSERT_PASSED + 1))
  else
    ASSERT_FAILED=$((ASSERT_FAILED + 1))
    echo "  FAIL: expected exit code $expected, got $actual $label" >&2
    return 1
  fi
}

assert_file_exists() {
  local path="$1" label="${2:-}"
  if [ -f "$path" ]; then
    ASSERT_PASSED=$((ASSERT_PASSED + 1))
  else
    ASSERT_FAILED=$((ASSERT_FAILED + 1))
    echo "  FAIL: expected file not found: $path $label" >&2
    return 1
  fi
}

reset_asserts() {
  ASSERT_PASSED=0
  ASSERT_FAILED=0
}

print_assert_summary() {
  local total=$((ASSERT_PASSED + ASSERT_FAILED))
  if [ "$ASSERT_FAILED" -eq 0 ]; then
    echo "  PASSED: $ASSERT_PASSED/$total assertions"
  else
    echo "  FAILED: $ASSERT_FAILED/$total assertions ($ASSERT_PASSED passed)"
  fi
}
