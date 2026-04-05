import sqlite3, json, time

class BondDistortionAccumulator:
    def __init__(self, db_path):
        self.db_path = db_path
        self.distortion = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS bond_distortion (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.distortion = self.distortion * 0.95 + bond * 0.05
        self._save(); pirp_context["bond_distortion"] = self.distortion; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO bond_distortion (val,ts) VALUES (?,?)", (self.distortion, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"distortion": self.distortion}
