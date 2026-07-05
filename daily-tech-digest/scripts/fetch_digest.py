#!/usr/bin/env python3
"""
fetch_digest.py — Collect daily AI/tech news from RSS feeds, GitHub Trending,
HuggingFace, and arXiv. Outputs structured JSON for the agent to summarize
and format into ~/Desktop/news-digest/YYYY-MM-DD.html

Usage:
    python3 fetch_digest.py                           # JSON to stdout
    python3 fetch_digest.py --save-raw                # also save raw JSON
    python3 fetch_digest.py --verify-links            # verify all URLs
    python3 fetch_digest.py --output-dir ~/custom     # custom output dir
    python3 fetch_digest.py --hours 48                # look back 48h instead of 24h
    python3 fetch_digest.py --date 2026-07-04         # target a specific date
    python3 fetch_digest.py --date 2026-07-04 --week  # Mon-Sun week containing date
    python3 fetch_digest.py --week --save-raw         # this week, save to disk
"""

import argparse
import hashlib
import json
import os
import socket
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

# ── Config ──────────────────────────────────────────────────────────────────

MAX_FETCH_TIMEOUT = 180  # seconds — hard ceiling (3 min) for any single URL fetch

# ── Data model ──────────────────────────────────────────────────────────────

@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    date: str
    language: str
    section: str
    raw_content: str = ""
    organization: str = ""
    arxiv_id: str = ""
    link_verified: bool = True
    focus_match: list = field(default_factory=list)
    priority_hint: int = 0

# ── Focus topic detection ────────────────────────────────────────────────────

FOCUS_TOPICS = {
    "embodied-ai": {
        "keywords": ["embodied", "具身智能", "humanoid", "robot manipulation",
                     "tactile sensing", "embodied intelligence", "具身", "人形机器人"],
        "priority_boost": 10,
    },
    "chip-eda": {
        "keywords": ["EDA", "electronic design automation", "chip design",
                     "semiconductor design", "RTL", "synthesis", "place-and-route",
                     "芯片设计", "EDA工具", "芯片EDA", "physical design"],
        "priority_boost": 9,
    },
    "robotics": {
        "keywords": ["robot", "机器人", "robotics", "autonomous navigation",
                     "manipulation", "机械臂", "自动驾驶", "autonomous driving"],
        "priority_boost": 8,
    },
    "ai-ml": {
        "keywords": ["large language model", "LLM", "GPT", "Claude", "Gemini",
                     "transformer", "diffusion", "neural network", "深度学习",
                     "大模型", "deep learning", "reinforcement learning", "RLHF",
                     "foundation model", "大语言模型", "machine learning"],
        "priority_boost": 7,
    },
    "memory-chips": {
        "keywords": ["HBM", "high bandwidth memory", "memory chip", "DRAM",
                     "NAND", "AI memory", "存储芯片", "高带宽内存", "内存芯片"],
        "priority_boost": 6,
    },
    "semiconductor": {
        "keywords": ["semiconductor", "chip", "fab", "foundry", "TSMC",
                     "3nm", "5nm", "wafer", "半导体", "芯片", "晶圆"],
        "priority_boost": 5,
    },
}


def detect_focus_topics(items):
    """Scan each item's title + raw_content against focus topic keywords.
    Mutates items in place — sets focus_match and priority_hint."""
    for item in items:
        text = f"{item.title} {item.raw_content}".lower()
        matched = []
        score = 0
        for topic_id, cfg in FOCUS_TOPICS.items():
            for kw in cfg["keywords"]:
                if kw.lower() in text:
                    if topic_id not in matched:
                        matched.append(topic_id)
                        score += cfg["priority_boost"]
                    break
        item.focus_match = matched
        item.priority_hint = score

# ── Link verification ────────────────────────────────────────────────────────

def verify_links(items):
    """Send HEAD request to each item URL. Items with 4xx/5xx/timeout are removed.
    Returns filtered list."""
    ok = []
    total = len(items)
    failed = 0
    for i, item in enumerate(items):
        try:
            resp = requests.head(item.url, timeout=10, allow_redirects=True,
                                headers={"User-Agent": "daily-tech-digest/1.0"})
            if 200 <= resp.status_code < 400:
                item.link_verified = True
                ok.append(item)
            else:
                print(f"  [dead] {item.url} → HTTP {resp.status_code}", file=sys.stderr)
                item.link_verified = False
                failed += 1
        except Exception:
            print(f"  [dead] {item.url} → unreachable", file=sys.stderr)
            item.link_verified = False
            failed += 1
        if (i + 1) % 10 == 0:
            print(f"  verified {i + 1}/{total} ...", file=sys.stderr)
    print(f"  link check: {len(ok)} OK, {failed} removed", file=sys.stderr)
    return ok

