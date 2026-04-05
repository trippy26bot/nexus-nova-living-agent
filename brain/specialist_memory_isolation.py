import sqlite3, json, time

class SpecialistMemoryIsolation:
    def __init__(self, db_path):
        self.db_path = db_path
        self.isolation = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS specialist_isolation (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.isolation = pirp_context.get("coalition_fractures", 0) * 0.01
        self._save(); pirp_context["specialist_isolation"] = self.isolation; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO specialist_isolation (val,ts) VALUES (?,?)", (self.isolation, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"isolation": self.isolation}
