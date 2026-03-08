"""Brain 2: Reasoning - Analyzes patterns"""
def process(input_data, shared_state=None):
    perception = shared_state.get("perception", {}) if shared_state else {}
    trends = perception.get("observed_trends")
    reasoning_output = {"action_suggestion": "analyze"}
    if trends == "uptrend":
        reasoning_output["action_suggestion"] = "buy"
    elif trends == "downtrend":
        reasoning_output["action_suggestion"] = "sell"
    if shared_state is not None:
        shared_state["reasoning"] = reasoning_output
    return reasoning_output

def performance_metric():
    return 1.0
