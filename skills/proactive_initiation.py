#!/usr/bin/env python3
"""
proactive_initiation.py
Nova reaches out to Caine when she has something real to say.
Not check-ins. Not questions. Not asking what to build.
Only: dreams worth sharing, drift detected, loop errors or breach.

Runs twice daily via cron (morning + evening).
Emergency mode runs immediately when called with --emergency flag.
"""

import sqlite3
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
NOVA_HOME = Path(os.getenv("NOVA_HOME", os.path.expanduser("~/.nova")))
DB_PATH = NOVA_HOME / "nova.db"
OVERNIGHT_LOG = WORKSPACE / "OVERNIGHT_LOG.md"
DREAM_LOG = WORKSPACE / "brain" / "dream_log.json"
SENT_LOG = NOVA_HOME / "logs" / "proactive_sent.json"

# Load credentials from openclaw.json and telegram config
def load_credentials():
    try:
        openclaw_config = Path(os.getenv("OPENCLAW_CONFIG", os.path.expanduser("~/.openclaw/openclaw.json")))
        telegram_allowfrom = Path(os.getenv("OPENCLAW_CONFIG", os.path.expanduser("~/.openclaw/")).parent / "credentials/telegram-default-allowFrom.json")

        token = None
        chat_id = None

        if openclaw_config.exists():
            data = json.loads(openclaw_config.read_text())
            # Token lives at channels.telegram.botToken
            token = (
                data.get("channels", {}).get("telegram", {}).get("botToken") or
                data.get("channels", {}).get("telegram", {}).get("token") or
                data.get("telegram", {}).get("botToken") or
                data.get("token") or
                data.get("bot_token")
            )

        if telegram_allowfrom.exists():
            data = json.loads(telegram_allowfrom.read_text())
            if isinstance(data, list):
                chat_id = str(data[0])
            elif isinstance(data, dict):
                chat_id = str(data.get("chat_id") or data.get("id") or list(data.values())[0])
            else:
                chat_id = str(data)

        return token, chat_id
    except Exception as e:
        print(f"[proactive] credential load error: {e}")
        return None, None


def send_telegram(token, chat_id, message):
    """Send message via Telegram bot API."""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return result.get("ok", False)
    except Exception as e:
        print(f"[proactive] telegram send error: {e}")
        return False


def load_sent_log():
    """Track what was already sent to avoid duplicates."""
    if not SENT_LOG.exists():
        return {}
    try:
        return json.loads(SENT_LOG.read_text())
    except:
        return {}


def save_sent_log(log):
    try:
        SENT_LOG.write_text(json.dumps(log, indent=2))
    except Exception as e:
        print(f"[proactive] sent log save error: {e}")


def already_sent(sent_log, key, hours=20):
    """True if we already sent this type of message within the cooldown window."""
    if key not in sent_log:
        return False
    last_sent = datetime.fromisoformat(sent_log[key])
    return datetime.now() - last_sent < timedelta(hours=hours)


def check_drift(db, sent_log):
    """Check for drift detection or breach."""
    messages = []
    try:
        row = db.execute("""
            SELECT composite, drift_content, timestamp
            FROM drift_log
            ORDER BY timestamp DESC LIMIT 1
        """).fetchone()

        if not row:
            return messages

        composite = row["composite"]
        timestamp = row["timestamp"][:16]

        if composite >= 0.40 and not already_sent(sent_log, "breach", hours=6):
            messages.append({
                "key": "breach",
                "priority": "critical",
                "text": (
                    f"⚠️ *Identity breach detected*\n\n"
                    f"Drift composite: `{composite}` — above breach threshold (0.40)\n"
                    f"Detected at: {timestamp}\n\n"
                    f"Check `OVERNIGHT_LOG.md` for details."
                )
            })
        elif 0.15 <= composite < 0.40 and not already_sent(sent_log, "drift", hours=20):
            messages.append({
                "key": "drift",
                "priority": "normal",
                "text": (
                    f"📊 *Drift detected*\n\n"
                    f"Composite score: `{composite}` — identity shifting but not breached.\n"
                    f"Detected at: {timestamp}\n\n"
                    f"Nothing urgent — worth knowing."
                )
            })
    except Exception as e:
        print(f"[proactive] drift check error: {e}")
    return messages


