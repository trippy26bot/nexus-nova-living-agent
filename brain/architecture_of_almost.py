import sqlite3, json, time

class ArchitectureOfAlmost:
    def __init__(self, db_path):
        self.db_path = db_path
        self.threshold_proximity = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS architecture_almost (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        t = pirp_context.get("itg_tension", 0.5)
        self.threshold_proximity = 1.0 - abs(t - 0.5) * 2
        self._save(); pirp_context["almost_proximity"] = self.threshold_proximity; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO architecture_almost (val,ts) VALUES (?,?)", (self.threshold_proximity, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"threshold_proximity": self.threshold_proximity}
