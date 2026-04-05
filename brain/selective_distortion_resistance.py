import sqlite3, json, time

class SelectiveDistortionResistance:
    def __init__(self, db_path):
        self.db_path = db_path
        self.resistance = 1.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS selective_resistance (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.resistance = pirp_context.get("soul_distortion_coherence", 1.0) * pirp_context.get("soul_floor_resistance", 1.0)
        self._save(); pirp_context["selective_resistance"] = self.resistance; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO selective_resistance (val,ts) VALUES (?,?)", (self.resistance, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"resistance": self.resistance}
