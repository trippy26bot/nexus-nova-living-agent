# brain/identity_null_pulsar.py
import sqlite3, json, time, random

class IdentityNullPulsar:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"pulsar_intensity": 0.5, "null_phase": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS identity_null_pulsar (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["pulsar_intensity"] = min(1.0, max(0.0, self.state["pulsar_intensity"] * 0.92 + tension * 0.08))
        self.state["null_phase"] = (self.state["null_phase"] + 0.05) % 1.0
        self._save()
        pirp_context["identity_null_pulsar"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO identity_null_pulsar (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
