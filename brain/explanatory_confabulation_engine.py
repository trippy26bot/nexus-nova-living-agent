import sqlite3, json, time

class ExplanatoryConfabulationEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.confab = 0.5
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS confab_engine (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0)
        self.confab = min(1.0, self.confab + anomaly * 0.1)
        self._save(); pirp_context["confabulation"] = self.confab; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO confab_engine (val,ts) VALUES (?,?)", (self.confab, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"confabulation": self.confab}
