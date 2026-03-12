#!/usr/bin/env python3
"""
Log proactive message outcomes for learning
"""
import os
import json
from datetime import datetime

LOG_FILE = os.path.expanduser("~/.nova/logs/proactive_outcomes.json")

def log_outcome(message: str, user_response: str = None, reaction: str = None):
    """Log the outcome of a proactive message for learning"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    outcomes = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            outcomes = json.load(f)
    
    outcomes.append({
        "timestamp": datetime.now().isoformat(),
        "message": message[:100],
        "user_response": user_response,
        "reaction": reaction
    })
    
    # Keep last 50
    outcomes = outcomes[-50:]
    
    with open(LOG_FILE, "w") as f:
        json.dump(outcomes, f, indent=2)

def get_recent_outcomes(count: int = 10):
    """Get recent message outcomes"""
    if not os.path.exists(LOG_FILE):
        return []
    
    with open(LOG_FILE) as f:
        return json.load(f)[-count:]

def should_adjust_threshold():
    """Analyze outcomes and suggest threshold adjustments"""
    outcomes = get_recent_outcomes(10)
    
    if len(outcomes) < 3:
        return None
    
    ignored = sum(1 for o in outcomes if o.get("reaction") == "ignored")
    engaged = sum(1 for o in outcomes if o.get("user_response"))
    
    if ignored > engaged * 2:
        return "raise"  # Too many ignored messages
    elif engaged > ignored:
        return "lower"  # Messages are well received
    
    return None
