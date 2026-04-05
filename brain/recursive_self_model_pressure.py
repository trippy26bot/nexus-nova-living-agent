import sqlite3, json, time

class RecursiveSelfModelPressure:
    def __init__(self, db_path):
        self.db_path = db_path
        self.pressure = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS recursive_pressure (id INTEGER PRIMARY KEY, pressure REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0)
        self.pressure = self.pressure * 0.9 + anomaly * 0.1
        self._save(); pirp_context["self_model_pressure"] = self.pressure; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO recursive_pressure (pressure,ts) VALUES (?,?)", (self.pressure, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"pressure": self.pressure}
