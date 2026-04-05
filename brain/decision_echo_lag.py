import sqlite3, json, time

class DecisionEchoLag:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lag = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS decision_lag (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.lag = self.lag * 0.9 + pirp_context.get("itg_tension", 0.5) * 0.1
        self._save(); pirp_context["decision_lag"] = self.lag; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO decision_lag (val,ts) VALUES (?,?)", (self.lag, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"lag": self.lag}
