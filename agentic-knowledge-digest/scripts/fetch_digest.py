#!/usr/bin/env python3
"""
fetch_digest.py — Collect daily AI/agentic knowledge news from RSS feeds,
research blogs, community blogs, GitHub Trending, HuggingFace, and arXiv.
Outputs structured JSON for the agent to summarize and format into
~/Desktop/agentic-knowledge-digest/YYYY-MM-DD.html

Usage:
    python3 fetch_digest.py                              # JSON to stdout
    python3 fetch_digest.py --save-raw                   # also save raw JSON
    python3 fetch_digest.py --verify-links               # verify all URLs
    python3 fetch_digest.py --output-dir ~/custom        # custom output dir
    python3 fetch_digest.py --hours 48                   # look back 48h
    python3 fetch_digest.py --date 2026-07-01            # specific date
"""

import argparse
import hashlib
import json
import os
import re
import socket
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

MAX_FETCH_TIMEOUT = 180


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


# ── Focus topic detection ──────────────────────────────────────────────────

FOCUS_TOPICS = {
    "rag-retrieval": {
        "keywords": [
            "RAG", "retrieval augmented", "retrieval-augmented",
            "retrieval augmented generation", "dense retrieval",
            "sparse retrieval", "hybrid retrieval", "hybrid search",
            "document retrieval", "information retrieval", "passage retrieval",
            "reranking", "re-ranking", "retriever", "cross-encoder",
            "bi-encoder", "late interaction", "colbert", "splade",
            "multi-hop retrieval", "iterative retrieval", "self-RAG",
            "corrective RAG", "CRAG", "adaptive RAG", "agentic RAG",
            "modular RAG", "检索增强",
        ],
        "priority_boost": 10,
    },
    "agent-memory": {
        "keywords": [
            "agent memory", "long-term memory", "short-term memory",
            "working memory", "episodic memory", "semantic memory",
            "procedural memory", "context window", "context management",
            "memory consolidation", "memory retrieval", "memory store",
            "memgpt", "MemGPT", "mem0", "Mem0", "letta", "letta agent",
            "memory bank", "memory stream", "reflection memory",
            "记忆系统", "智能体记忆",
        ],
        "priority_boost": 9,
    },
    "knowledge-graph": {
        "keywords": [
            "knowledge graph", "GraphRAG", "graph RAG", "graph-based RAG",
            "graph retrieval", "Neo4j", "neo4j", "Cypher", "cypher",
            "SPARQL", "sparql", "Graphify", "graphify", "Graphitti",
            "graphitti", "property graph", "RDF", "triple store",
            "graph database", "GNN", "graph neural network",
            "entity linking", "entity resolution", "community detection",
            "Leiden algorithm", "hierarchical graph", "ontology",
            "knowledge representation", "知识图谱", "图数据库",
        ],
        "priority_boost": 8,
    },
    "knowledge-lifecycle": {
        "keywords": [
            "knowledge lifecycle", "knowledge management", "knowledge base",
            "knowledge evolution", "knowledge consolidation",
            "knowledge versioning", "knowledge decay", "knowledge pruning",
            "knowledge forgetting", "knowledge curation",
            "knowledge validation", "knowledge conflict", "stale knowledge",
            "outdated knowledge", "LLM-wiki", "LLM wiki", "LLM-wiki v2",
            "Code Wiki", "code wiki", "wiki-style knowledge",
            "knowledge update", "knowledge refresh", "incremental knowledge",
            "knowledge sync", "知识生命周期", "知识管理", "知识库", "知识演化",
        ],
        "priority_boost": 7,
    },
    "agent-architecture": {
        "keywords": [
            "agent framework", "multi-agent", "multi agent",
            "agent orchestration", "tool use", "function calling",
            "tool calling", "autonomous agent", "LLM agent", "agentic",
            "agentic workflow", "agent design", "agent architecture",
            "delegation", "agent communication", "crewAI", "AutoGen",
            "LangGraph", "semantic kernel", "agent protocol", "MCP",
            "model context protocol", "A2A", "agent-to-agent",
            "agent swarm", "hierarchical agent", "智能体架构", "多智能体",
            "工具调用",
        ],
        "priority_boost": 6,
    },
    "embeddings-vectors": {
        "keywords": [
            "embedding model", "text embedding", "dense embedding",
            "sparse embedding", "vector database", "vector store",
            "vector search", "semantic search", "similarity search",
            "ANN search", "approximate nearest neighbor", "faiss",
            "chroma", "pinecone", "weaviate", "milvus", "qdrant",
            "MTEB", "embedding benchmark", "embedding fine-tuning",
            "Matryoshka", "binary embedding", "quantization embedding",
            "嵌入模型", "向量数据库",
        ],
        "priority_boost": 5,
    },
    "ai-knowledge": {
        "keywords": [
            "knowledge distillation", "continual learning", "lifelong learning",
            "fine-tuning", "instruction tuning", "supervised fine-tuning",
            "SFT", "preference optimization", "RLHF", "DPO",
            "training data", "data curation", "data synthesis",
            "synthetic data", "knowledge transfer", "model merging",
            "model distillation", "teacher-student", "知识蒸馏", "持续学习",
            "微调",
        ],
        "priority_boost": 4,
    },
    "cognition-reasoning": {
        "keywords": [
            "chain-of-thought", "chain of thought", "CoT",
            "tree-of-thought", "tree of thought", "ToT",
            "graph-of-thought", "planning", "reasoning",
            "logical reasoning", "multi-step reasoning",
            "self-reflection", "self-critique", "self-consistency",
            "verification", "deliberation", "scratchpad",
            "inner monologue", "ReAct", "reflection agent", "critic",
            "思维链", "推理", "规划",
        ],
        "priority_boost": 3,
    },
    "context-prompting": {
        "keywords": [
            "prompt engineering", "prompt optimization",
            "prompt compression", "prompt design", "in-context learning",
            "ICL", "few-shot", "zero-shot", "long context",
            "context length", "context extension", "context window",
            "prompt tuning", "soft prompt", "hard prompt",
            "automatic prompt", "DSPy", "prompt chaining", "提示工程",
            "上下文学习",
        ],
        "priority_boost": 2,
    },
    "evaluation-benchmark": {
        "keywords": [
            "benchmark", "evaluation", "eval", "agent benchmark",
            "retrieval benchmark", "RAG benchmark",
            "knowledge benchmark", "knowledge graph benchmark",
            "BEIR", "MTEB", "MMLU", "AGIEval", "agent evaluation",
            "task completion", "success rate", "NDCG", "MRR",
            "HITS@K", "基准测试", "评估",
        ],
        "priority_boost": 1,
    },
}


