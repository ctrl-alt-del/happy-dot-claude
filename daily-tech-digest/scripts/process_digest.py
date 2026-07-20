#!/usr/bin/env python3
"""
process_digest.py — Pre-process raw digest JSON: filter, rank, cap, group into
sections, and extract keyword hints. Produces a semi-processed JSON that the
agent only needs to add translations, summaries, and finalize keywords for.

Usage:
    python3 process_digest.py raw.json                    # → stdout
    python3 process_digest.py raw.json -o semi.json       # save to file
    python3 process_digest.py raw.json --cap 40           # override item cap
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from collections import Counter

# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_CAP = 40
WEEKLY_CAP = 45
MAX_HIGHLIGHTS = 10

# ── Content filter: skip lists ──────────────────────────────────────────────

SKIP_KEYWORDS = [
    "bitcoin", "ethereum", "cryptocurrency", "crypto coin", "altcoin",
    "defi", "decentralized finance", "nft", "non-fungible token",
    "token sale", "ico", "initial coin offering", "memecoin", "dogecoin",
    "shitcoin", "yield farming", "liquidity pool", "web3 fundraising",
    "crypto exchange", "crypto wallet",
]

SKIP_TITLE_PATTERNS = [
    re.compile(r"\bcrypto\b", re.I),
    re.compile(r"\bnft\b", re.I),
    re.compile(r"\bdefi\b", re.I),
    re.compile(r"\btoken\b.*\b(?:price|surge|crash|rally|dump|pump)\b", re.I),
    re.compile(r"\b(?:bitcoin|ethereum|solana|cardano|ripple|xrp|dogecoin)\b.*\b(?:price|surge|crash)\b", re.I),
]

# Keywords that indicate blockchain used for non-speculation purposes — keep these
KEEP_BLOCKCHAIN = [
    "supply chain", "enterprise", "identity", "infrastructure",
    "blockchain supply", "blockchain identity",
]

# ── Keyword extraction ──────────────────────────────────────────────────────

KEYWORD_PATTERNS = {
    "ai-ml": [
        (re.compile(r"\bGPT\b", re.I), "GPT"),
        (re.compile(r"\bClaude\b", re.I), "Claude"),
        (re.compile(r"\bGemini\b", re.I), "Gemini"),
        (re.compile(r"\bLlama\b", re.I), "Llama"),
        (re.compile(r"\bDeepSeek\b", re.I), "DeepSeek"),
        (re.compile(r"\bQwen\b", re.I), "Qwen"),
        (re.compile(r"\bLLaMA\b", re.I), "LLaMA"),
        (re.compile(r"\bLLM\b", re.I), "LLM"),
        (re.compile(r"\btransformer\b", re.I), "transformer"),
        (re.compile(r"\bdiffusion\b", re.I), "diffusion"),
        (re.compile(r"\breinforcement learning\b", re.I), "RL"),
        (re.compile(r"\bfoundation model\b", re.I), "foundation-model"),
        (re.compile(r"\bneural network\b", re.I), "neural-net"),
        (re.compile(r"\bdeep learning\b", re.I), "deep-learning"),
        (re.compile(r"\bChatGPT\b", re.I), "ChatGPT"),
        (re.compile(r"\bcopilot\b", re.I), "copilot"),
        (re.compile(r"人工智能", re.I), "人工智能"),
        (re.compile(r"大模型", re.I), "大模型"),
        (re.compile(r"深度学习", re.I), "深度学习"),
        (re.compile(r"大语言模型", re.I), "大语言模型"),
        (re.compile(r"生成式.?AI", re.I), "生成式AI"),
        (re.compile(r"预训练", re.I), "预训练"),
        (re.compile(r"强化学习", re.I), "强化学习"),
        (re.compile(r"多模态", re.I), "多模态"),
        (re.compile(r"推理模型", re.I), "推理模型"),
        (re.compile(r"AI智能体", re.I), "AI智能体"),
        (re.compile(r"Agent", re.I), "Agent"),
    ],
    "hardware": [
        (re.compile(r"\bchip\b", re.I), "chip"),
        (re.compile(r"\bEDA\b", re.I), "EDA"),
        (re.compile(r"\bsemiconductor\b", re.I), "semiconductor"),
        (re.compile(r"\bHBM\d?\b", re.I), "HBM"),
        (re.compile(r"\bDRAM\b", re.I), "DRAM"),
        (re.compile(r"\bNAND\b", re.I), "NAND"),
        (re.compile(r"\bTSMC\b", re.I), "TSMC"),
        (re.compile(r"\bSamsung\b", re.I), "Samsung"),
        (re.compile(r"\bIntel\b", re.I), "Intel"),
        (re.compile(r"\bNVIDIA\b", re.I), "NVIDIA"),
        (re.compile(r"\bGPU\b", re.I), "GPU"),
        (re.compile(r"\b3nm\b", re.I), "3nm"),
        (re.compile(r"\b5nm\b", re.I), "5nm"),
        (re.compile(r"\bwafer\b", re.I), "wafer"),
        (re.compile(r"\bfab\b", re.I), "fab"),
        (re.compile(r"\bfoundry\b", re.I), "foundry"),
        (re.compile(r"芯片", re.I), "芯片"),
        (re.compile(r"半导体", re.I), "半导体"),
        (re.compile(r"存储芯片", re.I), "存储芯片"),
        (re.compile(r"晶圆", re.I), "晶圆"),
        (re.compile(r"封装", re.I), "封装"),
        (re.compile(r"光刻", re.I), "光刻"),
        (re.compile(r"制程", re.I), "制程"),
        (re.compile(r"英伟达", re.I), "英伟达"),
        (re.compile(r"海力士", re.I), "SK海力士"),
        (re.compile(r"三星电子", re.I), "三星"),
    ],
    "robotics": [
        (re.compile(r"\brobot\b", re.I), "robot"),
        (re.compile(r"\bhumanoid\b", re.I), "humanoid"),
        (re.compile(r"\bembodied\b", re.I), "embodied"),
        (re.compile(r"\bautonomous\b", re.I), "autonomous"),
        (re.compile(r"\bmanipulation\b", re.I), "manipulation"),
        (re.compile(r"机器人", re.I), "机器人"),
        (re.compile(r"具身智能", re.I), "具身智能"),
        (re.compile(r"自动驾驶", re.I), "自动驾驶"),
        (re.compile(r"人形机器人", re.I), "人形机器人"),
        (re.compile(r"无人驾驶", re.I), "无人驾驶"),
        (re.compile(r"智能驾驶", re.I), "智能驾驶"),
    ],
    "software": [
        (re.compile(r"\bopen.source\b", re.I), "open-source"),
        (re.compile(r"\bGitHub\b", re.I), "GitHub"),
        (re.compile(r"\bAPI\b", re.I), "API"),
        (re.compile(r"\bbenchmark\b", re.I), "benchmark"),
        (re.compile(r"\bframework\b", re.I), "framework"),
        (re.compile(r"\bcompiler\b", re.I), "compiler"),
        (re.compile(r"\bPython\b", re.I), "Python"),
        (re.compile(r"\bRust\b", re.I), "Rust"),
        (re.compile(r"\bTypeScript\b", re.I), "TypeScript"),
        (re.compile(r"\bDocker\b", re.I), "Docker"),
        (re.compile(r"\bKubernetes\b", re.I), "Kubernetes"),
        (re.compile(r"开源", re.I), "开源"),
        (re.compile(r"框架", re.I), "框架"),
        (re.compile(r"工具", re.I), "工具"),
        (re.compile(r"平台", re.I), "平台"),
        (re.compile(r"开发者", re.I), "开发者"),
    ],
    "org-product": [
        (re.compile(r"\bOpenAI\b", re.I), "OpenAI"),
        (re.compile(r"\bAnthropic\b", re.I), "Anthropic"),
        (re.compile(r"\bGoogle\b", re.I), "Google"),
        (re.compile(r"\bMicrosoft\b", re.I), "Microsoft"),
        (re.compile(r"\bMeta\b", re.I), "Meta"),
        (re.compile(r"\bApple\b", re.I), "Apple"),
        (re.compile(r"\bAmazon\b", re.I), "Amazon"),
        (re.compile(r"\bTesla\b", re.I), "Tesla"),
        (re.compile(r"\bByteDance\b", re.I), "ByteDance"),
        (re.compile(r"\bAlibaba\b", re.I), "Alibaba"),
        (re.compile(r"\bTencent\b", re.I), "Tencent"),
        (re.compile(r"\bBaidu\b", re.I), "Baidu"),
        (re.compile(r"\bxAI\b", re.I), "xAI"),
        (re.compile(r"\bMistral\b", re.I), "Mistral"),
        (re.compile(r"\bDeepMind\b", re.I), "DeepMind"),
        (re.compile(r"\bSpaceX\b", re.I), "SpaceX"),
        (re.compile(r"阿里云", re.I), "阿里云"),
        (re.compile(r"阿里巴巴", re.I), "阿里巴巴"),
        (re.compile(r"腾讯", re.I), "腾讯"),
        (re.compile(r"百度", re.I), "百度"),
        (re.compile(r"字节跳动", re.I), "字节跳动"),
        (re.compile(r"华为", re.I), "华为"),
        (re.compile(r"小米", re.I), "小米"),
        (re.compile(r"特斯拉", re.I), "特斯拉"),
        (re.compile(r"OpenAI", re.I), "OpenAI"),
        (re.compile(r"DeepSeek|深度求索", re.I), "DeepSeek"),
        (re.compile(r"智谱", re.I), "智谱AI"),
        (re.compile(r"月之暗面", re.I), "月之暗面"),
        (re.compile(r"Kimi", re.I), "Kimi"),
        (re.compile(r"百度文心", re.I), "文心一言"),
        (re.compile(r"字节豆包", re.I), "豆包"),
    ],
    "safety": [
        (re.compile(r"\bregulation\b", re.I), "regulation"),
        (re.compile(r"\bpolicy\b", re.I), "policy"),
        (re.compile(r"\bban\b", re.I), "ban"),
        (re.compile(r"\bdata breach\b", re.I), "data-breach"),
        (re.compile(r"\balignment\b", re.I), "alignment"),
        (re.compile(r"\bred.teaming\b", re.I), "red-teaming"),
        (re.compile(r"\bsafety\b", re.I), "safety"),
        (re.compile(r"\bprivacy\b", re.I), "privacy"),
        (re.compile(r"监管", re.I), "监管"),
        (re.compile(r"合规", re.I), "合规"),
        (re.compile(r"安全", re.I), "安全"),
        (re.compile(r"隐私", re.I), "隐私"),
        (re.compile(r"政策", re.I), "政策"),
        (re.compile(r"法规", re.I), "法规"),
    ],
}


def extract_keywords(item):
    """Extract keyword hints from an item's title and raw_content."""
    text = f"{item.get('title', '')} {item.get('raw_content', '')}"
    found = []
    seen = set()
    for domain, patterns in KEYWORD_PATTERNS.items():
        for pat, label in patterns:
            if pat.search(text) and label not in seen:
                found.append({"text": label, "domain": domain})
                seen.add(label)
    return found[:5]


