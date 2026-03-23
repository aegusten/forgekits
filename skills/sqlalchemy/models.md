---
name: sqlalchemy-models
description: SQLAlchemy 2.0+ async model patterns with proper typing
category: sqlalchemy
tags: [database, models, sqlalchemy, async]
complexity: low
---

# SQLAlchemy Async Patterns

## Database Setup
```python
# src/project/database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from project.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Rules
- Always use `AsyncSession` — no sync sessions in async apps
- Always use `expire_on_commit=False` to avoid lazy loading issues
- Always use `mapped_column()` (SQLAlchemy 2.0+), not `Column()`
- Always use `Mapped[type]` annotations, not bare `Column` types
- Session management via FastAPI `Depends(get_db)` — never create sessions manually
- Commit in the dependency, not in the service — single transaction per request

## Relationship Pattern
```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    todos: Mapped[list["Todo"]] = relationship(back_populates="owner")

class Todo(Base, TimestampMixin):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="todos")
```
