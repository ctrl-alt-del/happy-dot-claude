# Python Analysis

## Language detection heuristics

The skill auto-detects Python if the project contains:
- `pyproject.toml`, `setup.py`, `setup.cfg`, or `requirements.txt`
- `__init__.py` files in source directories
- `.py` files as the dominant source file type
- `venv/`, `.venv/`, `poetry.lock`, or `Pipfile` confirms ecosystem

## Framework detection

After confirming Python, look for framework markers:
- FastAPI: `fastapi` in dependencies, `FastAPI()` instantiation, `@app.get`
- Django: `django` in dependencies, `settings.py`, `manage.py`, `urls.py`
- Flask: `flask` in dependencies, `app = Flask(__name__)`
- SQLAlchemy: `sqlalchemy` in deps, `Base = declarative_base()`
- Pydantic: `pydantic` in deps, `BaseModel` subclassing
- Alembic: `alembic/` directory, `alembic.ini`
- Pytest: `pytest` in dev deps, `conftest.py`
- Celery: `celery` in deps, `@app.task` decorators
- Click / Typer: CLI frameworks, `@app.command()` decorators

## Key directories to analyze

| Directory | What it contains | Priority |
|-----------|-----------------|----------|
| `src/<package>/` or `<package>/` | Primary application code | High |
| `api/` or `routes/` | API route definitions (FastAPI/Flask) | High |
| `models/` | SQLAlchemy/Django ORM models | High |
| `schemas/` | Pydantic schemas, serialization | High |
| `services/` | Business logic layer | High |
| `middleware/` | Auth, logging, CORS middleware | Medium |
| `core/` or `config/` | Application config, settings | Medium |
| `migrations/` or `alembic/versions/` | Database migrations | High |
| `cli/` or `commands/` | CLI entry points | Medium |
| `utils/` or `helpers/` | Utility functions | Low |
| `tasks/` | Celery/background tasks | Medium |
| `tests/` | Test files | Low (patterns only) |

## Dependency analysis

From `pyproject.toml` or `requirements.txt`:
- **Web frameworks**: `fastapi`, `flask`, `django`, `litestar`, `sanic`
- **ORM**: `sqlalchemy`, `django-orm`, `tortoise-orm`, `peewee`
- **Validation**: `pydantic`, `marshmallow`, `cerberus`, `attrs`
- **Async**: `asyncio`, `trio`, `anyio`
- **Task queues**: `celery`, `dramatiq`, `arq`, `huey`
- **Auth**: `python-jose`, `pyjwt`, `passlib`, `bcrypt`
- **Database drivers**: `asyncpg`, `psycopg2`, `aiosqlite`, `pymongo`
- **HTTP clients**: `httpx`, `aiohttp`, `requests`
- **Testing**: `pytest`, `coverage`, `factory-boy`, `faker`
- **Linting**: `ruff`, `black`, `mypy`, `flake8`, `isort`

## Symbol extraction patterns

### Class definitions (models, schemas, services)
```bash
rg "^class\s+\w+.*:" --include="*.py" --no-heading
```

### Pydantic models (data shapes)
```bash
rg "class\s+\w+\(BaseModel\)" --include="*.py" --no-heading
```

### SQLAlchemy models
```bash
rg "class\s+\w+\(Base\)|declarative_base|Column\(" --include="*.py" --no-heading
```

### FastAPI route decorators
```bash
rg "@(app|router)\.(get|post|put|delete|patch)\(" --include="*.py" --no-heading
```

### Function definitions
```bash
rg "^(async\s+)?def\s+\w+\(" --include="*.py" --no-heading
```

### Decorators (auth, caching, middleware)
```bash
rg "^@\w+|^@\w+\.\w+" --include="*.py" -A1 --no-heading | grep "@"
```

### Configuration (settings, env vars)
```bash
rg "os\.(environ|getenv)|settings\.|config\(" --include="*.py" --no-heading | head -30
```

### Exception definitions
```bash
rg "class\s+\w+Error|class\s+\w+Exception" --include="*.py" --no-heading
```

## Common conventions to detect

- **Package naming**: `snake_case` for packages and modules, `PascalCase` for
  classes, `UPPER_CASE` for constants
- **Test naming**: `test_*.py` files, `test_*` functions, `conftest.py` fixtures
- **Import style**: `import package` vs `from package import name`, relative
  vs absolute imports
- **Type hints**: Presence and frequency of type annotations — check if
  `mypy` or `pyright` is configured
- **Async patterns**: `async def` / `await` vs synchronous code
- **Dependency injection**: FastAPI `Depends()`, manual DI containers
- **Error handling**: try/except patterns, sentry/rollbar integration,
  structured logging (structlog, loguru)
- **Configuration**: `pydantic-settings`, `dynaconf`, or manual `os.getenv`

## Gotchas specific to Python ecosystems

- **Mutable default arguments**: `def foo(items=[])` — grep for `def.*=\[\]`
  or `def.*=\{\}` — classic source of bugs
- **Import time side effects**: Code executing at module level (not inside
  functions/classes) — can cause circular imports
- **asyncio mixing**: Mixing sync and async code in the same call chain
  without proper bridging — check for `asyncio.run()` inside async contexts
- **Global state**: Module-level mutable state (`_cache = {}`,
  `_connections = []`) — breaks test isolation
- **Unvalidated env vars**: `os.getenv("KEY")` without defaults or validation
  — crashes in production when env var is missing
- **Monkey patching**: `unittest.mock.patch` or manual attribute replacement
  — signals fragile test design
- **requirements.txt without pins**: Floating version specs (`>=`) without
  a lockfile — causes reproducibility issues
