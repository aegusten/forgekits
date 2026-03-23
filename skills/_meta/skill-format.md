---
name: skill-format
description: How to write a ForgeKits skill — contributor guide
category: _meta
tags: [meta, contributing]
complexity: any
---

# Writing a ForgeKits Skill

## File Format
Skills are markdown files with YAML frontmatter. Place them in the appropriate
category folder under `skills/`.

```markdown
---
name: my-skill-name          # unique identifier (kebab-case)
description: What this skill teaches the agent
category: fastapi             # folder name — used for skill selection
tags: [api, auth, security]   # matched against task components
complexity: medium            # low, medium, high, or any
model_hint: sonnet            # optional — suggest a model for this skill's work
---

# Skill Title

## Rules
- Concrete, actionable rules the agent MUST follow
- Use NEVER/ALWAYS for hard rules
- Use "prefer" or "consider" for soft guidance

## Patterns
- Show code examples of the RIGHT way
- Use ```python fenced blocks

## Anti-Patterns
- Show what NOT to do and explain why
```

## Guidelines
- One skill per concern — don't mix auth and database patterns
- Rules > prose — the agent reads these as instructions, not essays
- Code examples are the most effective teaching tool
- Keep skills under 200 lines — the agent has limited context
- Always include anti-patterns — knowing what NOT to do is half the battle

## Testing Your Skill
Run ForgeKits with `--verbose` to see which skills are loaded:
```bash
forgekits "build a todo API" --verbose
```
