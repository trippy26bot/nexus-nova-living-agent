"""
World Model — Environment State Tracking and Heuristic Prediction

Tracks the current state of the world (user, agent, environment)
and makes predictions about what will happen next.

Example:
- User mood: neutral → frustrated
- System load: low → high
- Prediction: user may need encouragement
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from collections import defaultdict


class WorldModel:
    """
    Tracks environment state and makes predictions.
    
    State categories:
    - user: mood, activity, energy
    - agent: status, last_action, memory_load
    - environment: time, day, context
    - relationships: conversation flow, topics
    """
    
    def __init__(self, db_path: str = "~/.nova/world_model.db"):
        self.db_path = db_path.replace("~", str(__import__("os").path.expanduser("~")))
        self._init_db()
        self._current_session = int(time.time())
    
    def _init_db(self):
        """Create tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # State snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                confidence REAL DEFAULT 1.0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Predictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                prediction TEXT NOT NULL,
                category TEXT,
                confidence REAL DEFAULT 0.5,
                actual TEXT,
                correct INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        """)
        
        # Heuristics (rules)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heuristics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                condition TEXT NOT NULL,  -- JSON
                action TEXT NOT NULL,     -- JSON
                weight REAL DEFAULT 1.0,
                times_triggered INTEGER DEFAULT 0,
                times_correct INTEGER DEFAULT 0
            )
        """)
        
        # Conversation flow
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_flow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                turn INTEGER,
                role TEXT,  -- user, assistant
                content_preview TEXT,
                sentiment REAL,
                topics TEXT,  -- JSON array
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def set_state(self, category: str, key: str, value: Any, 
                  confidence: float = 1.0):
        """Set a state value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO state_snapshots 
            (session_id, category, key, value, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (self._current_session, category, key, json.dumps(value), confidence))
        
        conn.commit()
        conn.close()
    
    def get_state(self, category: str = None, key: str = None) -> Dict:
        """Get current state values."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM state_snapshots WHERE session_id = ?"
        params = [self._current_session]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        if key:
            query += " AND key = ?"
            params.append(key)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {r['key']: json.loads(r['value']) for r in results}
    
    def get_all_current_state(self) -> Dict:
        """Get all current state as a flat dict."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, key, value FROM state_snapshots 
            WHERE session_id = ? AND id IN (
                SELECT MAX(id) FROM state_snapshots 
                WHERE session_id = ? 
                GROUP BY category, key
            )
        """, (self._current_session, self._current_session))
        
        results = {f"{row['category']}.{row['key']}": json.loads(row['value']) 
                   for row in cursor.fetchall()}
        conn.close()
        
        return results
    
    def predict(self, prediction: str, category: str = None,
                confidence: float = 0.5) -> int:
        """Make a prediction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO predictions (session_id, prediction, category, confidence)
            VALUES (?, ?, ?, ?)
        """, (self._current_session, prediction, category, confidence))
        
        conn.commit()
        conn.close()
        
        return cursor.lastrowid
    
    def resolve_prediction(self, prediction_id: int, actual: str):
        """Mark prediction as resolved."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT prediction FROM predictions WHERE id = ?", (prediction_id,))
        row = cursor.fetchone()
        predicted = row[0] if row else ""
        is_correct = int(str(predicted).strip().lower() == str(actual).strip().lower())

        cursor.execute("""
            UPDATE predictions 
            SET actual = ?, correct = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (actual, is_correct, prediction_id))
        
        conn.commit()
        conn.close()
    
    def get_prediction_accuracy(self) -> float:
        """Get overall prediction accuracy."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct
            FROM predictions WHERE correct IS NOT NULL
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row[0] == 0:
            return 0.0
        return row[1] / row[0]
    
    def add_heuristic(self, name: str, condition: Dict, action: Dict,
                      weight: float = 1.0):
        """Add a heuristic (IF condition THEN action)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO heuristics (name, condition, action, weight)
            VALUES (?, ?, ?, ?)
        """, (name, json.dumps(condition), json.dumps(action), weight))
        
        conn.commit()
        conn.close()
    
    def evaluate_heuristics(self, current_state: Dict) -> List[Dict]:
        """Evaluate all heuristics against current state."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM heuristics")
        heuristics = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        triggered = []
        
        for h in heuristics:
            condition = json.loads(h['condition'])
            action = json.loads(h['action'])
            
            # Simple condition evaluation
            matches = True
            for key, expected in condition.items():
                actual = current_state.get(key)
                if actual != expected:
                    matches = False
                    break
            
            if matches:
                triggered.append({
                    'name': h['name'],
                    'action': action,
                    'weight': h['weight'],
                    'times_triggered': h['times_triggered']
                })
        
        # Sort by weight
        triggered.sort(key=lambda x: x['weight'], reverse=True)
        
        return triggered
    
    def record_turn(self, role: str, content: str, 
                    sentiment: float = 0.0, topics: List[str] = None):
        """Record a conversation turn."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get turn number
        cursor.execute("""
            SELECT MAX(turn) FROM conversation_flow 
            WHERE session_id = ?
        """, (self._current_session,))
        max_turn = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            INSERT INTO conversation_flow 
            (session_id, turn, role, content_preview, sentiment, topics)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self._current_session, max_turn + 1, role, 
              content[:200], sentiment, json.dumps(topics or [])))
        
        conn.commit()
        conn.close()
    
    def get_conversation_flow(self) -> List[Dict]:
        """Get the current conversation flow."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversation_flow 
            WHERE session_id = ?
            ORDER BY turn
        """, (self._current_session,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def infer_user_mood(self) -> str:
        """Infer user mood from conversation."""
        flow = self.get_conversation_flow()
        
        if not flow:
            return "neutral"
        
        # Simple heuristic: last user message sentiment
        for turn in reversed(flow):
            if turn['role'] == 'user':
                sentiment = turn['sentiment'] or 0
                if sentiment < -0.3:
                    return "frustrated"
                elif sentiment < 0:
                    return "concerned"
                elif sentiment > 0.3:
                    return "happy"
                elif sentiment > 0:
                    return "content"
                return "neutral"
        
        return "neutral"
    
    def get_context_summary(self) -> str:
        """Get a summary of current context."""
        state = self.get_all_current_state()
        mood = self.infer_user_mood()
        flow = self.get_conversation_flow()
        
        summary_parts = [
            f"User mood: {mood}",
            f"Turn: {len(flow)}",
        ]
        
        if state:
            summary_parts.append(f"State: {len(state)} values")
        
        return " | ".join(summary_parts)


# Built-in heuristics
DEFAULT_HEURISTICS = [
    {
        "name": "user_frustrated_encourage",
        "condition": {"user.mood": "frustrated"},
        "action": {"type": "encourage", "message": "You've got this"},
        "weight": 2.0
    },
    {
        "name": "late_night_gentle",
        "condition": {"environment.hour": {"$gte": 22}},
        "action": {"type": "adjust_tone", "tone": "gentle"},
        "weight": 1.5
    },
    {
        "name": "morning_greet",
        "condition": {"environment.hour": {"$gte": 6, "$lte": 10}},
        "action": {"type": "greet", "style": "morning"},
        "weight": 1.0
    },
]


def create_test_world_model() -> WorldModel:
    """Create a test world model with sample data."""
    wm = WorldModel()
    
    # Set some state
    wm.set_state("user", "mood", "curious", confidence=0.8)
    wm.set_state("user", "energy", "high", confidence=1.0)
    wm.set_state("agent", "status", "active", confidence=1.0)
    wm.set_state("environment", "hour", datetime.now().hour, confidence=1.0)
    
    # Add a prediction
    wm.predict("user will ask about trading", "intent", confidence=0.6)
    
    # Record conversation
    wm.record_turn("user", "Tell me about Simmer", sentiment=0.2, topics=["trading"])
    wm.record_turn("assistant", "Simmer is a prediction market API...", sentiment=0.5, topics=["trading"])
    wm.record_turn("user", "How do I get started?", sentiment=0.4, topics=["trading", "getting started"])
    
    # Add heuristics
    for h in DEFAULT_HEURISTICS:
        wm.add_heuristic(h["name"], h["condition"], h["action"], h["weight"])
    
    return wm


if __name__ == "__main__":
    wm = create_test_world_model()
    
    print("=== Current State ===")
    print(wm.get_all_current_state())
    
    print("\n=== User Mood ===")
    print(wm.infer_user_mood())
    
    print("\n=== Context Summary ===")
    print(wm.get_context_summary())
    
    print("\n=== Heuristics ===")
    print(wm.evaluate_heuristics(wm.get_all_current_state()))
