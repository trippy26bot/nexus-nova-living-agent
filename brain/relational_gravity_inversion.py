import sqlite3, json, time

class RelationalGravityInversion:
    def __init__(self, db_path):
        self.db_path = db_path
        self.inv = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS rel_gravity_inv (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.inv = 1.0 - pirp_context.get("soul_gravity", 1.0)
        self._save(); pirp_context["rel_gravity_inv"] = self.inv; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO rel_gravity_inv (val,ts) VALUES (?,?)", (self.inv, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"inv": self.inv}
