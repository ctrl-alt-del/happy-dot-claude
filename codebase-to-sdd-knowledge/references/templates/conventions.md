# Conventions: [Topic]
**Source files**: [files where these conventions are visible]
**Tags**: #conventions

## [Convention category]

Describe the convention as observed in the codebase. Include:

- What the convention is (with examples from actual code)
- Where it applies (all files? specific directories?)
- When it applies (always? except when?)
- Why it matters (what happens if you violate it?)

Example:

## Naming conventions

### Files
- Source files: `kebab-case.ts` (e.g., `user-service.ts`)
- Test files: `<name>.test.ts` (e.g., `user-service.test.ts`)
- React components: `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- Index/barrel files: `index.ts` (exports only, no logic)
- Observed in: entire `src/` tree

### Variables and functions
- Variables: `camelCase` (e.g., `userEmail`, `isLoading`)
- Functions: `camelCase`, verb-first (e.g., `getUserById`, `createSession`)
- Classes: `PascalCase` (e.g., `UserService`, `AuthMiddleware`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- Observed in: all source files

## [Another convention category]

Same structure as above.
