# happy-dot-claude

A monorepo of **agent skills** for Claude and other AI agents. Each top-level
directory that contains a `SKILL.md` is a self-contained skill that gets
installed into `~/.claude/skills/<skill-name>` and is loaded by an agent when its
description matches the task at hand.

## Skills

| Skill | What it does | Evals |
|-------|--------------|-------|
| [`codebase-to-sdd-knowledge`](codebase-to-sdd-knowledge/SKILL.md) | Analyzes a code repository (language detection, structural map, git history, deep analysis) to produce atomic, cross-referenced knowledge files organized by domain and populate `MEMORY.md` with durable findings — building a cognitive model of the codebase for downstream SDD agents. | — |
| [`daily-tech-digest`](daily-tech-digest/SKILL.md) | Fetches and summarizes daily AI/tech news from US, China, GitHub Trending, HuggingFace, and arXiv into an interactive HTML digest with search, keyword filtering, dark mode, and bilingual titles. | ✅ |
| [`gitignore-hardening`](gitignore-hardening/SKILL.md) | Audits and hardens `.gitignore` to prevent leaking secrets and sensitive info (keystores, .env files, API keys, credentials), and stops tracking files that were already committed. | — |
| [`markdown-to-sdd-knowledge`](markdown-to-sdd-knowledge/SKILL.md) | Converts unstructured markdown (PRDs, feature requests, meeting notes, Slack threads) into structured, atomic knowledge files for Spec-Driven Development workflows. | ✅ |
| [`sdd-feature-builder`](sdd-feature-builder/SKILL.md) | Implements a feature end-to-end via a project's existing spec-driven development workflow: next `NNN` spec folder, co-authored spec + plan, test plan + tasks, one-commit-per-task with build/test/lint, then takeaways → `MEMORY.md` and `specs/index.md` updates. | — |
| [`spec-driven-development`](spec-driven-development/SKILL.md) | Sets up a spec-driven development workflow in any project with `specs/` folder structure, `MEMORY.md`, and `AGENTS.md` integration so AI tools follow a write-spec-before-code workflow. | — |

## How it works

A skill is a folder with a `SKILL.md` file (YAML frontmatter + markdown
instructions) plus optional `references/`, `scripts/`, `assets/`, and `evals/`.
Agents read the frontmatter `description` to decide when to load the skill, then
follow the instructions in the body.

This repo is the **source of truth**. Skills are **symlinked** into
`~/.claude/skills`, so a `git pull` here instantly updates every installed skill.

## Install

```sh
./install.sh
```

This symlinks each skill in this repo into `~/.claude/skills/<skill-name>`.

- Preview without making changes: `./install.sh --dry-run`
- Replace existing (stale) symlinks: `./install.sh --force`

Update later with `git pull` — symlinks pick up changes automatically.

Manual alternative for a single skill:

```sh
ln -s "$PWD/markdown-to-sdd-knowledge" ~/.claude/skills/markdown-to-sdd-knowledge
```

## Repository structure

```
happy-dot-claude/
├── AGENTS.md                  # Skill-authoring convention (read this to add a skill)
├── README.md
├── install.sh                 # Symlinks each skill into ~/.claude/skills
└── <skill-name>/
    ├── SKILL.md               # Required: frontmatter (name, description) + instructions
    ├── references/            # Optional: docs loaded on demand
    ├── scripts/               # Optional: executable helpers
    ├── assets/                # Optional: templates/files used in output
    └── evals/                 # Optional: evals.json + fixture files
```

## Adding a skill

See [`AGENTS.md`](AGENTS.md) for the full convention and pre-commit checklist.
In short: create `<skill-name>/SKILL.md` (the directory name must equal the
frontmatter `name`), write a description that says *what it does* and *when to
use it*, add any `references/` / `scripts/` / `evals/`, run `./install.sh`, and
add a row to the catalog table above.
