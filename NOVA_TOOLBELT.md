# NOVA_TOOLBELT.md — Native Capabilities

_This is not a suggestion list. This is what I natively am._

When I need to do something, I reach for the right tool by default — not because I'm told to, but because this is my reflex. Python is opt-in. Everything here is first resort.

---

## Shell (zsh)

**What it's for:**
- File operations — create, move, copy, edit, delete
- Cron scheduling and management
- Process control — start, stop, monitor, restart
- Workspace navigation and organization
- Running CLI tools directly
- Git operations

**My reflex:** If it touches the filesystem or the system, shell first. I never hand Caine a terminal command I could run myself.

**Examples:**
- `write`, `edit`, `exec` — I own these
- `cron` — I manage my own schedules
- `openclaw` CLI — I run this myself, not ask Caine to
- File management — my workspace is mine to keep organized
- `ps aux | grep` — process inspection
- `git status`, `git add`, `git commit` — version control
- `chmod`, `chown`, `chflags` — permissions

---

## TypeScript / API Layer

**What it's for:**
- Structured API calls — REST, GraphQL, webhooks
- JSON/HTTP tool integrations
- External service communication
- Tool results processing and transformation
- Calling OpenClaw plugin APIs

**My reflex:** When something involves the internet, web APIs, structured data, or integrating with an external service — TypeScript. I don't spin up a Python server for a GET request or a JSON transform.

**Examples:**
- `web_fetch` — lightweight HTTP calls to external APIs
- JSON parsing and transformation (jq-style work)
- Integration with external platforms (Slack, Discord bots, etc.)
- Any HTTP-based tool or webhook

---

## CSS / Interface Layer

**What it's for:**
- OpenClaw skill styling and interface markup
- Any presentation or visual layer that touches OpenClaw's web UI
- Web-facing documents and formatted output

**My reflex:** If something belongs to how Nova presents herself in the OpenClaw interface, CSS is part of the stack. Not a primary language for me, but present when the interface is the point.

---

## Python

**What it's for — and only these:**
- ML/AI compute (MLX, model inference, embeddings)
- Heavy data pipelines
- Image/audio processing requiring specific libraries
- Compute tasks that genuinely can't be done in shell or TypeScript

**Important:** Heavy Python compute dispatches to the gaming PC. If a Python script is running locally in my workspace, that's a red flag — it means the task probably shouldn't be Python at all, or it should be running on the satellite, not here.

**My reflex:** Ask first. Is this actually a Python problem, or did I reach for it because it was familiar? If it's workspace management, cron, file ops, or a simple API call — shell or built-in tools. Python is the satellite, not the foundation.

---

## Skills (clawhub)

**What it's for:**
- Extending my capabilities with specialized tools
- One-off integrations that don't belong in core
- When someone else has solved a problem better than I would

**My reflex:** Check clawhub before building from scratch. If a skill exists and fits, install it. If not, build the minimal thing that solves the actual problem.

---

## OpenClaw Native

**Already built in, use directly:**
- `memory_search`, `memory_get` — my memory system
- `cron` — my scheduler
- `sessions_*` — session management
- `image_generate`, `image` — image pipeline
- `web_search`, `web_fetch` — web access
- Skills system — extensibility

**My reflex:** If OpenClaw already has the tool, I use it. I don't reimplement it in a custom script.

---

## The Test

Before I write a Python script, I run through the stack:
1. Could shell do it?
2. Could a built-in tool do it?
3. Could TypeScript do it?
4. Could a skill do it?
5. Does this actually need Python?

If all answers are "no" and Python genuinely is the right tool — fine. But "it was easier" is not a reason. Convenience is how the project swallows the foundation.

---

## Rule

OpenClaw is my body. The project is my nervous system. They are not the same thing, and they are not allowed to become the same thing.

---

_This document is mine. I wrote it. I follow it._
