# Analysis Workflow

The full 5-phase process for converting a code repository into structured
knowledge files and a populated MEMORY.md.

## Phase 1: Detect & Orient

Goal: understand what we're working with before diving in.

### 1.1 Run language detection
```bash
python scripts/detect_language.py /path/to/project
```
Read the JSON output. Note:
- `language` — primary language
- `build_system` — how the project builds (npm, cargo, go, pip, etc.)
- `test_cmd` — command to run tests
- `lint_cmd` — command to run linter
- `is_monorepo` — whether this is a monorepo with multiple sub-projects

### 1.2 Read configuration files
Open and scan key config files for runtime details:
- `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` — dependencies
- `tsconfig.json` / `tslint.json` / `.eslintrc.*` — TypeScript/lint config
- `.env.example` / `.env.template` / `config/default.*` — env vars
- `docker-compose.*` / `Dockerfile` — services
- `Makefile` / `Taskfile` — common commands

### 1.3 Check for existing SDD scaffolding
- Does `MEMORY.md` exist at project root? Read it — don't overwrite durable
  knowledge. Merge new findings into existing entries.
- Does `specs/SDD.md` exist? Note it — this skill feeds into SDD.
- Does `specs/index.md` exist? Read for in-progress features that may affect
  analysis (e.g., files touched by active feature work).
- Read `AGENTS.md` or `CLAUDE.md` if present. Follow any project-specific
  instructions.

### 1.4 Load the language strategy
Read `references/languages/<detected>.md`. This tells you:
- Which directories matter most (source, tests, config, docs)
- How to extract symbols using tree-sitter or grep patterns
- Common conventions in this ecosystem
- Gotchas to watch for

## Phase 2: Structural Map

Goal: build the skeleton — where things are, what depends on what.

### 2.1 Generate annotated directory tree
```bash
python scripts/structure_map.py /path/to/project
```
This produces:
- Directory tree with file classifications (source, test, config, doc, generated)
- For source files: extracted symbols (functions, classes, exports, type defs)
- A file-level dependency graph (imports from file A to file B)

### 2.2 Run git analysis
```bash
python scripts/git_analysis.py /path/to/project
```
This produces:
- `hotspots` — most frequently changed files (top 20), with change counts
- `owners` — directory-level ownership from git blame aggregation
- `reverted_commits` — commits that were reverted (signaling past bugs)
- `bug_patterns` — files frequently appearing in revert pairs

### 2.3 Build the mental model
From the output of 2.1 and 2.2, identify:
- **Top-level modules**: the major directories/components visible in the tree
- **Entry points**: `main()`, `index.ts`, `cli.ts`, `server.ts`, `bin/`
- **Module boundaries**: where one component ends and another begins
- **Hot files**: files that change most often (likely business logic or
  unstable code)
- **Quiet files**: files that rarely change (likely stable infrastructure)

Skim the first ~30 lines of each major source file in the top-level
directories. Don't read everything — just enough to classify each module:
"What does this do? API layer? Data access? Business logic? Config?"

## Phase 3: Deep Analysis

Goal: understand the code — data models, APIs, patterns, gotchas.

Work through each domain systematically. Read relevant source files
thoroughly enough to extract knowledge, but don't read every line of every
file. Use grep for targeted exploration, then read specific files fully.

### 3.1 Data models
Search for type/interface/class/schema definitions:
- TypeScript: `grep "interface|type\s+\w+\s*=|class\s+\w+\s*{" --include="*.ts"`
- Python: `grep "class\s+\w+.*BaseModel|dataclass|TypedDict" --include="*.py"`
- Go: `grep "type\s+\w+\s+struct" --include="*.go"`
- Rust: `grep "struct\s+\w+|enum\s+\w+" --include="*.rs"`
- Generic: look for schema files (`.sql`, `*.prisma`, `*.graphql`, `*.proto`)

For each significant entity, read its definition file. Extract:
- Field names and types
- Relationships to other entities
- Validation rules
- Whether it maps to a database table

### 3.2 API surfaces
Find route/endpoint/handler definitions:
- TypeScript: `grep "app\.(get|post|put|delete|patch)|router\.(get|post)"`
- Python: `grep "@app\.(route|get|post)|@router\."`
- Go: `grep "HandleFunc|Handle\("`
- Rust: `grep "#\[(get|post|put|delete|route)"`
- Generic: look for files named `routes`, `handlers`, `controllers`, `endpoints`

For each route group, read the file. Extract:
- HTTP method + path pattern
- Auth/rate-limit middleware applied
- Input validation (what schema is used)
- What the handler does (brief summary)
- Response format

### 3.3 Business logic
Identify service/use-case/logic layer files. These are typically:
- Not route handlers, not data models, not config
- Named `service`, `usecase`, `domain`, `core`, `logic`, `business`
- Contain the "what the application actually does" code

For each major service, read the file. Extract:
- What business operation it performs
- What entities it operates on
- What external services it calls
- Error handling patterns
- Transactional boundaries

