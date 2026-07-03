# Collectors

Collectors are lightweight observation extractors that run at specific triggers.
They operate in tiers for performance: Tier 0 (deterministic filter, <50ms),
Tier 1 (light LLM triage, ~3s async), Tier 2 (full evolution, scheduled).

## Session Collector

**Trigger**: End of an agent conversation session.

### Tier 0 — Signal detection

Check the session transcript for signals:
- Did the agent report an error or failure?
- Did the agent explicitly call `@learn` or `@remember`?
- Did the agent discover something non-obvious (regex: "interesting", "surprising", "turns out", "discovered", "undocumented")?
- Was a bug root cause identified and fixed?

If none of these, skip. No observation written.

### Tier 1 — Light extraction

If Tier 0 flags the session, send a light prompt:

```
The following is a transcript of an AI agent session. Extract up to 3
raw observations — things learned, mistakes made, patterns discovered,
or surprising behaviors. Each observation should be one sentence.

Focus on durable, reusable knowledge — not session-specific details.

Transcript:
[transcript, truncated to last 5000 tokens]
```

Output format:
```json
[
  {"observation": "Calling init() twice in test setup causes state corruption in the SQLite driver.", "tags": ["testing", "database"]},
  {"observation": "The rate limiter uses a sliding window, not fixed window as the docs say.", "tags": ["api", "docs"]}
]
```

### PII scrub

Before writing to `memory/raw/`, apply PII redaction patterns (see `pii-protection.md`).

Write to `memory/raw/YYYY-MM-DD.json` (append if file exists).

## Git Collector

**Trigger**: Post-commit hook.

### Tier 0 — Signal detection

Check the commit message for regex matches:
- `revert` — code was rolled back, likely a mistake was made
- `fix` or `hotfix` — a bug was discovered and corrected
- `rollback` — deployment or data migration was reversed
- `TODO|FIXME|HACK` — technical debt acknowledged

Also check git diff stats:
- Files with >50% lines changed — significant refactor
- Configuration files changed (`.env`, `.config`, `*.yaml`, `*.json` in config dirs)

If none of these, skip.

### Tier 1 — Light extraction

For revert/fix/hotfix commits, send:

```
The following git commit message and diff describe a fix. Extract up to
2 raw observations about what went wrong and what the fix was. Focus on
patterns that might recur.

Commit: [message]
Files changed: [file list]

Diff:
[diff, truncated to 3000 tokens]
```

Output format:
```json
[
  {"observation": "The user cache TTL was too low (5s) causing cache stampede under load.", "tags": ["performance", "caching"]}
]
```

### PII scrub

Redact author emails from commit metadata before writing to `raw/`.

## Error Collector

**Trigger**: Build failure or test failure.

### Tier 0 — Signal detection

Check failure output:
- Is this a new failure (not seen before)? Compare error signature to recent failures.
- Is this a flaky test? Check if same test failed on retry.
- Is the error actionable? Skip "out of disk" or "network timeout" errors (infra, not code).

### Tier 1 — Light extraction

If Tier 0 flags a new, actionable error:

```
The following is a build/test failure. Extract the root cause, the
immediate trigger, and a prevention rule (what to do differently).
All as one raw observation.

Failure:
[error output, truncated to 3000 tokens]
```

Output format:
```json
[
  {"observation": "Test 'testPaymentFlow' fails when billing service returns 503. Root cause: no retry logic. Prevention: add exponential backoff retry to BillingClient.", "tags": ["testing", "api", "resilience"]}
]
```

### PII scrub

Redact file paths containing usernames (e.g., `/home/alice/project/` → `[PATH]/project/`).
Redact secrets or tokens that may appear in environment variable dumps in error output.

## Smart Collector Selection

When called via `memory-collect.sh`, the collector selects which sources to check
based on context:

| Context (passed via `--context`) | Active collectors |
|---|---|
| `coding` | Git + Error |
| `debugging` | Error + Session |
| `architecture` | Session |
| `ops` | None |
| `all` | All three |

If no context flag, defaults to `all`.

## Raw Observation Storage

All observations are written to `memory/raw/YYYY-MM-DD.json` in append mode:

```json
{
  "collected_at": "2026-07-03T14:25:30Z",
  "collector": "session",
  "source": "session-2026-07-03-abc123",
  "context": "debugging",
  "observations": [
    {
      "text": "Calling init() twice in test setup causes state corruption.",
      "tags": ["testing", "database"],
      "confidence": 0.5
    }
  ]
}
```

Files older than 30 days are cleaned up by `memory-evolve.sh` (distilled → `.done`,
unused → deleted).

## gitignore

`memory-init.sh` adds `memory/raw/` to `.gitignore` to prevent unreviewed
observations from being committed. The `.backup/` directory is also added.
