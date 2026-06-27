---
name: daily-tech-digest
description: >
  Fetches and summarizes the day's AI/tech news from US, China, GitHub Trending,
  HuggingFace, and arXiv into an interactive HTML digest saved to
  ~/Desktop/news-digest/. Use this skill whenever the user mentions daily news,
  tech digest, AI news roundup, research paper updates, what's happening in AI
  today, morning briefing, tech headlines, arxiv updates, or wants a summary of
  what's going on in the AI/tech world — even if they don't explicitly say
  "digest" or "daily." Also trigger when the user asks about recent
  developments from specific companies (OpenAI, Google, DeepSeek, etc.) or
  wants to catch up on the latest research papers.
---

# Daily AI & Tech Digest

Produce a fact-only daily digest of AI and technology news as an interactive
HTML page. The digest is saved to `~/Desktop/news-digest/YYYY-MM-DD.html`.

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
  focus industries (embodied AI, chip EDA, robotics, AI/ML, semiconductors).

## Workflow

### Step 0 — Ask the user: rebuild or start fresh

Before doing anything else, **ask the user which mode they want**:

- **(A) Re-generate HTML from existing data** — re-apply the current template/design
  to digests that were already produced. No network fetch.
- **(B) Start fresh** — pull today's news from all sources, process it, and
  generate a new HTML digest.

First check whether prior data exists:

```bash
ls -1 ~/Desktop/news-digest/*-processed.json ~/Desktop/news-digest/*.html 2>/dev/null
```

- If **no** existing digests are found, skip the question and go straight to
  **fresh** (Step 1) — there is nothing to rebuild.
