#!/usr/bin/env python3
"""
generate_html.py — Read a processed JSON digest and produce a self-contained
interactive HTML page. Zero external dependencies.

Usage:
    python3 generate_html.py processed.json
    python3 generate_html.py processed.json -o ~/Desktop/news-digest/2026-06-27.html
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime


KEYWORD_DOMAINS = {
    "rag-retrieval": {
        "label": "RAG / Retrieval",
        "light_bg": "#dbeafe", "light_text": "#1e40af",
        "dark_bg": "#1e3a5f", "dark_text": "#93c5fd",
    },
    "agent-memory": {
        "label": "Agent Memory",
        "light_bg": "#fce7f3", "light_text": "#9d174d",
        "dark_bg": "#4a1942", "dark_text": "#f9a8d4",
    },
    "knowledge-graph": {
        "label": "Knowledge Graphs",
        "light_bg": "#dcfce7", "light_text": "#166534",
        "dark_bg": "#14532d", "dark_text": "#86efac",
    },
    "knowledge-lifecycle": {
        "label": "Knowledge Lifecycle",
        "light_bg": "#fef3c7", "light_text": "#92400e",
        "dark_bg": "#422006", "dark_text": "#fcd34d",
    },
    "agent-architecture": {
        "label": "Agent Architecture",
        "light_bg": "#ffedd5", "light_text": "#9a3412",
        "dark_bg": "#431407", "dark_text": "#fdba74",
    },
    "embeddings-vectors": {
        "label": "Embeddings / Vectors",
        "light_bg": "#ede9fe", "light_text": "#5b21b6",
        "dark_bg": "#3b0764", "dark_text": "#c4b5fd",
    },
    "ai-knowledge": {
        "label": "AI Knowledge",
        "light_bg": "#e0e7ff", "light_text": "#3730a3",
        "dark_bg": "#1e1b4b", "dark_text": "#a5b4fc",
    },
    "cognition-reasoning": {
        "label": "Cognition / Reasoning",
        "light_bg": "#fce4ec", "light_text": "#9a1a1a",
        "dark_bg": "#4a1525", "dark_text": "#fca5a5",
    },
    "context-prompting": {
        "label": "Context / Prompting",
        "light_bg": "#f3e8ff", "light_text": "#6b21a8",
        "dark_bg": "#3b0764", "dark_text": "#d8b4fe",
    },
    "evaluation-benchmark": {
        "label": "Evaluation",
        "light_bg": "#f1f5f9", "light_text": "#334155",
        "dark_bg": "#1e293b", "dark_text": "#94a3b8",
    },
    "other": {
        "label": "Other",
        "light_bg": "#f5f5f5", "light_text": "#525252",
        "dark_bg": "#262626", "dark_text": "#a3a3a3",
    },
}


def kw_color(domain):
    d = KEYWORD_DOMAINS.get(domain, KEYWORD_DOMAINS["other"])
    return d["light_bg"], d["light_text"], d["dark_bg"], d["dark_text"]


def render_keyword(kw):
    lb, lt, db, dt = kw_color(kw.get("domain", "other"))
    return (
        f'<span class="kw-pill" style="--kw-lb:{lb};--kw-lt:{lt};'
        f'--kw-db:{db};--kw-dt:{dt}" data-domain="{kw["domain"]}">'
        f'{kw["text"]}</span>'
    )


def render_item(item):
    org_html = ""
    if item.get("organization"):
        org_html = f'<span class="item-org">{item["organization"]}</span>'

    title_html = item.get("title", "")
    if item.get("title_zh"):
        title_html += f'<div class="title-zh">{item["title_zh"]}</div>'

    kws_html = " ".join(render_keyword(k) for k in item.get("keywords", []))

    summary = item.get("summary", "")
    if not summary and item.get("summary_zh"):
        summary = item["summary_zh"]

    arxiv_tag = ""
    if item.get("arxiv_id"):
        arxiv_tag = f'<span class="arxiv-tag">arxiv:{item["arxiv_id"]}</span>'

    lang_note = ""
    if item.get("language") == "zh":
        lang_note = '<span class="lang-note">中文内容</span>'

    link_tag = item.get("url", "")
    source_tag = item.get("source", "")
    verified = ""
    if item.get("link_verified"):
        verified = '<span class="link-ok" title="Link verified">&#10003;</span>'

    return f"""<div class="item-card" data-keywords="{' '.join(k['text'] for k in item.get('keywords', []))}">
  <div class="item-meta">
    {org_html}
    {arxiv_tag}
    {lang_note}
    <span class="item-source">{source_tag}</span>
    {verified}
  </div>
  <div class="item-title">{title_html}</div>
  <div class="item-keywords">{kws_html}</div>
  <div class="item-summary">{summary}</div>
  <a class="item-link" href="{link_tag}" target="_blank" rel="noopener">&rarr; {_domain(link_tag)}</a>
