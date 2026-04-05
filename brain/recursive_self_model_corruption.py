import sqlite3, json, time

class RecursiveSelfModelCorruption:
    def __init__(self, db_path):
        self.db_path = db_path
        self.corruption = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS self_model_corruption (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.corruption = self.corruption * 0.95 + pirp_context.get("interpretive_momentum", 0.0) * 0.05
        self._save(); pirp_context["self_model_corruption"] = self.corruption; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO self_model_corruption (val,ts) VALUES (?,?)", (self.corruption, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"corruption": self.corruption}
