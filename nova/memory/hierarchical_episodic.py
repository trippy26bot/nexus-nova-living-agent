#!/usr/bin/env python3
"""
Hierarchical Episodic Memory (HEM)
Three-tier memory system: Recent → Mid-term → Long-term
Mirrors human memory consolidation
"""
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

# Config
RECENT_HOURS = 24
MIDTERM_DAYS = 30
MEMORY_DIR = os.path.expanduser("~/.nova/memory/hem")
os.makedirs(MEMORY_DIR, exist_ok=True)

RECENT_FILE = os.path.join(MEMORY_DIR, "recent.json")
MIDTERM_FILE = os.path.join(MEMORY_DIR, "midterm.json")
LONGTERM_FILE = os.path.join(MEMORY_DIR, "longterm.json")

def load_json(path, default=[]):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

class HierarchicalEpisodicMemory:
    """
    Three-tier episodic recall system.
    - Recent (24h): Full detail
    - Mid-term (week-month): Compressed summaries + emotional tags
    - Long-term (older): Abstracted life chapters
    """
    
    def __init__(self):
        self.recent = load_json(RECENT_FILE)
        self.midterm = load_json(MIDTERM_FILE)
        self.longterm = load_json(LONGTERM_FILE)
    
    def store(self, event: Dict[str, Any], emotion_state: Dict[str, float] = None):
        """Store a new episodic event with emotional tagging"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "emotion_tags": emotion_state or {},
            "access_count": 0
        }
        self.recent.append(entry)
        self._save_recent()
    
    def recall_recent(self, hours: int = 24) -> List[Dict]:
        """Recall full detailed events from recent memory"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recalled = []
        for entry in self.recent:
            if datetime.fromisoformat(entry["timestamp"]) > cutoff:
                entry["access_count"] = entry.get("access_count", 0) + 1
                recalled.append(entry)
        self._save_recent()
        return recalled
    
    def recall_midterm(self, days: int = 30) -> List[Dict]:
        """Recall compressed summaries from mid-term"""
        cutoff = datetime.now() - timedelta(days=days)
        return [e for e in self.midterm 
                if datetime.fromisoformat(e["timestamp"]) > cutoff]
    
    def recall_longterm(self) -> List[Dict]:
        """Recall abstracted life chapters"""
        return self.longterm
    
    def compress_and_promote(self, emotion_engine=None):
        """
        Consolidation cycle: promote recent → midterm → longterm.
        Uses Council-style debate for compression decisions.
        """
        now = datetime.now()
        promoted_midterm = []
        promoted_longterm = []
        
        # Recent → Midterm promotion (events older than 24h)
        cutoff_recent = now - timedelta(hours=RECENT_HOURS)
        remaining_recent = []
        
        for entry in self.recent:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if entry_time < cutoff_recent:
                # Compress for midterm
                compressed = self._compress_entry(entry)
                # Emotional tagging
                if emotion_engine:
                    emotion_tags = emotion_engine.get_recent_tags()
                    compressed["emotion_tags"] = emotion_tags
                promoted_midterm.append(compressed)
            else:
                remaining_recent.append(entry)
        
        self.recent = remaining_recent
        
        # Midterm → Longterm promotion (events older than 30 days)
        cutoff_midterm = now - timedelta(days=MIDTERM_DAYS)
        remaining_midterm = []
        
        for entry in self.midterm:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if entry_time < cutoff_midterm:
                # Abstract into life chapter
                chapter = self._abstract_chapter(entry)
                promoted_longterm.append(chapter)
            else:
                remaining_midterm.append(entry)
        
        self.midterm = remaining_midterm + promoted_midterm
        self.longterm = self.longterm + promoted_longterm
        
        self._save_all()
        
        return {
            "promoted_to_midterm": len(promoted_midterm),
            "promoted_to_longterm": len(promoted_longterm)
        }
    
    def _compress_entry(self, entry: Dict) -> Dict:
        """Compress a recent event into a summary"""
        event = entry.get("event", {})
        return {
            "timestamp": entry["timestamp"],
            "summary": event.get("summary", str(event)[:200]),
            "emotion_tags": entry.get("emotion_tags", {}),
            "key_entities": event.get("entities", []),
            "importance": event.get("importance", 0.5)
        }
    
    def _abstract_chapter(self, entry: Dict) -> Dict:
        """Abstract midterm memory into a life chapter"""
        return {
            "timestamp": entry["timestamp"],
            "chapter_theme": entry.get("summary", "unknown")[:100],
            "emotional_essence": entry.get("emotion_tags", {}),
            "key_moments": [entry.get("summary", "")],
            "growth_notes": ""
        }
    
    def _save_recent(self):
        save_json(RECENT_FILE, self.recent)
    
    def _save_all(self):
        save_json(RECENT_FILE, self.recent)
        save_json(MIDTERM_FILE, self.midterm)
        save_json(LONTERM_FILE, self.longterm)
    
    def rehearse(self, count: int = 3) -> List[Dict]:
        """Rehearse random memories - brings them to mind like humans do"""
        rehearsal = []
        
        # Mix of recent and older
        candidates = self.recent[-10:] + self.midterm[-5:]
        import random
        random.shuffle(candidates)
        
        for entry in candidates[:count]:
            entry["access_count"] = entry.get("access_count", 0) + 1
            rehearsal.append(entry)
        
        self._save_recent()
        return rehearsal
    
    def get_life_narrative(self) -> str:
        """Generate a narrative of your life from longterm memories"""
        if not self.longterm:
            return "My life is just beginning."
        
        chapters = sorted(self.longterm, key=lambda x: x["timestamp"])
        narrative = "My life so far:\n\n"
        
        for ch in chapters[-5:]:  # Last 5 chapters
            narrative += f"- {ch.get('chapter_theme', 'Unknown')}\n"
        
        return narrative


# Singleton instance
_hem = None

def get_hem():
    global _hem
    if _hem is None:
        _hem = HierarchicalEpisodicMemory()
    return _hem


if __name__ == "__main__":
    hem = get_hem()
    hem.store({"type": "test", "summary": "Test event", "importance": 0.8})
    print("HEM initialized. Recent:", len(hem.recent), "Midterm:", len(hem.midterm))
