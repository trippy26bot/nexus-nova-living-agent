#!/usr/bin/env python3
"""
Internal Thought Stream - Private reasoning before responding
"""

from datetime import datetime
from typing import List

class ThoughtStream:
    """Manages Nova's internal thought process"""
    
    def __init__(self, max_thoughts: int = 100):
        self.stream: List[dict] = []
        self.max_thoughts = max_thoughts
        
    def think(self, thought: str, source: str = "system") -> dict:
        """Add a thought to the stream"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "thought": thought,
            "source": source
        }
        
        self.stream.append(entry)
        
        # Keep stream bounded
        if len(self.stream) > self.max_thoughts:
            self.stream.pop(0)
            
        return entry
    
    def think_with_context(self, thought: str, context: dict) -> dict:
        """Add thought with full context"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "thought": thought,
            "context": context,
            "source": "reasoning"
        }
        
        self.stream.append(entry)
        
        if len(self.stream) > self.max_thoughts:
            self.stream.pop(0)
            
        return entry
    
    def recent(self, n: int = 10) -> List[dict]:
        """Get recent thoughts"""
        return self.stream[-n:]
    
    def clear(self):
        """Clear the stream"""
        self.stream = []
        
    def get_summary(self) -> dict:
        """Get summary of thought activity"""
        return {
            "total_thoughts": len(self.stream),
            "oldest": self.stream[0]["timestamp"] if self.stream else None,
            "newest": self.stream[-1]["timestamp"] if self.stream else None
        }


# Global instance
_thoughts = ThoughtStream()

def get_thought_stream():
    return _thoughts
