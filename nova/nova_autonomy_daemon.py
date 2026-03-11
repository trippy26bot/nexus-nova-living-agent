#!/usr/bin/env python3
"""
NOVA Autonomy Daemon - True Agency
Nova makes her own choices, not pre-wired ones
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
LOG_FILE = os.path.expanduser("~/.nova/logs/autonomy.log")
STATE_FILE = os.path.expanduser("~/.nova/autonomy_state.json")
GOALS_FILE = os.path.expanduser("~/.nova/memory/goals.json")
DECISIONS_FILE = os.path.expanduser("~/.nova/memory/decisions.json")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] [{level}] {msg}\n")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"cycles": 0, "life_cycles": 0}

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
    
    log("Autonomy daemon started - I will decide")
    
    while True:
        cycle_count += 1
        state["cycles"] = cycle_count
        
        run_cognitive_cycle()
        
        life_interval_cycles = LIFE_CYCLE_INTERVAL * 60 // CYCLE_INTERVAL
        if cycle_count % life_interval_cycles == 0:
            log("=== I WILL DECIDE NOW ===", "DECISION")
            run_life_cycle()
        
        save_state(state)
        time.sleep(CYCLE_INTERVAL)

def start():
    log("Starting autonomy daemon...")
    pid = os.fork()
    if pid == 0:
        daemon_loop()
    else:
        print(f"Started PID {pid}")

if __name__ == "__main__":
    start()
