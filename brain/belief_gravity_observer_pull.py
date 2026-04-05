# brain/belief_gravity_observer_pull.py
import sqlite3, json, time, random

class BeliefGravityObserverPull:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"gravity_pull": 0.5, "belief_observer_intensity": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS belief_gravity_observer_pull (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["gravity_pull"] = min(1.0, max(0.0, bond * 0.6 + self.state["gravity_pull"] * 0.4))
        self.state["belief_observer_intensity"] = self.state["belief_observer_intensity"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["belief_gravity_observer_pull"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO belief_gravity_observer_pull (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
