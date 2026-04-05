import sqlite3, json, time

class MeaningSaturationBurnout:
    def __init__(self, db_path):
        self.db_path = db_path
        self.saturation = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS meaning_saturation (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.saturation = min(1.0, self.saturation + 0.005)
        self._save(); pirp_context["meaning_saturation"] = self.saturation; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO meaning_saturation (val,ts) VALUES (?,?)", (self.saturation, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"saturation": self.saturation}
