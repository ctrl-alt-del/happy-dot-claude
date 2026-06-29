# Rust Analysis

## Language detection heuristics

The skill auto-detects Rust if the project contains:
- `Cargo.toml` at the root
- `.rs` files in `src/` directory
- `Cargo.lock` file (binary projects) or not (library projects)

## Project type detection

- **Binary**: `src/main.rs` exists, `[[bin]]` in Cargo.toml
- **Library**: `src/lib.rs` exists, no `main.rs`
- **Workspace**: `[workspace]` section in Cargo.toml with `members`
- **Procedural macro**: `[lib] proc-macro = true` in Cargo.toml

## Key directories to analyze

| Directory | What it contains | Priority |
|-----------|-----------------|----------|
| `src/` | All source code | High |
| `src/bin/` | Binary entry points (if multi-bin) | High |
| `src/routes/` or `src/handlers/` | Web handlers | High |
| `src/models/` or `src/entities/` | Domain types, entities | High |
| `src/db/` or `src/repository/` | Database access | High |
| `src/services/` | Business logic | High |
| `src/middleware/` | Auth, logging middleware | Medium |
| `src/config/` | Configuration | Medium |
| `src/error.rs` or `src/errors/` | Error types | High |
| `src/schema.rs` | Diesel schema (if using Diesel ORM) | High |
| `migrations/` | Database migrations (Diesel, sqlx, refinery) | High |
| `tests/` | Integration tests | Low (patterns only) |

## Dependency analysis (from Cargo.toml)

- **Web frameworks**: `actix-web`, `axum`, `rocket`, `warp`, `poem`, `tide`
- **ORM/database**: `diesel`, `sqlx`, `sea-orm`, `mongodb`, `redis`
- **Serialization**: `serde`, `serde_json`, `serde_yaml`
- **Validation**: `validator`, `garde`
- **Async runtime**: `tokio`, `async-std`, `smol`
- **Auth**: `jsonwebtoken`, `oauth2`, `argon2`, `bcrypt`
- **Logging**: `tracing`, `log`, `env_logger`, `slog`
- **HTTP client**: `reqwest`, `hyper`, `ureq`
- **gRPC**: `tonic`, `grpc`
- **CLI**: `clap`, `structopt`, `argh`
- **Testing**: `rstest`, `mockall`, `testcontainers`, `fake`
- **Error handling**: `thiserror`, `anyhow`, `eyre`
- **Migrations**: `refinery`, `diesel_migrations`, `sqlx-cli`
- **Template engine**: `askama`, `tera`, `handlebars`

## Symbol extraction patterns

### Structs and enums
```bash
rg "^(pub\s+)?(struct|enum)\s+\w+" --include="*.rs" --no-heading
```

### Trait definitions
```bash
rg "^(pub\s+)?trait\s+\w+" --include="*.rs" --no-heading
```

### Function definitions
```bash
rg "^(pub\s+)?(async\s+)?fn\s+\w+" --include="*.rs" --no-heading
```

### impl blocks (where logic lives)
```bash
rg "^impl\s+" --include="*.rs" -A2 --no-heading
```

### Route attributes (Axum, Actix)
```bash
rg "#\[(get|post|put|delete|patch|route|head)\(" --include="*.rs" --no-heading
```

### Middleware / layers
```bash
rg "\.layer\(|\.wrap\(|middleware" --include="*.rs" --no-heading
```

### Derive macros (data shapes)
```bash
rg "#\[derive\(" --include="*.rs" --no-heading | head -30
```

### Error type definitions
```bash
rg "#\[derive.*Error\]|enum\s+\w+Error|thiserror|anyhow" --include="*.rs" --no-heading
```

## Common conventions to detect

- **Module organization**: `mod.rs` pattern vs `module.rs` at same level
- **Visibility**: `pub` vs `pub(crate)` vs private — check module boundary
  discipline
- **Error handling**: `thiserror` for library errors, `anyhow` for
  application errors, or custom error enums
- **Async runtime**: Tokio is dominant — check for `#[tokio::main]` or
  `#[tokio::test]`
- **Testing**: `#[cfg(test)] mod tests { ... }` — usually in the same file
  as the code being tested (idiomatic Rust)
- **Trait usage**: Extension traits, From/Into implementations, Display/Debug
- **Builder pattern**: Common in Rust — check for `Builder` structs
- **Type-state pattern**: Using generics/phantom types to encode state at
  compile time
- **Unsafe blocks**: grep for `unsafe` — every one is a potential UB source
- **Panic vs Result**: Check if the codebase uses `.unwrap()` / `.expect()`
  liberally (potential crashes) or returns Results

## Gotchas specific to Rust ecosystems

- **`.unwrap()` / `.expect()` in production code**: Each one is a potential
  panic. Grep for them. Flag any in non-test code as gotchas.
- **`todo!()` / `unimplemented!()`**: Check for these — they panic at
  runtime if reached
- **`unsafe` blocks**: Each `unsafe` is a place where memory safety is the
  programmer's responsibility. Flag all of them. Check if they're
  documented with `// SAFETY:` comments.
- **Blocking in async**: Calling blocking I/O inside an async function on
  a Tokio runtime — grep for `std::thread::sleep`, `std::fs::read` inside
  async functions
- **Clone everywhere**: Excessive `.clone()` calls to satisfy the borrow
  checker instead of proper borrowing — signals performance issues and
  architectural friction
- **Large enum variants**: Enums with one very large variant (e.g., a
  massive error variant alongside small normal ones) — causes stack bloat
  when the enum is moved. Check for `#[allow(clippy::large_enum_variant)]`
- **Cargo feature gates**: Check `[features]` in Cargo.toml — complex
  feature sets can cause cryptic compile errors
- **Compile times**: Large dependency trees, heavy macro usage (syn,
  proc-macro2), and excessive generics — check build times in CI config