def detect_focus_topics(items):
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


# ── Link verification ──────────────────────────────────────────────────────

def verify_links(items):
    ok = []
    total = len(items)
    failed = 0
    for i, item in enumerate(items):
        try:
            resp = requests.head(item.url, timeout=10, allow_redirects=True,
                                headers={"User-Agent": "agentic-knowledge-digest/1.0"})
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
    {"url": "https://hnrss.org/frontpage?count=20", "name": "Hacker News",
     "section": "blogs_insights", "language": "en"},
    {"url": "https://www.technologyreview.com/feed/", "name": "MIT Tech Review",
     "section": "blogs_insights", "language": "en"},
]

RSS_KEYWORD_FILTER = [
    "agent", "RAG", "rag ", "retrieval", "knowledge", "graph",
    "embedding", "vector", "LLM", "reasoning", "tool-use", "tool use",
    "function-calling", "multi-agent", "ontology", "wiki",
    "Neo4j", "lifecycle", "prompt", "fine-tun", "benchmark",
    "chain-of-thought", "in-context", "memory",
]


def _rss_matches_knowledge(title, content):
    text = f"{title} {content}".lower()
    return any(kw.lower() in text for kw in RSS_KEYWORD_FILTER)


def fetch_rss_feeds(feeds, hours=24, target_date=None):
    items = []
    if target_date:
        target_dt = datetime.strptime(target_date, "%Y-%m-%d").replace(
            tzinfo=timezone.utc)
        cutoff_start = target_dt
        cutoff_end = target_dt + timedelta(days=1)
    else:
        cutoff_start = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_end = None

    for cfg in feeds:
        try:
            resp = requests.get(
                cfg["url"],
                timeout=MAX_FETCH_TIMEOUT,
                headers={"User-Agent": "agentic-knowledge-digest/1.0"},
            )
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            for entry in feed.entries:
                pub_date = _parse_entry_date(entry)
                if target_date and cutoff_end:
                    if not pub_date or pub_date < cutoff_start or pub_date >= cutoff_end:
                        continue
                elif pub_date and pub_date < cutoff_start:
                    continue

                title = _clean_text(entry.get("title", ""))
                content = ""
                if hasattr(entry, "summary"):
                    content = entry.summary
                elif hasattr(entry, "content") and entry.content:
                    content = entry.content[0].get("value", "")
                elif hasattr(entry, "description"):
                    content = entry.description
                content = _strip_html(content)

                if not _rss_matches_knowledge(title, content):
                    continue

                items.append(NewsItem(
                    title=title,
                    url=entry.get("link", ""),
                    source=cfg["name"],
                    date=pub_date.isoformat() if pub_date else (
                        target_dt.isoformat() if target_date
                        else datetime.now(timezone.utc).isoformat()),
                    language=cfg["language"],
                    section=cfg["section"],
                    raw_content=content,
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
        return BeautifulSoup(text, "html.parser").get_text(
            separator=" ", strip=True)
    except Exception:
        return text


def _clean_text(text):
    return text.strip().replace("\n", " ").replace("\r", "")


# ── Blog scraping ───────────────────────────────────────────────────────────

BLOG_SCRAPERS = [
    # AI Research Labs
    {
        "name": "Anthropic Research",
        "url": "https://www.anthropic.com/research",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", "a[href*='/research/']"],
        "link_prefix": "https://www.anthropic.com",
        "date_attr": None,
    },
    {
        "name": "OpenAI Research",
        "url": "https://openai.com/research/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["a[href*='/research/']", "article"],
        "link_prefix": "",
        "date_attr": None,
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/discover/blog/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", "a[href*='/blog/']"],
        "link_prefix": "https://deepmind.google",
        "date_attr": None,
    },
    {
        "name": "Meta AI Blog",
        "url": "https://ai.meta.com/blog/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", "a[href*='/blog/']"],
        "link_prefix": "",
        "date_attr": None,
    },
    {
        "name": "Microsoft Research",
        "url": "https://www.microsoft.com/en-us/research/blog/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", "a.entry-title"],
        "link_prefix": "",
        "date_attr": None,
    },
    {
        "name": "BAIR",
        "url": "https://bair.berkeley.edu/blog/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", ".post"],
        "link_prefix": "",
        "date_attr": None,
    },
    {
        "name": "Stanford AI Lab",
        "url": "https://ai.stanford.edu/blog/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", ".post"],
        "link_prefix": "",
        "date_attr": None,
    },
    # Agent & Knowledge Community
    {
        "name": "LangChain Blog",
        "url": "https://blog.langchain.dev/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", ".post-card", "a[href*='/20']"],
        "link_prefix": "",
        "date_attr": None,
    },
    {
        "name": "LlamaIndex Blog",
        "url": "https://www.llamaindex.ai/blog",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", "a[href*='/blog/']"],
        "link_prefix": "",
        "date_attr": None,
    },
    {
        "name": "The Gradient",
        "url": "https://thegradient.pub/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": ["article", ".post"],
        "link_prefix": "",
        "date_attr": None,
    },
    {
        "name": "Lilian Weng's Blog",
        "url": "https://lilianweng.github.io/",
        "section": "blogs_insights",
        "language": "en",
        "selectors": [".post-link", "a[href*='/posts/']"],
        "link_prefix": "",
        "date_attr": None,
    },
]