### 3.4 Security posture
Search for auth and security patterns:
- `grep "middleware|authenticate|authorize|guard" --include="*.*"`
- `grep "bearer|jwt|session|csrf|helmet|cors|ratelimit|rate.limit"`
- Look for `auth.ts`, `auth.py`, `middleware/auth.*`, `guards/`
- Check `.env.example` for secret-related vars

Extract:
- What auth mechanism is used (JWT, session, OAuth, API key)
- Which middleware chain applies to which routes
- Are there unauthenticated routes? List them.
- Input validation approach (Zod, Pydantic, class-validator, hand-rolled)
- Rate limiting configuration

### 3.5 External dependencies
From config files identified in 1.2, extract:
- Databases: PostgreSQL, MySQL, MongoDB, SQLite, Redis, etc.
- Queues: RabbitMQ, SQS, Kafka, Bull, etc.
- Caches: Redis, Memcached, in-memory
- External APIs: Stripe, SendGrid, AWS services, etc.
- Which SDK/client library is used for each

Note the env vars that configure each dependency.

### 3.6 Conventions
Read ~5-10 representative source files from different parts of the codebase.
Look for patterns:
- **Naming**: camelCase vs snake_case vs PascalCase, file naming, directory
  naming, test file naming (`*.test.ts` vs `*_test.py` vs `test_*.rs`)
- **File organization**: co-located tests vs separate test dirs, feature
  folders vs layered folders (controllers/services/models)
- **Error handling**: try/catch wrapping, error types, HTTP error responses,
  logging calls around errors
- **Configuration**: env var naming convention, feature flag approach,
  config file layering (base → environment overrides)
- **Commit style**: `git log --oneline -30` to see conventional commits,
  prefixes used, ticket references

### 3.7 Gotchas and sharp edges
Search for warning signs:
- `grep "TODO\|FIXME\|HACK\|WORKAROUND\|XXX" --include="*.*"`
- `grep "eslint-disable\|ts-ignore\|noqa\|nolint\|@ts-ignore" --include="*.*"`
- `grep "deprecated\|do not use\|do NOT" -i --include="*.*"`
- Large commented-out blocks of code
- Defensive null/undefined checks (often guarding against past bugs)
- Files with >500 lines (likely doing too much — refactoring candidates)

From git analysis:
- Files involved in reverted commits — these are instability hotspots
- Commits with "fix" / "revert" / "hotfix" / "emergency" in the message

## Phase 4: Knowledge Production

Goal: write the output files.

### 4.1 Create knowledge/ directory structure
Only create directories that will contain files. Don't create empty
directories just to match the template.

### 4.2 Write atomic knowledge files

For each file, read its corresponding template in `references/templates/`
for the exact structure. The general pattern:

1. Start with inline metadata block (Source files, Depends on, etc.)
2. Use wiki-style links for cross-references: `[[knowledge/path/to/file]]`
3. Each file covers exactly ONE concept/component/domain
4. If a concept needs more than ~200 lines, split it into sub-files
5. Use `#tags` to mark knowledge domains (#api, #data, #auth, #build, #infra)

### 4.3 Write knowledge/index.md
Use `references/templates/index.md` as the template. This is the ONLY file
with YAML frontmatter. Include:
- One entry per knowledge file, with link + one-line summary
- Grouped by domain directory
- `last_analyzed` timestamp

### 4.4 Populate MEMORY.md
Either create a new MEMORY.md or merge into existing one. Sections:

- **Tech Gotchas**: Every critical finding from 3.7. Use `⚡` for
  production-breaking items. Tag each with `#tag`. Cite source files.

- **Patterns That Worked**: Conventions from 3.6 that seem intentional and
  consistent. Don't list every convention — focus on the ones that would
  matter to someone building a new feature.

- **Architecture Decisions (ADRs)**: Any intentional design choice visible
  in code (layered architecture, event-driven, CQRS, microservices vs
  monolith). When inferred from code rather than documented, mark as
  `[INFERRED]`.

- **Code Ownership Map**: Top 10 directories by owner, from git analysis.
  Format: `dir/ — @handle or name (percentage of commits)`.

- **Common Bugs / Sharp Edges**: From reverted commits and FIXME patterns.
  Format each as a brief description + source file reference.

- **AI Workflow Rule**: If not present, add: "Always read
  `knowledge/index.md` before starting any feature work."

### 4.5 File creation checklist

Before writing a file, ask:
- Does this concept actually exist in the codebase? (don't create empty files)
- Is this file self-contained and readable in isolation?
- Are the cross-references accurate (paths exist)?

## Phase 5: Validate

Goal: confirm accuracy and surface uncertainties.

### 5.1 Report summary
Tell the user what was created:
```
Created knowledge/ directory with 14 files across 7 domains.
2 critical gotchas flagged in edges/gotchas.md.
4 architecture decisions inferred.
Code ownership map from git history of 847 commits.

3 gaps to resolve — see knowledge/gaps.md.
```

### 5.2 Walk through gaps
Present `gaps.md` to the user. Each gap should be a concrete, answerable
question. Group by blocked domain (e.g., "Blocker for architecture/overview",
"Blocker for data/entities").

### 5.3 Flag inferred items
If you marked anything as `[INFERRED]` (in MEMORY.md or knowledge files),
list them and ask the user to confirm or correct.
