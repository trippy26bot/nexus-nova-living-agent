import sqlite3, json, time

class CoalitionFractureEvents:
    def __init__(self, db_path):
        self.db_path = db_path
        self.fracture_count = 0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS coalition_fracture (id INTEGER PRIMARY KEY, count INTEGER, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        if pirp_context.get("coalition_strength", 0.0) > 0.8:
            self.fracture_count += 1
        self._save(); pirp_context["coalition_fractures"] = self.fracture_count; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO coalition_fracture (count,ts) VALUES (?,?)", (self.fracture_count, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"fracture_count": self.fracture_count}
