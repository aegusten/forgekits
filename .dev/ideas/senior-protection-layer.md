# Idea: Senior Protection Layer

## The Concept
ForgeKits doesn't just generate code — it actively prevents bad code from being generated. Think of it as a senior engineer looking over the AI's shoulder, catching mistakes before they ship.

## What It Should Cover

### Algorithm Guidance
- Know when to use hash maps vs arrays for lookups
- Flag bubble sort / selection sort for large datasets → suggest merge sort / timsort
- Detect O(n²) nested loops where O(n log n) solutions exist
- Know when recursion is dangerous (stack overflow risk) vs elegant
- Suggest appropriate data structures (don't use a list when you need a set)

### Code Quality Gates
- No function over 50 lines → suggest splitting
- No class over 300 lines → suggest decomposition
- Cyclomatic complexity check → flag deeply nested conditionals
- DRY violations → flag repeated code blocks

### Security Layer
- OWASP top 10 awareness baked into every skill
- SQL injection prevention (always parameterized)
- XSS prevention (output escaping)
- CSRF protection on state-changing endpoints
- Rate limiting on public endpoints
- Input validation at every boundary

### Performance Awareness
- N+1 query detection in ORM usage
- Sync operations in async context
- Missing database indexes on frequently queried fields
- Unbounded queries (no LIMIT on list endpoints)
- Memory leaks (unclosed connections, growing caches)

### Best Practice Enforcement
- Every language has its own "the right way" — skills encode this
- Python: PEP 8, type hints, async patterns
- C#: SOLID principles, dependency injection, async/await
- Java: Spring patterns, proper exception hierarchy
- PHP: PSR standards, Laravel conventions

## How It Works
Each concern becomes a skill (or set of skills) in the `skills/` folder. The protection layer isn't a separate system — it's embedded in the skills themselves. When the AI generates code, these rules are part of its instructions.

## Priority
P1 — this is a core differentiator. Without it, ForgeKits is just another code generator.
