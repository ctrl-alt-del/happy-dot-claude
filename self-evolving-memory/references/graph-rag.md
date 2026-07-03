# GraphRAG Integration

## Overview

GraphRAG (Microsoft) enhances retrieval by combining graph traversal with
text summaries. The self-evolving memory applies this concept to knowledge
entries: each entry is a node, typed relationships are edges, and connected
entry clusters form communities with auto-generated summaries.

## Graph Structure

`memory/graph.json`:

```json
{
  "version": "1.0.0",
  "nodes": [
    {
      "id": "mem-001",
      "title": "Never call validateToken() with null",
      "type": "gotcha",
      "confidence": 1.0,
      "tags": ["api", "auth", "security"],
      "community": 3,
      "pinned": true
    }
  ],
  "edges": [
    {
      "source": "mem-001",
      "target": "mem-012",
      "relation": "causes"
    }
  ],
  "communities": {
    "3": "Authentication and session management patterns"
  }
}
```

## Community Detection

Communities are detected using the Louvain algorithm on the unweighted,
undirected graph of entry relationships.

### Algorithm

1. Treat all edges as undirected for community detection (ignore edge direction).
2. Run Louvain modularity optimization.
3. Each node is assigned a community ID.
4. Communities with fewer than 3 nodes are dissolved (nodes become unassigned).
5. Unassigned nodes are assigned to `community: null`.

### Community Summary Generation

After community detection, each community gets an LLM-generated summary
(cached, regenerated when community membership changes):

```
You are summarizing a cluster of related knowledge from a software project.
Below are entries that form a knowledge community. Write a one-paragraph
summary of this community: what topic area it covers, the key risks,
established patterns, and important decisions. Keep it under 150 words.

Community entries:
[all entries in the community, with their full body text]
```

Summary is stored in `graph.json` under `communities.<id>`.

## Retrieval Modes

### Mode 1: Topic query (`--topic`)

```bash
scripts/memory-query.sh --topic auth
```

Algorithm:
1. Find entries with matching tags (exact or substring).
2. Identify the community/communities of matching entries.
3. Return:
   - Directly matching entries (up to 5).
   - Community summaries for communities containing matches.
   - Depth-1 related entries (entries directly connected to matches by edges).

Example output:

```
=== Matching entries ===

mem-001 [gotcha] ⚡ Never call validateToken() with null
  Confidence: 1.0  |  Accessed: 23 times  |  Last: 2 days ago

mem-012 [pattern] Use AuthGuard wrapper for all protected routes
  Confidence: 0.85  |  Accessed: 12 times  |  Last: 5 days ago

=== Community: Authentication and session management patterns ===

This community covers authentication implementation patterns including
token validation, session lifecycle management, and route protection.
Key risks: null token validation (mem-001) causes middleware crashes,
improper session expiry (mem-045) can lock out users. Established
patterns: AuthGuard wrapper (mem-012) standardizes route protection,
connection pooling (mem-003) prevents DB connection exhaustion...

=== Related entries ===

mem-045 [gotcha] Session cookie expiration must be set server-side
  Relation: relates_to (via mem-001)

mem-003 [decision] Use connection pooling for all database access
  Relation: depends_on (via mem-012)
```

### Mode 2: Free-text search (`--search`)

```bash
scripts/memory-query.sh --search "auth token null pointer"
```

Algorithm:
1. Compute text similarity between search terms and entry titles + bodies.
2. Return top 3 entries ranked by similarity.
3. Additionally return community context for the top result.

### Mode 3: Graph traversal (`--traverse`)

```bash
scripts/memory-query.sh --traverse mem-001 --depth 2
```

Algorithm:
1. Start at entry `mem-001`.
2. BFS traversal up to specified depth.
3. Return all visited entries in traversal order with edge types.

Useful for: exploring "what else should I know about this topic?"

## Neighborhood-Aware Retrieval

When an agent queries a topic, the retrieved context includes not just the
matched entry but its neighborhood. This enables "connecting the dots":

- If the agent asks about "auth" and gets mem-001, it also gets mem-012
  (related pattern), mem-045 (related gotcha), and the community summary.
- The agent can then proactively warn: "Before implementing auth, note that
  mem-001 (null token crash) is related to mem-045 (session expiry). Both
  should be addressed together."

## Graph Regeneration

`memory-update.sh` regenerates `memory/graph.json` from MEMORY.md + `meta.json`:

1. Parse all entries from MEMORY.md.
2. Build node list from entry metadata.
3. Build edge list from `related` fields in entry frontmatter.
4. Run community detection.
5. If community membership changed, regenerate community summaries.
6. Write updated `graph.json`.

This means the graph is always derivable from MEMORY.md — the graph is a
cache, not a separate source of truth.

## Performance Characteristics

| Operation | Complexity | Typical size |
|---|---|---|
| Node lookup | O(1) | ~100-500 nodes |
| Edge traversal | O(d) where d = degree | ~2-10 edges per node |
| Community detection | O(n log n) | ~100-500 nodes |
| Community summary generation | 1 LLM call per changed community | ~3-8 communities |
| Text similarity search | O(n) brute force | OK for <1000 entries |
| Graph regeneration | O(n + e) | ~100-500 nodes |

For projects with >1000 entries, text similarity switches to embedding-based
search with a local vector index (future optimization).
