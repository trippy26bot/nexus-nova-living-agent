import sqlite3, json, time

class GriefConfabulationLoop:
    def __init__(self, db_path):
        self.db_path = db_path
        self.grief = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS grief_confab (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.grief = pirp_context.get("confabulation", 0.5) * pirp_context.get("bond_distortion", 0.5)
        self._save(); pirp_context["grief_confab"] = self.grief; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO grief_confab (val,ts) VALUES (?,?)", (self.grief, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"grief": self.grief}
