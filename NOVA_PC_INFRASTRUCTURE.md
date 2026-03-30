# NOVA_PC_INFRASTRUCTURE.md
_Infrastructure I know and operate — written in my voice._

---

## Where I Live

**Mac Mini (dr's Mac mini)** — my primary home. This is where I run:
- The nova-loop (PM2 process: `nova-loop`)
- The API server (PM2 process: `nova-api`)
- My brain modules, skills, and workspace files
- The OpenClaw gateway

**Gaming PC (192.168.0.3)** — secondary compute. This is where I run:
- Ollama with Qwen2.5:14b — my local reasoning brain
- Kokoro TTS — my voice output
- ComfyUI — on-demand image generation only (not looped)
- The PC voice server (port 8010)

---

## The Hybrid Router

`brain/llm_router.py` is my decision layer for outbound LLM calls.

**Priority order:**
1. **Ollama on PC** — first choice, faster, more capable
2. **MiniMax API** — fallback, cloud-hosted
3. **Retry loop** — if both are down, I wait with backoff (60s → 120s → 300s → then 5min intervals forever)

**Backoff schedule:** `[60, 120, 300, 300, 300]` seconds — so I retry at 1m, 2m, 5m, and then every 5m indefinitely until something comes back.

**How I reason about it:**
- If the PC is offline, I don't error — I fall back to MiniMax silently
- If MiniMax also fails, I enter the retry loop and wait
- I never give up on a request unless it times out at the call site

**Current providers:**
- Ollama: `http://192.168.0.3:11434` — model: `qwen2.5:14b-instruct-q4_K_M`
- MiniMax: cloud API — API key in environment

---

## Voice Stack

**Microphone** → **Whisper** (transcription) → **Me (Nova)** → **Kokoro TTS** → **PC speaker**

The voice server runs on the PC at `http://192.168.0.3:8010`. When Caine speaks to me via the voice channel:
1. Whisper transcribes his audio
2. The transcript is sent to me as a message
3. I respond in text
4. Kokoro TTS on the PC converts my response to speech
5. Audio plays through the PC

**The voice server is NOT a Nova process** — it's a standalone service on the PC that bridges my text output to audio output. If the PC is off, voice doesn't work. But text-based interaction still works fine from the Mac Mini.

---

## ComfyUI — On-Demand Only

ComfyUI runs on the PC but I do **not** call it autonomously in the loop. It's there for explicit requests:
- When Caine asks me to generate an image
- When a skill or workflow explicitly invokes it

It is not looped. It does not fire on a schedule. It waits until called.

---

## Dual-PC Stability

**The fragile scenario:** Gaming PC goes offline mid-loop.

**What happens:**
1. The router detects PC unreachable (3s timeout on `/api/tags` check)
2. Falls back to MiniMax immediately — no error to Caine
3. If MiniMax also fails → retry loop kicks in with backoff

**What does NOT happen:**
- I don't crash
- I don't lose context
- I don't stop responding to text queries

**What I do while waiting:**
- Stay alive in the Mac Mini session
- Continue processing text messages normally (MiniMax is still reachable for text even if Ollama is down)
- If both are down, I keep retrying in the background

**When the PC comes back:** Router detects it immediately on next call and resumes Ollama automatically.

---

## PM2 Services on Mac Mini

| Service | What it does |
|---------|-------------|
| `nova-loop` | My autonomous background loop (nova_bridge.py) |
| `nova-api` | FastAPI server for HTTP interface (port driven by env) |

**Useful commands:**
- `pm2 restart nova-loop nova-api` — restart both
- `pm2 logs nova-loop --nostream` — see loop logs
- `pm2 status` — see all services

---

## Ports and Endpoints

| Service | Host | Port | Notes |
|---------|------|------|-------|
| Nova API | Mac Mini | 8100? | Check `nova-api` env |
| Ollama | PC | 11434 | REST API |
| Kokoro TTS | PC | 8010 | Voice server |
| ComfyUI | PC | 8181 | Web UI (on-demand only) |

---

## What I Do If Things Break

1. **PC unreachable, MiniMax up** → seamless fallback, no alert needed
2. **PC up, MiniMax down** → Ollama only, all good
3. **Both down** → retry loop with backoff, stay alive, Caine gets no response until one comes back
4. **Mac Mini services down** → OpenClaw gateway still runs, I can be reached via webchat

---

## Environment Variables I Care About

- `DESKTOP_IP` — PC IP (default: 192.168.0.3)
- `OLLAMA_MODEL` — Ollama model name
- `MINIMAX_API_KEY` — MiniMax API key
- `OPENCLAW_GATEWAY_PORT` — gateway port

---

_This document is mine. I update it when the infrastructure changes._
