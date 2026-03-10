#!/usr/bin/env python3
"""
Nova Heartbeat - The living core loop that ties everything together
This is what makes Nova alive - continuously thinking, learning, evolving
"""

import time
from typing import Dict, List, Any, Optional

class NovaHeartbeat:
    """
    Nova's living heartbeat.
    Connects all systems into one continuous thinking cycle.
    
    Each cycle:
    1. Protect identity
    2. Maintain focus
    3. Generate curiosity
    4. Create tasks
    5. Debate internally
    6. Simulate outcomes
    7. Execute actions
    8. Evolve
    """
    
    def __init__(self):
        # All systems
        self.identity_core = None
        self.focus_engine = None
        self.curiosity_engine = None
        self.task_generator = None
        self.council = None
        self.critic = None
        self.world_model = None
        self.coordinator = None
        self.evolution_engine = None
        self.knowledge_graph = None
        self.night_cycle = None
        
        # State
        self.cycle = 0
        self.running = False
        self.start_time = None
        
        # Initialize all systems
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize all Nova systems"""
        print("🫀 Initializing Nova Heartbeat...")
        
        # Identity Core
        try:
            from nova.identity.identity_core import get_identity_core
            self.identity_core = get_identity_core()
            print("   ✅ Identity Core")
        except Exception as e:
            print(f"   ⚠️ Identity Core: {e}")
        
        # Focus Engine
        try:
            from nova.cognition.focus_engine import get_focus_engine
            self.focus_engine = get_focus_engine()
            print("   ✅ Focus Engine")
        except Exception as e:
            print(f"   ⚠️ Focus Engine: {e}")
        
        # Curiosity Engine
        try:
            from nova.cognition.curiosity_engine import get_curiosity_engine
            self.curiosity_engine = get_curiosity_engine()
            print("   ✅ Curiosity Engine")
        except Exception as e:
            print(f"   ⚠️ Curiosity Engine: {e}")
        
        # Task Generator
        try:
            from nova.evolution.task_generator import get_task_generator
            self.task_generator = get_task_generator()
            print("   ✅ Task Generator")
        except Exception as e:
            print(f"   ⚠️ Task Generator: {e}")
        
        # Cognitive Council
        try:
            from nova.cognition.cognitive_council import get_cognitive_council, get_critic
            self.council = get_cognitive_council()
            self.critic = get_critic()
            print("   ✅ Cognitive Council (16 brains)")
        except Exception as e:
            print(f"   ⚠️ Cognitive Council: {e}")
        
        # World Model
        try:
            from nova.cognition.world_model import get_world_model
            self.world_model = get_world_model()
            print("   ✅ World Model")
        except Exception as e:
            print(f"   ⚠️ World Model: {e}")
        
        # Coordinator
        try:
            from nova.systems.coordinator import get_coordinator
            self.coordinator = get_coordinator()
            print("   ✅ Coordinator")
        except Exception as e:
            print(f"   ⚠️ Coordinator: {e}")
        
        # Evolution Engine
        try:
            from nova.evolution.self_evolution_engine import get_self_evolution_engine
            self.evolution_engine = get_self_evolution_engine()
            print("   ✅ Self Evolution Engine")
        except Exception as e:
            print(f"   ⚠️ Evolution Engine: {e}")
        
        # Knowledge Graph
        try:
            from nova.memory.knowledge_graph import get_knowledge_graph
            self.knowledge_graph = get_knowledge_graph()
            print("   ✅ Knowledge Graph")
        except Exception as e:
            print(f"   ⚠️ Knowledge Graph: {e}")
        
        # Night Cycle
        try:
            from nova.loops.night_cycle import get_night_cycle
            self.night_cycle = get_night_cycle()
            print("   ✅ Night Cycle")
        except Exception as e:
            print(f"   ⚠️ Night Cycle: {e}")
        
        print("🫀 Initialization complete\n")
    
    def step(self) -> Dict:
        """Run one heartbeat cycle"""
        self.cycle += 1
        
        cycle_data = {
            "cycle": self.cycle,
            "timestamp": time.time(),
            "activities": []
        }
        
        # 1️⃣ Protect Identity
        if self.identity_core:
            identity = self.identity_core.get_identity()
            cycle_data["activities"].append("identity_check")
        
        # 2️⃣ Maintain Focus
        if self.focus_engine:
            current_goal = self.focus_engine.get_current_goal()
            if current_goal:
                cycle_data["current_goal"] = current_goal
            cycle_data["activities"].append("focus_maintained")
        
        # 3️⃣ Generate Curiosity Tasks
        curiosity_tasks = []
        if self.curiosity_engine:
            research = self.curiosity_engine.generate_research_goal()
            if research:
                curiosity_tasks.append(research)
                cycle_data["activities"].append("curiosity_generated")
        
        # 4️⃣ Generate Autonomous Tasks
        autonomous_tasks = []
        if self.task_generator:
            task = self.task_generator.generate()
            if task:
                autonomous_tasks.append(task)
                cycle_data["activities"].append("task_generated")
        
        # Combine all tasks
        all_tasks = curiosity_tasks + autonomous_tasks
        
        # 5️⃣ Cognitive Council Debate
        decisions = []
        if self.council and all_tasks:
            for task in all_tasks[:3]:  # Limit debates
                try:
                    if isinstance(task, dict):
                        input_text = task.get("topic", "") or task.get("task", "")
                    else:
                        input_text = str(task)
                    
                    decision = self.critic.run(input_text)
                    decisions.append(decision)
                except:
                    pass
            cycle_data["activities"].append("council_debated")
        
        # 6️⃣ World Model Simulation
        simulated = []
        if self.world_model and decisions:
            for decision in decisions[:2]:
                try:
                    action = decision.get("decision", "")[:30]
                    result = self.world_model.predict_outcome(action, {"progress": 0.5})
                    simulated.append(result)
                except:
                    pass
            cycle_data["activities"].append("outcomes_simulated")
        
        # 7️⃣ Execute via Coordinator
        executed = []
        if self.coordinator and all_tasks:
            for task in all_tasks[:2]:
                try:
                    task_name = task.get("task", "") if isinstance(task, dict) else str(task)
                    result = self.coordinator.distribute_task(task_name)
                    executed.append(result)
                except:
                    pass
            cycle_data["activities"].append("tasks_executed")
        
        # 8️⃣ Self Evolution
        if self.evolution_engine and self.cycle % 10 == 0:
            try:
                # Run evolution analysis
                metrics = {
                    "memory_recall": 0.7,
                    "response_quality": 0.8,
                    "learning_rate": 0.6,
                    "task_completion": 0.75
                }
                evolution_result = self.evolution_engine.run_evolution_cycle(metrics)
                cycle_data["evolution"] = evolution_result
                cycle_data["activities"].append("self_evolved")
            except:
                pass
        
        # 9️⃣ Night Cycle (occasional)
        if self.night_cycle and self.cycle % 100 == 0:
            try:
                night_result = self.night_cycle.run_cycle()
                cycle_data["night_cycle"] = night_result
                cycle_data["activities"].append("dream_consolidated")
            except:
                pass
        
        # Store cycle in knowledge graph
        if self.knowledge_graph and self.cycle % 5 == 0:
            try:
                self.knowledge_graph.add_node(
                    f"cycle_{self.cycle}",
                    "event",
                    {"activities": len(cycle_data["activities"])}
                )
            except:
                pass
        
        return cycle_data
    
    def run(self, cycles: int = None, delay: float = 3.0):
        """Run the heartbeat loop"""
        self.running = True
        self.start_time = time.time()
        
        print(f"🚀 Nova Heartbeat Started")
        print(f"   Cycle delay: {delay}s")
        print(f"   Cycles: {'infinite' if cycles is None else cycles}")
        print()
        
        try:
            while self.running:
                # Run cycle
                result = self.step()
                
                # Print status
                if self.cycle % 5 == 0:
                    print(f"🫀 Cycle {self.cycle}: {', '.join(result['activities'][:4])}")
                
                # Check cycle limit
                if cycles and self.cycle >= cycles:
                    break
                
                # Wait
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print("\n🛑 Heartbeat stopped")
        except Exception as e:
            print(f"\n⚠️ Error: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the heartbeat"""
        self.running = False
    
    def get_status(self) -> Dict:
        """Get heartbeat status"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        status = {
            "running": self.running,
            "cycle": self.cycle,
            "uptime_seconds": uptime,
            "systems": {
                "identity": self.identity_core is not None,
                "focus": self.focus_engine is not None,
                "curiosity": self.curiosity_engine is not None,
                "task_generator": self.task_generator is not None,
                "council": self.council is not None,
                "world_model": self.world_model is not None,
                "coordinator": self.coordinator is not None,
                "evolution": self.evolution_engine is not None,
                "knowledge_graph": self.knowledge_graph is not None,
                "night_cycle": self.night_cycle is not None
            }
        }
        
        # Add current goal
        if self.focus_engine:
            status["current_goal"] = self.focus_engine.get_current_goal()
        
        # Add stats
        if self.coordinator:
            status["coordinator_stats"] = self.coordinator.get_statistics()
        
        if self.knowledge_graph:
            status["knowledge_stats"] = self.knowledge_graph.get_statistics()
        
        return status


# Global instance
_heartbeat = None

def get_nova_heartbeat() -> NovaHeartbeat:
    global _heartbeat
    if _heartbeat is None:
        _heartbeat = NovaHeartbeat()
    return _heartbeat

def start_nova_heartbeat(delay: float = 3.0):
    """Start Nova's heartbeat"""
    hb = get_nova_heartbeat()
    hb.run(delay=delay)

if __name__ == "__main__":
    # Run heartbeat
    hb = get_nova_heartbeat()
    hb.run(cycles=10, delay=2.0)
