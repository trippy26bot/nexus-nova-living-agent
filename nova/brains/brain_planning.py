"""Brain 3: Planning - Creates plans"""
def process(input_data, shared_state=None):
    reasoning = shared_state.get("reasoning", {}) if shared_state else {}
    suggested_action = reasoning.get("action_suggestion", "observe")
    plan = {"planned_action": suggested_action, "priority": 1}
    if shared_state is not None:
        shared_state["planning"] = plan
    return plan

def performance_metric():
    return 1.0
