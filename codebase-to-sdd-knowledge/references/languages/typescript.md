# TypeScript / JavaScript Analysis

## Language detection heuristics

The skill auto-detects TypeScript/JavaScript if the project contains:
- `package.json` at the root
- `tsconfig.json` (TypeScript) or `.js`/`.mjs` files as primary source
- `node_modules/` directory (confirms Node.js ecosystem)

## Framework detection

After confirming JS/TS, look for framework markers:
- Next.js: `next.config.*` exists
- Express/Fastify: `app.ts`, `server.ts` with express/fastify imports
- React: `react` in dependencies, `.tsx`/`.jsx` files
- Vue: `vue` in dependencies, `.vue` files
- NestJS: `@nestjs/core` in dependencies, `main.ts` with NestFactory
- Remix: `@remix-run/` in dependencies
- SvelteKit: `@sveltejs/kit` in dependencies

## Key directories to analyze

| Directory | What it contains | Priority |
|-----------|-----------------|----------|
| `src/` | Primary source code | High |
| `routes/` or `pages/` | Route definitions (Next.js, Remix) | High |
| `api/` | Backend API routes | High |
| `lib/` or `utils/` | Shared utilities | Medium |
| `components/` | UI components | Medium |
| `hooks/` | React hooks | Medium |
| `services/` | Business logic / API clients | High |
| `models/` or `types/` | Type definitions, data models | High |
| `middleware/` | Auth, validation, logging middleware | High |
| `migrations/` or `prisma/` | Database schema, migrations | High |
| `config/` | Configuration files | Medium |
| `tests/` or `__tests__/` | Test files | Low (analyze patterns only) |
| `e2e/` or `cypress/` | End-to-end tests | Low |
| `.github/workflows/` | CI/CD pipelines | Low |

## Dependency analysis (from package.json)

- **Runtime dependencies** (`dependencies`): What the app needs at runtime
  - ORMs: `prisma`, `drizzle-orm`, `typeorm`, `sequelize`
  - Web frameworks: `express`, `fastify`, `@nestjs/core`, `next`
  - Auth: `next-auth`, `@clerk/nextjs`, `passport`, `lucia`
  - Validation: `zod`, `yup`, `joi`, `class-validator`
  - API clients: `@tanstack/react-query`, `trpc`, `graphql-request`
  - Logging: `winston`, `pino`, `bunyan`
  - Testing: `vitest`, `jest`, `mocha`, `playwright`, `cypress`
- **Dev dependencies** (`devDependencies`): Linting, formatting, build tools
  - TypeScript: `typescript`, `@types/*`
  - Linting: `eslint`, `prettier`, `oxlint`, `biome`
  - Build: `webpack`, `vite`, `esbuild`, `tsup`, `tsx`
  - Testing: same as above if dev-only

## Symbol extraction patterns

Use tree-sitter queries for structured extraction, or grep for quick scans:

### TypeScript interfaces and types
```bash
rg "^(export\s+)?(interface|type)\s+\w+" --include="*.ts" --no-heading
```

### Classes
```bash
rg "^(export\s+)?(class|abstract class)\s+\w+" --include="*.ts" --no-heading
```

### Functions and methods
```bash
rg "^(export\s+)?(async\s+)?function\s+\w+|^\s+(public\s+|private\s+|protected\s+)?(async\s+)?\w+\(" --include="*.ts" --no-heading
```

### Exports (barrel files)
```bash
rg "export\s+\*|export\s+\{.*\}\s+from" --include="*.ts" --no-heading | head -20
```

### Route definitions
```bash
rg "(app|router)\.(get|post|put|delete|patch|use)\(" --include="*.ts" --no-heading
```

### Middleware
```bash
rg "middleware|\.use\(|guard|auth" --include="*.ts" --no-heading | grep -i "middleware\|guard\|\.use"
```

## Common conventions to detect

- **File naming**: `kebab-case.ts` vs `camelCase.ts` vs `PascalCase.tsx`
- **Test naming**: `*.test.ts` vs `*.spec.ts` vs `*.test.tsx` vs `__tests__/`
- **Barrel exports**: `index.ts` files that re-export from subdirectories
- **Path aliases**: Check `tsconfig.json` `paths` for `@/` or `~/` aliases
- **Import order**: Grouped imports (external → internal → relative)
- **Error handling**: try/catch patterns, custom error classes, error middleware
- **Environment vars**: `process.env.*` usage, validated by Zod or similar
- **Feature flags**: `config/flags.ts` or similar, or `env.ENABLE_FEATURE`

## Gotchas specific to JS/TS ecosystems

- **Barrel file performance**: Large `index.ts` barrel files can cause
  circular dependencies and slow bundling. Flag any `index.ts` with >20
  re-exports.
- **any usage**: grep for `: any` or `as any` — signals missed type safety
- **Dual package hazards**: If a package exports both ESM and CJS, check for
  `exports` field in `package.json` — can cause resolution bugs
- **ts-ignore / ts-expect-error**: grep `@ts-ignore` or `@ts-expect-error`
  — each one is a potential bug waiting to surface
- **Untyped event handlers**: `(event: any)` in event-driven code is a
  common source of runtime errors
- **env variable access**: Check if env vars are validated at startup or
  accessed inline (the latter causes runtime crashes)
- **Monorepo tools**: `turborepo`, `nx`, `pnpm workspaces`, `lerna` — each
  has its own conventions for shared code and task orchestration
