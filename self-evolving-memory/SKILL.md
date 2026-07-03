---
name: self-evolving-memory
version: "1.0.0"
description: >
  Creates, manages, and evolves a self-improving project memory that auto-distills
  knowledge from agent sessions, git history, and error logs into a durable
  knowledge base with GraphRAG-style entity relationships and community detection.
  The memory consolidates similar entries, forgets stale/unused items, and
  "connects the dots" across domains. Use this whenever the user wants to set up
  an evolving project memory, onboard a project into the memory system, evolve or
  consolidate existing MEMORY.md, query the memory graph, visualize the knowledge
  graph, migrate between memory schema versions, or integrate memory into other
  skills. Trigger especially when the user mentions: self-evolving memory,
  knowledge base, MEMORY.md evolution, graph memory, learning from mistakes,
  auto-distill, knowledge consolidation, memory forget/decay, connecting the dots,
  knowledge graph visualization, or memory retention policies. Also trigger when
  the user wants to run any memory-* script or mentions the memory dashboard.
---

# Self-Evolving Memory

A self-improving, graph-backed project memory that evolves through observation,
distillation, consolidation, and controlled forgetting.

## Quick start

```bash
# Onboard a project (fresh or with existing MEMORY.md)
./scripts/memory-init.sh

# Run nightly evolution cycle (distill → consolidate → connect → forget)
./scripts/memory-evolve.sh

# Query the memory for a topic
./scripts/memory-query.sh --topic auth

# Open the dashboard
./scripts/memory-graph.sh
```

## Workflow

### Phase 1: Initialize memory

Run `scripts/memory-init.sh`. This handles three scenarios:

1. **Fresh project** — scaffolds MEMORY.md + `memory/` from templates.
2. **Existing MEMORY.md with plain entries** — parses entries, assigns IDs, enriches
   with default metadata, creates `memory/`, infers graph from tags.
3. **Existing `memory/` directory** — validates, reports version, offers migration
   if schema is outdated.

See `references/migration.md` for migration chain details.

### Phase 2: Collect observations

Collectors run automatically via Git hooks and session end triggers:

| Collector | Trigger | Extracts |
|---|---|---|
| Session | Post agent-conversation | What was asked, worked, broke, learned |
| Git | On commit matching `revert\|fix\|hotfix\|rollback` | Revert patterns, bug-fix patterns, architecture shifts |
| Error | On build/test failure | Root cause, resolution, prevention rule |

Tiered performance model:
- **Tier 0** (<50ms, non-blocking): Deterministic regex filter. Skip if no signal.
- **Tier 1** (~3s, async): Light LLM triage on flagged events. Extracts raw observations.
- **Tier 2** (~20s, scheduled): Full evolution cycle. Runs nightly or via manual `--evolve`.

See `references/collectors.md` for collector specifications.

### Phase 3: Evolve the memory

Run `scripts/memory-evolve.sh` (nightly cron or manual).

Evolution phases run in order:

1. **Distill** — LLM extracts atomic knowledge items from queued `raw/` observations
   into candidate entries.
2. **Consolidate** — Finds similar entries via tag-overlap pre-filter, merges into
   stronger entries.
3. **Connect** — Builds typed relationships between entries: `causes`, `prevents`,
   `supersedes`, `relates_to`, `depends_on`.
4. **Forget** — Applies decay function. Entries below threshold are flagged for review.
   After review window (default: 7 days), auto-deprecated unless pinned.
5. **Promote** — High-confidence, frequently-used entries are promoted to confirmed.

See `references/evolution-engine.md` for algorithms and decay formulas.

### Phase 4: Retrieve and use memory

Three retrieval modes available via `scripts/memory-query.sh`:

| Mode | Trigger | Method |
|---|---|---|
| Pre-task load | `--topic <tag>` | Tag search → graph traversal → entry + community summary |
| Mid-task lookup | `--search <terms>` | Keyword/embedding match → top 3 entries |
| Post-task write | Write to MEMORY.md → `scripts/memory-update.sh` | Regenerates meta.json + graph.json |

