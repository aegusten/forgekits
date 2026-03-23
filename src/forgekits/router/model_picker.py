"""ForgeKits — model picker.

Maps task classification to model selection.
Respects user overrides (--model flag) and skill-level model hints.
"""

from __future__ import annotations

from forgekits.models import TaskClassification

# Default mapping: complexity → model
COMPLEXITY_MODEL_MAP: dict[str, str] = {
    "low": "haiku",
    "medium": "sonnet",
    "high": "opus",
}

# Phase-level overrides: some phases always need a stronger model
PHASE_MODEL_OVERRIDES: dict[str, str] = {
    "skeleton": "sonnet",      # project structure matters — don't cheap out
    "data_model": "sonnet",    # schema design needs thought
    "services": "sonnet",      # business logic
    "routes": "haiku",         # mostly mechanical wiring
    "config": "haiku",         # boilerplate
    "documentation": "sonnet", # self-documenting needs quality
    "validation": "haiku",     # syntax checking
}


class ModelPicker:
    """Selects the right model for a task or phase."""

    def __init__(self, user_override: str | None = None) -> None:
        self._user_override = user_override

    def pick_for_task(self, classification: TaskClassification) -> str:
        """Pick the initial model based on task classification."""
        if self._user_override:
            return self._user_override
        return classification.recommended_model

    def pick_for_phase(
        self, phase_name: str, base_model: str, skill_hint: str | None = None
    ) -> str:
        """Pick the model for a specific pipeline phase.

        Priority: user override > skill hint > phase override > base model
        """
        if self._user_override:
            return self._user_override

        if skill_hint:
            return skill_hint

        return PHASE_MODEL_OVERRIDES.get(phase_name, base_model)
