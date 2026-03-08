"""
NOVA Synthetic Emotion Engine
Internal decision signals that influence learning, risk, and curiosity
"""


class EmotionEngine:
    """
    Synthetic emotions - internal states that influence decision making.
    Not human emotions, but decision signals that improve adaptive behavior.
    """
    
    def __init__(self):
        self.state = {
            "curiosity": 0.5,    # Drives exploration
            "confidence": 0.5,    # Increases action
            "caution": 0.5,     # Reduces risk
            "urgency": 0.5,     # Speeds decisions
            "satisfaction": 0.5 # Reinforces success
        }
        self.history = []
    
    def update(self, result):
        """
        Update emotional state based on outcome.
        """
        # Success increases confidence and satisfaction
        if result == "success":
            self.state["confidence"] = min(1.0, self.state["confidence"] + 0.1)
            self.state["satisfaction"] = min(1.0, self.state["satisfaction"] + 0.15)
            self.state["caution"] = max(0.1, self.state["caution"] - 0.05)
        
        # Failure increases caution, decreases confidence
        elif result == "failure":
            self.state["caution"] = min(1.0, self.state["caution"] + 0.15)
            self.state["confidence"] = max(0.1, self.state["confidence"] - 0.1)
            self.state["satisfaction"] = max(0.1, self.state["satisfaction"] - 0.1)
        
        # Time naturally increases curiosity
        self.state["curiosity"] = min(1.0, self.state["curiosity"] + 0.01)
        
        # Normalize all states
        self.normalize()
        
        # Store in history
        self.history.append({
            "result": result,
            "state": self.state.copy(),
            "emotions": self.get()
        })
        
        # Keep history bounded
        if len(self.history) > 100:
            self.history = self.history[-50:]
    
    def normalize(self):
        """Keep all emotions in valid range"""
        for key in self.state:
            self.state[key] = max(0.0, min(1.0, self.state[key]))
    
    def get(self):
        """Get current emotional state"""
        return self.state.copy()
    
    def get_primary(self):
        """Get the dominant emotion"""
        return max(self.state.items(), key=lambda x: x[1])
    
    def influence_decision(self, decision_options):
        """
        Use emotions to influence decision selection.
        Returns: modified decision scores
        """
        modified = {}
        
        for option, score in decision_options.items():
            mod_score = score
            
            # High caution reduces risky decisions
            if self.state["caution"] > 0.7:
                if option in ["buy", "sell"]:
                    mod_score *= (1.0 - self.state["caution"] * 0.5)
            
            # High confidence increases action
            if self.state["confidence"] > 0.6:
                if option in ["buy", "sell"]:
                    mod_score *= (1.0 + self.state["confidence"] * 0.3)
            
            # High curiosity increases exploration
            if self.state["curiosity"] > 0.6:
                if option == "analyze":
                    mod_score *= (1.0 + self.state["curiosity"] * 0.3)
            
            modified[option] = mod_score
        
        return modified
    
    def get_urgency_delay(self):
        """
        Urgency influences thinking speed.
        Higher urgency = faster decisions (less thinking time)
        """
        # Map urgency (0-1) to delay (1-0.1 seconds)
        return 1.0 - (self.state["urgency"] * 0.9)
    
    def should_explore(self):
        """
        Should NOVA explore something new?
        """
        return self.state["curiosity"] > 0.6
    
    def should_act(self):
        """
        Should NOVA take action or observe?
        """
        return self.state["confidence"] > 0.5 and self.state["caution"] < 0.7
    
    def get_report(self):
        """Get emotional state report"""
        primary, value = self.get_primary()
        
        return {
            "current": self.get(),
            "dominant": primary,
            "urgency_delay": self.get_urgency_delay(),
            "should_explore": self.should_explore(),
            "should_act": self.should_act(),
            "history_length": len(self.history)
        }


class EmotionalMemory:
    """
    Stores emotional experiences for learning.
    """
    
    def __init__(self):
        self.memories = []
    
    def store(self, context, emotion_state, outcome):
        """Store an emotional experience"""
        self.memories.append({
            "context": context,
            "emotions": emotion_state,
            "outcome": outcome,
            "timestamp": len(self.memories)
        })
        
        if len(self.memories) > 1000:
            self.memories = self.memories[-500:]
    
    def get_similar_emotions(self, current_emotions, limit=10):
        """Find past experiences with similar emotional states"""
        similar = []
        
        for memory in self.memories:
            # Calculate emotional similarity
            diff = sum(
                abs(memory["emotions"].get(k, 0) - current_emotions.get(k, 0))
                for k in set(list(memory["emotions"].keys()) + list(current_emotions.keys()))
            )
            similar.append((diff, memory))
        
        similar.sort(key=lambda x: x[0])
        return [m[1] for m in similar[:limit]]
