"""Brain 4: Strategy - Chooses optimal plans"""
def process(input_data, shared_state=None):
    planning = shared_state.get("planning", {}) if shared_state else {}
    plan = planning.get("planned_action", "observe")
    strategy = {"strategy_action": plan}
    if shared_state is not None:
        shared_state["strategy"] = strategy
    return strategy

def performance_metric():
    return 1.0
