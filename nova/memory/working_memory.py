#!/usr/bin/env python3
"""
Nova Working Memory - Active thought buffer
The central cognitive loop buffer for temporary reasoning context
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class WorkingMemoryItem:
    content: Any
    type: str  # 'thought', 'goal', 'task', 'context'
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None

class WorkingMemory:
    """
    Active thought buffer - the working memory for Nova's cognition.
    This is the central cognitive loop buffer.
    """
    
    def __init__(self, max_items: int = 20, ttl: float = 300):
        self.items: List[WorkingMemoryItem] = []
        self.max_items = max_items
        self.ttl = ttl  # Time to live in seconds
    
    def add(self, content: Any, item_type: str = 'thought', importance: float = 0.5, ttl: float = None):
        """Add item to working memory"""
        item = WorkingMemoryItem(
            content=content,
            type=item_type,
            importance=importance,
            expires_at=time.time() + (ttl or self.ttl)
        )
        
        # Remove expired items first
        self._clean()
        
        # Add new item
        self.items.append(item)
        
        # Keep only max items (by importance)
        if len(self.items) > self.max_items:
            self.items.sort(key=lambda x: x.importance, reverse=True)
            self.items = self.items[:self.max_items]
        
        return item
    
    def get(self, item_type: str = None) -> List[Any]:
        """Get items, optionally filtered by type"""
        self._clean()
        
        if item_type is None:
            return [i.content for i in self.items]
        
        return [i.content for i in self.items if i.type == item_type]
    
    def get_thoughts(self) -> List[Any]:
        """Get current thoughts"""
        return self.get('thought')
    
    def get_goals(self) -> List[Any]:
        """Get active goals"""
        return self.get('goal')
    
    def get_tasks(self) -> List[Any]:
        """Get active tasks"""
        return self.get('task')
    
    def get_context(self) -> List[Any]:
        """Get conversation context"""
        return self.get('context')
    
    def _clean(self):
        """Remove expired items"""
        now = time.time()
        self.items = [i for i in self.items 
                    if i.expires_at is None or i.expires_at > now]
    
    def clear(self, item_type: str = None):
        """Clear working memory"""
        if item_type is None:
            self.items = []
        else:
            self.items = [i for i in self.items if i.type != item_type]
    
    def summarize(self) -> Dict:
        """Get summary of working memory"""
        by_type = {}
        for item in self.items:
            if item.type not in by_type:
                by_type[item.type] = []
            by_type[item.type].append(item.content)
        
        return {
            "total_items": len(self.items),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "items": by_type
        }
    
    def importance_score(self) -> float:
        """Calculate overall importance score"""
        if not self.items:
            return 0.0
        return sum(i.importance for i in self.items) / len(self.items)


# Global instance
_working_memory = None

def get_working_memory():
    global _working_memory
    if _working_memory is None:
        _working_memory = WorkingMemory()
    return _working_memory
