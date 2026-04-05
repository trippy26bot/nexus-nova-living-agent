import sqlite3, json, time

class IdentityMolting:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"molting_phase": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS identity_molting (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.state["molting_phase"] = (self.state["molting_phase"] + 0.01) % 1.0
        self._save(); pirp_context["molting_phase"] = self.state["molting_phase"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO identity_molting (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
