<p align="center">
  <img src="logo/logo.png" alt="ForgeKits Logo" width="200" />
</p>

<h1 align="center">ForgeKits</h1>

<p align="center">
  <strong>AI-powered POC scaffolder — senior-level Python projects from a single prompt.</strong>
</p>

<p align="center">
  <a href="#usage">Usage</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#future-integrations">Roadmap</a> •
  <a href="#contributing">Contributing</a>
</p>

ForgeKits is an open-source CLI tool that takes a one-line description of what you want to build and produces a complete, production-quality Python project with proper architecture, error handling, and documentation — the kind of code a senior engineer would write.

Built for junior developers and vibe coders who want to ship fast without shipping garbage.

```bash
pip install forgekits
forgekits "build a todo REST API with auth"
```

---

## Why ForgeKits?

| Without ForgeKits | With ForgeKits |
|---|---|
| Flat file structure, everything in `app.py` | Service layer, proper separation of concerns |
| No error handling, bare `except: pass` | Custom exceptions, domain-specific error codes |
| Hardcoded secrets in source code | Environment-based config with `.env.example` |
| No documentation, no context for the next developer | Auto-generated `DECISIONS.md` explaining every choice |
| Business logic in route handlers | Thin controllers → service layer → data layer |
| No type hints, no validation | Full type annotations, Pydantic schemas |

---

## How It Works

### High-Level Flow

```mermaid
graph LR
    A[User Prompt] --> B[CLI Interface]
    B --> C[Task Classifier]
    C --> D[Skill Loader]
    D --> E[Pipeline Runner]
    E --> F[File Writer]
    F --> G[Working Project]

    style A fill:#f9f,stroke:#333
    style G fill:#9f9,stroke:#333
```

### Three-Layer Architecture

```mermaid
graph TB
    subgraph "Layer 1 — INTERFACE"
        CLI["cli.py<br/>Direct | Interactive | Spec File"]
    end

    subgraph "Layer 2 — BRAIN"
        ORC["orchestrator.py"]
        CLS["classifier.py<br/>Task Analysis"]
        MPK["model_picker.py<br/>Model Selection"]
        PLR["pipeline/runner.py<br/>Phase Execution"]
        ENV["pipeline/envelope.py<br/>Context Passing"]
    end

    subgraph "Layer 3 — HANDS"
        WRT["generator/writer.py<br/>File Output"]
        VAL["generator/validator.py<br/>Syntax + Secrets"]
    end

    CLI --> ORC
    ORC --> CLS
    ORC --> MPK
    ORC --> PLR
    PLR --> ENV
    ORC --> WRT
    ORC --> VAL

    style CLI fill:#e1f5fe
    style ORC fill:#fff3e0
    style WRT fill:#e8f5e9
    style VAL fill:#e8f5e9
```

### Pipeline Phase Execution