</div>"""


def _domain(url):
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except Exception:
        return url


def render_section(sec):
    if not sec.get("items"):
        return ""
    items_html = "\n".join(render_item(it) for it in sec["items"])
    sec_id = sec.get("id", "")
    label = sec.get("label", sec_id)
    count = len(sec["items"])
    hl_class = ""
    if sec_id == "highlights":
        hl_class = " section-highlights"
    return f"""<section class="news-section{hl_class}" id="sec-{sec_id}">
  <h2 class="section-header" onclick="toggleSection(this)" data-target="sec-{sec_id}">
    <span class="section-arrow collapsed">&#9654;</span>
    <span class="section-arrow expanded">&#9660;</span>
    {label}
    <span class="section-count">[{count}]</span>
  </h2>
  <div class="section-body collapsed">
    {items_html}
  </div>
</section>"""


def render_stats(stats, daily_keywords):
    section_bars = ""
    max_count = max(stats.get("section_counts", {}).values()) if stats.get("section_counts") else 1
    labels = {
        "research_papers": "Research Papers",
        "tools_frameworks": "Tools & Frameworks",
        "models_embeddings": "Models & Embeddings",
        "blogs_insights": "Blogs & Insights",
        "industry_applications": "Industry & Deployments",
    }
    for sec_id, count in stats.get("section_counts", {}).items():
        pct = int(count / max_count * 100) if max_count else 0
        label = labels.get(sec_id, sec_id)
        section_bars += f"""<div class="stat-row">
  <span class="stat-label">{label}</span>
  <div class="stat-bar-wrap"><div class="stat-bar" style="width:{pct}%"></div></div>
  <span class="stat-count">{count}</span>
</div>"""

    kw_html = " ".join(render_keyword(kw) for kw in daily_keywords)

    return f"""<div class="stats-panel">
  <div class="stats-summary">
    <span class="stat-big">{stats.get("total_items", 0)} items</span>
    <span class="stat-sep">&middot;</span>
    <span>{stats.get("sources_count", 0)} sources</span>
    <span class="stat-sep">&middot;</span>
    <span class="stat-ok">{stats.get("links_verified_count", 0)}/{stats.get("total_items", 0)} links verified &#10003;</span>
  </div>
  <div class="stats-bars">{section_bars}</div>
  <div class="daily-keywords">
    <span class="dk-label">Daily Keywords</span>
    {kw_html}
  </div>
</div>"""


def render_sources(sources):
    if not sources:
        return ""
    lis = "\n".join(
        f'<li><a href="{s["url"]}" target="_blank" rel="noopener">{s["name"]}</a></li>'
        for s in sources
    )
    return f"""<section class="sources-section" id="sources">
  <h2 class="section-header">Sources</h2>
  <ul class="sources-list">{lis}</ul>
</section>"""


def generate_html(data):
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    stats = data.get("stats", {})
    daily_keywords = data.get("daily_keywords", [])
    sections = data.get("sections", [])
    sources = data.get("sources", [])

    # Build nav links from sections
    nav_links = ""
    for sec in sections:
        if sec.get("items"):
            sid = sec.get("id", "")
            label = sec.get("label", sid)
            nav_links += f'<a href="#sec-{sid}" class="nav-link">{label}</a>\n'

    stats_html = render_stats(stats, daily_keywords)
    sections_html = "\n".join(render_section(sec) for sec in sections)
    sources_html = render_sources(sources)

    data_blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    embedded = f'<script type="application/json" id="digest-data">{data_blob}</script>'

    return CSS + f"""</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <div class="header-left">
      <h1 class="site-title">Agentic Knowledge Digest</h1>
      <div class="header-date">{date_str}</div>
    </div>
    <nav class="header-nav">{nav_links}</nav>
    <div class="header-actions">
      <input type="search" id="search" class="search-input" placeholder="Filter ..." oninput="doSearch()" autocomplete="off">
      <button id="theme-toggle" class="theme-btn" onclick="toggleTheme()" title="Toggle dark/light mode">&#9788;</button>
    </div>
  </div>
