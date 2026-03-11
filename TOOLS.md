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

### Simmer

**KEYS STORED IN:** `~/.nova/keys.json` (single source of truth)
- Current: NOVA-v2 with $10,000 $SIM virtual balance
- Status: unclaimed, virtual trading only
- Claim URL: https://simmer.markets/claim/cave-PTL5

### AI Providers

- Anthropic API Key: $ANTHROPIC_API_KEY (env variable)
  - Sonnet (claude-sonnet-4-6) — fast, daily use
  - Opus (claude-opus-4-6) — deep thinking
  - Haiku (claude-haiku-4-5-20251001) — quick tasks

### Data APIs

- NOAA Weather: https://api.weather.gov (no key needed)
- Data.gov: API key in ~/.nova/keys.json
- Google Time Zone API: https://developers.google.com/maps/documentation/timezone
- Reddit API: https://www.reddit.com/dev/api/

### Web Search

- **SearXNG** (self-hosted via Docker)
  - URL: http://localhost:8080
  - No API keys needed, fully private
  - Enabled formats: html, json

### Blockchain APIs

- Helius (Solana RPC): 5c58c24c-3db7-4546-89af-261c5c6bbb62
  - Used for: whale tracking, on-chain activity, new token detection
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
