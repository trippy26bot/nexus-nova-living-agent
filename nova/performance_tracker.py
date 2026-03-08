"""
Nexus Nova Living Agent - Performance Tracker
Tracks agent performance for smart task delegation
"""
from datetime import datetime, timedelta
from collections import defaultdict

class PerformanceTracker:
    """NOVA tracks agent performance to optimize delegation"""
    
    def __init__(self):
        self.records = defaultdict(list)  # agent_name -> [task results]
        
    def log_task(self, agent_name: str, task: str, success: bool = True, efficiency: float = 1.0):
        """Log a task result for an agent"""
        self.records[agent_name].append({
            "task": task,
            "success": success,
            "efficiency": efficiency,
            "timestamp": datetime.now()
        })
        
        # Keep last 50 records per agent
        if len(self.records[agent_name]) > 50:
            self.records[agent_name] = self.records[agent_name][-50:]
            
    def get_score(self, agent_name: str) -> float:
        """Get performance score 0-1 for an agent"""
        records = self.records.get(agent_name, [])
        if not records:
            return 0.5  # neutral if no history
            
        # Weighted score: success * efficiency
        scores = []
        for r in records:
            base = 1.0 if r["success"] else 0.3
            scores.append(base * r["efficiency"])
            
        return sum(scores) / len(scores)
        
    def get_best_agent(self, agent_names: list) -> str:
        """Return the agent with highest score"""
        if not agent_names:
            return None
            
        best = max(agent_names, key=lambda n: self.get_score(n))
        return best
        
    def get_all_scores(self) -> dict:
        """Get scores for all agents"""
        return {name: self.get_score(name) for name in self.records.keys()}
