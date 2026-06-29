# [Component Name]
**Source files**: `src/path/to/file.ts`, `src/path/to/other.ts`
**Entities**: [list of entity names this component owns]
**Depends on**: [[knowledge/data/entities]], [[knowledge/apis/interfaces]]
**Depended on by**: [[knowledge/apis/routes]], [[knowledge/architecture/components]]
**See also**: [[knowledge/edges/gotchas#relevant-heading]]
**Tags**: #api #[domain] #[another-domain]

## What it does

What responsibility does this module/component have? What problem does it
solve? One or two sentences that someone unfamiliar with the codebase can
understand.

## How it works

Walk through the key logic. What are the main functions/classes? How do they
interact?

### Key types
- `TypeName` — what it represents (file:line)
- `OtherType` — what it represents (file:line)

### Key functions
- `functionName()` — what it does, what it returns, how it fails
- `otherFunction()` — what it does, what it returns, how it fails

## Key patterns

What patterns (design or code) are used in this component? e.g.,
Repository pattern, Observer pattern, middleware chain, factory function.

## Gotchas

Anything about this component that would surprise someone modifying it
for the first time:
- [warning] Description of gotcha
- [warning] Description of another gotcha
