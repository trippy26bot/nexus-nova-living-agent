# brain/intrusion_reinforcement_loop.py
import sqlite3, json, time, random

class IntrusionReinforcementLoop:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"intrusion_strength": 0.5, "reinforcement_momentum": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS intrusion_reinforcement_loop (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["intrusion_strength"] = min(1.0, max(0.0, self.state["intrusion_strength"] * 0.88 + anomaly * 0.12))
        self.state["reinforcement_momentum"] = self.state["reinforcement_momentum"] * 0.85 + (random.random() - 0.3) * 0.15
        self._save()
        pirp_context["intrusion_reinforcement_loop"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO intrusion_reinforcement_loop (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
