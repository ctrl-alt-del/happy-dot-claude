---
name: codebase-to-sdd-knowledge
description: >
  Analyzes code repositories to extract structured, atomic knowledge files
  for Spec-Driven Development workflows. Produces small, focused files
  organized by domain (architecture, data models, APIs, conventions,
  patterns, gotchas, ownership) with explicit cross-references forming a
  navigable knowledge graph. Populates MEMORY.md with durable findings
  derived from code analysis, git history, and structural inspection.
  Use this whenever the user asks to understand a codebase, onboard onto
  a project, extract project knowledge from source code, prepare a repo
  for SDD, generate structured documentation from an existing codebase,
  or needs an AI-maintained cognitive model of a codebase — even if they
  say "what does this project do?", "help me understand this code",
  "analyze this repo", "document this codebase", "map out the
  architecture", or "what are the conventions here?".
---

# Codebase to SDD Knowledge

Analyze a code repository and produce two artifacts:

1. **`knowledge/` directory** — small, atomic markdown files, one concept
   per file, cross-referenced with wiki-style links. This is a navigable
   knowledge graph that SDD agents can traverse to find exactly what they
   need without loading everything into context.

2. **`MEMORY.md` (populated)** — durable project knowledge: tech gotchas,
   patterns that work, architecture decisions, code ownership, and common
   bugs — derived from actual code and git history, not templates.

## When to use this

- The user asks to understand a codebase they're new to
- Someone wants architectural documentation generated from existing code
- A repo needs to be prepared for spec-driven development
- An AI agent needs a durable mental model of the project before building
  features
- The user says "onboard me onto this project", "what does this code do?",
  "document the architecture", or similar

## When NOT to use this

- The repo already has a populated `knowledge/` directory and the user
  only wants to answer a specific question — just read the relevant
  knowledge files
- The user is setting up SDD from scratch — use `spec-driven-development`
  instead (this skill runs after or alongside it)
- The user is converting a markdown document to knowledge — use
  `markdown-to-sdd-knowledge` instead
- The user wants to build a feature — use `sdd-feature-builder` instead

## Quick start

```
1. Run scripts/detect_language.py on the project root
   → identifies language, build system, test/lint commands, monorepo status
2. Run scripts/git_analysis.py on the project root
   → hotspots, ownership map, reverted commits (potential bugs)
3. Run scripts/structure_map.py on the project root
   → annotated directory tree with symbol extraction
4. Read references/languages/<detected>.md for what to look for
5. Follow references/workflow.md for the full 5-phase process
```

## How this skill works

The skill builds a cognitive model of the codebase through five phases:

| Phase | What happens | Key output |
|-------|-------------|------------|
| 1. Detect & Orient | Language, build system, existing scaffolding | Baseline understanding |
| 2. Structural Map | Directory tree, symbol extraction, git hotspots | Dependency graph, hotspots |
| 3. Deep Analysis | Per-language: data models, APIs, patterns, gotchas | Detailed code understanding |
| 4. Knowledge Production | Write atomic files + populate MEMORY.md | `knowledge/` + `MEMORY.md` |
| 5. Validate | Report summary, flag gaps, ask user questions | Confirmed accuracy |

The full workflow is in `references/workflow.md` — read it when starting.

## Output structure

Each codebase gets a `knowledge/` directory at the project root. Files are
only created for concepts that actually exist in the codebase — not every
template is filled.

```
knowledge/
├── index.md                          ← structured TOC (with YAML frontmatter)
├── architecture/
│   ├── overview.md                   ← high-level architecture
│   ├── components.md                 ← top-level modules and their roles
│   ├── entry-points.md               ← CLI, servers, main()
│   ├── data-flow.md                  ← how data moves through the system
│   └── external-services.md          ← databases, caches, queues, 3rd-party APIs
├── data/
│   ├── entities.md                   ← core business entities
│   ├── database-schema.md            ← tables, relationships, migrations
│   └── api-models.md                 ← DTOs, request/response types
├── apis/
│   ├── routes.md                     ← REST/GraphQL/gRPC route groups
│   └── interfaces.md                 ← internal module contracts
├── security/
│   └── auth-model.md                 ← auth middlewares, validation, rate limiting
├── conventions/
│   ├── naming.md                     ← naming patterns observed
│   ├── file-organization.md          ← directory/file conventions
│   ├── testing.md                    ← test patterns, fixtures, runners
│   ├── error-handling.md             ← error patterns, logging approach
│   ├── configuration.md              ← env vars, feature flags, profiles
│   └── commit-style.md              ← git commit conventions
├── patterns/
│   └── common.md                     ← recurring design and code patterns
├── edges/
│   ├── gotchas.md                    ← critical things that will bite you
│   ├── tech-debt.md                  ← TODOs, FIXMEs, known debt
│   └── flaky-areas.md               ← unstable tests, race conditions
├── ownership/
│   └── owners.md                     ← directory/file ownership from git
└── gaps.md                           ← uncertainties, questions for the user
```