# ── RSS fetcher ─────────────────────────────────────────────────────────────

RSS_FEEDS = [
    # US / Silicon Valley News
    {"url": "https://hnrss.org/frontpage?count=20", "name": "Hacker News", "section": "us_news", "language": "en"},
    {"url": "https://techcrunch.com/feed/", "name": "TechCrunch", "section": "us_news", "language": "en"},
    {"url": "https://www.theverge.com/rss/index.xml", "name": "The Verge", "section": "us_news", "language": "en"},
    {"url": "https://feeds.arstechnica.com/arstechnica/index", "name": "Ars Technica", "section": "us_news", "language": "en"},
    {"url": "https://www.technologyreview.com/feed/", "name": "MIT Tech Review", "section": "us_news", "language": "en"},
    # Apple / Google
    {"url": "https://9to5mac.com/feed/", "name": "9to5Mac", "section": "us_news", "language": "en"},
    {"url": "https://9to5google.com/feed/", "name": "9to5Google", "section": "us_news", "language": "en"},
    # Tesla / SpaceX
    {"url": "https://electrek.co/feed/", "name": "Electrek", "section": "us_news", "language": "en"},
    {"url": "https://www.teslarati.com/feed/", "name": "Teslarati", "section": "us_news", "language": "en"},
    {"url": "https://spacenews.com/feed/", "name": "SpaceNews", "section": "us_news", "language": "en"},
    # China (English)
    {"url": "https://technode.com/feed/", "name": "TechNode", "section": "china_news", "language": "en"},
    {"url": "https://www.scmp.com/rss/4/feed", "name": "SCMP Tech", "section": "china_news", "language": "en"},
    {"url": "https://pandaily.com/feed/", "name": "Pandaily", "section": "china_news", "language": "en"},
    # China (Chinese)
    {"url": "https://36kr.com/feed", "name": "36kr", "section": "china_news", "language": "zh"},
    {"url": "https://www.huxiu.com/rss/0.xml", "name": "Huxiu", "section": "china_news", "language": "zh"},
]


def fetch_rss_feeds(feeds, hours=24, target_date=None):
    items = []
    if target_date:
        date_dt = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        day_start = date_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = date_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        cutoff = day_start
        upper = day_end + timedelta(days=1)  # allow next day too for timezone fuzz
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        upper = None

    for cfg in feeds:
        try:
            resp = requests.get(
                cfg["url"],
                timeout=MAX_FETCH_TIMEOUT,
                headers={"User-Agent": "daily-tech-digest/1.0"},
            )
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            for entry in feed.entries:
                pub_date = _parse_entry_date(entry)
                if target_date:
                    if pub_date and (pub_date < cutoff or pub_date > upper):
                        continue
                else:
                    if pub_date and pub_date < cutoff:
                        continue

                content = ""
                if hasattr(entry, "summary"):
                    content = entry.summary
                elif hasattr(entry, "content") and entry.content:
                    content = entry.content[0].get("value", "")
                elif hasattr(entry, "description"):
                    content = entry.description

                items.append(NewsItem(
                    title=_clean_text(entry.get("title", "")),
                    url=entry.get("link", ""),
                    source=cfg["name"],
                    date=pub_date.isoformat() if pub_date else datetime.now(timezone.utc).isoformat(),
                    language=cfg["language"],
                    section=cfg["section"],
                    raw_content=_strip_html(content),
                ))
        except Exception as exc:
            print(f"  [warn] {cfg['name']}: {exc}", file=sys.stderr)

    return items


def _parse_entry_date(entry):
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc)
    return None


def _strip_html(text):
    if not text:
        return ""
    try:
        return BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
    except Exception:
        return text


def _clean_text(text):
    return text.strip().replace("\n", " ").replace("\r", "")

# ── GitHub Trending scraper ─────────────────────────────────────────────────

def fetch_github_trending(target_date=None):
    if target_date and target_date != datetime.now(timezone.utc).strftime("%Y-%m-%d"):
        return _fetch_github_search(target_date)
    return _fetch_github_trending_today()


