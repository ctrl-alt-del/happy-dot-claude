# AGENTS.md

Guidance for AI agents (and humans) working in this repository.

## What this repo is

`happy-dot-claude` is a monorepo of **agent skills**. Every top-level directory
that contains a `SKILL.md` is one skill. Skills are installed into
`~/.claude/skills/<skill-name>` via symlink (`./install.sh`), so this repo is the
source of truth and `git pull` updates installed skills live.

When working here you are usually doing one of: **adding a skill**, **editing an
existing skill**, or **maintaining repo docs/tooling**. Follow the conventions
below so skills load and trigger correctly for downstream agents.

## Anatomy of a skill

```
<skill-name>/
├── SKILL.md      # REQUIRED
├── references/   # optional — docs loaded into context on demand
├── scripts/      # optional — executable code for deterministic/repetitive work
├── assets/       # optional — files used in output (templates, icons, fonts)
└── evals/        # optional — evals.json + evals/files/ fixtures
```

`SKILL.md` is the only required file. It has YAML frontmatter followed by markdown
instructions:

```markdown
---
name: my-skill
description: >
  What the skill does AND when to use it (trigger contexts and phrases).
---

# My Skill

Imperative instructions for the agent...
```

## Conventions

### Naming
- The directory name MUST equal the frontmatter `name`.
- Use lowercase kebab-case (e.g., `markdown-to-sdd-knowledge`).

### Description (this is the trigger)
The `description` is how an agent decides whether to load the skill. It MUST:
- State **what the skill does** AND **when to use it** (contexts, trigger phrases).
- Be specific and slightly "pushy" to counter under-triggering — e.g., "Use this
  whenever the user mentions X, Y, or Z, even if they don't say 'skill'."
- Hold ALL the "when to use" information. Do not bury triggering rules in the body.

### Body
- Use imperative voice ("Read the file", "Extract each fact").
- Keep `SKILL.md` under ~500 lines. If it grows past that, move detail into
  `references/` and point to it from the body (progressive disclosure).
- For a reference file longer than ~300 lines, add a table of contents.
- For multi-variant skills, put each variant in its own reference file and select
  the right one from `SKILL.md`.

### Bundled resources
- `references/` — documentation the agent reads only when needed.
- `scripts/` — deterministic code; prefer scripts over prose for repetitive,
  exact operations.
- `assets/` — templates/fonts/icons used to produce output.

### Evals (encouraged for verifiable skills)
Skills with objectively checkable output (transforms, extraction, code-gen, fixed
workflows) should ship evals. Layout:

```
evals/
├── evals.json
└── files/        # input fixtures referenced by evals
```

`evals.json` schema (see `markdown-to-sdd-knowledge/evals/evals.json` for a full
example):

```json
{
  "skill_name": "<name>",
  "evals": [
    {
      "id": 1,
      "prompt": "Instruction given to an agent that has the skill",
      "expected_output": "Prose description of the correct result",
      "files": ["evals/files/example.md"],
      "expectations": ["A concrete, checkable assertion", "..."]
    }
  ]
}
```

## Adding a skill

1. Create `<skill-name>/SKILL.md` with valid frontmatter (`name` == dir name).
2. Write a description that says what it does AND when to trigger.
3. Add `references/`, `scripts/`, `assets/`, `evals/` as needed.
4. Run `./install.sh` to symlink it into `~/.claude/skills`.
5. Add a row to the catalog table in `README.md`.

## Pre-commit checklist

- [ ] `SKILL.md` has YAML frontmatter with `name` and `description`.
- [ ] Directory name equals the frontmatter `name` (kebab-case).
- [ ] `description` states what it does AND when to use it.
- [ ] `SKILL.md` is under ~500 lines; long detail lives in `references/`.
- [ ] All referenced files and links resolve.
- [ ] `evals/files/` fixtures exist for any eval that lists them.
- [ ] README catalog table updated.
- [ ] No secrets, credentials, or malware; behavior matches the description
      (principle of least surprise).

## Reference examples

- `markdown-to-sdd-knowledge/` is a complete, well-formed skill (frontmatter,
  `references/`, `evals/`). Use it as the template when authoring new skills.
- `codebase-to-sdd-knowledge/` demonstrates `scripts/` (deterministic helper
  tools), a multi-phase workflow, and language-specific reference files — a
  more advanced skill structure for complex analysis workflows.
