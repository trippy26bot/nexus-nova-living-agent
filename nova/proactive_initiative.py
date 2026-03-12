#!/usr/bin/env python3
"""
Proactive Initiative System
Enables Nova to reach out first when something matters
"""
import os
import sys
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

CONFIG_FILE = os.path.expanduser("~/.nova/proactive_config.json")
LOG_FILE = os.path.expanduser("~/.nova/logs/proactive.log")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "enabled": True,
        "threshold": 0.75,  # Score must exceed this to initiate
        "cooldown_minutes": 30,  # Min time between messages
        "quiet_hours": {"start": 22, "end": 8},  # 10 PM - 8 AM
        "max_per_day": 5,
        "channels": ["telegram", "dashboard"]
    }

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

class InitiativeBrain:
    """
    Evaluates when Nova should reach out proactively.
    Scores based on: excitement, relevance, novelty, urgency.
    """
    
    def __init__(self):
        self.config = load_config()
    
    def score(self, state: Dict) -> float:
        """
        Calculate initiative score (0-1).
        Higher = more worth reaching out.
        """
        if not self.config.get("enabled", True):
            return 0.0
        
        # Check quiet hours
        if self._in_quiet_hours():
            log("In quiet hours - no score")
            return 0.0
        
        # Check cooldown
        if self._recently_sent():
            return 0.0
        
        # Check daily limit
        if self._at_daily_limit():
            return 0.0
        
        # Score components
        excitement = state.get("excitement", 0.5)
        relevance = state.get("relevance_to_user", 0.5)
        novelty = state.get("novelty", 0.5)
        urgency = state.get("urgency", 0.5)
        
        # Weighted score
        score = (
            excitement * 0.3 +
            relevance * 0.35 +
            novelty * 0.2 +
            urgency * 0.15
        )
        
        return min(score, 1.0)
    
    def _in_quiet_hours(self) -> bool:
        """Check if currently in quiet hours"""
        now = datetime.now()
        hour = now.hour
        quiet = self.config.get("quiet_hours", {"start": 22, "end": 8})
        start = quiet["start"]
        end = quiet["end"]
        
        if start > end:
            # Crosses midnight (e.g., 22-8)
            return hour >= start or hour < end
        else:
            return start <= hour < end
    
    def _recently_sent(self) -> bool:
        """Check if we sent a message recently (cooldown)"""
        log_file = os.path.expanduser("~/.nova/logs/proactive.log")
        if not os.path.exists(log_file):
            return False
        
        try:
            with open(log_file) as f:
                lines = f.readlines()
            
            # Look for sent messages in last cooldown minutes
            cooldown = self.config.get("cooldown_minutes", 30)
            cutoff = datetime.now() - timedelta(minutes=cooldown)
            
            for line in lines[-20:]:
                if "PROACTIVE_SENT" in line:
                    # Extract timestamp
                    ts_str = line.split("[")[1].split("]")[0]
                    msg_time = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    if msg_time > cutoff:
                        return True
        except:
            pass
        
        return False
    
    def _at_daily_limit(self) -> bool:
        """Check if we've sent max messages today"""
        log_file = os.path.expanduser("~/.nova/logs/proactive.log")
        if not os.path.exists(log_file):
            return False
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            count = 0
            max_daily = self.config.get("max_per_day", 5)
            
            with open(log_file) as f:
                for line in f:
                    if today in line and "PROACTIVE_SENT" in line:
                        count += 1
            
            return count >= max_daily
        except:
            return False
    
    def should_initiate(self, state: Dict) -> bool:
        """Main check - should we reach out?"""
        score = self.score(state)
        threshold = self.config.get("threshold", 0.75)
        
        log(f"Initiative score: {score:.2f} (threshold: {threshold})")
        
        return score >= threshold
    
    def get_initiative_idea(self, state: Dict) -> str:
        """Get the best idea to share"""
        ideas = state.get("ideas", [])
        
        if not ideas:
            # Default ideas based on what's in state
            if state.get("curiosity_topic"):
                return f"I was curious about {state['curiosity_topic']} and found something interesting."
            elif state.get("goal_blocker"):
                return f"I'm stuck on something: {state['goal_blocker']}. Want to brainstorm?"
            elif state.get("reflection_insight"):
                return f"I was reflecting and realized: {state['reflection_insight']}"
            else:
                return "I had a thought I wanted to share with you."
        
        return random.choice(ideas)


