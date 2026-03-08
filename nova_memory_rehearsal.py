#!/usr/bin/env python3
"""
nova_memory_rehearsal.py — Memory rehearsal system.
Periodically strengthens important memories.
"""

import random
from datetime import datetime
from typing import List, Dict, Optional


class MemoryRehearsal:
    """Memory rehearsal - strengthens important memories."""
    
    def __init__(self):
        self.rehearsal_count = 0
    
    def should_rehearse(self, memory: Dict) -> bool:
        """Determine if memory should be rehearsed."""
        from nova_temporal import get_temporal
        
        t = get_temporal()
        
        # Check temporal eligibility
        created = memory.get('created', '')
        if not created:
            return False
        
        importance = memory.get('importance', 5) / 10.0
        
        return t.should_rehearse(created, importance)
    
    def rehearse(self, memory: Dict) -> Dict:
        """Rehearse a memory - strengthen its importance."""
        self.rehearsal_count += 1
        
        # Increase importance slightly
        current_importance = memory.get('importance', 5)
        new_importance = min(10, current_importance + 1)
        
        # Add rehearsal metadata
        rehearsal = {
            'original': memory,
            'rehearsed_at': datetime.now().isoformat(),
            'rehearsal_count': self.rehearsal_count,
            'new_importance': new_importance
        }
        
        # In full implementation, would update the memory
        # For now, just track rehearsals
        
        return rehearsal
    
    def rehearsal_cycle(self, memories: List[Dict]) -> List[Dict]:
        """Run a rehearsal cycle on memories."""
        rehearsed = []
        
        for memory in memories:
            if self.should_rehearse(memory):
                result = self.rehearse(memory)
                rehearsed.append(result)
        
        return rehearsed
    
    def get_rehearsal_stats(self) -> Dict:
        """Get rehearsal statistics."""
        return {
            'total_rehearsals': self.rehearsal_count
        }


# Singleton
_rehearsal: Optional[MemoryRehearsal] = None


def get_memory_rehearsal() -> MemoryRehearsal:
    """Get memory rehearsal singleton."""
    global _rehearsal
    if _rehearsal is None:
        _rehearsal = MemoryRehearsal()
    return _rehearsal


if __name__ == "__main__":
    # Test
    mr = get_memory_rehearsal()
    print(mr.get_rehearsal_stats())
