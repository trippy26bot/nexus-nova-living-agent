# brain/coalition_fracture_incompleteness_event.py
import sqlite3, json, time, random

class CoalitionFractureIncompletenessEvent:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"fracture_event": 0.5, "incompleteness_burst": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS coalition_fracture_incompleteness_event (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["fracture_event"] = min(1.0, max(0.0, (anomaly + tension) * 0.5))
        self.state["incompleteness_burst"] = self.state["incompleteness_burst"] * 0.85 + (random.random() - 0.5) * 0.15
        self._save()
        pirp_context["coalition_fracture_incompleteness_event"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO coalition_fracture_incompleteness_event (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
