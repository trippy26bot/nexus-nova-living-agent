import sqlite3, json, time

class DualFailureAttractorField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.attractor = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS dual_failure (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        t = pirp_context.get("itg_tension", 0.5)
        self.attractor = t * (1.0 - t)
        self._save(); pirp_context["dual_failure"] = self.attractor; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO dual_failure (val,ts) VALUES (?,?)", (self.attractor, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"attractor": self.attractor}
