# Memory Entry Format

## YAML frontmatter specification

Each entry in MEMORY.md may carry an optional YAML frontmatter block enclosed by
`---` delimiters. Entries without frontmatter are treated as confirmed/permanent
with all metadata set to defaults.

### Fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `id` | string | auto | `mem-XXX` | Unique entry identifier, auto-assigned |
| `type` | enum | yes | `fact` | `gotcha`, `pattern`, `decision`, `fact` |
| `confidence` | float | yes | `0.5` | 0.0–1.0. 1.0 = human-verified |
| `created` | ISO 8601 | yes | now | Creation timestamp |
| `last_accessed` | ISO 8601 | auto | now | Updated on every retrieval |
| `access_count` | integer | auto | `0` | Incremented on every retrieval |
| `tags` | string[] | recommended | `[]` | Topic tags for search and community detection |
| `source` | string | recommended | `""` | Where this came from: session ID, commit SHA, etc. |
| `related` | string[] | optional | `[]` | IDs of related entries (mutual edges) |
| `superseded_by` | string or null | optional | `null` | ID of entry that replaces this one |
| `deprecated` | boolean | auto | `false` | Set by forget phase |
| `pinned` | boolean | optional | `false` | If true, never deprecated by forget phase |
| `recurrence_count` | integer | auto | `1` | How many observations led to this entry |

### Type semantics

| Type | Meaning | Typical source |
|---|---|---|
| `gotcha` | Something to avoid. A trap, footgun, or surprising behavior. Prefixed `⚡` if production-breaking. | Error collector, revert patterns |
| `pattern` | A reusable approach or convention that worked. | Session collector, code analysis |
| `decision` | An architecture or design decision with rationale. Equivalent to a lightweight ADR. | Architecture discussions, session collector |
| `fact` | An unqualified piece of knowledge: ownership, dependency, constraint. | Code analysis, session collector |

### Entry lifecycle

```
raw observation  →  candidate entry  →  confirmed entry  →  deprecated
(confidence: 0)     (confidence: ~0.5)   (confidence: 0.8+)   (deprecated: true)
                                                        OR
                                                   pinned (never deprecated)
```

### Example entries

#### Gotcha (production-breaking)

```markdown
---
id: mem-001
type: gotcha
confidence: 1.0
tags: [api, auth, security]
source: "session-2026-07-03-fix-auth-null"
recurrence_count: 4
related: [mem-012, mem-045]
---

## ⚡ Never call `validateToken()` with a null argument

- **What**: `validateToken(null)` throws an unhandled NullPointerException that crashes the auth middleware
- **Where**: `src/auth/token.ts:42`
- **Why**: The function assumes non-null input. Callers in `middleware/auth.ts:87` pass user input directly.
- **How to avoid**: Always wrap in `if (token != null)` or use `Optional<Token>`. The helper `safeValidate()` in `src/auth/helpers.ts` already does this.
- **Who to ask**: Auth team (@auth-owners)
```

#### Pattern

```markdown
---
id: mem-002
type: pattern
confidence: 0.85
tags: [testing, api, e2e]
source: "session-2026-07-01-api-tests"
recurrence_count: 3
related: [mem-008]
---

## Use test fixtures from `test/fixtures/` instead of inline test data

Pattern observed across 12 test files. Inline test data causes duplication when
API schemas change. The `test/fixtures/` directory provides factory functions
that generate valid payloads with optional overrides.
```

#### Decision

```markdown
---
id: mem-003
type: decision
confidence: 1.0
tags: [architecture, database]
source: "session-2026-06-28-arch-review"
related: [mem-010, mem-011]
---

## ADR: Use connection pooling for all database access

**Decision**: All services must use the shared connection pool via `db.getPool()`
instead of creating individual connections.

**Rationale**: Individual connections exhausted the database's connection limit
during load testing (max 100 connections, spike to 200+ with per-request connections).

**Alternatives considered**: Per-service pools (rejected: still too many connections),
single shared pool (chosen: bounded at 20, queues excess).

**Consequences**: All new services must import `src/db/pool.ts`. Legacy services in
`src/legacy/` are exempt until migration (tracked in mem-010).
```

#### Fact

```markdown
---
id: mem-004
type: fact
confidence: 0.9
tags: [ownership, docs]
source: "codebase-analysis-2026-06-15"
---

## Code ownership: `src/payments/`

- Primary owner: billing-team
- Secondary: platform-team (for webhook handling only)
- Last major refactor: 2026-03 (migration from Stripe v1 to v2)
- Related decisions: mem-007, mem-012
```

### Frontmatter parsing rules

1. Frontmatter is only parsed if the entry starts with `---` on its own line.
2. Frontmatter ends at the next `---` on its own line.
3. Entries are separated by blank lines OR by a new `---` frontmatter block.
4. Entries without `id` get one auto-assigned on `memory-update.sh`.
5. `access_count`, `last_accessed`, `deprecated` are managed by scripts, not
   edited by hand. Hand-edited values are overwritten on update.
6. The first H1 or H2 heading in the body is used as the entry title in listings.
