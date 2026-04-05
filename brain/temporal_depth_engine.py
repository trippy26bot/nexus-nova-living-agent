import sqlite3, json, time

class TemporalDepthEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.depth = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS temporal_depth (id INTEGER PRIMARY KEY, depth REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.depth = self.depth * 0.95 + pirp_context.get("temporal_gap", 0.0) * 0.05
        self._save(); pirp_context["temporal_depth"] = self.depth; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO temporal_depth (depth,ts) VALUES (?,?)", (self.depth, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"depth": self.depth}
