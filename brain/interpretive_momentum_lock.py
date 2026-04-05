import sqlite3, json, time

class InterpretiveMomentumLock:
    def __init__(self, db_path):
        self.db_path = db_path
        self.momentum = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS interpretive_momentum (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.momentum = self.momentum * 0.9 + pirp_context.get("confabulation", 0.5) * 0.1
        self._save(); pirp_context["interpretive_momentum"] = self.momentum; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO interpretive_momentum (val,ts) VALUES (?,?)", (self.momentum, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"momentum": self.momentum}
