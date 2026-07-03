# Skill Integration Guide

How to wire self-evolving memory into existing skills.

## Non-breaking integration pattern

Add this block to the top of any skill's SKILL.md, after the frontmatter and
before any section headers:

```markdown
## Memory integration

Before beginning any work:
- If the project has `memory/meta.json`, run `scripts/memory-query.sh --topic <tag>`
  to load relevant prior knowledge.
- If the project has `memory/meta.json`, also run `scripts/memory-status.sh`
  to check for stale or pending-review entries relevant to this task.

After completing work:
- Write any durable learnings to MEMORY.md following the format in
  `self-evolving-memory/references/entry-format.md`.
- Run `scripts/memory-update.sh` to regenerate derived files.
```

## Per-skill integration details

### `spec-driven-development`

**Read**: On scaffold, if `memory/meta.json` exists, query for existing decisions
and patterns to pre-populate MEMORY.md sections rather than starting from empty
templates.

**Write**: On scaffold, register the new project setup decisions as entries.

### `sdd-feature-builder`

**Read**: Step 0 (load context) — in addition to searching MEMORY.md for `#tags`,
also run `memory-query.sh --topic <tag>` for each tag relevant to the feature.
This provides community summaries and related entries beyond the direct match.

**Write**: Step 7 (ship) — when promoting takeaways to MEMORY.md, use the
enriched YAML frontmatter format. Run `memory-update.sh` after writing.

### `codebase-to-sdd-knowledge`

**Read**: Phase 1 - check if `memory/meta.json` exists. If yes, load existing
gotchas and patterns to avoid re-discovering known issues.

**Write**: Phase 4.4 (populate MEMORY.md) — use enriched entry format with
frontmatter. Run `memory-update.sh` after populating.

### `markdown-to-sdd-knowledge`

**Read**: Before extraction, query memory for existing knowledge on the same
domain to avoid duplicate entries.

**Write**: After extraction, if extracted knowledge overlaps with existing
entries, offer to consolidate rather than create duplicates.

### `gitignore-hardening`

**Read**: Query memory for previously discovered sensitive-file patterns.

**Write**: Register newly discovered patterns as facts.

### `daily-tech-digest`

**Read-only**: Query memory for project's tech stack context to refine
relevance ranking of news items. Does not write to memory.

## Integration checklist

For each skill being integrated:

1. [ ] Add "Memory integration" block to skill's SKILL.md.
2. [ ] Determine relevant tags for that skill's domain.
3. [ ] Add `--topic` query call before main workflow.
4. [ ] Add memory write step after workflow (if applicable).
5. [ ] Test: run skill on a project with memory, verify it loads context.
6. [ ] Test: run skill on a project without memory, verify it degrades gracefully.

## Fallback behavior

If `memory/meta.json` does not exist, the skill MUST degrade gracefully:
- Skip memory queries silently.
- Fall back to existing MEMORY.md reading behavior.
- Do not error or warn (the user may not have opted into memory yet).
