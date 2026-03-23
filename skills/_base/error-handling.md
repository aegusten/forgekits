---
name: error-handling
description: Proper error handling patterns — no silent failures
category: _base
tags: [errors, exceptions, resilience]
complexity: any
---

# Error Handling

## Rules
- NEVER use bare `except: pass` — always catch specific exceptions
- NEVER silently swallow errors — log them at minimum
- Custom exceptions for domain errors (e.g. `UserNotFoundError`)
- HTTP exceptions belong in routes ONLY — services raise domain exceptions
- Always return meaningful error messages to the API consumer

## Pattern: Domain Exceptions

```python
# src/project/exceptions.py
class AppError(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str | int) -> None:
        super().__init__(f"{resource} with id '{id}' not found", "NOT_FOUND")

class ValidationError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "VALIDATION_ERROR")
```

## Pattern: Route-Level Error Handling

```python
# In routes — translate domain exceptions to HTTP responses
@router.get("/{item_id}")
async def get_item(item_id: int, service: ItemService = Depends()):
    try:
        return await service.get_by_id(item_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
```

## Anti-Patterns to AVOID
- `except Exception: pass`
- Returning `None` instead of raising on not-found
- Catching exceptions just to re-raise them unchanged
- Generic "Something went wrong" messages without error codes
