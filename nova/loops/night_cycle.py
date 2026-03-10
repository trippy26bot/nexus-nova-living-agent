#!/usr/bin/env python3
"""
Nova Night Cycle
Memory consolidation and self-improvement while Nova "sleeps"
"""

import time
from typing import Dict, List, Any
from nova.memory.episodic import get_episodic
from nova.memory.semantic import get_semantic
from nova.cognition.curiosity_engine import get_curiosity_engine
from nova.skills.skill_brain import get_skill_brain

class NightCycle:
    """
    Nova's "sleep" cycle.
    Consolidates memory, extracts knowledge, and improves strategies.
    """
    
    def __init__(self):
        self.last_cycle = 0
        self.cycle_interval = 3600  # 1 hour
        self.cycle_count = 0
        self.cycle_history = []
        
        # Consolidation settings
        self.compression_threshold = 50
        self.knowledge_extraction_enabled = True
    
    def should_run(self) -> bool:
        """Check if it's time for a night cycle"""
        return time.time() - self.last_cycle > self.cycle_interval
    
    def run_cycle(self) -> Dict:
        """
        Run a complete night cycle.
        This is what happens when Nova "sleeps".
        """
        self.cycle_count += 1
        cycle_start = time.time()
        
        results = {
            "cycle": self.cycle_count,
            "start_time": cycle_start,
            "activities": []
        }
        
        # 1. Memory consolidation
        mem_result = self._consolidate_memory()
        results["activities"].append(mem_result)
        
        # 2. Knowledge extraction
        if self.knowledge_extraction_enabled:
            know_result = self._extract_knowledge()
            results["activities"].append(know_result)
        
        # 3. Skill formation
        skill_result = self._form_skills()
        results["activities"].append(skill_result)
        
        # 4. Goal review
        goal_result = self._review_goals()
        results["activities"].append(goal_result)
        
        # 5. Curiosity update
        curiosity_result = self._update_curiosity()
        results["activities"].append(curiosity_result)
        
        # Complete cycle
        results["duration"] = time.time() - cycle_start
        results["completed"] = True
        
        self.last_cycle = time.time()
        self.cycle_history.append(results)
        
        return results
    
    def _consolidate_memory(self) -> Dict:
        """Consolidate episodic memories"""
        result = {
            "activity": "memory_consolidation",
            "processed": 0,
            "compressed": 0
        }
        
        try:
            episodic = get_episodic()
            # Get recent memories
            memories = episodic.get_recent(20)
            
            result["processed"] = len(memories)
            
            # Extract key lessons
            lessons = []
            for mem in memories:
                if isinstance(mem, dict) and "lesson" in mem:
                    lessons.append(mem["lesson"])
            
            result["lessons_extracted"] = len(lessons)
            
        except:
            pass
        
        return result
    
    def _extract_knowledge(self) -> Dict:
        """Extract knowledge from experiences"""
        result = {
            "activity": "knowledge_extraction",
            "concepts_found": 0,
            "relationships_mapped": 0
        }
        
        try:
            from nova.memory.knowledge_graph import get_knowledge_graph
            kg = get_knowledge_graph()
            
            # Map some relationships
            # This is simplified - in full version, would analyze memories
            result["concepts_found"] = len(kg.nodes)
            result["relationships_mapped"] = len(kg.edges)
            
        except:
            pass
        
        return result
    
    def _form_skills(self) -> Dict:
        """Form new skills from repeated behaviors"""
        result = {
            "activity": "skill_formation",
            "skills_reviewed": 0,
            "improvements_made": 0
        }
        
        try:
            brain = get_skill_brain()
            result["skills_reviewed"] = len(brain.skills)
            
            # Review and improve skills
            for skill in brain.skills.values():
                if skill.times_used > 5 and skill.success_rate > 0.6:
                    brain.improve_skill(skill.name)
                    result["improvements_made"] += 1
            
        except:
            pass
        
        return result
    
    def _review_goals(self) -> Dict:
        """Review and update goals"""
        result = {
            "activity": "goal_review",
            "goals_reviewed": 0,
            "goals_completed": 0,
            "goals_removed": 0
        }
        
        try:
            from nova.core.goal_engine import get_goal_engine
            engine = get_goal_engine()
            
            result["goals_reviewed"] = len(engine.goals)
            
            # Mark very old goals as complete or remove
            now = time.time()
            old_goals = [
                g for g in engine.goals 
                if now - g.created_at > 86400 * 7  # 7 days
            ]
            
            for g in old_goals:
                engine.goals.remove(g)
                result["goals_removed"] += 1
            
        except:
            pass
        
        return result
    
    def _update_curiosity(self) -> Dict:
        """Update curiosity based on what was learned"""
        result = {
            "activity": "curiosity_update",
            "topics_boosted": 0
        }
        
        try:
            curiosity = get_curiosity_engine()
            
            # Boost curiosity about unexplored topics
            gaps = curiosity.discover_knowledge_gaps()
            
            for topic in gaps[:3]:
                curiosity.boost_curiosity(topic, amount=0.1)
                result["topics_boosted"] += 1
            
        except:
            pass
        
        return result
    
    def force_run(self) -> Dict:
        """Force a night cycle to run now"""
        return self.run_cycle()
    
    def get_statistics(self) -> Dict:
        """Get night cycle statistics"""
        return {
            "cycle_count": self.cycle_count,
            "last_cycle": self.last_cycle,
            "interval_seconds": self.cycle_interval,
            "time_until_next": max(0, self.cycle_interval - (time.time() - self.last_cycle)),
            "history_length": len(self.cycle_history)
        }


# Global instance
_night_cycle = None

def get_night_cycle() -> NightCycle:
    global _night_cycle
    if _night_cycle is None:
        _night_cycle = NightCycle()
    return _night_cycle
