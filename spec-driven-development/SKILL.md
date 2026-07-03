---
name: spec-driven-development
description: >
  Sets up a spec-driven development (SDD) workflow in any project. Creates the specs/ folder
  structure, MEMORY.md for accumulated knowledge, and AGENTS.md integration so AI tools
  follow a write-spec-before-code workflow. Use this skill when the user asks to set up
  spec-driven development, write specs before coding, add SDD, GitHub spec kit, structured
  feature development, or when they want a formal process for building features with
  documented specifications, test plans, and task breakdowns. Also use when the user says
  "I want to follow a spec-first approach" or mentions feature specs, planning documents,
  or any similar process-improvement workflow for their codebase.
---

# Spec-Driven Development Setup

Sets up a complete spec-driven development workflow in any project. Creates the
folder structure, templates, and AGENTS.md integration so AI tools follow a
write-spec-before-code process for every feature.

> **Related skills:**
> - This skill only *sets up* the scaffolding. To actually build a feature,
>   use the `sdd-feature-builder` skill.
> - To populate `MEMORY.md` and generate a `knowledge/` directory from existing
>   source code (rather than starting with empty templates), use the
>   `codebase-to-sdd-knowledge` skill after setup.

## Memory integration

If the project already has `memory/meta.json` (from the `self-evolving-memory`
skill), skip the plain MEMORY.md step below. Instead, after scaffolding the
project, run `scripts/memory-init.sh` to initialize the self-evolving memory.
This creates the `memory/` directory alongside MEMORY.md and enables automatic
knowledge evolution (distillation, consolidation, connection, forgetting).

When writing to MEMORY.md, use the enriched YAML frontmatter entry format from
`self-evolving-memory/references/entry-format.md`. Include `type`, `confidence`,
`tags`, and `source` fields.

If `memory/meta.json` does not exist, use the plain MEMORY.md template below.

## Migration to self-evolving memory

If the project was set up with an older version of this skill and has a plain
MEMORY.md (no YAML frontmatter on entries, no `memory/` directory), migrate it
to the self-evolving memory system:

1. **Detect**: MEMORY.md exists AND `memory/meta.json` does NOT exist.
2. **Run**: `scripts/memory-init.sh` — this parses the plain MEMORY.md, assigns
   `mem-XXX` IDs to each entry, infers `type` from section headers
   (`## 🧠 Tech Gotchas` → `gotcha`, `## 🔧 Patterns That Worked` → `pattern`,
   `## 📐 Architecture Decisions` → `decision`, `## 📂 Code Ownership Map` →
   `fact`, `## 🐛 Common Bugs Fixed` → `gotcha`), extracts tags from `#tag`
   mentions in entry bodies, and creates the `memory/` directory structure.
   The original MEMORY.md is backed up to `memory/.backup/pre-migration/`.
3. **Verify**: Run `scripts/memory-status.sh` — confirm all entries were parsed
   and counts match expectations.
4. **Evolve** (optional): Run `scripts/memory-evolve.sh` to consolidate similar
   entries, build the relationship graph, and compute initial confidence scores.
5. **Report**: "Migrated N entries to self-evolving memory. Run
   `scripts/memory-graph.sh` to visualize the knowledge graph."

All existing MEMORY.md content is preserved. Plain entries without frontmatter
are treated as confirmed/permanent with default metadata and will be enriched
with YAML frontmatter on the next evolution cycle.

## What Gets Created

```
{project_root}/
├── MEMORY.md                          # Accumulated project knowledge
├── AGENTS.md / CLAUDE.md              # Updated with trigger section
└── specs/                             # Feature specifications
    ├── SDD.md                         # Workflow reference for AI
    ├── index.md                       # Feature manifest with status
    └── _template/                     # Stubs for new features
        ├── plan.md
        ├── spec.md
        ├── tasks.md
        ├── test_plan.md
        ├── takeaways.md
        └── ux-ui/                     # Mockups and screenshots
```

## Setup Steps

### Step 1: Assess the Project

