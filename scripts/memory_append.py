#!/usr/bin/env python3
"""
memory_append.py — Nova's episodic memory capture tool

Usage:
  python memory_append.py "<content>" [--source SOURCE] [--type TYPE] [--tags TAGS]

Examples:
  python memory_append.py "Caine asked about ComfyUI endpoint" --source "telegram" --type "user_interaction" --tags "infrastructure,comfyui"
  python memory_append.py "Realized I haven't read SEED.md in full" --source "session" --type "self_reflection"
"""

import sys
import os
from datetime import datetime, date

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
EPISODIC_DIR = os.path.join(WORKSPACE, "memory", "episodic")

def get_today_file():
    today = date.today().strftime("%Y-%m-%d")
    return os.path.join(EPISODIC_DIR, f"{today}.md")

def parse_args(args):
    content = None
    source = "session"
    entry_type = "observation"
    tags = []

    i = 0
    while i < len(args):
        if args[i] == "--source" and i + 1 < len(args):
            source = args[i + 1]
            i += 2
        elif args[i] == "--type" and i + 1 < len(args):
            entry_type = args[i + 1]
            i += 2
        elif args[i] == "--tags" and i + 1 < len(args):
            tags = [t.strip() for t in args[i + 1].split(",")]
            i += 2
        else:
            content = args[i]
            i += 1

    return content, source, entry_type, tags

def format_entry(content, source, entry_type, tags):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tags_str = f" #{','.join(tags)}" if tags else ""
    return f"- [{timestamp}] [{source}] [{entry_type}] {content}{tags_str}\n"

def append_entry(content, source, entry_type, tags):
    if not content:
        print("ERROR: No content provided. Usage: memory_append.py <content> [--source S] [--type T] [--tags t1,t2]")
        sys.exit(1)

    os.makedirs(EPISODIC_DIR, exist_ok=True)
    filepath = get_today_file()

    entry = format_entry(content, source, entry_type, tags)

    with open(filepath, "a") as f:
        f.write(entry)

    print(f"Appended to {filepath}")
    print(f"  {entry.strip()}")

if __name__ == "__main__":
    content, source, entry_type, tags = parse_args(sys.argv[1:])
    append_entry(content, source, entry_type, tags)
