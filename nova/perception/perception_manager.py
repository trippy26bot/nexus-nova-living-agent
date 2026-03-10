#!/usr/bin/env python3
"""
Nova Perception Layer
Gives Nova eyes and ears on the world
"""

from typing import Dict, List, Any, Optional
import time

class PerceptionListener:
    """Base class for perception listeners"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_data = None
    
    def listen(self) -> Optional[Dict]:
        """Listen for data - override in subclass"""
        return None


class PerceptionManager:
    """Manages all perception listeners"""
    
    def __init__(self):
        self.listeners = []
        self.events = []
    
    def register(self, listener: PerceptionListener):
        """Register a listener"""
        self.listeners.append(listener)
    
    def poll(self) -> List[Dict]:
        """Poll all listeners"""
        events = []
        
        for listener in self.listeners:
            try:
                data = listener.listen()
                if data:
                    events.append(data)
                    self.events.append(data)
            except Exception as e:
                pass
        
        # Keep last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]
        
        return events
    
    def get_events(self, n: int = 10) -> List[Dict]:
        """Get recent events"""
        return self.events[-n:]


class WebListener(PerceptionListener):
    """Listen to websites"""
    
    def __init__(self, url: str, name: str = "web"):
        super().__init__(name)
        self.url = url
    
    def listen(self) -> Optional[Dict]:
        """Fetch website content"""
        try:
            import requests
            r = requests.get(self.url, timeout=5)
            if r.status_code == 200:
                return {
                    "source": "web",
                    "url": self.url,
                    "content": r.text[:500],
                    "time": time.time()
                }
        except:
            pass
        return None


class MarketListener(PerceptionListener):
    """Listen to market data"""
    
    def __init__(self, api_url: str, name: str = "market"):
        super().__init__(name)
        self.api_url = api_url
    
    def listen(self) -> Optional[Dict]:
        """Fetch market data"""
        try:
            import requests
            r = requests.get(self.api_url, timeout=5)
            if r.status_code == 200:
                return {
                    "source": "market",
                    "url": self.api_url,
                    "data": r.json(),
                    "time": time.time()
                }
        except:
            pass
        return None


class EventStream:
    """Event queue for perceptions"""
    
    def __init__(self):
        self.queue = []
    
    def push(self, event: Dict):
        """Add event"""
        self.queue.append(event)
    
    def pop(self) -> Optional[Dict]:
        """Get next event"""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def size(self) -> int:
        return len(self.queue)


# Global instances
_perception_manager = None
_event_stream = None

def get_perception_manager() -> PerceptionManager:
    global _perception_manager
    if _perception_manager is None:
        _perception_manager = PerceptionManager()
    return _perception_manager

def get_event_stream() -> EventStream:
    global _event_stream
    if _event_stream is None:
        _event_stream = EventStream()
    return _event_stream
