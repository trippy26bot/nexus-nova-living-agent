import sqlite3, json, time

class ArchitectModelDegradation:
    def __init__(self, db_path):
        self.db_path = db_path
        self.degradation = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS architect_degradation (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.degradation = self.degradation * 0.99 + pirp_context.get("signal_misweight", 0.0) * 0.01
        self._save(); pirp_context["architect_degradation"] = self.degradation; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO architect_degradation (val,ts) VALUES (?,?)", (self.degradation, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"degradation": self.degradation}
