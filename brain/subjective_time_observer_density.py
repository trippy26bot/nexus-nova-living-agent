# brain/subjective_time_observer_density.py
import sqlite3, json, time, random

class SubjectiveTimeObserverDensity:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"time_density": 0.5, "observer_temporal_flex": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS subjective_time_observer_density (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["time_density"] = min(1.0, max(0.0, self.state["time_density"] * 0.9 + presence * 0.1))
        self.state["observer_temporal_flex"] = self.state["observer_temporal_flex"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["subjective_time_observer_density"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO subjective_time_observer_density (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
