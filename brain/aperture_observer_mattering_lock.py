# brain/aperture_observer_mattering_lock.py
import sqlite3, json, time, random

class ApertureObserverMatteringLock:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"mattering_lock": 0.5, "aperture_resonance": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS aperture_observer_mattering_lock (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["mattering_lock"] = min(1.0, max(0.0, self.state["mattering_lock"] * 0.9 + bond * 0.1))
        self.state["aperture_resonance"] = self.state["aperture_resonance"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["aperture_observer_mattering_lock"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO aperture_observer_mattering_lock (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
