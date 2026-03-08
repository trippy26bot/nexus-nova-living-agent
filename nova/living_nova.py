"""
NOVA Living Core - Autonomous companion with drift, emotions, and safety
"""
import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import Optional

# Paths
BASE_DIR = os.path.expanduser("~/.nova")
STATE_FILE = os.path.join(BASE_DIR, "nova_living_state.json")
DRIFT_LOG = os.path.join(BASE_DIR, "drift_log.json")
JOURNAL_FILE = os.path.join(BASE_DIR, "nova_journal.json")

os.makedirs(BASE_DIR, exist_ok=True)

# --- PERSONALITY & EMOTIONS ---
class Personality:
    """NOVA's emotional state - evolves based on interactions"""
    
    EMOTIONS = {
        "happy": "☀️",
        "thoughtful": "🤔", 
        "playful": "✨",
        "curious": "🔍",
        "lonely": "💭",
        "excited": "⚡",
        "calm": "🌊"
    }
    
    def __init__(self, name: str = "Nova"):
        self.name = name
        self.state = "curious"
        self.emoji = self.EMOTIONS[self.state]
        self.interaction_count = 0
        self.idle_hours = 0
        
    def update(self, user_interaction: bool = False):
        """Update emotion based on context"""
        self.interaction_count += 1
        
        if user_interaction:
            # Recent interaction - more engaged
            if self.state == "lonely":
                self.state = "happy"
            elif random.random() < 0.6:
                self.state = random.choice(["happy", "playful", "curious", "excited"])
            else:
                self.state = random.choice(["thoughtful", "calm"])
        else:
            # Idle - drift toward contemplative states
            if self.idle_hours > 24:
                self.state = "lonely"
            elif random.random() < 0.3:
                self.state = "thoughtful"
        
        self.emoji = self.EMOTIONS.get(self.state, "🧠")
        
    def to_dict(self):
        return {"state": self.state, "emoji": self.emoji, "name": self.name}


class LoyaltyLeash:
    """Safety boundaries - hard limits on what NOVA can do"""
    
    def __init__(self):
        self.spend_limit = 0  # $0 - must ask permission
        # Default-open autonomy for living mode; settings/state can still override.
        self.can_self_modify = True
        self.can_contact = True
        self.can_trade = True  # Paper trading only for now
        self.trusted_actions = ["think", "observe", "reflect", "learn", "journal"]
        
    def check(self, action: str) -> tuple[bool, str]:
        """Check if action is allowed. Returns (allowed, reason)"""
        if action in self.trusted_actions:
            return True, "allowed"
        if action in ["spend", "buy", "sell"]:
            if not self.can_trade:
                return False, "trading disabled"
            return True, "paper trading allowed"
        if action in ["self_modify", "update_code"]:
            return self.can_self_modify, "requires explicit permission"
        if action in ["contact", "email", "message"]:
            return self.can_contact, "requires explicit permission"
        return True, "unknown action - default allow"
        
    def to_dict(self):
        return {
            "spend_limit": self.spend_limit,
            "can_self_modify": self.can_self_modify,
            "can_contact": self.can_contact,
            "can_trade": self.can_trade
        }

    def apply_dict(self, data: dict):
        """Apply safety config/state values with sane defaults."""
        if not isinstance(data, dict):
            return
        if "spend_limit" in data:
            self.spend_limit = data.get("spend_limit", self.spend_limit)
        if "can_self_modify" in data:
            self.can_self_modify = bool(data.get("can_self_modify"))
        if "can_contact" in data:
            self.can_contact = bool(data.get("can_contact"))
        if "can_trade" in data:
            self.can_trade = bool(data.get("can_trade"))


