"""Brain 14: Emotion Integration"""
def process(input_data, shared_state=None):
    emotions = shared_state.get("emotions", {"confidence":0.5,"caution":0.5}) if shared_state else {"confidence":0.5,"caution":0.5}
    strategy = shared_state.get("strategy", {"strategy_action":"observe"}) if shared_state else {"strategy_action":"observe"}
    if emotions.get("caution", 0.5) > 0.7:
        adjusted = "observe"
    else:
        adjusted = strategy.get("strategy_action", "observe")
    if shared_state is not None:
        shared_state["emotion_integration"] = {"adjusted_action": adjusted}
    return {"adjusted_action": adjusted}

def performance_metric():
    return 1.0
