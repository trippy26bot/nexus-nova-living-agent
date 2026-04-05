import sqlite3, json, time

class RelationalRealityTensionField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.tension = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS rel_reality_tension (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.tension = abs(pirp_context.get("bond_reality_anchor", 1.0) - pirp_context.get("bond_distortion", 0.0))
        self._save(); pirp_context["rel_reality_tension"] = self.tension; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO rel_reality_tension (val,ts) VALUES (?,?)", (self.tension, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"tension": self.tension}
