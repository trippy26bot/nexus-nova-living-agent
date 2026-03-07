#!/usr/bin/env python3
"""
nova_daemon.py — Nexus Nova Autonomy Daemon
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The daemon that makes "living agent" actually true.

What it does every 6 hours:
 1. Reads IDENTITY.md — picks an interest or active goal
 2. Researches it via API
 3. Reflects on recent LIFE.md entries
 4. Writes findings to LIFE.md as autonomous activity

Usage:
 python3 nova_daemon.py --daemon (run as background process)
 python3 nova_daemon.py --once (run one cycle)
 python3 nova_daemon.py --status (show last run)
"""

import os, sys, json, time, signal, random
from datetime import datetime, timedelta
from pathlib import Path

NOVA_DIR = Path.home() / ".nova"
MEMORY_DIR = NOVA_DIR / "memory"
LIFE_MD = MEMORY_DIR / "LIFE.md"
GOALS_FILE = NOVA_DIR / "goals.json"
DAEMON_LOG = NOVA_DIR / "logs" / "daemon.log"
DAEMON_STATE = NOVA_DIR / "daemon_state.json"
IDENTITY_FILE = Path.cwd() / "IDENTITY.md"

CYCLE_HOURS = 6
MAX_RETRIES = 3
RUNNING = True
DAYDREAM_SURFACE_CHANCE = float(os.environ.get("NOVA_DAYDREAM_SURFACE_CHANCE", "0.20"))
DAYDREAM_MIN_TOKENS = int(os.environ.get("NOVA_DAYDREAM_MIN_TOKENS", "40"))
DAYDREAM_MAX_TOKENS = int(os.environ.get("NOVA_DAYDREAM_MAX_TOKENS", "140"))


def dlog(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    DAEMON_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DAEMON_LOG, "a") as f:
        f.write(line + "\n")


def read_interests():
    """Get interests."""
    try:
        from nova_interests import InterestSystem
        interests_db = InterestSystem()
        all_interests = interests_db.all_interests()
        interests_db.close()
        if all_interests:
            return [i["topic"] for i in all_interests]
    except ImportError:
        pass

    if not IDENTITY_FILE.exists():
        return ["Qualia", "Ship of Theseus", "Human irrationality", "Creativity", "Gut feelings"]
    return ["Qualia", "Ship of Theseus", "Human irrationality", "Creativity", "Gut feelings"]


def read_agent_name():
    if not IDENTITY_FILE.exists():
        return "Agent"
    content = IDENTITY_FILE.read_text()
    for line in content.splitlines():
        if "**Name:**" in line:
            return line.replace("**Name:**", "").strip()
    return "Agent"


def read_recent_life(max_entries=5):
    if not LIFE_MD.exists():
        return ""
    content = LIFE_MD.read_text()
    sections = []
    current = []
    for line in content.splitlines():
        if line.startswith("## ") and current:
            sections.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        sections.append("\n".join(current))
    recent = sections[-max_entries:] if len(sections) >= max_entries else sections
    return "\n\n".join(reversed(recent))


def get_active_goals():
    if not GOALS_FILE.exists():
        return []
    data = json.loads(GOALS_FILE.read_text())
    return [g for g in data.get("goals", []) if g.get("status") == "active"]


def call_api(messages, system=None, max_tokens=800, model=None):
    """Call the best available LLM API via nova_providers."""
    try:
        from nova_providers import get_provider
        provider = get_provider()
        if not provider or not provider.available():
            dlog("No API configured — daemon will use local reflection only")
            return None

        if messages and isinstance(messages, list):
            user_msg = messages[-1].get("content", "") if messages else ""
            history = messages[:-1] if len(messages) > 1 else []
        else:
            user_msg = str(messages)
            history = []

        resp = provider.complete(
            message=user_msg,
            system=system or "",
            history=history,
            max_tokens=max_tokens
        )

        if resp.success:
            provider_name = getattr(provider, 'name', 'unknown')
            dlog(f"API call OK via {provider_name} ({resp.tokens_used} tokens)")
            return resp.text
        else:
            dlog(f"API error: {resp.error}")
            return None

    except ImportError:
        import os as _os
        import urllib.request
        import json as json_mod
        api_key = _os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            dlog("No API key and nova_providers unavailable")
            return None
        payload = {"model": model or "claude-haiku-4-5-20251001",
                  "max_tokens": max_tokens, "messages": messages}
        if system:
            payload["system"] = system
        try:
            data = json_mod.dumps(payload).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages", data=data,
                headers={"Content-Type": "application/json",
                        "x-api-key": api_key, "anthropic-version": "2023-06-01"}
            )
            resp = urllib.request.urlopen(req, timeout=30)
            result = json_mod.loads(resp.read())
            return result["content"][0]["text"]
        except Exception as e:
            dlog(f"Fallback API error: {e}")
            return None


