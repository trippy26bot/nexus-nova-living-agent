#!/usr/bin/env python3
"""
nova_goal_engine.py — goal management for living-agent loops.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


@dataclass
class Goal:
    id: str
    description: str
    category: str  # short_term, long_term, emergent
    priority: float = 0.5
    created_at: str = None
    last_active: str = None
    iterations: int = 0
    max_iterations: int = 10
    reward_score: float = 0.5
    status: str = "active"  # active, completed, abandoned, paused


@dataclass
class GoalSet:
    short_term: List[str] = field(default_factory=list)
    long_term: List[str] = field(default_factory=list)
    emergent: List[str] = field(default_factory=list)


class GoalEngine:
    """Goal engine with priority scoring and reward updates."""
    
    # Safety bounds
    MAX_GOALS = 20
    MAX_ITERATIONS_PER_GOAL = 10
    MAX_RUNTIME_MINUTES = 30
    ITERATION_TIMEOUT_SECONDS = 300  # 5 minutes per iteration
    
    # Priority factors
    PRIORITY_FACTORS = {
        'recency': 0.2,      # Recently active
        'reward': 0.4,       # Reward score
        'age': 0.2,          # Older goals get slight boost
        'category': 0.2,     # Category weight
    }
    
    def __init__(self, path: Path = None):
        base_dir = Path(os.environ.get("NOVA_DATA_DIR", ".nova")).expanduser().resolve()
        self.path = path or (base_dir / "goals_state.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        self.goals: List[Goal] = []
        self.start_time: Optional[datetime] = None
        self.load_goals()
    
    def load_goals(self):
        """Load goals from file."""
        if not self.path.exists():
            self.goals = self._default_goals()
            return
        
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            goals_data = data.get("goals", [])
            self.goals = [Goal(**g) for g in goals_data]
        except:
            self.goals = self._default_goals()
    
    def _default_goals(self) -> List[Goal]:
        return [
            Goal(
                id="default_1",
                description="maintain_task_reliability",
                category="short_term",
                priority=0.8,
                created_at=datetime.now().isoformat()
            ),
            Goal(
                id="default_2", 
                description="improve_memory_continuity",
                category="long_term",
                priority=0.6,
                created_at=datetime.now().isoformat()
            )
        ]
    
    def save(self):
        """Save goals to file."""
        payload = {
            "updated_at": datetime.now().isoformat(),
            "goals": [g.__dict__ for g in self.goals]
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    
    def add_goal(self, description: str, category: str = "short_term", 
                priority: float = 0.5) -> Goal:
        """Add a new goal."""
        if len(self.goals) >= self.MAX_GOALS:
            return None  # Safety bound
        
        goal = Goal(
            id=f"goal_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            description=description,
            category=category,
            priority=priority,
            created_at=datetime.now().isoformat(),
            max_iterations=self.MAX_ITERATIONS_PER_GOAL
        )
        
        self.goals.append(goal)
        self.save()
        return goal
    
    def calculate_priority(self, goal: Goal) -> float:
        """Calculate priority score using multiple factors."""
        score = 0.0
        
        # Factor 1: Reward score (40% weight)
        score += goal.reward_score * self.PRIORITY_FACTORS['reward']
        
        # Factor 2: Recency (20% weight)
        if goal.last_active:
            last = datetime.fromisoformat(goal.last_active)
            hours_since = (datetime.now() - last).total_seconds() / 3600
            recency = max(0, 1 - (hours_since / 24))  # Decay over 24h
            score += recency * self.PRIORITY_FACTORS['recency']
        else:
            score += 0.5 * self.PRIORITY_FACTORS['recency']
        
        # Factor 3: Age (20% weight)
        if goal.created_at:
            created = datetime.fromisoformat(goal.created_at)
            days_old = (datetime.now() - created).total_seconds() / 86400
            age = min(1.0, days_old / 30)  # Max out at 30 days
            score += age * self.PRIORITY_FACTORS['age']
        
        # Factor 4: Category (20% weight)
        category_weights = {"short_term": 1.0, "long_term": 0.7, "emergent": 0.5}
        score += category_weights.get(goal.category, 0.5) * self.PRIORITY_FACTORS['category']
        
        return min(1.0, score)
    
    def get_prioritized_goals(self, category: str = None) -> List[Goal]:
        """Get goals sorted by calculated priority."""
        # Update priorities
        for goal in self.goals:
            goal.priority = self.calculate_priority(goal)
        
        # Filter by category if specified
        filtered = self.goals
        if category:
            filtered = [g for g in self.goals if g.category == category]
        
        # Sort by priority
        sorted_goals = sorted(filtered, key=lambda g: g.priority, reverse=True)
        return sorted_goals
    
    def update_reward(self, goal_id: str, success: bool, 
                    progress: float = 0.0) -> bool:
        """Update goal reward based on outcome."""
        for goal in self.goals:
            if goal.id == goal_id:
                if success:
                    goal.reward_score = min(1.0, goal.reward_score + 0.15 + progress)
                else:
                    goal.reward_score = max(0.0, goal.reward_score - 0.1)
                
                goal.last_active = datetime.now().isoformat()
                self.save()
                return True
        return False
    
    def start_loop(self):
        """Start continuous goal loop (with safety bounds)."""
        self.start_time = datetime.now()
    
    def should_continue(self) -> bool:
        """Check if goal loop should continue (safety bounds)."""
        if not self.start_time:
            return False
        
        # Time budget check
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        if elapsed >= self.MAX_RUNTIME_MINUTES:
            return False
        
        # Check iteration bounds
        for goal in self.goals:
            if goal.iterations >= goal.max_iterations:
                return False
        
        return True
    
    def get_next_goal(self) -> Optional[Goal]:
        """Get next goal to work on."""
        active = [g for g in self.goals if g.status == "active"]
        if not active:
            return None
        
        prioritized = sorted(active, key=lambda g: self.calculate_priority(g), reverse=True)
        return prioritized[0] if prioritized else None
    
    def record_iteration(self, goal_id: str):
        """Record that an iteration was performed."""
        for goal in self.goals:
            if goal.id == goal_id:
                goal.iterations += 1
                goal.last_active = datetime.now().isoformat()
                
                # Auto-pause if max iterations reached
                if goal.iterations >= goal.max_iterations:
                    goal.status = "paused"
                
                self.save()
                return True
        return False
    
    def complete_goal(self, goal_id: str):
        """Mark a goal as completed."""
        for goal in self.goals:
            if goal.id == goal_id:
                goal.status = "completed"
                goal.last_active = datetime.now().isoformat()
                self.save()
                return True
        return False
    
    def abandon_goal(self, goal_id: str):
        """Mark a goal as abandoned."""
        for goal in self.goals:
            if goal.id == goal_id:
                goal.status = "abandoned"
                goal.last_active = datetime.now().isoformat()
                self.save()
                return True
        return False
    
    def evolve_from_reflection(self, goals: GoalSet, reflection: Dict) -> GoalSet:
        """Minimal goal evolution heuristic."""
        lessons = reflection.get("lessons", []) if isinstance(reflection, dict) else []
        if any("reliability" in str(x).lower() for x in lessons):
            if "maintain_task_reliability" not in goals.short_term:
                goals.short_term.insert(0, "maintain_task_reliability")
        if any("memory" in str(x).lower() for x in lessons):
            if "improve_memory_continuity" not in goals.long_term:
                goals.long_term.append("improve_memory_continuity")
        return goals
    
    def get_status(self) -> Dict:
        """Get goal engine status."""
        active = len([g for g in self.goals if g.status == "active"])
        completed = len([g for g in self.goals if g.status == "completed"])
        paused = len([g for g in self.goals if g.status == "paused"])
        
        return {
            "total": len(self.goals),
            "active": active,
            "completed": completed,
            "paused": paused,
            "runtime_minutes": (datetime.now() - self.start_time).total_seconds() / 60 if self.start_time else 0
        }
