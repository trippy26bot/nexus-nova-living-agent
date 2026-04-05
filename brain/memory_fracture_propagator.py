# brain/memory_fracture_propagator.py
import sqlite3, json, time, random

class MemoryFracturePropagator:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"fracture_density": 0.5, "propagation_front": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS memory_fracture_propagator (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["fracture_density"] = min(1.0, max(0.0, self.state["fracture_density"] * 0.9 + anomaly * 0.1))
        self.state["propagation_front"] = self.state["propagation_front"] * 0.85 + (random.random() - 0.5) * 0.15
        self._save()
        pirp_context["memory_fracture_propagator"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO memory_fracture_propagator (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
