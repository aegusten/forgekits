---
name: anti-patterns
description: Common mistakes junior devs make — avoid these at all costs
category: _base
tags: [anti-patterns, mistakes, warnings]
complexity: any
---

# Anti-Patterns — What NOT to Generate

## Security Anti-Patterns
- NEVER hardcode secrets, API keys, passwords, or connection strings
- NEVER store passwords in plain text — always hash with bcrypt/argon2
- NEVER use `eval()` or `exec()` with any user input
- NEVER construct SQL with string formatting — use parameterized queries
- NEVER disable CORS entirely (`allow_origins=["*"]`) in production config
- NEVER log sensitive data (passwords, tokens, PII)

## Architecture Anti-Patterns
- NEVER put business logic in route handlers — use the service layer
- NEVER access the database directly from routes — go through services
- NEVER create circular imports between modules
- NEVER use global mutable state (module-level dicts, lists as caches)
- NEVER create a "utils.py" dumping ground — name things by what they do

## Python Anti-Patterns
- NEVER use `except: pass` or `except Exception: pass`
- NEVER use mutable default arguments (`def foo(items=[]): ...`)
- NEVER use `from module import *`
- NEVER ignore type hints — every function gets annotated
- NEVER use `time.sleep()` in async code — use `asyncio.sleep()`

## FastAPI Anti-Patterns
- NEVER use synchronous DB calls in async route handlers
- NEVER return raw SQLAlchemy models from routes — use Pydantic schemas
- NEVER skip input validation — Pydantic handles this, use it
- NEVER create a single `routes.py` with all endpoints — split by resource
- NEVER forget to add response_model to route decorators

## Database Anti-Patterns
- NEVER use `autocommit=True` — explicit transactions always
- NEVER skip `created_at`/`updated_at` timestamps on models
- NEVER use `String` for IDs when `Integer` or `UUID` is appropriate
- NEVER forget to close/dispose database connections on shutdown
