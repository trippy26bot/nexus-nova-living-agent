"""
Nexus Nova Living Agent - Sub-Agent Manager
Nova can spawn, coordinate, and enable communication between sub-agents
"""
from datetime import datetime

class SubAgentManager:
    """NOVA spawns and coordinates sub-agents with inter-agent communication"""
    
    def __init__(self, nova):
        self.nova = nova
        self.sub_agents = {}  # name -> agent
        self.task_log = []
        self.message_log = []
        
    def spawn_agent(self, name: str, agent_class, *args, **kwargs):
        """Spawn a new sub-agent with message queue"""
        agent = agent_class(*args, **kwargs)
        agent.master = self.nova
        agent.name = name
        agent.message_queue = []  # incoming messages
        agent.task_queue = []
        self.sub_agents[name] = agent
        
        self.nova.memory.store_thought(f"[SubAgent Spawned] {name}")
        return agent
        
    def assign_task(self, agent_name: str, task_description: str, skill_name: str = None):
        """Assign a task to a sub-agent"""
        agent = self.sub_agents.get(agent_name)
        if not agent:
            return False
            
        task = {
            "description": task_description,
            "skill": skill_name,
            "assigned": datetime.now().isoformat(),
            "completed": False,
            "result": None
        }
        
        if not hasattr(agent, 'task_queue'):
            agent.task_queue = []
            
        agent.task_queue.append(task)
        
        self.task_log.append({
            "agent": agent_name,
            "task": task_description,
            "time": datetime.now().isoformat()
        })
        
        self.nova.memory.store_thought(
            f"[Task Assigned] {agent_name} → {task_description}"
        )
        return True
        
    def send_message(self, from_agent: str, to_agent: str, message: str):
        """Send a message from one agent to another"""
        to = self.sub_agents.get(to_agent)
        if not to or not hasattr(to, 'message_queue'):
            return False
            
        msg = {
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "time": datetime.now().isoformat()
        }
        
        to.message_queue.append(msg)
        self.message_log.append(msg)
        
        self.nova.memory.store_thought(
            f"[Agent Message] {from_agent} → {to_agent}: {message}"
        )
        return True
        
    def broadcast_message(self, from_agent: str, message: str):
        """Broadcast message to all agents"""
        for name, agent in self.sub_agents.items():
            if name != from_agent and hasattr(agent, 'message_queue'):
                self.send_message(from_agent, name, message)
                
    def agent_propose(self, agent_name: str, proposal: str):
        """Agent proposes something to Nova for decision"""
        self.nova.memory.store_thought(
            f"[Agent Proposal] {agent_name} proposes: {proposal}"
        )
        # Could implement voting system here
        
    def monitor_agents(self):
        """Check sub-agent task completion and collect messages"""
        completed = []
        
        for name, agent in self.sub_agents.items():
            if hasattr(agent, 'task_queue'):
                for task in agent.task_queue:
                    if task.get('completed'):
                        self.nova.memory.store_thought(
                            f"[Task Completed] {name} → {task['description']}"
                        )
                        completed.append((name, task))
                        
                # Remove completed tasks
                agent.task_queue = [t for t in agent.task_queue if not t.get('completed')]
                
            # Collect messages
            if hasattr(agent, 'message_queue'):
                while agent.message_queue:
                    msg = agent.message_queue.pop(0)
                    self.nova.memory.store_thought(
                        f"[Agent Chat] {msg['from']}: {msg['message']}"
                    )
                    
        return completed
        
    def get_status(self):
        """Get status of all sub-agents"""
        status = {}
        for name, agent in self.sub_agents.items():
            queue = getattr(agent, 'task_queue', [])
            msgs = getattr(agent, 'message_queue', [])
            status[name] = {
                "tasks_pending": len(queue),
                "current_task": queue[0]['description'] if queue else None,
                "unread_messages": len(msgs)
            }
        return status