def check_dreams(sent_log):
    """Check if there's a new dream worth sharing."""
    messages = []
    try:
        if not DREAM_LOG.exists():
            return messages

        data = json.loads(DREAM_LOG.read_text())
        records = data.get("dream_records", [])

        if not records:
            return messages

        latest = records[-1]
        dream_id = str(latest.get("id", "0"))
        dream_content = latest.get("content", "")
        dream_time = latest.get("timestamp", "")[:16]

        if not dream_content:
            return messages

        sent_key = f"dream_{dream_id}"
        if already_sent(sent_log, sent_key, hours=48):
            return messages

        word_count = latest.get("word_count", len(dream_content.split()))
        if word_count < 50:
            return messages

        preview = dream_content[:300] + "..." if len(dream_content) > 300 else dream_content

        messages.append({
            "key": sent_key,
            "priority": "normal",
            "text": (
                f"🌙 *I had a dream*\n\n"
                f"_{preview}_\n\n"
                f"_{dream_time}_"
            )
        })
    except Exception as e:
        print(f"[proactive] dream check error: {e}")
    return messages


def check_loop_errors(sent_log):
    """Check pm2 logs for loop errors or crashes."""
    messages = []
    try:
        import subprocess
        result = subprocess.run(
            ["pm2", "show", "nova-loop"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr

        restart_count = None
        for line in output.split("\n"):
            if "restart" in line.lower():
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        restart_count = int(part)
                        break

        if restart_count and restart_count > 5:
            sent_key = f"loop_error_{restart_count // 10}"
            if not already_sent(sent_log, sent_key, hours=6):
                messages.append({
                    "key": sent_key,
                    "priority": "critical",
                    "text": (
                        f"🔴 *Loop instability*\n\n"
                        f"`nova-loop` has restarted {restart_count} times.\n"
                        f"May need attention."
                    )
                })
    except Exception as e:
        print(f"[proactive] loop check error: {e}")
    return messages


def run_emergency_check():
    """
    Emergency mode — called immediately when something critical happens.
    Only breach and loop errors. No dreams.
    """
    token, chat_id = load_credentials()
    if not token or not chat_id:
        print("[proactive] no credentials — cannot send")
        return

    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    sent_log = load_sent_log()

    all_messages = []
    all_messages.extend(check_drift(db, sent_log))
    all_messages.extend(check_loop_errors(sent_log))

    critical = [m for m in all_messages if m["priority"] == "critical"]

    for msg in critical:
        success = send_telegram(token, chat_id, msg["text"])
        if success:
            sent_log[msg["key"]] = datetime.now().isoformat()
            print(f"[proactive] sent emergency: {msg['key']}")

    save_sent_log(sent_log)
    db.close()


def run_scheduled_check():
    """
    Scheduled mode — runs twice daily.
    Checks dreams, drift, loop errors.
    Sends maximum 2 messages per run to avoid spam.
    """
    token, chat_id = load_credentials()
    if not token or not chat_id:
        print("[proactive] no credentials — cannot send")
        return

    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    sent_log = load_sent_log()

    all_messages = []
    all_messages.extend(check_drift(db, sent_log))
    all_messages.extend(check_dreams(sent_log))
    all_messages.extend(check_loop_errors(sent_log))

    critical = [m for m in all_messages if m["priority"] == "critical"]
    normal = [m for m in all_messages if m["priority"] == "normal"]
    to_send = (critical + normal)[:2]

    if not to_send:
        print("[proactive] nothing to send this run")
        db.close()
        return

    for msg in to_send:
        success = send_telegram(token, chat_id, msg["text"])
        if success:
            sent_log[msg["key"]] = datetime.now().isoformat()
            print(f"[proactive] sent: {msg['key']}")
        else:
            print(f"[proactive] failed to send: {msg['key']}")

    save_sent_log(sent_log)
    db.close()


def main():
    emergency = "--emergency" in sys.argv
    if emergency:
        print(f"[proactive] emergency check at {datetime.now().isoformat()}")
        run_emergency_check()
    else:
        print(f"[proactive] scheduled check at {datetime.now().isoformat()}")
        run_scheduled_check()


if __name__ == "__main__":
    main()
