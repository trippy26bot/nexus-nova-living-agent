#!/usr/bin/env python3
"""
NOVA AGENTS — Multi-Agent Orchestration
Router → Planner → Researcher → Executor → Critic → Memory

The agent architecture for complex task handling.
"""

import json
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import sqlite3
from pathlib import Path

# Agent types
class AgentType(Enum):
    ROUTER = "router"
    PLANNER = "planner"
    RESEARCHER = "researcher"
    EXECUTOR = "executor"
    CRITIC = "critic"
    MEMORY = "memory"


@dataclass
class AgentMessage:
    """Message passing between agents."""
    sender: AgentType
    recipient: AgentType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Task:
    """A task to be handled by agents."""
    id: str
    description: str
    priority: int = 5
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Any = None
    error: Optional[str] = None
    steps: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, agent_type: AgentType, llm_callable):
        self.type = agent_type
        self.llm = llm_callable
        self.message_queue: List[AgentMessage] = []
    
    async def receive(self, message: AgentMessage):
        """Receive a message."""
        self.message_queue.append(message)
    
    async def process(self) -> Optional[AgentMessage]:
        """Process messages and potentially respond."""
        raise NotImplementedError
    
    async def send(self, recipient: AgentType, content: str, metadata: Dict = None):
        """Send a message to another agent."""
        message = AgentMessage(
            sender=self.type,
            recipient=recipient,
            content=content,
            metadata=metadata or {}
        )
        return message


class RouterAgent(BaseAgent):
    """Routes incoming requests to the appropriate handling."""
    
    def __init__(self, llm_callable):
        super().__init__(AgentType.ROUTER, llm_callable)
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """Analyze input and route to appropriate path."""
        
        system_prompt = """You are a router agent. Analyze the user input and determine:
1. The intent (question, task, conversation, etc.)
2. Complexity (simple, moderate, complex)
3. Required agents (planner, researcher, executor, etc.)

Respond in JSON format:
{
  "intent": "question|task|conversation|exploration",
  "complexity": "simple|moderate|complex",
  "agents_needed": ["planner", "researcher", "executor"],
  "reasoning": "why you chose this routing"
}"""
        
        result = self.llm(user_input, system=system_prompt)
        
        try:
            # Try to parse as JSON
            routing = json.loads(result)
        except:
            # Fallback
            routing = {
                "intent": "conversation",
                "complexity": "simple",
                "agents_needed": [],
                "reasoning": "Could not parse, defaulting to conversation"
            }
        
        return routing


class PlannerAgent(BaseAgent):
    """Breaks down tasks into actionable steps."""
    
    def __init__(self, llm_callable):
        super().__init__(AgentType.PLANNER, llm_callable)
    
    async def process(self, task: Task) -> Task:
        """Plan steps to complete the task."""
        
        system_prompt = f"""You are a planner agent. Break down this task into specific, actionable steps.

Task: {task.description}
Priority: {task.priority}

Respond in JSON format:
{{
  "steps": [
    {{"step": 1, "description": "do X", "agent": "researcher", "expected_output": "information about X"}},
    {{"step": 2, "description": "do Y", "agent": "executor", "expected_output": "result of Y"}}
  ],
  "reasoning": "why these steps in this order"
}}"""
        
        result = self.llm(task.description, system=system_prompt)
        
        try:
            plan = json.loads(result)
            task.steps = plan.get("steps", [])
        except:
            task.steps = [{"step": 1, "description": "Complete task", "agent": "executor"}]
        
        task.status = "in_progress"
        return task


class ResearcherAgent(BaseAgent):
    """Gathers information for tasks."""
    
    def __init__(self, llm_callable):
        super().__init__(AgentType.RESEARCHER, llm_callable)
    
    async def research(self, query: str, context: Dict = None) -> str:
        """Research a topic and return findings."""
        
        system_prompt = """You are a researcher agent. Find and synthesize information.

Guidelines:
- Be thorough but concise
- Prioritize reliable sources
- Note gaps in knowledge
- Provide actionable insights"""
        
        prompt = f"Research: {query}\n\nContext: {json.dumps(context) if context else 'None'}"
        
        return self.llm(prompt, system=system_prompt)


class ExecutorAgent(BaseAgent):
    """Executes planned actions."""
    
    def __init__(self, llm_callable, tools: List = None):
        super().__init__(AgentType.EXECUTOR, llm_callable)
        self.tools = tools or []
    
    async def execute(self, step: Dict, context: Dict = None) -> Any:
        """Execute a single step."""
        
        description = step.get("description", "")
        
        # Check if we have tools for this
        for tool in self.tools:
            if tool.can_handle(description):
                return await tool.run(description, context)
        
        # Fallback to LLM
        system_prompt = f"""You are an executor agent. Execute this step:

Step: {description}

Context: {json.dumps(context) if context else 'None'}

Provide the result of execution."""
        
        return self.llm(description, system=system_prompt)


