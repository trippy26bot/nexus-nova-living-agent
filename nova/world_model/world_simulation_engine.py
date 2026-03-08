"""World Simulation Engine - Chooses best action"""
class WorldSimulationEngine:
    def __init__(self, world_state, emotions):
        self.world_state = world_state
        self.emotions = emotions
    
    def choose_best_action(self, actions):
        return actions[0] if actions else "observe"
