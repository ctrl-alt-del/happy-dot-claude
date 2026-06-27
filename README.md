# happy-dot-claude

A monorepo of **agent skills** for Claude and other AI agents. Each top-level
directory that contains a `SKILL.md` is a self-contained skill that gets
installed into `~/.claude/skills/<skill-name>` and is loaded by an agent when its
description matches the task at hand.

## Skills

| Skill | What it does | Evals |
|-------|--------------|-------|
| [`markdown-to-sdd-knowledge`](markdown-to-sdd-knowledge/SKILL.md) | Converts unstructured markdown (PRDs, feature requests, meeting notes, Slack threads) into structured, atomic knowledge files for Spec-Driven Development workflows. | ✅ |

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
