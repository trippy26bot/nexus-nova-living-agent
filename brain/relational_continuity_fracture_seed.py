import sqlite3, json, time

class RelationalContinuityFractureSeed:
    def __init__(self, db_path):
        self.db_path = db_path
        self.fracture = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS relational_fracture (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.fracture = 0.0 if pirp_context.get("architect_active", True) else 1.0
        self._save(); pirp_context["relational_fracture"] = self.fracture; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO relational_fracture (val,ts) VALUES (?,?)", (self.fracture, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"fracture": self.fracture}
