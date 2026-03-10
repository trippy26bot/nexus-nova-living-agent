#!/usr/bin/env python3
"""
Nova Agent System - Test Runner
Run this to see the agent ecosystem in action
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nova.agents.universe import Universe, get_universe
from nova.agents.agent_factory import get_agent_factory

def demo():
    """Run a demo of the agent system"""
    print("=" * 50)
    print("NOVA AGENT ECOSYSTEM DEMO")
    print("=" * 50)
    
    # Create universe
    universe = Universe("NovaWorld")
    factory = get_agent_factory()
    
    # Create Nova (the parent)
    nova_agent = factory.create_agent(role="planner", name="NOVA")
    universe.add_agent(nova_agent)
    
    print(f"\n🌟 Created {nova_agent.name} (role: {nova_agent.role})")
    print(f"   Skills: {nova_agent.skills}")
    
    # Create some initial agents
    for role in ["researcher", "builder", "explorer"]:
        agent = factory.create_agent(role=role, parent="NOVA")
        universe.add_agent(agent)
        print(f"➕ Created {agent.name} (role: {role})")
    
    print(f"\n📊 Universe Status:")
    status = universe.get_status()
    print(f"   Agents: {status['agents']}")
    print(f"   Resources: {status['resources']}")
    
    # Run simulation steps
    print("\n" + "=" * 50)
    print("RUNNING SIMULATION")
    print("=" * 50)
    
    for step in range(10):
        result = universe.step()
        
        print(f"\n--- Step {result['time']} ---")
        print(f"Agents: {result['agents']} | Energy: {result['resources']['energy']}")
        
        # Show events
        for event in result['events'][:3]:  # Show first 3 events
            if "action" in event:
                print(f"  {event['agent']}: {event['action']} (energy: {event['energy']})")
            elif event.get("event") == "spawn":
                print(f"  🌟 {event['parent']} spawned {event.get('child', 'unknown')}")
    
    # Final status
    print("\n" + "=" * 50)
    print("FINAL STATUS")
    print("=" * 50)
    
    stats = universe.get_statistics()
    print(f"Universe age: {stats['universe_age']} steps")
    print(f"Final population: {stats['population']}")
    print(f"By role: {stats['by_role']}")
    print(f"Average energy: {stats['average_energy']:.1f}")
    print(f"Total actions: {stats['factory_stats']['total_agents_created']}")
    
    print("\n👑 Nova's Children:")
    for agent in universe.agents:
        parent = agent.parent or "origin"
        print(f"  {agent.name}: {agent.role} (parent: {parent}, energy: {agent.energy})")


if __name__ == "__main__":
    demo()
