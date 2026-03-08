#!/usr/bin/env python3
"""Bootstrap NOVA - create all necessary folders and files"""
import os
import json

BASE = os.path.expanduser("~/.nova")
LOGS = os.path.join(BASE, "logs")
MEMORY_FILE = os.path.join(BASE, "memory.json")
KEYS_FILE = os.path.join(BASE, "keys.json")
DAEMON_STATE = os.path.join(BASE, "daemon_state.json")

# Create directories
os.makedirs(LOGS, exist_ok=True)
print(f"✅ Created logs folder: {LOGS}")

# Create memory file
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)
    print(f"✅ Created memory file: {MEMORY_FILE}")

# Create daemon state
if not os.path.exists(DAEMON_STATE):
    with open(DAEMON_STATE, "w") as f:
        json.dump({"state": {}, "timestamp": ""}, f)
    print(f"✅ Created daemon state: {DAEMON_STATE}")

# Create key vault with placeholders
if not os.path.exists(KEYS_FILE):
    default_keys = {
        "simmer": "YOUR_SIMMER_KEY_HERE"
    }
    with open(KEYS_FILE, "w") as f:
        json.dump(default_keys, f, indent=2)
    print(f"✅ Created key vault: {KEYS_FILE}")
    print("⚠️  Edit ~/.nova/keys.json with your actual API keys!")

print("\n🧠 NOVA bootstrap complete!")
print("Next: edit keys, then run: python3 nova_daemon.py start")