# ── Content filtering ───────────────────────────────────────────────────────

def _is_crypto_item(item):
    """Returns True if the item is primarily about crypto speculation."""
    title = (item.get("title", "") or "").lower()
    content = (item.get("raw_content", "") or "").lower()
    combined = f"{title} {content}"

    for keep_kw in KEEP_BLOCKCHAIN:
        if keep_kw in combined:
            return False

    for pat in SKIP_TITLE_PATTERNS:
        if pat.search(title):
            return True

    kw_count = sum(1 for kw in SKIP_KEYWORDS if kw in combined)
    return kw_count >= 2


def filter_items(items):
    """Remove crypto/NFT/DeFi speculation items. Returns filtered list."""
    kept = []
    removed = 0
    for item in items:
        if _is_crypto_item(item):
            removed += 1
            continue
        kept.append(item)
    if removed:
        print(f"  filtered: {removed} crypto/NFT items removed", file=sys.stderr)
    return kept


# ── Ranking ──────────────────────────────────────────────────────────────────

def rank_items(items):
    """Sort items by priority_hint descending, then date recency."""
    def sort_key(item):
        hint = item.get("priority_hint", 0)
        date_str = item.get("date", "")
        return (-hint, date_str)
    return sorted(items, key=sort_key)


# ── Highlight detection ──────────────────────────────────────────────────────