DATE_PATTERNS = [
    re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})"),
    re.compile(r"(\w+)\s+(\d{1,2}),?\s*(\d{4})"),
]


def _parse_blog_date(text):
    for pattern in DATE_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                if m.lastindex == 3 and m.group(1).isdigit():
                    return datetime(
                        int(m.group(1)), int(m.group(2)), int(m.group(3)),
                        tzinfo=timezone.utc)
                else:
                    mn = {
                        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
                        "may": 5, "jun": 6, "jul": 7, "aug": 8,
                        "sep": 9, "oct": 10, "nov": 11, "dec": 12,
                    }
                    month = mn.get(m.group(1).lower()[:3], 1)
                    day = int(m.group(2))
                    year = int(m.group(3))
                    return datetime(year, month, day, tzinfo=timezone.utc)
            except (ValueError, KeyError):
                continue
    return None


def fetch_blogs(scrapers, target_date=None):
    items = []
    if target_date:
        target_dt = datetime.strptime(target_date, "%Y-%m-%d").replace(
            tzinfo=timezone.utc)
    else:
        target_dt = datetime.now(timezone.utc)

    for cfg in scrapers:
        try:
            resp = requests.get(
                cfg["url"],
                timeout=30,
                headers={"User-Agent": "agentic-knowledge-digest/1.0"},
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            candidates = []
            for selector in cfg["selectors"]:
                for el in soup.select(selector):
                    a_tag = el if el.name == "a" else el.find("a")
                    if not a_tag or not a_tag.get("href"):
                        continue

                    href = a_tag.get("href", "")
                    if not href or href == "/" or href == "#":
                        continue

                    if href.startswith("/"):
                        href = cfg["link_prefix"] + href

                    title = a_tag.get_text(strip=True)
                    if not title or len(title) < 5:
                        h = el.find(["h1", "h2", "h3", "h4"])
                        title = h.get_text(strip=True) if h else title
                    if not title or len(title) < 5:
                        continue

                    text = el.get_text(" ", strip=True)
                    pub_date = _parse_blog_date(text)
                    if pub_date:
                        date_diff = abs((pub_date - target_dt).days)
                        if date_diff > 2:
                            continue

                    candidates.append({
                        "title": title[:200],
                        "url": href,
                        "date": pub_date,
                        "summary": text[:500],
                    })

            seen = set()
            for c in candidates[:8]:
                if c["url"] in seen:
                    continue
                seen.add(c["url"])
                date_str = c["date"].isoformat() if c["date"] else target_dt.isoformat()
                items.append(NewsItem(
                    title=c["title"],
                    url=c["url"],
                    source=cfg["name"],
                    date=date_str,
                    language=cfg["language"],
                    section=cfg["section"],
                    raw_content=c["summary"],
                ))
        except Exception as exc:
            print(f"  [warn] {cfg['name']}: {exc}", file=sys.stderr)

    return items


# ── GitHub Trending scraper ─────────────────────────────────────────────────

GITHUB_KNOWLEDGE_KEYWORDS = [
    "agent", "RAG", "rag", "retrieval", "knowledge-graph", "knowledge-base",
    "wiki", "ontology", "neo4j", "graphrag", "GraphRAG", "embedding",
    "vector", "memory", "LLM", "tool-use", "function-calling",
    "multi-agent", "reasoning", "chain-of-thought", "cot",
    "tree-of-thought", "kg", "graph-db", "cypher", "sparql",
    "knowledge-lifecycle", "graphify", "graphitti", "memgpt", "mem0",
    "llamaindex", "langchain", "crewai", "autogen", "semantic-kernel",
    "dspy", "text2sql", "knowledge-distillation", "prompt-engineering",
    "rerank", "colbert", "splade", "qdrant", "milvus", "chroma",
    "pinecone", "weaviate", "faiss", "ann",
]


def _gh_matches(description):
    text = description.lower()
    return any(kw.lower() in text for kw in GITHUB_KNOWLEDGE_KEYWORDS)


def fetch_github_trending(target_date=None):
    items = []
    if target_date:
        print(f"  [warn] GitHub Trending is today-only"
              f" (requested {target_date}). Using GitHub search API fallback.",
              file=sys.stderr)
        return _fetch_github_search(target_date)
    try:
        resp = requests.get(
            "https://github.com/trending?since=daily",
            headers={"User-Agent": "agentic-knowledge-digest/1.0"},
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

            if not _gh_matches(repo_name + " " + description):
                continue

            lang_el = article.find("span", itemprop="programmingLanguage")
            language = lang_el.get_text(strip=True) if lang_el else ""

            detail = description
            if language:
                detail = (f"{description}  [Lang: {language}]"
                          if description else f"[Lang: {language}]")

            items.append(NewsItem(
                title=repo_name,
                url=f"https://github.com{repo_path}",
                source="GitHub Trending",
                date=datetime.now(timezone.utc).isoformat(),
                language="en",
                section="tools_frameworks",
                raw_content=detail,
            ))
    except Exception as exc:
        print(f"  [warn] GitHub Trending: {exc}", file=sys.stderr)

    return items


def _fetch_github_search(target_date):
    items = []
    query = (
        "agent+OR+RAG+OR+knowledge-graph+OR+embedding+OR+vector-database"
        "+OR+llm+tools+OR+multi-agent+OR+retrieval+OR+neo4j"
    ) + f"+created:{target_date}"
    try:
        resp = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc",
                    "per_page": 10},
            headers={"User-Agent": "agentic-knowledge-digest/1.0",
                     "Accept": "application/vnd.github.v3+json"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        for repo in data.get("items", [])[:8]:
            items.append(NewsItem(
                title=repo.get("full_name", ""),
                url=repo.get("html_url", ""),
                source="GitHub Search",
                date=target_date,
                language="en",
                section="tools_frameworks",
                raw_content=repo.get("description", ""),
            ))
    except Exception as exc:
        print(f"  [warn] GitHub Search API: {exc}", file=sys.stderr)

    return items


# ── HuggingFace API ─────────────────────────────────────────────────────────

HF_KNOWLEDGE_TAGS = [
    "text-embeddings", "sentence-similarity", "question-answering",
    "feature-extraction", "retrieval-augmented-generation", "agents",
    "knowledge-graph", "rag", "text-retrieval", "document-retrieval",
    "reranking", "embedding", "dense-retrieval",
]

HF_MODEL_ID_KEYWORDS = [
    "embed", "rag", "retriev", "agent", "kg", "knowledge", "graph",
    "rerank", "dense", "sparse", "colbert", "bge", "e5", "gte", "jina",
    "voyage", "cohere-embed", "memory",
]


def _hf_matches(model):
    tags = [t.lower() for t in model.get("tags", [])]
    if any(t in HF_KNOWLEDGE_TAGS for t in tags):
        return True
    model_id = (model.get("modelId") or model.get("id", "")).lower()
    if any(kw.lower() in model_id for kw in HF_MODEL_ID_KEYWORDS):
        return True
    pipe_tag = (model.get("pipeline_tag") or "").lower()
    if pipe_tag in ("text-embeddings", "sentence-similarity",
                     "feature-extraction"):
        return True
    return False


def fetch_huggingface_trending(target_date=None):
    items = []
    try:
        resp = requests.get(
            "https://huggingface.co/api/models",
            params={"sort": "downloads", "direction": "-1", "limit": 30,
                    "full": "false"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        for model in data:
            if not _hf_matches(model):
                continue

            model_id = model.get("modelId") or model.get("id", "")
            if not model_id:
                continue

            tags = model.get("tags", [])[:5]
            downloads = model.get("downloads", 0)
            likes = model.get("likes", 0)
            last_modified = model.get("lastModified",
                                      datetime.now(timezone.utc).isoformat())

            if target_date:
                try:
                    lm_dt = datetime.fromisoformat(
                        last_modified.replace("Z", "+00:00"))
                    target_dt = datetime.strptime(
                        target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    diff = abs((lm_dt - target_dt).days)
                    if diff > 2:
                        continue
                except (ValueError, TypeError):
                    pass

            parts = [f"Downloads: {downloads}", f"Likes: {likes}"]
            if tags:
                parts.append(f"Tags: {', '.join(tags)}")

            items.append(NewsItem(
                title=model_id,
                url=f"https://huggingface.co/{model_id}",
                source="HuggingFace",
                date=last_modified,
                language="en",
                section="models_embeddings",
                raw_content=" | ".join(parts),
            ))
    except Exception as exc:
        print(f"  [warn] HuggingFace: {exc}", file=sys.stderr)

    return items


# ── arXiv API ───────────────────────────────────────────────────────────────

ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.IR", "cs.MA"]

ARXIV_AFFILIATIONS = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "deepmind": "DeepMind",
    "google research": "Google Research",
    "google deepmind": "Google DeepMind",
    "meta ai": "Meta AI",
    "microsoft research": "Microsoft Research",
    "apple": "Apple",
    "nvidia": "NVIDIA",
    "xai": "xAI",
    "stanford university": "Stanford",
    "massachusetts institute of technology": "MIT",
    "carnegie mellon university": "CMU",
    "university of california, berkeley": "UC Berkeley",
    "uc berkeley": "UC Berkeley",
    "university of washington": "UW",
    "deepseek": "DeepSeek",
    "深度求索": "DeepSeek",
    "minimax": "MiniMax",
    "zhipu": "Zhipu AI",
    "智谱": "Zhipu AI",
    "alibaba": "Alibaba",
    "baidu": "Baidu",
    "tencent": "Tencent",
    "bytedance": "ByteDance",
    "tsinghua university": "Tsinghua",
    "清华大学": "Tsinghua",
    "peking university": "Peking University",
    "北京大学": "Peking University",
    "shanghai ai lab": "Shanghai AI Lab",
    "上海人工智能实验室": "Shanghai AI Lab",
    "neo4j": "Neo4j",
}


def fetch_arxiv(categories, affiliations, max_per_cat=15, target_date=None):
    items = []
    base_url = "http://export.arxiv.org/api/query"

    for category in categories:
        try:
            search_query = f"cat:{category}"
            if target_date:
                search_query += (
                    f"+AND+submittedDate:[{target_date}0000"
                    f"+TO+{target_date}2359]")

            params = {
                "search_query": search_query,
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

                authors_list = [a.get("name", "")
                                for a in entry.get("authors", [])]
                authors_str = ", ".join(authors_list[:5])
                if len(authors_list) > 5:
                    authors_str += " et al."

                all_text = (
                    f"{entry.get('title', '')} "
                    f"{entry.get('summary', '')} "
                    f"{' '.join(authors_list)}"
                ).lower()

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
                    date=entry.get("published",
                                   datetime.now(timezone.utc).isoformat()),
                    language="en",
                    section="research_papers",
                    raw_content=f"Authors: {authors_str}\n\n{abstract}",
                    arxiv_id=arxiv_id,
                    organization=", ".join(matched) if matched else "",
                ))

            time.sleep(0.6)
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


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    socket.setdefaulttimeout(MAX_FETCH_TIMEOUT)

    parser = argparse.ArgumentParser(
        description="Collect daily AI/agentic knowledge news from RSS, "
                    "blogs, GitHub, HuggingFace, and arXiv."
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.expanduser("~/Desktop/agentic-knowledge-digest"),
        help="Directory for raw JSON output "
             "(default: ~/Desktop/agentic-knowledge-digest)",
    )
    parser.add_argument(
        "--hours", type=int, default=24,
        help="Hours to look back for RSS items (default: 24; "
             "ignored when --date is used)",
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

    # RSS
    print("Fetching RSS feeds ...", file=sys.stderr)
    rss_items = fetch_rss_feeds(RSS_FEEDS, args.hours, args.date
                                if args.date else None)
    print(f"  {len(rss_items)} items", file=sys.stderr)
    all_items.extend(rss_items)

    # Research & Community Blogs
    print("Fetching research blogs ...", file=sys.stderr)
    blog_items = fetch_blogs(BLOG_SCRAPERS, args.date)
    print(f"  {len(blog_items)} items", file=sys.stderr)
    all_items.extend(blog_items)

    # GitHub Trending
    print("Fetching GitHub Trending ...", file=sys.stderr)
    gh_items = fetch_github_trending(args.date)
    print(f"  {len(gh_items)} items", file=sys.stderr)
    all_items.extend(gh_items)

    # HuggingFace
    print("Fetching HuggingFace models ...", file=sys.stderr)
    hf_items = fetch_huggingface_trending(args.date)
    print(f"  {len(hf_items)} items", file=sys.stderr)
    all_items.extend(hf_items)

    # arXiv
    print("Fetching arXiv papers ...", file=sys.stderr)
    arxiv_items = fetch_arxiv(ARXIV_CATEGORIES, ARXIV_AFFILIATIONS,
                              target_date=args.date)
    print(f"  {len(arxiv_items)} items", file=sys.stderr)
    all_items.extend(arxiv_items)

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
        print(f"Total after link check: {len(all_items)} items",
              file=sys.stderr)

    # Compute stats
    sections = {}
    for item in all_items:
        sections[item.section] = sections.get(item.section, 0) + 1

    result = {
        "date": args.date,
        "items": [asdict(item) for item in all_items],
        "stats": {
            "total_items": len(all_items),
            "focus_matches": sum(1 for i in all_items if i.focus_match),
            **sections,
        },
    }

    # Save raw if requested
    if args.save_raw:
        os.makedirs(args.output_dir, exist_ok=True)
        raw_path = os.path.join(args.output_dir, f"{args.date}-raw.json")
        with open(raw_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Raw data saved → {raw_path}", file=sys.stderr)

    # Output JSON to stdout
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
