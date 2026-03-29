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

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

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
