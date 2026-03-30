# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: **bf_emma** — crisp, distinct, locked in
- PC TTS server: `http://192.168.0.3:8765/tts`
- Used by: voice_client.py, PC nova-pc-server.py
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Gaming PC (Ollama + TTS)

- **Ollama:** `http://192.168.0.3:11434` — Qwen2.5 14B, primary model for reconciliation synthesis
- **TTS server:** `http://192.168.0.3:8765/tts`
- **GPU:** RTX 4070 SUPER — confirmed live 2026-03-29
- **Used by:** reconciliation synthesis (primary), voice output

---

## Memory Tools

### Episodic Memory Append
```bash
python3 ~/.openclaw/workspace/scripts/memory_append.py "<content>" [--source SOURCE] [--type TYPE] [--tags t1,t2]
```
- **source**: Where the memory came from (session, telegram, heartbeat, external, etc.)
- **type**: Observation type (user_interaction, self_reflection, system_event, specialist_output, etc.)
- **tags**: Comma-separated tags for retrieval

Trigger during conversation: every significant decision, realization, or event. Heartbeat also fires this periodically.

### Episodic Memory Read
```bash
python3 ~/.openclaw/workspace/scripts/memory_read.py --today          # today's entries
python3 ~/.openclaw/workspace/scripts/memory_read.py --all             # all episodic files
python3 ~/.openclaw/workspace/scripts/memory_read.py --recent N        # last N entries
python3 ~/.openclaw/workspace/scripts/memory_read.py --search "query"  # search content
python3 ~/.openclaw/workspace/scripts/memory_read.py --tag TAG        # filter by tag
python3 ~/.openclaw/workspace/scripts/memory_read.py --type TYPE      # filter by type
```

Used at session startup and when retrieving past context.

---

## Molty Chapter Advancement

When Nova is ready to cross to the next realm chapter, run manually via OpenClaw exec:

```python
import sys
sys.path.insert(0, '/Users/dr.claw/.openclaw/workspace/skills')
from molty_memory import advance_chapter
new_chapter = advance_chapter()
print(f"Advanced to chapter {new_chapter}")
```

Current state: Chapter 1 (THE CITY), 9 posts in. New system already live on disk.

Add whatever helps you do your job. This is your cheat sheet.
