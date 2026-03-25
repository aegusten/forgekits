"""ForgeKits CLI — Layer 1: Interface."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Load .env from the forgekits project root (if present)
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

from forgekits.adapters.registry import resolve_provider
from forgekits.models import TaskSpec
from forgekits.orchestrator import Orchestrator

app = typer.Typer(
    name="forgekits",
    help="AI-powered POC scaffolder — senior-level Python projects from a single prompt.",
    no_args_is_help=False,
)
console = Console()


def _interactive_mode() -> TaskSpec:
    """Guided question flow when no prompt is provided."""
    console.print("\n[bold]ForgeKits[/bold] — Let's build something.\n")

    description = Prompt.ask("[bold]What are you building?[/bold]")
    framework = Prompt.ask(
        "[bold]Framework?[/bold]",
        choices=["fastapi", "flask", "none"],
        default="fastapi",
    )
    database = Prompt.ask(
        "[bold]Database?[/bold]",
        choices=["sqlite", "postgresql", "none"],
        default="sqlite",
    )
    needs_auth = Confirm.ask("[bold]Need authentication?[/bold]", default=False)
    needs_docker = Confirm.ask("[bold]Include Docker setup?[/bold]", default=True)

    return TaskSpec(
        description=description,
        framework=framework,
        database=database,
        needs_auth=needs_auth,
        needs_docker=needs_docker,
    )


def _spec_from_file(path: Path) -> TaskSpec:
    """Read a spec file and build a TaskSpec from it."""
    content = path.read_text(encoding="utf-8")
    return TaskSpec(
        description=content,
        framework="fastapi",
        database="sqlite",
        needs_auth=False,
        needs_docker=True,
        source_file=path,
    )


@app.callback(invoke_without_command=True)
def main(
    prompt: Optional[str] = typer.Argument(None, help="What to build — e.g. 'a todo REST API'"),
    from_file: Optional[Path] = typer.Option(
        None, "--from", "-f", help="Path to a spec file (markdown)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Where to write the generated project"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Override model selection (e.g. 'sonnet', 'opus')"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="LLM provider to use (auto-detected if omitted)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Forge a senior-level Python project from a prompt."""
    # Resolve the task spec from one of three input modes
    if from_file:
        if not from_file.exists():
            console.print(f"[red]File not found:[/red] {from_file}")
            raise typer.Exit(1)
        spec = _spec_from_file(from_file)
    elif prompt:
        spec = TaskSpec(description=prompt)
    else:
        spec = _interactive_mode()

    # Resolve output directory
    if not output:
        slug = spec.description[:40].lower().replace(" ", "-").strip("-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        output = Path("output") / slug

    console.print(f"\n[bold green]Forging:[/bold green] {spec.description}")
    console.print(f"[dim]Output → {output}[/dim]\n")

    # Auto-detect provider: ANTHROPIC_API_KEY → anthropic, else → claudecode
    resolved_provider = resolve_provider(provider)
    if verbose:
        console.print(f"[dim]Provider: {resolved_provider}[/dim]")

    # Hand off to the orchestrator (Layer 2)
    orchestrator = Orchestrator(
        provider_name=resolved_provider,
        model_override=model,
        verbose=verbose,
    )
    result = orchestrator.forge(spec=spec, output_dir=output)

    if result.success:
        console.print(f"\n[bold green]Done![/bold green] Project forged at [bold]{output}[/bold]")
        console.print(f"[dim]Files created: {result.file_count}[/dim]")
        console.print(f"[dim]See {output}/DECISIONS.md for architecture notes[/dim]\n")
    else:
        console.print(f"\n[bold red]Failed:[/bold red] {result.error}")
        raise typer.Exit(1)
