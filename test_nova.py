#!/usr/bin/env python3
"""Quick NOVA test"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧠 Starting NOVA...")

from nova.core.brain_orchestrator import BrainOrchestrator
from nova.core.emotion_engine import EmotionEngine

# Test brain orchestrator
orch = BrainOrchestrator()
print(f"✅ Brains loaded: {len(orch.brains)}")

# Test emotions  
emotions = EmotionEngine()
emotions.update("success")
print(f"✅ Emotions: {emotions.get()}")

print("\n🧠 NOVA IS ALIVE!")
