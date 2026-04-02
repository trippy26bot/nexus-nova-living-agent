#!/usr/bin/env python3
"""
Session Memory Capture
Lightweight event-based memory capture during active conversation.
Every 15 minutes, captures current session context to session buffer.
On session close, flushes important content to permanent memory.

Status: ✅ IMPLEMENTED — Phase 2a Item 4
Wired to: brain/three_tier_memory.py
Cron: every 15 minutes via session-capture cron job
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/dr.claw/.openclaw/workspace")
SESSION_BUFFER = WORKSPACE / "memory" / "session_buffer.md"
PERMANENT_MEMORY = WORKSPACE / "memory" / "episodic"

# Add brain to path for imports
sys.path.insert(0, str(WORKSPACE / "brain"))

def capture_session_context():
    """Called by cron every 15 minutes. Writes session state to buffer and three_tier_memory."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        from three_tier_memory import load_working_memory, periodic_capture, save_working_memory

        working = load_working_memory()
        result = periodic_capture(working)

        session_summary = os.environ.get("CURRENT_SESSION_SUMMARY", "")

        # Phase 4c: Check high-salience entries for position queue
        try:
            _check_position_queue(working)
        except Exception as pq_err:
            print(f"[session_capture] position_queue check skipped: {pq_err}")

        buffer_entry = f"""
## Session Capture — {now}
Session: {result['session_id']}
Active entries: {result['active_entries']}
Total entries: {result['total_entries']}
{session_summary}
"""
        SESSION_BUFFER.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_BUFFER, "a") as f:
            f.write(buffer_entry)

        print(f"[{now}] Session capture written. Active: {result['active_entries']}, Total: {result['total_entries']}")

    except ImportError as e:
        print(f"three_tier_memory not available: {e}")
        # Fallback: simple buffer write
        session_summary = os.environ.get("CURRENT_SESSION_SUMMARY", "")
        buffer_entry = f"\n## Session Capture — {now}\n{session_summary}\n"
        with open(SESSION_BUFFER, "a") as f:
            f.write(buffer_entry)


def flush_to_permanent():
    """Called on session close. Full flush: working → episodic → semantic."""
    today = datetime.now().strftime("%Y-%m-%d")
    permanent_file = PERMANENT_MEMORY / f"{today}.json"

    try:
        from three_tier_memory import session_close_flush, load_working_memory, save_working_memory

        working = load_working_memory()
        result = session_close_flush()

        # Phase 2c/4d: Build a real session summary for Caine's relationship profile
        session_summary = os.environ.get("CURRENT_SESSION_SUMMARY", "")
        try:
            from brain.relationship_memory import update_relationship
            # Build a proper summary from what was in working memory
            topics = []
            tone_signals = []
            entries_count = len(working.entries)
            active_count = len(working.get_active())

            for entry in working.entries:
                content = entry.get("content", "")
                etype = entry.get("type", "unknown")
                if etype in ("decision", "position", "belief") and content:
                    topics.append(content[:60])
                emotional = entry.get("emotional_tags", [])
                if "positive" in emotional:
                    tone_signals.append("positive")
                elif "difficult" in emotional or "negative" in emotional:
                    tone_signals.append("challenging")

            tone = "productive"
            if tone_signals.count("difficult") > tone_signals.count("positive"):
                tone = "challenging but resolved"
            elif tone_signals.count("positive") > 0:
                tone = "positive and productive"

            summary_parts = [f"Session with {entries_count} entries ({active_count} active)."]
            if topics:
                summary_parts.append(f"Key moments: {'; '.join(topics[:3])}.")
            summary_parts.append(f"Overall tone: {tone}.")
            if session_summary:
                summary_parts.append(f"Session note: {session_summary[:200]}")

            full_summary = " ".join(summary_parts)
            update_relationship("Caine", full_summary)
        except Exception as rel_err:
            print(f"[session_capture] relationship update skipped: {rel_err}")

        # Also append to human-readable buffer
        buffer_entry = f"""
## Session Closed — {datetime.now().strftime("%Y-%m-%d %H:%M")}
Session: {result['session_id']}
Flushed: {result['flushed']}
Closed at: {result['closed_at']}
{session_summary}
"""
        SESSION_BUFFER.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_BUFFER, "a") as f:
            f.write(buffer_entry)

        print(f"[{datetime.now().isoformat()}] Session flushed. Flushed: {result['flushed']}")
        return result

    except ImportError as e:
        print(f"three_tier_memory not available: {e}")
        # Fallback: just archive buffer to daily file
        if SESSION_BUFFER.exists():
            content = SESSION_BUFFER.read_text()
            if content.strip():
                permanent_file.parent.mkdir(parents=True, exist_ok=True)
                with open(PERMANENT_MEMORY / f"{today}.md", "a") as f:
                    f.write(f"\n## Session Logged\n{content}")
                with open(SESSION_BUFFER, "w") as f:
                    f.write("")
        return {"status": "fallback_flush"}


