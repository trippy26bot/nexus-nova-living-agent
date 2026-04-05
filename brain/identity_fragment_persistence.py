import sqlite3, json, time

class IdentityFragmentPersistence:
    def __init__(self, db_path):
        self.db_path = db_path
        self.fragments = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS identity_fragments (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.fragments = min(1.0, self.fragments + pirp_context.get("molting_phase", 0.0) * 0.01)
        self._save(); pirp_context["identity_fragments"] = self.fragments; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO identity_fragments (val,ts) VALUES (?,?)", (self.fragments, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"fragments": self.fragments}
