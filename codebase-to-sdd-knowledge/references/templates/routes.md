# API Routes
**Source files**: `src/routes/auth.ts`, `src/routes/users.ts`, `src/routes/projects.ts`
**Depends on**: [[knowledge/data/entities]], [[knowledge/security/auth-model]]
**Depended on by**: [[knowledge/architecture/components]]
**Tags**: #api #routes

## Route groups

### Auth (`src/routes/auth.ts`)

| Method | Path | Auth | Validation | Handler | Purpose |
|--------|------|------|-----------|---------|---------|
| POST | `/auth/login` | None | `loginSchema` | `loginHandler` | Authenticate user, return JWT |
| POST | `/auth/register` | None | `registerSchema` | `registerHandler` | Create new user account |
| POST | `/auth/refresh` | None | `refreshSchema` | `refreshHandler` | Refresh access token |
| POST | `/auth/logout` | Required | None | `logoutHandler` | Invalidate session |

### Users (`src/routes/users.ts`)

| Method | Path | Auth | Validation | Handler | Purpose |
|--------|------|------|-----------|---------|---------|
| GET | `/users/me` | Required | None | `getCurrentUser` | Get current user profile |
| PATCH | `/users/me` | Required | `updateUserSchema` | `updateCurrentUser` | Update current user |
| GET | `/users/:id` | Required | UUID param | `getUserById` | Get user by ID (admin only) |

## Global middleware

| Middleware | Source | Applied to |
|-----------|--------|-----------|
| CORS | `src/middleware/cors.ts` | All routes |
| Rate limiter | `src/middleware/rate-limit.ts` | All routes (100 req/15min) |
| Auth guard | `src/middleware/auth.ts` | Routes marked "Required" |
| Request logging | `src/middleware/logger.ts` | All routes |
| Error handler | `src/middleware/error-handler.ts` | All routes (global catch) |

## Authentication flow

Describe how authentication works:
- Token type: JWT (access token + refresh token)
- Token location: `Authorization: Bearer <token>` header
- Token expiry: Access 15 min, Refresh 7 days
- Session storage: Redis (key: `session:<userId>`, TTL: 7 days)

## Standard response format

```json
{
  "data": { ... },
  "error": null,
  "meta": { "page": 1, "limit": 20, "total": 100 }
}
```

## Error response format

```json
{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [{ "field": "email", "message": "Required" }]
  }
}
```
