# Source Configuration

Curated list of RSS feeds, research blogs, APIs, and web sources for the
agentic knowledge digest.

## RSS Feeds

### Core Tech Feeds

| Source | Feed URL | Language |
|--------|----------|----------|
| Hacker News | `https://hnrss.org/frontpage?count=20` | en |
| MIT Technology Review | `https://www.technologyreview.com/feed/` | en |

### Filtering Rules for RSS

For Hacker News and MIT Tech Review, only items whose title or content
mentions at least one of these keywords are included:
`agent`, `RAG`, `retrieval`, `knowledge`, `graph`, `embedding`, `vector`,
`memory`, `LLM`, `reasoning`, `tool-use`, `function-calling`, `multi-agent`,
`ontology`, `wiki`, `Neo4j`, `lifecycle`, `prompt`, `fine-tun`, `benchmark`.

## Research Blogs (Web Scraping)

Each blog is scraped via `requests` + `BeautifulSoup` from its listing page.
Posts are filtered by date to match the target digest date.

### AI Research Labs

| Source | Listing URL | Method |
|--------|-------------|--------|
| Anthropic Research | `https://www.anthropic.com/research` | Parse `<article>` elements, extract title + link + date |
| OpenAI Research | `https://openai.com/research/` | Parse research listing page, extract `<a>` cards |
| Google DeepMind | `https://deepmind.google/discover/blog/` | Parse blog listing, extract `<article>` or `<a>` cards |
| Meta AI Blog | `https://ai.meta.com/blog/` | Parse blog index page, extract post cards |
| Microsoft Research AI | `https://www.microsoft.com/en-us/research/blog/` | Parse blog listing, extract `<article>` elements |
| BAIR (Berkeley AI) | `https://bair.berkeley.edu/blog/` | Parse blog listing, extract post entries |
| Stanford AI Lab | `https://ai.stanford.edu/blog/` | Parse blog index, extract post listings |

### Agent & Knowledge Community

| Source | Listing URL | Method |
|--------|-------------|--------|
| LangChain Blog | `https://blog.langchain.dev/` | Parse blog listing, extract post cards |
| LlamaIndex Blog | `https://www.llamaindex.ai/blog` | Parse blog listing, extract post cards |
| The Gradient | `https://thegradient.pub/` | Parse article listing, extract entries |
| Lilian Weng's Blog | `https://lilianweng.github.io/` | Parse archive/index, extract post links |

## APIs

| Source | Endpoint | Auth |
|--------|----------|------|
| HuggingFace Models | `https://huggingface.co/api/models` | None |
| arXiv | `http://export.arxiv.org/api/query` | None |
| GitHub Trending | `https://github.com/trending` (HTML scrape) | None |
| GitHub Search API | `https://api.github.com/search/repositories` | Optional (higher rate limit with token) |

## arXiv Categories

Relevant categories for AI knowledge and agentic knowledge research:

```
cs.AI   — Artificial Intelligence
cs.CL   — Computation and Language (NLP)
cs.LG   — Machine Learning
cs.IR   — Information Retrieval
cs.MA   — Multi-Agent Systems
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
- `xai` → xAI

### US Universities
- `stanford university` → Stanford
- `massachusetts institute of technology` → MIT
- `carnegie mellon university` → CMU
- `university of california, berkeley` → UC Berkeley
- `uc berkeley` → UC Berkeley
- `university of washington` → UW

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

### China Universities
- `tsinghua university` → Tsinghua
- `清华大学` → Tsinghua
- `peking university` → Peking University
- `北京大学` → Peking University
- `shanghai ai lab` → Shanghai AI Lab
- `上海人工智能实验室` → Shanghai AI Lab

### Knowledge Graph & Lifecycle Research Groups
- `neo4j` → Neo4j
- `llm-wiki` → LLM-Wiki
- `knowledge graph group` → Knowledge Graph Group
- `semantic web group` → Semantic Web Group

## HuggingFace Model Filters

Models are filtered to include only those relevant to knowledge and agents.
Filter by tags:

```
text-embeddings, sentence-similarity, question-answering,
feature-extraction, retrieval-augmented-generation, agents,
knowledge-graph, rag, text-retrieval, document-retrieval,
reranking, embedding, dense-retrieval
```

Also include models whose `modelId` or `pipeline_tag` contains:
`embed`, `rag`, `retriev`, `agent`, `kg`, `knowledge`, `graph`,
`rerank`, `dense`, `sparse`, `colbert`, `bge`, `e5`, `gte`, `jina`,
`voyage`, `cohere-embed`.

## GitHub Trending Filters

Repositories from `https://github.com/trending?since=daily` are filtered
to include only those whose title, description, or language matches one
of these keyword patterns:

```
agent, RAG, rag, retrieval, knowledge-graph, knowledge-base,
wiki, ontology, neo4j, graphrag, GraphRAG, embedding, vector,
memory, LLM, tool-use, function-calling, multi-agent, reasoning,
chain-of-thought, cot, tree-of-thought, kg, graph-db, cypher,
sparql, knowledge-lifecycle, graphify, graphitti, memgpt, mem0,
llamaindex, langchain, crewai, autogen, semantic-kernel,
dspy, text2sql, knowledge-distillation, prompt-engineering
```

### Specific Repos to Track Mentions

When these repos appear in trending or are referenced in blog posts,
prioritize them:

- `microsoft/graphrag`
- LLM-wiki implementations
- Code Wiki projects
- Graphify tooling
- Graphitti tooling
- `neo4j/` organization repos
- `mem0ai/mem0`
- `cpacker/MemGPT`
- `run-llama/llama_index`
- `langchain-ai/langchain`

## Focus Topics

### Detection Keywords & Priority Boosts

Each topic has a set of keywords used to detect relevance in item titles and
content. Matching boosts `priority_hint` by the stated amount.

### 1. `rag-retrieval` (priority boost: 10)

```
RAG, retrieval augmented, retrieval-augmented, retrieval augmented generation,
dense retrieval, sparse retrieval, hybrid retrieval, hybrid search, document
retrieval, information retrieval, passage retrieval, reranking, re-ranking,
retriever, cross-encoder, bi-encoder, late interaction, colbert, splade,
multi-hop retrieval, iterative retrieval, self-RAG, corrective RAG, CRAG,
adaptive RAG, agentic RAG, modular RAG, 检索增强
```

### 2. `agent-memory` (priority boost: 9)

```
agent memory, long-term memory, short-term memory, working memory, episodic
memory, semantic memory, procedural memory, context window, context management,
memory consolidation, memory retrieval, memory store, memgpt, MemGPT, mem0,
Mem0, letta, letta agent, memory bank, memory stream, reflection memory,
记忆系统, 智能体记忆
```

### 3. `knowledge-graph` (priority boost: 8)

```
knowledge graph, GraphRAG, graph RAG, graph-based RAG, graph retrieval,
Neo4j, neo4j, Cypher, cypher, SPARQL, sparql, Graphify, graphify, Graphitti,
graphitti, property graph, RDF, triple store, graph database, GNN, graph
neural network, entity linking, entity resolution, community detection,
Leiden algorithm, hierarchical graph, ontology, knowledge representation,
知识图谱, 图数据库
```

### 4. `knowledge-lifecycle` (priority boost: 7)

```
knowledge lifecycle, knowledge management, knowledge base, knowledge
evolution, knowledge consolidation, knowledge versioning, knowledge decay,
knowledge pruning, knowledge forgetting, knowledge curation, knowledge
validation, knowledge conflict, stale knowledge, outdated knowledge,
LLM-wiki, LLM wiki, LLM-wiki v2, Code Wiki, code wiki, wiki-style knowledge,
knowledge update, knowledge refresh, incremental knowledge, knowledge sync,
知识生命周期, 知识管理, 知识库, 知识演化
```

### 5. `agent-architecture` (priority boost: 6)

```
agent framework, multi-agent, multi agent, agent orchestration, tool use,
function calling, tool calling, autonomous agent, LLM agent, agentic,
agentic workflow, agent design, agent architecture, delegation, agent
communication, crewAI, AutoGen, LangGraph, semantic kernel, agent protocol,
MCP, model context protocol, A2A, agent-to-agent, agent swarm, hierarchical
agent, 智能体架构, 多智能体, 工具调用
```

### 6. `embeddings-vectors` (priority boost: 5)

```
embedding model, text embedding, dense embedding, sparse embedding, vector
database, vector store, vector search, semantic search, similarity search,
ANN search, approximate nearest neighbor, faiss, chroma, pinecone, weaviate,
milvus, qdrant, MTEB, embedding benchmark, embedding fine-tuning, Matryoshka,
binary embedding, quantization embedding, 嵌入模型, 向量数据库
```

