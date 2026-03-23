"""ForgeKits — shared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TaskSpec:
    """What the user wants to build — output of Layer 1."""

    description: str
    framework: str = "fastapi"
    database: str = "sqlite"
    needs_auth: bool = False
    needs_docker: bool = True
    source_file: Path | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskClassification:
    """How the Brain categorizes a task — output of the classifier."""

    complexity: str  # "low", "medium", "high"
    components: list[str] = field(default_factory=list)  # ["models", "routes", "schemas", ...]
    skills_needed: list[str] = field(default_factory=list)  # skill file names to load
    recommended_model: str = "sonnet"  # "haiku", "sonnet", "opus"


@dataclass
class GeneratedFile:
    """A single file to be written — output of a pipeline phase."""

    path: str  # relative path within the project (e.g. "src/models/todo.py")
    content: str
    description: str = ""  # why this file exists — used in DECISIONS.md


@dataclass
class PhaseEnvelope:
    """Context passed between pipeline phases — borrowed from IRIS.

    Constraints accumulate across phases and are never dropped.
    Older decisions/artifacts can be summarized to save tokens.
    """

    phase_name: str
    key_decisions: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)  # file paths produced
    constraints: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)


@dataclass
class ForgeResult:
    """Final output of the orchestrator."""

    success: bool
    file_count: int = 0
    files: list[GeneratedFile] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    error: str | None = None
    envelopes: list[PhaseEnvelope] = field(default_factory=list)
