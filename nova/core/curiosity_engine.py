"""
NOVA Curiosity and Goal Engine
Allows NOVA to generate her own objectives instead of waiting for commands
"""
import random
from datetime import datetime


class CuriosityEngine:
    """
    NOVA's curiosity system - drives exploration and learning
    """
    
    def __init__(self, memory_system):
        self.memory = memory_system
        self.exploration_history = []
        self.curiosity_topics = [
            "market_patterns",
            "brain_performance",
            "strategy_optimization",
            "new_markets",
            "system_improvement",
            "knowledge_gaps"
        ]
        self.curiosity_weights = {topic: 0.5 for topic in self.curiosity_topics}
    
    def evaluate_curiosity(self):
        """
        Evaluate what NOVA should be curious about.
        Returns list of topics to explore.
        """
        topics = []
        
        # Add randomness to exploration
        for topic in self.curiosity_topics:
            score = self.curiosity_weights.get(topic, 0.5)
            
            # Add random exploration
            score += random.uniform(-0.1, 0.1)
            
            if score > 0.4:
                topics.append(topic)
        
        return topics
    
    def generate_exploration_goal(self):
        """
        Generate a curiosity-driven goal.
        """
        topic = random.choice(self.evaluate_curiosity())
        
        # Generate topic-specific questions
        questions = {
            "market_patterns": [
                "What patterns led to my best trades?",
                "Are there recurring market conditions?",
                "What timeframes show strongest signals?"
            ],
            "brain_performance": [
                "Which brains are most accurate?",
                "Should I adjust brain weights?",
                "Are any brains counterproductive?"
            ],
            "strategy_optimization": [
                "How can I improve my win rate?",
                "What position sizing works best?",
                "Should I change trade frequency?"
            ],
            "new_markets": [
                "Are there new markets to explore?",
                "What markets have high liquidity?",
                "Should I diversify?"
            ],
            "system_improvement": [
                "What would make me faster?",
                "How can I reduce errors?",
                "What parts need updating?"
            ],
            "knowledge_gaps": [
                "What don't I know that matters?",
                "What information am I missing?",
                "What should I research?"
            ]
        }
        
        question = random.choice(questions.get(topic, ["What should I learn?"]))
        
        return {
            "type": "curiosity",
            "topic": topic,
            "question": question,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def update_curiosity(self, topic, result):
        """
        Update curiosity based on exploration result.
        """
        if topic in self.curiosity_weights:
            if result.get("valuable", False):
                self.curiosity_weights[topic] = min(1.0, self.curiosity_weights[topic] + 0.1)
            else:
                self.curiosity_weights[topic] = max(0.1, self.curiosity_weights[topic] - 0.05)
    
    def get_curiosity_report(self):
        """Get current curiosity state"""
        return {
            "topics": self.curiosity_topics,
            "weights": self.curiosity_weights,
            "explorations": len(self.exploration_history)
        }


class GoalEngine:
    """
    NOVA's goal system - creates and manages objectives
    """
    
    def __init__(self, identity, memory_system):
        self.identity = identity
        self.memory = memory_system
        self.active_goals = []
        self.completed_goals = []
        self.goal_templates = self._init_goal_templates()
    
    def _init_goal_templates(self):
        """Initialize goal templates"""
        return {
            "improve_accuracy": {
                "description": "Improve trading accuracy",
                "target": 0.65,
                "metric": "win_rate",
                "actions": ["analyze_brains", "adjust_weights", "test_strategies"]
            },
            "learn_pattern": {
                "description": "Learn a new market pattern",
                "target": 3,
                "metric": "patterns_found",
                "actions": ["analyze_history", "test_hypothesis", "store_knowledge"]
            },
            "reduce_drawdown": {
                "description": "Reduce maximum drawdown",
                "target": 0.08,
                "metric": "max_drawdown",
                "actions": ["analyze_losses", "adjust_risk", "test_changes"]
            },
            "expand_knowledge": {
                "description": "Expand knowledge base",
                "target": 10,
                "metric": "new_memories",
                "actions": ["research", "explore", "store"]
            },
            "optimize_execution": {
                "description": "Improve execution speed",
                "target": 0.5,
                "metric": "execution_time",
                "actions": ["profile_system", "optimize_code", "test"]
            }
        }
    
    def generate_goal(self, goal_type=None):
        """
        Generate a new goal.
        """
        if goal_type is None:
            goal_type = random.choice(list(self.goal_templates.keys()))
        
        template = self.goal_templates.get(goal_type, self.goal_templates["expand_knowledge"])
        
        goal = {
            "id": f"goal_{datetime.utcnow().timestamp()}",
            "type": goal_type,
            "description": template["description"],
            "target": template["target"],
            "metric": template["metric"],
            "actions": template["actions"],
            "progress": 0,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.active_goals.append(goal)
        
        return goal
    
    def update_progress(self, goal_id, progress):
        """Update progress on a goal"""
        for goal in self.active_goals:
            if goal["id"] == goal_id:
                goal["progress"] = progress
                goal["updated_at"] = datetime.utcnow().isoformat()
                
                # Check completion
                if progress >= goal["target"]:
                    self.complete_goal(goal_id)
                
                break
    
    def complete_goal(self, goal_id):
        """Mark a goal as completed"""
        for goal in self.active_goals:
            if goal["id"] == goal_id:
                goal["status"] = "completed"
                goal["completed_at"] = datetime.utcnow().isoformat()
                self.completed_goals.append(goal)
                self.active_goals.remove(goal)
                break
    
    def get_active_goals(self):
        """Get all active goals"""
        return self.active_goals
    
    def get_goals_summary(self):
        """Get summary of all goals"""
        return {
            "active": len(self.active_goals),
            "completed": len(self.completed_goals),
            "goals": self.active_goals[:5]
        }
    
    def evaluate_goals(self):
        """
        Evaluate current goals and progress.
        Returns suggested actions.
        """
        suggestions = []
        
        for goal in self.active_goals:
            progress_pct = (goal["progress"] / goal["target"]) * 100 if goal["target"] > 0 else 0
            
            if progress_pct < 10:
                suggestions.append({
                    "goal_id": goal["id"],
                    "suggestion": f"Little progress on {goal['description']}. Try: {goal['actions'][0]}",
                    "priority": "high"
                })
            elif progress_pct < 50:
                suggestions.append({
                    "goal_id": goal["id"],
                    "suggestion": f"Making progress on {goal['description']}. Continue with: {goal['actions'][1]}",
                    "priority": "medium"
                })
        
        return suggestions


class AutonomousDrive:
    """
    Combines curiosity and goals to drive NOVA's autonomous behavior.
    This is what makes her "alive" instead of just reactive.
    """
    
    def __init__(self, identity, memory_system):
        self.identity = identity
        self.memory = memory_system
        self.curiosity = CuriosityEngine(memory_system)
        self.goals = GoalEngine(identity, memory_system)
        self.cycle_count = 0
    
    def evaluate_state(self):
        """
        Evaluate current state and determine what to do.
        This is NOVA's "thought process" when not given a command.
        """
        self.cycle_count += 1
        
        # Check existing goals
        suggestions = self.goals.evaluate_goals()
        
        # Every 10 cycles, generate curiosity-driven goal
        if self.cycle_count % 10 == 0:
            curiosity_goal = self.curiosity.generate_exploration_goal()
            return {
                "type": "curiosity",
                "goal": curiosity_goal,
                "suggestions": suggestions
            }
        
        # If there are active suggestions, pursue them
        if suggestions:
            return {
                "type": "goal_focused",
                "suggestion": suggestions[0],
                "goals": self.goals.get_goals_summary()
            }
        
        # Default: generate new goal if none active
        if not self.goals.get_active_goals():
            new_goal = self.goals.generate_goal()
            return {
                "type": "new_goal",
                "goal": new_goal
            }
        
        return {
            "type": "continue",
            "status": "working_on_goals",
            "goals": self.goals.get_goals_summary()
        }
    
    def get_autonomy_report(self):
        """Get full autonomy status"""
        return {
            "curiosity": self.curiosity.get_curiosity_report(),
            "goals": self.goals.get_goals_summary(),
            "total_cycles": self.cycle_count
        }
