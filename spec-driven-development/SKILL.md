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

> **Related skill:** this skill only *sets up* the scaffolding. To actually build
> a feature against an already-set-up workflow, use the `sdd-feature-builder`
> skill, which assigns the next `NNN` spec folder, co-authors spec + plan, and
> implements one commit per task through to takeaways and `MEMORY.md`.

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

Create `MEMORY.md` at project root. Start with an empty template — it grows organically
as features ship. The template includes sections for:
- API/tech gotchas (tagged for searchability)
- Patterns that worked
- Architecture decisions (ADRs)
- Code ownership map
- Common bugs fixed
- AI workflow rule

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
