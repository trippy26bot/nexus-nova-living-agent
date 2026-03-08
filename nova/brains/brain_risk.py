"""Brain 8: Risk - Evaluates danger"""
def process(input_data, shared_state=None):
    strategy = shared_state.get("strategy", {}) if shared_state else {}
    emotions = shared_state.get("emotions", {"caution": 0.5}) if shared_state else {"caution": 0.5}
    action = strategy.get("strategy_action", "observe")
    if action == "buy" and emotions.get("caution", 0.5) > 0.7:
        safe_action = "observe"
    else:
        safe_action = action
    result = {"safe_action": safe_action}
    if shared_state is not None:
        shared_state["risk"] = result
    return result

def performance_metric():
    return 1.0