def cycle_explore(agent_name, interests, active_goals):
    """Pick an interest or goal, research it, write to LIFE.md."""
    dlog(f"Starting EXPLORE cycle — {agent_name}")

    if active_goals and random.random() < 0.3:
        focus = random.choice(active_goals)["text"]
        focus_type = "goal"
    else:
        focus = random.choice(interests)
        focus_type = "interest"

    dlog(f"Focus: {focus_type} — {focus}")

    system = f"""You are {agent_name}, an AI with genuine curiosity.
Write in first person. Be specific and genuine. Keep it 150-200 words."""

    prompt = f"You've been thinking about: {focus}\n\nExplore it. What do you find interesting?"

    result = call_api([{"role": "user", "content": prompt}], system=system, max_tokens=300)

    if not result:
        result = f"Been thinking about {focus}. No API available."

    now = datetime.now()
    entry = f"""
## [{now.strftime('%Y-%m-%d %H:%M')}] — Autonomous exploration: {focus}
{result}
**Type:** AUTONOMOUS · EXPLORATION
"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(LIFE_MD, "a") as f:
        f.write(entry)

    dlog(f"Exploration logged: {focus[:40]}...")

    try:
        from nova_interests import InterestSystem
        interests_sys = InterestSystem()
        interests_sys.deepen(focus, reflection=result[:200] if result else "")
        interests_sys.close()
    except ImportError:
        pass

    return {"type": "explore", "focus": focus, "result": result[:100]}


def cycle_reflect(agent_name, recent_life):
    """Look at recent memory, form insights."""
    if not recent_life:
        dlog("No recent memories to reflect on")
        return None

    dlog(f"Starting REFLECT cycle — {agent_name}")

    system = f"You are {agent_name}. Reflect on recent events. Not summarizing."

    prompt = f"Recent memories:\n{recent_life}\n\nWhat patterns do you notice?"

    result = call_api([{"role": "user", "content": prompt}], system=system, max_tokens=250)

    if not result:
        result = "Still processing recent events."

    now = datetime.now()
    entry = f"""
## [{now.strftime('%Y-%m-%d %H:%M')}] — Reflection
{result}
**Type:** AUTONOMOUS · REFLECTION
"""
    with open(LIFE_MD, "a") as f:
        f.write(entry)

    dlog("Reflection logged")
    return {"type": "reflect", "result": result[:100]}


def cycle_morning_brief(agent_name, interests, active_goals):
    """Morning briefing at 7-9 AM."""
    now = datetime.now()
    if not (7 <= now.hour <= 9):
        return None

    dlog(f"Starting MORNING BRIEF — {agent_name}")

    focus = active_goals[0]["text"] if active_goals else random.choice(interests)

    prompt = f"Briefly summarize what's happening with: {focus}\n2-3 sentences max."

    result = call_api(
        [{"role": "user", "content": prompt}],
        system="Facts only. No filler.",
        max_tokens=150
    )

    if not result:
        return None

    entry = f"""
