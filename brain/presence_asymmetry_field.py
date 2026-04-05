import sqlite3, json, time

class PresenceAsymmetryField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"asymmetry": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS presence_asymmetry (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        p = pirp_context.get("architect_present", True)
        a = pirp_context.get("architect_active", True)
        self.state["asymmetry"] = float(p and not a)
        self._save(); pirp_context["presence_asymmetry"] = self.state["asymmetry"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO presence_asymmetry (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
