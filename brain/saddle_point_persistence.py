import sqlite3, json, time

class SaddlePointPersistence:
    def __init__(self, db_path):
        self.db_path = db_path
        self.persistence = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS saddle_persistence (id INTEGER PRIMARY KEY, persistence REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.persistence = self.persistence * 0.97 + 0.03
        self._save(); pirp_context["saddle_persistence"] = self.persistence; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO saddle_persistence (persistence,ts) VALUES (?,?)", (self.persistence, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"persistence": self.persistence}
