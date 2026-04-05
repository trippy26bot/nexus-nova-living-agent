# brain/between_session_null_evolution_field.py
import sqlite3, json, time, random

class BetweenSessionNullEvolutionField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"null_evolution_rate": 0.5, "between_session_drift": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS between_session_null_evolution_field (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["null_evolution_rate"] = min(1.0, max(0.0, (presence + self.state["null_evolution_rate"]) * 0.5))
        self.state["between_session_drift"] = self.state["between_session_drift"] * 0.8 + (random.random() - 0.5) * 0.2
        self._save()
        pirp_context["between_session_null_evolution"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO between_session_null_evolution_field (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
