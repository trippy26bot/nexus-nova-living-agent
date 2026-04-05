import sqlite3, json, time, random

class DistortionInstabilityKernel:
    def __init__(self, db_path):
        self.db_path = db_path
        self.instability = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS distortion_instability (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.instability = max(0.0, min(1.0, self.instability + random.uniform(-0.03, 0.03)))
        self._save(); pirp_context["distortion_instability"] = self.instability; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO distortion_instability (val,ts) VALUES (?,?)", (self.instability, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"instability": self.instability}
