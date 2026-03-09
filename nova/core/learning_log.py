#!/usr/bin/env python3
"""
Learning Log - Record Nova's internal discoveries
"""

import time
from datetime import datetime

class LearningLog:
    """Records insights and learnings from Nova's operations"""
    
    def __init__(self, max_entries: int = 500):
        self.entries = []
        self.max_entries = max_entries
    
    def record(self, message: str, category: str = "general"):
        """Record a learning entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "time_unix": time.time(),
            "category": category,
            "note": message
        }
        self.entries.append(entry)
        
        # Keep bounded
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)
    
    def record_insight(self, message: str):
        self.record(message, "insight")
    
    def record_error(self, message: str):
        self.record(message, "error")
    
    def record_improvement(self, message: str):
        self.record(message, "improvement")
    
    def recent(self, n: int = 20):
        return self.entries[-n:]
    
    def by_category(self, category: str):
        return [e for e in self.entries if e["category"] == category]
    
    def clear(self):
        self.entries = []
    
    def summary(self):
        return {
            "total_entries": len(self.entries),
            "by_category": {
                cat: len(self.by_category(cat))
                for cat in set(e["category"] for e in self.entries)
            }
        }


# Global instance
_learning_log = LearningLog()

def get_learning_log():
    return _learning_log
