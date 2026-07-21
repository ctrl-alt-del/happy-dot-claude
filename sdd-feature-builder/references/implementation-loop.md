# Implementation Loop (one commit per task)

Run this loop for every task in `tasks.md`. Keep exactly one task `in_progress`.

## The loop (TDD — Red → Green → Refactor)

1. **Re-read the task** and the files it `touches`. Re-check the relevant
   `MEMORY.md` `#tag` entries and `constitution.md` articles for that area first
   — most repeated bugs are logged there.

2. **Red — Write failing tests** FIRST (if the task includes tests):
   - Write the test code. It MUST fail before implementation.
   - Run the test to confirm it fails (Red phase).
   - Do NOT write implementation code until tests exist and fail.

3. **Green — Implement** the smallest change that makes tests pass:
   - Follow existing code conventions (imports, style, libraries already in use).
   - Add no comments unless the project's conventions ask for them.
   - Run tests — they must pass (Green phase).

4. **Refactor** — clean up while tests stay green:
   - Remove duplication, improve names, simplify.
   - Re-run tests after each refactor step.

5. **Verify** with the project's commands, in this order:
   - Build (e.g. `./gradlew assembleDebug`, `npm run build`)
   - Full test suite (e.g. `./gradlew testDebug`, `npm test`)
   - Lint (e.g. `./gradlew lint`, `npm run lint`)
   **Output the test results** — show the evidence (passing test count, build
   exit code). Do NOT just say "tests pass." Show the output.

6. **Fix** anything red and re-run until green.

7. **Commit** — stage only the files for this task and write a message that
   matches the repo's existing style (inspect `git log --oneline` first; some
   repos use Conventional Commits like `feat:`/`docs:`, others use sentence-case
   subjects). Reference the feature ID when the repo does.

8. **Mark the task done** in `tasks.md`. Move to the next.

## Staged implementation (for large features)

When a feature has 10+ tasks, work in stages to avoid context overflow.
Scope each run with an argument:

```
Implement only Setup (Phase 1) and Foundational (Phase 2). Stop before user story phases.
```

Then:

```
Now implement User Story 1 (Phase 3) only. Stop before User Story 2.
```

Verify each stage works before moving to the next. Re-read `MEMORY.md` and
`constitution.md` at the start of each stage.

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

## Verification evidence

After each task's verify step, output the actual results:
- Test runner output (pass/fail counts, not just "all green")
- Build exit code
- Lint output (zero warnings/errors, or list what remains)

This is how the user knows verification actually ran. Never assert success
without showing the evidence.

## Verification before declaring the feature complete

Run the full build + test + lint suite once more against the final state and
ensure it is green before moving to the ship checklist.