Before creating anything, scan the project to understand:
- **Tech stack**: language, framework, build system
- **Build commands**: how to compile, test, lint
- **Testing conventions**: framework, test location, commands
- **Existing AGENTS.md / CLAUDE.md**: integrate with or create
- **Existing docs/**: leave permanent docs alone; specs/ is separate

### Step 2: Create the Folder Structure

Create `specs/` at project root with `_template/` and `ux-ui/` subdirectory.
Create `_template/ux-ui/` as an empty directory for mockups.

### Step 3: Write Template Files

Fill in the template files in `_template/`. Use `assets/templates/` from this skill
as the source. **Replace placeholders** with project-specific values:

- `{project_build_cmd}` → Actual build command (e.g., `npm run build`, `./gradlew assembleDebug`)
- `{project_test_cmd}` → Actual test command (e.g., `npm test`, `./gradlew testDebug`)
- `{tech_stack}` → Language and framework (e.g., "React + TypeScript", "Java + Android")
- `{project_name}` → Project name from package.json, build.gradle, or directory name

### Step 4: Create MEMORY.md

Create `MEMORY.md` at project root. Start with the template — it grows organically
as features ship. The template includes sections for:
- API/tech gotchas (tagged for searchability)
- Patterns that worked
- Architecture decisions (ADRs)
- Code ownership map
- Common bugs fixed
- AI workflow rule

If the project already has existing code, consider running the
`codebase-to-sdd-knowledge` skill after setup to populate `MEMORY.md` and
generate a `knowledge/` directory from analysis of the actual codebase,
git history, and structure — rather than starting from an empty template.

### Step 5: Update AGENTS.md / CLAUDE.md

If `AGENTS.md` or `CLAUDE.md` already exists, append the trigger section.
If neither exists, create `AGENTS.md` with the trigger section and a brief
project summary.

The trigger section:
```markdown
## Triggering Feature Development

When the user describes a new feature (creates, builds, adds, wants a new screen,
etc.), follow the spec-driven development workflow in `specs/SDD.md`. Read
`MEMORY.md` before writing any spec to avoid repeating known bugs. The workflow:
1. Generate mockups if needed (`canvas-design` + `theme-factory`)
2. Co-author spec + plan (`doc-coauthoring`)
3. Write test plan and tasks
4. Implement one commit per task
5. Write takeaways → promote to `MEMORY.md`
```

### Step 6: Customize specs/SDD.md

Write `specs/SDD.md` by copying `assets/templates/SDD.md` and replacing:
- `{project_build_cmd}` and `{project_test_cmd}` with actual commands
- Any tech-specific skill recommendations
- If the project has a design system, document the colors for `theme-factory`

### Step 7: Report

After setup, summarize what was created and how to use it:
- How to start a new feature (just describe it)
- Where feature specs live (`specs/NNN-feature-name/`)
- How MEMORY.md evolves (takeaways → curate → promote)
- That `codebase-to-sdd-knowledge` can populate MEMORY.md and generate a
  `knowledge/` directory from existing code when setting up SDD on a project
  that already has source code
- That `self-evolving-memory` can initialize a self-evolving memory layer on
  top of MEMORY.md — enabling auto-distillation, consolidation, and usage-based
  forgetting over time

## Template Customization

The templates in `assets/templates/` are starting points. Adapt them to the
project's conventions:
- If the project uses a different issue tracker, adjust the status values
- If the project has strict commit message conventions, reflect them in tasks.md
- If features often involve UI changes, emphasize the UX/UI section in spec.md
- For CLI/API projects, replace UX/UI with API contract or CLI interface section

## What NOT to Change

- `specs/` is separate from permanent `docs/` — don't merge them
- `MEMORY.md` is project-wide, not per-feature
- YAML frontmatter in MEMORY.md entries (from `self-evolving-memory`) must be preserved — do not strip it
- Feature IDs are zero-padded sequential (001, 002, ...)
- One task = one commit (build + test must pass per task)
- `index.md` tracks file conflicts via the `touches` column
- `plan.md` frontmatter is machine-parseable — keep the YAML structure

## References

- `assets/templates/SDD.md` — Workflow reference template
- `assets/templates/MEMORY.md` — Starting memory template
- `assets/templates/plan.md` — Feature plan template (with frontmatter)
- `assets/templates/spec.md` — Specification template
- `assets/templates/tasks.md` — Task checklist template
- `assets/templates/test_plan.md` — Test plan template
- `assets/templates/takeaways.md` — Feature takeaways template
- `assets/templates/index.md` — Feature index template
- `self-evolving-memory/references/entry-format.md` — Enriched MEMORY.md entry format (use when `memory/meta.json` exists)
