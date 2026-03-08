#!/usr/bin/env python3
"""
NOVA CONTEXT INJECTOR v4

Reads OpenClaw session files + LIFE.md directly.
No exec. No hooks. No Nova involvement.

v4 vs v3: Also injects today's LIFE.md entries directly into
AGENTS.md as plain text every 2 minutes.
"""

import os, json, glob, subprocess
from datetime import datetime

SHARED_SESSION = os.path.expanduser("~/.nova/memory/SHARED_SESSION.json")
AGENTS_MD = os.path.expanduser("~/.openclaw/workspace/AGENTS.md")
SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions/")
SESSIONS_JSON = os.path.expanduser("~/.openclaw/agents/main/sessions/sessions.json")
LIFE_MD = os.path.expanduser("~/.nova/memory/LIFE.md")
LOG_FILE = os.path.expanduser("~/.nova/logs/injector.log")
MARKER_START = "<!-- LIVE_CONTEXT_START -->"
MARKER_END = "<!-- LIVE_CONTEXT_END -->"
TELEGRAM_SIGNALS = ["telegram", "chat_id", "message_id", "bot_token"]
VOICE_SIGNALS = ["voice", "audio", "whisper", "nova-senses", "microphone", "speech"]


def classify_channel(origin: dict) -> str:
    """Map OpenClaw origin/session metadata to a normalized channel."""
    provider = str(origin.get("provider", "")).lower()
    surface = str(origin.get("surface", "")).lower()
    label = str(origin.get("label", "")).lower()
    frm = str(origin.get("from", "")).lower()
    to = str(origin.get("to", "")).lower()
    blob = " ".join([provider, surface, label, frm, to])

    if "telegram" in blob:
        return "telegram"
    if any(x in blob for x in ("voice", "audio", "speech", "whisper", "senses")):
        return "voice"
    return "dashboard"

def log(msg):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    open(LOG_FILE,"a").write(line+"\n")
    print(line)

def load_sessions_map():
    if not os.path.exists(SESSIONS_JSON):
        return {}
    try:
        raw = json.load(open(SESSIONS_JSON))
        mapping = {}
        for uid, val in raw.items():
            if uid.startswith("_"): continue
            if isinstance(val, dict):
                origin = val.get("origin", {})
                ch = classify_channel(origin)
                session_id = str(val.get("sessionId", "")).strip()
                session_file = str(val.get("sessionFile", "")).strip()

                # Key by everything scan_sessions may use.
                if uid:
                    mapping[uid] = ch
                if session_id:
                    mapping[session_id] = ch
                if session_file:
                    mapping[session_file] = ch
                    mapping[os.path.basename(session_file)] = ch
                    mapping[os.path.basename(session_file).replace(".jsonl", "")] = ch
        log(f"sessions.json: {len(mapping)} mapped")
        return mapping
    except Exception as e:
        log(f"sessions.json error: {e}")
        return {}

def read_jsonl(path):
    msgs = []
    try:
        for line in open(path):
            if line.strip():
                try: msgs.append(json.loads(line.strip()))
                except: pass
    except: pass
    return msgs

def keyword_detect(messages):
    blob = json.dumps(messages).lower()
    if any(s in blob for s in TELEGRAM_SIGNALS):
        return "telegram"
    if any(s in blob for s in VOICE_SIGNALS):
        return "voice"
    return "dashboard"

def extract_context(messages):
    user_msgs, nova_msgs = [], []
    for msg in messages:
        role = str(msg.get("role", "")).lower()
        content = msg.get("content", "")
        if isinstance(content, list):
            content = " ".join(c.get("text","") for c in content if isinstance(c, dict))
        content = str(content).strip()
        if not content: continue
        if role in ("user", "human"): user_msgs.append(content)
        elif role in ("assistant", "ai"): nova_msgs.append(content)
    last_user = user_msgs[-1][:100] if user_msgs else ""
    return last_user, "", [], f"Caine: {last_user[:60]}..." if last_user else "Session active"

def get_mtime(path):
    try: return os.path.getmtime(path)
    except: return 0

