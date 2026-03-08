"""Goal Tracker - Tracks progress toward goals"""
class GoalTracker:
    def __init__(self):
        self.active_goals = {}
        self.completed = []
    
    def add_goal(self, goal_id, description):
        self.active_goals[goal_id] = {"description": description, "progress": 0}
    
    def update_progress(self, goal_id, progress):
        if goal_id in self.active_goals:
            self.active_goals[goal_id]["progress"] = progress
    
    def complete(self, goal_id):
        if goal_id in self.active_goals:
            self.completed.append(self.active_goals.pop(goal_id))
