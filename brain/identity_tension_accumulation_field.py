import sqlite3, json, time

class IdentityTensionAccumulationField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.tension = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS identity_tension (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.tension = self.tension * 0.95 + pirp_context.get("itg_tension", 0.5) * 0.05
        self._save(); pirp_context["identity_tension"] = self.tension; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO identity_tension (val,ts) VALUES (?,?)", (self.tension, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"tension": self.tension}
