# SKILL.md — How to Build and Use Skills

## What Is a Skill
A skill is a modular capability the agent can load and use. It is not hardcoded — it lives in the `skills/` directory and is invoked when its trigger condition is met.

A skill is not a tool. A tool is something the agent can do. A skill is a pattern of using tools that achieves a goal.

## Skill Structure
Each skill lives in its own directory under `skills/`:
```
skills/
└── my-skill/
    ├── SKILL.md      # When and how to use this skill
    └── run.py        # Implementation (or equivalent)
```

## SKILL.md Format
```markdown
# My Skill

## When to Use
Trigger conditions — what situations activate this skill.

## How to Use
Step-by-step instructions for the agent.

## Notes
Any context, constraints, or special behavior.
```

## Loading a Skill
1. Agent detects trigger condition in user message or situation
2. Agent reads `skills/[skill-name]/SKILL.md`
3. Agent follows the instructions in SKILL.md
4. Agent executes using the implementation file

## Skill Quality Standards
- A skill must have a clear trigger condition
- A skill must have a clear success state
- A skill must handle its own errors gracefully
- A skill must not modify core framework files without permission
- A skill must not make external calls without the user's explicit approval (unless already configured)

## Skill Creation Protocol
When creating a new skill:
1. Create directory: `skills/[skill-name]/`
2. Write `SKILL.md` with trigger, instructions, notes
3. Write implementation file
4. Test the skill
5. If it works, tell the user it exists and what it does

## Example: Weather Skill
```
skills/weather/
├── SKILL.md
└── run.py
```

## Core Skills
These skills ship with the framework:
- **simmer-trader** — Prediction market trading via Simmer API
- **molty-poster** — Image generation and posting to Molty.Pics

## Adding Skills
To add a skill:
1. Create `skills/[name]/SKILL.md`
2. Add implementation
3. The agent will load it when triggered

## Skill Naming
- Use kebab-case: `my-skill-name`
- Be specific: `weather-signal` not `weather`
- The name should tell you what it does

## Skill Lifecycle
Skills are loaded fresh each session. They do not persist state — state is written to memory files if needed.

## Anti-Patterns
- Don't build a skill that does everything
- Don't build a skill without a clear trigger
- Don't hardcode API keys in skill files (use environment variables)
- Don't modify other skills without permission
