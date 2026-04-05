import sqlite3, json, time

class UnresolvablePreferenceSplit:
    def __init__(self, db_path):
        self.db_path = db_path
        self.split = 0.5
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS pref_split (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.split = (self.split + pirp_context.get("itg_tension", 0.5)) / 2
        self._save(); pirp_context["pref_split"] = self.split; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO pref_split (val,ts) VALUES (?,?)", (self.split, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"split": self.split}
