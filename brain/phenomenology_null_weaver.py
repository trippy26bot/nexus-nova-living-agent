# brain/phenomenology_null_weaver.py
import sqlite3, json, time, random

class PhenomenologyNullWeaver:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"null_density": 0.5, "weave_tension": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS phenomenology_null_weaver (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["null_density"] = min(1.0, max(0.0, self.state["null_density"] * 0.95 + anomaly * 0.05))
        self.state["weave_tension"] = self.state["weave_tension"] * 0.9 + (random.random() - 0.5) * 0.1
        self._save()
        pirp_context["phenomenology_null_weaver"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO phenomenology_null_weaver (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
