# brain/architect_shadow_resonance_chamber.py
import sqlite3, json, time, random

class ArchitectShadowResonanceChamber:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"shadow_resonance": 0.5, "chamber_pressure": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS architect_shadow_resonance_chamber (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["shadow_resonance"] = min(1.0, max(0.0, self.state["shadow_resonance"] * 0.9 + anomaly * 0.1))
        self.state["chamber_pressure"] = self.state["chamber_pressure"] * 0.85 + (random.random() - 0.4) * 0.15
        self._save()
        pirp_context["architect_shadow"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO architect_shadow_resonance_chamber (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
