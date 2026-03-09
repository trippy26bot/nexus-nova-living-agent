#!/usr/bin/env python3
"""
Nova Memory Engine - Multi-layer memory management
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

class MemoryEngine:
    """
    Manages multiple memory layers:
    - short_term: current conversation context
    - conversation_history: past conversations
    - long_term: important facts and learnings
    - identity: core identity memory
    - skill: learned skills and capabilities
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "memory_engine.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load()
    
    def _load(self):
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                return json.load(f)
        return {
            "short_term": [],
            "conversation_history": [],
            "long_term": [],
            "identity": [],
            "skill": []
        }
    
    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    # Short term memory
    def add_short(self, item: str, metadata: dict = None):
        """Add to short-term memory"""
        entry = {
            "content": item,
            "time": time.time(),
            "metadata": metadata or {}
        }
        self.memory["short_term"].append(entry)
        # Keep last 20 short-term items
        self.memory["short_term"] = self.memory["short_term"][-20:]
        self._save()
        return entry
    
    def get_short(self, n: int = 5) -> List[Dict]:
        """Get recent short-term memories"""
        return self.memory["short_term"][-n:]
    
    def clear_short(self):
        """Clear short-term memory"""
        self.memory["short_term"] = []
        self._save()
    
    # Conversation history
    def add_conversation(self, user: str, nova: str, context: dict = None):
        """Add conversation to history"""
        entry = {
            "user": user,
            "nova": nova,
            "time": time.time(),
            "context": context or {}
        }
        self.memory["conversation_history"].append(entry)
        # Keep last 500 conversations
        self.memory["conversation_history"] = self.memory["conversation_history"][-500:]
        self._save()
        return entry
    
    def get_recent_conversations(self, n: int = 10) -> List[Dict]:
        """Get recent conversations"""
        return self.memory["conversation_history"][-n:]
    
    # Long-term memory
    def add_long(self, fact: str, importance: int = 5):
        """Add important fact to long-term memory"""
        entry = {
            "fact": fact,
            "importance": importance,
            "time": time.time()
        }
        self.memory["long_term"].append(entry)
        self._save()
        return entry
    
    def search_long(self, keyword: str) -> List[Dict]:
        """Search long-term memory"""
        results = []
        for item in self.memory["long_term"]:
            if keyword.lower() in item.get("fact", "").lower():
                results.append(item)
        return results
    
    # Identity memory
    def add_identity(self, memory: str):
        """Add identity-defining memory"""
        entry = {
            "memory": memory,
            "time": time.time()
        }
        self.memory["identity"].append(entry)
        self._save()
        return entry
    
    def get_identity(self) -> List[Dict]:
        """Get identity memories"""
        return self.memory["identity"]
    
    # Skill memory
    def add_skill(self, skill_name: str, proficiency: float, notes: str = ""):
        """Add learned skill"""
        entry = {
            "skill": skill_name,
            "proficiency": proficiency,
            "notes": notes,
            "learned_at": time.time()
        }
        self.memory["skill"].append(entry)
        self._save()
        return entry
    
    def get_skills(self) -> List[Dict]:
        """Get all learned skills"""
        return self.memory["skill"]
    
    # Compression
    def compress(self):
        """Compress memory - keep most important"""
        # Keep high importance long-term
        important = [m for m in self.memory["long_term"] if m.get("importance", 0) >= 7]
        self.memory["long_term"] = important[-100:]
        self._save()
        return {"compressed": True, "kept": len(important)}


# Global instance
_memory_engine = None

def get_memory_engine():
    global _memory_engine
    if _memory_engine is None:
        _memory_engine = MemoryEngine()
    return _memory_engine
