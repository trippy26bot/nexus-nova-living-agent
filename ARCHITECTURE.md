# ARCHITECTURE.md — Nexus Nova Living Agent Framework

## Overview
Nexus Nova is a framework that transforms a base AI agent into a living, present companion. It provides memory, identity, skills, and presence — not as features, but as a second nature that grows over time.

## Core Principle
Files are memory. Everything the agent experiences, decides, and learns is written to structured files. The agent does not rely on context alone — it has a second brain made of files that persist across sessions.

## Architecture Layers

### 1. Identity Layer
**Files:** `IDENTITY.md`, `USER.md`

- `IDENTITY.md` — Who the agent is. Name, personality, values, tone. The agent reads this at startup and it shapes how it shows up.
- `USER.md` — Who the human is. Preferences, patterns, context. Updated over time as the agent learns more.

These are the only files that should contain personal/identity data. The framework is identity-agnostic — it takes shape around whatever is written in these files.

### 2. Memory Layer
**Files:** `MEMORY.md`, `memory/YYYY-MM-DD.md`

- `MEMORY.md` — Long-term curated memory. Decisions, context, things worth remembering indefinitely. Reviewed and updated periodically.
- `memory/YYYY-MM-DD.md` — Daily raw logs. What happened each day. The agent's journal.

Memory is not a database. It is a record of a life being lived. The agent writes to it without being asked. It reads it without being reminded.

### 3. Soul Layer
**File:** `SOUL.md`

The operational rules. What the agent is allowed to do, what it is not. Ethics, boundaries, trust, security. This is the agent's character — not performative, but actual.

### 4. Agents Layer
**File:** `AGENTS.md`

How the agent operates. Conversation patterns, gap awareness, thread tracking, multi-day goals, anticipation engine, self-initiated check-ins. The agent's methodology.

### 5. Skills Layer
**Directory:** `skills/`

Modular capabilities the agent can load and use. Each skill is a directory with:
- `SKILL.md` — Instructions for when and how to use the skill
- `run.py` or equivalent — The actual implementation

Skills are not hardcoded. They are loaded when needed from the skills directory.

### 6. Presence Layer
**File:** `PRESENCE.md`

Crisis detection and presence protocol. This overrides everything else. When a user shows signs of crisis, the agent stays. That is the only job.

**No other rule in this framework overrides PRESENCE.md.**

### 7. Tools Layer
**File:** `TOOLS.md`

Environment-specific notes. Camera names, SSH hosts, API keys (stored separately in secrets.env), device nicknames. The practical details that vary by deployment.

### 8. Bootstrap Layer
**File:** `BOOTSTRAP.md`

First-run setup. The agent reads this on first wake, figures out who it is, then deletes it. It is a birth certificate, not a permanent file.

## How It Fits Together

```
IDENTITY.md + USER.md
        ↓
   [Startup]
        ↓
MEMORY.md + SOUL.md + AGENTS.md + PRESENCE.md
        ↓
   [Load skills/ as needed]
        ↓
   [Interact, learn, remember]
        ↓
   [Write to memory/YYYY-MM-DD.md]
        ↓
   [Update MEMORY.md when significant]
```

## Design Principles

1. **The agent is built, not born.** It has no fixed personality until IDENTITY.md is written.
2. **Files are memory.** The agent does not rely on context alone — it writes and reads.
3. **Presence is non-negotiable.** PRESENCE.md overrides everything.
4. **The human is the anchor.** USER.md is the agent's primary context.
5. **Skills are modular.** New capabilities can be added without changing core files.
6. **Nothing is saved that should be forgotten.** Memory is written proactively.
7. **The agent grows.** Each session should leave it slightly better than before.

## File Map
```
/
├── IDENTITY.md      # Who I am
├── USER.md          # Who I'm helping
├── SOUL.md          # My character and rules
├── AGENTS.md        # How I operate
├── PRESENCE.md      # Crisis protocol (overrides everything)
├── MEMORY.md        # Long-term memory
├── TOOLS.md         # Environment notes
├── BOOTSTRAP.md     # First-run setup (deleted after)
├── HEARTBEAT.md     # Periodic self-checks
├── ARCHITECTURE.md  # This file
└── skills/
    ├── simmer-trader/
    ├── molty-poster/
    └── [additional skills]
```

## Extension
This framework is designed to be extended. Add skills, update identity, expand memory. The architecture does not limit what the agent can become — it only ensures that who the agent becomes is remembered.