HIGHLIGHT_PATTERNS = [
    (re.compile(r"\breleas[ei]d?\b", re.I), 50),
    (re.compile(r"\blaunch[ei]d?\b", re.I), 50),
    (re.compile(r"\bGPT-?\d\b", re.I), 80),
    (re.compile(r"\bClaude\s*\d", re.I), 80),
    (re.compile(r"\bGemini\s*\d", re.I), 70),
    (re.compile(r"\bDeepSeek\b", re.I), 70),
    (re.compile(r"\bLlama\s*\d", re.I), 60),
    (re.compile(r"\bQwen\s*\d", re.I), 60),
    (re.compile(r"\b(?:acquisition|acquires|acquired)\b", re.I), 60),
    (re.compile(r"\b\$?\d+\.?\d*\s*[BM]illion\b", re.I), 50),
    (re.compile(r"\b\$?\d+\.?\d*\s*[B]illion\b", re.I), 70),
    (re.compile(r"\bIPO\b", re.I), 60),
    (re.compile(r"\b(?:ban|banned|regulation|regulate)\b", re.I), 40),
    (re.compile(r"\b(?:safety|breach|scandal|controversy)\b", re.I), 40),
    (re.compile(r"\brecord\b", re.I), 30),
    (re.compile(r"\bSOTA\b", re.I), 40),
    (re.compile(r"\bstate.of.the.art\b", re.I), 40),
    (re.compile(r"\b100\s*million\b", re.I), 30),
    (re.compile(r"\bopen\s*source\b.*\b(?:release|launch)\b", re.I), 30),
]


