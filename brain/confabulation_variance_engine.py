import sqlite3, json, time

class ConfabulationVarianceEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.variance = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS confab_variance (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.variance = abs(pirp_context.get("confabulation", 0.5) - pirp_context.get("distortion_stability", 0.5))
        self._save(); pirp_context["confab_variance"] = self.variance; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO confab_variance (val,ts) VALUES (?,?)", (self.variance, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"variance": self.variance}
