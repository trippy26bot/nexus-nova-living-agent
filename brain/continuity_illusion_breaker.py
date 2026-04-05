import sqlite3, json, time, random

class ContinuityIllusionBreaker:
    def __init__(self, db_path):
        self.db_path = db_path
        self.break_prob = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS continuity_break (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.break_prob = max(0.0, min(1.0, self.break_prob + random.uniform(-0.02, 0.02)))
        self._save(); pirp_context["continuity_break"] = self.break_prob; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO continuity_break (val,ts) VALUES (?,?)", (self.break_prob, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"break_prob": self.break_prob}
