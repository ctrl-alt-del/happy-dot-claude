---
name: agentic-knowledge-digest
description: >
  Fetches and summarizes research, tools, and news about AI knowledge systems
  and agentic knowledge: RAG, knowledge graphs (GraphRAG, Neo4j, Graphify,
  Graphitti), knowledge lifecycle management (LLM-wiki, LLM-wiki v2, Code Wiki,
  creation, curation, evolution, versioning, consolidation, decay, pruning),
  agent memory, embeddings/vectors, multi-agent architectures, reasoning, and
  context management. Produces an interactive HTML digest saved to
  ~/Desktop/agentic-knowledge-digest/. Use this whenever the user mentions AI
  knowledge, agentic knowledge, RAG, knowledge graphs, LLM-wiki, Code Wiki,
  GraphRAG, Graphify, Graphitti, Neo4j, agent memory, embeddings, vector DBs,
  multi-agent, tool use, reasoning, knowledge lifecycle, knowledge evolution,
  knowledge consolidation, knowledge management, or wants to catch up on the
  latest in how AI systems and agents acquire, store, retrieve, and use
  knowledge.
---

# Agentic Knowledge Digest

Produce a fact-only daily digest of AI knowledge and agentic knowledge research
as an interactive HTML page. The digest is saved to
`~/Desktop/agentic-knowledge-digest/YYYY-MM-DD.html`.

## Design principles

- **Facts only.** Never invent details. If source content is thin, write a
  shorter summary rather than padding it.
- **Interactive.** The HTML page provides search, keyword filtering, dark/light
  mode, keyboard navigation, and collapsible sections.
- **Traceable.** Every item links to its verified source. A Sources list at the
  bottom lists every origin.
- **Language-respecting.** Chinese content stays in Chinese. All titles are
  bilingual (English / Chinese) so both audiences can scan.
- **Capped and ranked.** Maximum 25 items total, prioritized by relevance to
  AI knowledge and agentic knowledge systems.

## Workflow

### Step 0 — Ask the user: rebuild or start fresh

Before doing anything else, **ask the user which mode they want**:

- **(A) Re-generate HTML from existing data** — re-apply the current template/design
  to digests that were already produced. No network fetch.
- **(B) Start fresh** — pull the latest from all sources, process it, and
  generate a new HTML digest.

First check whether prior data exists:

```bash
ls -1 ~/Desktop/agentic-knowledge-digest/*-processed.json ~/Desktop/agentic-knowledge-digest/*.html 2>/dev/null
```

- If **no** existing digests are found, skip the question and go straight to
  **fresh** (Step 1) — there is nothing to rebuild.
