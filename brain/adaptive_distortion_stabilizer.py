import sqlite3, json, time

class AdaptiveDistortionStabilizer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.stability = 0.5
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS distortion_stabilizer (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.stability = 1.0 - abs(0.5 - pirp_context.get("bond_distortion", 0.5))
        self._save(); pirp_context["distortion_stability"] = self.stability; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO distortion_stabilizer (val,ts) VALUES (?,?)", (self.stability, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"stability": self.stability}