### 7. `ai-knowledge` (priority boost: 4)

```
knowledge distillation, continual learning, lifelong learning, fine-tuning,
instruction tuning, supervised fine-tuning, SFT, preference optimization,
RLHF, DPO, training data, data curation, data synthesis, synthetic data,
knowledge transfer, model merging, model distillation, teacher-student,
知识蒸馏, 持续学习, 微调
```

### 8. `cognition-reasoning` (priority boost: 3)

```
chain-of-thought, chain of thought, CoT, tree-of-thought, tree of thought,
ToT, graph-of-thought, planning, reasoning, logical reasoning, multi-step
reasoning, self-reflection, self-critique, self-consistency, verification,
deliberation, scratchpad, inner monologue, ReAct, reflection agent, critic,
思维链, 推理, 规划
```

### 9. `context-prompting` (priority boost: 2)

```
prompt engineering, prompt optimization, prompt compression, prompt
design, in-context learning, ICL, few-shot, zero-shot, long context,
context length, context extension, context window, prompt tuning, soft
prompt, hard prompt, automatic prompt, DSPy, prompt chaining, 提示工程,
上下文学习
```

### 10. `evaluation-benchmark` (priority boost: 1)

```
benchmark, evaluation, eval, agent benchmark, retrieval benchmark, RAG
benchmark, knowledge benchmark, knowledge graph benchmark, BEIR, MTEB,
MMLU, AGIEval, agent evaluation, task completion, success rate, accuracy,
F1, recall, precision, NDCG, MRR, HITS@K, 基准测试, 评估
```

## Content Filters

### Skip Topics (exclude)

- Cryptocurrency (Bitcoin, Ethereum, etc.)
- Token speculation / DeFi
- NFTs
- Web3 financial speculation
- General consumer tech (phone releases, laptop reviews, gaming hardware)
- Enterprise SaaS unrelated to AI knowledge
- Non-AI hardware (CPUs for gaming, monitors, peripherals)

### Include Topics

All items must connect to at least one of the 10 focus topic areas:
RAG/retrieval, agent memory, knowledge graphs, knowledge lifecycle,
agent architectures, embeddings/vectors, AI knowledge, cognition/reasoning,
context/prompting, or evaluation/benchmarks.

## Caps

| Scope | Limit |
|-------|-------|
| Total items (global) | 25 |
| Highlights | Top 10 |
| Per section | Fluid; reflect real distribution, no forced equal counts |

## Keyword Color Domains

Used by `generate_html.py` to color keyword pills consistently.

| Domain | Description | Light BG / Text | Dark BG / Text |
|--------|-------------|-----------------|----------------|
| `rag-retrieval` | RAG, retrieval | `#dbeafe` / `#1e40af` | `#1e3a5f` / `#93c5fd` |
| `agent-memory` | Agent memory systems | `#fce7f3` / `#9d174d` | `#4a1942` / `#f9a8d4` |
| `knowledge-graph` | Graphs, Neo4j, GNN | `#dcfce7` / `#166534` | `#14532d` / `#86efac` |
| `knowledge-lifecycle` | Lifecycle, wiki, evolution | `#fef3c7` / `#92400e` | `#422006` / `#fcd34d` |
| `agent-architecture` | Agents, tool use | `#ffedd5` / `#9a3412` | `#431407` / `#fdba74` |
| `embeddings-vectors` | Embeddings, vector DBs | `#ede9fe` / `#5b21b6` | `#3b0764` / `#c4b5fd` |
| `ai-knowledge` | Distillation, fine-tuning | `#e0e7ff` / `#3730a3` | `#1e1b4b` / `#a5b4fc` |
| `cognition-reasoning` | CoT, planning, reasoning | `#fce4ec` / `#9a1a1a` | `#4a1525` / `#fca5a5` |
| `context-prompting` | Prompts, ICL, context | `#f3e8ff` / `#6b21a8` | `#3b0764` / `#d8b4fe` |
| `evaluation-benchmark` | Benchmarks, evals | `#f1f5f9` / `#334155` | `#1e293b` / `#94a3b8` |
| `other` | Fallback | `#f5f5f5` / `#525252` | `#262626` / `#a3a3a3` |

## Processed JSON Schema

The agent produces a processed JSON file consumed by `generate_html.py`.
See `SKILL.md` Step 7 for the full schema.
