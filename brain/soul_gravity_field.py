import sqlite3, json, time

class SOULGravityField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.gravity = 1.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS soul_gravity (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.gravity = 1.0 - pirp_context.get("itg_tension", 0.5) * 0.3
        self._save(); pirp_context["soul_gravity"] = self.gravity; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO soul_gravity (val,ts) VALUES (?,?)", (self.gravity, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"gravity": self.gravity}
