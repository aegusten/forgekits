"""ForgeKits — single pipeline phase.

Each phase generates a specific part of the project (skeleton, models, routes, etc.).
Phases receive context from prior phases via envelopes and produce GeneratedFiles.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from forgekits.adapters.base import LLMAdapter, LLMMessage
from forgekits.models import GeneratedFile


@dataclass
class PhaseResult:
    """Output of a single pipeline phase."""

    files: list[GeneratedFile] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    tokens_used: int = 0


PHASE_SYSTEM_TEMPLATE = """\
You are a senior Python engineer generating production-quality code for a project.

## Your Task
Generate the {phase_name} phase of the project.

## Skills & Patterns to Follow
{skills_content}

## Context from Prior Phases
{envelope_context}

## Output Format
Return a JSON array of files to create. Each file has:
- "path": relative file path (e.g. "src/models/todo.py")
- "content": the full file content
- "description": one-line explanation of why this file exists

Also include:
- "decisions": list of architectural decisions made in this phase
- "constraints": list of constraints the next phase must follow
- "open_questions": list of unresolved questions (if any)

Return ONLY valid JSON with this structure:
{{
  "files": [...],
  "decisions": [...],
  "constraints": [...],
  "open_questions": [...]
}}
"""


class Phase:
    """Executes a single generation phase."""

    def __init__(
        self,
        name: str,
        adapter: LLMAdapter,
        instruction: str,
    ) -> None:
        self.name = name
        self._adapter = adapter
        self._instruction = instruction

    async def execute(
        self,
        skills_content: str,
        envelope_context: str,
    ) -> PhaseResult:
        """Run this phase and return generated files."""
        system = PHASE_SYSTEM_TEMPLATE.format(
            phase_name=self.name,
            skills_content=skills_content or "(no specific skills for this phase)",
            envelope_context=envelope_context or "(first phase — no prior context)",
        )

        response = await self._adapter.generate(
            messages=[LLMMessage(role="user", content=self._instruction)],
            system=system,
            max_tokens=8192,
        )

        result = self._parse_response(response.content)
        result.tokens_used = response.input_tokens + response.output_tokens
        return result

    def _parse_response(self, content: str) -> PhaseResult:
        """Parse the LLM's JSON response into a PhaseResult."""
        try:
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)

            files = [
                GeneratedFile(
                    path=f["path"],
                    content=f["content"],
                    description=f.get("description", ""),
                )
                for f in data.get("files", [])
            ]

            return PhaseResult(
                files=files,
                decisions=data.get("decisions", []),
                constraints=data.get("constraints", []),
                open_questions=data.get("open_questions", []),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return PhaseResult(
                decisions=[f"Phase {self.name} returned unparseable output"],
                open_questions=["Manual review needed — LLM output was not valid JSON"],
            )
