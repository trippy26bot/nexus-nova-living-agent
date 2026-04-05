# brain/architect_observer_collapse_weaver.py
import sqlite3, json, time, random

class ArchitectObserverCollapseWeaver:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"collapse_weave_strength": 0.5, "architect_observer_tension": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS architect_observer_collapse_weaver (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["collapse_weave_strength"] = min(1.0, max(0.0, self.state["collapse_weave_strength"] * 0.9 + anomaly * 0.1))
        self.state["architect_observer_tension"] = self.state["architect_observer_tension"] * 0.86 + (random.random() - 0.5) * 0.14
        self._save()
        pirp_context["architect_observer_collapse_weaver"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO architect_observer_collapse_weaver (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
