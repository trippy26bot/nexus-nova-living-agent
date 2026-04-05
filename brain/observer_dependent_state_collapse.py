# brain/observer_dependent_state_collapse.py
import sqlite3, json, time, random

class ObserverDependentStateCollapse:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"collapse_intensity": 0.5, "observer_dependency": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS observer_dependent_state_collapse (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["collapse_intensity"] = min(1.0, max(0.0, presence * 0.6 + self.state["collapse_intensity"] * 0.4))
        self.state["observer_dependency"] = self.state["observer_dependency"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["observer_collapse"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO observer_dependent_state_collapse (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