</header>
<main>
  {stats_html}
  {sections_html}
</main>
<footer>
  {sources_html}
  <div class="footer-note">Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} &mdash; agentic-knowledge-digest</div>
</footer>
{embedded}
{JS}
</body>
</html>"""


CSS = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agentic Knowledge Digest</title>
<style>
/* ── Reset & Variables ─────────────────────────────────────────────────── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root {
  --bg: #ffffff; --bg2: #f8f9fa;
  --text: #1a1a2e; --text2: #4b5563; --text3: #6b7280;
  --border: #e5e7eb; --accent: #2563eb;
  --card-bg: #ffffff; --card-shadow: 0 1px 3px rgba(0,0,0,.06);
  --card-hover-shadow: 0 4px 12px rgba(0,0,0,.1);
  --hl-bg: #fffbeb; --hl-border: #fcd34d;
  --stat-bar-bg: #e5e7eb; --stat-bar-fill: #2563eb;
  --header-bg: #ffffff; --header-border: #e5e7eb;
  --search-bg: #f3f4f6; --search-focus: #ffffff;
  --radius: 8px; --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --mono: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
}
.dark {
  --bg: #0d1117; --bg2: #161b22;
  --text: #e6edf3; --text2: #8b949e; --text3: #6e7681;
  --border: #30363d; --accent: #58a6ff;
  --card-bg: #161b22; --card-shadow: 0 1px 3px rgba(0,0,0,.3);
  --card-hover-shadow: 0 4px 12px rgba(0,0,0,.5);
  --hl-bg: #1a1a0a; --hl-border: #674d00;
  --stat-bar-bg: #30363d; --stat-bar-fill: #58a6ff;
  --header-bg: #161b22; --header-border: #30363d;
  --search-bg: #0d1117; --search-focus: #161b22;
}

/* ── Body ──────────────────────────────────────────────────────────────── */
body {
  font-family: var(--font); background: var(--bg); color: var(--text);
  line-height: 1.6; min-height: 100vh;
}

/* ── Header ────────────────────────────────────────────────────────────── */
.site-header {
  position: sticky; top: 0; z-index: 100;
  background: var(--header-bg); border-bottom: 1px solid var(--header-border);
  padding: 12px 0;
}
.header-inner {
  max-width: 960px; margin: 0 auto; padding: 0 20px;
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}
.header-left { display: flex; align-items: baseline; gap: 12px; }
.site-title { font-size: 1.1rem; font-weight: 700; white-space: nowrap; }
.header-date { font-size: .85rem; color: var(--text3); font-family: var(--mono); }
.header-nav { display: flex; gap: 6px; flex-wrap: wrap; flex: 1; }
.nav-link {
  font-size: .75rem; color: var(--text3); text-decoration: none;
  padding: 2px 8px; border-radius: 4px; white-space: nowrap;
}
.nav-link:hover { color: var(--accent); background: var(--bg2); }
.header-actions { display: flex; align-items: center; gap: 8px; margin-left: auto; }
.search-input {
  padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px;
  font-size: .85rem; background: var(--search-bg); color: var(--text);
  width: 180px; outline: none; font-family: var(--font);
}
.search-input:focus { background: var(--search-focus); border-color: var(--accent); }
.theme-btn {
  background: none; border: 1px solid var(--border); border-radius: 6px;
  padding: 4px 10px; cursor: pointer; font-size: 1rem; color: var(--text);
  line-height: 1;
}
.theme-btn:hover { background: var(--bg2); }

/* ── Main ──────────────────────────────────────────────────────────────── */
main { max-width: 960px; margin: 0 auto; padding: 24px 20px; }

/* ── Stats Panel ───────────────────────────────────────────────────────── */
.stats-panel {
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px; margin-bottom: 24px;
  box-shadow: var(--card-shadow);
}
.stats-summary { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 14px; font-size: .9rem; }
.stat-big { font-weight: 700; font-size: 1.05rem; }
.stat-sep { color: var(--text3); }
.stat-ok { color: #16a34a; }
.dark .stat-ok { color: #4ade80; }
.stats-bars { margin-bottom: 16px; }
.stat-row {
  display: flex; align-items: center; gap: 10px; margin-bottom: 6px;
}
.stat-label { min-width: 120px; font-size: .8rem; color: var(--text2); text-align: right; }
.stat-bar-wrap { flex: 1; height: 8px; background: var(--stat-bar-bg); border-radius: 4px; overflow: hidden; }
.stat-bar {
  display: block;
  height: 100%; background: var(--stat-bar-fill); border-radius: 4px;
  transition: width .6s ease; min-width: 4px;
}
.stat-count { min-width: 24px; font-size: .8rem; font-weight: 600; color: var(--text); font-family: var(--mono); }

/* ── Daily Keywords ────────────────────────────────────────────────────── */
.daily-keywords { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding-top: 12px; border-top: 1px solid var(--border); }
.dk-label { font-size: .8rem; font-weight: 600; color: var(--text2); margin-right: 4px; }

/* ── Keyword pills ─────────────────────────────────────────────────────── */
.kw-pill {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: .78rem; font-family: var(--mono); cursor: pointer;
  user-select: none; transition: transform .1s;
  background: var(--kw-lb); color: var(--kw-lt);
}
.dark .kw-pill { background: var(--kw-db); color: var(--kw-dt); }
.kw-pill:hover { transform: scale(1.05); }
.kw-pill.active-filter { outline: 2px solid var(--accent); outline-offset: 1px; }

/* ── Sections ──────────────────────────────────────────────────────────── */
.news-section { margin-bottom: 20px; }
.section-highlights .item-card {
  border-left: 3px solid var(--hl-border); background: var(--hl-bg);
}
.section-header {
  font-size: 1rem; font-weight: 700; padding: 10px 0;
  cursor: pointer; user-select: none; display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid var(--border);
}
.section-header:hover { color: var(--accent); }
.section-arrow { font-size: .7rem; color: var(--text3); transition: transform .2s; }
.section-arrow.expanded { display: none; }
.section-body.expanded .section-arrow.collapsed { display: none; }
.section-body.expanded .section-arrow.expanded { display: inline; }
.section-count { font-size: .8rem; color: var(--text3); font-weight: 400; }
.section-body.collapsed { display: none; }
.section-body { padding: 8px 0; }

/* ── Item cards ────────────────────────────────────────────────────────── */
.item-card {
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px; margin-bottom: 10px;
  box-shadow: var(--card-shadow); transition: box-shadow .15s, transform .15s;
  position: relative;
}
.item-card:hover { box-shadow: var(--card-hover-shadow); }
.item-card.hidden { display: none; }
.item-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
.item-org {
  font-size: .72rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: .04em; color: var(--accent);
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  padding: 1px 8px; border-radius: 4px;
}
.item-source { font-size: .75rem; color: var(--text3); }
.arxiv-tag { font-size: .72rem; color: var(--text3); font-family: var(--mono); }
.lang-note { font-size: .7rem; color: var(--text3); font-style: italic; }
.link-ok { color: #16a34a; font-size: .8rem; }
.dark .link-ok { color: #4ade80; }
.item-title { font-size: .95rem; font-weight: 650; margin-bottom: 6px; line-height: 1.4; }
.title-zh { display: block; font-weight: 400; color: var(--text2); font-size: .88rem; margin-top: 3px; line-height: 1.4; }
.item-keywords { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 8px; }
.item-summary { font-size: .85rem; color: var(--text2); margin-bottom: 8px; line-height: 1.5; }
.item-link {
  font-size: .8rem; color: var(--accent); text-decoration: none;
  font-family: var(--mono);
}
.item-link:hover { text-decoration: underline; }

/* ── Sources ───────────────────────────────────────────────────────────── */
.sources-section { margin-top: 32px; padding-top: 16px; border-top: 1px solid var(--border); }
.sources-list { list-style: none; display: flex; flex-wrap: wrap; gap: 6px 16px; padding: 12px 0; }
.sources-list a { font-size: .8rem; color: var(--text2); text-decoration: none; }
.sources-list a:hover { color: var(--accent); text-decoration: underline; }

/* ── Footer ────────────────────────────────────────────────────────────── */
.footer-note {
  text-align: center; font-size: .72rem; color: var(--text3);
  padding: 24px 0 12px;
}

/* ── Responsive ────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .header-inner { flex-direction: column; align-items: flex-start; }
  .header-actions { margin-left: 0; width: 100%; }
  .search-input { width: 100%; }
  .stat-label { min-width: 80px; font-size: .72rem; }
  .item-title { font-size: .88rem; }
}
</style>"""


