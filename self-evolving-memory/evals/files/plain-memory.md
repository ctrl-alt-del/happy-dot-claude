# MEMORY — Accumulated Project Knowledge

## 🧠 Tech Gotchas

### ⚡ Never call `validateToken()` with a null argument
- **What**: `validateToken(null)` throws an unhandled NullPointerException that crashes the auth middleware
- **Where**: `src/auth/token.ts:42`
- **Why**: The function assumes non-null input. Callers in `middleware/auth.ts:87` pass user input directly.
- **How to avoid**: Always wrap in `if (token != null)` or use `Optional<Token>`. The helper `safeValidate()` in `src/auth/helpers.ts` already does this.

### The rate limiter uses sliding window, not fixed window as documented
- The documentation says fixed window but the implementation at `src/api/rate-limiter.ts:120` uses a sliding window algorithm.
- This means the rate limit is more permissive than expected during burst traffic.

## 🔧 Patterns That Worked

### Use test fixtures from `test/fixtures/` instead of inline test data
Pattern observed across 12 test files. Inline test data causes duplication when API schemas change. The `test/fixtures/` directory provides factory functions that generate valid payloads with optional overrides.

### Wrap all database calls in try/catch with structured error logging
Every service that interacts with the database should follow the error handling pattern in `src/db/errors.ts`. This ensures consistent error responses and prevents unhandled promise rejections.

## 📐 Architecture Decisions

### ADR: Use connection pooling for all database access
**Decision**: All services must use the shared connection pool via `db.getPool()` instead of creating individual connections. **Rationale**: Individual connections exhausted the database's connection limit during load testing.

## 📂 Code Ownership Map
| File | Touched By | Why |
|------|-----------|-----|
| src/auth/ | auth-team | Primary ownership of authentication module |
| src/payments/ | billing-team | Payment processing and webhook handling |

## 🐛 Common Bugs Fixed

### Cache stampede during peak traffic (fixed 2026-06-15)
The user cache TTL was set to 5 seconds, causing cache stampede under load. Fixed by increasing TTL to 60 seconds and adding request coalescing in `src/cache/user-cache.ts`.

### Double-init in test setup causes SQLite state corruption (fixed 2026-06-28)
Calling `init()` twice in test setup corrupts the SQLite in-memory database. Fixed by adding a singleton guard in `test/setup.ts`.

## 📋 Facts

### The billing module depends on Stripe API v2024-06-20
Any billing change must be tested against this specific API version. The Stripe SDK is pinned in `package.json`.
