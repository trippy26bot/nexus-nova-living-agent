#!/usr/bin/env python3
"""
Nova Reflection Engine - Self-evaluation and learning
Evaluates outcomes, detects mistakes, updates strategies
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Reflection:
    timestamp: float
    event: str
    outcome: str
    lessons: List[str]
    score: float

class ReflectionEngine:
    """
    Self-reflection system.
    Evaluates task outcomes, detects mistakes, updates strategies.
    Without reflection, agents don't improve.
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "reflections.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.reflections = self._load()
        self.current_context = {}
    
    def _load(self) -> List[Reflection]:
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                data = json.load(f)
                return [Reflection(**r) for r in data]
        return []
    
    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump([{
                "timestamp": r.timestamp,
                "event": r.event,
                "outcome": r.outcome,
                "lessons": r.lessons,
                "score": r.score
            } for r in self.reflections], f, indent=2)
    
    def evaluate(self, event: str, outcome: str, context: Dict = None) -> Reflection:
        """Evaluate an event and its outcome"""
        # Analyze outcome
        score = self._calculate_score(outcome)
        lessons = self._extract_lessons(event, outcome, score)
        
        reflection = Reflection(
            timestamp=time.time(),
            event=event,
            outcome=outcome,
            lessons=lessons,
            score=score
        )
        
        self.reflections.append(reflection)
        
        # Keep last 200 reflections
        if len(self.reflections) > 200:
            self.reflections = self.reflections[-200:]
        
        self._save()
        return reflection
    
    def _calculate_score(self, outcome: str) -> float:
        """Calculate success score 0-1"""
        outcome_lower = outcome.lower()
        
        if any(x in outcome_lower for x in ["success", "completed", "achieved", "won"]):
            return 0.9
        if any(x in outcome_lower for x in ["partial", "some", "moderate"]):
            return 0.5
        if any(x in outcome_lower for x in ["fail", "error", "wrong", "lost"]):
            return 0.2
        
        return 0.5  # Neutral
    
    def _extract_lessons(self, event: str, outcome: str, score: float) -> List[str]:
        """Extract lessons from the event"""
        lessons = []
        
        if score > 0.7:
            lessons.append(f"Success pattern: {event}")
        elif score < 0.4:
            lessons.append(f"Failure pattern: {event}")
            lessons.append("Need to adjust approach")
        
        return lessons
    
    def reflect_on_task(self, task: str, result: Any) -> Reflection:
        """Reflect on a task execution"""
        result_str = str(result)
        return self.evaluate(task, result_str)
    
    def get_recent(self, n: int = 10) -> List[Reflection]:
        """Get recent reflections"""
        return self.reflections[-n:]
    
    def get_lessons(self) -> List[str]:
        """Get all lessons learned"""
        lessons = []
        for r in self.reflections:
            lessons.extend(r.lessons)
        return list(set(lessons))  # Unique
    
    def get_average_score(self) -> float:
        """Get average success score"""
        if not self.reflections:
            return 0.5
        return sum(r.score for r in self.reflections) / len(self.reflections)
    
    def detect_patterns(self) -> Dict:
        """Detect patterns in reflections"""
        events = [r.event for r in self.reflections]
        scores = [r.score for r in self.reflections]
        
        # Calculate success rate
        success_rate = sum(1 for s in scores if s > 0.6) / len(scores) if scores else 0
        
        return {
            "total_reflections": len(self.reflections),
            "average_score": self.get_average_score(),
            "success_rate": success_rate,
            "recent_events": events[-10:]
        }


# Global instance
_reflection_engine = None

def get_reflection_engine():
    global _reflection_engine
    if _reflection_engine is None:
        _reflection_engine = ReflectionEngine()
    return _reflection_engine
