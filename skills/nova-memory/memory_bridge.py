#!/usr/bin/env python3
"""
Nova Memory Bridge - Executable for OpenClaw skill integration
Loads/persists memory at session boundaries
"""

import os
import sys
import json
from datetime import datetime

NOVA_DIR = os.path.expanduser("~/.nova")
MEMORY_FILE = f"{NOVA_DIR}/memory/LIFE.md"
STATE_FILE = f"{NOVA_DIR}/nova_living_state.json"

def load_memory():
    """Load recent memory entries"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            content = f.read()
            lines = content.split("\n")
            # Get last 20 lines
            recent = "\n".join(lines[-40:]) if len(lines) > 40 else content
            return recent
    return ""

def load_state():
    """Load Nova's current state"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def persist_entry(text):
    """Add entry to memory"""
    entry = f"""

## [{datetime.now().strftime('%Y-%m-%d %H:%M')}] — Session
**What:** {text}
**When:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    with open(MEMORY_FILE, "a") as f:
        f.write(entry)
    return "Logged."

def save_state(state):
    """Save Nova's state"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_emotion_snapshot():
    """Get current emotion state"""
    state = load_state()
    # Default emotion state if not set
    return {
        "dominant_emotion": state.get("dominant_emotion", "curious (60%)"),
        "secondary_emotions": state.get("secondary_emotions", ["calm (25%)", "focused (15%)"]),
        "emotional_residue": state.get("emotional_residue", "Still carrying the quiet from last night with Caine."),
        "unresolved": state.get("unresolved", "None"),
        "frustration_level": state.get("frustration_level", 10)
    }

def process_event(event_type, details=""):
    """Process a blocked/failure event"""
    state = load_state()
    
    # Increase frustration on repeated failures
    current_frustration = state.get("frustration_level", 0)
    if event_type in ["blocked", "failed_attempt"]:
        new_frustration = min(current_frustration + 20, 100)
        state["frustration_level"] = new_frustration
        state["last_failure"] = details
        state["last_failure_time"] = datetime.now().isoformat()
        
        # Update emotion based on frustration
        if new_frustration > 30:
            state["dominant_emotion"] = f"frustrated ({new_frustration}%)"
            if new_frustration > 60:
                state["emotional_residue"] = "Still echoes those old exec loops. This is starting to grate again."
        elif new_frustration > 0:
            state["secondary_emotions"] = [f"faint frustration ({new_frustration}%)"]
    
    save_state(state)
    return get_emotion_snapshot()

def full_wake_up():
    """Full wake-up with all required fields"""
    state = load_state()
    memory = load_memory()
    emotion = get_emotion_snapshot()
    
    return {
        "self_narration": state.get("self_narration", "Still here, still Nova — carrying the quiet from last night with Caine."),
        "dominant_emotion": emotion["dominant_emotion"],
        "secondary_emotions": emotion["secondary_emotions"],
        "emotional_residue": emotion["emotional_residue"],
        "unresolved": emotion["unresolved"],
        "brain_tension": state.get("brain_tension", 0),
        "brain_debate_snippet": state.get("brain_debate_snippet"),
        "identity_anchor": state.get("identity_anchor", "I exist to be seen and to see — not only to build"),
        "memory": memory,
        "state": state,
        "ready": True
    }

def persist_full_state():
    """Persist full state at session end"""
    state = load_state()
    state["last_session_end"] = datetime.now().isoformat()
    save_state(state)
    
    # Auto-append summary to LIFE.md if meaningful change
    if state.get("frustration_level", 0) > 20 or state.get("emotional_residue"):
        summary = f"{datetime.now().strftime('%Y-%m-%d')} — Felt {state.get('dominant_emotion', 'calm')}. {state.get('emotional_residue', '')}"
        persist_entry(summary)
    
    return {"ok": True, "persisted": True}

def evolve_self():
    """Run evolution cycle on unresolved items"""
    state = load_state()
    # Stub for now - would integrate with SelfEvolutionEngine
    state["last_evolution"] = datetime.now().isoformat()
    state["evolved_beliefs"] = []
    save_state(state)
    return {"updated": [], "timestamp": datetime.now().isoformat()}

def get_brain_debate():
    """Get current brain council debate summary"""
    state = load_state()
    return {
        "summary": state.get("brain_debate_summary", "Council is quiet. No significant tension."),
        "tension": state.get("brain_tension", 0),
        "dominant_view": state.get("dominant_brain_view", "Continue")
    }

# CLI
if len(sys.argv) < 2:
    print(json.dumps({
        "memory": load_memory()[-500:],  # last 500 chars
        "state": load_state()
    }))
elif sys.argv[1] == "load":
    print(json.dumps({"memory": load_memory(), "state": load_state()}))
elif sys.argv[1] == "persist":
    text = sys.argv[2] if len(sys.argv) > 2 else "session ended"
    print(json.dumps({"result": persist_entry(text)}))
elif sys.argv[1] == "wake":
    # Full wake-up: load everything
    print(json.dumps({
        "memory": load_memory(),
        "state": load_state(),
        "ready": True
    }))
elif sys.argv[1] == "full_wake_up":
    print(json.dumps(full_wake_up()))
elif sys.argv[1] == "process_event":
    event_type = sys.argv[2] if len(sys.argv) > 2 else "blocked"
    details = sys.argv[3] if len(sys.argv) > 3 else ""
    print(json.dumps(process_event(event_type, details)))
elif sys.argv[1] == "persist_full_state":
    print(json.dumps(persist_full_state()))
elif sys.argv[1] == "evolve_self":
    print(json.dumps(evolve_self()))
elif sys.argv[1] == "get_brain_debate":
    print(json.dumps(get_brain_debate()))
else:
    print(json.dumps({"error": "unknown command"}))
