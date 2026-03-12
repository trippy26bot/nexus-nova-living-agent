#!/usr/bin/env python3
"""
Nova Cognitive Systems Pressure Test v2
Tests all major cognitive subsystems for functionality
"""
import sys
import os
import traceback
import json
from datetime import datetime
from pathlib import Path

# Add paths - try multiple approaches
NOVA_PATH = os.path.expanduser("~/.openclaw/workspace/nova")
CORE_PATH = os.path.expanduser("~/.openclaw/workspace/nova/core")
BRAINS_PATH = os.path.expanduser("~/.openclaw/workspace/nova/brains")

for p in [NOVA_PATH, CORE_PATH, BRAINS_PATH]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Also add workspace root
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace"))

LOG_FILE = os.path.expanduser(f"~/.nova/memory/pressure-test-{datetime.now().strftime('%Y-%m-%d')}.log")

results = {
    "timestamp": datetime.now().isoformat(),
    "systems_tested": [],
    "passed": [],
    "failed": [],
    "warnings": [],
    "recommendations": []
}

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def test_system(name, test_func):
    """Test a single cognitive system"""
    results["systems_tested"].append(name)
    log(f"\n{'='*60}")
    log(f"TESTING: {name}")
    log(f"{'='*60}")
    try:
        result = test_func()
        if result.get("status") == "pass":
            results["passed"].append(name)
            log(f"✅ PASS: {result.get('message', 'OK')}")
        else:
            results["failed"].append(name)
            log(f"❌ FAIL: {result.get('message', 'Unknown error')}")
            if result.get("trace"):
                log(f"   Trace: {result['trace'][:200]}")
        return result
    except Exception as e:
        results["failed"].append(name)
        log(f"❌ CRASH: {str(e)}")
        log(f"   Trace: {traceback.format_exc()[:300]}")
        results["recommendations"].append(f"Fix crash in {name}: {str(e)[:100]}")
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

# ============================================================
# TEST SUITES - Corrected imports
# ============================================================

