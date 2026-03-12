#!/usr/bin/env python3
"""
Nova Intelligence Expansion Engine
Invent new abilities, test them, keep what works
"""

import time
import random
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
from datetime import datetime


class IdeaGenerator:
    """Generates new ability ideas based on weaknesses"""
    
    def __init__(self):
        self.generators = {
            "speed": ["parallelize", "cache", "optimize", "precompute"],
            "accuracy": ["validate", "verify", "double_check", "ensemble"],
            "capability": ["add_tool", "new_skill", "expand_api", "enhance"],
            "reliability": ["add_retry", "add_fallback", "add_timeout", "add_backup"]
        }
    
    def generate(self, weakness: str, count: int = 5) -> List[Dict]:
        """Generate ideas to address a weakness"""
        ideas = []
        categories = list(self.generators.keys())
        
        for i in range(count):
            category = random.choice(categories)
            approach = random.choice(self.generators[category])
            
            idea = {
                "id": f"idea_{int(time.time())}_{i}",
                "weakness": weakness,
                "approach": approach,
                "category": category,
                "description": f"{approach} to improve {weakness}",
                "timestamp": datetime.now().isoformat()
            }
            ideas.append(idea)
        
        return ideas
    
    def generate_creative(self, context: Dict, count: int = 3) -> List[Dict]:
        """Generate creative ideas based on context"""
        ideas = []
        
        # Look at what's available
        available_tools = context.get("tools", [])
        current_skills = context.get("skills", [])
        recent_tasks = context.get("recent_tasks", [])
        
        # Generate combination ideas
        if available_tools and current_skills:
            for i in range(count):
                tool = random.choice(available_tools)
                skill = random.choice(current_skills)
                
                ideas.append({
                    "id": f"creative_{int(time.time())}_{i}",
                    "type": "combination",
                    "description": f"Combine {tool} with {skill}",
                    "tool": tool,
                    "skill": skill
                })
        
        return ideas
    
    def register_generator(self, category: str, approaches: List[str]):
        """Register new generator approaches"""
        self.generators[category] = approaches


class ExperimentLab:
    """Tests ideas safely in sandbox"""
    
    def __init__(self):
        self.experiments = []
        self.sandbox_enabled = True
    
    def test(self, idea: Dict, simulator: Optional[Callable] = None) -> Dict:
        """Test an idea in sandbox"""
        experiment = {
            "idea": idea,
            "timestamp": datetime.now().isoformat(),
            "status": "running"
        }
        
        if simulator:
            # Use custom simulator
            result = simulator(idea)
        else:
            # Default simulation - simple success/failure
            # In reality, this would run the actual code
            success_prob = 0.5 + random.random() * 0.4  # 50-90% success
            
            result = {
                "success": random.random() < success_prob,
                "performance_delta": random.uniform(-0.1, 0.5) if success_prob > 0.7 else random.uniform(-0.3, 0.1),
                "confidence": success_prob
            }
        
        experiment["result"] = result
        experiment["status"] = "completed"
        
        self.experiments.append(experiment)
        
        return {
            "experiment": experiment,
            "recommended": result.get("success", False)
        }
    
    def test_batch(self, ideas: List[Dict], simulator: Optional[Callable] = None) -> List[Dict]:
        """Test multiple ideas"""
        return [self.test(idea, simulator) for idea in ideas]
    
    def get_experiment(self, experiment_id: int) -> Optional[Dict]:
        """Get a specific experiment"""
        if 0 <= experiment_id < len(self.experiments):
            return self.experiments[experiment_id]
        return None
    
    def get_recent_experiments(self, limit: int = 10) -> List[Dict]:
        """Get recent experiments"""
        return self.experiments[-limit:]


class ImprovementValidator:
    """Determines if improvement is worth keeping"""
    
    def __init__(self, thresholds: Optional[Dict] = None):
        self.thresholds = thresholds or {
            "min_success_rate": 0.7,
            "min_performance_delta": 0.1,
            "min_confidence": 0.6
        }
    
    def validate(self, result: Dict) -> bool:
        """Validate if experiment result is worth keeping"""
        if not result.get("success", False):
            return False
        
        if result.get("confidence", 0) < self.thresholds["min_confidence"]:
            return False
        
        if result.get("performance_delta", 0) < self.thresholds["min_performance_delta"]:
            return False
        
        return True
    
    def score(self, result: Dict) -> float:
        """Score an experiment result"""
        if not result.get("success", False):
            return 0.0
        
        confidence = result.get("confidence", 0.5)
        performance = result.get("performance_delta", 0)
        
        return confidence * 0.6 + max(0, performance) * 0.4


