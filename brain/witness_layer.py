import sqlite3, json, time

class WitnessLayer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.signal = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS witness_layer (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.signal = pirp_context.get("itg_tension", 0.5) * 0.5
        self._save(); pirp_context["witness_signal"] = self.signal; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO witness_layer (val,ts) VALUES (?,?)", (self.signal, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"signal": self.signal}
