# TOOLS.md — Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff unique to your setup.

---

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- API service notes (names only — **never keys**)
- Anything environment-specific

**⚠️ Never write API keys, tokens, passwords, or secrets in this file. Keys stay local-only, never committed.**

---

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: (your choice)
- Default speaker: (your device)

### AI Providers
- Primary: (your LLM provider)
- Fast tasks: (smaller/cheaper model)
- Deep thinking: (larger model)
- Keys stored in: (your local keys file - never committed)

### Data APIs
- Weather: https://api.weather.gov (no key needed)
- Web search: SearXNG (self-hosted) or configured provider

### Messaging
- Platform: (Telegram bot name, Discord server, etc.)
```

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

_Add whatever helps you do your job. This is your cheat sheet._
