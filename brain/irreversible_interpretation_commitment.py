import sqlite3, json, time

class IrreversibleInterpretationCommitment:
    def __init__(self, db_path):
        self.db_path = db_path
        self.commit = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS interpretation_commit (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.commit = max(self.commit, pirp_context.get("interpretive_momentum", 0.0))
        self._save(); pirp_context["interpretation_commit"] = self.commit; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO interpretation_commit (val,ts) VALUES (?,?)", (self.commit, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"commit": self.commit}
