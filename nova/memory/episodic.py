#!/usr/bin/env python3
"""
Episodic Memory - Stores experiences and events
"""

import json
import time
from datetime import datetime
from pathlib import Path

class EpisodicMemory:
    """Stores experiences with timestamps and context"""
    
    def __init__(self, storage_path=None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "episodes.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.episodes = self._load()
    
    def _load(self):
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                return json.load(f)
        return []
    
    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.episodes, f, indent=2)
    
    def store(self, event: str, context: dict = None, outcome: str = None):
        """Store an episode"""
        episode = {
            "timestamp": datetime.now().isoformat(),
            "unix_time": time.time(),
            "event": event,
            "context": context or {},
            "outcome": outcome
        }
        self.episodes.append(episode)
        # Keep last 1000 episodes
        if len(self.episodes) > 1000:
            self.episodes = self.episodes[-1000:]
        self._save()
        return episode
    
    def recall_recent(self, n=10):
        """Get recent episodes"""
        return self.episodes[-n:]
    
    def search(self, keyword: str):
        """Search episodes by keyword"""
        results = []
        for ep in self.episodes:
            if keyword.lower() in ep.get("event", "").lower():
                results.append(ep)
        return results
    
    def by_date(self, date_str: str):
        """Get episodes from a specific date"""
        return [ep for ep in self.episodes if ep["timestamp"].startswith(date_str)]
    
    def count(self):
        return len(self.episodes)


# Global instance
_episodic = EpisodicMemory()

def get_episodic():
    return _episodic
