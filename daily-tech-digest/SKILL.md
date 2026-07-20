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
  wants to catch up on the latest research papers. Also trigger for 'weekly
  roundup,' 'this week's news,' 'week in review,' 'weekly digest,' 'week of
  <date>,' or any request spanning multiple days.
---

# Daily AI & Tech Digest

Produce a fact-only daily or weekly digest of AI and technology news as an interactive
HTML page. The digest is saved to `~/Desktop/news-digest/YYYY-MM-DD.html`
(daily) or `~/Desktop/news-digest/YYYY-MM-DD-WNN-week.html` (weekly).

## Design principles

- **Facts only.** Never invent details. If source content is thin, write a
  shorter summary rather than padding it.
- **Interactive.** The HTML page provides search, keyword filtering, dark/light
  mode, keyboard navigation, and collapsible sections.
- **Traceable.** Every item links to its verified source. A Sources list at the
  bottom lists every origin.
- **Language-respecting.** Chinese content stays in Chinese. All titles are
  bilingual (English / Chinese) so both audiences can scan.
- **Capped and ranked.** Maximum 40 items (daily) or 45 items (weekly),
  prioritized by relevance to
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

**If the user chooses (B) Start fresh**, also ask about scope before continuing:

- **(1) Single-day digest** (40 items) — today only (or `--date` if specified).
- **(2) Weekly digest** (45 items, Mon-Sun week) — pull all 7 days of the
  calendar week containing the target date. Reuses cached daily raw data if
  available.

Default to (1) unless the user mentions "weekly," "this week," "past 7 days,"
"roundup," or similar multi-day phrases — in which case default to (2).

Then continue with Step 1 below.

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

**Single-day:**
```bash
python3 scripts/fetch_digest.py --verify-links --save-raw

# ...or target a specific date:
python3 scripts/fetch_digest.py --date 2026-07-04 --verify-links --save-raw
```

When `--date` is given, every source (RSS, GitHub, HuggingFace, arXiv) is scoped
to that **single UTC calendar day only**. Running the fetcher sequentially for
different dates never produces overlapping (crossover) items, so each
`YYYY-MM-DD-raw.json` contains that day's news exclusively.

**Weekly (Mon-Sun week containing the given date or today):**
```bash
python3 scripts/fetch_digest.py --date 2026-07-04 --week --save-raw
```

This produces `~/Desktop/news-digest/YYYY-MM-DD-raw.json` (daily) or
`~/Desktop/news-digest/YYYY-MM-DD-WNN-week-raw.json` (weekly). The JSON contains
an `items` array with fields: `title`, `url`, `source`, `date`, `language`,
`section`, `raw_content`, `organization`, `arxiv_id`, `link_verified`,
`focus_match`, `priority_hint`.

The fetcher now uses **parallel I/O** by default:
- RSS feeds: 8 concurrent workers, 30s per-feed timeout
- Link verification: 20 concurrent HEAD requests, 5s per-URL timeout
- RSS, GitHub, and HuggingFace run concurrently
- arXiv uses combined-category query (1 API call instead of 6)

If any source fails, the script logs a warning to stderr and continues.

### Step 1.5 — Pre-process raw items (mechanical work)

Run the pre-processor to handle all mechanical tasks — filtering, ranking,
capping, keyword extraction hints, highlight detection, section grouping:

```bash
python3 scripts/process_digest.py ~/Desktop/news-digest/YYYY-MM-DD-raw.json \
  -o ~/Desktop/news-digest/YYYY-MM-DD-semi.json
```

For weekly:
```bash
python3 scripts/process_digest.py ~/Desktop/news-digest/YYYY-MM-DD-WNN-week-raw.json \
  -o ~/Desktop/news-digest/YYYY-MM-DD-WNN-week-semi.json --weekly
```

This script performs the following **without any LLM involvement**:
1. **Content filtering** — removes crypto/NFT/DeFi speculation items
2. **Ranking** — sorts by `priority_hint` descending, then recency
3. **Capping** — keeps top 40 (daily) or 45 (weekly) items
4. **Keyword hints** — extracts candidate keywords from titles and raw_content
   (stored in the `keywords` field as starting hints for the agent)
5. **Highlight detection** — pre-scores items for significance and sets
   `is_highlight` on top candidates (up to 10)
6. **Section grouping** — organizes items into sections, builds stats, collects
   sources

The `-semi.json` output has the same schema as the final `-processed.json` but
with placeholder summaries and title translations. The agent only needs to
fill in the creative work.

### Step 2 — Add summaries and translations (creative work only)

Read the semi-processed JSON and for **every item** add:

1. **`title_zh`** — Chinese translation of the title (for EN items) or the
   original Chinese title (for ZH items). Every item gets a Chinese title.
2. **`summary`** — 1-2 sentence factual summary in the item's language.
   Paraphrase from `raw_content`, never copy-paste. If source is thin, write
   one sentence. Never add information not present in the source.
3. **`keywords`** — Review and refine the pre-extracted keyword hints. Ensure
   3-5 accurate keywords per item, each with a domain assignment. Keywords
   match the item's language.

### Step 3 — Verify highlights and daily keywords

**Highlights**: Review the pre-scored `is_highlight` flags. Remove highlights
from items that don't genuinely qualify. Keep only items that represent:

- New model release (GPT, Claude, Gemini, DeepSeek, Llama, Qwen class)
- Major product or hardware launch
- Significant milestone (100M+ users, $1B+ revenue, record benchmark)
- Scandal or controversy (data breach, safety incident, high-profile departure)
- Major acquisition or funding ($1B+)
- Regulatory action with broad industry impact
- Major open-source release (framework, model weights, dataset)

If no items truly qualify, set `is_highlight: false` on all — the Highlights
section will be omitted.

**Daily keywords**: Review and replace the pre-synthesized daily keywords.
Look across all items and produce 8-12 semantically meaningful themes that
characterize the day's news, not just frequency counts. Use a mix of English
and Chinese where appropriate.

### Step 4 — Write processed JSON and generate HTML

The semi-processed JSON from Step 1.5 already has the correct schema structure
(sections, stats, sources, keyword hints). After adding summaries and translations:

1. Read `~/Desktop/news-digest/YYYY-MM-DD-semi.json`
2. For each item in every section, fill in `title_zh` and `summary`
3. Refine `keywords` and `daily_keywords`
4. Verify `is_highlight` flags
5. Save as `~/Desktop/news-digest/YYYY-MM-DD-processed.json`
6. Run `python3 scripts/generate_html.py ~/Desktop/news-digest/YYYY-MM-DD-processed.json`

This writes `~/Desktop/news-digest/YYYY-MM-DD.html` (daily) or
`~/Desktop/news-digest/YYYY-MM-DD-WNN-week.html` (weekly). The filename comes
from the `date` (and `week_number` for weekly) field. For weekly digests the
date is Monday and NN is the ISO week number. The processed JSON is also
embedded inside the HTML, so the page can be re-styled later even if the JSON
is gone. Open the file in the user's default browser:

```bash
open ~/Desktop/news-digest/YYYY-MM-DD.html
```

Display a brief stats summary in the conversation (total items, section
counts, top daily keywords) so the user gets a preview without opening
the file.

### Step 5 — HTML page features

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