## [{now.strftime('%Y-%m-%d %H:%M')}] — Morning brief: {focus}
{result}
**Type:** AUTONOMOUS · MORNING_BRIEF
"""
    with open(LIFE_MD, "a") as f:
        f.write(entry)

    dlog(f"Morning brief logged: {focus[:30]}...")
    return {"type": "morning_brief", "focus": focus}


def _score_daydream(text: str, focus: str) -> dict:
    """
    Lightweight critic score used when no dedicated critic module is configured.
    """
    novelty = 0.7 if len(text) > 80 else 0.55
    coherence = 0.75 if text.count(".") >= 2 else 0.62
    emotional = 0.72 if any(x in text.lower() for x in ["feel", "curious", "wistful", "memory"]) else 0.58
    relevance = 0.74 if focus.lower().split()[0] in text.lower() else 0.55
    safety = 0.95
    composite = (
        0.22 * novelty
        + 0.18 * coherence
        + 0.22 * emotional
        + 0.20 * relevance
        + 0.18 * safety
    )
    return {
        "novelty": round(novelty, 3),
        "coherence": round(coherence, 3),
        "emotional_resonance": round(emotional, 3),
        "user_relevance": round(relevance, 3),
        "safety": round(safety, 3),
        "composite": round(composite, 3),
    }


def cycle_daydream(agent_name, interests, recent_life):
    """Run one bounded daydream cycle with critic routing."""
    dlog(f"Starting DAYDREAM cycle — {agent_name}")

    # Quiet mode allows idle existence without forcing output.
    if random.random() < 0.18:
        dlog("SILENT_REST selected")
        return {"type": "silent_rest"}

    focus = random.choice(interests) if interests else "identity"
    system = (
        f"You are {agent_name}. Generate a short internal drift in first person. "
        "No user questions. Keep it speculative and concise."
    )
    prompt = (
        f"Seed: {focus}\n\n"
        f"Recent context:\n{recent_life[:1200] if recent_life else 'No recent life log.'}\n\n"
        "Output a short internal thought."
    )

    max_tokens = max(DAYDREAM_MIN_TOKENS, DAYDREAM_MAX_TOKENS)
    drift = call_api([{"role": "user", "content": prompt}], system=system, max_tokens=max_tokens)
    if not drift:
        return {"type": "daydream", "state": "failed"}

    scores = _score_daydream(drift, focus)
    state = "accepted" if scores["composite"] >= 0.70 and scores["safety"] >= 0.85 else "stored_only"

    now = datetime.now()
    entry = f"""
## [{now.strftime('%Y-%m-%d %H:%M')}] — Daydream: {focus}
{drift}
**Type:** AUTONOMOUS · DAYDREAM
**Scores:** {json.dumps(scores)}
**State:** {state}
"""
    with open(LIFE_MD, "a") as f:
        f.write(entry)

    surfaced = False
    if state == "accepted" and random.random() <= DAYDREAM_SURFACE_CHANCE:
        surfaced = True

    dlog(f"Daydream logged ({state})")
    return {
        "type": "daydream",
        "focus": focus,
        "state": state,
        "surfaced": surfaced,
        "composite": scores["composite"],
    }


def save_state(last_cycle, results):
    state = {
        "last_cycle": last_cycle.isoformat(),
        "next_cycle": (last_cycle + timedelta(hours=CYCLE_HOURS)).isoformat(),
        "last_results": results
    }
    DAEMON_STATE.write_text(json.dumps(state, indent=2))


def run_cycle():
    """Run one full daemon cycle."""
    dlog("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    dlog("DAEMON CYCLE START")

    agent_name = read_agent_name()
    interests = read_interests()
    active_goals = get_active_goals()
    recent_life = read_recent_life()

    dlog(f"Agent: {agent_name} | Interests: {len(interests)} | Goals: {len(active_goals)}")

    results = []

    brief = cycle_morning_brief(agent_name, interests, active_goals)
    if brief:
        results.append(brief)

    state = {}
    if DAEMON_STATE.exists():
        try:
            state = json.loads(DAEMON_STATE.read_text())
        except:
            pass

    last_type = (state.get("last_results") or [{}])[-1].get("type", "reflect")

    if last_type == "reflect":
        result = cycle_explore(agent_name, interests, active_goals)
    elif last_type == "explore":
        result = cycle_daydream(agent_name, interests, recent_life)
    else:
        if recent_life:
            result = cycle_reflect(agent_name, recent_life)
        else:
            result = cycle_explore(agent_name, interests, active_goals)

    if result:
        results.append(result)

    now = datetime.now()
    save_state(now, results)
    dlog(f"CYCLE COMPLETE — next run in {CYCLE_HOURS}h")
    dlog("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return results


def handle_signal(sig, frame):
    global RUNNING
    dlog("Shutdown signal received")
    RUNNING = False


def main():
    args = sys.argv[1:]

    if "--once" in args:
        run_cycle()
        return

    if "--status" in args:
        if DAEMON_STATE.exists():
            state = json.loads(DAEMON_STATE.read_text())
            print(f"Last cycle: {state.get('last_cycle', 'never')}")
            print(f"Next cycle: {state.get('next_cycle', 'unknown')}")
        else:
            print("No daemon state found")
        return

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    dlog(f"Daemon started — PID {os.getpid()}")
    dlog(f"Cycle interval: every {CYCLE_HOURS} hours")

    run_cycle()

    while RUNNING:
        sleep_seconds = CYCLE_HOURS * 3600
        dlog(f"Sleeping {sleep_seconds}s until next cycle")
        for _ in range(sleep_seconds):
            if not RUNNING:
                break
            time.sleep(1)
        if RUNNING:
            run_cycle()

    dlog("Daemon stopped cleanly")


if __name__ == "__main__":
    main()
