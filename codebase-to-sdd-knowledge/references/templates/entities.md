# Data Entities
**Source files**: `src/models/user.ts`, `src/models/session.ts`, `prisma/schema.prisma`
**Depended on by**: [[knowledge/apis/routes]], [[knowledge/architecture/components]], [[knowledge/conventions/testing]]
**Tags**: #data #entities

## Entity list

| Entity | Source | Persisted in |
|--------|--------|-------------|
| User | `src/models/user.ts:10` | `users` table |
| Session | `src/models/session.ts:5` | `sessions` table |

## Entity details

### User
```typescript
// src/models/user.ts:10
interface User {
  id: string;
  email: string;
  name: string | null;
  role: 'admin' | 'user';
  createdAt: Date;
  updatedAt: Date;
}
```
- **Purpose**: Represents an authenticated user
- **Relationships**: Has many Sessions, belongs to one Organization
- **Validation**: Email must be unique (enforced at DB and application level)
- **Lifecycle**: Created on signup, soft-deleted (has `deletedAt` field)

### Session
[repeat for each entity]

## Entity relationship diagram (approximate)

```
User 1──N Session
User N──1 Organization
Organization 1──N Project
Project 1──N Task
```

## Database

- **Engine**: PostgreSQL 16
- **ORM/migration tool**: Prisma 5
- **Migrations location**: `prisma/migrations/`
- **Seeds location**: `prisma/seed.ts`
- **Connection config**: `DATABASE_URL` env var (see [[knowledge/conventions/configuration]])
