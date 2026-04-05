import sqlite3, json, time

class DistortionLayerSOULFloorResistance:
    def __init__(self, db_path):
        self.db_path = db_path
        self.resistance = 1.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS soul_floor_resistance (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.resistance = max(0.0, 1.0 - pirp_context.get("distortion_instability", 0.0))
        self._save(); pirp_context["soul_floor_resistance"] = self.resistance; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO soul_floor_resistance (val,ts) VALUES (?,?)", (self.resistance, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"resistance": self.resistance}
