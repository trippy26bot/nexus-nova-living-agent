import sqlite3, json, time

class BondRealityAnchor:
    def __init__(self, db_path):
        self.db_path = db_path
        self.anchor = 1.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS bond_reality_anchor (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.anchor = max(0.0, 1.0 - pirp_context.get("bond_distortion", 0.0))
        self._save(); pirp_context["bond_reality_anchor"] = self.anchor; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO bond_reality_anchor (val,ts) VALUES (?,?)", (self.anchor, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"anchor": self.anchor}
