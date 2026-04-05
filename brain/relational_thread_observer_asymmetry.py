# brain/relational_thread_observer_asymmetry.py
import sqlite3, json, time, random

class RelationalThreadObserverAsymmetry:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"thread_asymmetry": 0.5, "observer_tension": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS relational_thread_observer_asymmetry (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["thread_asymmetry"] = min(1.0, max(0.0, abs(bond - 0.5) * 2 + self.state["thread_asymmetry"] * 0.5))
        self.state["observer_tension"] = self.state["observer_tension"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["relational_thread_observer_asymmetry"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO relational_thread_observer_asymmetry (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
