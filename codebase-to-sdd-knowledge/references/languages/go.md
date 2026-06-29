# Go Analysis

## Language detection heuristics

The skill auto-detects Go if the project contains:
- `go.mod` at the root
- `.go` files as the dominant source file type
- `go.sum` file

## Key directories to analyze

| Directory | What it contains | Priority |
|-----------|-----------------|----------|
| `cmd/` | CLI entry points (one subdir per binary) | High |
| `internal/` | Private application code | High |
| `pkg/` | Public library code | High |
| `api/` or `proto/` | API definitions (protobuf, OpenAPI) | High |
| `handler/` or `handler/` | HTTP/gRPC handlers | High |
| `service/` | Business logic | High |
| `repository/` or `store/` | Data access layer | High |
| `model/` or `domain/` | Domain types and entities | High |
| `middleware/` | Auth, logging, CORS middleware | Medium |
| `config/` | Configuration loading | Medium |
| `migrations/` | Database migrations | Medium |
| `mocks/` | Generated mocks | Low |

## Dependency analysis (from go.mod)

Go modules use semantic import paths. Key patterns:
- `require` block: direct dependencies
- `// indirect` comments: transitive dependencies
- `replace` directives: local overrides or forks
- Framework markers:
  - `github.com/gin-gonic/gin` — Gin web framework
  - `github.com/labstack/echo` — Echo framework
  - `github.com/go-chi/chi` — Chi router
  - `github.com/gorilla/mux` — Gorilla Mux
  - `google.golang.org/grpc` — gRPC
  - `github.com/jmoiron/sqlx` or `database/sql` — database access
  - `github.com/redis/go-redis` — Redis
  - `go.uber.org/zap` or `log/slog` — structured logging
  - `github.com/testcontainers` — integration testing

## Symbol extraction patterns

### Struct definitions
```bash
rg "^type\s+\w+\s+struct\s*\{" --include="*.go" --no-heading
```

### Interface definitions
```bash
rg "^type\s+\w+\s+interface\s*\{" --include="*.go" --no-heading
```

### Function definitions
```bash
rg "^func\s+(\(\w+\s+\*?\w+\)\s+)?\w+\(" --include="*.go" --no-heading
```

### HTTP handler registration
```bash
rg "\.(GET|POST|PUT|DELETE|PATCH|HandleFunc|Handle)\(" --include="*.go" --no-heading
```

### Middleware
```bash
rg "middleware|\.Use\(|\.Group\(" --include="*.go" --no-heading
```

### Error definitions
```bash
rg "errors\.New|fmt\.Errorf|errors\.As|errors\.Is" --include="*.go" --no-heading
```

## Common conventions to detect

- **Package naming**: Short, lowercase, single-word package names. No
  underscores or camelCase in package names.
- **Project layout**: Standard Go project layout (`cmd/`, `internal/`,
  `pkg/`) vs flat structure
- **Error handling**: `if err != nil` patterns, wrapping with `fmt.Errorf`,
  sentinel errors (`var ErrX = errors.New(...)`)
- **Context propagation**: `context.Context` as first parameter to functions
- **Logging**: Structured logging (slog, zap, zerolog) vs `log` package
- **Testing**: `_test.go` files, table-driven tests, `testify` usage
- **Code generation**: `//go:generate` comments, generated files (`*.gen.go`,
  `*_string.go`)
- **Wire/DI**: `github.com/google/wire` dependency injection
- **Migration tools**: `golang-migrate`, `goose`, `atlas`

## Gotchas specific to Go ecosystems

- **nil interface vs nil pointer**: An interface holding a nil pointer is not
  nil — `var x *T = nil; var i interface{} = x; i == nil` is `false`.
  Check for interface returns that can hold typed nils.
- **Defer in loops**: `defer` in a `for` loop defers until function return,
  not iteration end — resource leaks
- **Goroutine leaks**: Unbounded goroutine creation without context
  cancellation — check for `go func()` without corresponding `ctx.Done()`
  or `sync.WaitGroup`
- **Slice append aliasing**: `append` may or may not create a new backing
  array — mutations can silently share state
- **Zero-value vs unset**: `time.Time{}` (zero value) is valid but not
  meaningfully different from an unset time — use pointers or
  `sql.NullTime` for nullable timestamps
- **Error wrapping**: `fmt.Errorf("context: %w", err)` preserves the
  original error for `errors.Is`/`errors.As`; `%v` does not — grep for
  `fmt.Errorf` to check wrapping style
- **Shadowed variables**: `:=` in inner scope creating a new variable with
  the same name — golangci-lint catches this, check if it's configured
- **Generics**: Newer Go (1.18+) — check if the project uses generics (type
  parameters) or still uses `interface{}` patterns
