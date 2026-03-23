# ForgeKits — CLAUDE.md

## What This Project Is
ForgeKits is an AI-powered CLI tool that generates senior-level Python projects from a single prompt.
It's open source, designed for junior devs and vibe coders who want production-quality POCs fast.

## Architecture
Three layers:
1. **Interface** (`cli.py`) — handles user input (direct prompt, interactive, spec file)
2. **Brain** (`orchestrator.py`, `router/`, `pipeline/`) — classifies tasks, picks models, runs generation phases
3. **Hands** (`generator/`) — writes files, validates output

Key patterns:
- **Provider adapter pattern** — `adapters/base.py` defines the interface, `adapters/anthropic.py` implements it
- **Skill system** — markdown files in `skills/` with YAML frontmatter, loaded by `skills/loader.py`
- **Pipeline phases** — sequential generation with context envelopes between phases (from IRIS)
- **Model routing** — classifier picks model at startup, model_picker refines per phase

## Commands
```bash
pip install -e ".[dev]"        # install in dev mode
forgekits "build a todo API"   # direct mode
forgekits                      # interactive mode
forgekits --from spec.md       # spec file mode
pytest                         # run tests
ruff check src/                # lint
```

## Rules for Contributors
- Type hints on ALL functions
- No business logic in cli.py — everything goes through the orchestrator
- Skills are the product — invest quality there
- One skill per concern, under 200 lines
- Test skill loading and parsing, not LLM output (non-deterministic)