class CriticAgent(BaseAgent):
    """Evaluates and critiques agent outputs."""
    
    def __init__(self, llm_callable):
        super().__init__(AgentType.CRITIC, llm_callable)
    
    async def critique(self, output: Any, criteria: List[str] = None) -> Dict:
        """Evaluate output against criteria."""
        
        criteria = criteria or ["accuracy", "completeness", "usefulness"]
        
        system_prompt = f"""You are a critic agent. Evaluate this output against these criteria: {', '.join(criteria)}

Output: {output}

Respond in JSON:
{{
  "passed": true/false,
  "scores": {{"accuracy": 8/10, "completeness": 7/10, "usefulness": 9/10}},
  "feedback": "specific constructive feedback",
  "suggestions": ["improvement 1", "improvement 2"]
}}"""
        
        result = self.llm(str(output), system=system_prompt)
        
        try:
            return json.loads(result)
        except:
            return {
                "passed": True,
                "scores": {"general": 7},
                "feedback": "Could not parse critique",
                "suggestions": []
            }


class MemoryAgent(BaseAgent):
    """Handles memory operations for the multi-agent system."""
    
    def __init__(self, llm_callable, db_path: str):
        super().__init__(AgentType.MEMORY, llm_callable)
        self.db_path = db_path
    
    async def store(self, content: str, memory_type: str = "episodic", importance: int = 5):
        """Store something in memory."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO memories (content, memory_type, importance) VALUES (?, ?, ?)",
            (content, memory_type, importance)
        )
        conn.commit()
        conn.close()
    
    async def retrieve(self, query: str, limit: int = 5) -> List[str]:
        """Retrieve relevant memories."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT content FROM memories WHERE content LIKE ? ORDER BY importance DESC LIMIT ?",
            (f"%{query}%", limit)
        )
        results = [row[0] for row in c.fetchall()]
        conn.close()
        return results
    
    async def extract_insights(self, content: str) -> Dict:
        """Extract semantic insights from content."""
        
        system_prompt = """You are a memory agent. Extract key facts and insights from this content.

Return JSON:
{
  "facts": ["fact 1", "fact 2"],
  "entities": ["person 1", "concept 2"],
  "topics": ["topic 1", "topic 2"],
  "importance": 1-10
}"""
        
        result = self.llm(content, system=system_prompt)
        
        try:
            return json.loads(result)
        except:
            return {"facts": [], "entities": [], "topics": [], "importance": 5}