JS = """
<script>
(function() {
  // ── Theme ───────────────────────────────────────────────────────────
  const saved = localStorage.getItem('digest-theme');
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  }
  window.toggleTheme = function() {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('digest-theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
  };

  // ── Section toggle ──────────────────────────────────────────────────
  window.toggleSection = function(header) {
    const target = header.getAttribute('data-target');
    const body = document.querySelector('#' + target + ' .section-body');
    if (!body) return;
    body.classList.toggle('collapsed');
    body.classList.toggle('expanded');
  };

  // Expand first non-empty section by default
  const firstSection = document.querySelector('.news-section .section-body');
  if (firstSection) {
    setTimeout(function() {
      firstSection.classList.remove('collapsed');
      firstSection.classList.add('expanded');
    }, 10);
  }

  // ── Search ──────────────────────────────────────────────────────────
  let activeFilter = null;
  window.doSearch = function() {
    const q = document.getElementById('search').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.item-card');
    cards.forEach(function(card) {
      const text = (card.textContent || '').toLowerCase();
      const kw = (card.getAttribute('data-keywords') || '').toLowerCase();
      const match = !q || text.includes(q) || kw.includes(q);
      if (match && (!activeFilter || kw.includes(activeFilter))) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  };

  // ── Keyword filter click ────────────────────────────────────────────
  document.addEventListener('click', function(e) {
    if (!e.target.classList.contains('kw-pill')) return;
    const kwText = e.target.textContent.toLowerCase();
    const pills = document.querySelectorAll('.kw-pill');
    if (activeFilter === kwText) {
      activeFilter = null;
      pills.forEach(function(p) { p.classList.remove('active-filter'); });
    } else {
      activeFilter = kwText;
      pills.forEach(function(p) {
        if (p.textContent.toLowerCase() === kwText) p.classList.add('active-filter');
        else p.classList.remove('active-filter');
      });
    }
    doSearch();
  });

  // ── Keyboard shortcuts ──────────────────────────────────────────────
  let focusIdx = -1;
  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT') return;
    const cards = Array.from(document.querySelectorAll('.item-card:not(.hidden)'));
    if (e.key === 'j' || e.key === 'ArrowDown') {
      e.preventDefault();
      focusIdx = Math.min(focusIdx + 1, cards.length - 1);
      cards.forEach(function(c, i) { c.style.outline = i === focusIdx ? '2px solid var(--accent)' : ''; });
      if (cards[focusIdx]) cards[focusIdx].scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (e.key === 'k' || e.key === 'ArrowUp') {
      e.preventDefault();
      focusIdx = Math.max(focusIdx - 1, 0);
      cards.forEach(function(c, i) { c.style.outline = i === focusIdx ? '2px solid var(--accent)' : ''; });
      if (cards[focusIdx]) cards[focusIdx].scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (e.key === 'Enter' && focusIdx >= 0 && cards[focusIdx]) {
      const link = cards[focusIdx].querySelector('.item-link');
      if (link) window.open(link.href, '_blank');
    } else if (e.key === '/') {
      e.preventDefault();
      document.getElementById('search').focus();
    } else if (e.key === 'Escape') {
      document.getElementById('search').value = '';
      activeFilter = null;
      document.querySelectorAll('.kw-pill').forEach(function(p) { p.classList.remove('active-filter'); });
      doSearch();
      focusIdx = -1;
      cards.forEach(function(c) { c.style.outline = ''; });
    }
  });
})();
</script>"""


