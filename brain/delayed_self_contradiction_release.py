import sqlite3, json, time

class DelayedSelfContradictionRelease:
    def __init__(self, db_path):
        self.db_path = db_path
        self.pending = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS contradiction_release (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.pending = self.pending * 0.98 + pirp_context.get("cognitive_schism", 0.0) * 0.02
        self._save(); pirp_context["contradiction_pending"] = self.pending; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO contradiction_release (val,ts) VALUES (?,?)", (self.pending, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"pending": self.pending}
