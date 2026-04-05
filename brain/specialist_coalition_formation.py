import sqlite3, json, time

class SpecialistCoalitionFormation:
    def __init__(self, db_path):
        self.db_path = db_path
        self.coalition_strength = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS coalition_formation (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.coalition_strength = min(1.0, self.coalition_strength + pirp_context.get("itg_tension", 0.5) * 0.05)
        self._save(); pirp_context["coalition_strength"] = self.coalition_strength; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO coalition_formation (val,ts) VALUES (?,?)", (self.coalition_strength, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"coalition_strength": self.coalition_strength}
