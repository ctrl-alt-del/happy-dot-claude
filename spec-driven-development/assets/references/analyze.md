# Cross-Artifact Consistency Analysis

Run this READ-ONLY procedure after tasks.md is written but BEFORE implementation.
It checks that spec.md, plan.md, and tasks.md are consistent and complete.

## Procedure

### 1. Requirement Traceability

For EVERY functional requirement (FR-XXX) in spec.md:
- [ ] Is there a corresponding task in tasks.md?
- [ ] Is there a corresponding design element in plan.md (data model, API contract, or approach)?
- [ ] Does the acceptance scenario for this FR map to at least one test in test_plan.md?

### 2. Task Traceability

For EVERY task in tasks.md:
- [ ] Does it trace back to a specific user story or FR in spec.md?
- [ ] If it has no clear requirement parent, it is an ORPHAN TASK — flag as Gap
- [ ] Does the file path in the task description match the plan.md touches list?

### 3. Cross-Artifact Consistency

- [ ] Plan technical choices don't contradict spec requirements
  - Example: spec says "offline-capable" but plan assumes always-connected → Conflict
  - Example: spec says "no external APIs" but plan uses a cloud service → Conflict
- [ ] File paths are consistent across plan.md touches, tasks.md paths, and index.md
- [ ] Plan.md Constitution Check gates are all passed or justified in Complexity Tracking
- [ ] Plan.md data model entities match spec.md user story entities

### 4. Coverage

- [ ] Every spec user story has a corresponding phase in tasks.md
- [ ] Every spec edge case has a corresponding test in test_plan.md
- [ ] Every spec non-functional requirement is addressed in plan.md
- [ ] Every plan.md "Files to Create/Change" appears in at least one task

### 5. Status & Dependencies

- [ ] Tasks within phases are ordered by dependency (no dependency inversion)
- [ ] [P] markers are correct (tasks marked [P] truly share no files or data)
- [ ] Plan.md `depends_on` matches index.md for the same feature

## Output Format

Produce a report with three severity levels:

### 🔴 Critical (blocks implementation)
- Requirement FR-XXX has no task coverage — gap
- Plan contradicts spec on [specific point] — conflict

### 🟡 Major (should fix before implementation)
- Task T0XX is orphaned (no requirement parent)
- File path mismatch: plan.md says `src/foo.py`, tasks.md says `src/bar/foo.py`

### 🟢 Minor (can proceed, note for later)
- Edge case [X] from spec has no test (low risk)
- Test plan doesn't cover boundary [Y]

## After Analysis

- **Clean report** → proceed to implementation
- **Issues found** → return to the owning phase:
  - Gap → return to tasks.md (add missing task)
  - Conflict → return to plan.md (reconcile with spec) or spec.md (update requirement)
  - Ambiguity → return to clarification (resolve [NEEDS CLARIFICATION])
- Re-run analysis after fixes until clean
