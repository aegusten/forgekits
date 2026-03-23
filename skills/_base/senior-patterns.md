---
name: senior-patterns
description: Patterns a senior engineer always follows — the quality bar
category: _base
tags: [quality, patterns, best-practices]
complexity: any
---

# Senior Engineering Patterns

## Type Hints Everywhere
- ALL function signatures MUST have type hints (params + return)
- Use `from __future__ import annotations` at the top of every file
- Use modern syntax: `str | None` not `Optional[str]`, `list[str]` not `List[str]`

## Dependency Injection
- Services receive their dependencies via constructor or FastAPI `Depends()`
- No global state — no module-level DB sessions or service instances
- Makes testing trivial: swap real dependencies for mocks

## Configuration
- All config via environment variables
- Use pydantic-settings or a simple dataclass + `os.environ`
- Validate required config at startup — fail fast, not at first request
- `.env.example` is the documentation for what's needed

## Separation of Concerns
- Routes: input validation, HTTP concerns, response formatting
- Services: business logic, orchestration, domain rules
- Models: data structure, relationships, constraints
- Schemas: API contract (what goes in, what comes out)

## Async by Default
- Use `async def` for all route handlers and service methods
- Use async SQLAlchemy sessions (`AsyncSession`)
- Use `asyncio.gather()` for concurrent independent operations

## What NOT to Do
- No business logic in route handlers
- No raw SQL strings with user input (use ORM or parameterized queries)
- No `import *`
- No circular imports (if it happens, your architecture is wrong)
- No god classes or functions over 50 lines
- No hardcoded URLs, ports, or connection strings