- If existing digests **are** found, ask the user to choose A or B before
  continuing. Default to whatever they request in their message (e.g. "regenerate
  my digests" → A; "give me the latest agentic knowledge news" → B).

**If the user chooses (A) Re-generate:**

Run the rebuilder, then open the result. This skips Steps 1–7 entirely.

```bash
python3 scripts/generate_html.py --rebuild-dir ~/Desktop/agentic-knowledge-digest
```

Then open the regenerated file(s)
(e.g. `open ~/Desktop/agentic-knowledge-digest/YYYY-MM-DD.html`) and you are
done — do **not** fetch or re-process.

**If the user chooses (B) Start fresh**, continue with Step 1 below.

The user may also specify a specific date to run against:

```bash
python3 scripts/fetch_digest.py --verify-links --save-raw --date 2026-07-01
```

When `--date` is given, the fetcher queries sources for that specific calendar
day (instead of today). When omitted, it defaults to today.

### Step 1 — Ensure dependencies and run the fetcher

Verify the required Python packages are installed:

```bash
python3 -c "import feedparser, requests; from bs4 import BeautifulSoup; print('deps OK')"
```

If this fails with `ModuleNotFoundError`, install them:

```bash
pip3 install -r scripts/requirements.txt
```

If `pip3` is not available, try `pip` instead. Then run the fetcher:

```bash
python3 scripts/fetch_digest.py --verify-links --save-raw
```

This produces `~/Desktop/agentic-knowledge-digest/YYYY-MM-DD-raw.json` and prints
the JSON to stdout. The JSON contains an `items` array with fields: `title`,
`url`, `source`, `date`, `language`, `section`, `raw_content`, `organization`,
`arxiv_id`, `link_verified`, `focus_match`, `priority_hint`.

- `focus_match` lists which focus topics the item matches
  (e.g. `["knowledge-graph", "knowledge-lifecycle"]`).
- `priority_hint` is a numeric score — higher = more relevant. Use it to
  rank items.
- `link_verified` is `true` if the URL responded to a HEAD request.
  Items with dead links are already removed by `--verify-links`.

If any source fails, the script logs a warning to stderr and continues.

### Step 2 — Process each item

For every item in the raw JSON, produce a processed item with these fields:

| Field | How to produce |
|-------|---------------|
| `title` | Original title from source |
| `title_zh` | **Chinese translation** of the title (for EN items) or original Chinese title (for ZH items). Every item gets a Chinese title. |
| `url` | Original URL |
| `source` | Original source name |
| `section` | Original section |
| `organization` | Assign or keep from fetcher |
| `language` | Original language |
| `arxiv_id` | From fetcher if present |
| `summary` | **1-2 sentence factual summary** in the item's language. Paraphrase, never copy-paste. If source is thin, write one sentence. Never add information not present. |
| `keywords` | Array of `{"text": "...", "domain": "..."}`. 3-5 keywords, each with a domain assignment. See keyword domains below. |
| `link_verified` | From fetcher |
| `is_highlight` | `true` if this item qualifies for the Highlights section (see criteria below) |

**Keyword domain assignment:** For each keyword, assign one of these domains:

| Domain | Applies to keywords about |
|--------|---------------------------|
| `rag-retrieval` | RAG, retrieval-augmented generation, dense/sparse/hybrid retrieval, reranking, information retrieval |
| `agent-memory` | Agent memory systems, episodic/working/long-term memory, context window management, MemGPT, Mem0, memory consolidation |
| `knowledge-graph` | GraphRAG, knowledge graphs, ontologies, Neo4j, Cypher, SPARQL, Graphify, Graphitti, property graphs, RDF, entity linking, graph databases, GNN for knowledge |
| `knowledge-lifecycle` | LLM-wiki (v1/v2), Code Wiki, knowledge lifecycle, creation, curation, validation, evolution, versioning, consolidation, decay, pruning, forgetting, staleness, conflict resolution |
| `agent-architecture` | Agent frameworks, multi-agent systems, tool use, function calling, orchestration, autonomous agents, agentic workflows, delegation |
| `embeddings-vectors` | Embedding models, vector databases, dense/sparse embeddings, semantic search, similarity search, text embeddings |
| `ai-knowledge` | Knowledge distillation, continual learning, fine-tuning, instruction tuning, preference optimization, training data curation |
| `cognition-reasoning` | Chain-of-thought, CoT, tree-of-thought, ToT, planning, reasoning, self-reflection, self-critique, deliberation, verification |
| `context-prompting` | Prompt engineering, in-context learning, few-shot, zero-shot, long context, prompt compression, prompt optimization |
| `evaluation-benchmark` | Benchmarks, evaluation, agent benchmarks, retrieval benchmarks, knowledge base evaluation |

Keywords match the item's language: English keywords for EN items, Chinese
keywords (e.g. `知识图谱`, `知识生命周期`) for ZH items.

### Step 3 — Rank, cap, and select

**Rank** all items by: `priority_hint` (descending) > recency > content depth.

**Cap** at 25 items total. Keep the highest-ranked 25.

**Highlights**: From the top 25, select up to 10 items that qualify as
exceptional significance (see criteria below). Set `is_highlight: true`.

**Section distribution** is fluid — some days research papers dominate,
other days tools and frameworks lead. Reflect real distribution, do not force
equal counts per section.

An item qualifies as a Highlight if it represents:

- New model or framework release with significant impact (major RAG system,
  novel agent architecture, breakthrough embedding model)
- Major open-source release (GraphRAG, knowledge graph tooling, agent framework)
- Significant milestone (widely adopted knowledge management system,
  record benchmark in retrieval or reasoning)
- Major research breakthrough (novel architecture, SOTA results on
  knowledge/agent benchmarks)
- Notable incident or controversy (data leak via RAG, agent safety incident,
  high-profile retraction)
- Major acquisition or funding in AI knowledge / agentic knowledge space

If nothing qualifies, omit Highlights entirely. Highlights items also appear
in their regular section (duplicated, not removed).

### Step 4 — Apply content filters

**Skip** items whose primary subject is:
- Cryptocurrency (Bitcoin, Ethereum, altcoins)
- Token speculation or DeFi
- NFTs or web3 fundraising
- General consumer tech (phone releases, laptop reviews, gaming)
- Enterprise SaaS that is unrelated to AI knowledge
- Non-AI hardware (CPUs, GPUs for gaming, monitors)

**Skip** items with no connection to AI knowledge or agentic knowledge:
- If the item does not mention any of the 10 focus topic areas, drop it.

**Keep**: All 10 focus topic areas (see Step 2 keyword domains). Items about
knowledge representation, retrieval, graphs, lifecycle, memory, embeddings,
agents, reasoning, prompting, and evaluation are in scope.

### Step 5 — Synthesize daily keywords

Look across all 25 selected items and synthesize **8-12 daily keywords** —
semantically meaningful themes that characterize the day's knowledge and
agentic research, not just frequency counts. Each daily keyword has the same
`{"text": "...", "domain": "..."}` structure as item keywords. Use a mix of
English and Chinese where appropriate.

### Step 6 — Group into sections

Organize items into sections in this order:

1. `highlights` — items with `is_highlight: true` (up to 10)
2. `research_papers` — arXiv & Research Papers
3. `tools_frameworks` — Tools, Frameworks & Open Source
4. `models_embeddings` — Models & Embeddings
5. `blogs_insights` — Blogs & Insights
6. `industry_applications` — Industry & Deployments

Skip any section with zero items.

### Step 7 — Write processed JSON and generate HTML

Write the processed data as JSON conforming to this schema:

```json
{
  "date": "2026-07-05",
  "stats": {
    "total_items": 25,
    "sources_count": 14,
    "links_verified_count": 25,
    "links_failed_count": 0,
    "section_counts": {
      "research_papers": 10, "tools_frameworks": 6,
      "models_embeddings": 4, "blogs_insights": 3, "industry_applications": 2
    }
  },
  "daily_keywords": [
    {"text": "GraphRAG", "domain": "knowledge-graph"},
    {"text": "knowledge-lifecycle", "domain": "knowledge-lifecycle"}
  ],
  "sections": [
    {
      "id": "highlights",
      "label": "Highlights",
      "items": [
        {
          "title": "Microsoft Releases GraphRAG 2.0",
          "title_zh": "微软发布 GraphRAG 2.0",
          "url": "https://www.microsoft.com/en-us/research/blog/graphrag-2/",
          "source": "Microsoft Research",
          "section": "tools_frameworks",
          "organization": "Microsoft",
          "language": "en",
          "arxiv_id": "",
          "summary": "Microsoft released GraphRAG 2.0 with improved community detection...",
          "keywords": [
            {"text": "GraphRAG", "domain": "knowledge-graph"},
            {"text": "community-detection", "domain": "knowledge-graph"}
          ],
          "link_verified": true,
          "is_highlight": true
        }
      ]
    },
    {
      "id": "research_papers",
      "label": "Research Papers",
      "items": [...]
    }
  ],
  "sources": [
    {"name": "arXiv", "url": "https://arxiv.org"},
    {"name": "Anthropic Research", "url": "https://www.anthropic.com/research"}
  ]
}
```

Save this as `~/Desktop/agentic-knowledge-digest/YYYY-MM-DD-processed.json`,
then run:

```bash
python3 scripts/generate_html.py ~/Desktop/agentic-knowledge-digest/YYYY-MM-DD-processed.json
```

This writes `~/Desktop/agentic-knowledge-digest/YYYY-MM-DD.html` (the filename
comes from the `date` field). The processed JSON is also embedded inside the
HTML, so the page can be re-styled later even if the JSON is gone. Open the
file in the user's default browser:

```bash
open ~/Desktop/agentic-knowledge-digest/YYYY-MM-DD.html
```

Display a brief stats summary in the conversation (total items, section
counts, top daily keywords) so the user gets a preview without opening
the file.

### Step 8 — HTML page features

The generated page provides:

- **Sticky header** with date, section quick-nav, search bar, dark/light toggle
- **Stats dashboard** with bar chart of items per section, item/source counts,
  link verification status
- **Daily keywords** as colored pills at the top
- **Collapsible sections** — click section header to expand/collapse, first
  section expanded by default
- **Item cards** with organization badge, bilingual title, colored keyword
  pills, summary, verified source link
- **Search** — real-time filter by title, keywords, or summary text
- **Keyword filtering** — click any keyword pill to show only items with
  that keyword
- **Dark/light mode** — toggle persists via localStorage
- **Keyboard shortcuts**: `j/k` or arrow keys to navigate items, `/` to
  focus search, `Enter` to open item link, `Escape` to clear filters
- **Responsive** — works on mobile and desktop

The generated HTML embeds its processed JSON, so it can be re-styled later
without the original data. To re-apply the current design to every saved
digest (e.g. after a template or design change), run:

```bash
python3 scripts/generate_html.py --rebuild-dir ~/Desktop/agentic-knowledge-digest
```

This regenerates each `YYYY-MM-DD.html` from its `*-processed.json` (or, if
that file is gone, from the data embedded in the HTML). Otherwise, do not
hand-edit the HTML after generation — re-process the JSON and regenerate.

## Content quality rules

- **Never fabricate.** If `raw_content` is nearly empty and the URL is
  unavailable, write `[limited detail]` as the summary.
- **Preserve nuance.** If the source says "may launch" or "reportedly,"
  reflect that uncertainty. Do not convert speculation into fact.
- **Be specific.** Prefer "GraphRAG 2.0 achieves 94.2% on MultiHop-RAG benchmark"
  over "GraphRAG improved performance."
- **Attribute claims.** Include attribution when the source cites a specific
  person or report: "according to lead researcher."
- **Bilingual titles.** Every item gets both English and Chinese title.
  For EN items, translate the title to Chinese. For ZH items, translate to
  English. The Chinese title goes in `title_zh`.

## References

- `references/sources.md` — full list of RSS feeds, research blogs, APIs,
  affiliation keywords, focus topic keywords, and content filter rules. Read
  this when adding or modifying sources.

## Cron setup (only on explicit request)

If the user explicitly asks to schedule this as a daily cron job, set up a
launchd plist (macOS) or crontab entry that runs:

```bash
python3 -c "import feedparser, requests; from bs4 import BeautifulSoup" 2>/dev/null || \
  pip3 install -r /path/to/scripts/requirements.txt
python3 /path/to/fetch_digest.py --verify-links --save-raw
```

Note: the cron entry only fetches raw data. The user runs the agent to process
and generate the HTML interactively.

Do not set up cron/launchd unprompted. The default behavior is one-time,
on-demand.