### Approximate file counts by codebase size

| Codebase size | Knowledge files | Turnaround |
|---|---|---|
| Small lib (<20 files) | 6–8 files | ~30 seconds |
| Medium project (20–100 files) | 10–16 files | ~1–2 minutes |
| Large repo (100–500 files) | 15–22 files | ~2–5 minutes |
| Monorepo (500+ files) | 20–30+ files | ~5–10 minutes |

## File format conventions

### Every knowledge file uses inline metadata (NOT YAML frontmatter)

Each file opens with bold metadata fields, then the body. This is the
standard format:

```markdown
# Component Name
**Source files**: `src/path/file.ts`, `src/other.ts`
**Entities**: User, Session, Token
**Depends on**: [[data/entities]], [[conventions/naming]]
**Depended on by**: [[apis/routes]], [[architecture/components]]
**See also**: [[edges/gotchas#auth-pitfalls]]
**Tags**: #auth #security #api

## What it does
...

## How it works
...

## Key patterns
...

## Gotchas
...
```

The only exception is `index.md`, which uses YAML frontmatter for
machine-parseable metadata:

```yaml
---
last_analyzed: 2026-06-30
files_count: 14
domains: [architecture, data, apis, conventions, edges, ownership, security]
coverage: 0.78
language: typescript
---
# Knowledge Index
...
```

### Wiki-style links use project-root-relative paths

All links in knowledge files are relative to the project root:
- `[[knowledge/data/entities]]` — link to another knowledge file
- `[[knowledge/edges/gotchas#auth-pitfalls]]` — link to a heading within a file

### MEMORY.md sections to populate

When writing to `MEMORY.md` (create or update at project root):
- **Tech Gotchas** — critical guardrails found in code (`⚠️` markers for
  production-breaking items)
- **Patterns That Worked** — conventions observed in actual code
- **Architecture Decisions (ADRs)** — inferred from structure and comments
- **Code Ownership Map** — from git blame aggregation
- **Common Bugs / Sharp Edges** — from git reverted commits and FIXME patterns
- **AI Workflow Rule** — keep existing if present, otherwise add:
  "Always read `knowledge/index.md` before starting any feature work."

Each entry in gotchas and patterns should be tagged for searchability
(`#api`, `#ui`, `#build`, `#security`, `#data`, `#infra`).

## Language-specific strategies

Detect the primary language (Phase 1), then read the relevant file:

- [TypeScript/JavaScript](references/languages/typescript.md)
- [Python](references/languages/python.md)
- [Go](references/languages/go.md)
- [Rust](references/languages/rust.md)
- [Generic (any language)](references/languages/generic.md)

Each language file tells you:
- Which directories and files are significant in that ecosystem
- What tree-sitter queries extract symbols effectively
- Common conventions and gotchas to watch for
- Build/test/lint tool detection heuristics

## Knowledge file templates

When creating knowledge files, read the corresponding template for exact
structure and required fields:

- [Architecture overview](references/templates/architecture-overview.md)
- [Component (one module)](references/templates/component.md)
- [Data entities](references/templates/entities.md)
- [API routes](references/templates/routes.md)
- [Conventions](references/templates/conventions.md)
- [Gotchas](references/templates/gotchas.md)
- [Code ownership](references/templates/owners.md)
- [Index (TOC)](references/templates/index.md)

## Refreshing knowledge

When code changes, knowledge files can go stale. Read
[references/update-workflow.md](references/update-workflow.md) for how to
refresh efficiently using a patch-based approach — only updating what
changed rather than regenerating everything.

## Scripts

These scripts handle deterministic, repetitive work. Run them before
starting analysis:

| Script | Purpose |
|--------|---------|
| `scripts/detect_language.py` | Auto-detect language, build system, test/lint commands |
| `scripts/git_analysis.py` | Hotspots, ownership, reverted commits, bug patterns |
| `scripts/structure_map.py` | Directory tree with tree-sitter symbol extraction |

Run them from the skill directory with the project root as an argument:
```bash
python scripts/detect_language.py /path/to/project
```

## Failure modes

- **Permission denied**: Ask the user for access. Skip restricted
  directories and note them in `gaps.md`.
- **No build system detected**: Fall back to `references/languages/generic.md`.
  Note the gap.
- **Massive codebase (>1000 files)**: Analyze top-level directories only.
  Note in `gaps.md` what was skipped and why.
- **Mixed languages**: Select the dominant language (most files). Note other
  languages in `gaps.md` for later analysis.
- **Unreadable files (binary, minified, generated)**: Skip them. List paths
  in `gaps.md` under a "Skipped files" section.
- **No git history** (shallow clone, new repo): Skip git analysis. Note in
  `gaps.md` under "Missing data" section.