ForgeKits generates projects in sequential phases, passing context between them via **envelopes** — a pattern borrowed from [IRIS](https://github.com/Artiselite/IRIS).

```mermaid
graph LR
    P1[Skeleton] -->|envelope| P2[Data Model]
    P2 -->|envelope| P3[Services]
    P3 -->|envelope| P4[Routes]
    P4 -->|envelope| P5[Wiring]
    P5 -->|envelope| P6[Documentation]

    subgraph "Envelope Contents"
        direction TB
        E1["Key Decisions"]
        E2["Artifacts (files created)"]
        E3["Constraints (accumulate, never dropped)"]
        E4["Open Questions"]
    end

    style P1 fill:#e3f2fd
    style P2 fill:#e3f2fd
    style P3 fill:#e3f2fd
    style P4 fill:#e3f2fd
    style P5 fill:#e3f2fd
    style P6 fill:#e3f2fd
```

### Model Routing

The agent picks its own model — twice. First at startup based on task complexity, then refined per-phase.

```mermaid
graph TB
    TASK["User Task"] --> CLASSIFY["Classifier<br/>(runs on Haiku — cheap)"]
    CLASSIFY -->|"low complexity"| HAIKU["Haiku<br/>Boilerplate, config"]
    CLASSIFY -->|"medium complexity"| SONNET["Sonnet<br/>Business logic, architecture"]
    CLASSIFY -->|"high complexity"| OPUS["Opus<br/>Complex systems, design"]

    subgraph "Per-Phase Routing"
        SONNET --> PH1["skeleton → Sonnet"]
        SONNET --> PH2["routes → Haiku"]
        SONNET --> PH3["services → Sonnet"]
        SONNET --> PH4["docs → Sonnet"]
    end

    style CLASSIFY fill:#fff9c4
    style HAIKU fill:#c8e6c9
    style SONNET fill:#bbdefb
    style OPUS fill:#e1bee7
```

### Provider Adapter Pattern

ForgeKits ships with Anthropic (Claude) but is designed for any provider.

```mermaid
classDiagram
    class LLMAdapter {
        <<abstract>>
        +generate(messages, system, temperature) LLMResponse
        +model_tier() str
        +provider_name str
    }

    class AnthropicAdapter {
        +generate(messages, system, temperature) LLMResponse
        +model_tier() str
        +provider_name = "anthropic"
    }

    class OpenAIAdapter {
        +generate(messages, system, temperature) LLMResponse
        +model_tier() str
        +provider_name = "openai"
        [community contribution]
    }

    class OllamaAdapter {
        +generate(messages, system, temperature) LLMResponse
        +model_tier() str
        +provider_name = "ollama"
        [community contribution]
    }

    LLMAdapter <|-- AnthropicAdapter
    LLMAdapter <|-- OpenAIAdapter
    LLMAdapter <|-- OllamaAdapter

    style OpenAIAdapter fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style OllamaAdapter fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

### Skill System

Skills are markdown files with YAML frontmatter — the core product. They encode senior-level knowledge that shapes every generated project.

```mermaid
graph TB
    subgraph "skills/"
        subgraph "_base/ (always loaded)"
            S1["project-structure.md"]
            S2["error-handling.md"]
            S3["senior-patterns.md"]
            S4["anti-patterns.md"]
        end

        subgraph "fastapi/"
            S5["fastapi-setup.md"]
            S6["fastapi-routes.md"]
            S7["fastapi-models.md"]
            S8["fastapi-auth.md"]
        end

        subgraph "sqlalchemy/"
            S9["models.md"]
            S10["async-session.md 🔜"]
            S11["migrations.md 🔜"]
        end

        subgraph "flask/ 🔜"
            S12["..."]
        end
    end

    LOADER["SkillLoader"] --> S1
    LOADER --> S5
    LOADER --> S9
    TASK["Task: 'build a todo API'"] --> LOADER

    style S1 fill:#c8e6c9
    style S2 fill:#c8e6c9
    style S3 fill:#c8e6c9
    style S4 fill:#c8e6c9
    style S12 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style S10 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
    style S11 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

---

## Usage

### Direct Mode
```bash
forgekits "build a todo REST API with auth"
# → output/build-a-todo-rest-api-with-auth/
```

### Interactive Mode
```bash
forgekits
# What are you building? > a bookstore API
# Framework? > fastapi
# Database? > postgresql
# Need authentication? > yes
# Include Docker setup? > yes
```

### Spec File Mode
```bash
forgekits --from workspace/my-project-spec.md
```

### Options
```bash
forgekits "build an API" --output ~/projects/my-api    # custom output path
forgekits "build an API" --model opus                   # force a specific model
forgekits "build an API" --provider anthropic            # select provider
forgekits "build an API" --verbose                       # show skill loading, model picks
```

---

## Generated Project Structure

Every project ForgeKits generates follows this structure:

```
my-project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py              # app factory with lifespan events
│       ├── config.py            # env-based configuration
│       ├── database.py          # async SQLAlchemy session
│       ├── models/              # SQLAlchemy models
│       ├── schemas/             # Pydantic request/response schemas
│       ├── services/            # business logic (one per domain)
│       ├── routes/              # thin API controllers
│       └── exceptions.py        # custom domain exceptions
├── tests/
├── pyproject.toml
├── Dockerfile
├── .env.example
├── .gitignore
├── README.md                    # setup instructions + API docs
├── DECISIONS.md                 # why every choice was made
└── CLAUDE.md                    # AI help for the developer after scaffolding
```

---

## Project Structure

```
forgekits/
├── src/forgekits/               # the Python package
│   ├── cli.py                   # Layer 1 — user interface
│   ├── models.py                # shared data types
│   ├── orchestrator.py          # the brain — connects everything
│   ├── adapters/                # provider-agnostic LLM interface
│   │   ├── base.py              # abstract adapter contract
│   │   ├── anthropic.py         # Claude implementation
│   │   └── registry.py          # adapter discovery
│   ├── router/                  # task analysis + model selection
│   │   ├── classifier.py        # complexity analysis
│   │   └── model_picker.py      # model routing logic
│   ├── pipeline/                # multi-phase generation
│   │   ├── phase.py             # single phase execution
│   │   ├── envelope.py          # context passing between phases
│   │   └── runner.py            # pipeline orchestration
│   ├── skills/                  # skill loader
│   │   └── loader.py            # parses markdown + YAML frontmatter
│   └── generator/               # file output
│       ├── writer.py            # writes files to disk
│       └── validator.py         # syntax + secret checking
├── skills/                      # THE PRODUCT — curated skill library
│   ├── _base/                   # always loaded
│   ├── fastapi/                 # FastAPI-specific patterns
│   ├── sqlalchemy/              # database patterns
│   └── _meta/                   # contributor guides
├── workspace/                   # user drops spec files here
├── output/                      # generated projects land here
└── tests/
```

---

## Future Integrations

### Self-Generating Project Intelligence

ForgeKits will evolve from a code scaffolder into a **full project architect**. The AI won't just generate code — it will generate everything a senior engineer produces before, during, and after writing code.

```mermaid
graph TB
    subgraph "v0.1 — Current"
        A1["Code Generation"]
        A2["DECISIONS.md"]
    end

    subgraph "v0.2 — Project Architecture"
        B1["ARCHITECTURE.md<br/>System design, component map,<br/>data flow diagrams"]
        B2["Database Schema Diagram<br/>ERD auto-generated from models,<br/>Mermaid + SQL migration plan"]
        B3["API Contract<br/>OpenAPI spec generated<br/>before code exists"]
    end

    subgraph "v0.3 — Business Layer"
        C1["BUSINESS-PLAN.md<br/>Problem statement, target users,<br/>competitive landscape, MVP scope"]
        C2["BACKLOG.md<br/>Prioritized user stories,<br/>acceptance criteria, effort estimates"]
        C3["MILESTONES.md<br/>Phase breakdown, dependencies,<br/>risk flags, definition of done"]
    end

    subgraph "v0.4 — Living Documents"
        D1["Auto-Update Engine<br/>Watches code changes,<br/>updates all docs in sync"]
        D2["Drift Detection<br/>Flags when code diverges<br/>from documented architecture"]
        D3["Changelog Generation<br/>Commit history → human-readable<br/>release notes"]
    end

    A1 --> B1
    A2 --> B1
    B1 --> C1
    B2 --> C2
    C1 --> D1
    C2 --> D2

    style A1 fill:#c8e6c9
    style A2 fill:#c8e6c9
    style B1 fill:#bbdefb
    style B2 fill:#bbdefb
    style B3 fill:#bbdefb
    style C1 fill:#fff9c4
    style C2 fill:#fff9c4
    style C3 fill:#fff9c4
    style D1 fill:#e1bee7
    style D2 fill:#e1bee7
    style D3 fill:#e1bee7
```

### v0.2 — Project Architecture Generation

The AI generates architectural documentation **before writing code**, then generates code that matches.

| Document | What It Contains | When It's Generated |
|---|---|---|
| `ARCHITECTURE.md` | System design, component boundaries, data flow, tech decisions | Phase 0 — before any code |
| `DATABASE.md` | ERD diagram (Mermaid), table definitions, index strategy, migration plan | Phase 1 — alongside data models |
| `API-CONTRACT.md` | OpenAPI spec, endpoint inventory, auth requirements, rate limits | Phase 1 — before routes are written |
| `DECISIONS.md` | Every architectural choice with rationale | Accumulated across all phases |

```mermaid
graph LR
    PROMPT["User Prompt"] --> ARCH["Generate Architecture"]
    ARCH --> DB["Generate DB Schema + ERD"]
    ARCH --> API["Generate API Contract"]
    DB --> CODE["Generate Code<br/>(matches the architecture)"]
    API --> CODE
    CODE --> VALIDATE["Validate Code ↔ Docs"]

    style ARCH fill:#bbdefb
    style VALIDATE fill:#fff9c4
```

### v0.3 — Business Intelligence Layer

ForgeKits becomes a **product thinking partner**, not just a code generator.

| Document | What It Contains |
|---|---|
| `BUSINESS-PLAN.md` | Problem statement, target users, value proposition, competitive analysis, MVP scope |
| `BACKLOG.md` | User stories with acceptance criteria, priority (P0-P3), effort estimates, dependencies |
| `MILESTONES.md` | Phased delivery plan, risk flags, definition of done per milestone |
| `TECH-STACK.md` | Why each technology was chosen, alternatives considered, migration paths |

### v0.4 — Living Documentation Engine

Documents don't rot. When code changes, docs update automatically.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant FK as ForgeKits Watcher
    participant Code as Codebase
    participant Docs as Documentation

    Dev->>Code: Makes changes (new model, new route)
    FK->>Code: Detects changes (file watcher / git hook)
    FK->>Docs: Reads current ARCHITECTURE.md
    FK->>FK: Compares code state vs documented state
    alt Drift detected
        FK->>Docs: Updates ARCHITECTURE.md
        FK->>Docs: Updates DATABASE.md (new ERD)
        FK->>Docs: Updates BACKLOG.md (marks stories done)
        FK->>Dev: "Updated 3 docs to match your changes"
    else No drift
        FK->>Dev: "Docs are in sync"
    end
```

### v0.5+ — Planned Integrations

| Feature | Description |
|---|---|
| **Flask support** | Skills + pipeline phases for Flask projects |
| **Django support** | Full Django project generation with admin, ORM, migrations |
| **TypeScript/Node** | Second language support — Express, Fastify, NestJS |
| **OpenAI adapter** | Community-contributed provider for GPT models |
| **Ollama adapter** | Local model support — fully offline generation |
| **Test generation** | Auto-generate pytest test suite alongside application code |
| **CI/CD generation** | GitHub Actions, Docker Compose, deployment configs |
| **Skill marketplace** | Community-contributed skill packs installable via CLI |
| **VS Code extension** | Run ForgeKits from the editor, preview generated structure |

---

## Contributing

### Adding a New Skill
1. Create a `.md` file in the appropriate `skills/` subfolder
2. Add YAML frontmatter (see `skills/_meta/skill-format.md`)
3. Write rules, patterns, and anti-patterns
4. Test with `forgekits "your test prompt" --verbose`
5. Submit a PR

### Adding a New Provider
1. Create `src/forgekits/adapters/your_provider.py`
2. Subclass `LLMAdapter` from `adapters/base.py`
3. Register in `adapters/registry.py`
4. Submit a PR

---

## Acknowledgments

- **[IRIS](https://github.com/Artiselite/IRIS)** — The context envelope pattern and skill system architecture are inspired by IRIS, an intelligent runtime system for Claude Code by [@Artiselite](https://github.com/Artiselite).

---

## License

MIT
