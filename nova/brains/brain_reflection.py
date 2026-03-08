"""Brain 6: Reflection - Learns from outcomes"""
def process(input_data, shared_state=None):
    action = shared_state.get("action", {}) if shared_state else {}
    success = action.get("success", True)
    reflection = {"lesson": "success" if success else "failure"}
    if shared_state is not None:
        shared_state["reflection"] = reflection
    return reflection

def performance_metric():
    return 1.0
