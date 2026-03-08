"""Brain 12: Creativity - Generates novel ideas"""
def process(input_data, shared_state=None):
    alternatives = ["analyze", "explore", "experiment"]
    if shared_state is not None:
        shared_state["creativity"] = {"alternatives": alternatives}
    return {"alternatives": alternatives}

def performance_metric():
    return 1.0
