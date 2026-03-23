---
name: fastapi-routes
description: FastAPI route handler patterns — thin controllers, proper status codes
category: fastapi
tags: [api, routes, fastapi, endpoints]
complexity: low
---

# FastAPI Route Patterns

## Thin Controller Pattern
Routes do THREE things only:
1. Validate input (Pydantic does this automatically)
2. Call the service layer
3. Return the response

```python
from fastapi import APIRouter, Depends, HTTPException, status

from project.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from project.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=list[TodoResponse])
async def list_todos(
    skip: int = 0,
    limit: int = 100,
    service: TodoService = Depends(),
) -> list[TodoResponse]:
    return await service.list(skip=skip, limit=limit)

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    data: TodoCreate,
    service: TodoService = Depends(),
) -> TodoResponse:
    return await service.create(data)

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    service: TodoService = Depends(),
) -> TodoResponse:
    todo = await service.get_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    data: TodoUpdate,
    service: TodoService = Depends(),
) -> TodoResponse:
    todo = await service.update(todo_id, data)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    service: TodoService = Depends(),
) -> None:
    await service.delete(todo_id)
```

## Status Code Rules
- `200` — GET success, PATCH/PUT success
- `201` — POST that creates a resource
- `204` — DELETE success (no body)
- `400` — Bad request / validation error
- `404` — Resource not found
- `422` — Pydantic validation failure (FastAPI handles this)
- `500` — Never intentionally return this

## Rules
- Always set `response_model` on every route
- Always set `status_code` on POST (201) and DELETE (204)
- Always use `tags` for OpenAPI grouping
- Never put business logic here — delegate to services
