---
name: fastapi-models
description: SQLAlchemy models and Pydantic schemas for FastAPI projects
category: fastapi
tags: [models, schemas, database, sqlalchemy, pydantic]
complexity: low
---

# Models & Schemas

## SQLAlchemy Model Pattern

```python
# src/project/models/base.py
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

```python
# src/project/models/todo.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from project.models.base import Base, TimestampMixin

class Todo(Base, TimestampMixin):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), default=None)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
```

## Pydantic Schema Pattern

```python
# src/project/schemas/todo.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TodoBase(BaseModel):
    title: str
    description: str | None = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

class TodoResponse(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

## Rules
- Models and schemas are SEPARATE — never return ORM models from routes
- Every model gets `created_at` and `updated_at` via TimestampMixin
- Use `Mapped[]` type annotations (SQLAlchemy 2.0+ style)
- Schemas: `Create` for POST, `Update` for PATCH (all fields optional), `Response` for output
- `model_config = ConfigDict(from_attributes=True)` on all response schemas