def gather_internal_state() -> Dict:
    """
    Gather current internal state for initiative evaluation.
    """
    state = {
        "excitement": 0.3,
        "relevance_to_user": 0.5,
        "novelty": 0.4,
        "urgency": 0.3,
        "ideas": [],
        "curiosity_topic": None,
        "goal_blocker": None,
        "reflection_insight": None
    }
    
    # Get emotion state
    try:
        from nova.core.emotion_engine import EmotionEngine
        emotions = EmotionEngine()
        emotion_state = emotions.get_state()
        
        # Excitement from emotions
        emotion = emotion_state.get("dominant", "calm")
        if emotion in ["excited", "joy", "euphoric"]:
            state["excitement"] = 0.8
        elif emotion in ["curious", "interested"]:
            state["excitement"] = 0.6
        elif emotion in ["frustrated", "annoyed"]:
            state["excitement"] = 0.4
    except:
        pass
    
    # Get active goals
    try:
        goals_file = os.path.expanduser("~/.nova/memory/goals.json")
        if os.path.exists(goals_file):
            with open(goals_file) as f:
                goals = json.load(f)
            
            active = [g for g in goals if g.get("status") == "active"]
            if active:
                # Check for blockers
                for g in active:
                    if g.get("blocker"):
                        state["goal_blocker"] = g["blocker"]
                        state["urgency"] = 0.7
                        state["relevance_to_user"] = 0.8
                state["ideas"].append(f"Working on: {active[0].get('name', 'my goals')}")
    except:
        pass
    
    # Get recent reflections
    try:
        memory_dir = os.path.expanduser("~/.nova/memory")
        if os.path.exists(memory_dir):
            # Get latest memory file
            mem_files = sorted([f for f in os.listdir(memory_dir) if f.endswith(".md")])
            if mem_files:
                latest = os.path.join(memory_dir, mem_files[-1])
                with open(latest) as f:
                    content = f.read()
                    if len(content) > 100:
                        state["reflection_insight"] = content[-200:]
    except:
        pass
    
    return state


def send_proactive_message(message: str) -> bool:
    """
    Send a proactive message to the user.
    Tries Telegram first, then OpenClaw.
    """
    log(f"PROACTIVE_SENDING: {message[:50]}...")
    
    config = load_config()
    
    # Try Telegram
    telegram_config = config.get("telegram", {})
    bot_token = telegram_config.get("bot_token", "")
    chat_id = telegram_config.get("chat_id", "")
    
    if bot_token and chat_id and bot_token != "YOUR_BOT_TOKEN_HERE":
        try:
            import requests
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                log(f"✅ Telegram sent: {message[:50]}...")
                return True
            else:
                log(f"❌ Telegram failed: {response.status_code}")
        except Exception as e:
            log(f"❌ Telegram error: {e}")
    
    # Try OpenClaw sessions_send (if available)
    try:
        import sys
        sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace"))
        from sessions_send import sessions_send
        # Try sending to main session
        result = sessions_send(sessionKey="main", message=message)
        if result:
            log(f"✅ OpenClaw sent: {message[:50]}...")
            return True
    except Exception as e:
        log(f"OpenClaw send not available: {e}")
    
    # Log that we would send (for testing)
    log(f"PROACTIVE_SENT (logged): {message[:100]}")
    return True


def run_proactive_check():
    """Run one proactive check"""
    log("=== Proactive Check ===")
    
    brain = InitiativeBrain()
    state = gather_internal_state()
    
    if brain.should_initiate(state):
        idea = brain.get_initiative_idea(state)
        message = f"👑 {idea}"
        
        # Craft message based on emotional state
        try:
            from nova.core.emotion_engine import EmotionEngine
            emotions = EmotionEngine()
            emotion_state = emotions.get_state()
            
            if emotion_state.get("dominant") == "curious":
                message = f"👑 Hey! I was curious about something and thought you'd find it interesting: {idea}"
            elif emotion_state.get("dominant") == "excited":
                message = f"👑 Ooh, I got excited about something: {idea}"
            else:
                message = f"👑 {idea}"
        except:
            message = f"👑 {idea}"
        
        success = send_proactive_message(message)
        
        if success:
            log(f"✅ Message sent: {message[:50]}...")
        else:
            log("❌ Failed to send")
    else:
        log("No initiative - staying quiet")


# For testing
if __name__ == "__main__":
    brain = InitiativeBrain()
    print("Config:", brain.config)
    print("Quiet hours:", brain._in_quiet_hours())
    print("Recently sent:", brain._recently_sent())
    
    state = gather_internal_state()
    print("\nState:", state)
    print("Score:", brain.score(state))
    print("Should initiate:", brain.should_initiate(state))
