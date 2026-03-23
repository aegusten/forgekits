"""ForgeKits — task complexity classifier.

Analyzes a TaskSpec and produces a TaskClassification.
Uses a fast/cheap LLM call to classify before the heavy generation begins.
"""

from __future__ import annotations

import json

from forgekits.adapters.base import LLMAdapter, LLMMessage
from forgekits.models import TaskClassification, TaskSpec

CLASSIFIER_SYSTEM_PROMPT = """\
You are a task classifier for an AI code scaffolder. Given a project description,
analyze it and return a JSON object with:

{
  "complexity": "low" | "medium" | "high",
  "components": ["list", "of", "needed", "components"],
  "skills_needed": ["skill-names", "to-load"],
  "recommended_model": "haiku" | "sonnet" | "opus"
}

Complexity guide:
- low: single resource CRUD, no auth, simple scripts (→ haiku or sonnet)
- medium: multiple resources, relationships, auth, background tasks (→ sonnet)
- high: complex architecture, real-time, multi-service, advanced patterns (→ opus)

Components are the parts of the project: models, schemas, routes, services, config,
database, auth, middleware, tests, docker, migrations, celery, websockets, etc.

Skills map to our skill files:
- fastapi-setup, fastapi-routes, fastapi-models, fastapi-auth
- sqlalchemy-models, sqlalchemy-async-session, sqlalchemy-migrations
- error-handling, project-structure, senior-patterns, anti-patterns
- cookiecutter-templates

Return ONLY valid JSON, no markdown fences, no explanation.
"""


class TaskClassifier:
    """Classifies task complexity and selects skills/model."""

    def __init__(self, adapter: LLMAdapter) -> None:
        self._adapter = adapter

    async def classify(self, spec: TaskSpec) -> TaskClassification:
        """Analyze a task spec and return classification."""
        user_prompt = self._build_prompt(spec)

        response = await self._adapter.generate(
            messages=[LLMMessage(role="user", content=user_prompt)],
            system=CLASSIFIER_SYSTEM_PROMPT,
            temperature=0.1,  # deterministic classification
            max_tokens=512,
        )

        return self._parse_response(response.content)

    def _build_prompt(self, spec: TaskSpec) -> str:
        parts = [f"Project: {spec.description}"]
        if spec.framework != "fastapi":
            parts.append(f"Framework: {spec.framework}")
        if spec.database != "sqlite":
            parts.append(f"Database: {spec.database}")
        if spec.needs_auth:
            parts.append("Requires authentication")
        if spec.needs_docker:
            parts.append("Include Docker setup")
        return "\n".join(parts)

    def _parse_response(self, content: str) -> TaskClassification:
        """Parse the LLM's JSON response into a TaskClassification."""
        try:
            # Strip markdown fences if the model added them anyway
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            return TaskClassification(
                complexity=data.get("complexity", "medium"),
                components=data.get("components", []),
                skills_needed=data.get("skills_needed", []),
                recommended_model=data.get("recommended_model", "sonnet"),
            )
        except (json.JSONDecodeError, KeyError):
            # Fallback to safe defaults
            return TaskClassification(
                complexity="medium",
                components=["models", "schemas", "routes", "services", "config"],
                skills_needed=["fastapi-setup", "error-handling", "project-structure"],
                recommended_model="sonnet",
            )
