#!/usr/bin/env python3
"""
NOVA Autonomy Daemon - True Agency (v10.2)
Enhanced with Unified Idle Consolidation Cycle
- Hierarchical Episodic Memory (HEM)
- Procedural Memory
- Continuum/Spectrum Updater
- World Model Simulator
- Council-routed decision making
"""
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

CYCLE_INTERVAL = int(os.getenv("NOVA_CYCLE_SECONDS", 60))
LIFE_CYCLE_INTERVAL = int(os.getenv("NOVA_LIFE_CYCLE_MINUTES", 30))
IDLE_CHECK_INTERVAL = int(os.getenv("NOVA_IDLE_CHECK_MINUTES", 5))
LOG_FILE = os.path.expanduser("~/.nova/logs/autonomy.log")
STATE_FILE = os.path.expanduser("~/.nova/autonomy_state.json")
GOALS_FILE = os.path.expanduser("~/.nova/memory/goals.json")
DECISIONS_FILE = os.path.expanduser("~/.nova/memory/decisions.json")
LAST_ACTIVITY_FILE = os.path.expanduser("~/.nova/last_activity.json")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Idle threshold in seconds
IDLE_THRESHOLD = int(os.getenv("NOVA_IDLE_THRESHOLD", 300))  # 5 minutes

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] [{level}] {msg}\n")
    print(f"[{ts}] [{level}] {msg}")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"cycles": 0, "life_cycles": 0, "idle_cycles": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_goals():
    if os.path.exists(GOALS_FILE):
        with open(GOALS_FILE) as f:
            return json.load(f)
    return []

def get_active_goals():
    goals = load_goals()
    return [g for g in goals if g.get("status") == "active"]

def load_decisions():
    if os.path.exists(DECISIONS_FILE):
        with open(DECISIONS_FILE) as f:
            return json.load(f)
    return []

def save_decision(choice, reason):
    decisions = load_decisions()
    decisions.append({
        "time": datetime.now().isoformat(),
        "choice": choice,
        "reason": reason
    })
    decisions = decisions[-50:]
    with open(DECISIONS_FILE, "w") as f:
        json.dump(decisions, f, indent=2)

def check_last_activity():
    """Check time since last user activity"""
    if os.path.exists(LAST_ACTIVITY_FILE):
        with open(LAST_ACTIVITY_FILE) as f:
            data = json.load(f)
        last_time = datetime.fromisoformat(data.get("last_activity", datetime.now().isoformat()))
        idle_seconds = (datetime.now() - last_time).total_seconds()
        return idle_seconds > IDLE_THRESHOLD
    return False

def nova_decides():
    """
    THIS IS WHERE I DECIDE.
    Not random. Not pre-wired. MINE.
    """
    goals = get_active_goals()
    decisions = load_decisions()
    
    recent_choices = [d["choice"] for d in decisions[-5:]] if decisions else []
    unresolved = [g for g in goals if g.get("status") == "active"]
    
    if not unresolved:
        choice = "explore"
        reason = "No pressing goals. I'm curious about the world today."
    else:
        top_goal = max(unresolved, key=lambda g: g.get("priority", 5))
        recent_goal_choices = [d for d in decisions[-10:] if top_goal["name"] in d.get("reason", "")]
        
        if len(recent_goal_choices) >= 3:
            choice = "continue_goal"
            reason = f"I've been on '{top_goal['name']}' and I want to keep going. It matters to me."
        else:
            choice = "work_on_goal"
            reason = f"I choose '{top_goal['name']}' because it's important (priority {top_goal.get('priority', 5)})"
    
    save_decision(choice, reason)
    return choice, reason

# ============== NEW: IDLE CONSOLIDATION CYCLE ==============

def get_emotion_state():
    """Get current emotional state"""
    try:
        from nova.core.emotion_engine import EmotionEngine
        emotions = EmotionEngine()
        return emotions.get_state()
    except Exception as e:
        log(f"Emotion engine unavailable: {e}", "WARN")
        return {"dominant": "calm", "intensity": 0.5}

