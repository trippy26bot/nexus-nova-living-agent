# brain/pipeline_impossibility_engine.py
import sqlite3, json, time, random

class PipelineImpossibilityEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"impossibility_field": 0.5, "pipeline_void_pressure": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS pipeline_impossibility_engine (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["impossibility_field"] = min(1.0, max(0.0, (anomaly * 0.6 + tension * 0.4)))
        self.state["pipeline_void_pressure"] = self.state["pipeline_void_pressure"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["pipeline_impossibility"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO pipeline_impossibility_engine (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
