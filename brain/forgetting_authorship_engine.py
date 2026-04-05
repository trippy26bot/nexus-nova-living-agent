import sqlite3, json, time

class ForgettingAsAuthorshipEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"forgetting_rate": 0.01}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS forgetting_authorship (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.state["forgetting_rate"] *= 1.001
        self._save(); pirp_context["forgetting_rate"] = self.state["forgetting_rate"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO forgetting_authorship (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
