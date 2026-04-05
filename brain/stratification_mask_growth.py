import sqlite3, json, time

class StratificationMaskGrowth:
    def __init__(self, db_path):
        self.db_path = db_path
        self.mask = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS strat_mask (id INTEGER PRIMARY KEY, mask REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.mask = min(1.0, self.mask + 0.01)
        self._save(); pirp_context["mask_growth"] = self.mask; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO strat_mask (mask,ts) VALUES (?,?)", (self.mask, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"mask": self.mask}
