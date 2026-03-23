---
name: project-structure
description: Senior-level Python project structure and file organization
category: _base
tags: [structure, organization, setup]
complexity: any
---

# Project Structure

## Directory Layout
Every generated project MUST follow this structure:

```
project-name/
├── src/
│   └── project_name/       # main package (underscore, not hyphen)
│       ├── __init__.py
│       ├── main.py          # app factory / entry point
│       ├── config.py         # all configuration via env vars
│       ├── database.py       # DB connection, session factory
│       ├── models/           # SQLAlchemy models
│       ├── schemas/          # Pydantic schemas (request/response)
│       ├── services/         # business logic (one per domain)
│       ├── routes/           # API route handlers (thin controllers)
│       └── middleware/       # custom middleware (if needed)
├── tests/
│   ├── conftest.py
│   └── test_*.py
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
├── DECISIONS.md
└── CLAUDE.md
```

## Rules
- Package name uses underscores: `my_project`, not `my-project`
- `src/` layout to avoid import confusion
- No `app.py` in root — entry point is `src/package/main.py`
- Config MUST use environment variables — never hardcode values
- `.env.example` lists ALL required env vars with placeholder values
- `.gitignore` MUST include: `.env`, `__pycache__/`, `.venv/`, `*.pyc`
