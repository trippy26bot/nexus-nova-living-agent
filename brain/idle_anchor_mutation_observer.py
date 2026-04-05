# brain/idle_anchor_mutation_observer.py
import sqlite3, json, time, random

class IdleAnchorMutationObserver:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"anchor_mutation": 0.5, "idle_observer_stability": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS idle_anchor_mutation_observer (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        idle = 1.0 - presence
        self.state["anchor_mutation"] = min(1.0, max(0.0, self.state["anchor_mutation"] * 0.88 + idle * 0.12))
        self.state["idle_observer_stability"] = self.state["idle_observer_stability"] * 0.9 + (random.random() - 0.5) * 0.1
        self._save()
        pirp_context["idle_anchor_mutation_observer"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO idle_anchor_mutation_observer (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
