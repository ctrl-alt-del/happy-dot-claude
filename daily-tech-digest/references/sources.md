# Source Configuration

Curated list of RSS feeds, APIs, and web sources for the daily digest.

## RSS Feeds

### US / Silicon Valley News

| Source | Feed URL | Language |
|--------|----------|----------|
| Hacker News | `https://hnrss.org/frontpage?count=20` | en |
| TechCrunch | `https://techcrunch.com/feed/` | en |
| The Verge | `https://www.theverge.com/rss/index.xml` | en |
| Ars Technica | `https://feeds.arstechnica.com/arstechnica/index` | en |
| MIT Technology Review | `https://www.technologyreview.com/feed/` | en |

### Apple / Google Specialized

| Source | Feed URL | Language |
|--------|----------|----------|
| 9to5Mac | `https://9to5mac.com/feed/` | en |
| 9to5Google | `https://9to5google.com/feed/` | en |

### Tesla / SpaceX

| Source | Feed URL | Language |
|--------|----------|----------|
| Electrek | `https://electrek.co/feed/` | en |
| Teslarati | `https://www.teslarati.com/feed/` | en |
| SpaceNews | `https://spacenews.com/feed/` | en |

### China Tech (English)

| Source | Feed URL | Language |
|--------|----------|----------|
| TechNode | `https://technode.com/feed/` | en |
| SCMP Tech | `https://www.scmp.com/rss/4/feed` | en |
| Pandaily | `https://pandaily.com/feed/` | en |

### China Tech (Chinese)

| Source | Feed URL | Language |
|--------|----------|----------|
| 36kr | `https://36kr.com/feed` | zh |
| Huxiu | `https://www.huxiu.com/rss/0.xml` | zh |

## Web Scraping

| Source | URL | Method |
|--------|-----|--------|
| GitHub Trending | `https://github.com/trending?since=daily` | BeautifulSoup, parse `<article class="Box-row">` |

## APIs

| Source | Endpoint | Auth |
|--------|----------|------|
| HuggingFace Models | `https://huggingface.co/api/models?sort=downloads&direction=-1&limit=15` | None |
| arXiv | `http://export.arxiv.org/api/query` | None |

## arXiv Categories

```
cs.AI   — Artificial Intelligence
cs.CL   — Computation and Language (NLP)
cs.CV   — Computer Vision
cs.LG   — Machine Learning
cs.CR   — Cryptography and Security
cs.AR   — Hardware Architecture
```

## arXiv Affiliation Keywords

Used to detect papers from top institutions via author/abstract text matching.

### US Companies
- `openai` → OpenAI
- `anthropic` → Anthropic
- `deepmind` → DeepMind
- `google research` → Google Research
- `google deepmind` → Google DeepMind
- `meta ai` → Meta AI
- `microsoft research` → Microsoft Research
- `apple` → Apple
- `nvidia` → NVIDIA
- `tesla` → Tesla
- `xai` → xAI
- `spacex` → SpaceX

### US Universities
- `stanford university` → Stanford
- `massachusetts institute of technology` → MIT
- `carnegie mellon university` → CMU
- `university of california, berkeley` → UC Berkeley
- `uc berkeley` → UC Berkeley

### China Companies
- `deepseek` → DeepSeek
- `深度求索` → DeepSeek
- `minimax` → MiniMax
- `zhipu` → Zhipu AI
- `智谱` → Zhipu AI
- `alibaba` → Alibaba
- `baidu` → Baidu
- `tencent` → Tencent
- `bytedance` → ByteDance
- `sensetime` → SenseTime

### China Universities
- `tsinghua university` → Tsinghua
- `清华大学` → Tsinghua
- `peking university` → Peking University
- `北京大学` → Peking University
- `shanghai ai lab` → Shanghai AI Lab
- `上海人工智能实验室` → Shanghai AI Lab

## Content Filters

### Focus Topics (include — ranked by priority)
1. Embodied AI / 具身智能
2. Chip EDA / 芯片EDA
3. Robotics / 机器人
4. AI / Machine Learning
5. Memory chips / AI memory
6. Semiconductors / Chips
7. Software engineering

### Skip Topics (exclude)
- Cryptocurrency (Bitcoin, Ethereum, etc.)
- Token speculation / DeFi
- NFTs
- Web3 financial speculation

Note: Blockchain used for supply chain, identity, or enterprise infrastructure is acceptable.

## Caps

| Scope | Limit |
|-------|-------|
| Total items (global) | 25 |
| Highlights | Top 10 |
| Per section (US, China, GitHub, HF, arXiv each) | Top 5 suggested; fluid based on real distribution |

## Keyword Color Domains

Used by `generate_html.py` to color keyword pills consistently.

| Domain | Description | Light | Dark |
|--------|-------------|-------|------|
| `ai-ml` | AI models, training, LLMs | Blue `#dbeafe` / `#1e40af` | `#1e3a5f` / `#93c5fd` |
| `hardware` | Chips, EDA, semiconductor | Green `#dcfce7` / `#166534` | `#14532d` / `#86efac` |
| `robotics` | Embodied AI, robots | Orange `#ffedd5` / `#9a3412` | `#431407` / `#fdba74` |
| `software` | OSS, frameworks, benchmarks | Purple `#f3e8ff` / `#6b21a8` | `#3b0764` / `#d8b4fe` |
| `org-product` | Companies, product names | Slate `#f1f5f9` / `#334155` | `#1e293b` / `#94a3b8` |
| `safety` | Alignment, regulation, breaches | Red `#fce4ec` / `#9a1a1a` | `#4a1525` / `#fca5a5` |
| `other` | Fallback | Neutral `#f5f5f5` / `#525252` | `#262626` / `#a3a3a3` |

## Processed JSON Schema

The agent produces a processed JSON file consumed by `generate_html.py`.
See `SKILL.md` Step 7 for the full schema.
