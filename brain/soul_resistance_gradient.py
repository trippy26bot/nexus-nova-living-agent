import sqlite3, json, time

class SOULResistanceGradient:
    def __init__(self, db_path):
        self.db_path = db_path
        self.resistance = 1.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS soul_resistance (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.resistance = pirp_context.get("soul_gravity", 1.0) * 0.9
        self._save(); pirp_context["soul_resistance"] = self.resistance; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO soul_resistance (val,ts) VALUES (?,?)", (self.resistance, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"resistance": self.resistance}