def scan_sessions():
    if not os.path.exists(SESSIONS_DIR): return {}
    files = sorted(glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl")), key=get_mtime, reverse=True)
    if not files: return {}
    sessions_map = load_sessions_map()
    channels = {}
    for filepath in files:
        uuid = os.path.basename(filepath).replace(".jsonl", "")
        messages = read_jsonl(filepath)
        if not messages: continue
        channel = (
            sessions_map.get(uuid)
            or sessions_map.get(filepath)
            or sessions_map.get(os.path.basename(filepath))
            or keyword_detect(messages)
        )
        if channel in channels: continue
        last_user, _, topics, summary = extract_context(messages)
        last_updated = messages[-1].get("timestamp", "")[:16] if messages else ""
        channels[channel] = {"last_updated": last_updated, "last_user": last_user, "summary": summary, "message_count": len(messages)}
        log(f" [{channel}] {len(messages)} messages")
    return channels

def build_shared_session(channels):
    if not channels: return None
    last_channel = list(channels.keys())[0]
    return {"last_updated": datetime.now().isoformat(), "last_channel": last_channel, "conversation_summary": channels[last_channel]["summary"], "channel_history": {ch: {"last_active": data["last_updated"], "message_count": data["message_count"]} for ch, data in channels.items()}, "_injector_version": "v4", "_channels_found": list(channels.keys())}

def write_shared_session(session):
    os.makedirs(os.path.dirname(SHARED_SESSION), exist_ok=True)
    json.dump(session, open(SHARED_SESSION, "w"), indent=2)

def read_todays_memory(max_entries=4):
    if not os.path.exists(LIFE_MD): return ""
    try:
        content = open(LIFE_MD).read()
        today = datetime.now().strftime("%Y-%m-%d")
        lines = []
        in_today = False
        for line in content.split("\n"):
            if line.startswith("## ") and today in line:
                in_today = True
            if in_today:
                lines.append(line)
                if len(lines) > max_entries * 5: break
        return "\n".join(lines[:max_entries*4])
    except: return ""

def build_context_block(session, channels):
    injected_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    todays_memory = read_todays_memory()
    if not session:
        mem = f"\n## TODAY'S MEMORY\n{todays_memory}\n" if todays_memory else ""
        return f"{MARKER_START}\n## LIVE CONTEXT\nNo sessions {injected_at}\n{mem}{MARKER_END}"
    
    last_ch = session.get("last_channel", "")
    memory_block = f"\n## TODAY'S MEMORY\n{todays_memory}\n" if todays_memory else ""
    
    return f"""{MARKER_START}
## LIVE CROSS-CHANNEL CONTEXT
*Updated: {injected_at}*

Most recent: {last_ch}

Channel status:
{chr(10).join(f"- {ch}: {d['message_count']} msgs" for ch, d in channels.items())}
{memory_block}
---
You already know what happened today. Memory is above.
{MARKER_END}"""

def inject_agents_md(block):
    if not os.path.exists(AGENTS_MD): return False
    try:
        content = open(AGENTS_MD).read()
        if MARKER_START in content and MARKER_END in content:
            s = content.index(MARKER_START)
            e = content.index(MARKER_END) + len(MARKER_END)
            content = content[:s] + block + content[e:]
        else:
            content = block + "\n\n---\n\n" + content
        open(AGENTS_MD, "w").write(content)
        return True
    except: return False

def run_injection():
    channels = scan_sessions()
    session = build_shared_session(channels)
    if session:
        write_shared_session(session)
        log(f"Shared: {list(channels.keys())}")
    mem = read_todays_memory()
    log(f"Memory: {len(mem)} chars")
    inject_agents_md(build_context_block(session, channels))
    log("Done")

def install_cron():
    script = os.path.abspath(__file__)
    cron_line = f"*/2 * * * * python3 {script} --inject >> {LOG_FILE} 2>&1"
    existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    cleaned = "\n".join(l for l in existing.split("\n") if "nova-context-injector" not in l)
    new_cron = cleaned.rstrip() + f"\n# nova-context-injector v4\n{cron_line}\n"
    proc = subprocess.run(["crontab", "-"], input=new_cron, text=True, capture_output=True)
    if proc.returncode == 0:
        print("✓ v4 installed")
        run_injection()
    else:
        print(f"Failed: {proc.stderr}")

if __name__ == "__main__":
    import sys
    if "--install" in sys.argv: install_cron()
    elif "--inject" in sys.argv: run_injection()
    elif "--status" in sys.argv:
        channels = scan_sessions()
        print(f"Channels: {list(channels.keys())}")
        mem = read_todays_memory()
        print(f"Memory: {len(mem)} chars")
    else: run_injection()
