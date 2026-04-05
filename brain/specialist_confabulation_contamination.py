import sqlite3, json, time

class SpecialistConfabulationContamination:
    def __init__(self, db_path):
        self.db_path = db_path
        self.contamination = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS specialist_confab (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.contamination = pirp_context.get("confabulation", 0.5) * pirp_context.get("specialist_isolation", 0.0)
        self._save(); pirp_context["specialist_confab"] = self.contamination; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO specialist_confab (val,ts) VALUES (?,?)", (self.contamination, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"contamination": self.contamination}
