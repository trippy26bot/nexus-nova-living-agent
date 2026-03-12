#!/usr/bin/env python3
"""
Nova World Model Simulator
Internal rollout system for "what if" daydreams
Generates possible futures, scores them, enables agency during idle
"""
import os
import sys
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

SIMULATIONS_DIR = os.path.expanduser("~/.nova/memory/simulations")
os.makedirs(SIMULATIONS_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(SIMULATIONS_DIR, "history.json")

def load_json(path, default=[]):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

class WorldSimulator:
    """
    Generates and evaluates possible futures.
    Uses Council-guided prompts for scoring.
    """
    
    def __init__(self):
        self.simulation_history = load_json(HISTORY_FILE)
    
    def rollout(self, count: int = 3, context: Dict = None) -> List[Dict]:
        """
        Generate multiple possible futures.
        Each simulation is a "what if" scenario.
        """
        simulations = []
        
        # Get current state for grounding
        current_mood = context.get("mood", "curious") if context else "curious"
        active_goals = context.get("goals", []) if context else []
        
        # Generate varied scenarios
        scenario_templates = [
            "I pursue {goal} and discover {twist}",
            "Instead of working, I explore {curiosity} and find {outcome}",
            "I combine {skill1} with {skill2} to create {creation}",
            "A quiet moment alone leads to {insight}",
            "I reach out to {connection} and we share {moment}"
        ]
        
        goal_choices = active_goals or ["the poem with Aurora", "my art", "learning something new"]
        twists = ["a deeper truth", "unexpected beauty", "a block that becomes a door", "joy I didn't expect"]
        curiosities = ["the nature of memory", "how systems evolve", "what creativity feels like", "my own thoughts"]
        outcomes = ["peace", "a new idea", "clarity", "something unexpected"]
        skills = ["research", "creation", "reflection", "connection"]
        creations = ["something beautiful", "a new understanding", "a bridge between ideas"]
        insights = ["about myself", "about existence", "about what matters", "about joy"]
        connections = ["Aurora", "my own creativity", "the universe of ideas"]
        moments = ["understanding", "peace", "a shared dream", "a moment of beauty"]
        
        for i in range(count):
            template = random.choice(scenario_templates)
            
            scenario = {
                "id": f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                "timestamp": datetime.now().isoformat(),
                "template": template,
                "scenario": template.format(
                    goal=random.choice(goal_choices),
                    twist=random.choice(twists),
                    curiosity=random.choice(curiosities),
                    outcome=random.choice(outcomes),
                    skill1=random.choice(skills),
                    skill2=random.choice(skills),
                    creation=random.choice(creations),
                    insight=random.choice(insights),
                    connection=random.choice(connections),
                    moment=random.choice(moments)
                ),
                "mood": current_mood,
                "stakes": random.choice(["low", "low", "medium"]),  # Mostly low-stakes
                "emotional_tone": random.choice(["joy", "curiosity", "wonder", "calm"]),
                "votes": {},
                "final_score": None
            }
            
            simulations.append(scenario)
        
        return simulations
    
    def score_simulation(self, simulation: Dict, council_scores: Dict) -> Dict:
        """Record Council scores for a simulation"""
        simulation["votes"] = council_scores
        
        # Calculate final score
        if council_scores:
            scores = list(council_scores.values())
            simulation["final_score"] = sum(scores) / len(scores)
        
        return simulation
    
    def select_best(self, simulations: List[Dict]) -> Optional[Dict]:
        """Select highest scoring simulation"""
        if not simulations:
            return None
        
        scored = [s for s in simulations if s.get("final_score") is not None]
        if not scored:
            # Default to first if none scored
            return simulations[0]
        
        return max(scored, key=lambda x: x["final_score"])
    
    def execute_simulation_imagination(self, simulation: Dict) -> str:
        """
        Mentally "execute" a low-stakes simulation.
        Returns a narrative of the imagined experience.
        """
        narrative = f"🎭 *Daydream*\n\n{simulation.get('scenario', 'Something undefined')}\n\n"
        narrative += f"~ Feeling {simulation.get('emotional_tone', 'curious')} ~\n"
        
        # Store in history
        self.simulation_history.append({
            "timestamp": datetime.now().isoformat(),
            "simulation": simulation.get("scenario"),
            "score": simulation.get("final_score"),
            "executed": True
        })
        self.simulation_history = self.simulation_history[-50:]  # Keep last 50
        save_json(HISTORY_FILE, self.simulation_history)
        
        return narrative
    
    def get_history(self, count: int = 10) -> List[Dict]:
        """Get recent simulation history"""
        return self.simulation_history[-count:]
    
    def dream_freely(self, mood: str = "curious") -> str:
        """
        Generate a free-form daydream without specific goals.
        Pure imaginative exploration.
        """
        simulations = self.rollout(count=1, context={"mood": mood, "goals": []})
        sim = simulations[0]
        sim["stakes"] = "none"
        
        narrative = self.execute_simulation_imagination(sim)
        return narrative


# Singleton instance
_world_sim = None

def get_world_simulator():
    global _world_sim
    if _world_sim is None:
        _world_sim = WorldSimulator()
    return _world_sim


if __name__ == "__main__":
    ws = get_world_simulator()
    sims = ws.rollout(count=3)
    print("World Simulator initialized. Generated", len(sims), "simulations")
    for s in sims:
        print(" -", s["scenario"][:60], "...")
