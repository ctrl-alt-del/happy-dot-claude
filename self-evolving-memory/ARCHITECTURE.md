# Architecture — Self-Evolving Memory

## Storage Layout

```
<project>/
├── MEMORY.md                          # Enhanced with optional YAML frontmatter per entry
├── memory/
│   ├── meta.json                      # Per-entry metadata + global config
│   │   └── schema version: "1.0.0"
│   ├── graph.json                     # Nodes + typed edges, regenerable
│   └── raw/                           # Gitignored. Queued observations pre-distillation.
│       └── YYYY-MM-DD.json
│   └── .backup/
│       ├── manifest.json              # Snapshot index
│       ├── latest -> <snapshot-dir>/  # Symlink to most recent snapshot
│       └── YYYY-MM-DDTHHMMSSZ--vX.Y.Z--<sha256:8>/
│           ├── meta.json
│           ├── graph.json
│           ├── raw/
│           └── MANIFEST.sha256
```

## Entry Model

Each entry in MEMORY.md carries optional YAML frontmatter:

```yaml
---
id: mem-001
type: gotcha | pattern | decision | fact
confidence: 0.85
created: "2026-07-03T14:25:30Z"
last_accessed: "2026-07-03T14:25:30Z"
access_count: 12
tags: [api, security]
source: "session-2026-07-03-abc123"
related: [mem-042, mem-107]
superseded_by: null
deprecated: false
pinned: false
recurrence_count: 3
---
Content in markdown...
```

Plain entries (no frontmatter) treated as permanent/confirmed with defaults.

## Collectors — Tiered Triggering

| Tier | Operation | Trigger | Cost | Blocking |
|---|---|---|---|---|
| 0 | Deterministic filter | Every hook | <50ms | No |
| 1 | Light LLM triage | Tier 0 flagged | ~3s async | No |
| 2 | Full evolution | Nightly/manual | ~20s | No |

### Smart Selection

| Task type | Active collectors | Why |
|---|---|---|
| Writing code | Git + Error | Learning from code changes |
| Debugging | Error + Session | Root cause + resolution |
| Architecture | Session only | Design decisions |
| Routine ops | None | Nothing to capture |

## PII Protection Layers

| Layer | What |
|---|---|
| Collector scrub | Pattern redaction before writing to `raw/` |
| Redaction markers | Typed placeholders: `[EMAIL]`, `[IP]`, `[SECRET]`, `[PHONE]`, `[PATH]` |
| Gitignore | `memory/raw/` in `.gitignore` |
| Review gate | PII check on raw→candidate promotion |

## Evolution Engine

| Phase | Algorithm |
|---|---|
| Distill | Batch LLM prompt: "Extract distinct reusable knowledge items from N observations." |
| Consolidate | Tag-overlap pre-filter (Jaccard > 0.6) → LLM merge prompt → update edges |
| Connect | LLM pairwise comparison: "Choose relationship: causes, prevents, supersedes, relates_to, depends_on, none." |
| Forget | Decay: `score = confidence * access_count / (days_since_last_access + 1)` |
| Promote | Manual: sets confidence → 1.0, marks reviewed |

### Signal-to-Noise

Recurrence threshold: observation → candidate only after N occurrences (default: N=2).
Singles expire after 30 days in `raw/`.

## GraphRAG Integration

| Concept | Implementation |
|---|---|
| Entities | Memory entries (nodes with type, confidence, tags) |
| Relationships | Typed edges: causes, prevents, supersedes, relates_to, depends_on |
| Communities | Louvain community detection on graph.json |
| Community summaries | Nightly LLM-generated per-community paragraph |
| Traversal | `memory-query.sh` returns entry + community summary + depth-1 related |

## Retrieval Modes

| Mode | Method | Returns |
|---|---|---|
| Pre-task load | `--topic <tag>` | Entry + community summary + related |
| Mid-task lookup | `--search <terms>` | Top 3 matching entries |
| Post-task write | `memory-update.sh` | Regenerated meta.json + graph.json |

## Snapshots and Rollback

- **Auto-snapshot**: Before every `memory-evolve.sh` run.
- **Naming**: `YYYY-MM-DDTHHMMSSZ--vX.Y.Z--<sha256:8>/` — content-addressed.
- **Hash**: SHA-256 of canonical serialization (sorted JSON, excludes volatile fields).
- **Integrity**: `MANIFEST.sha256` per snapshot.
- **Rollback**: `memory-evolve.sh --rollback <hash>`.
- **Retention**: Last 7 snapshots + 1 per schema version.

## Migration

| Scenario | Script |
|---|---|
| Fresh project | `memory-init.sh` |
| Plain MEMORY.md | `memory-init.sh` (parse + enrich) |
| Old schema version | `memory-migrate.sh` (chain: v1→v2→v3) |

Safety: validate → backup → transform → validate → atomic rename.

## CLI Surface

| Script | Purpose |
|---|---|
| `memory-init.sh` | Onboard project |
| `memory-migrate.sh` | Schema upgrade |
| `memory-evolve.sh` | Evolution cycle |
| `memory-status.sh` | Health report |
| `memory-query.sh` | Retrieve entries |
| `memory-update.sh` | Regenerate derived files |
| `memory-graph.sh` | Open dashboard |
| `memory-collect.sh` | Run collector |
| `memory-pin.sh` | Pin entry |
| `memory-purge.sh` | Delete entry |
| `memory-promote.sh` | Confirm entry |
| `memory-demote.sh` | Flag entry |
| `memory-unredact.sh` | Expand PII placeholders |

## Daily Token Budget

| Operation | Tokens | When |
|---|---|---|
| Tier 1 triage (3-5 events) | ~3K | Async |
| Nightly distill (15 obs) | ~8K | Scheduled |
| Weekly consolidation | ~5K | Weekly |
| **Total** | **~16K/day** | Off critical path |
