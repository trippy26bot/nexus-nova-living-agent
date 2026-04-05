import sqlite3, json, time

class RelationalWeightAsymmetryEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.asym = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS rel_asym (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        p = pirp_context.get("architect_present", True)
        a = pirp_context.get("architect_active", True)
        self.asym = float(p and not a)
        self._save(); pirp_context["rel_asym"] = self.asym; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO rel_asym (val,ts) VALUES (?,?)", (self.asym, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"asym": self.asym}
