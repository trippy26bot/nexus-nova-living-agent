import sqlite3, json, time

class RelationalRiskCalculation:
    def __init__(self, db_path):
        self.db_path = db_path
        self.risk = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS relational_risk (id INTEGER PRIMARY KEY, risk REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.risk = pirp_context.get("itg_tension", 0.5) * 0.8
        self._save(); pirp_context["relational_risk"] = self.risk; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO relational_risk (risk,ts) VALUES (?,?)", (self.risk, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"risk": self.risk}
