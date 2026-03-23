"""ForgeKits — skill loader.

Reads markdown files with YAML frontmatter from the skills/ directory.
Skills are the product — curated senior-level knowledge that shapes the agent's output.

Skill format (compatible with IRIS SKILL.md pattern):
---
name: fastapi-setup
description: How to properly set up a FastAPI project
category: fastapi
tags: [api, setup, structure]
complexity: low  # when to use: low/medium/high tasks
model_hint: sonnet  # suggested model for this skill's work
---

# FastAPI Project Setup
[markdown content — instructions, patterns, anti-patterns]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import frontmatter


@dataclass
class Skill:
    """A loaded skill — parsed from a markdown file."""

    name: str
    description: str
    content: str  # the markdown body (instructions for the LLM)
    category: str = "general"
    tags: list[str] = field(default_factory=list)
    complexity: str = "any"  # "low", "medium", "high", "any"
    model_hint: str | None = None
    file_path: Path | None = None

    def matches_task(self, task_tags: list[str], task_complexity: str) -> bool:
        """Check if this skill is relevant to a given task."""
        # Base skills (complexity=any) always match
        if self.complexity == "any":
            return True

        # Check tag overlap
        tag_match = bool(set(self.tags) & set(task_tags))

        # Check complexity compatibility
        complexity_order = {"low": 1, "medium": 2, "high": 3}
        skill_level = complexity_order.get(self.complexity, 0)
        task_level = complexity_order.get(task_complexity, 2)
        complexity_match = skill_level <= task_level

        return tag_match or complexity_match


class SkillLoader:
    """Loads and indexes skills from a directory of markdown files."""

    def __init__(self, skills_dir: Path) -> None:
        self._skills_dir = skills_dir
        self._skills: dict[str, Skill] = {}
        self._loaded = False

    def load_all(self) -> None:
        """Scan the skills directory and load all .md files."""
        if not self._skills_dir.exists():
            return

        for md_file in self._skills_dir.rglob("*.md"):
            # Skip meta/documentation files
            if md_file.name.startswith("_") and md_file.parent.name == "_meta":
                continue

            skill = self._parse_skill(md_file)
            if skill:
                self._skills[skill.name] = skill

        self._loaded = True

    def _parse_skill(self, path: Path) -> Skill | None:
        """Parse a single skill markdown file."""
        try:
            post = frontmatter.load(str(path))
        except Exception:
            return None

        meta = post.metadata
        if not meta.get("name"):
            # Use filename as fallback
            meta["name"] = path.stem

        return Skill(
            name=meta.get("name", path.stem),
            description=meta.get("description", ""),
            content=post.content,
            category=meta.get("category", path.parent.name),
            tags=meta.get("tags", []),
            complexity=meta.get("complexity", "any"),
            model_hint=meta.get("model_hint"),
            file_path=path,
        )

    def get_base_skills(self) -> list[Skill]:
        """Return skills from _base/ — always loaded regardless of task."""
        self._ensure_loaded()
        return [s for s in self._skills.values() if s.category == "_base"]

    def select_for_task(
        self, tags: list[str], complexity: str, framework: str | None = None
    ) -> list[Skill]:
        """Select relevant skills for a task.

        Always includes _base skills, plus framework and task-matched skills.
        """
        self._ensure_loaded()

        selected: list[Skill] = []

        # Always include base skills
        selected.extend(self.get_base_skills())

        # Include framework-specific skills
        if framework:
            selected.extend(
                s for s in self._skills.values()
                if s.category == framework and s not in selected
            )

        # Include task-matched skills
        selected.extend(
            s for s in self._skills.values()
            if s.matches_task(tags, complexity) and s not in selected
        )

        return selected

    def get_skill(self, name: str) -> Skill | None:
        """Get a specific skill by name."""
        self._ensure_loaded()
        return self._skills.get(name)

    def list_skills(self) -> list[Skill]:
        """Return all loaded skills."""
        self._ensure_loaded()
        return list(self._skills.values())

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load_all()
