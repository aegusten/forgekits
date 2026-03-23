"""ForgeKits — pipeline runner.

Executes phases in sequence, passing context via envelopes.
Handles model switching between phases based on the ModelPicker.
"""

from __future__ import annotations

from forgekits.adapters import get_adapter
from forgekits.models import GeneratedFile, TaskClassification, TaskSpec
from forgekits.pipeline.envelope import EnvelopeManager
from forgekits.pipeline.phase import Phase, PhaseResult
from forgekits.router.model_picker import ModelPicker
from forgekits.skills.loader import Skill

# Default phase sequence for a REST API project
DEFAULT_PHASES: list[dict[str, str]] = [
    {
        "name": "skeleton",
        "instruction": (
            "Generate the project skeleton: pyproject.toml, directory structure, "
            "config.py (env-based), database.py (async session), main.py (app factory), "
            ".env.example, .gitignore, Dockerfile (if requested). "
            "NO business logic yet — just the foundation."
        ),
    },
    {
        "name": "data_model",
        "instruction": (
            "Generate SQLAlchemy models and Pydantic schemas for the project. "
            "Include created_at/updated_at timestamps, proper relationships, "
            "and type hints on everything."
        ),
    },
    {
        "name": "services",
        "instruction": (
            "Generate the service layer — all business logic lives here. "
            "Each service gets its own file. Proper error handling, async operations, "
            "no raw SQL, no business logic in routes."
        ),
    },
    {
        "name": "routes",
        "instruction": (
            "Generate API route handlers. Thin controllers that validate input, "
            "call the service layer, and return responses. Proper status codes, "
            "input validation via Pydantic, error responses."
        ),
    },
    {
        "name": "wiring",
        "instruction": (
            "Wire everything together: register routers in main.py, set up CORS, "
            "configure lifespan events for DB startup/shutdown, add health check endpoint."
        ),
    },
    {
        "name": "documentation",
        "instruction": (
            "Generate DECISIONS.md (why each architectural choice was made), "
            "README.md (setup instructions, API endpoints, project structure), "
            "and a CLAUDE.md (so the developer gets AI help after scaffolding)."
        ),
    },
]


class PipelineRunner:
    """Runs the generation pipeline phase by phase."""

    def __init__(
        self,
        provider_name: str,
        model_picker: ModelPicker,
        classification: TaskClassification,
        skills: list[Skill],
        verbose: bool = False,
    ) -> None:
        self._provider_name = provider_name
        self._model_picker = model_picker
        self._classification = classification
        self._skills = skills
        self._verbose = verbose
        self._envelope_mgr = EnvelopeManager()

    async def run(self, spec: TaskSpec) -> tuple[list[GeneratedFile], list[str]]:
        """Execute all phases and return (files, decisions)."""
        all_files: list[GeneratedFile] = []
        all_decisions: list[str] = []
        base_model = self._model_picker.pick_for_task(self._classification)

        # Build combined skills content
        skills_content = self._build_skills_content()

        phases = self._select_phases(spec)

        for phase_def in phases:
            phase_name = phase_def["name"]

            # Pick model for this phase (may differ from base)
            skill_hint = self._get_skill_hint_for_phase(phase_name)
            model = self._model_picker.pick_for_phase(phase_name, base_model, skill_hint)

            # Create adapter with phase-specific model
            adapter = get_adapter(self._provider_name, model)

            # Build phase context from envelopes
            envelope_context = self._envelope_mgr.get_context_for_next_phase()

            # Enrich instruction with task spec details
            instruction = self._enrich_instruction(phase_def["instruction"], spec)

            # Execute phase
            phase = Phase(name=phase_name, adapter=adapter, instruction=instruction)
            result: PhaseResult = await phase.execute(skills_content, envelope_context)

            # Record envelope for next phase
            self._envelope_mgr.create_envelope(
                phase_name=phase_name,
                decisions=result.decisions,
                artifacts=[f.path for f in result.files],
                constraints=result.constraints,
                open_questions=result.open_questions,
            )

            all_files.extend(result.files)
            all_decisions.extend(result.decisions)

        return all_files, all_decisions

    def _build_skills_content(self) -> str:
        """Combine all selected skills into a single context string."""
        if not self._skills:
            return ""
        parts = []
        for skill in self._skills:
            parts.append(f"## Skill: {skill.name}\n{skill.content}")
        return "\n\n---\n\n".join(parts)

    def _select_phases(self, spec: TaskSpec) -> list[dict[str, str]]:
        """Select which phases to run based on the task spec."""
        phases = list(DEFAULT_PHASES)

        # Skip Docker phase content if not needed (handled in skeleton instruction)
        # Add auth phase if needed
        if spec.needs_auth:
            auth_phase = {
                "name": "auth",
                "instruction": (
                    "Generate authentication: JWT token creation/validation, "
                    "password hashing with bcrypt, auth middleware, "
                    "login/register endpoints, user model if not already created. "
                    "Use python-jose for JWT, passlib for hashing."
                ),
            }
            # Insert after services, before routes
            routes_idx = next(
                (i for i, p in enumerate(phases) if p["name"] == "routes"), len(phases)
            )
            phases.insert(routes_idx, auth_phase)

        return phases

    def _enrich_instruction(self, instruction: str, spec: TaskSpec) -> str:
        """Add task-specific context to a phase instruction."""
        parts = [instruction, f"\nProject description: {spec.description}"]
        parts.append(f"Framework: {spec.framework}")
        parts.append(f"Database: {spec.database}")
        if not spec.needs_docker:
            parts.append("Docker: NOT requested — skip Dockerfile and docker-compose.")
        return "\n".join(parts)

    def _get_skill_hint_for_phase(self, phase_name: str) -> str | None:
        """Check if any loaded skill has a model hint relevant to this phase."""
        phase_category_map = {
            "skeleton": "general",
            "data_model": "sqlalchemy",
            "services": "general",
            "routes": "fastapi",
            "auth": "fastapi",
            "wiring": "fastapi",
            "documentation": "general",
        }
        target_category = phase_category_map.get(phase_name)
        if not target_category:
            return None

        for skill in self._skills:
            if skill.category == target_category and skill.model_hint:
                return skill.model_hint
        return None

    @property
    def envelopes(self) -> list:
        return self._envelope_mgr.envelopes