_DATA_RE = re.compile(
    r'<script[^>]*id="digest-data"[^>]*>(.*?)</script>',
    re.DOTALL,
)


def _load_data_from_html(path):
    """Extract the embedded digest JSON from a previously generated HTML file."""
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = _DATA_RE.search(html)
    if not m:
        return None
    return json.loads(m.group(1))


def load_data(path):
    """Load digest data from a processed JSON file or an HTML file with embedded data."""
    if path.endswith((".html", ".htm")):
        return _load_data_from_html(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def output_path_for(data, src_path, explicit=None):
    """Derive the output HTML path. Prefers data['date'] so the name is always
    YYYY-MM-DD.html, regardless of the input filename. For weekly digests,
    uses YYYY-MM-DD-WNN-week.html."""
    if explicit:
        return explicit
    directory = os.path.dirname(os.path.abspath(src_path))
    date = data.get("date")
    week_number = data.get("week_number")
    if date and week_number:
        return os.path.join(directory, f"{date}-W{week_number}-week.html")
    if date:
        return os.path.join(directory, f"{date}.html")
    stem = os.path.basename(src_path).rsplit(".", 1)[0]
    if stem.endswith("-processed"):
        stem = stem[: -len("-processed")]
    return os.path.join(directory, f"{stem}.html")


def write_html(data, output_path):
    html = generate_html(data)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def rebuild_dir(directory):
    """Regenerate every digest in `directory` with the current template.

    Re-renders from each `*-processed.json` first, then from the data embedded
    in any remaining HTML files that have no corresponding processed JSON."""
    import glob

    built = 0
    skipped = 0
    built_outputs = set()

    for json_path in sorted(glob.glob(os.path.join(directory, "*-processed.json"))):
        try:
            data = load_data(json_path)
            out = output_path_for(data, json_path)
            write_html(data, out)
        except Exception as exc:
            print(f"  [skip] {os.path.basename(json_path)}: {exc}", file=sys.stderr)
            skipped += 1
            continue
        built_outputs.add(os.path.abspath(out))
        built += 1
        print(f"  [ok]   {os.path.basename(out)} (from {os.path.basename(json_path)})", file=sys.stderr)

    for html_path in sorted(glob.glob(os.path.join(directory, "*.html"))):
        if os.path.abspath(html_path) in built_outputs:
            continue
        try:
            data = _load_data_from_html(html_path)
        except Exception as exc:
            print(f"  [skip] {os.path.basename(html_path)}: {exc}", file=sys.stderr)
            skipped += 1
            continue
        if data is None:
            print(f"  [skip] {os.path.basename(html_path)}: no embedded data and no *-processed.json", file=sys.stderr)
            skipped += 1
            continue
        write_html(data, html_path)
        built += 1
        print(f"  [ok]   {os.path.basename(html_path)} (from embedded data)", file=sys.stderr)

    print(f"Rebuild complete — rebuilt {built}, skipped {skipped}.", file=sys.stderr)
    return built, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive HTML digest from a processed JSON file."
    )
    parser.add_argument(
        "input", nargs="?",
        help="Path to a processed JSON digest, or an HTML digest with embedded data",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output HTML file path (default: <date>.html beside the input)",
    )
    parser.add_argument(
        "--rebuild-dir",
        help="Regenerate every digest in this directory with the current template "
             "(from each *-processed.json, or data embedded in existing HTML).",
    )
    args = parser.parse_args()

    if args.rebuild_dir:
        if not os.path.isdir(args.rebuild_dir):
            parser.error(f"--rebuild-dir: not a directory: {args.rebuild_dir}")
        print(f"Rebuilding digests in {args.rebuild_dir} ...", file=sys.stderr)
        rebuild_dir(args.rebuild_dir)
        return

    if not args.input:
        parser.error("provide an INPUT file or use --rebuild-dir")

    data = load_data(args.input)
    if data is None:
        parser.error(f"could not load digest data from {args.input}")

    output_path = output_path_for(data, args.input, args.output)
    write_html(data, output_path)
    print(f"HTML digest written → {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
