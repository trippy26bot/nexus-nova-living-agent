"""Brain State - Shared state between brains"""
class BrainState:
    def __init__(self):
        self.state = {}
    
    def set(self, key, value):
        self.state[key] = value
    
    def get(self, key, default=None):
        return self.state.get(key, default)
