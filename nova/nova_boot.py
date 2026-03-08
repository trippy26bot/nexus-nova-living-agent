#!/usr/bin/env python3
"""
NOVA 1000% - Autonomous Living AI Agent
Main entry point
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_loop import AgentLoop
from core.brain_orchestrator import BrainOrchestrator
from core.meta_brain import MetaBrain
from core.cognitive_mesh import CognitiveMesh
from core.emotion_engine import EmotionEngine
from core.world_model import WorldModel
from core.curiosity_engine import AutonomousDrive
from memory.nova_memory import NovaMemory
from memory.neural_memory_map import NeuralMemoryMap
from core.identity import NovaIdentity
from connectors.trading_connector import TradingConnector
from brokers import get_adapter


def initialize_nova():
    """Initialize all NOVA systems"""
    print("🧠 Initializing NOVA 1000%...")
    
    # Core systems
    print("  • Loading brain orchestrator...")
    brain_orchestrator = BrainOrchestrator()
    
    print("  • Loading meta brain...")
    meta_brain = MetaBrain(brain_orchestrator)
    
    print("  • Loading cognitive mesh...")
    cognitive_mesh = CognitiveMesh(brain_orchestrator)
    
    print("  • Loading memory system...")
    memory = NovaMemory()
    
    print("  • Loading neural memory map...")
    neural_memory = NeuralMemoryMap()
    
    print("  • Loading identity...")
    identity = NovaIdentity()
    
    print("  • Loading emotion engine...")
    emotions = EmotionEngine()
    
    print("  • Loading world model...")
    world_model = WorldModel()
    
    print("  • Loading curiosity & goals...")
    curiosity = AutonomousDrive(identity, memory)
    
    print("  • Loading trading connector...")
    try:
        broker = get_adapter()
        connector = TradingConnector()
        connector.connect_brains(brain_orchestrator)
        connector.connect_broker(broker)
    except Exception as e:
        print(f"  ⚠️ Trading connector not available: {e}")
        connector = None
    
    print("  ✅ NOVA initialized!")
    
    return {
        "brain_orchestrator": brain_orchestrator,
        "meta_brain": meta_brain,
        "cognitive_mesh": cognitive_mesh,
        "memory": memory,
        "neural_memory": neural_memory,
        "identity": identity,
        "emotions": emotions,
        "world_model": world_model,
        "curiosity": curiosity,
        "connector": connector
    }


def run_nova(cycles=None, interval=60):
    """Run NOVA's thinking loop"""
    systems = initialize_nova()
    
    # Create agent loop
    loop = AgentLoop(
        systems["meta_brain"],
        systems["memory"],
        systems["connector"]
    )
    
    print(f"\n🚀 Starting NOVA thinking loop (interval: {interval}s)")
    print("Press Ctrl+C to stop\n")
    
    if cycles:
        # Run for specific number of cycles
        for i in range(cycles):
            print(f"\n--- Cycle {i+1}/{cycles} ---")
            loop.cycle(interval)
    else:
        # Run forever
        loop.start(interval)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NOVA 1000% - Autonomous AI Agent")
    parser.add_argument("--cycles", type=int, default=None, help="Number of cycles to run")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between cycles")
    
    args = parser.parse_args()
    
    try:
        run_nova(cycles=args.cycles, interval=args.interval)
    except KeyboardInterrupt:
        print("\n\n👋 NOVA shutting down...")
