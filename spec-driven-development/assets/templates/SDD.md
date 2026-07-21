# Spec-Driven Development Workflow

## Phases

0. **Constitution** — Establish/check governing principles (once per project, then referenced).
1. **Spec** — Write plan.md + spec.md + UX mockups. Review with stakeholder.
2. **Plan** — Break into tasks.md + test_plan.md. Estimate and order.
2.5. **Checklist** — Quality checklist for requirements (completeness, clarity, consistency).
3. **Build** — Implement one task per commit. Verify build + tests at each commit.
3.5. **Analyze** — Cross-artifact consistency check (spec ↔ plan ↔ tasks).
4. **Ship** — Write takeaways.md. Merge to MEMORY.md.
4.5. **Converge** — Assess codebase against spec/plan/tasks. Append gaps. Loop until clean.

## Skills to Use

### Constitution Phase
- No skill needed. Read `constitution.md` at project root. Run constitution gate check
  in plan.md's "Constitution Check" section. If the project has no constitution yet,
  use the template from this skill's `assets/templates/constitution.md`.

### Spec Writing Phase
- **`doc-coauthoring`**: Invoke when starting spec.md or plan.md. Enforces a
  describe → review → approve → iterate loop. Prevents guessing requirements.
- **`[NEEDS CLARIFICATION]`**: Before spec approval, resolve ALL ambiguity markers
  in spec.md. Surface unresolved markers to the stakeholder.

### Mockup Generation Phase
- **`canvas-design` + `theme-factory`**: Invoke when user describes a feature
  but has NO mockup. `canvas-design` generates visual layout; `theme-factory`
  applies the project's existing color scheme. Output to ux-ui/.
  Skip when user provides real screenshots — AI reads them natively.

### Checklist Phase
- No skill needed. Use `assets/templates/checklist.md` to generate a quality
  checklist. Verify ALL `[NEEDS CLARIFICATION]` markers are resolved. Verify every
  user story has an independent test description. Verify edge cases are enumerated.
  If the checklist surfaces gaps, return to spec writing phase.

### Interactive Prototyping Phase (optional)
- **`frontend-design`**: When feature has complex interaction logic (navigation
  flow, state transitions). Generates HTML/React prototype.
- **`webapp-testing`**: Verifies HTML prototype interactions with Playwright.
  Use when: feature has >= 3 screens or multi-step flows that would be
  expensive to get wrong in native code.

### Analyze Phase
- No skill needed. See `assets/references/analyze.md` for the full procedure.
  In brief: verify every spec requirement traces to plan and tasks, every task
  traces back to a requirement, file paths are consistent, and no contradictions
  exist between artifacts. Produce a severity-graded report. Do NOT edit files —
  report findings and return to the owning phase to fix them. Run before
  implementation and re-run if artifacts change.

### Converge Phase
- No skill needed. See `assets/references/converge.md` for the full procedure.
  In brief: after implementation, compare code against spec/plan/tasks. Append
  remaining work as new tasks in tasks.md. Loop until clean. NEVER edit code —
  only append to tasks.md.

### Reading Provided Screenshots
- No skill needed. AI reads real UI screenshots natively. Only use when the
  user provides actual images of their intended UI.

### Test Plan Authoring
- No skill needed. Apply standard practices:
  - AAA pattern (Arrange-Act-Assert)
  - Boundary testing
  - Equivalence partitioning
  Reference project-specific testing conventions.

### Codebase Knowledge Generation
- **`codebase-to-sdd-knowledge`**: Invoke when there is existing code but no
  `knowledge/` directory or when `MEMORY.md` is sparse. Analyzes the codebase
  to produce structured knowledge files (`knowledge/`) and populate `MEMORY.md`
  with durable findings from actual code and git history — not templates. Run
  once during SDD setup and re-run when the codebase structure changes
  significantly.

## Skill Invocation Order

```
Feature Request Received
│
├── constitution.md exists?
│   ├── YES → read and hold principles for all later phases
│   └── NO  → create from template → continue
│
├── knowledge/ directory exists and is recent?
│   ├── YES → proceed
│   └── NO  → codebase-to-sdd-knowledge → generate knowledge/ + populate MEMORY.md
│
├── User has mockup?
│   ├── YES → AI reads natively → spec writing
│   └── NO  → canvas-design + theme-factory → generate mockup
│
├── doc-coauthoring → co-write spec.md + plan.md
│   └── MUST resolve ALL [NEEDS CLARIFICATION] markers before proceeding
│
├── Checklist phase → generate quality checklist
│   ├── PASS → proceed to tasks
│   └── FAIL → return to spec writing to fix gaps
│
├── Complex flow (>= 3 screens)?
│   ├── YES → frontend-design → HTML prototype
│   │         └── webapp-testing → verify interactions
│   └── NO  → skip
│
├── Write tasks.md + test_plan.md → tasks derived from spec requirements
│
├── Analyze phase → cross-artifact consistency check
│   ├── CLEAN → proceed to implementation
│   └── ISSUES → return to owning phase, fix, re-analyze
│
├── Implementation → tasks.md → one commit per task
│
├── Converge phase → assess codebase against spec/plan/tasks
│   ├── CONVERGED → proceed to ship
│   └── TASKS APPENDED → implement appended tasks → converge again
│
└── Ship → takeaways.md → promote to MEMORY.md → update index
```

## Conventions

- Folder names: `NNN-short-kebab-name/` (e.g., `001-user-auth/`)
- NNN is zero-padded sequential ID (001, 002, ...)
- Statuses: 📋 Planned → 🚧 In Progress → ✅ Done → 📦 Archived
- One task = one independent, build-verifiable, test-passing commit
- File conflicts surface via `touches` field in plan.md frontmatter + index.md
- Tasks are organized by phase: Setup → Foundational → User Stories (P1, P2, P3) → Polish

## Build & Test Commands

- Build: `{project_build_cmd}`
- Test: `{project_test_cmd}`

These commands are used in tasks.md for each task's verification step.

## References

- `assets/references/analyze.md` — Cross-artifact consistency analysis procedure
- `assets/references/converge.md` — Post-implementation gap detection procedure
