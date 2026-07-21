# Ship Checklist

## Phase checklist (whole feature)

- [ ] Step 0 context loaded (AGENTS/CLAUDE, constitution.md, SDD.md, MEMORY tags, index.md).
- [ ] `constitution.md` exists; all 7 articles held in memory for the feature.
- [ ] `specs/NNN-name/` created from `_template/`; ID is sequential + zero-padded.
- [ ] Mockups in `ux-ui/` (UI features without a provided mockup) — else skipped.
- [ ] ALL `[NEEDS CLARIFICATION]` markers in spec.md resolved (Step 3.5).
- [ ] `spec.md` + `plan.md` co-authored and approved (`doc-coauthoring`).
- [ ] `plan.md` frontmatter complete: `feature_id`, `name`, `status`,
      `depends_on`, `touches`, `created`.
- [ ] `plan.md` Constitution Check gates are all passed or justified in Complexity Tracking.
- [ ] Requirements quality checklist passed (Step 4.5).
- [ ] `test_plan.md` + `tasks.md` written (AAA; one task = one commit; organized by phase).
- [ ] Cross-artifact analysis (Step 5.5) returned clean — no gaps, conflicts, or ambiguities.
- [ ] Every task implemented, verified (build/test/lint), and committed.

## Ship checklist (after the last task)

- [ ] **Converge**: codebase assessed against spec/plan/tasks. No gaps remain.
      If tasks were appended, implemented and re-converged until clean.
- [ ] **takeaways.md** filled: what went well, what we learned, API/tech
      surprises, patterns worth reusing.
- [ ] **MEMORY.md** updated:
  - [ ] New gotchas added, tagged (`#api`/`#ui`/`#build`/`#security`), with `⚡`
        on anything that broke in production or is a hard guardrail.
  - [ ] "Patterns That Worked" appended if a reusable pattern emerged.
  - [ ] "Architecture Decisions" gets a new ADR if a real decision was made.
  - [ ] "Code Ownership Map" rows updated with this feature's ID.
  - [ ] "Common Bugs Fixed" lists any real defect + its fix.
- [ ] **constitution.md** reviewed:
  - [ ] Any pattern that recurred across ≥3 features proposed as a constitution
        amendment? (Amendment Log entry with rationale)
  - [ ] Any existing article that proved impractical? (Amendment Log entry
        proposing removal or modification)
- [ ] **specs/index.md**: feature status set (`✅ Done`), `touches` filled,
      `depends_on` recorded, `last_updated` bumped.
- [ ] **plan.md** `status` flipped to match the index.
- [ ] **AGENTS.md** updated if it carries a code-ownership map or "known gaps"
      note that this feature changes.
- [ ] Final full build + test + lint is green.
- [ ] No secrets committed; commit messages match the repo's convention.

## Status vocabulary

`📋 Planned → 🚧 In Progress → ✅ Done → 📦 Archived`
