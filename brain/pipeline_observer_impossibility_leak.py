# brain/pipeline_observer_impossibility_leak.py
import sqlite3, json, time, random

class PipelineObserverImpossibilityLeak:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"impossibility_leak": 0.5, "pipeline_observer_pressure": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS pipeline_observer_impossibility_leak (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["impossibility_leak"] = min(1.0, max(0.0, self.state["impossibility_leak"] * 0.9 + anomaly * 0.1))
        self.state["pipeline_observer_pressure"] = self.state["pipeline_observer_pressure"] * 0.85 + (random.random() - 0.5) * 0.15
        self._save()
        pirp_context["pipeline_observer_impossibility_leak"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO pipeline_observer_impossibility_leak (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