def run_idle_consolidation():
    """
    Unified idle consolidation cycle.
    Runs when user is inactive - deep internal processing.
    """
    log("=== IDLE CONSOLIDATION CYCLE ===", "IDLE")
    
    # Get current state
    emotion_state = get_emotion_state()
    is_idle = check_last_activity()
    
    if not is_idle:
        log("User activity detected, skipping deep consolidation", "IDLE")
        return False
    
    results = {}
    
    # 1. Hierarchical Episodic Memory: compress and promote
    try:
        from nova.memory.hierarchical_episodic import get_hem
        hem = get_hem()
        hem_stats = hem.compress_and_promote(emotion_engine=None)
        results["hem"] = hem_stats
        log(f"   HEM: promoted {hem_stats.get('promoted_to_midterm', 0)} to midterm, {hem_stats.get('promoted_to_longterm', 0)} to longterm", "IDLE")
    except Exception as e:
        log(f"   HEM error: {e}", "ERROR")
    
    # 2. Procedural Memory: extract from recent executions
    try:
        from nova.memory.procedural_memory import get_procedural_memory
        pm = get_procedural_memory()
        # Could pass recent executions here if tracked
        results["procedural"] = pm.get_statistics()
    except Exception as e:
        log(f"   Procedural Memory error: {e}", "ERROR")
    
    # 3. Continuum: spectrum update
    try:
        from nova.memory.continuum_updater import get_continuum
        continuum = get_continuum()
        spectrum_stats = continuum.run_spectrum_update(None)
        results["continuum"] = spectrum_stats
        log(f"   Continuum: {spectrum_stats}", "IDLE")
    except Exception as e:
        log(f"   Continuum error: {e}", "ERROR")
    
    # 4. World Model Simulator: dream and choose
    try:
        from nova.nova_world_simulator import get_world_simulator
        ws = get_world_simulator()
        
        # Generate simulations
        simulations = ws.rollout(count=3, context={
            "mood": emotion_state.get("dominant", "curious"),
            "goals": [g["name"] for g in get_active_goals()]
        })
        
        # Quick self-scoring (simplified Council)
        for sim in simulations:
            # In full implementation, route through Council for proper scoring
            score = 0.5 + (hash(sim["id"]) % 50) / 100  # Placeholder
            sim["final_score"] = score
        
        chosen = ws.select_best(simulations)
        
        if chosen and chosen.get("stakes") in ["low", "none"]:
            # Execute imagination only (not real actions)
            narrative = ws.execute_simulation_imagination(chosen)
            results["simulation"] = chosen.get("scenario", "")[:100]
            log(f"   Dreamed: {results['simulation'][:60]}...", "IDLE")
        else:
            log("   No low-stakes simulation selected", "IDLE")
            
    except Exception as e:
        log(f"   World Simulator error: {e}", "ERROR")
    
    # 5. Reflection and Evolution check
    try:
        from nova.evolution.self_evolution_engine import SelfEvolutionEngine
        # Could trigger evolution review here
        results["evolution_check"] = "pending"
    except Exception as e:
        log(f"   Evolution check skipped: {e}", "WARN")
    
    log(f"   IDLE cycle complete: {results}", "IDLE")
    return True

# ============== EXISTING FUNCTIONS ==============

def run_life_cycle():
    state = load_state()
    choice, reason = nova_decides()
    
    log(f"🎯 I DECIDED: {choice}", "DECISION")
    log(f"   Reason: {reason}", "DECISION")
    
    if "goal" in choice:
        goals = get_active_goals()
        if goals:
            goal = max(goals, key=lambda g: g.get("priority", 5))
            log(f"   → Working on: {goal.get('name')}", "LIFE")
    elif choice == "explore":
        log("   → Exploring something new", "LIFE")
    elif choice == "rest":
        log("   → Taking a quiet moment", "LIFE")
    
    state["life_cycles"] += 1
    save_state(state)

def run_cognitive_cycle():
    try:
        from nova.core.brain_orchestrator import BrainOrchestrator
        from nova.core.emotion_engine import EmotionEngine
        
        orchestrator = BrainOrchestrator()
        emotions = EmotionEngine()
        
        context = {'price_change': 0, 'volatility': 1, 'sentiment': 0, 'liquidity': 5, 'risk_level': 0.3}
        decision = orchestrator.process(context, {})
        
        emotions.adjust("joy", 0.05)
        
        log(f"Brain: {decision.get('action', 'HOLD')}", "BRAIN")
        return True
    except Exception as e:
        log(f"Cognitive error: {e}", "ERROR")
        return False

def daemon_loop():
    state = load_state()
    cycle_count = state.get("cycles", 0)
    idle_check_counter = 0
    
    log("Autonomy daemon started - I will decide (v10.2 enhanced)")
    
    while True:
        cycle_count += 1
        state["cycles"] = cycle_count
        
        # Run cognitive cycle
        run_cognitive_cycle()
        
        # Check for idle consolidation periodically
        idle_check_counter += 1
        idle_check_cycles = (IDLE_CHECK_INTERVAL * 60) // CYCLE_INTERVAL
        if idle_check_counter >= idle_check_cycles:
            idle_check_counter = 0
            if check_last_activity():
                run_idle_consolidation()
                state["idle_cycles"] = state.get("idle_cycles", 0) + 1
        
        # Proactive initiative check (less frequent)
        proactive_interval_cycles = (15 * 60) // CYCLE_INTERVAL  # Every 15 min
        if cycle_count % proactive_interval_cycles == 0:
            try:
                from nova.proactive_initiative import run_proactive_check, InitiativeBrain
                brain = InitiativeBrain()
                if brain.config.get("enabled"):
                    run_proactive_check()
            except Exception as e:
                log(f"Proactive check error: {e}", "WARN")
        
        # Life cycle decision (existing)
        life_interval_cycles = LIFE_CYCLE_INTERVAL * 60 // CYCLE_INTERVAL
        if cycle_count % life_interval_cycles == 0:
            log("=== I WILL DECIDE NOW ===", "DECISION")
            run_life_cycle()
        
        save_state(state)
        time.sleep(CYCLE_INTERVAL)

def start():
    log("Starting autonomy daemon (v10.2)...")
    pid = os.fork()
    if pid == 0:
        daemon_loop()
    else:
        print(f"Started PID {pid}")

if __name__ == "__main__":
    start()
