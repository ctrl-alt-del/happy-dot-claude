# Gotchas & Sharp Edges
**Source files**: [files containing the gotchas]
**Tags**: #gotchas #warnings

## Critical gotchas

Items marked ⚡ are production-breaking. Do not ignore these.

### ⚡ [Gotcha title]
- **What**: Describe the gotcha — what unexpected behavior occurs
- **Where**: `src/path/file.ts:42`
- **Why**: Why this happens (root cause)
- **How to avoid**: What to do instead
- **Who to ask**: If unclear, who might know more

### [Less critical gotcha title]
Same structure but without ⚡ marker.

## Known bugs

Bugs found in code (from FIXME comments, reverted commits, or code inspection):

### [Bug description]
- **Source**: `src/path/file.ts:87` (FIXME comment) or `git revert abc123`
- **Impact**: What goes wrong
- **Reproduction**: How to trigger it (if known)
- **Workaround**: Current workaround (if any)

## Anti-patterns in the codebase

Recurring patterns that should not be emulated:

### [Anti-pattern title]
- **What**: The anti-pattern
- **Where it appears**: Files/paths
- **Why it's a problem**: What can go wrong
- **What to do instead**: The correct approach
