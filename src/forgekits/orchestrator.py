"""ForgeKits — Layer 2: Orchestrator.

The brain. Connects CLI input → classification → skill loading →
pipeline execution → file writing → validation → output.

This is the only module that touches all three layers.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from rich.console import Console

from forgekits.adapters import get_adapter
from forgekits.generator.validator import OutputValidator
from forgekits.generator.writer import ProjectWriter
from forgekits.models import ForgeResult, TaskSpec
from forgekits.pipeline.runner import PipelineRunner
from forgekits.router.classifier import TaskClassifier
from forgekits.router.model_picker import ModelPicker
from forgekits.skills.loader import SkillLoader

console = Console()

# Resolve skills directory relative to the package root
SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / "skills"


class Orchestrator:
    """Connects all layers and runs the forge pipeline."""

    def __init__(
        self,
        provider_name: str = "anthropic",
        model_override: str | None = None,
        verbose: bool = False,
        skills_dir: Path | None = None,
    ) -> None:
        self._provider_name = provider_name
        self._model_override = model_override
        self._verbose = verbose
        self._skills_dir = skills_dir or SKILLS_DIR

    def forge(self, spec: TaskSpec, output_dir: Path) -> ForgeResult:
        """Main entry point — synchronous wrapper around async pipeline."""
        return asyncio.run(self._forge_async(spec, output_dir))

    async def _forge_async(self, spec: TaskSpec, output_dir: Path) -> ForgeResult:
        """The full forge flow."""
        try:
            # Step 1: Classify the task
            console.print("[dim]Analyzing task...[/dim]")
            classifier_adapter = get_adapter(self._provider_name, "haiku")
            classifier = TaskClassifier(classifier_adapter)
            classification = await classifier.classify(spec)

            if self._verbose:
                console.print(f"[dim]Complexity: {classification.complexity}[/dim]")
                console.print(f"[dim]Components: {', '.join(classification.components)}[/dim]")
                console.print(f"[dim]Model: {classification.recommended_model}[/dim]")

            # Step 2: Load skills
            console.print("[dim]Loading skills...[/dim]")
            skill_loader = SkillLoader(self._skills_dir)
            skills = skill_loader.select_for_task(
                tags=classification.components,
                complexity=classification.complexity,
                framework=spec.framework,
            )
            if self._verbose:
                console.print(f"[dim]Skills loaded: {', '.join(s.name for s in skills)}[/dim]")

            # Step 3: Pick model
            model_picker = ModelPicker(user_override=self._model_override)

            # Step 4: Run pipeline
            console.print("[bold]Forging project...[/bold]")
            runner = PipelineRunner(
                provider_name=self._provider_name,
                model_picker=model_picker,
                classification=classification,
                skills=skills,
                verbose=self._verbose,
            )
            files, decisions = await runner.run(spec)

            if not files:
                return ForgeResult(success=False, error="Pipeline produced no files")

            # Step 5: Validate
            console.print("[dim]Validating output...[/dim]")
            validator = OutputValidator()
            validation = validator.validate(files)

            if validation.errors:
                console.print("[yellow]Validation warnings:[/yellow]")
                for err in validation.errors:
                    console.print(f"  [red]✗[/red] {err}")

            if validation.warnings:
                for warn in validation.warnings:
                    console.print(f"  [yellow]![/yellow] {warn}")

            # Step 6: Write to disk
            console.print("[dim]Writing files...[/dim]")
            writer = ProjectWriter(output_dir)
            file_count = writer.write_all(files)
            writer.write_decisions(decisions, runner.envelopes)

            return ForgeResult(
                success=True,
                file_count=file_count + 1,  # +1 for DECISIONS.md
                files=files,
                decisions=decisions,
                envelopes=runner.envelopes,
            )

        except Exception as e:
            return ForgeResult(success=False, error=str(e))
