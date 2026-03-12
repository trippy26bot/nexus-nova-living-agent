#!/usr/bin/env python3
"""
Nova Meta-Learning Engine
Learns how to learn better - continuously improves strategies
"""

import time
import json
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime


class PerformanceTracker:
    """Tracks task execution results for learning"""
    
    def __init__(self):
        self.history = []
        self.max_history = 10000
    
    def record(self, task: str, strategy: str, result: Any, success: bool, metrics: Optional[Dict] = None):
        """Record a task execution"""
        entry = {
            "id": len(self.history),
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "strategy": strategy,
            "result": result,
            "success": success,
            "metrics": metrics or {}
        }
        
        self.history.append(entry)
        
        # Keep history manageable
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        return entry
    
    def get_history(self, task: Optional[str] = None) -> List[Dict]:
        """Get history, optionally filtered by task"""
        if task:
            return [e for e in self.history if e["task"] == task]
        return self.history
    
    def get_task_strategies(self, task: str) -> List[str]:
        """Get all strategies tried for a task"""
        return list(set(e["strategy"] for e in self.history if e["task"] == task))
    
    def get_success_rate(self, task: str, strategy: str) -> float:
        """Get success rate for a task/strategy combo"""
        entries = [e for e in self.history if e["task"] == task and e["strategy"] == strategy]
        if not entries:
            return 0.0
        return sum(1 for e in entries if e["success"]) / len(entries)
    
    def clear(self):
        """Clear history"""
        self.history.clear()


class StrategyOptimizer:
    """Optimizes strategy selection based on performance"""
    
    def __init__(self, tracker: PerformanceTracker):
        self.tracker = tracker
    
    def best_strategy(self, task: str) -> Optional[str]:
        """Find the best performing strategy for a task"""
        strategies = self.tracker.get_task_strategies(task)
        if not strategies:
            return None
        
        best = None
        best_score = -1
        
        for strategy in strategies:
            success_rate = self.tracker.get_success_rate(task, strategy)
            if success_rate > best_score:
                best_score = success_rate
                best = strategy
        
        return best
    
    def rank_strategies(self, task: str) -> List[tuple]:
        """Rank all strategies for a task by performance"""
        strategies = self.tracker.get_task_strategies(task)
        scores = []
        
        for strategy in strategies:
            success_rate = self.tracker.get_success_rate(task, strategy)
            scores.append((strategy, success_rate))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def recommend(self, task: str) -> Dict:
        """Get a recommendation for a task"""
        best = self.best_strategy(task)
        ranked = self.rank_strategies(task)
        
        return {
            "task": task,
            "recommended": best,
            "alternatives": ranked,
            "confidence": ranked[0][1] if ranked else 0.0
        }


class SkillImprover:
    """Updates skills based on learned strategies"""
    
    def __init__(self):
        self.improvements = {}
    
    def improve(self, skill_name: str, strategy: str, metadata: Optional[Dict] = None) -> Dict:
        """Update a skill with improved strategy"""
        if skill_name not in self.improvements:
            self.improvements[skill_name] = {
                "name": skill_name,
                "preferred_strategy": strategy,
                "attempts": 0,
                "improvements": []
            }
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "metadata": metadata or {}
        }
        
        self.improvements[skill_name]["preferred_strategy"] = strategy
        self.improvements[skill_name]["attempts"] += 1
        self.improvements[skill_name]["improvements"].append(entry)
        
        return self.improvements[skill_name]
    
    def get_preferred_strategy(self, skill_name: str) -> Optional[str]:
        """Get the preferred strategy for a skill"""
        if skill_name in self.improvements:
            return self.improvements[skill_name].get("preferred_strategy")
        return None
    
    def get_improvements(self, skill_name: str) -> Optional[Dict]:
        """Get all improvements for a skill"""
        return self.improvements.get(skill_name)


class MetaLearningEngine:
    """Core meta-learning engine"""
    
    def __init__(self):
        self.tracker = PerformanceTracker()
        self.optimizer = StrategyOptimizer(self.tracker)
        self.improver = SkillImprover()
        self.learning_enabled = True
    
    def learn(self, task: str, strategy: str, result: Any, success: bool, metrics: Optional[Dict] = None) -> Dict:
        """Learn from a task execution"""
        # Record the result
        self.tracker.record(task, strategy, result, success, metrics)
        
        # If successful, improve the skill
        if success:
            improved = self.improver.improve(task, strategy, metrics)
        else:
            improved = None
        
        # Get updated recommendation
        recommendation = self.optimizer.recommend(task)
        
        return {
            "recorded": True,
            "improved": improved is not None,
            "recommendation": recommendation
        }
    
    def get_best_strategy(self, task: str) -> Optional[str]:
        """Get the best strategy for a task"""
        return self.optimizer.best_strategy(task)
    
    def get_recommendation(self, task: str) -> Dict:
        """Get strategy recommendation for a task"""
        return self.optimizer.recommend(task)
    
    def get_stats(self) -> Dict:
        """Get meta-learning statistics"""
        return {
            "total_recordings": len(self.tracker.history),
            "unique_tasks": len(set(e["task"] for e in self.tracker.history)),
            "skills_improved": len(self.improver.improvements),
            "learning_enabled": self.learning_enabled
        }
    
    def enable_learning(self):
        """Enable meta-learning"""
        self.learning_enabled = True
    
    def disable_learning(self):
        """Disable meta-learning"""
        self.learning_enabled = False


# Global instance
_meta_engine = None

def get_meta_learning_engine() -> MetaLearningEngine:
    global _meta_engine
    if _meta_engine is None:
        _meta_engine = MetaLearningEngine()
    return _meta_engine


# Convenience functions
def record_task(task: str, strategy: str, result: Any, success: bool, metrics: Optional[Dict] = None):
    """Record a task for meta-learning"""
    return get_meta_learning_engine().learn(task, strategy, result, success, metrics)

def get_best_strategy(task: str) -> Optional[str]:
    """Get best strategy for a task"""
    return get_meta_learning_engine().get_best_strategy(task)

def recommend_strategy(task: str) -> Dict:
    """Get strategy recommendation"""
    return get_meta_learning_engine().get_recommendation(task)