def _fetch_github_trending_today():
    items = []
    try:
        resp = requests.get(
            "https://github.com/trending?since=daily",
            headers={"User-Agent": "daily-tech-digest/1.0"},
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for article in soup.find_all("article", class_="Box-row"):
            h2 = article.find("h2")
            if not h2:
                continue
            a_tag = h2.find("a")
            if not a_tag:
                continue

            repo_path = a_tag.get("href", "").strip()
            repo_name = repo_path.strip("/")

            desc_el = article.find("p", class_="col-9")
            description = desc_el.get_text(strip=True) if desc_el else ""

            lang_el = article.find("span", itemprop="programmingLanguage")
            language = lang_el.get_text(strip=True) if lang_el else ""

            detail = description
            if language:
                detail = f"{description}  [Lang: {language}]" if description else f"[Lang: {language}]"

            items.append(NewsItem(
                title=repo_name,
                url=f"https://github.com{repo_path}",
                source="GitHub Trending",
                date=datetime.now(timezone.utc).isoformat(),
                language="en",
                section="github_trending",
                raw_content=detail,
            ))
    except Exception as exc:
        print(f"  [warn] GitHub Trending: {exc}", file=sys.stderr)

    return items


def _fetch_github_search(target_date):
    """Fallback for historical dates — use GitHub Search API for repos
    created or updated on the target date."""
    items = []
    try:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        date_str = date_obj.strftime("%Y-%m-%d")
        resp = requests.get(
            "https://api.github.com/search/repositories",
            params={
                "q": f"created:{date_str}..{date_str} stars:>=10",
                "sort": "stars",
                "order": "desc",
                "per_page": 15,
            },
            headers={
                "User-Agent": "daily-tech-digest/1.0",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        for repo in data.get("items", []):
            lang = repo.get("language") or ""
            desc = repo.get("description") or ""
            detail = desc
            if lang:
                detail = f"{desc}  [Lang: {lang}]" if desc else f"[Lang: {lang}]"
            items.append(NewsItem(
                title=repo.get("full_name", ""),
                url=repo.get("html_url", ""),
                source="GitHub Trending",
                date=date_obj.replace(tzinfo=timezone.utc).isoformat(),
                language="en",
                section="github_trending",
                raw_content=detail,
            ))
    except Exception as exc:
        print(f"  [warn] GitHub Search ({target_date}): {exc}", file=sys.stderr)
    return items


# ── HuggingFace API ─────────────────────────────────────────────────────────

def fetch_huggingface_trending(target_date=None):
    items = []
    try:
        resp = requests.get(
            "https://huggingface.co/api/models",
            params={"sort": "downloads", "direction": "-1", "limit": 15, "full": "false"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        for model in data:
            model_id = model.get("modelId") or model.get("id", "")
            if not model_id:
                continue

            tags = model.get("tags", [])[:5]
            downloads = model.get("downloads", 0)
            likes = model.get("likes", 0)
            last_modified = model.get("lastModified", datetime.now(timezone.utc).isoformat())
            if target_date:
                last_modified = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat()

            parts = [f"Downloads: {downloads}", f"Likes: {likes}"]
            if tags:
                parts.append(f"Tags: {', '.join(tags)}")

            items.append(NewsItem(
                title=model_id,
                url=f"https://huggingface.co/{model_id}",
                source="HuggingFace",
                date=last_modified,
                language="en",
                section="hf_trending",
                raw_content=" | ".join(parts),
            ))
    except Exception as exc:
        print(f"  [warn] HuggingFace: {exc}", file=sys.stderr)

    return items


# ── arXiv API ───────────────────────────────────────────────────────────────

ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.CR", "cs.AR"]

ARXIV_AFFILIATIONS = {
    # US companies
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "deepmind": "DeepMind",
    "google research": "Google Research",
    "google deepmind": "Google DeepMind",
    "meta ai": "Meta AI",
    "microsoft research": "Microsoft Research",
    "apple": "Apple",
    "nvidia": "NVIDIA",
    "tesla": "Tesla",
    "xai": "xAI",
    "spacex": "SpaceX",
    # US universities
    "stanford university": "Stanford",
    "massachusetts institute of technology": "MIT",
    "carnegie mellon university": "CMU",
    "university of california, berkeley": "UC Berkeley",
    "uc berkeley": "UC Berkeley",
    # China companies
    "deepseek": "DeepSeek",
    "深度求索": "DeepSeek",
    "minimax": "MiniMax",
    "zhipu": "Zhipu AI",
    "智谱": "Zhipu AI",
    "alibaba": "Alibaba",
    "baidu": "Baidu",
    "tencent": "Tencent",
    "bytedance": "ByteDance",
    "sensetime": "SenseTime",
    # China universities
    "tsinghua university": "Tsinghua",
    "清华大学": "Tsinghua",
    "peking university": "Peking University",
    "北京大学": "Peking University",
    "shanghai ai lab": "Shanghai AI Lab",
    "上海人工智能实验室": "Shanghai AI Lab",
}


def fetch_arxiv(categories, affiliations, max_per_cat=15, target_date=None):
    items = []
    base_url = "http://export.arxiv.org/api/query"

    for category in categories:
        try:
            params = {
                "search_query": f"cat:{category}",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "start": 0,
                "max_results": max_per_cat,
            }
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)

            for entry in feed.entries:
                arxiv_id = entry.id.split("/abs/")[-1]
                if "v" in arxiv_id:
                    arxiv_id = arxiv_id.split("v")[0]

                authors_list = [a.get("name", "") for a in entry.get("authors", [])]
                authors_str = ", ".join(authors_list[:5])
                if len(authors_list) > 5:
                    authors_str += " et al."

                all_text = f"{entry.get('title', '')} {entry.get('summary', '')} {' '.join(authors_list)}".lower()

                matched = []
                for keyword, org_name in affiliations.items():
                    if keyword.lower() in all_text:
                        if org_name not in matched:
                            matched.append(org_name)

                abstract = _strip_html(entry.get("summary", ""))

                items.append(NewsItem(
                    title=_clean_text(entry.get("title", "")),
                    url=entry.get("id", entry.get("link", "")),
                    source="arXiv",
                    date=entry.get("published", datetime.now(timezone.utc).isoformat()),
                    language="en",
                    section="arxiv_top" if matched else "arxiv_other",
                    raw_content=f"Authors: {authors_str}\n\n{abstract}",
                    arxiv_id=arxiv_id,
                    organization=", ".join(matched) if matched else "",
                ))

            time.sleep(0.6)  # arXiv rate limit courtesy
        except Exception as exc:
            print(f"  [warn] arXiv {category}: {exc}", file=sys.stderr)

    return items


# ── Deduplication ───────────────────────────────────────────────────────────

def deduplicate(items):
    seen = set()
    unique = []
    for item in items:
        normalized = item.url.rstrip("/")
        h = hashlib.md5(normalized.encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(item)
    return unique


# ── Cache loading for weekly mode ────────────────────────────────────────────

def _load_cached_items(date_str, output_dir):
    """Load items from an existing YYYY-MM-DD-raw.json if it exists."""
    path = os.path.join(output_dir, f"{date_str}-raw.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        items = [NewsItem(**item) for item in data.get("items", [])]
        print(f"  [cache] {date_str}: loaded {len(items)} existing items",
              file=sys.stderr)
        return items
    except Exception as exc:
        print(f"  [warn] {date_str}: cache load failed: {exc}",
              file=sys.stderr)
        return None


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    socket.setdefaulttimeout(MAX_FETCH_TIMEOUT)

    parser = argparse.ArgumentParser(
        description="Collect daily AI/tech news from RSS, GitHub, HuggingFace, and arXiv."
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.expanduser("~/Desktop/news-digest"),
        help="Directory for raw JSON output (default: ~/Desktop/news-digest)",
    )
    parser.add_argument(
        "--hours", type=int, default=24,
        help="Hours to look back for RSS items (default: 24; ignored when --date is used)",
    )
    parser.add_argument(
        "--save-raw", action="store_true",
        help="Save raw JSON to output directory",
    )
    parser.add_argument(
        "--verify-links", action="store_true",
        help="Verify all item URLs with HEAD requests; remove dead links",
    )
    parser.add_argument(
        "--skip-focus", action="store_true",
        help="Skip focus topic detection",
    )
    parser.add_argument(
        "--date",
        help="Target date as YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--week", action="store_true",
        help="Fetch for the Mon-Sun calendar week containing --date. "
             "Reuses existing YYYY-MM-DD-raw.json files for days already fetched.",
    )
    args = parser.parse_args()

    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            parser.error("--date must be in YYYY-MM-DD format")
        print(f"Target date: {args.date}", file=sys.stderr)
    else:
        args.date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        print(f"Target date: {args.date} (today)", file=sys.stderr)

    all_items = []

    if args.week:
        target_dt = datetime.strptime(args.date, "%Y-%m-%d")
        monday = target_dt - timedelta(days=target_dt.weekday())
        iso_week = monday.isocalendar().week
        sunday = monday + timedelta(days=6)

        print(f"Weekly mode: Mon {monday.strftime('%Y-%m-%d')} to "
              f"Sun {sunday.strftime('%Y-%m-%d')} (W{iso_week})",
              file=sys.stderr)

        cached_days = 0
        fetched_days = 0
        for offset in range(7):
            day_date = (monday + timedelta(days=offset)).strftime("%Y-%m-%d")
            print(f"\n--- {day_date} ---", file=sys.stderr)

            cached = _load_cached_items(day_date, args.output_dir)
            if cached is not None:
                all_items.extend(cached)
                cached_days += 1
                continue

            fetched_days += 1
            rss_items = fetch_rss_feeds(RSS_FEEDS, args.hours, day_date)
            print(f"  RSS: {len(rss_items)} items", file=sys.stderr)
            all_items.extend(rss_items)

            gh_items = fetch_github_trending(day_date)
            print(f"  GitHub: {len(gh_items)} items", file=sys.stderr)
            all_items.extend(gh_items)

            hf_items = fetch_huggingface_trending(day_date)
            print(f"  HF: {len(hf_items)} items", file=sys.stderr)
            all_items.extend(hf_items)

            arxiv_items = fetch_arxiv(ARXIV_CATEGORIES, ARXIV_AFFILIATIONS,
                                       target_date=day_date)
            print(f"  arXiv: {len(arxiv_items)} items", file=sys.stderr)
            all_items.extend(arxiv_items)

        print(f"\nCached days: {cached_days}, "
              f"fetched days: {fetched_days}",
              file=sys.stderr)

        result_date = monday.strftime("%Y-%m-%d")
    else:
        # RSS
        print("Fetching RSS feeds ...", file=sys.stderr)
        rss_items = fetch_rss_feeds(RSS_FEEDS, args.hours, args.date)
        print(f"  {len(rss_items)} items", file=sys.stderr)
        all_items.extend(rss_items)

        # GitHub Trending
        print("Fetching GitHub Trending ...", file=sys.stderr)
        gh_items = fetch_github_trending(args.date)
        print(f"  {len(gh_items)} items", file=sys.stderr)
        all_items.extend(gh_items)

        # HuggingFace
        print("Fetching HuggingFace trending ...", file=sys.stderr)
        hf_items = fetch_huggingface_trending(args.date)
        print(f"  {len(hf_items)} items", file=sys.stderr)
        all_items.extend(hf_items)

        # arXiv
        print("Fetching arXiv papers ...", file=sys.stderr)
        arxiv_items = fetch_arxiv(ARXIV_CATEGORIES, ARXIV_AFFILIATIONS,
                                  target_date=args.date)
        print(f"  {len(arxiv_items)} items", file=sys.stderr)
        all_items.extend(arxiv_items)

        result_date = args.date

    # Deduplicate
    all_items = deduplicate(all_items)
    print(f"\nTotal after dedup: {len(all_items)} items", file=sys.stderr)

    # Focus topic detection
    if not args.skip_focus:
        print("Detecting focus topics ...", file=sys.stderr)
        detect_focus_topics(all_items)
        focused = sum(1 for i in all_items if i.focus_match)
        print(f"  {focused} items match focus topics", file=sys.stderr)

    # Link verification
    if args.verify_links:
        print(f"\nVerifying {len(all_items)} links ...", file=sys.stderr)
        all_items = verify_links(all_items)
        print(f"Total after link check: {len(all_items)} items", file=sys.stderr)

    # Compute stats
    sections = {}
    for item in all_items:
        sections[item.section] = sections.get(item.section, 0) + 1

    result = {
        "date": result_date,
        "items": [asdict(item) for item in all_items],
        "stats": {
            "total_items": len(all_items),
            "focus_matches": sum(1 for i in all_items if i.focus_match),
            **sections,
        },
    }
    if args.week:
        result["week_number"] = iso_week

    # Save raw if requested
    if args.save_raw:
        os.makedirs(args.output_dir, exist_ok=True)
        if args.week:
            raw_name = f"{result_date}-W{iso_week}-week-raw.json"
        else:
            raw_name = f"{args.date}-raw.json"
        raw_path = os.path.join(args.output_dir, raw_name)
        with open(raw_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Raw data saved → {raw_path}", file=sys.stderr)

    # Output JSON to stdout
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
