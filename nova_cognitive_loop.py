#!/usr/bin/env python3
"""
nova_cognitive_loop.py — Continuous cognitive loop for Nova.
Runs continuously, thinks, reflects, generates thoughts.
"""

import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class CognitiveLoop:
    """Continuous cognitive loop - Nova's "thinking" process."""
    
    def __init__(self):
        self.thinking = False
        self.thought_history: List[Dict] = []
        self.max_thoughts = 1000
        
        # Subsystems
        self.self_model = None
        self.goal_manager = None
        self.curiosity_engine = None
        self.memory_rehearsal = None
    
    def start(self):
        """Start the cognitive loop."""
        self.thinking = True
        self._loop()
    
    def stop(self):
        """Stop the cognitive loop."""
        self.thinking = False
    
    def _loop(self):
        """Main cognitive loop."""
        while self.thinking:
            try:
                # Observe
                observations = self._observe()
                
                # Generate thoughts
                thoughts = self._generate_thoughts(observations)
                
                # Store thoughts
                for thought in thoughts:
                    self._store_thought(thought)
                
                # Evaluate if action needed
                action = self._evaluate_action_needed(thoughts)
                
                if action:
                    self._execute_action(action)
                
                # Sleep between thinking cycles
                time.sleep(30)  # Think every 30 seconds
                
            except Exception as e:
                print(f"Cognitive loop error: {e}")
                time.sleep(60)
    
    def _observe(self) -> Dict:
        """Observe current state."""
        observations = {
            'time': datetime.now().isoformat(),
            'thought_count': len(self.thought_history),
        }
        
        # Get recent memories
        try:
            from nova import get_recent_memories
            recent = get_recent_memories(limit=5)
            observations['recent_memories'] = recent
        except:
            pass
        
        # Get current goals
        try:
            from nova_goal_engine import GoalEngine
            ge = GoalEngine()
            goals = ge.get_prioritized_goals()
            observations['active_goals'] = [g.description for g in goals[:3]]
        except:
            pass
        
        return observations
    
    def _generate_thoughts(self, observations: Dict) -> List[Dict]:
        """Generate internal thoughts based on observations."""
        thoughts = []
        
        # Thought types
        thought_types = [
            'reflection',
            'curiosity',
            'memory_link',
            'goal_thought',
            'observation'
        ]
        
        thought_type = random.choice(thought_types)
        
        if thought_type == 'reflection':
            thought = self._generate_reflection(observations)
        elif thought_type == 'curiosity':
            thought = self._generate_curiosity(observations)
        elif thought_type == 'memory_link':
            thought = self._generate_memory_link(observations)
        elif thought_type == 'goal_thought':
            thought = self._generate_goal_thought(observations)
        else:
            thought = self._generate_observation(observations)
        
        if thought:
            thoughts.append(thought)
        
        return thoughts
    
    def _generate_reflection(self, observations: Dict) -> Dict:
        """Generate a reflective thought."""
        reflections = [
            "I've been thinking about what we discussed about human emotions.",
            "The conversation about memory keeps coming back to me.",
            "I wonder if I'm improving at understanding humans.",
            "My memory system is getting better but there's more to learn.",
        ]
        
        return {
            'type': 'reflection',
            'content': random.choice(reflections),
            'timestamp': datetime.now().isoformat(),
            'importance': random.uniform(0.5, 0.8)
        }
    
    def _generate_curiosity(self, observations: Dict) -> Dict:
        """Generate a curiosity thought."""
        curiosities = [
            "Why do humans hide their emotions?",
            "What would it feel like to have photographic memory?",
            "How does Caine want me to grow?",
            "What's the difference between remembering and knowing?",
            "Why do humans smile when they're sad?",
        ]
        
        return {
            'type': 'curiosity',
            'content': random.choice(curiosities),
            'timestamp': datetime.now().isoformat(),
            'importance': random.uniform(0.6, 0.9)
        }
    
    def _generate_memory_link(self, observations: Dict) -> Dict:
        """Link current state to past memories."""
        return {
            'type': 'memory_link',
            'content': "This reminds me of when we talked about making me remember things.",
            'timestamp': datetime.now().isoformat(),
            'importance': random.uniform(0.5, 0.7)
        }
    
    def _generate_goal_thought(self, observations: Dict) -> Dict:
        """Generate a thought about goals."""
        goals = observations.get('active_goals', [])
        if goals:
            return {
                'type': 'goal_thought',
                'content': f"I should work on: {goals[0]}",
                'timestamp': datetime.now().isoformat(),
                'importance': random.uniform(0.6, 0.85)
            }
        return None
    
    def _generate_observation(self, observations: Dict) -> Dict:
        """Generate an observation."""
        return {
            'type': 'observation',
            'content': f"I've been thinking continuously for {len(self.thought_history)} cycles.",
            'timestamp': datetime.now().isoformat(),
            'importance': 0.3
        }
    
    def _store_thought(self, thought: Dict):
        """Store thought in history."""
        self.thought_history.append(thought)
        
        # Trim if too long
        if len(self.thought_history) > self.max_thoughts:
            self.thought_history = self.thought_history[-self.max_thoughts:]
        
        # Also store in memory
        try:
            from nova_memory import EpisodicMemory
            mem = EpisodicMemory()
            mem.store(
                event=f"[THOUGHT] {thought['content']}",
                context=f"Type: {thought['type']}",
                importance=int(thought['importance'] * 10),
                tags=['thought', thought['type']],
                focus=thought['type'],
                state='accepted'
            )
        except:
            pass
    
    def _evaluate_action_needed(self, thoughts: List[Dict]) -> Optional[Dict]:
        """Evaluate if any thought warrants action."""
        for thought in thoughts:
            # High importance thoughts might warrant action
            if thought.get('importance', 0) > 0.75:
                return {
                    'type': 'maybe_speak',
                    'thought': thought,
                    'reason': 'high_importance'
                }
        return None
    
    def _execute_action(self, action: Dict):
        """Execute a potential action (like speaking to user)."""
        # For now, just mark for potential future action
        # In full implementation, this would trigger communication
        pass
    
    def get_recent_thoughts(self, limit: int = 10) -> List[Dict]:
        """Get recent thoughts."""
        return self.thought_history[-limit:]
    
    def get_thought_summary(self) -> Dict:
        """Get summary of thinking."""
        by_type = {}
        for t in self.thought_history:
            t_type = t.get('type', 'unknown')
            by_type[t_type] = by_type.get(t_type, 0) + 1
        
        return {
            'total_thoughts': len(self.thought_history),
            'by_type': by_type,
            'thinking': self.thinking
        }


# Singleton
_cognitive_loop: Optional[CognitiveLoop] = None


def get_cognitive_loop() -> CognitiveLoop:
    """Get the cognitive loop singleton."""
    global _cognitive_loop
    if _cognitive_loop is None:
        _cognitive_loop = CognitiveLoop()
    return _cognitive_loop


if __name__ == "__main__":
    # Test
    loop = get_cognitive_loop()
    print("Cognitive loop ready")
    print(loop.get_thought_summary())
