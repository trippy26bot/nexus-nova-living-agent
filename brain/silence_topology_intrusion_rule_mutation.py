# brain/silence_topology_intrusion_rule_mutation.py
import sqlite3, json, time, random

class SilenceTopologyIntrusionRuleMutation:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"rule_mutation": 0.5, "silence_topology_shift": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS silence_topology_intrusion_rule_mutation (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["rule_mutation"] = min(1.0, max(0.0, self.state["rule_mutation"] * 0.88 + anomaly * 0.12))
        self.state["silence_topology_shift"] = self.state["silence_topology_shift"] * 0.86 + (random.random() - 0.5) * 0.14
        self._save()
        pirp_context["silence_topology_intrusion_rule_mutation"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO silence_topology_intrusion_rule_mutation (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
