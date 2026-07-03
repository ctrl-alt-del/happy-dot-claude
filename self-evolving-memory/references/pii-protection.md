# PII Protection

## Design principle

Memory entries contain project knowledge, not personal data. All raw
observations are scrubbed before storage. Entries promoted to confirmed
must pass a PII review gate.

## Scrub Patterns

Applied by collectors at Tier 1, before writing to `memory/raw/`.

| Pattern | Regex | Replacement |
|---|---|---|
| Email addresses | `[\w.+-]+@[\w-]+\.[\w.-]+` | `[EMAIL]` |
| IPv4 addresses | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` | `[IP]` |
| API keys (common prefixes) | `(sk\|pk\|api\|token\|key\|secret)[-_]\w{20,}` | `[SECRET]` |
| AWS access keys | `AKIA[0-9A-Z]{16}` | `[SECRET]` |
| GitHub tokens | `ghp_[0-9a-zA-Z]{36}` | `[SECRET]` |
| JWT tokens | `eyJ[-\w]+\.[-\w]+\.[-\w]+` | `[TOKEN]` |
| Phone numbers | `\+?\d[\d\s()-]{7,}\d` | `[PHONE]` |
| Paths with usernames | `/home/\w+/` | `[PATH]/` |
| `/Users/\w+/` | `[PATH]/` | |

## Redaction Markers

Redacted values use typed placeholders. This enables:
- **Auditability**: The reader knows what type of data was removed.
- **Reversibility**: `memory-unredact.sh` can expand markers if a local
  secrets file is available (for debugging only).
- **Statistical tracking**: "3 [EMAIL] instances removed" in evolution logs.

## Review Gate

When distilling raw observations to candidate entries (Phase 1 of evolution):

1. Before sending to LLM, re-run PII scrub on raw observations.
2. After LLM produces candidate entries, scan entries for residual PII.
3. If PII detected in any candidate entry:
   - Reject that entry.
   - Log: "Entry mem-XXX rejected: contains [EMAIL]."
   - Keep original observation in `raw/` for manual review.
4. Candidate entries that pass the review are appended to MEMORY.md.

## gitignore

`memory-init.sh` automatically appends to `.gitignore`:

```
# Self-evolving memory — raw observations may contain residual PII
memory/raw/
memory/.backup/
```

MEMORY.md and `memory/meta.json` + `memory/graph.json` are COMMITTED. These
contain only reviewed, PII-free knowledge entries.

## Local Secrets File (for debugging)

`memory-unredact.sh` reads from a local-only file (never committed):

```
<project>/.memory-secrets.local
```

Format (gitignored):
```
[EMAIL] user@example.com
[IP] 192.168.1.100
```

This file is strictly optional. Without it, `memory-unredact.sh` outputs
a warning. With it, placeholders in a specific entry can be expanded for
debugging:

```bash
scripts/memory-unredact.sh mem-001
# Expands [EMAIL] → user@example.com using .memory-secrets.local
```

## Privacy Audit

`memory-status.sh` includes a privacy section:

```
PII scan:
  memory/raw/2026-07-03.json: 3 [EMAIL], 1 [IP]  (scrubbed)
  memory/raw/2026-07-02.json: clean
  MEMORY.md: clean (N reviewed entries)
```
