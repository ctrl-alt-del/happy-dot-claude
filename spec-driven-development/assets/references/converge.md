# Post-Implementation Convergence

Run this after all tasks.md tasks are implemented. It assesses whether the
codebase satisfies the spec, plan, and tasks.

**CRITICAL RULE**: This procedure NEVER edits code. It only appends findings
as new tasks to tasks.md.

## Procedure

### 1. Spec Acceptance Check

For each user story's acceptance scenarios in spec.md:
- Does the implemented code satisfy the scenario?
- Walk through the Given/When/Then in the running application
- If a scenario fails → Critical gap, append to tasks.md

### 2. Plan Fidelity Check

Compare the implementation against plan.md:
- Does the data model match plan.md's data model?
- Do API/CLI contracts match plan.md's contracts?
- Was the approach followed? If deviated, is the deviation intentional?
- Are constitution gates still satisfied?

### 3. Task Completion Check

Verify every task in tasks.md is actually implemented:
- Each task's file paths exist and contain the described functionality
- Edge cases from spec.md are handled
- Quickstart validation scenarios pass

### 4. Constitution Compliance

Re-run the Constitution Check gates:
- Article II (TDD): Do tests exist and pass?
- Article III (Modularity): Is the feature a self-contained module?
- Article IV (Simplicity): Did we stay within the file budget?
- Article V (Anti-Abstraction): No unnecessary wrappers added during implementation?
- Article VI (Integration Reality): Real components preferred over mocks?
- Article VII (Observability): Logging, health checks, metrics present?

## Output

### ✅ Converged

No gaps found. tasks.md left unchanged. Feature is complete — proceed to ship.

### 📋 Tasks Appended

Gaps found. New tasks appended under `## Convergence (Cycle N)` in tasks.md.
The tasks describe what's missing and how to verify the fix.

## Loop

1. Converge finds gaps → tasks appended
2. Run implementation loop on appended tasks
3. Converge again
4. Repeat until Converged

If converge appends tasks more than 3 times, something is structurally wrong
with the spec or plan. Stop and re-examine the artifacts.

## Findings Severity

### 🔴 Critical (missing requirement)
- Acceptance scenario from spec.md is not satisfied
- Functional requirement FR-XXX is not implemented
- Constitution gate fails

### 🟡 Major (deviation from plan)
- Implementation diverges from plan.md approach without documented rationale
- Data model differs from plan without documented rationale
- File structure differs from plan without documented rationale

### 🟢 Minor (quality/optimization)
- Missing log statement (Article VII)
- Performance optimization opportunity
- Code style inconsistency

Only Critical and Major findings become convergence tasks. Minor findings are
noted but don't block convergence.
