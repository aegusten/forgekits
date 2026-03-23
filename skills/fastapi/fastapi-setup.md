---
name: fastapi-setup
description: FastAPI app factory, lifespan events, middleware, and config
category: fastapi
tags: [api, setup, fastapi, config]
complexity: low
model_hint: sonnet
---

# FastAPI Project Setup

## App Factory Pattern
Always use a factory function to create the FastAPI app:

```python
# src/project/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from project.config import settings
from project.database import engine, Base
from project.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (dev only), init connections
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose connections
    await engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # NOT ["*"] — be explicit
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()
```

## Config Pattern
```python
# src/project/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    app_version: str = "0.1.0"
    database_url: str
    cors_origins: list[str] = ["http://localhost:3000"]
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

## Rules
- Always use lifespan context manager (not deprecated `on_event`)
- Always version the API prefix (`/api/v1/`)
- Always include a `/health` endpoint
- CORS origins must be explicit — never `["*"]` in config defaults
