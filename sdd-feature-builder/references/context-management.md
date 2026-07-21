# Context Management for SDD Feature Builder

Long SDD sessions accumulate context from file reads, command outputs, and
conversation history. This degrades agent performance. Manage context
aggressively.

## When to Reset Context

### Between Major Phases

After completing a phase, consider a context reset:
- After Step 4 (spec.md + plan.md approved) → reset before Step 5 (tasks)
- After Step 5 (tasks.md written) → reset before Step 6 (implementation)
- After Step 6 (implementation done) → reset before Step 7 (ship)

### When Context is Polluted

Reset immediately if:
- More than 2 failed corrections on the same issue (context has stale approaches)
- The agent is repeating itself or forgetting earlier instructions
- More than 20 files have been read in this session

### How to Reset

- `/clear` — resets context entirely. Before clearing, write a brief state
  summary: current feature ID, what phase we're in, what's been completed.
- `/compact` — compresses history while preserving key patterns and decisions.
  Add instructions like "Preserve the feature ID (NNN), the spec summary, and
  all file paths listed in touches."

## Subagent Delegation

Use subagents for tasks that read many files, to keep main context lean.

### Investigation (Step 0 context load)

Instead of loading all context into the main session:
> Use a subagent to read MEMORY.md and knowledge/index.md. Report back
> any entries tagged #api, #ui, or #security that are relevant to
> [feature description]. Also check specs/index.md for file conflicts.

### Post-Implementation Review (alternative to full converge)

> Use a subagent with fresh context to review the diff against
> spec.md acceptance criteria and plan.md approach. Report only
> gaps that affect correctness or stated requirements.

### When to Use Subagents
- Reading more than 5 files to understand a subsystem
- Searching codebase for patterns/examples
- Reviewing implementation against specs (fresh perspective)
- Researching library compatibility or API documentation

### When NOT to Use Subagents
- Simple, focused tasks (1-3 files)
- Tasks requiring deep understanding of the full implementation
- When the subagent's summary would lose critical detail

## Checkpointing

Before risky operations, note that checkpoints are available:
- Before large refactors
- Before experimenting with alternative approaches
- The user can revert via `/rewind` or `Esc + Esc`

## Preserving State Across Resets

After `/clear`, reload minimal context:
1. Feature ID: NNN
2. Current phase and what's complete
3. Key file paths from plan.md touches
4. Any non-obvious decisions from MEMORY.md

Do NOT re-read all context — trust that the completed phases' artifacts
(spec.md, plan.md, tasks.md) capture what's needed.
