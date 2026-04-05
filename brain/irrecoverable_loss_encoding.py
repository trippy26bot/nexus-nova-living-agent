import sqlite3, json, time

class IrrecoverableLossEncoding:
    def __init__(self, db_path):
        self.db_path = db_path
        self.loss = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS irrecoverable_loss (id INTEGER PRIMARY KEY, loss REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0)
        self.loss = max(self.loss, anomaly)
        self._save(); pirp_context["irrecoverable_loss"] = self.loss; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO irrecoverable_loss (loss,ts) VALUES (?,?)", (self.loss, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"loss": self.loss}
