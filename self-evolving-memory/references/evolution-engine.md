# Evolution Engine

The evolution engine runs in five sequential phases. It is triggered by
`memory-evolve.sh` and processes queued observations into durable memory entries.

## Phase 1: Distill

**Input**: Queued raw observations in `memory/raw/YYYY-MM-DD.json`
**Output**: Candidate entries appended to MEMORY.md with `confidence: 0.5`

### Algorithm

1. Load all unprocessed `.json` files from `memory/raw/`.
2. Group observations by source type (session, git, error).
3. For each group, batch observations into chunks of 10.
4. For each chunk, send to LLM with prompt:

```
You are distilling observations from a software project into reusable knowledge entries.

Below are N observations collected from sessions, git history, and error logs.
Each observation is a short description of something that happened.

Extract distinct, reusable knowledge items. For each item, produce:
- type: gotcha | pattern | decision | fact
- title: concise one-line summary
- body: explanation with concrete details (file paths, function names, versions)
- tags: 1-3 relevant topic tags
- confidence: 0.5 (initial estimate)

Skip trivial or duplicate observations. If multiple observations describe the
same thing, merge them into one entry.

Observations:
[observations block]
```

5. For each extracted entry, check MEMORY.md for similar existing entries
   (tag overlap > 0.5 AND title similarity). If found, skip (consolidate phase
   handles merging).
6. Append new non-duplicate entries to MEMORY.md with `recurrence_count = N`
   (number of observations that contributed).
7. Mark processed `.json` files as distilled (rename to `YYYY-MM-DD.done`).

### Recurrence threshold

Observations are only distilled if they appear at least N times (default: N=2).
Single-occurrence observations remain in `raw/` for 30 days, then expire.

The recurrence check uses normalized text similarity:
```
sim(obs_a, obs_b) > 0.8 → same observation
```

## Phase 2: Consolidate

**Input**: All confirmed and candidate entries in MEMORY.md
**Output**: Merged entries, fewer total entries, higher average confidence

### Algorithm

1. Load all entries from MEMORY.md + `memory/meta.json`.
2. Exclude deprecated entries.
3. For each pair of entries with the same `type`:

   a. Compute tag overlap (Jaccard similarity of tag sets).
   b. If Jaccard < 0.6, skip (not similar enough).
   c. Compute body similarity (text overlap or LLM judgment).
   d. If similarity > threshold, add to merge candidates.

4. For each merge candidate group, send to LLM:

```
Merge these related knowledge entries into a single, stronger entry.
Preserve all non-redundant information. Combine tags. Set confidence
to max(confidences). Note the source entries.

Original entries:
[entries block]
```

5. Write merged entry. Set `superseded_by` on originals. Keep originals
   with `deprecated: true` for audit trail.
6. Update `memory/graph.json` — merged edges point to new entry.

### Merge guard

Never merge entries with `pinned: true` unless explicitly requested.
Never merge entries of different `type` values.

## Phase 3: Connect

**Input**: New and recently modified entries in MEMORY.md
**Output**: Updated `memory/graph.json` with typed relationships

### Algorithm

1. For each new or modified entry since last connect run:
2. Find candidate related entries (tag overlap > 0, excluding self).
3. For each pair (new_entry, candidate), ask LLM:

```
How are these two knowledge entries related?
Options: causes, prevents, supersedes, relates_to, depends_on, none.

Entry A:
[entry A]
Entry B:
[entry B]
```

4. If not "none", add bidirectional edge. The inverse is:
   - `causes` ↔ `caused_by`
   - `prevents` ↔ `prevented_by`
   - `supersedes` ↔ `superseded_by`
   - `relates_to` ↔ `relates_to` (symmetric)
   - `depends_on` ↔ `required_by`

5. Update `memory/graph.json` with new edges.
6. Run Louvain community detection to update community assignments.
7. For communities that changed, regenerate community summary:

```
You are summarizing a cluster of related knowledge from a software project.
Below are entries that form a knowledge community. Write a one-paragraph
summary of this community: what topic area it covers, the key risks,
established patterns, and important decisions.

Community entries:
[community entries]
```

### Edge persistence

Edges are stored in `memory/graph.json`:
```json
{
  "nodes": [{"id": "mem-001", "community": 3}, ...],
  "edges": [{"source": "mem-001", "target": "mem-002", "relation": "causes"}, ...],
  "communities": {"3": "Authentication and session management patterns"}
}
```

## Phase 4: Forget

**Input**: All entries in `memory/meta.json`
**Output**: Flagged entries, auto-deprecated entries (post review window)

### Decay function

```
score = confidence * access_count / (days_since_last_access + 1)
```

Where:
- `confidence`: 0.0–1.0
- `access_count`: total times entry was retrieved
- `days_since_last_access`: days since `last_accessed`

### Thresholds

| Score | Action |
|---|---|
| ≥ 0.5 | Keep, no action |
| 0.2 ≤ score < 0.5 | Flag for review (appears in `memory-status.sh` and dashboard review queue) |
| < 0.2 for ≥ 7 days | Auto-deprecate → `deprecated: true` |

### Exemptions

- `pinned: true` entries are never deprecated.
- Entries created within the last 7 days are never deprecated.
- Entries with `⚡` marker (production-breaking) require manual confirmation to deprecate.

### Deprecation

A deprecated entry remains in MEMORY.md and is still queryable. It is marked
`deprecated: true` and appears dimmed in the dashboard. Deprecated entries are
skipped by the Connect phase and excluded from default query results (override
with `--include-deprecated`).

Permanent deletion requires `memory-purge.sh <id>`, which writes a tombstone
to `memory/.backup/tombstones.json`.

## Phase 5: Promote

**Input**: Entries with access_count > threshold or manual promotion
**Output**: Increased confidence, "reviewed" flag

### Automatic promotion triggers

| Condition | Action |
|---|---|
| Entry accessed ≥ 10 times | Confidence → max(current + 0.1, 0.8) |
| Entry accessed ≥ 50 times | Confidence → 1.0, auto-mark reviewed |

### Manual promotion

```bash
scripts/memory-promote.sh <id>
```
Sets `confidence: 1.0`, marks as reviewed. Irreversible (but can be demoted).

### Anti-recency bias protection

A highly useful but niche entry (e.g., "How to rotate the encryption key" — accessed
once every 90 days but critical) would get a low score under naive decay. To protect
this, pinned entries are exempt AND the decay formula uses `days_since_last_access + 1`
(not a harsher exponential), giving niche entries a long grace period.