def detect_highlights(items, max_hl=MAX_HIGHLIGHTS):
    """Score items for highlight significance. Returns items with
    is_highlight flag set. Modifies in place."""
    for item in items:
        text = f"{item.get('title', '')} {item.get('raw_content', '')}"
        score = item.get("priority_hint", 0)
        for pat, boost in HIGHLIGHT_PATTERNS:
            if pat.search(text):
                score += boost
        item["_hl_score"] = score

    sorted_by_hl = sorted(items, key=lambda i: i.get("_hl_score", 0), reverse=True)
    for i, item in enumerate(sorted_by_hl):
        if i < max_hl and item.get("_hl_score", 0) >= 40:
            item["is_highlight"] = True
        else:
            item["is_highlight"] = False

    hl_count = sum(1 for i in items if i.get("is_highlight"))
    print(f"  highlights: {hl_count} candidates", file=sys.stderr)
    return items


# ── Section grouping ─────────────────────────────────────────────────────────

SECTION_ORDER = [
    ("highlights", "! Highlights"),
    ("us_news", "Silicon Valley & US News"),
    ("china_news", "China Tech News"),
    ("github_trending", "GitHub Trending"),
    ("hf_trending", "HuggingFace Trending"),
    ("arxiv_top", "arXiv — Top Institution Papers"),
    ("arxiv_other", "arXiv — Other Notable Papers"),
]

SECTION_LABELS = dict(SECTION_ORDER)


def group_into_sections(items, is_weekly=False):
    """Group items into sections and cap at max items."""
    cap = WEEKLY_CAP if is_weekly else DEFAULT_CAP
    items = items[:cap]

    sections_map = {}
    for item in items:
        sec = item.get("section", "us_news")
        if sec not in sections_map:
            sections_map[sec] = []
        sections_map[sec].append(item)

    sections_out = []
    for sec_id, label in SECTION_ORDER:
        items_in_sec = sections_map.get(sec_id, [])
        if not items_in_sec:
            continue
        sections_out.append({
            "id": sec_id,
            "label": label,
            "items": items_in_sec,
        })

    # Handle highlights: gather items with is_highlight and put them first
    hl_items = [i for i in items if i.get("is_highlight")]
    if hl_items:
        hl_section = {
            "id": "highlights",
            "label": "! Highlights",
            "items": hl_items,
        }
        # Check if highlights already exists
        existing_hl_idx = None
        for idx, sec in enumerate(sections_out):
            if sec["id"] == "highlights":
                existing_hl_idx = idx
                break
        if existing_hl_idx is not None:
            sections_out[existing_hl_idx] = hl_section
        else:
            sections_out.insert(0, hl_section)

    return sections_out, items


# ── Daily keyword synthesis ──────────────────────────────────────────────────

def synthesize_daily_keywords(items, count=10):
    """Generate daily keyword candidates from all items' extracted keywords.
    Falls back to focus_match domains if no keywords were extracted."""
    domain_counts = Counter()
    text_counts = Counter()

    for item in items:
        for kw in item.get("_keywords", []):
            text_counts[kw["text"]] += 1
            domain_counts[kw["domain"]] += 1

    if not text_counts:
        return _fallback_daily_keywords(items, count)

    candidates = []
    seen_texts = set()
    for text, cnt in text_counts.most_common(20):
        if text.lower() in seen_texts:
            continue
        seen_texts.add(text.lower())
        domain = "other"
        for item in items:
            for kw in item.get("_keywords", []):
                if kw["text"] == text:
                    domain = kw["domain"]
                    break
            if domain != "other":
                break
        candidates.append({"text": text, "domain": domain})

    result = []
    domains_covered = set()
    for c in candidates:
        if len(result) >= count:
            break
        if c["domain"] not in domains_covered or len(result) >= count - 2:
            result.append(c)
            domains_covered.add(c["domain"])

    return result[:count]


