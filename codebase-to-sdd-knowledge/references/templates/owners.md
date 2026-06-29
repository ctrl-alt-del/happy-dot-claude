# Code Ownership
**Source**: Git history (git blame aggregation)
**Tags**: #ownership #team

## Ownership by directory

Ranked by commit count. Format: `directory/ — @handle or Name (percentage of commits to this directory)`

| Directory | Primary owner | Share | Secondary owner |
|-----------|--------------|-------|-----------------|
| `src/routes/` | @alice | 62% | @bob (21%) |
| `src/models/` | @charlie | 48% | @alice (35%) |
| `src/services/` | @bob | 55% | @diana (30%) |
| `src/lib/` | @diana | 40% | @charlie (35%) |
| `tests/` | @alice | 45% | @bob (28%) |
| `config/` | @charlie | 70% | — |
| `migrations/` | @bob | 50% | @alice (30%) |

## Hotspot files

Files that change most frequently (likely high-churn business logic or
unstable code):

| File | Changes | Last changed | Primary modifier |
|------|---------|-------------|-----------------|
| `src/routes/auth.ts` | 47 | 2026-06-15 | @alice |
| `src/services/payment.ts` | 38 | 2026-06-28 | @bob |
| `src/models/user.ts` | 31 | 2026-06-20 | @charlie |

## Reverted commits (potential bug sources)

| Commit | Date | Files | Author | Reason (from commit message) |
|--------|------|-------|--------|------------------------------|
| `abc1234` | 2026-05-10 | `src/services/payment.ts` | @bob | "Revert: payment processing double-counting" |
| `def5678` | 2026-04-22 | `src/routes/auth.ts`, `src/models/session.ts` | @alice | "Revert: session expiry not enforced" |

## When to ask whom

- Questions about auth/security → @alice
- Questions about payment/transactions → @bob
- Questions about data models → @charlie
- Questions about infrastructure/deployment → @charlie
- Questions about shared utilities → @diana