See `references/graph-rag.md` for GraphRAG traversal and community detection details.

### Phase 5: Review and manage

Human-in-the-loop tools:

| Command | Effect |
|---|---|
| `scripts/memory-status.sh` | Health report: counts, staleness, pending reviews |
| `scripts/memory-pin.sh <id>` | Pin entry — never forgets |
| `scripts/memory-purge.sh <id>` | Force-delete with tombstone record |
| `scripts/memory-promote.sh <id>` | Confidence → 1.0, mark reviewed |
| `scripts/memory-demote.sh <id>` | Flag for review, drop confidence |

### Phase 6: Visualize

Run `scripts/memory-graph.sh` to regenerate `memory/graph.json` and open the
view-only dashboard (`assets/memory-dashboard.html`). The dashboard shows:

- Force-directed graph (nodes = entries, edges = typed relationships)
- Entry inspector with full content and metadata
- Evolution log with before/after diffs
- Health panel with staleness distribution
- Review queue for entries needing human attention

### Phase 7: Migrate

When the `memory/` schema version is outdated:

```bash
scripts/memory-migrate.sh [--dry-run]
```

- Validates current data (schema check, referential integrity)
- Creates backup in `memory/.backup/<timestamp>-<old-version>/`
- Applies migration chain (v1→v2→v3, no direct jumps)
- Validates migrated data
- Atomic rename: temp → real files
- Reports: "Preserved X entries, enhanced Y with default metadata"

See `references/migration.md` for version history and changelog.

### Phase 8: Integrate with skills

To teach an existing skill to use memory, add to its SKILL.md:

```markdown
## Memory integration
- Before starting, if `memory/meta.json` exists, run `memory-query.sh --topic <tag>`.
- After completing, promote durable learnings to MEMORY.md.
```

See `references/skill-integration.md` for per-skill integration guides.

## Memory entry format

Entries in MEMORY.md use optional YAML frontmatter. Plain entries without
frontmatter are treated as permanent/confirmed with default metadata.

See `references/entry-format.md` for the full specification.

## PII protection

All collectors scrub PII before writing to `raw/`. Patterns redacted: emails,
IPs, API keys/tokens, phone numbers, file paths with usernames. Raw observations
(`memory/raw/`) are gitignored. Entries promoted from raw must pass a PII check.

See `references/pii-protection.md` for scrub patterns and review gates.

## Files at a glance

| Path | Purpose |
|---|---|
| `references/entry-format.md` | MEMORY.md entry specification with frontmatter fields |
| `references/evolution-engine.md` | Distill, consolidate, connect, forget algorithms |
| `references/collectors.md` | Session, Git, Error collector specifications |
| `references/migration.md` | Schema version history, migration chains, rollback |
| `references/skill-integration.md` | How to wire memory into other skills |
| `references/pii-protection.md` | Scrub patterns, redaction, review gates |
| `references/graph-rag.md` | GraphRAG traversal, community detection, query modes |
| `scripts/memory-init.sh` | Onboard project (fresh or plain MEMORY.md) |
| `scripts/memory-migrate.sh` | Upgrade `memory/` schema version |
| `scripts/memory-evolve.sh` | Full evolution cycle |
| `scripts/memory-status.sh` | Health report |
| `scripts/memory-query.sh` | Retrieve entries for agents |
| `scripts/memory-update.sh` | Regenerate meta.json + graph.json |
| `scripts/memory-graph.sh` | Regenerate graph + open dashboard |
| `scripts/memory-collect.sh` | Run context-appropriate collector |
| `scripts/memory-pin.sh` | Pin entry |
| `scripts/memory-purge.sh` | Force-delete entry |
| `scripts/memory-promote.sh` | Confidence → 1.0 |
| `scripts/memory-demote.sh` | Flag for review |
| `scripts/memory-unredact.sh` | Expand PII placeholders |
| `assets/memory-dashboard.html` | View-only visualization dashboard |
| `evals/evals.json` | Evaluation definitions |
