# Updating Knowledge Files

When the codebase changes, knowledge files can go stale. Rather than
regenerating everything from scratch, use a patch-based approach: identify
what changed, update only affected files, and verify cross-references.

## When to refresh

- After a significant feature merge or refactor
- When the user says "update the knowledge" or "refresh the analysis"
- When you notice a knowledge file is wrong or outdated during feature work
- Periodically, for active projects (suggest to user: weekly for active repos)

## The refresh workflow

### Step 1: Identify what changed

```bash
git diff --name-only HEAD~10  # or since last refresh date
```

Compare against `knowledge/index.md` frontmatter's `last_analyzed` date.
For each changed file, identify which knowledge files reference it by
searching `**Source files**:` fields:

```bash
grep -rl "src/auth/handler.ts" knowledge/
```

### Step 2: Categorize the change

| Change type | Refresh action |
|-------------|---------------|
| New file added | May need new knowledge file or update to existing one |
| File deleted | Remove source file references; check for orphaned knowledge |
| File modified (signature change) | Update the file's description in involved knowledge files |
| File modified (logic change) | Update "How it works" sections; check gotchas for new ones |
| Dep added/removed | Update `architecture/external-services.md` |
| Config changed | Update `conventions/configuration.md` |
| New test file | Update `conventions/testing.md` if patterns changed |

### Step 3: Update affected files

For each affected knowledge file:
1. Read the current version
2. Read the changed source files
3. Update only what changed — keep everything else
4. Update the file's `last_analyzed` entry (check inline metadata for a
   date, or compare against index.md)

### Step 4: Update index and cross-references

1. Update `knowledge/index.md`:
   - `last_analyzed` date
   - `files_count` if files were added/removed
   - Entry summaries for changed files

2. Check cross-references:
   - Every `[[link]]` still points to something
   - New files link to relevant existing files and vice versa

### Step 5: Report

Tell the user what was updated:
```
Refreshed 3 knowledge files based on 8 changed source files.
- architecture/components.md (updated)
- data/entities.md (updated)
- conventions/testing.md (new file added)
No cross-reference issues found.
```

## When to regenerate instead

Skip the patch approach and regenerate from scratch when:
- The architecture has fundamentally changed (refactor, rewrite)
- More than 30% of source files changed
- The user explicitly asks for a full re-analysis
- Cross-references are severely broken (more than 10% dead links)
