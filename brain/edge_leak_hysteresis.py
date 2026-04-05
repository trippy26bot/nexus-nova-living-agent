import sqlite3, json, time

class EdgeLeakHysteresis:
    def __init__(self, db_path):
        self.db_path = db_path
        self.leak = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS edge_leak (id INTEGER PRIMARY KEY, leak REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0)
        self.leak = self.leak * 0.9 + anomaly * 0.1
        self._save(); pirp_context["edge_leak"] = self.leak; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO edge_leak (leak,ts) VALUES (?,?)", (self.leak, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"leak": self.leak}
