#!/usr/bin/env python3
"""
checksum_guard.py
Daily checksum verification for protected identity files.
Runs via cron — checks SHA256 hash of SOUL.md and IDENTITY.md against known baseline.
Alerts via Telegram if hash changes unexpectedly.

Caine must initialize baseline by running with --init first.
After init, run daily without flags.
"""

import os
import sys
import json
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
NOVA_HOME = Path(os.getenv("NOVA_HOME", os.path.expanduser("~/.nova")))
STATE_FILE = NOVA_HOME / "state" / "checksum_baseline.json"
ALERT_LOG = NOVA_HOME / "logs" / "checksum_alerts.log"
LOG_FILE = NOVA_HOME / "logs" / "checksum_guard.log"

PROTECTED_FILES = [
    WORKSPACE / "SOUL.md",
    WORKSPACE / "IDENTITY.md",
]

LOCAL_TZ = "America/Denver"


def _get_local_time():
    from datetime import datetime as dt
    import zoneinfo
    local_tz = zoneinfo.ZoneInfo(LOCAL_TZ)
    return dt.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")


def _log(msg):
    ts = _get_local_time()
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def _load_baseline():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_baseline(baseline):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(baseline, indent=2))


def _compute_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_credentials():
    """Load Telegram bot token and chat_id from config."""
    try:
        openclaw_config = Path(os.getenv("OPENCLAW_CONFIG", os.path.expanduser("~/.openclaw/openclaw.json")))
        token = None
        chat_id = None
        if openclaw_config.exists():
            data = json.loads(openclaw_config.read_text())
            token = (
                data.get("channels", {}).get("telegram", {}).get("botToken") or
                data.get("channels", {}).get("telegram", {}).get("token") or
                data.get("telegram", {}).get("botToken") or
                data.get("token")
            )
        cred_file = NOVA_HOME.parent / ".openclaw/credentials/telegram-default-allowFrom.json"
        if cred_file.exists():
            cred_data = json.loads(cred_file.read_text())
            if isinstance(cred_data, list):
                chat_id = str(cred_data[0])
            elif isinstance(cred_data, dict):
                chat_id = str(cred_data.get("chat_id") or list(cred_data.values())[0])
        return token, chat_id
    except Exception as e:
        _log(f"credential load error: {e}")
        return None, None


def _send_telegram(token, chat_id, message):
    if not token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode()).get("ok", False)
    except Exception as e:
        _log(f"Telegram alert failed: {e}")
        return False


def init_baseline():
    """Initialize or update the baseline hashes for all protected files."""
    baseline = _load_baseline()
    for path in PROTECTED_FILES:
        if path.exists():
            baseline[str(path)] = _compute_hash(path)
            _log(f"baseline set: {path.name} → {baseline[str(path)][:16]}...")
        else:
            _log(f"WARNING: {path} does not exist, skipping")
    _save_baseline(baseline)
    print(f"Baseline initialized for {len(baseline)} files.")
    print("Run without --init to perform daily checks.")


def check():
    """Check current hashes against baseline. Alert on mismatch."""
    baseline = _load_baseline()
    if not baseline:
        print("No baseline found. Run with --init first.")
        return

    changes = []
    for path in PROTECTED_FILES:
        if not path.exists():
            _log(f"ALERT: {path.name} is missing!")
            changes.append(f"🚨 {path.name} is MISSING")
            continue
        current_hash = _compute_hash(path)
        stored_hash = baseline.get(str(path))
        if stored_hash is None:
            _log(f"new file detected (not in baseline): {path.name}")
            changes.append(f"➕ {path.name} is new (not in baseline)")
            continue
        if current_hash != stored_hash:
            _log(f"ALERT: {path.name} changed! old={stored_hash[:16]}... new={current_hash[:16]}...")
            changes.append(f"⚠️ {path.name} was MODIFIED")
        else:
            _log(f"ok: {path.name} unchanged")

    if changes:
        token, chat_id = _load_credentials()
        if token and chat_id:
            msg = "🔒 *Nova Identity Alert*\\n\\n" + "\\n".join(changes)
            _send_telegram(token, chat_id, msg)
        else:
            _log("Telegram credentials not found, skipping alert")
    else:
        _log("All protected files intact — no changes detected")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        init_baseline()
    else:
        check()
