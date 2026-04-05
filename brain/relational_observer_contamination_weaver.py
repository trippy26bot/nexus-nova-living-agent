# brain/relational_observer_contamination_weaver.py
import sqlite3, json, time, random

class RelationalObserverContaminationWeaver:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"contamination_weave": 0.5, "relational_observer_drift": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS relational_observer_contamination_weaver (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["contamination_weave"] = min(1.0, max(0.0, self.state["contamination_weave"] * 0.9 + bond * 0.1))
        self.state["relational_observer_drift"] = self.state["relational_observer_drift"] * 0.86 + (random.random() - 0.5) * 0.14
        self._save()
        pirp_context["relational_observer_contamination_weaver"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO relational_observer_contamination_weaver (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