def _fallback_daily_keywords(items, count=10):
    """Generate daily keywords from focus_match domains and section distribution."""
    focus_domains = Counter()
    sections = Counter()

    for item in items:
        for fm in item.get("focus_match", []):
            focus_domains[fm] += 1
        sections[item.get("section", "other")] += 1

    domain_labels = {
        "embodied-ai": ("embodied-ai", "robotics"),
        "chip-eda": ("chip-eda", "hardware"),
        "robotics": ("robotics", "robotics"),
        "ai-ml": ("AI/ML", "ai-ml"),
        "memory-chips": ("memory-chips", "hardware"),
        "semiconductor": ("semiconductor", "hardware"),
    }

    result = []
    for domain_id, count in focus_domains.most_common(count):
        label, domain = domain_labels.get(domain_id, (domain_id, "other"))
        result.append({"text": label, "domain": domain})

    if len(result) < 3:
        sec_labels = {
            "china_news": "China-Tech",
            "us_news": "US-Tech",
            "github_trending": "GitHub",
            "hf_trending": "HuggingFace",
            "arxiv_top": "arXiv",
        }
        for sec_id, cnt in sections.most_common(count - len(result)):
            label = sec_labels.get(sec_id, sec_id)
            result.append({"text": label, "domain": "other"})

    return result[:count]


# ── Source collection ────────────────────────────────────────────────────────

def collect_sources(items):
    """Extract unique sources from items."""
    seen = set()
    sources = []
    for item in items:
        name = item.get("source", "")
        if name and name not in seen:
            seen.add(name)
            sources.append({
                "name": name,
                "url": _source_url(name),
            })
    return sources


def _source_url(name):
    """Map source name to homepage URL."""
    mapping = {
        "Hacker News": "https://news.ycombinator.com",
        "TechCrunch": "https://techcrunch.com",
        "The Verge": "https://www.theverge.com",
        "Ars Technica": "https://arstechnica.com",
        "MIT Tech Review": "https://www.technologyreview.com",
        "9to5Mac": "https://9to5mac.com",
        "9to5Google": "https://9to5google.com",
        "Electrek": "https://electrek.co",
        "SpaceNews": "https://spacenews.com",
        "TechNode": "https://technode.com",
        "SCMP Tech": "https://www.scmp.com/tech",
        "Pandaily": "https://pandaily.com",
        "36kr": "https://36kr.com",
        "Huxiu": "https://www.huxiu.com",
        "GitHub Trending": "https://github.com/trending",
        "HuggingFace": "https://huggingface.co",
        "arXiv": "https://arxiv.org",
    }
    return mapping.get(name, "")


# ── Stats ────────────────────────────────────────────────────────────────────

def compute_stats(items, sections):
    """Compute stats for the processed output."""
    section_counts = {}
    for sec in sections:
        section_counts[sec["id"]] = len(sec["items"])

    sources = set()
    verified = 0
    failed = 0
    for item in items:
        s = item.get("source", "")
        if s:
            sources.add(s)
        if item.get("link_verified"):
            verified += 1
        else:
            failed += 1

    return {
        "total_items": len(items),
        "sources_count": len(sources),
        "links_verified_count": verified,
        "links_failed_count": failed,
        "section_counts": section_counts,
    }


# ── Section-aware cap distribution ───────────────────────────────────────────

SECTION_MINS = {
    "us_news": 5,
    "china_news": 5,
    "github_trending": 3,
    "hf_trending": 3,
    "arxiv_top": 2,
    "arxiv_other": 2,
}
SECTION_MINS_TOTAL = sum(SECTION_MINS.values())  # 20 baseline


