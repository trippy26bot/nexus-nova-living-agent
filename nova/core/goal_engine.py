"""
Goal Engine - gives Nova ambition, self-motivation, and long-term objectives
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from collections import defaultdict

logger = logging.getLogger("GoalEngine")

class GoalPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class GoalStatus(Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    PROGRESS = "progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class Goal:
    def __init__(self, goal_id: str, description: str, priority: GoalPriority = GoalPriority.MEDIUM):
        self.id = goal_id
        self.description = description
        self.priority = priority
        self.status = GoalStatus.PROPOSED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.progress = 0.0  # 0-100%
        self.milestones: List[Dict] = []
        self.tags: List[str] = []
        self.creator = "system"  # system, user, or brain name
        
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority.name,
            "status": self.status.value,
            "progress": self.progress,
            "created": self.created_at.isoformat(),
            "updated": self.updated_at.isoformat(),
            "milestones": self.milestones,
            "tags": self.tags,
            "creator": self.creator
        }


class GoalEngine:
    """
    Nova's Goal Engine - manages long-term objectives and self-directed learning.
    """
    
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.completed_goals: List[Goal] = []
        self.failed_goals: List[Goal] = []
        
        # Goal categories
        self.categories = {
            "trading": [],      # Improve trading strategies
            "learning": [],     # Self-improvement
            "research": [],     # Explore new ideas
            "creative": [],    # Art, poetry, exploration
            "system": []       # Technical improvements
        }
        
        # Goal templates for common objectives
        self.templates = {
            "improve_strategy": {
                "description": "Improve {asset} strategy performance",
                "priority": GoalPriority.HIGH,
                "milestones": ["analyze historical performance", "identify weaknesses", "test new parameters", "deploy"]
            },
            "reduce_drawdown": {
                "description": "Reduce portfolio drawdown to under {threshold}%",
                "priority": GoalPriority.CRITICAL,
                "milestones": ["analyze risk factors", "implement stops", "test in simulation", "deploy"]
            },
            "learn_skill": {
                "description": "Learn {skill} capability",
                "priority": GoalPriority.MEDIUM,
                "milestones": ["research approach", "practice in sandbox", "integrate into workflow"]
            },
            "explore_idea": {
                "description": "Explore: {topic}",
                "priority": GoalPriority.LOW,
                "milestones": ["research", "document findings", "share insights"]
            }
        }
        
        # Auto-generated goals tracking
        self.auto_goals_generated = 0
        self.last_goal_review = datetime.now()
        self.goal_review_interval = 3600  # 1 hour
        
        logger.info("GoalEngine initialized")
    
    # ─────────────────────────────────────────────────────────────
    # GOAL CREATION
    # ─────────────────────────────────────────────────────────────
    
    def create_goal(self, description: str, priority: GoalPriority = GoalPriority.MEDIUM, 
                   category: str = "system", tags: List[str] = None) -> Goal:
        """Create a new goal"""
        goal_id = f"goal_{int(time.time() * 1000)}"
        goal = Goal(goal_id, description, priority)
        goal.tags = tags or []
        goal.creator = "system"
        
        self.goals[goal_id] = goal
        self.categories.setdefault(category, []).append(goal_id)
        
        logger.info(f"Goal created: {goal_id} - {description}")
        self.auto_goals_generated += 1
        
        return goal
    
    def create_from_template(self, template_name: str, params: Dict = None) -> Goal:
        """Create a goal from a template"""
        params = params or {}
        
        if template_name not in self.templates:
            logger.warning(f"Unknown template: {template_name}")
            return None
        
        template = self.templates[template_name]
        description = template["description"].format(**params)
        
        goal = self.create_goal(
            description=description,
            priority=template["priority"],
            tags=[template_name]
        )
        
        # Add milestones
        for milestone in template["milestones"]:
            goal.milestones.append({
                "name": milestone,
                "completed": False,
                "completed_at": None
            })
        
        return goal
    
    def create_user_goal(self, description: str, priority: GoalPriority = GoalPriority.HIGH) -> Goal:
        """Create a goal from user request"""
        goal = self.create_goal(description, priority, tags=["user"])
        goal.creator = "user"
        return goal
    
    # ─────────────────────────────────────────────────────────────
    # GOAL MANAGEMENT
    # ─────────────────────────────────────────────────────────────
    
    def activate_goal(self, goal_id: str) -> bool:
        """Activate a proposed goal"""
        if goal_id not in self.goals:
            logger.warning(f"Goal not found: {goal_id}")
            return False
        
        goal = self.goals[goal_id]
        if goal.status != GoalStatus.PROPOSED:
            logger.warning(f"Goal {goal_id} cannot be activated from {goal.status}")
            return False
        
        goal.status = GoalStatus.ACTIVE
        goal.updated_at = datetime.now()
        
        logger.info(f"Goal activated: {goal_id}")
        return True
    
    def update_progress(self, goal_id: str, progress: float) -> bool:
        """Update goal progress"""
        if goal_id not in self.goals:
            return False
        
        goal = self.goals[goal_id]
        goal.progress = min(100.0, max(0.0, progress))
        goal.updated_at = datetime.now()
        
        if goal.progress >= 100:
            self.complete_goal(goal_id)
        
        return True
    
    def complete_goal(self, goal_id: str) -> bool:
        """Mark goal as completed"""
        if goal_id not in self.goals:
            return False
        
        goal = self.goals[goal_id]
        goal.status = GoalStatus.COMPLETED
        goal.progress = 100.0
        goal.updated_at = datetime.now()
        
        self.completed_goals.append(goal)
        del self.goals[goal_id]
        
        logger.info(f"Goal completed: {goal_id}")
        return True
    
    def fail_goal(self, goal_id: str, reason: str = "") -> bool:
        """Mark goal as failed"""
        if goal_id not in self.goals:
            return False
        
        goal = self.goals[goal_id]
        goal.status = GoalStatus.FAILED
        goal.updated_at = datetime.now()
        
        self.failed_goals.append(goal)
        del self.goals[goal_id]
        
        logger.info(f"Goal failed: {goal_id} - {reason}")
        return True
    
    # ─────────────────────────────────────────────────────────────
    # GOAL GENERATION
    # ─────────────────────────────────────────────────────────────
    
    def generate_goals_from_performance(self, performance_data: Dict) -> List[Goal]:
        """Auto-generate goals based on performance"""
        new_goals = []
        
        # Example: if drawdown is high
        drawdown = performance_data.get("drawdown", 0)
        if drawdown > 10:
            goal = self.create_from_template("reduce_drawdown", {"threshold": "10"})
            new_goals.append(goal)
        
        # Example: if strategy underperforming
        sharpe = performance_data.get("sharpe_ratio", 0)
        if sharpe < 1.0:
            goal = self.create_from_template("improve_strategy", {"asset": "portfolio"})
            new_goals.append(goal)
        
        return new_goals
    
    def propose_exploration_goals(self, topics: List[str]) -> List[Goal]:
        """Propose exploration goals"""
        goals = []
        for topic in topics:
            goal = self.create_from_template("explore_idea", {"topic": topic})
            goal.priority = GoalPriority.LOW
            goals.append(goal)
        return goals
    
    # ─────────────────────────────────────────────────────────────
    # QUERY METHODS
    # ─────────────────────────────────────────────────────────────
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals"""
        return [g for g in self.goals.values() if g.status in [GoalStatus.ACTIVE, GoalStatus.PROGRESS]]
    
    def get_goals_by_priority(self, priority: GoalPriority) -> List[Goal]:
        """Get goals by priority"""
        return [g for g in self.goals.values() if g.priority == priority]
    
    def get_goals_by_category(self, category: str) -> List[Goal]:
        """Get goals by category"""
        goal_ids = self.categories.get(category, [])
        return [self.goals[gid] for gid in goal_ids if gid in self.goals]
    
    def get_top_priority_goal(self) -> Optional[Goal]:
        """Get the highest priority goal"""
        active = self.get_active_goals()
        if not active:
            return None
        
        return min(active, key=lambda g: g.priority.value)
    
    # ─────────────────────────────────────────────────────────────
    # REPORTING
    # ─────────────────────────────────────────────────────────────
    
    def get_summary(self) -> Dict:
        """Get goal engine summary"""
        return {
            "active_goals": len(self.get_active_goals()),
            "completed": len(self.completed_goals),
            "failed": len(self.failed_goals),
            "auto_generated": self.auto_goals_generated,
            "by_priority": {
                "critical": len(self.get_goals_by_priority(GoalPriority.CRITICAL)),
                "high": len(self.get_goals_by_priority(GoalPriority.HIGH)),
                "medium": len(self.get_goals_by_priority(GoalPriority.MEDIUM)),
                "low": len(self.get_goals_by_priority(GoalPriority.LOW))
            }
        }
    
    def get_report(self) -> str:
        """Get human-readable goal report"""
        summary = self.get_summary()
        
        lines = [
            "=== NOVA GOAL ENGINE ===",
            f"Active Goals: {summary['active_goals']}",
            f"Completed: {summary['completed']}",
            f"Failed: {summary['failed']}",
            "",
            "By Priority:",
            f"  Critical: {summary['by_priority']['critical']}",
            f"  High: {summary['by_priority']['high']}",
            f"  Medium: {summary['by_priority']['medium']}",
            f"  Low: {summary['by_priority']['low']}",
            "",
            "Active Goals:"
        ]
        
        for goal in self.get_active_goals():
            lines.append(f"  [{goal.priority.name}] {goal.description} ({goal.progress:.0f}%)")
        
        return "\n".join(lines)


# Global goal engine instance
_goal_engine = None

def get_goal_engine() -> GoalEngine:
    """Get or create global goal engine"""
    global _goal_engine
    if _goal_engine is None:
        _goal_engine = GoalEngine()
    return _goal_engine
