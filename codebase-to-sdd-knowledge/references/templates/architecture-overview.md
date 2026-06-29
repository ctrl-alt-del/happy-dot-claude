# Architecture Overview
**Source files**: [list key config files and entry points]
**Depended on by**: [[knowledge/architecture/components]]
**Tags**: #architecture

## What it is

Brief description of the overall system architecture. What does this project
build? Is it a web server, a CLI tool, a library, a mobile app?

## Architecture style

- **Style**: e.g., layered, hexagonal/ports-and-adapters, microservices,
  monolith, event-driven, CQRS
- **Justification** [INFERRED from code structure]: Why this style appears
  to have been chosen

## Technology stack

| Layer | Technology |
|-------|-----------|
| Runtime | e.g., Node.js 20, Python 3.12, Go 1.22 |
| Framework | e.g., Next.js 14, FastAPI, Axum |
| Database | e.g., PostgreSQL 16, MongoDB 7 |
| Cache | e.g., Redis 7 |
| Queue | e.g., RabbitMQ, Bull, Celery |
| File storage | e.g., S3, MinIO, local disk |

## Project structure at a glance

```
project/
├── src/            — primary source code
│   ├── routes/     — API endpoint definitions
│   ├── models/     — data models and types
│   ├── services/   — business logic
│   └── lib/        — shared utilities
├── tests/          — test suite
├── config/         — configuration files
└── docs/           — documentation
```

## Build and run

| Command | Purpose |
|---------|---------|
| `...` | Install dependencies |
| `...` | Run development server |
| `...` | Run tests |
| `...` | Build for production |
| `...` | Lint |
