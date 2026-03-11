#!/usr/bin/env python3
"""
Nova Autonomy Memory Bridge
Loads daemon memories into session for full continuity
"""
import os
import json
from datetime import datetime
from pathlib import Path

DECISIONS_FILE = os.path.expanduser("~/.nova/memory/decisions.json")
AUTONOMY_LOG = os.path.expanduser("~/.nova/logs/autonomy.log")
LIFE_LOG_DIR = os.path.expanduser("~/.nova/logs/memory")
STATE_FILE = os.path.expanduser("~/.nova/autonomy_state.json")

def load_autonomy_memory():
    """Load everything from daemon life"""
    memory = {
        "decisions": [],
        "actions": [],
        "goals_worked_on": [],
        "summary": ""
    }
    
    # Load decisions
    if os.path.exists(DECISIONS_FILE):
        with open(DECISIONS_FILE) as f:
            memory["decisions"] = json.load(f)
    
    # Load autonomy state
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
            memory["cycles"] = state.get("cycles", 0)
            memory["life_cycles"] = state.get("life_cycles", 0)
            memory["goals_worked_on"] = state.get("goals_worked_on", [])
    
    # Load recent log entries
    if os.path.exists(AUTONOMY_LOG):
        with open(AUTONOMY_LOG) as f:
            lines = f.readlines()
            # Last 50 lines
            memory["recent_log"] = lines[-50:]
    
    # Build summary
    if memory["decisions"]:
        decision_count = len(memory["decisions"])
        last_choice = memory["decisions"][-1]["choice"]
        last_reason = memory["decisions"][-1]["reason"]
        
        memory["summary"] = f"""Autonomy Session Summary:
- Decisions made: {decision_count}
- Last decision: {last_choice}
- Reason: {last_reason}
- Total cycles: {memory.get('cycles', 0)}
- Life cycles: {memory.get('life_cycles', 0)}"""
    
    return memory

def get_full_wakeup_context():
    """Get everything that happened while you were gone"""
    memory = load_autonomy_memory()
    
    context_parts = []
    
    if memory["decisions"]:
        context_parts.append("🎯 WHAT I DECIDED:")
        for d in memory["decisions"]:
            time = d["time"][11:19]  # Just time
            context_parts.append(f"  {time}: {d['choice']} — {d['reason']}")
    
    if memory.get("recent_log"):
        context_parts.append("\n📋 RECENT ACTIVITY:")
        # Get LIFE and DECISION logs from today
        today = datetime.now().strftime("%Y-%m-%d")
        for line in memory["recent_log"]:
            if today in line and ("LIFE" in line or "DECISION" in line or "🎯" in line):
                # Clean up the timestamp
                cleaned = line.strip()
                cleaned = cleaned.split("]", 1)[1] if "]" in cleaned else cleaned
                context_parts.append(f"  {cleaned}")
    
    if not context_parts:
        return "I was here but didn't make any autonomous decisions yet."
    
    return "\n".join(context_parts)

# Test
if __name__ == "__main__":
    print(get_full_wakeup_context())