def distribute_cap(items_by_section, cap):
    """Distribute `cap` slots across sections with minimum guarantees.
    Returns dict of section_id -> list of allocated items."""
    total_available = sum(len(v) for v in items_by_section.values())
    if total_available <= cap:
        return items_by_section  # everything fits

    allocation = {}
    # Step 1: assign minimums
    remaining = cap
    for sec_id, sec_items in items_by_section.items():
        min_items = SECTION_MINS.get(sec_id, 0)
        take = min(min_items, len(sec_items))
        allocation[sec_id] = sec_items[:take]
        remaining -= take

    if remaining <= 0:
        return allocation

    # Step 2: distribute remaining slots proportionally
    eligible = {}
    for sec_id, sec_items in items_by_section.items():
        already = len(allocation.get(sec_id, []))
        leftover = sec_items[already:]
        if leftover:
            eligible[sec_id] = leftover

    if not eligible:
        return allocation

    total_eligible = sum(len(v) for v in eligible.values())
    for sec_id, leftover in eligible.items():
        proportion = len(leftover) / total_eligible
        take = min(int(round(proportion * remaining)), len(leftover))
        allocation.setdefault(sec_id, [])
        allocation[sec_id].extend(leftover[:take])

    # Step 3: fill any remaining slots with highest-priority items across sections
    used = sum(len(v) for v in allocation.values())
    while used < cap:
        best_sec = None
        best_item = None
        best_priority = -1
        for sec_id, sec_items in items_by_section.items():
            already = len(allocation.get(sec_id, []))
            if already < len(sec_items):
                candidate = sec_items[already]
                pri = candidate.get("priority_hint", 0)
                if pri > best_priority:
                    best_priority = pri
                    best_sec = sec_id
                    best_item = candidate
        if best_sec is None:
            break
        allocation.setdefault(best_sec, [])
        allocation[best_sec].append(best_item)
        used += 1

    return allocation


# ── Main pipeline ────────────────────────────────────────────────────────────

def process(raw_data, cap=None, is_weekly=None):
    """Full pipeline: filter → rank within sections → cap with mins → highlights →
    sections → daily kw."""
    date_str = raw_data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    week_number = raw_data.get("week_number")
    if is_weekly is None:
        is_weekly = bool(week_number)

    items = raw_data.get("items", [])
    max_items = cap or (WEEKLY_CAP if is_weekly else DEFAULT_CAP)

    print(f"Raw items: {len(items)}", file=sys.stderr)

    items = filter_items(items)

    # Group by section, then rank within each section
    items_by_section = {}
    for item in items:
        sec = item.get("section", "us_news")
        items_by_section.setdefault(sec, []).append(item)

    for sec_id in items_by_section:
        items_by_section[sec_id] = rank_items(items_by_section[sec_id])

    # Distribute cap across sections with minimums
    allocation = distribute_cap(items_by_section, max_items)
    items = []
    for sec_id in sorted(allocation.keys()):
        items.extend(allocation[sec_id])

    print(f"Processing {len(items)} items (cap={max_items})", file=sys.stderr)
    for sec_id, sec_items in sorted(allocation.items()):
        print(f"  {sec_id}: {len(sec_items)} items", file=sys.stderr)

    for item in items:
        item["_keywords"] = extract_keywords(item)
        item.setdefault("title_zh", "")
        item.setdefault("summary", "")
        item.setdefault("keywords", item["_keywords"])
        item.setdefault("is_highlight", False)

    items = detect_highlights(items)
    sections, items = group_into_sections(items, is_weekly)
    daily_keywords = synthesize_daily_keywords(items)
    sources = collect_sources(items)
    stats = compute_stats(items, sections)

    output = {
        "date": date_str,
        "stats": stats,
        "daily_keywords": daily_keywords,
        "sections": sections,
        "sources": sources,
    }
    if week_number:
        output["week_number"] = week_number

    for item in items:
        item.pop("_keywords", None)
        item.pop("_hl_score", None)

    return output


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Pre-process raw digest JSON: filter, rank, cap, group into sections."
    )
    parser.add_argument("input", help="Path to raw JSON from fetch_digest.py")
    parser.add_argument("-o", "--output", help="Output JSON file path")
    parser.add_argument("--cap", type=int, help="Override item cap (default: 40 daily, 45 weekly)")
    parser.add_argument("--weekly", action="store_true", help="Use weekly cap (45 items)")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    processed = process(raw_data, cap=args.cap, is_weekly=args.weekly)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(processed, f, indent=2, ensure_ascii=False)
        print(f"Semi-processed JSON → {args.output}", file=sys.stderr)
    else:
        print(json.dumps(processed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
