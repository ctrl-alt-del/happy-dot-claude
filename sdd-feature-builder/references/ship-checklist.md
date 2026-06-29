# Ship Checklist

## Phase checklist (whole feature)

- [ ] Step 0 context loaded (AGENTS/CLAUDE, SDD.md, MEMORY tags, index.md).
- [ ] `specs/NNN-name/` created from `_template/`; ID is sequential + zero-padded.
- [ ] Mockups in `ux-ui/` (UI features without a provided mockup) — else skipped.
- [ ] `spec.md` + `plan.md` co-authored and approved (`doc-coauthoring`).
- [ ] `plan.md` frontmatter complete: `feature_id`, `name`, `status`,
      `depends_on`, `touches`, `created`.
- [ ] `test_plan.md` + `tasks.md` written (AAA; one task = one commit).
- [ ] Every task implemented, verified (build/test/lint), and committed.

## Ship checklist (after the last task)

- [ ] **takeaways.md** filled: what went well, what we learned, API/tech
      surprises, patterns worth reusing.
- [ ] **MEMORY.md** updated:
  - [ ] New gotchas added, tagged (`#api`/`#ui`/`#build`/`#security`), with `⚡`
        on anything that broke in production or is a hard guardrail.
  - [ ] "Patterns That Worked" appended if a reusable pattern emerged.
  - [ ] "Architecture Decisions" gets a new ADR if a real decision was made.
  - [ ] "Code Ownership Map" rows updated with this feature's ID.
  - [ ] "Common Bugs Fixed" lists any real defect + its fix.
- [ ] **specs/index.md**: feature status set (`✅ Done`), `touches` filled,
      `depends_on` recorded, `last_updated` bumped.
- [ ] **plan.md** `status` flipped to match the index.
- [ ] **AGENTS.md** updated if it carries a code-ownership map or "known gaps"
      note that this feature changes.
- [ ] Final full build + test + lint is green.
- [ ] No secrets committed; commit messages match the repo's convention.

## Status vocabulary

`📋 Planned → 🚧 In Progress → ✅ Done → 📦 Archived`