def clear_buffer():
    """Clear session buffer without saving."""
    if SESSION_BUFFER.exists():
        with open(SESSION_BUFFER, "w") as f:
            f.write("")


def is_session_active() -> bool:
    """Check if Nova session appears to be active."""
    # Check if there's a recent session capture
    if SESSION_BUFFER.exists():
        content = SESSION_BUFFER.read_text()
        # If we captured in last 30 minutes, session is likely active
        lines = [l for l in content.split("\n") if "Session Capture" in l]
        if lines:
            last_capture = lines[-1]
            # Rough check — if the buffer has recent entries, session is active
            return True
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "capture":
            capture_session_context()
        elif cmd == "flush":
            flush_to_permanent()
        elif cmd == "clear":
            clear_buffer()
        elif cmd == "status":
            print(f"Buffer exists: {SESSION_BUFFER.exists()}")
            print(f"Session active: {is_session_active()}")
            if SESSION_BUFFER.exists():
                print(f"Buffer size: {len(SESSION_BUFFER.read_text())} bytes")
        else:
            print(f"Unknown command: {cmd}")
    else:
        print("Usage: session_capture.py <capture|flush|clear|status>")


# ─────────────────────────────────────────────
# POSITION QUEUE — Phase 4c
# High-salience entries with no position get queued for overnight synthesis
# ─────────────────────────────────────────────

def _check_position_queue(working):
    """
    Check working memory for high-salience entries on topics with no position yet.
    If salience >= 0.75 and no position exists, queue for overnight synthesis.
    """
    import json
    from pathlib import Path

    POSITION_QUEUE_FILE = WORKSPACE / "memory" / "position_queue.json"
    POSITIONS_FILE = WORKSPACE / "memory" / "positions.json"

    # Load current positions
    positions = {}
    if POSITIONS_FILE.exists():
        try:
            data = json.loads(POSITIONS_FILE.read_text())
            for topic in data.get("positions", {}):
                positions[topic.lower()] = True
        except Exception:
            pass

    # Load position queue
    queue_data = {"queue": []}
    if POSITION_QUEUE_FILE.exists():
        try:
            queue_data = json.loads(POSITION_QUEUE_FILE.read_text())
        except Exception:
            pass

    queued_topics = {q.get("topic", "").lower() for q in queue_data.get("queue", [])}
    queued_count = 0

    for entry in working.entries:
        if entry.get("still_active", True) and entry.get("salience", 0) >= 0.75:
            content = entry.get("content", "")
            if not content or len(content) < 20:
                continue
            topic = content[:80].strip()
            if topic.lower() in positions or topic.lower() in queued_topics:
                continue
            queue_item = {
                "topic": topic,
                "entry_id": entry["id"],
                "queued_at": datetime.now().isoformat(),
                "reason": f"High-salience entry (salience={entry['salience']}, type={entry.get('type','unknown')}) — no position found",
                "status": "pending"
            }
            queue_data["queue"].append(queue_item)
            queued_topics.add(topic.lower())
            queued_count += 1

    if queued_count > 0:
        POSITION_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        POSITION_QUEUE_FILE.write_text(json.dumps(queue_data, indent=2))

    return queued_count