class AbilityRegistry:
    """Stores new abilities"""
    
    def __init__(self):
        self.abilities = {}
        self.ability_history = []
    
    def add(self, ability: Dict) -> str:
        """Add a new ability"""
        ability_id = ability.get("id", f"ability_{len(self.abilities)}")
        
        self.abilities[ability_id] = {
            **ability,
            "added_at": datetime.now().isoformat(),
            "times_used": 0,
            "success_rate": 0.0
        }
        
        self.ability_history.append(ability_id)
        
        return ability_id
    
    def get(self, ability_id: str) -> Optional[Dict]:
        """Get an ability"""
        return self.abilities.get(ability_id)
    
    def get_all(self) -> Dict[str, Dict]:
        """Get all abilities"""
        return dict(self.abilities)
    
    def update_usage(self, ability_id: str, success: bool):
        """Update ability usage statistics"""
        if ability_id in self.abilities:
            ability = self.abilities[ability_id]
            ability["times_used"] += 1
            
            # Update success rate
            total = ability["times_used"]
            current_rate = ability["success_rate"]
            ability["success_rate"] = (current_rate * (total - 1) + (1 if success else 0)) / total
    
    def remove(self, ability_id: str) -> bool:
        """Remove an ability"""
        if ability_id in self.abilities:
            del self.abilities[ability_id]
            return True
        return False


class ExpansionEngine:
    """Core intelligence expansion engine"""
    
    def __init__(self):
        self.idea_generator = IdeaGenerator()
        self.experiment_lab = ExperimentLab()
        self.validator = ImprovementValidator()
        self.registry = AbilityRegistry()
        
        self.expansion_enabled = True
        self.auto_expand = False
        self.expansion_history = []
    
    def expand(self, weakness: str = None, context: Dict = None) -> Dict:
        """Run expansion cycle"""
        if not self.expansion_enabled:
            return {"expanded": False, "reason": "disabled"}
        
        # Generate ideas
        if weakness:
            ideas = self.idea_generator.generate(weakness)
        elif context:
            ideas = self.idea_generator.generate_creative(context)
        else:
            return {"expanded": False, "reason": "no_context"}
        
        # Test ideas
        results = self.experiment_lab.test_batch(ideas)
        
        # Validate and add successful ones
        added = []
        for i, result in enumerate(results):
            if self.validator.validate(result.get("result", {})):
                ability = ideas[i]
                ability_id = self.registry.add(ability)
                added.append(ability_id)
        
        # Record expansion
        expansion = {
            "timestamp": datetime.now().isoformat(),
            "weakness": weakness,
            "ideas_tested": len(ideas),
            "abilities_added": len(added),
            "added_ids": added
        }
        self.expansion_history.append(expansion)
        
        return {
            "expanded": len(added) > 0,
            "ideas_tested": len(ideas),
            "abilities_added": len(added),
            "new_abilities": added
        }
    
    def get_abilities(self) -> Dict[str, Dict]:
        """Get all registered abilities"""
        return self.registry.get_all()
    
    def use_ability(self, ability_id: str, success: bool):
        """Record ability usage"""
        self.registry.update_usage(ability_id, success)
    
    def get_stats(self) -> Dict:
        """Get expansion engine statistics"""
        return {
            "expansion_enabled": self.expansion_enabled,
            "auto_expand": self.auto_expand,
            "total_abilities": len(self.registry.abilities),
            "total_expansions": len(self.expansion_history),
            "experiments_run": len(self.experiment_lab.experiments)
        }
    
    def enable(self):
        """Enable expansion"""
        self.expansion_enabled = True
    
    def disable(self):
        """Disable expansion"""
        self.expansion_enabled = False
    
    def set_auto_expand(self, enabled: bool):
        """Set auto-expansion mode"""
        self.auto_expand = enabled


# Global instance
_expansion_engine = None

def get_expansion_engine() -> ExpansionEngine:
    global _expansion_engine
    if _expansion_engine is None:
        _expansion_engine = ExpansionEngine()
    return _expansion_engine


# Convenience functions
def expand_intelligence(weakness: str = None, context: Dict = None) -> Dict:
    """Run intelligence expansion"""
    return get_expansion_engine().expand(weakness, context)

def get_all_abilities() -> Dict[str, Dict]:
    """Get all registered abilities"""
    return get_expansion_engine().get_abilities()
