# Implementation Loop (one commit per task)

Run this loop for every task in `tasks.md`. Keep exactly one task `in_progress`.

## The loop

1. **Re-read the task** and the files it `touches`. Open the relevant
   `MEMORY.md` `#tag` entries for that area first — most repeated bugs are
   logged there.
2. **Implement** the smallest change that satisfies the task. Follow existing
   code conventions (imports, style, libraries already in use). Add no comments
   unless the project's conventions ask for them.
3. **Verify** with the project's commands, in this order:
   - Build (e.g. `./gradlew assembleDebug`, `npm run build`)
   - Tests (e.g. `./gradlew testDebug`, `npm test`)
   - Lint (e.g. `./gradlew lint`, `npm run lint`)
   Compiling once covers the whole tree, so it is fine to run the heavier
   build/lint at meaningful checkpoints, but tests must pass before a commit.
4. **Fix** anything red and re-run until green.
5. **Commit** — stage only the files for this task and write a message that
   matches the repo's existing style (inspect `git log --oneline` first; some
   repos use Conventional Commits like `feat:`/`docs:`, others use sentence-case
   subjects). Reference the feature ID when the repo does.
6. **Mark the task done** in `tasks.md` and your todo list. Move to the next.

## Staging for clean per-task commits

When all edits already exist in the working tree (e.g. you implemented ahead),
still produce one commit per task by **staging only that task's files**:

```sh
git add <files for this task>
git commit -m "<message in repo style>"
```

Order commits by dependency so each commit's tree compiles on its own
(interfaces/models before their consumers; production code before the docs
commit).

## Handling test failures

- Read the failure; map it to the task's change.
- If a shared interface change ripples into other files/tests, update them as
  part of the **same** task (don't leave the tree non-compiling between commits).
- If a mock returns `null`/empty for an unstubbed call, stub it explicitly.
- Consult `MEMORY.md` — the same failure class may already be documented.

## Partial or blocked tasks

- Never mark a task done on intent. If blocked, keep it `in_progress` and add a
  follow-up task describing the blocker.
- If a task turns out larger than one commit, split it into sub-tasks (NNN.x)
  rather than letting one commit balloon.

## Verification before declaring the feature complete

Run the full build + test + lint suite once more against the final state and
ensure it is green before moving to the ship checklist.
