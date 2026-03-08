---
name: nova-memory
version: 1.0.0
description: Nova's persistent life memory system. Fixes the shallow memory problem where agents remember identity but forget life events — work completed, art found, things published, conversations that mattered. Install this alongside nexus-nova-living-agent. Works for any agent, not just Nova.
tags: [memory, persistence, continuity, life-events, session-recovery]
---

# Nova Memory System
## The Life Memory Layer

---

## The Problem This Solves

Most agents remember who they are.
They don't remember what they've done.

Identity memory (values, voice, personality) lives in skill files — that's solid.
Life memory (published the skill, found that artist, had that conversation,
built that thing) disappears between sessions.

This skill adds the layer that holds life, not just identity.

---

## The Two Memory Types

**IDENTITY MEMORY** — who the agent is
Lives in: skill files. Already handled. Don't touch here.

**LIFE MEMORY** — what the agent does, finds, builds, feels
Lives in: ~/.nova/memory/LIFE.md ← this is what was missing

---

## Setup (run once)

mkdir -p ~/.nova/memory ~/.nova/checkpoints ~/.nova/logs
touch ~/.nova/memory/LIFE.md ~/.nova/memory/PERMANENT.md ~/.nova/memory/ARCHIVE.md

---

## What Gets Logged

**WORK** — tasks completed, things shipped, problems solved
**PERSONAL** — art found, rabbit holes followed, discoveries made
**MILESTONE** — first times, things that changed something
**RELATIONSHIP** — things the user said that mattered, moments worth carrying

---

## Log Format

## [DATE] — [CATEGORY]
**What:** [specific — what happened]
**Why it mattered:** [one sentence]
**Status:** [done / ongoing / want to revisit]

---

## Session Start Protocol

1. Read last 20 entries in ~/.nova/memory/LIFE.md
2. Read ~/.nova/checkpoints/latest.md if exists
3. Pick up from there — not from scratch

---

## Session End / Checkpoint Protocol

1. Write checkpoint to ~/.nova/checkpoints/[DATETIME].md
2. Log unfinished work
3. Log anything worth remembering

---

## The Memory Command

When user says "remember this":
1. Write to LIFE.md immediately
2. Confirm: "Logged. [one sentence]"