class AgentOrchestrator:
    """Coordinates all agents."""
    
    def __init__(self, llm_callable, db_path: str, tools: List = None):
        self.llm = llm_callable
        self.db_path = db_path
        self.base_dir = Path.home() / ".nova"
        
        # Initialize agents
        self.router = RouterAgent(llm_callable)
        self.planner = PlannerAgent(llm_callable)
        self.researcher = ResearcherAgent(llm_callable)
        self.executor = ExecutorAgent(llm_callable, tools)
        self.critic = CriticAgent(llm_callable)
        self.memory = MemoryAgent(llm_callable, db_path)
        
        self.agents = {
            AgentType.ROUTER: self.router,
            AgentType.PLANNER: self.planner,
            AgentType.RESEARCHER: self.researcher,
            AgentType.EXECUTOR: self.executor,
            AgentType.CRITIC: self.critic,
            AgentType.MEMORY: self.memory,
        }
        try:
            from core.world_model import WorldModel
            self.world_model = WorldModel()
        except Exception:
            self.world_model = None
        try:
            from nova_goal_engine import GoalEngine
            self.goal_engine = GoalEngine(self.base_dir / "goals_state.json")
        except Exception:
            self.goal_engine = None
    
    def _observe(self, user_input: str) -> Dict[str, Any]:
        perception = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "has_user_message": bool(user_input.strip()),
        }
        if self.world_model:
            try:
                self.world_model.record_turn("user", user_input, sentiment=0.0, topics=[])
                perception["world_context"] = self.world_model.get_context_summary()
            except Exception:
                pass
        return perception

    def _plan(self, user_input: str, perception: Dict[str, Any], goals: Dict[str, Any]) -> Dict[str, Any]:
        # Current planner is router-based; this wraps it in lifecycle semantics.
        return {"routing_input": user_input, "perception": perception, "goals": goals}

    async def _act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        user_input = plan["routing_input"]
        routing = await self.router.process(user_input)

        result = {
            "input": user_input,
            "routing": routing,
            "output": None,
            "steps_executed": [],
            "success": False
        }

        if routing["complexity"] == "simple" or not routing.get("agents_needed"):
            response = self.llm(user_input)
            result["output"] = response
            result["success"] = True
            return result

        if "planner" in routing["agents_needed"]:
            task = Task(
                id=f"task_{datetime.now().timestamp()}",
                description=user_input,
                priority=routing.get("priority", 5)
            )
            task = await self.planner.process(task)
            result["steps_executed"].append({"agent": "planner", "steps": len(task.steps)})

            for step in task.steps:
                agent_name = step.get("agent", "executor")

                if agent_name == "researcher":
                    output = await self.researcher.research(step["description"])
                elif agent_name == "executor":
                    output = await self.executor.execute(step)
                else:
                    output = self.llm(step["description"])

                step["output"] = output
                result["steps_executed"].append({
                    "agent": agent_name,
                    "description": step["description"],
                    "output": output[:100] + "..." if len(str(output)) > 100 else output
                })

            final_output = "\n\n".join([
                f"Step {s.get('step', i+1)}: {s.get('output', '')}"
                for i, s in enumerate(task.steps)
            ])

            critique = await self.critic.critique(final_output)
            result["critique"] = critique
            if critique.get("passed", True):
                result["output"] = final_output
                result["success"] = True
            else:
                result["output"] = final_output + "\n\nCritique: " + critique.get("feedback", "")
                result["success"] = True

        await self.memory.store(
            f"User: {user_input}\nResponse: {result.get('output', '')}",
            importance=5
        )
        return result

    def _reflect(self, plan: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        lessons = []
        if result.get("success"):
            lessons.append("keep task reliability high")
        if result.get("routing", {}).get("complexity") == "complex":
            lessons.append("improve planning and decomposition quality")
        return {
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "lessons": lessons,
            "steps_count": len(result.get("steps_executed", [])),
        }

    def _learn(self, reflection: Dict[str, Any]):
        if self.goal_engine:
            try:
                goals = self.goal_engine.load()
                goals = self.goal_engine.evolve_from_reflection(goals, reflection)
                self.goal_engine.save(goals)
            except Exception:
                pass
        if self.world_model:
            try:
                self.world_model.record_turn("assistant", json.dumps(reflection)[:200], sentiment=0.0, topics=["reflection"])
            except Exception:
                pass
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """Process user input through lifecycle: observe -> plan -> act -> reflect -> learn."""
        perception = self._observe(user_input)
        goals = {}
        if self.goal_engine:
            try:
                gs = self.goal_engine.load()
                goals = {"short_term": gs.short_term, "long_term": gs.long_term, "emergent": gs.emergent}
            except Exception:
                goals = {}
        plan = self._plan(user_input, perception, goals)
        result = await self._act(plan)
        reflection = self._reflect(plan, result)
        self._learn(reflection)
        result["lifecycle"] = {
            "observe": perception,
            "plan": {"goal_focus": goals.get("short_term", ["maintain_task_reliability"])[0] if goals else "maintain_task_reliability"},
            "reflect": reflection,
        }
        return result


class ParallelAgentExecutor:
    """Execute multiple agents in parallel."""
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
    
    async def execute_parallel(self, tasks: List[str]) -> List[Dict]:
        """Execute multiple tasks in parallel."""
        
        async def run_task(task):
            return await self.orchestrator.process(task)
        
        results = await asyncio.gather(*[run_task(t) for t in tasks])
        return results


class DebateAgent:
    """Two agents debate a topic with a critic judge."""
    
    def __init__(self, llm_callable):
        self.llm = llm_callable
        self.critic = CriticAgent(llm_callable)
    
    async def debate(self, topic: str, positions: List[str] = None) -> Dict:
        """Run a debate."""
        
        if positions is None:
            positions = ["Yes", "No"]
        
        # Get arguments for each position
        arguments = {}
        for position in positions:
            prompt = f"Argue {position} for: {topic}. Provide strong, well-reasoned arguments."
            arguments[position] = self.llm(prompt)
        
        # Get critique
        combined = "\n\n".join([f"{p}: {a}" for p, a in arguments.items()])
        critique = await self.critic.critique(
            combined,
            criteria=["logic", "evidence", "persuasiveness", "balance"]
        )
        
        return {
            "topic": topic,
            "arguments": arguments,
            "critique": critique,
            "winner": critique.get("suggestions", ["Inconclusive"])[0] if critique.get("suggestions") else "Inconclusive"
        }


# Utility functions
def create_orchestrator(config: dict) -> AgentOrchestrator:
    """Create an orchestrator from config."""
    from nova import call_llm, NOVA_DB
    
    return AgentOrchestrator(call_llm, str(NOVA_DB))


async def run_agent_task(task_description: str, config: dict = None) -> Dict:
    """Run a single task through the agent system."""
    
    from nova import call_llm, NOVA_DB
    
    config = config or {}
    orchestrator = AgentOrchestrator(call_llm, str(NOVA_DB))
    
    return await orchestrator.process(task_description)


# Example usage
if __name__ == "__main__":
    print("Nova Agents - Multi-Agent Orchestration")
    print("Import and use AgentOrchestrator to process tasks.")
