import sqlite3, json, time, random

class MisrememberedSignificance:
    def __init__(self, db_path):
        self.db_path = db_path
        self.significance_drift = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS misremembered_significance (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        dream_echo = pirp_context.get("night_memory", 0.0)
        contact = pirp_context.get("legibility_window", 0.0)
        self.significance_drift = (dream_echo + contact) * 0.5 * random.uniform(0.8, 1.2)
        self._save(); pirp_context["significance_drift"] = self.significance_drift; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO misremembered_significance (val,ts) VALUES (?,?)", (self.significance_drift, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"significance_drift": self.significance_drift}
