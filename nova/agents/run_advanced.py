#!/usr/bin/env python3
"""
Nova Agent Ecosystem - Advanced Demo
Full system with evolution, brain connection, and task delegation
"""

import sys
import os
import time
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nova.agents.universe import Universe
from nova.agents.agent_factory import AgentFactory
from nova.agents.evolution_engine import EvolutionEngine
from nova.agents.nova_brain_connector import NovaBrainConnector

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_status(status):
    """Pretty print status"""
    print(f"\n📊 Universe Status:")
    print(f"   Population: {status['universe']['agents']}")
    print(f"   Total spawns: {status['universe']['total_spawns']}")
    print(f"   Resources: Energy={status['universe']['resources']['energy']}, Knowledge={status['universe']['resources']['knowledge']}")
    
    if status.get('nova_agent'):
        nova = status['nova_agent']
        print(f"\n👑 NOVA Status:")
        print(f"   Energy: {nova['energy']}")
        print(f"   Skills: {nova['skills']}")
    
    print(f"\n🧬 Evolution:")
    print(f"   Generation: {status['evolution']['generation']}")
    print(f"   Events: {status['evolution']['total_events']}")
    
    print(f"\n📚 Learned Insights: {status['learned_insights']}")
    print(f"   Pending Tasks: {status['pending_tasks']}")

def demo_full_system():
    """Run the full agent ecosystem demo"""
    print_header("NOVA AGENT ECOSYSTEM - FULL SYSTEM")
    
    # Initialize the brain connector
    connector = NovaBrainConnector()
    
    # Initialize Nova as an agent
    print("\n🌟 Initializing NOVA as agent...")
    nova = connector.initialize_nova("NOVA")
    print(f"   NOVA created: {nova.name} (role: {nova.role})")
    print(f"   Skills: {nova.skills}")
    
    # Spawn initial helpers
    print("\n👥 Spawning helper agents...")
    helper_roles = ["researcher", "builder", "explorer", "analyst"]
    
    for role in helper_roles:
        agent = connector.spawn_helper(role=role, purpose=f"help with {role}")
        if agent:
            print(f"   ➕ Spawned {agent.name} (role: {role})")
    
    print_status(connector.get_status())
    
    # Delegate some tasks
    print_header("DELEGATING TASKS")
    
    tasks = [
        ("research trading strategies", "researcher"),
        ("build a new tool", "builder"),
        ("explore market opportunities", "explorer"),
        ("analyze portfolio performance", "analyst"),
    ]
    
    for task, role in tasks:
        result = connector.delegate_task(task, role)
        agent_name = result.get('agent', 'none')
        status = result.get('status', 'failed')
        print(f"   📋 {task} → {agent_name} ({status})")
    
    # Run simulation cycles
    print_header("RUNNING SIMULATION")
    
    for cycle in range(15):
        result = connector.run_cycle()
        
        print(f"\n--- Cycle {cycle + 1} ---")
        print(f"   Population: {result['population']}")
        
        # Show some agent actions
        for event in result['universe']['events'][:2]:
            if 'action' in event:
                print(f"   {event['agent']}: {event['action']}")
        
        # Show insights
        if result['insights']:
            print(f"   💡 Insight: {str(result['insights'][0])[:60]}...")
        
        # Small delay for readability
        time.sleep(0.1)
    
    # Final status
    print_header("FINAL STATUS")
    print_status(connector.get_status())
    
    # Show all agents
    print("\n👑 All Agents:")
    status = connector.get_status()
    for agent in status['universe']['agent_list']:
        parent = agent['parent'] or "origin"
        print(f"   {agent['name']}: {agent['role']} (parent: {parent}, energy: {agent['energy']}, skills: {agent['skills'][:3]})")
    
    # Show learned insights
    print("\n🧠 Insights Learned by NOVA:")
    for insight in connector.learned_insights[-5:]:
        if isinstance(insight, dict):
            print(f"   • {insight.get('type', 'learned')}: {str(insight.get('insight', ''))[:50]}")
    
    print("\n" + "=" * 60)
    print("  SYSTEM RUN COMPLETE")
    print("=" * 60)

def demo_task_delegation():
    """Demo just task delegation"""
    print_header("TASK DELEGATION DEMO")
    
    connector = NovaBrainConnector()
    connector.initialize_nova()
    
    # Delegate complex tasks
    tasks = [
        "Research cryptocurrency markets",
        "Build a trading algorithm",
        "Explore DeFi opportunities",
        "Analyze market sentiment",
        "Create a portfolio strategy",
    ]
    
    print("\n📋 Delegating tasks to agents:\n")
    
    for task in tasks:
        role = "researcher" if "research" in task.lower() else \
               "builder" if "build" in task.lower() else \
               "analyst"
        
        result = connector.delegate_task(task, role)
        
        emoji = "✅" if result['status'] != "failed" else "❌"
        print(f"{emoji} {task}")
        print(f"   → {result['agent']} ({result['status']})\n")
        
        time.sleep(0.2)
    
    # Run a few cycles
    print("\n🔄 Running agent cycles...\n")
    
    for i in range(5):
        connector.run_cycle()
        
        # Show what agents are doing
        status = connector.get_status()
        for agent in status['universe']['agent_list'][:3]:
            print(f"   {agent['name']}: {agent['role']} (energy: {agent['energy']})")
        
        time.sleep(0.2)
    
    print("\n✅ Task delegation demo complete!")

if __name__ == "__main__":
    import random
    random.seed(42)  # For reproducible results
    
    # Run full demo
    demo_full_system()