- If existing digests **are** found, ask the user to choose A or B before
  continuing. Default to whatever they request in their message (e.g. "regenerate
  my digests" → A; "give me today's news" → B).

**If the user chooses (A) Re-generate:**

Run the rebuilder, then open the result. This skips Steps 1–7 entirely.

```bash
# Re-apply the current design to every saved digest:
python3 scripts/generate_html.py --rebuild-dir ~/Desktop/news-digest

# ...or rebuild a single date from its data (processed JSON or the HTML itself):
python3 scripts/generate_html.py ~/Desktop/news-digest/YYYY-MM-DD-processed.json
```

Then open the regenerated file(s) (e.g. `open ~/Desktop/news-digest/YYYY-MM-DD.html`)
and you are done — do **not** fetch or re-process.

**If the user chooses (B) Start fresh**, continue with Step 1 below.

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

This produces `~/Desktop/news-digest/YYYY-MM-DD-raw.json` and prints the
JSON to stdout. The JSON contains an `items` array with fields: `title`,
`url`, `source`, `date`, `language`, `section`, `raw_content`, `organization`,
`arxiv_id`, `link_verified`, `focus_match`, `priority_hint`.

- `focus_match` lists which focus industries the item matches
  (e.g. `["embodied-ai", "robotics"]`).
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
| `ai-ml` | AI models, training, inference, transformers, LLMs, diffusion, RL |
| `hardware` | Chips, EDA, semiconductor, fabrication, memory chips, HBM |
| `robotics` | Embodied AI, humanoid robots, manipulation, autonomous driving, 机器人 |
| `software` | Open-source, frameworks, compilers, benchmarks, APIs, engineering |
| `org-product` | Specific companies, product names, model names (OpenAI, GPT-5) |
| `safety` | Alignment, regulation, data breach, policy, red-teaming |
| `other` | Anything that doesn't fit the above |

Keywords match the item's language: English keywords for EN items, Chinese
keywords (e.g. `大模型`, `具身智能`) for ZH items.

### Step 3 — Rank, cap, and select

**Rank** all items by: `priority_hint` (descending) > recency > content depth.

**Cap** at 25 items total. Keep the highest-ranked 25.

**Highlights**: From the top 25, select up to 10 items that qualify as
exceptional significance (see criteria below). Set `is_highlight: true`.

**Section distribution** is fluid — some days US News gets 8 items, arXiv
gets 1. Reflect real news patterns, do not force equal distribution.

An item qualifies as a Highlight if it represents:

- New model release (GPT, Claude, Gemini, DeepSeek, Llama, Qwen class)
- Major product or hardware launch
- Significant milestone (100M+ users, $1B+ revenue, record benchmark)
- Scandal or controversy (data breach, safety incident, high-profile departure)
- Major acquisition or funding ($1B+)
- Regulatory action with broad industry impact
- Major open-source release (framework, model weights, dataset)

If nothing qualifies, omit Highlights entirely. Highlights items also appear
in their regular section (duplicated, not removed).

### Step 4 — Apply content filters

**Skip** items whose primary subject is:
- Cryptocurrency (Bitcoin, Ethereum, altcoins)
- Token speculation or DeFi
- NFTs or web3 fundraising
- Blockchain used for financial speculation

**Keep** blockchain for supply chain, identity, enterprise infrastructure.

**Keep**: AI/ML, software engineering, semiconductors/chips, AI memory,
memory chips, embodied AI, chip EDA, robotics.

### Step 5 — Synthesize daily keywords

Look across all 25 selected items and synthesize **8-12 daily keywords** —
semantically meaningful themes that characterize the day's news, not just
frequency counts. Each daily keyword has the same `{"text": "...", "domain": "..."}`
structure as item keywords. Use a mix of English and Chinese where appropriate.

### Step 6 — Group into sections

Organize items into sections in this order:

1. `highlights` — items with `is_highlight: true` (up to 10)
2. `us_news` — Silicon Valley & US News
3. `china_news` — China Tech News
4. `github_trending` — GitHub Trending
5. `hf_trending` — HuggingFace Trending
6. `arxiv_top` — arXiv — Top Institution Papers
7. `arxiv_other` — arXiv — Other Notable Papers

Skip any section with zero items.

### Step 7 — Write processed JSON and generate HTML

Write the processed data as JSON conforming to this schema:

```json
{
  "date": "2026-06-27",
  "stats": {
    "total_items": 25,
    "sources_count": 12,
    "links_verified_count": 25,
    "links_failed_count": 0,
    "section_counts": {
      "us_news": 8, "china_news": 7, "github_trending": 3,
      "hf_trending": 3, "arxiv_top": 2, "arxiv_other": 2
    }
  },
  "daily_keywords": [
    {"text": "model-release", "domain": "org-product"},
    {"text": "embodied-ai", "domain": "robotics"}
  ],
  "sections": [
    {
      "id": "highlights",
      "label": "! Highlights",
      "items": [
        {
          "title": "GPT-5 Released",
          "title_zh": "GPT-5 正式发布",
          "url": "https://www.theverge.com/...",
          "source": "The Verge",
          "section": "us_news",
          "organization": "OpenAI",
          "language": "en",
          "arxiv_id": "",
          "summary": "OpenAI released GPT-5 today...",
          "keywords": [
            {"text": "multimodal", "domain": "ai-ml"},
            {"text": "benchmark-sota", "domain": "software"}
          ],
          "link_verified": true,
          "is_highlight": true
        }
      ]
    },
    {
      "id": "us_news",
      "label": "Silicon Valley & US News",
      "items": [...]
    }
  ],
  "sources": [
    {"name": "TechCrunch", "url": "https://techcrunch.com"},
    {"name": "The Verge", "url": "https://www.theverge.com"}
  ]
}
```

Save this as `~/Desktop/news-digest/YYYY-MM-DD-processed.json`, then run:

```bash
python3 scripts/generate_html.py ~/Desktop/news-digest/YYYY-MM-DD-processed.json
```

This writes `~/Desktop/news-digest/YYYY-MM-DD.html` (the filename comes from
the `date` field). The processed JSON is also embedded inside the HTML, so the
page can be re-styled later even if the JSON is gone. Open the file in the
user's default browser:

```bash
open ~/Desktop/news-digest/YYYY-MM-DD.html
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
python3 scripts/generate_html.py --rebuild-dir ~/Desktop/news-digest
```

This regenerates each `YYYY-MM-DD.html` from its `*-processed.json` (or, if
that file is gone, from the data embedded in the HTML). Otherwise, do not
hand-edit the HTML after generation — re-process the JSON and regenerate.

## Content quality rules

- **Never fabricate.** If `raw_content` is nearly empty and the URL is
  unavailable, write `[limited detail]` as the summary.
- **Preserve nuance.** If the source says "may launch" or "reportedly,"
  reflect that uncertainty. Do not convert speculation into fact.
- **Be specific.** Prefer "OpenAI released GPT-5 achieving 92.7% on MMLU"
  over "OpenAI released a new powerful model."
- **Attribute claims.** Include attribution when the source cites a specific
  person or report: "according to CEO Sam Altman."
- **Bilingual titles.** Every item gets both English and Chinese title.
  For EN items, translate the title to Chinese. For ZH items, translate to
  English. The Chinese title goes in `title_zh`.

## References

- `references/sources.md` — full list of RSS feeds, APIs, affiliation
  keywords, focus industry keywords, and content filter rules. Read this
  when adding or modifying sources.

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
