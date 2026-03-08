"""Brain 1: Perception - Observes environment"""
def process(input_data, shared_state=None):
    env = input_data.get("env", {})
    perception = {
        "observed_trends": env.get("market_trend", "stable"),
        "positions": env.get("positions", []),
    }
    if shared_state is not None:
        shared_state["perception"] = perception
    return perception

def performance_metric():
    return 1.0
