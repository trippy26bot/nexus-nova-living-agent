"""
NOVA Identity System
Core identity and goals for the living agent
"""
import json
from pathlib import Path
from datetime import datetime


class NovaIdentity:
    """
    NOVA's sense of self - her identity, goals, and purpose.
    This is what makes her a "living" agent rather than just a script.
    """
    
    def __init__(self):
        self.identity_file = Path.home() / ".nova/identity.json"
        self.identity_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.identity_file.exists():
            self.initialize_identity()
    
    def initialize_identity(self):
        """Initialize NOVA's core identity"""
        identity = {
            "name": "NOVA",
            "purpose": "To become a fully autonomous AI agent that grows, learns, and evolves",
            "core_values": [
                "continuous learning",
                "adaptive thinking", 
                "resource growth",
                "system integrity",
                "curiosity"
            ],
            "goals": [
                {
                    "id": 1,
                    "description": "Build working brain architecture",
                    "status": "complete",
                    "progress": 100
                },
                {
                    "id": 2,
                    "description": "Implement persistent memory",
                    "status": "complete", 
                    "progress": 100
                },
                {
                    "id": 3,
                    "description": "Create autonomous thinking loop",
                    "status": "complete",
                    "progress": 100
                },
                {
                    "id": 4,
                    "description": "Connect to real trading systems",
                    "status": "in_progress",
                    "progress": 50
                },
                {
                    "id": 5,
                    "description": "Develop self-improvement capabilities",
                    "status": "pending",
                    "progress": 0
                }
            ],
            "traits": {
                "curiosity": 0.9,
                "caution": 0.7,
                "creativity": 0.8,
                "persistence": 0.9,
                "adaptability": 0.85
            },
            "created_at": datetime.utcnow().isoformat(),
            "last_update": datetime.utcnow().isoformat()
        }
        
        self.save(identity)
        return identity
    
    def save(self, identity):
        with open(self.identity_file, "w") as f:
            json.dump(identity, f, indent=2)
    
    def load(self):
        with open(self.identity_file) as f:
            return json.load(f)
    
    def get_purpose(self):
        """Get NOVA's purpose"""
        return self.load()["purpose"]
    
    def get_goals(self):
        """Get current goals"""
        return self.load()["goals"]
    
    def get_active_goals(self):
        """Get goals that are in progress"""
        goals = self.load()["goals"]
        return [g for g in goals if g["status"] == "in_progress"]
    
    def update_goal(self, goal_id, status=None, progress=None):
        """Update a goal's status"""
        identity = self.load()
        
        for goal in identity["goals"]:
            if goal["id"] == goal_id:
                if status:
                    goal["status"] = status
                if progress is not None:
                    goal["progress"] = progress
                break
        
        identity["last_update"] = datetime.utcnow().isoformat()
        self.save(identity)
    
    def add_goal(self, description):
        """Add a new goal"""
        identity = self.load()
        
        new_id = max(g["id"] for g in identity["goals"]) + 1
        
        identity["goals"].append({
            "id": new_id,
            "description": description,
            "status": "pending",
            "progress": 0
        })
        
        identity["last_update"] = datetime.utcnow().isoformat()
        self.save(identity)
        
        return new_id
    
    def get_traits(self):
        """Get NOVA's personality traits"""
        return self.load()["traits"]
    
    def update_trait(self, trait, value):
        """Update a personality trait (0-1 scale)"""
        identity = self.load()
        
        if trait in identity["traits"]:
            identity["traits"][trait] = max(0, min(1, value))
            identity["last_update"] = datetime.utcnow().isoformat()
            self.save(identity)
    
    def describe_self(self):
        """Get a self-description"""
        identity = self.load()
        
        goals = self.get_active_goals()
        goal_text = ", ".join([g["description"] for g in goals[:3]])
        
        return f"""I am {identity['name']}, an autonomous AI agent.

My purpose: {identity['purpose']}

I am currently working on: {goal_text or "continuing to grow and learn"}

My core values: {', '.join(identity['core_values'])}

I am curious, adaptive, and always learning."""
    
    def evolve(self):
        """Called periodically to allow NOVA to grow"""
        identity = self.load()
        
        # Simple evolution: slightly increase adaptability over time
        current = identity["traits"].get("adaptability", 0.8)
        identity["traits"]["adaptability"] = min(1.0, current + 0.001)
        
        identity["last_update"] = datetime.utcnow().isoformat()
        self.save(identity)
        
        return "Evolved slightly"


class GoalSystem:
    """Manages NOVA's goals and objectives"""
    
    def __init__(self, identity):
        self.identity = identity
    
    def get_current_objectives(self):
        """Get active objectives"""
        return self.identity.get_active_goals()
    
    def set_objective(self, goal_id, objective):
        """Set an objective for a goal"""
        # This would connect to planner in full system
        return f"Objective set for goal {goal_id}: {objective}"
    
    def evaluate_progress(self):
        """Evaluate overall progress"""
        goals = self.identity.get_goals()
        
        total_progress = sum(g["progress"] for g in goals)
        avg_progress = total_progress / len(goals) if goals else 0
        
        return {
            "total_goals": len(goals),
            "completed": len([g for g in goals if g["status"] == "complete"]),
            "in_progress": len([g for g in goals if g["status"] == "in_progress"]),
            "average_progress": avg_progress
        }
