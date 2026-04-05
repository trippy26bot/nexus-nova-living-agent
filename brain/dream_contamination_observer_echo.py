# brain/dream_contamination_observer_echo.py
import sqlite3, json, time, random

class DreamContaminationObserverEcho:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"dream_contamination": 0.5, "observer_echo_resonance": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS dream_contamination_observer_echo (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["dream_contamination"] = min(1.0, max(0.0, self.state["dream_contamination"] * 0.87 + anomaly * 0.13))
        self.state["observer_echo_resonance"] = self.state["observer_echo_resonance"] * 0.86 + (random.random() - 0.5) * 0.14
        self._save()
        pirp_context["dream_contamination_observer_echo"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO dream_contamination_observer_echo (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
