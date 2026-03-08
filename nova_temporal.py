#!/usr/bin/env python3
"""
nova_temporal.py — Temporal awareness for Nova.
Understanding of time and memory age.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional


class TemporalAwareness:
    """Understanding of time and memory age."""
    
    def __init__(self):
        self.current_time = datetime.now()
        self.session_start = self.current_time
    
    def now(self) -> datetime:
        """Get current time."""
        self.current_time = datetime.now()
        return self.current_time
    
    def memory_age(self, timestamp: str) -> Dict:
        """Calculate memory age and return human-readable label.
        
        Returns:
            {
                'age': timedelta,
                'label': 'earlier today' / 'yesterday' / etc,
                'hours': float
            }
        """
        try:
            mem_time = datetime.fromisoformat(timestamp)
        except:
            return {'label': 'unknown', 'hours': 0, 'age': None}
        
        age = self.now() - mem_time
        hours = age.total_seconds() / 3600
        
        # Convert to human-readable
        if hours < 1:
            label = "just now"
        elif hours < 2:
            label = "about an hour ago"
        elif hours < 24:
            label = f"earlier today"
        elif hours < 48:
            label = "yesterday"
        elif hours < 168:  # 7 days
            days = int(hours / 24)
            label = f"{days} days ago"
        elif hours < 720:  # ~30 days
            weeks = int(hours / 168)
            label = f"{weeks} weeks ago"
        else:
            months = int(hours / 720)
            label = f"{months} months ago"
        
        return {
            'age': age,
            'label': label,
            'hours': hours
        }
    
    def format_memory_reference(self, timestamp: str) -> str:
        """Format a memory reference in natural language.
        
        Example: "Earlier today you mentioned..."
        """
        age_info = self.memory_age(timestamp)
        
        prefixes = {
            "just now": "Just now",
            "about an hour ago": "About an hour ago",
            "earlier today": "Earlier today",
            "yesterday": "Yesterday"
        }
        
        base = prefixes.get(age_info['label'], age_info['label'])
        
        return base
    
    def get_session_duration(self) -> str:
        """Get how long this session has been running."""
        duration = self.now() - self.session_start
        hours = duration.total_seconds() / 3600
        
        if hours < 1:
            mins = int(duration.total_seconds() / 60)
            return f"{mins} minutes"
        elif hours < 24:
            return f"{int(hours)} hours"
        else:
            days = int(hours / 24)
            return f"{days} days"
    
    def should_rehearse(self, timestamp: str, importance: float) -> bool:
        """Determine if a memory should be rehearsed.
        
        Based on age and importance - important memories should be
        rehearsed more often to strengthen recall.
        """
        age_info = self.memory_age(timestamp)
        hours = age_info['hours']
        
        # Rehearsal intervals based on importance
        if importance > 0.8:
            # High importance - rehearse after 24 hours
            return hours > 24
        elif importance > 0.5:
            # Medium - rehearse after 72 hours
            return hours > 72
        else:
            # Low - rehearse after 168 hours (week)
            return hours > 168
    
    def get_temporal_context(self) -> Dict:
        """Get overall temporal context."""
        return {
            "session_duration": self.get_session_duration(),
            "current_time": self.now().strftime("%H:%M"),
            "current_date": self.now().strftime("%Y-%m-%d")
        }


# Singleton
_temporal: Optional[TemporalAwareness] = None


def get_temporal() -> TemporalAwareness:
    """Get temporal awareness singleton."""
    global _temporal
    if _temporal is None:
        _temporal = TemporalAwareness()
    return _temporal


if __name__ == "__main__":
    # Test
    t = get_temporal()
    
    # Test memory age
    import time
    now = datetime.now().isoformat()
    time.sleep(1)
    
    age = t.memory_age(now)
    print(f"Memory age: {age}")
    print(f"Session: {t.get_session_duration()}")
