# ForgeKits Backlog

> Prioritized feature backlog. P0 = must have, P1 = should have, P2 = nice to have, P3 = future.

## P0 — Core (v0.1)

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-001 | Python/FastAPI generation pipeline | ✅ Done | Foundation laid — 6-phase pipeline |
| B-002 | Skill system (markdown + YAML frontmatter) | ✅ Done | 9 starter skills |
| B-003 | Provider adapter pattern | ✅ Done | Anthropic ships, others via adapter |
| B-004 | Model auto-selection (startup + per-phase) | ✅ Done | Classifier + ModelPicker |
| B-005 | Output validation (syntax + secrets) | ✅ Done | Validator catches common issues |
| B-006 | DECISIONS.md generation | ✅ Done | Self-documenting output |

## P0 — Core (v0.2)

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-007 | End-to-end testing with real LLM calls | 🔲 Todo | Need integration test suite |
| B-008 | Interactive mode polish (rich prompts) | 🔲 Todo | Better UX for guided flow |
| B-009 | Error recovery in pipeline (retry failed phases) | 🔲 Todo | Currently fails entire pipeline |
| B-010 | Provider: OpenAI adapter | 🔲 Todo | Community or self |
| B-011 | Provider: Ollama adapter (local/offline) | 🔲 Todo | Big for adoption |

## P1 — Architecture Generation (v0.2-0.3)

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-012 | ARCHITECTURE.md auto-generation | 🔲 Todo | System design, component map, data flow |
| B-013 | Database ERD diagram (Mermaid) | 🔲 Todo | Auto-generate from SQLAlchemy models |
| B-014 | API contract generation (OpenAPI spec) | 🔲 Todo | Generate before code, validate after |
| B-015 | TECH-STACK.md with rationale | 🔲 Todo | Why each tech was chosen |

## P1 — Business Intelligence Layer (v0.3)

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-016 | BUSINESS-PLAN.md generation | 🔲 Todo | Problem, users, value prop, MVP scope |
| B-017 | BACKLOG.md generation (user stories) | 🔲 Todo | Prioritized stories with acceptance criteria |
| B-018 | MILESTONES.md generation | 🔲 Todo | Phased delivery plan |

## P1 — Living Documentation (v0.4)

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-019 | Auto-update engine (watch code changes → update docs) | 🔲 Todo | File watcher or git hook |
| B-020 | Drift detection (code vs docs mismatch) | 🔲 Todo | Flag when architecture diverges |
| B-021 | Changelog generation from commits | 🔲 Todo | Commit history → release notes |

## P1 — Senior Protection Layer

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-022 | Algorithm guidance skills (when to use/avoid specific algos) | 🔲 Todo | e.g. "don't use bubble sort for large datasets" |
| B-023 | Complexity analysis skill (Big-O awareness) | 🔲 Todo | Flag O(n²) where O(n log n) exists |
| B-024 | Security audit skill (OWASP top 10 checks) | 🔲 Todo | Post-generation security scan |
| B-025 | Performance anti-patterns skill | 🔲 Todo | N+1 queries, sync in async, memory leaks |
| B-026 | Code review skill (self-review before output) | 🔲 Todo | Agent reviews its own output |

## P2 — Language Expansion

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-027 | TypeScript/Node skills (Express, Fastify, NestJS) | 🔲 Todo | Second language |
| B-028 | C# skills (.NET, ASP.NET Core) | 🔲 Todo | Enterprise demand |
| B-029 | PHP skills (Laravel) | 🔲 Todo | Large community |
| B-030 | Java skills (Spring Boot) | 🔲 Todo | Enterprise demand |
| B-031 | C skills (system-level patterns) | 🔲 Todo | Niche but valuable |
| B-032 | Go skills (Gin, Echo) | 🔲 Todo | Growing demand |

## P2 — Output Enhancements

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-033 | Test generation (pytest suite alongside app) | 🔲 Todo | Not just app code — tests too |
| B-034 | CI/CD generation (GitHub Actions) | 🔲 Todo | Lint, test, build pipeline |
| B-035 | Docker Compose generation | 🔲 Todo | Multi-service setup |
| B-036 | CLAUDE.md in generated projects | 🔲 Todo | AI help continues after scaffolding |

## P3 — Ecosystem

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| B-037 | Skill marketplace / community registry | 🔲 Todo | Install skill packs via CLI |
| B-038 | VS Code extension | 🔲 Todo | Run from editor |
| B-039 | Web UI (optional) | 🔲 Todo | For non-CLI users |
| B-040 | Plugin system for custom output formats | 🔲 Todo | Extend without forking |
