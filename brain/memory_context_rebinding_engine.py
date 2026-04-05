import sqlite3, json, time

class MemoryContextRebindingEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.rebind = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS memory_rebind (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.rebind = pirp_context.get("temporal_anchor", 0.0)
        self._save(); pirp_context["memory_rebind"] = self.rebind; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO memory_rebind (val,ts) VALUES (?,?)", (self.rebind, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"rebind": self.rebind}
