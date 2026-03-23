"""ForgeKits — context envelope manager (borrowed from IRIS).

The envelope pattern ensures context flows cleanly between pipeline phases.
Constraints accumulate and are never dropped — this prevents later phases
from violating decisions made by earlier ones.
"""

from __future__ import annotations

from forgekits.models import PhaseEnvelope


class EnvelopeManager:
    """Manages context envelopes across pipeline phases."""

    def __init__(self) -> None:
        self._envelopes: list[PhaseEnvelope] = []
        self._accumulated_constraints: list[str] = []

    def create_envelope(
        self,
        phase_name: str,
        decisions: list[str] | None = None,
        artifacts: list[str] | None = None,
        constraints: list[str] | None = None,
        open_questions: list[str] | None = None,
    ) -> PhaseEnvelope:
        """Create a new envelope for a completed phase."""
        new_constraints = constraints or []
        self._accumulated_constraints.extend(new_constraints)

        envelope = PhaseEnvelope(
            phase_name=phase_name,
            key_decisions=decisions or [],
            artifacts=artifacts or [],
            constraints=list(self._accumulated_constraints),  # copy all accumulated
            open_questions=open_questions or [],
        )
        self._envelopes.append(envelope)
        return envelope

    def get_context_for_next_phase(self) -> str:
        """Build a context string for the next phase's system prompt.

        Includes all accumulated constraints and recent decisions.
        Older envelopes are summarized to save tokens.
        """
        if not self._envelopes:
            return ""

        parts: list[str] = []

        # Always include all constraints
        if self._accumulated_constraints:
            parts.append("## Constraints (MUST follow)")
            for c in self._accumulated_constraints:
                parts.append(f"- {c}")

        # Include last 2 envelopes in detail, summarize older ones
        recent = self._envelopes[-2:]
        older = self._envelopes[:-2]

        if older:
            parts.append("\n## Prior Phases (summary)")
            for env in older:
                parts.append(f"- **{env.phase_name}**: {len(env.artifacts)} files created")

        for env in recent:
            parts.append(f"\n## Phase: {env.phase_name}")
            if env.key_decisions:
                parts.append("**Decisions:**")
                for d in env.key_decisions:
                    parts.append(f"- {d}")
            if env.artifacts:
                parts.append("**Files created:**")
                for a in env.artifacts:
                    parts.append(f"- `{a}`")
            if env.open_questions:
                parts.append("**Open questions:**")
                for q in env.open_questions:
                    parts.append(f"- {q}")

        return "\n".join(parts)

    @property
    def envelopes(self) -> list[PhaseEnvelope]:
        return list(self._envelopes)

    @property
    def all_constraints(self) -> list[str]:
        return list(self._accumulated_constraints)