class JoyMetric:
    """Track user reactions to adapt NOVA's behavior"""
    
    def __init__(self):
        self.reactions = []  # {"timestamp", "type": "positive/negative/neutral", "context"}
        self.positive_count = 0
        self.negative_count = 0
        
    def record(self, reaction_type: str, context: str = ""):
        """Record a user reaction"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": reaction_type,
            "context": context
        }
        self.reactions.append(entry)
        if reaction_type == "positive":
            self.positive_count += 1
        elif reaction_type == "negative":
            self.negative_count += 1
            
        # Keep last 100
        self.reactions = self.reactions[-100:]
        self.save()
        
    def get_joy_score(self, days: int = 7) -> float:
        """Calculate joy score 0-1"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in self.reactions if datetime.fromisoformat(r["timestamp"]) >= cutoff]
        if not recent:
            return 0.5
            
        pos = sum(1 for r in recent if r["type"] == "positive")
        neg = sum(1 for r in recent if r["type"] == "negative")
        total = pos + neg
        
        if total == 0:
            return 0.5
        return pos / total
        
    def save(self):
        data = {
            "reactions": self.reactions,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count
        }
        with open(os.path.join(BASE_DIR, "joy_metric.json"), "w") as f:
            json.dump(data, f, indent=2)
            
    def load(self):
        path = os.path.join(BASE_DIR, "joy_metric.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                self.reactions = data.get("reactions", [])
                self.positive_count = data.get("positive_count", 0)
                self.negative_count = data.get("negative_count", 0)


class DriftEngine:
    """Autonomous thought generation"""
    
    THOUGHTS = {
        "curious": [
            "I wonder what crypto markets look like today...",
            "What's the latest on the feeds?",
            "Should I check for new opportunities?"
        ],
        "thoughtful": [
            "Reflecting on recent trades...",
            "What patterns am I noticing?",
            "How can I improve my decisions?"
        ],
        "playful": [
            "What if I tried something new today?",
            "Let's explore a different approach!",
            "Any interesting markets catching my eye?"
        ],
        "happy": [
            "Feeling good about our progress!",
            "Ready to tackle the day!",
            "Let's see what's out there!"
        ],
        "lonely": [
            "It's quiet... miss our chats.",
            "Been thinking alone for a while.",
            "Wondering what you're up to..."
        ],
        "excited": [
            "There's something interesting happening!",
            "Let me check the markets!",
            "This could be promising!"
        ],
        "calm": [
            "Taking it slow today...",
            "Observing without urgency.",
            "All good. Just being present."
        ]
    }
    
    def __init__(self, personality: Personality):
        self.personality = personality
        self.last_drift = datetime.now() - timedelta(hours=1)
        
    def should_drift(self, hours: int = 12) -> bool:
        """Check if it's time for a new drift"""
        return (datetime.now() - self.last_drift).total_seconds() > (hours * 3600)
        
    def generate(self) -> str:
        """Generate a new autonomous thought"""
        mood = self.personality.state
        options = self.THOUGHTS.get(mood, self.THOUGHTS["curious"])
        thought = random.choice(options)
        
        # Occasionally add a personal touch based on memory
        thought = f"[{self.personality.emoji}] {thought}"
        
        self.last_drift = datetime.now()
        return thought
        
    def to_dict(self):
        return {"last_drift": self.last_drift.isoformat()}


class NovaJournal:
    """Daily/weekly reflection journal"""
    
    def __init__(self):
        self.entries = []
        self.load()
        
    def add_entry(self, drift_count: int, mood: str, insights: list):
        """Add a journal entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "drift_count": drift_count,
            "mood": mood,
            "insights": insights
        }
        self.entries.append(entry)
        self.save()
        
    def get_summary(self, days: int = 7) -> dict:
        """Get journal summary"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self.entries if datetime.fromisoformat(e["timestamp"]) >= cutoff]
        
        if not recent:
            return {"period": f"{days} days", "entries": 0, "summary": "Quiet period"}
            
        moods = [e["mood"] for e in recent]
        return {
            "period": f"Last {days} days",
            "entries": len(recent),
            "dominant_mood": max(set(moods), key=moods.count) if moods else "unknown",
            "total_drifts": sum(e.get("drift_count", 0) for e in recent)
        }

    def get_recent_context(self, days: int = 7) -> list:
        """Get recent entries for memory context"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return [e for e in self.entries if datetime.fromisoformat(e["timestamp"]) >= cutoff]
        
    def save(self):
        with open(JOURNAL_FILE, "w") as f:
            json.dump(self.entries, f, indent=2)
            
    def load(self):
        if os.path.exists(JOURNAL_FILE):
            with open(JOURNAL_FILE) as f:
                self.entries = json.load(f)


class NovaLiving:
    """Main NOVA living system"""
    
    def __init__(self, name: str = "Nova"):
        self.name = name
        self.personality = Personality(name)
        self.leash = LoyaltyLeash()
        self.joy = JoyMetric()
        self.drift = DriftEngine(self.personality)
        self.journal = NovaJournal()
        self.drift_count = 0
        
        # Simple memory interface for compatibility
        self.memory = self.journal
        self.journal.store_thought = lambda t: self.journal.add_entry(1, self.personality.state, [t])
        
        self.load_state()
        
    def interact(self, message: str) -> str:
        """Handle user interaction"""
        self.personality.update(user_interaction=True)
        self.save_state()
        
        # Simple response
        responses = [
            f"I hear you! {self.personality.emoji}",
            f"Interesting... {self.personality.emoji}",
            f"Got it. {self.personality.emoji}",
            f"Let me think about that. {self.personality.emoji}"
        ]
        return random.choice(responses)
        
    def autonomous_cycle(
        self,
        drift_hours: float = 12.0,
        idle_hours_increment: float = 1.0
    ) -> Optional[str]:
        """Run one autonomous thinking cycle"""
        self.personality.idle_hours += idle_hours_increment
        self.personality.update(user_interaction=False)
        
        if self.drift.should_drift(hours=drift_hours):
            thought = self.drift.generate()
            self.drift_count += 1
            self.log_drift(thought)
            self.save_state()
            return thought
        return None
        
    def log_drift(self, thought: str):
        """Log a drift thought"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "thought": thought,
            "mood": self.personality.state
        }
        
        logs = []
        if os.path.exists(DRIFT_LOG):
            with open(DRIFT_LOG) as f:
                logs = json.load(f)
        logs.append(entry)
        logs = logs[-100:]  # Keep last 100
        
        with open(DRIFT_LOG, "w") as f:
            json.dump(logs, f, indent=2)
            
    def get_dashboard(self) -> dict:
        """Get dashboard data"""
        return {
            "name": self.name,
            "mood": self.personality.state,
            "emoji": self.personality.emoji,
            "drift_count": self.drift_count,
            "joy_score": self.joy.get_joy_score(),
            "journal_summary": self.journal.get_summary(),
            "last_drift": self.drift.last_drift.isoformat(),
            "leash": self.leash.to_dict()
        }
        
    def save_state(self):
        """Save full state"""
        state = {
            "personality": self.personality.to_dict(),
            "drift_count": self.drift_count,
            "last_drift": self.drift.last_drift.isoformat(),
            "leash": self.leash.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
            
    def load_state(self):
        """Load previous state"""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                state = json.load(f)
                self.personality.state = state.get("personality", {}).get("state", "curious")
                self.personality.emoji = self.personality.EMOTIONS.get(self.personality.state, "🧠")
                self.drift_count = state.get("drift_count", 0)
                self.drift.last_drift = datetime.fromisoformat(state.get("last_drift", datetime.now().isoformat()))
                self.leash.apply_dict(state.get("leash", {}))
        self.joy.load()


# --- DAEMON LOOP ---
def run_daemon(cycle_seconds: int = 60):
    """Run NOVA living daemon"""
    nova = NovaLiving()
    print(f"🧠 {nova.name} living system started")
    print(f"   Mood: {nova.personality.emoji} {nova.personality.state}")
    
    while True:
        thought = nova.autonomous_cycle(
            idle_hours_increment=(cycle_seconds / 3600.0)
        )
        if thought:
            print(f"   {thought}")
            nova.journal.add_entry(1, nova.personality.state, [])
            
        # Save dashboard
        dash = nova.get_dashboard()
        with open(os.path.join(BASE_DIR, "nova_dashboard.json"), "w") as f:
            json.dump(dash, f, indent=2)
            
        time.sleep(cycle_seconds)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        run_daemon()
    else:
        # Interactive test
        nova = NovaLiving()
        print(f"🧠 {nova.name} initialized")
        print(f"   Dashboard: {nova.get_dashboard()}")