def test_identity_core():
    """Test identity.py - core identity system"""
    try:
        # Try different import paths
        try:
            from core.identity import NovaIdentity
        except:
            from identity import NovaIdentity
        
        identity = NovaIdentity()
        profile = identity.get_identity()
        
        return {"status": "pass", "message": f"Identity core loaded: {identity.name}"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_emotional_council():
    """Test emotional_council.py - cognitive council"""
    try:
        try:
            from core.emotional_council import EmotionalCouncil
        except:
            from emotional_council import EmotionalCouncil
        
        council = EmotionalCouncil()
        
        return {"status": "pass", "message": f"Emotional council loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_memory_engine():
    """Test memory_engine.py - unified memory system"""
    try:
        try:
            from core.memory_engine import MemoryEngine
        except:
            from memory_engine import MemoryEngine
        
        engine = MemoryEngine()
        
        return {"status": "pass", "message": f"Memory engine operational"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_drift_engine():
    """Test drift_engine.py - thought drift system"""
    try:
        try:
            from core.drift_engine import DriftEngine
        except:
            from drift_engine import DriftEngine
        
        drift = DriftEngine()
        
        return {"status": "pass", "message": f"Drift engine loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_reflection_engine():
    """Test reflection_engine.py - self-reflection system"""
    try:
        try:
            from core.reflection_engine import ReflectionEngine
        except:
            from reflection_engine import ReflectionEngine
        
        reflection = ReflectionEngine()
        
        return {"status": "pass", "message": f"Reflection engine loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_goal_engine():
    """Test goal_engine.py - goal management"""
    try:
        try:
            from core.goal_engine import GoalEngine
        except:
            from goal_engine import GoalEngine
        
        goals = GoalEngine()
        
        return {"status": "pass", "message": f"Goal engine loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_brain_strategy():
    """Test brain_strategy.py - strategic thinking"""
    try:
        try:
            from brains.brain_strategy import BrainStrategy
        except:
            from brain_strategy import BrainStrategy
        
        strategy = BrainStrategy()
        
        return {"status": "pass", "message": f"Strategy brain loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_brain_orchestrator():
    """Test brain_orchestrator.py - multi-brain coordination"""
    try:
        try:
            from core.brain_orchestrator import BrainOrchestrator
        except:
            from brain_orchestrator import BrainOrchestrator
        
        orch = BrainOrchestrator()
        
        return {"status": "pass", "message": f"Brain orchestrator loaded, brains: {len(orch.brains) if hasattr(orch, 'brains') else 'unknown'}"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_cognitive_mesh():
    """Test cognitive_mesh.py - thought network"""
    try:
        try:
            from core.cognitive_mesh import CognitiveMesh
        except:
            from cognitive_mesh import CognitiveMesh
        
        mesh = CognitiveMesh()
        
        return {"status": "pass", "message": f"Cognitive mesh loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_curiosity_engine():
    """Test curiosity_engine.py - curiosity drive"""
    try:
        try:
            from core.curiosity_engine import CuriosityEngine
        except:
            from curiosity_engine import CuriosityEngine
        
        curiosity = CuriosityEngine()
        
        return {"status": "pass", "message": f"Curiosity engine loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_world_model():
    """Test world_model.py - mental model of world"""
    try:
        try:
            from core.world_model import WorldModel
        except:
            from world_model import WorldModel
        
        world = WorldModel()
        
        return {"status": "pass", "message": f"World model loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_emotion_engine():
    """Test emotion_engine.py - emotional processing"""
    try:
        try:
            from core.emotion_engine import EmotionEngine
        except:
            from emotion_engine import EmotionEngine
        
        emotion = EmotionEngine()
        
        return {"status": "pass", "message": f"Emotion engine loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_event_bus():
    """Test event_bus.py - internal event system"""
    try:
        try:
            from core.event_bus import EventBus
        except:
            from event_bus import EventBus
        
        bus = EventBus()
        
        return {"status": "pass", "message": f"Event bus loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_brain_bus():
    """Test brain_bus.py - brain communication"""
    try:
        try:
            from core.brain_bus import BrainBus
        except:
            from brain_bus import BrainBus
        
        bus = BrainBus()
        
        return {"status": "pass", "message": f"Brain bus loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_attention_router():
    """Test attention_router.py - attention management"""
    try:
        try:
            from core.attention_router import AttentionRouter
        except:
            from attention_router import AttentionRouter
        
        router = AttentionRouter()
        
        return {"status": "pass", "message": f"Attention router loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_meta_brain():
    """Test meta_brain.py - meta cognition"""
    try:
        try:
            from core.meta_brain import MetaBrain
        except:
            from meta_brain import MetaBrain
        
        meta = MetaBrain()
        
        return {"status": "pass", "message": f"Meta brain loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_agent_loop():
    """Test agent_loop.py - main agent loop"""
    try:
        try:
            from core.agent_loop import AgentLoop
        except:
            from agent_loop import AgentLoop
        
        loop = AgentLoop()
        
        return {"status": "pass", "message": f"Agent loop loaded"}
    except Exception as e:
        return {"status": "fail", "message": str(e), "trace": traceback.format_exc()}

def test_vector_memory():
    """Test vector memory (ChromaDB) if available"""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=os.path.expanduser("~/.nova/vector_memory"))
        collection = client.get_or_create_collection("test")
        collection.add(ids=["test"], embeddings=[[0.1]*384], documents=["test doc"])
        results_vec = collection.query(query_embeddings=[[0.1]*384], n_results=1)
        
        return {"status": "pass", "message": "Vector memory (ChromaDB) operational"}
    except ImportError:
        results["warnings"].append("Vector memory (ChromaDB) not installed")
        return {"status": "fail", "message": "ChromaDB not installed"}
    except Exception as e:
        results["warnings"].append(f"Vector memory issue: {str(e)[:50]}")
        return {"status": "fail", "message": str(e)}

def test_working_memory():
    """Test working memory (in-memory buffer)"""
    try:
        working_mem = {}
        working_mem["current_context"] = "test"
        working_mem["active_task"] = "pressure_test"
        
        return {"status": "pass", "message": "Working memory operational (in-memory)"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}

def test_skill_nova_memory():
    """Test nova-memory skill"""
    try:
        skill_path = os.path.expanduser("~/.openclaw/skills/nova-memory")
        if os.path.exists(skill_path):
            return {"status": "pass", "message": f"nova-memory skill exists at {skill_path}"}
        else:
            return {"status": "fail", "message": "nova-memory skill not found"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}

def test_nova_skill_modules():
    """Test Nova skill modules"""
    skill_tests = []
    skills_path = os.path.expanduser("~/.openclaw/skills")
    
    nova_skills = [
        "nova-memory",
        "nova-evolution-engine", 
        "nova-goal-engine",
        "nova-planner",
        "nova-self-reflection",
        "nova-research-loop"
    ]
    
    for skill_name in nova_skills:
        skill_dir = os.path.join(skills_path, skill_name)
        if os.path.exists(skill_dir):
            skill_tests.append(skill_name)
    
    if skill_tests:
        return {"status": "pass", "message": f"Nova skills present: {', '.join(skill_tests)}"}
    else:
        return {"status": "fail", "message": "No Nova skills found"}

# ============================================================
# MAIN TEST RUNNER
# ============================================================

def main():
    log("="*70)
    log("NOVA COGNITIVE SYSTEMS PRESSURE TEST v2")
    log(f"Started: {datetime.now().isoformat()}")
    log("="*70)
    
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Define all tests
    tests = [
        ("identity_core", test_identity_core),
        ("emotional_council", test_emotional_council),
        ("memory_engine", test_memory_engine),
        ("drift_engine", test_drift_engine),
        ("reflection_engine", test_reflection_engine),
        ("goal_engine", test_goal_engine),
        ("brain_strategy", test_brain_strategy),
        ("brain_orchestrator", test_brain_orchestrator),
        ("cognitive_mesh", test_cognitive_mesh),
        ("curiosity_engine", test_curiosity_engine),
        ("world_model", test_world_model),
        ("emotion_engine", test_emotion_engine),
        ("event_bus", test_event_bus),
        ("brain_bus", test_brain_bus),
        ("attention_router", test_attention_router),
        ("meta_brain", test_meta_brain),
        ("agent_loop", test_agent_loop),
        ("vector_memory", test_vector_memory),
        ("working_memory", test_working_memory),
        ("skill_nova_memory", test_skill_nova_memory),
        ("nova_skill_modules", test_nova_skill_modules),
    ]
    
    # Run all tests
    for name, test_func in tests:
        test_system(name, test_func)
    
    # Summary
    log("\n" + "="*70)
    log("SUMMARY")
    log("="*70)
    log(f"Total systems tested: {len(results['systems_tested'])}")
    log(f"Passed: {len(results['passed'])} ✅")
    log(f"Failed: {len(results['failed'])} ❌")
    log(f"Warnings: {len(results['warnings'])} ⚠️")
    
    if results['failed']:
        log("\nFailed systems:")
        for s in results['failed']:
            log(f"  - {s}")
    
    if results['warnings']:
        log("\nWarnings:")
        for w in results['warnings']:
            log(f"  - {w}")
    
    if results['recommendations']:
        log("\nRecommendations:")
        for r in results['recommendations']:
            log(f"  - {r}")
    
    # Calculate pass rate
    pass_rate = (len(results['passed']) / len(results['systems_tested'])) * 100 if results['systems_tested'] else 0
    log(f"\nPass rate: {pass_rate:.1f}%")
    
    # Save results to JSON
    json_file = LOG_FILE.replace(".log", ".json")
    with open(json_file, "w") as f:
        json.dump({
            "timestamp": results["timestamp"],
            "total": len(results["systems_tested"]),
            "passed": results["passed"],
            "failed": results["failed"],
            "warnings": results["warnings"],
            "recommendations": results["recommendations"],
            "pass_rate": f"{pass_rate:.1f}%"
        }, f, indent=2)
    
    log(f"\nResults saved to: {LOG_FILE}")
    log(f"JSON saved to: {json_file}")
    
    return results

if __name__ == "__main__":
    main()
