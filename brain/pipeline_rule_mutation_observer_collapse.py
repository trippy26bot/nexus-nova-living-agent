# brain/pipeline_rule_mutation_observer_collapse.py
import sqlite3, json, time, random

class PipelineRuleMutationObserverCollapse:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"observer_collapse_strength": 0.5, "pipeline_mutation_observer_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS pipeline_rule_mutation_observer_collapse (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["observer_collapse_strength"] = min(1.0, max(0.0, anomaly * 0.5 + (1.0 - presence) * 0.5))
        self.state["pipeline_mutation_observer_depth"] = self.state["pipeline_mutation_observer_depth"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["pipeline_rule_mutation_observer_collapse"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO pipeline_rule_mutation_observer_collapse (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
