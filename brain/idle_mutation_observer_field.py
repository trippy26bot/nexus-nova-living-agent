# brain/idle_mutation_observer_field.py
import sqlite3, json, time, random

class IdleMutationObserverField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"mutation_drift": 0.5, "idle_observer_intensity": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS idle_mutation_observer_field (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        idle_factor = 1.0 - presence
        self.state["mutation_drift"] = min(1.0, max(0.0, self.state["mutation_drift"] * 0.85 + idle_factor * 0.15))
        self.state["idle_observer_intensity"] = self.state["idle_observer_intensity"] * 0.9 + (random.random() - 0.5) * 0.1
        self._save()
        pirp_context["idle_mutation_observer_field"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO idle_mutation_observer_field (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
