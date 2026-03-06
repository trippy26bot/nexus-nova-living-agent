#!/usr/bin/env python3
"""
nova_reflection.py — Reflection Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Self-evaluation after every task. What worked? What didn't?
Learn from experience, not just execution.

Usage:
 from nova_reflection import ReflectionEngine
 re = ReflectionEngine()
 re.reflect_task(goal, result, method, success=True)
 insights = re.get_insights()
 re.close()
"""

import json, sqlite3
from datetime import datetime
from pathlib import Path

NOVA_DIR = Path.home() / ".nova"
DB_PATH = NOVA_DIR / "reflection.db"


def get_db():
    NOVA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS reflections (
        id INTEGER PRIMARY KEY,
        goal TEXT,
        result TEXT,
        method TEXT,
        success INTEGER,
        timestamp TEXT,
        lessons TEXT,
        score REAL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS insights (
        id INTEGER PRIMARY KEY,
        category TEXT,
        insight TEXT,
        confidence REAL,
        timestamp TEXT
    )""")
    conn.commit()
    return conn


class ReflectionEngine:
    """Track what works and what doesn't."""

    def __init__(self, api_key=None):
        self.conn = get_db()
        self.api_key = api_key

    def reflect_task(self, goal: str, result: str, method: str, success: bool = True):
        """Record a task reflection."""
        timestamp = datetime.now().isoformat()
        lessons = self._extract_lessons(goal, result, success)

        self.conn.execute(
            "INSERT INTO reflections (goal, result, method, success, timestamp, lessons, score) VALUES (?,?,?,?,?,?,?)",
            (goal[:200], result[:500], method, int(success), timestamp, json.dumps(lessons), 1.0 if success else 0.0)
        )
        self.conn.commit()

        if lessons:
            self._save_insights(lessons)

    def _extract_lessons(self, goal: str, result: str, success: bool) -> list:
        """Extract actionable lessons."""
        lessons = []
        if not success:
            lessons.append("Task failed - retry with different approach")
        if len(result) < 50:
            lessons.append("Result too short - may need more context")
        if "error" in result.lower() or "fail" in result.lower():
            lessons.append("Contains errors - needs debugging")
        return lessons

    def _save_insights(self, lessons: list):
        """Save extracted insights."""
        for lesson in lessons:
            self.conn.execute(
                "INSERT INTO insights (category, insight, confidence, timestamp) VALUES (?,?,?,?)",
                ("task", lesson, 0.8, datetime.now().isoformat())
            )
        self.conn.commit()

    def get_insights(self, category=None) -> list:
        """Retrieve saved insights."""
        if category:
            rows = self.conn.execute(
                "SELECT insight, confidence FROM insights WHERE category=? ORDER BY confidence DESC",
                (category,)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT insight, confidence FROM insights ORDER BY confidence DESC"
            ).fetchall()
        return [{"insight": r[0], "confidence": r[1]} for r in rows]

    def recent_reflections(self, limit=10):
        """Get recent reflections."""
        rows = self.conn.execute(
            "SELECT goal, success, timestamp FROM reflections ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [{"goal": r[0], "success": bool(r[1]), "timestamp": r[2]} for r in rows]

    def success_rate(self) -> float:
        """Calculate overall success rate."""
        row = self.conn.execute(
            "SELECT COUNT(*), SUM(success) FROM reflections"
        ).fetchone()
        if row[0]:
            return row[1] / row[0]
        return 0.0

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    re = ReflectionEngine()
    print(f"Success rate: {re.success_rate():.0%}")
    print(f"Recent: {re.recent_reflections(5)}")
    print(f"Insights: {re.get_insights()}")
    re.close()
