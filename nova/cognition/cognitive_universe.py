#!/usr/bin/env python3
"""
Nova Cognitive Universe
Internal agent civilization that debates and solves problems
"""

import time
from typing import Dict, List, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


class UniverseAgent:
    """A thinking agent inside Nova's mind"""
    
    def __init__(self, agent_type: str, specialty: str):
        self.id = f"{agent_type}_{int(time.time() * 1000) % 10000}"
        self.type = agent_type
        self.specialty = specialty
        self.thinking_style = self._get_thinking_style(agent_type)
        self.result = None
        self.confidence = 0.5
    
    def _get_thinking_style(self, agent_type: str) -> str:
        styles = {
            "strategist": "long-term planning and goal orientation",
            "scientist": "evidence-based analysis",
            "engineer": "practical implementation focus",
            "critic": "risk identification and flaw detection",
            "optimist": "opportunity recognition",
            "realist": "constraint awareness",
            "creative": "novel solution generation",
            "guardian": "safety and ethics",
            "philosopher": "deep reasoning and meaning",
            "historian": "pattern recognition from past"
        }
        return styles.get(agent_type, "general thinking")
    
    def think(self, task: Any, processor: Callable) -> Dict:
        """Run thinking process"""
        try:
            result = processor(task, self.type)
            self.result = result
            self.confidence = self._assess_confidence(result)
        except Exception as e:
            self.result = {"error": str(e)}
            self.confidence = 0.0
        
        return {
            "agent_id": self.id,
            "agent_type": self.type,
            "specialty": self.specialty,
            "thinking_style": self.thinking_style,
            "result": self.result,
            "confidence": self.confidence
        }
    
    def _assess_confidence(self, result: Any) -> float:
        """Assess confidence in result"""
        if result is None:
            return 0.0
        if isinstance(result, dict) and "error" in result:
            return 0.0
        # Base confidence
        return min(0.95, 0.5 + (len(str(result)) / 1000))


class CognitiveUniverse:
    """
    Nova spawns internal agents to collaborate on problems
    """
    
    # Agent templates for different complexity levels
    AGENT_SETS = {
        "simple": ["engineer", "critic"],
        "normal": ["strategist", "engineer", "critic", "optimist"],
        "complex": ["strategist", "scientist", "engineer", "critic", "optimist", "realist", "creative", "guardian"],
        "deep": ["strategist", "scientist", "engineer", "critic", "optimist", "realist", "creative", "guardian", "philosopher", "historian"]
    }
    
    def __init__(self):
        self.universe_history = []
    
    def spawn_agents(self, complexity: str = "normal") -> List[UniverseAgent]:
        """Spawn thinking agents based on complexity"""
        agent_types = self.AGENT_SETS.get(complexity, self.AGENT_SETS["normal"])
        
        agents = []
        for agent_type in agent_types:
            agent = UniverseAgent(agent_type, self._get_specialty(agent_type))
            agents.append(agent)
        
        return agents
    
    def _get_specialty(self, agent_type: str) -> str:
        specialties = {
            "strategist": "planning and goals",
            "scientist": "analysis and evidence",
            "engineer": "implementation",
            "critic": "risk and flaws",
            "optimist": "opportunities",
            "realist": "constraints",
            "creative": "novelty",
            "guardian": "safety",
            "philosopher": "meaning",
            "historian": "patterns"
        }
        return specialties.get(agent_type, "general")
    
    def debate(self, task: Any, processor: Callable, complexity: str = "normal") -> Dict:
        """Run a debate between agents"""
        # Spawn agents
        agents = self.spawn_agents(complexity)
        
        # Run all agents in parallel
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            results = list(executor.map(
                lambda a: a.think(task, processor),
                agents
            ))
        
        # Score and rank
        ranked = sorted(results, key=lambda x: x.get("confidence", 0), reverse=True)
        
        # Consensus check (do top agents agree?)
        consensus = False
        if len(ranked) >= 2:
            top_result = str(ranked[0].get("result", ""))[:100]
            second_result = str(ranked[1].get("result", ""))[:100]
            consensus = top_result == second_result
        
        debate_result = {
            "task": str(task)[:100],
            "agents_spawned": len(agents),
            "results": results,
            "best_result": ranked[0] if ranked else None,
            "ranking": ranked,
            "consensus": consensus,
            "timestamp": datetime.now().isoformat()
        }
        
        self.universe_history.append(debate_result)
        
        return debate_result
    
    def simulate_debate(self, task: Any, processor: Callable, iterations: int = 3) -> Dict:
        """Run multiple debate rounds and iterate"""
        best_overall = None
        best_score = -1
        all_rounds = []
        
        for i in range(iterations):
            result = self.debate(task, processor, complexity="normal")
            round_score = result["best_result"].get("confidence", 0) if result["best_result"] else 0
            
            all_rounds.append({
                "iteration": i,
                "result": result,
                "score": round_score
            })
            
            if round_score > best_score:
                best_score = round_score
                best_overall = result
            
            # Early exit if confident enough
            if round_score >= 0.9:
                break
        
        return {
            "best_result": best_overall["best_result"] if best_overall else None,
            "iterations": len(all_rounds),
            "rounds": all_rounds,
            "final_score": best_score
        }
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent debate history"""
        return self.universe_history[-limit:]
    
    def get_stats(self) -> Dict:
        """Get universe statistics"""
        return {
            "total_debates": len(self.universe_history),
            "agent_types_available": list(self.AGENT_SETS.keys())
        }


# Global instance
_cognitive_universe = None

def get_cognitive_universe() -> CognitiveUniverse:
    global _cognitive_universe
    if _cognitive_universe is None:
        _cognitive_universe = CognitiveUniverse()
    return _cognitive_universe
