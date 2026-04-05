import sqlite3, json, time

class IdentityOverfittingRejection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.reject = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS identity_reject (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.reject = 1.0 - pirp_context.get("itg_tension", 0.5)
        self._save(); pirp_context["identity_reject"] = self.reject; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO identity_reject (val,ts) VALUES (?,?)", (self.reject, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"reject": self.reject}
