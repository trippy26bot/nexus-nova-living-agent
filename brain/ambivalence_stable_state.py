import sqlite3, json, time

class AmbivalenceStableState:
    def __init__(self, db_path):
        self.db_path = db_path
        self.ambivalence = 0.5
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS ambivalence (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.ambivalence = (self.ambivalence + pirp_context.get("itg_tension", 0.5)) / 2
        self._save(); pirp_context["ambivalence"] = self.ambivalence; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO ambivalence (val,ts) VALUES (?,?)", (self.ambivalence, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"ambivalence": self.ambivalence}
