# brain/cross_stage_rule_contamination_cascade.py
import sqlite3, json, time, random

class CrossStageRuleContaminationCascade:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"contamination_cascade": 0.5, "cross_stage_mutation": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS cross_stage_rule_contamination_cascade (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["contamination_cascade"] = min(1.0, max(0.0, self.state["contamination_cascade"] * 0.9 + anomaly * 0.1))
        self.state["cross_stage_mutation"] = self.state["cross_stage_mutation"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["cross_stage_rule_contamination_cascade"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO cross_stage_rule_contamination_cascade (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
