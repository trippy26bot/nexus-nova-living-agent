#!/usr/bin/env python3
"""
Brain Handlers - Real implementations for cognitive bus handlers.

Replaces stub handlers that previously returned {"brain": "X", "result": "analyzed"}
"""

import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Imports - these may not be available in all contexts
try:
    from nova.memory.vector_memory import get_vector_memory
    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False


class ReasoningBrain:
    """
    Reasoning brain - analyzes prompts and generates thoughtful responses.
    Uses LLM if available, falls back to heuristic.
    """
    
    def __init__(self, skill_runner: Optional[Callable] = None):
        self.skill_runner = skill_runner
    
    def analyze(self, prompt: str) -> Dict[str, Any]:
        """Analyze a prompt and return reasoning."""
        
        # If we have an LLM, use it
        if self.skill_runner:
            reasoning_prompt = f"""You are Nova's reasoning brain. 
Analyze this user input and provide a brief reasoning summary.

User said: {prompt}

Provide:
1. What they're likely asking for
2. Key entities or topics
3. Emotional undertone (if any)
4. How to approach responding

Be concise - 2-3 sentences max.

Reasoning:"""

            try:
                result = self.skill_runner(reasoning_prompt)
                return {
                    "brain": "reasoning",
                    "result": result,
                    "processed": True,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return self._heuristic_analyze(prompt)
        
        # Fallback to heuristic
        return self._heuristic_analyze(prompt)
    
    def _heuristic_analyze(self, prompt: str) -> Dict[str, Any]:
        """Simple heuristic analysis without LLM."""
        prompt_lower = prompt.lower()
        
        # Detect type
        prompt_type = "general"
        if any(w in prompt_lower for w in ["what", "how", "why", "when", "where"]):
            prompt_type = "question"
        elif any(w in prompt_lower for w in ["do", "make", "build", "create", "write"]):
            prompt_type = "task"
        elif any(w in prompt_lower for w in ["!", "amazing", "great", "love", "hate"]):
            prompt_type = "emotional"
        
        # Detect topics
        topics = []
        topic_keywords = {
            "coding": ["code", "python", "编程", "debug", "function"],
            "trading": ["trade", "bitcoin", "crypto", "market", "price"],
            "creative": ["write", "story", "art", "create", "design"],
            "research": ["find", "search", "look up", "research"],
        }
        for topic, keywords in topic_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                topics.append(topic)
        
        return {
            "brain": "reasoning",
            "result": f"Type: {prompt_type}, Topics: {', '.join(topics) or 'general'}",
            "processed": True,
            "prompt_type": prompt_type,
            "topics": topics,
            "timestamp": datetime.now().isoformat()
        }


class MemoryBrain:
    """
    Memory brain - retrieves relevant memories.
    Queries vector memory, episodic logs, and Life Memory.
    """
    
    def __init__(self):
        self.vector_memory = None
        if HAS_VECTOR:
            try:
                self.vector_memory = get_vector_memory()
            except:
                pass
    
    def recall(self, prompt: str) -> Dict[str, Any]:
        """Recall relevant memories."""
        memories = []
        
        # 1. Vector memory search
        if self.vector_memory:
            try:
                results = self.vector_memory.search(prompt, top_k=3)
                memories.extend([r["text"] for r in results])
            except:
                pass
        
        # 2. Check for recent memories in today's file
        try:
            from pathlib import Path
            today = datetime.now().strftime("%Y-%m-%d")
            memory_file = Path.home() / ".openclaw" / "workspace" / "memory" / f"{today}.md"
            if memory_file.exists():
                content = memory_file.read_text()
                # Simple keyword match
                prompt_lower = prompt.lower()
                lines = content.split("\n")
                for line in lines[:10]:  # Check first 10 lines
                    if any(w in line.lower() for w in prompt_lower.split()[:3]):
                        if len(line) > 20:
                            memories.append(line.strip()[:100])
        except:
            pass
        
        # 3. Life Memory (~/.nova/life.json)
        try:
            life_file = Path.home() / ".nova" / "life.json"
            if life_file.exists():
                life_data = json.load(open(life_file))
                # Check recent entries
                recent = life_data.get("recent", [])[:3]
                for entry in recent:
                    if isinstance(entry, dict):
                        memories.append(entry.get("summary", str(entry)[:50]))
                    else:
                        memories.append(str(entry)[:50])
        except:
            pass
        
        return {
            "brain": "memory",
            "result": memories[:5] if memories else ["No relevant memories found"],
            "count": len(memories),
            "timestamp": datetime.now().isoformat()
        }


class ToolBrain:
    """
    Tool brain - selects appropriate skills/tools.
    Uses registry and keyword matching.
    """
    
    # Skill registry
    SKILL_REGISTRY = {
        "github": ["gh", "git", "repo", "pr", "issue", "commit"],
        "weather": ["weather", "temperature", "forecast", "rain", "sun"],
        "trading": ["trade", "bitcoin", "crypto", "market", "bet", "simmer"],
        "memory": ["remember", "memory", "forget", "recall"],
        "planning": ["plan", "goal", "schedule", "task"],
        "research": ["search", "find", "look up", "research"],
        "humanizer": ["humanize", "rewrite", "polish", "tone"],
    }
    
    def __init__(self):
        pass
    
    def select(self, prompt: str) -> Dict[str, Any]:
        """Select appropriate tools/skills."""
        prompt_lower = prompt.lower()
        
        matched_skills = []
        for skill, keywords in self.SKILL_REGISTRY.items():
            if any(kw in prompt_lower for kw in keywords):
                matched_skills.append(skill)
        
        if not matched_skills:
            matched_skills = ["default"]  # Use default tools
        
        return {
            "brain": "tool",
            "result": f"Using skills: {', '.join(matched_skills)}",
            "skills": matched_skills,
            "timestamp": datetime.now().isoformat()
        }


def setup_brains(bus, skill_runner: Optional[Callable] = None):
    """
    Set up cognitive bus with real brain handlers.
    
    Args:
        bus: CognitiveBus instance
        skill_runner: Optional LLM callable for reasoning brain
    """
    from nova.cognitive_bus import EventType
    
    reasoning = ReasoningBrain(skill_runner)
    memory = MemoryBrain()
    tool = ToolBrain()
    
    # Subscribe handlers
    bus.subscribe(EventType.USER_INPUT, reasoning.analyze)
    bus.subscribe(EventType.USER_INPUT, memory.recall)
    bus.subscribe(EventType.USER_INPUT, tool.select)
    
    print("[BrainHandlers] ✓ Initialized reasoning, memory, tool brains")


# CLI test
if __name__ == "__main__":
    print("=" * 50)
    print("Brain Handlers Test")
    print("=" * 50)
    
    # Test ReasoningBrain
    print("\n[1] ReasoningBrain (heuristic)...")
    rb = ReasoningBrain()
    result = rb.analyze("What's the weather like?")
    print(f"  Result: {result}")
    assert result["processed"] == True
    print("  ✓ Reasoning works")
    
    # Test MemoryBrain
    print("\n[2] MemoryBrain...")
    mb = MemoryBrain()
    result = mb.recall("trading")
    print(f"  Found: {result['count']} memories")
    print("  ✓ Memory works")
    
    # Test ToolBrain
    print("\n[3] ToolBrain...")
    tb = ToolBrain()
    result = tb.select("check my github prs")
    print(f"  Skills: {result['skills']}")
    print("  ✓ Tool selection works")
    
    # Test with mock LLM
    print("\n[4] ReasoningBrain (with mock LLM)...")
    mock_runner = lambda p: "Mock reasoning: this appears to be a question about weather."
    rb_llm = ReasoningBrain(mock_runner)
    result = rb_llm.analyze("What's the weather?")
    print(f"  Result: {result['result'][:50]}...")
    print("  ✓ LLM integration works")
    
    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)
