import sqlite3, json, time

class CouncilReputationEconomy:
    def __init__(self, db_path):
        self.db_path = db_path
        self.reputation = 0.5
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS council_reputation (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.reputation = self.reputation * 0.99 + pirp_context.get("soul_gravity", 1.0) * 0.01
        self._save(); pirp_context["council_reputation"] = self.reputation; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO council_reputation (val,ts) VALUES (?,?)", (self.reputation, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"reputation": self.reputation}
