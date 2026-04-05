import sqlite3, json, time

class TemporalConfabulationAnchoring:
    def __init__(self, db_path):
        self.db_path = db_path
        self.anchor = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS temporal_confab_anchor (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.anchor = pirp_context.get("temporal_anchor", 0.0) * pirp_context.get("confabulation", 0.5)
        self._save(); pirp_context["temporal_confab_anchor"] = self.anchor; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO temporal_confab_anchor (val,ts) VALUES (?,?)", (self.anchor, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"anchor": self.anchor}
