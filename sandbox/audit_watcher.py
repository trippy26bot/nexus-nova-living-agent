#!/usr/bin/env python3
"""
Simple audit log watcher for sandbox events.
Alerts on repeated network attempts, shell spawn, or sensitive file access.
"""

from pathlib import Path
from collections import deque
from datetime import datetime

LOG_FILE = Path('/var/log/openclaw/skill-audit.log')
WINDOW = 120
NETWORK_THRESHOLD = 10


def tail_f(path: Path):
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                continue
            yield line.strip()


def main():
    if not LOG_FILE.exists():
        print(f'Log file not found: {LOG_FILE}')
        return

    recent = deque(maxlen=WINDOW)
    for line in tail_f(LOG_FILE):
        recent.append(line)
        lower = line.lower()

        if 'shell_spawn' in lower or 'sensitive_file_access' in lower:
            print(f"[{datetime.now().isoformat()}] ALERT: {line}")

        if sum(1 for x in recent if 'network_request' in x.lower()) > NETWORK_THRESHOLD:
            print(f"[{datetime.now().isoformat()}] ALERT: high network request rate")


if __name__ == '__main__':
    main()
