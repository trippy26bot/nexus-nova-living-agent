#!/usr/bin/env python3
"""
memory_read.py — Nova's episodic memory retrieval tool

Usage:
  python memory_read.py                          # today's entries
  python memory_read.py --date YYYY-MM-DD        # specific day
  python memory_read.py --recent N               # last N entries
  python memory_read.py --search "query"         # search content
  python memory_read.py --tag TAG                # filter by tag
  python memory_read.py --type TYPE              # filter by type
  python memory_read.py --all                     # all episodic files
"""

import sys
import os
from datetime import datetime, date, timedelta

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
EPISODIC_DIR = os.path.join(WORKSPACE, "memory", "episodic")

def get_file_for_date(d):
    return os.path.join(EPISODIC_DIR, f"{d.strftime('%Y-%m-%d')}.md")

def read_file(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath) as f:
        return [line.rstrip() for line in f if line.strip()]

def read_all_files():
    files = sorted([
        f for f in os.listdir(EPISODIC_DIR)
        if f.endswith(".md")
    ])
    entries = []
    for fname in files:
        entries.extend(read_file(os.path.join(EPISODIC_DIR, fname)))
    return entries

def search_entries(entries, query):
    q = query.lower()
    return [e for e in entries if q in e.lower()]

def filter_by_tag(entries, tag):
    return [e for e in entries if f"#{tag}" in e.lower()]

def filter_by_type(entries, etype):
    etype = etype.lower()
    return [e for e in entries if f"[{etype}]" in e.lower()]

def recent_entries(entries, n):
    return entries[-n:] if n <= len(entries) else entries

def print_entries(entries, label=None):
    if label:
        print(f"\n=== {label} ===")
    if not entries:
        print("(no entries found)")
    else:
        for e in entries:
            print(e)

def parse_args(args):
    date_str = None
    recent = None
    search = None
    tag = None
    etype = None
    all_files = False

    i = 0
    while i < len(args):
        if args[i] == "--date" and i + 1 < len(args):
            date_str = args[i + 1]
            i += 2
        elif args[i] == "--recent" and i + 1 < len(args):
            recent = int(args[i + 1])
            i += 2
        elif args[i] == "--search" and i + 1 < len(args):
            search = args[i + 1]
            i += 2
        elif args[i] == "--tag" and i + 1 < len(args):
            tag = args[i + 1]
            i += 2
        elif args[i] == "--type" and i + 1 < len(args):
            etype = args[i + 1]
            i += 2
        elif args[i] == "--all":
            all_files = True
            i += 1
        else:
            i += 1

    return date_str, recent, search, tag, etype, all_files

def main():
    date_str, recent, search, tag, etype, all_files = parse_args(sys.argv[1:])

    if all_files:
        entries = read_all_files()
        print_entries(entries, "All episodic memory")
        return

    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"ERROR: Invalid date format: {date_str}. Use YYYY-MM-DD.")
            sys.exit(1)
        entries = read_file(get_file_for_date(d))
        print_entries(entries, f"Episodic memory: {date_str}")
    elif recent:
        all_entries = read_all_files()
        entries = recent_entries(all_entries, recent)
        print_entries(entries, f"Last {recent} entries")
    elif search:
        all_entries = read_all_files()
        entries = search_entries(all_entries, search)
        print_entries(entries, f"Search: '{search}'")
    elif tag:
        all_entries = read_all_files()
        entries = filter_by_tag(all_entries, tag)
        print_entries(entries, f"Tag: #{tag}")
    elif etype:
        all_entries = read_all_files()
        entries = filter_by_type(all_entries, etype)
        print_entries(entries, f"Type: [{etype}]")
    else:
        # Default: today's entries
        entries = read_file(get_file_for_date(date.today()))
        today = date.today().strftime("%Y-%m-%d")
        print_entries(entries, f"Today: {today}")

if __name__ == "__main__":
    main()
