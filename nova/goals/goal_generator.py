"""Goal Generator - Creates objectives for NOVA"""
import random

class GoalGenerator:
    def __init__(self):
        self.goals = []
        self.goal_templates = [
            "improve_trading_accuracy",
            "learn_new_pattern",
            "optimize_strategy",
            "reduce_risk",
            "explore_markets"
        ]
    
    def generate(self):
        goal = random.choice(self.goal_templates)
        self.goals.append(goal)
        return goal
    
    def get_goals(self):
        return self.goals
