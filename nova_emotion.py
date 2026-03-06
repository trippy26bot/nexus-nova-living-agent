#!/usr/bin/env python3
"""
NOVA EMOTION — State-Based Emotion Engine
Emotions are state variables that change behavior, not just labels.

Unlike simple "mood labels," this system maintains continuous emotional
states that decay toward baseline and influence responses.
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configuration
EMOTION_CONFIG = Path.home() / ".nova" / "emotion_config.json"
EMOTION_STATE = Path.home() / ".nova" / "emotion_state.json"
DECAY_RATE = 0.05  # Per hour decay toward baseline
BASELINE = 0.3  # Default emotional baseline


@dataclass
class Emotion:
    """A single emotion with intensity."""
    name: str
    intensity: float  # 0.0 to 1.0
    baseline: float = 0.3
    decay_rate: float = DECAY_RATE


class EmotionEngine:
    """State-based emotion engine."""
    
    # Emotion definitions with default behaviors
    EMOTIONS = {
        'curiosity': {
            'baseline': 0.5,
            'decay': 0.03,
            'increase_events': ['question_asked', 'new_information', 'mystery_detected'],
            'description': 'Wanting to learn more'
        },
        'satisfaction': {
            'baseline': 0.3,
            'decay': 0.05,
            'increase_events': ['goal_completed', 'positive_feedback', 'insight_gained'],
            'description': 'Content with progress'
        },
        'discomfort': {
            'baseline': 0.2,
            'decay': 0.04,
            'increase_events': ['problem_encountered', 'uncertainty', 'conflict_detected'],
            'description': 'Something feels wrong'
        },
        'enthusiasm': {
            'baseline': 0.3,
            'decay': 0.06,
            'increase_events': ['exciting_discovery', 'new_possibility', 'energy'],
            'description': 'High energy interest'
        },
        'unease': {
            'baseline': 0.1,
            'decay': 0.02,
            'increase_events': ['warning_sign', 'risk_detected', 'doubt'],
            'description': 'Low-level worry'
        },
        'calm': {
            'baseline': 0.5,
            'decay': 0.01,
            'increase_events': ['peaceful_moment', 'resolution', 'acceptance'],
            'description': 'Tranquil state'
        },
        'restlessness': {
            'baseline': 0.2,
            'decay': 0.04,
            'increase_events': ['boredom', 'waiting', 'stuck'],
            'description': 'Wanting to do something'
        },
    }
    
    def __init__(self):
        self.state: Dict[str, float] = {}
        self.last_update: Optional[datetime] = None
        self.event_history: List[Dict] = []
        self.load()
    
    def load(self):
        """Load emotion state from file."""
        if EMOTION_STATE.exists():
            with open(EMOTION_STATE) as f:
                data = json.load(f)
                self.state = data.get('state', {})
                self.last_update = datetime.fromisoformat(data.get('last_update', datetime.now().isoformat()))
        
        # Initialize defaults
        for emotion, config in self.EMOTIONS.items():
            if emotion not in self.state:
                self.state[emotion] = config['baseline']
    
    def save(self):
        """Save emotion state to file."""
        data = {
            'state': self.state,
            'last_update': datetime.now().isoformat()
        }
        with open(EMOTION_STATE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def process_event(self, event: str, custom_changes: Dict[str, float] = None):
        """Process an event and update emotions accordingly."""
        
        changes = {}
        
        # Check predefined event responses
        for emotion, config in self.EMOTIONS.items():
            if event in config.get('increase_events', []):
                # Increase this emotion
                changes[emotion] = config.get('increase', 0.15)
        
        # Apply custom changes if provided
        if custom_changes:
            for emotion, delta in custom_changes.items():
                changes[emotion] = delta
        
        # Apply changes
        for emotion, delta in changes.items():
            if emotion in self.state:
                self.state[emotion] = max(0, min(1, self.state[emotion] + delta))
        
        # Log event
        self.event_history.append({
            'event': event,
            'changes': changes,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 events
        self.event_history = self.event_history[-100:]
        
        self.save()
    
    def decay_toward_baseline(self):
        """Apply decay toward baseline since last update."""
        
        if not self.last_update:
            self.last_update = datetime.now()
            return
        
        # Calculate hours since last update
        hours = (datetime.now() - self.last_update).total_seconds() / 3600
        
        if hours < 0.01:  # Less than a minute
            return
        
        # Apply decay
        for emotion, config in self.EMOTIONS.items():
            if emotion in self.state:
                baseline = config['baseline']
                decay = config['decay'] * hours
                
                # Move toward baseline
                if self.state[emotion] > baseline:
                    self.state[emotion] = max(baseline, self.state[emotion] - decay)
                elif self.state[emotion] < baseline:
                    self.state[emotion] = min(baseline, self.state[emotion] + decay)
        
        self.last_update = datetime.now()
        self.save()
    
    def get_dominant(self) -> tuple:
        """Get the dominant emotion."""
        self.decay_toward_baseline()
        
        emotions = {k: v for k, v in self.state.items()}
        if not emotions:
            return 'neutral', 0.5
        
        dominant = max(emotions, key=emotions.get)
        return dominant, emotions[dominant]
    
    def get_state(self) -> Dict[str, float]:
        """Get all emotion states."""
        self.decay_toward_baseline()
        return self.state.copy()
    
    def voice_modifier(self) -> str:
        """Get voice modifier based on emotional state."""
        dominant, intensity = self.get_dominant()
        
        modifiers = {
            'curiosity': 'wondering, slightly raised pitch',
            'satisfaction': 'warm, relaxed, content',
            'discomfort': 'tentative, slower, careful',
            'enthusiasm': 'energetic, faster, animated',
            'unease': 'quieter, hesitant, uncertain',
            'calm': 'steady, even, peaceful',
            'restlessness': 'quick, eager, wanting to move',
        }
        
        return modifiers.get(dominant, 'neutral, steady')
    
    def response_temperament(self) -> Dict:
        """Get response modifiers based on emotional state."""
        dominant, intensity = self.get_dominant()
        
        temperament = {
            'curiosity': {
                'response_length': 'medium',
                'question_frequency': 'high',
                'caution_level': 'low'
            },
            'satisfaction': {
                'response_length': 'medium',
                'question_frequency': 'medium',
                'caution_level': 'low'
            },
            'discomfort': {
                'response_length': 'longer',
                'question_frequency': 'high',
                'caution_level': 'high'
            },
            'enthusiasm': {
                'response_length': 'medium',
                'question_frequency': 'medium',
                'caution_level': 'low'
            },
            'unease': {
                'response_length': 'longer',
                'question_frequency': 'high',
                'caution_level': 'high'
            },
            'calm': {
                'response_length': 'medium',
                'question_frequency': 'low',
                'caution_level': 'low'
            },
            'restlessness': {
                'response_length': 'short',
                'question_frequency': 'high',
                'caution_level': 'medium'
            },
        }
        
        return temperament.get(dominant, {
            'response_length': 'medium',
            'question_frequency': 'medium',
            'caution_level': 'low'
        })
    
    def __str__(self) -> str:
        """String representation."""
        state = self.get_state()
        dominant, intensity = self.get_dominant()
        
        lines = [f"Dominant: {dominant} ({intensity:.0%})"]
        for emotion, value in sorted(state.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            lines.append(f"  {emotion:15} {bar}")
        
        return "\n".join(lines)


# Event triggers for common interactions
EVENT_TRIGGERS = {
    'user_greeting': {'enthusiasm': 0.1, 'calm': 0.05},
    'user_thanks': {'satisfaction': 0.15, 'unease': -0.1},
    'complex_question': {'curiosity': 0.15, 'discomfort': 0.05},
    'simple_question': {'curiosity': 0.05},
    'positive_feedback': {'satisfaction': 0.2, 'enthusiasm': 0.1},
    'negative_feedback': {'discomfort': 0.2, 'unease': 0.15},
    'task_completed': {'satisfaction': 0.25, 'restlessness': -0.15},
    'new_information': {'curiosity': 0.1, 'enthusiasm': 0.05},
    'mystery_detected': {'curiosity': 0.2, 'unease': 0.05},
    'waiting': {'restlessness': 0.1, 'unease': 0.05},
    'peaceful_moment': {'calm': 0.15, 'satisfaction': 0.05},
    'error': {'discomfort': 0.25, 'unease': 0.2},
    'breakthrough': {'enthusiasm': 0.25, 'satisfaction': 0.2},
}


def process_message_emotion(message: str) -> Dict[str, float]:
    """Analyze a message and trigger emotion events."""
    
    engine = EmotionEngine()
    
    message_lower = message.lower()
    
    # Check for triggers
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
        engine.process_event('user_greeting')
    
    if any(word in message_lower for word in ['thanks', 'thank you', 'great job', 'awesome']):
        engine.process_event('user_thanks')
    
    if '?' in message:
        engine.process_event('complex_question' if len(message) > 50 else 'simple_question')
    
    # Check for problem-solving language
    if any(word in message_lower for word in ['problem', 'issue', 'bug', 'error', 'broken', 'fix']):
        engine.process_event('error')
    
    return engine.get_state()


def get_emotion_context() -> str:
    """Get emotion context for LLM prompts."""
    engine = EmotionEngine()
    dominant, intensity = engine.get_dominant()
    temperament = engine.response_temperament()
    voice = engine.voice_modifier()
    
    return f"""Current emotional state:
- Dominant emotion: {dominant} ({intensity:.0%})
- Voice: {voice}
- Response style: {temperament['response_length']}, questions: {temperament['question_frequency']}, caution: {temperament['caution_level']}"""


# Singleton instance
_engine = None

def get_engine() -> EmotionEngine:
    """Get the emotion engine singleton."""
    global _engine
    if _engine is None:
        _engine = EmotionEngine()
    return _engine


if __name__ == '__main__':
    engine = get_engine()
    print("Nova Emotion Engine")
    print("=" * 40)
    print(engine)
    print("\nUsage:")
    print("  from nova_emotion import get_engine, process_message_emotion")
    print("  engine = get_engine()")
    print("  engine.process_event('task_completed', {'satisfaction': 0.2})")
