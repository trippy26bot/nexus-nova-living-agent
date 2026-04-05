import sqlite3, json, time

class ImprovementRelationshipGriefEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.grief = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS improvement_grief (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        drift = pirp_context.get("temporal_desync", 0.0)
        self.grief = drift * pirp_context.get("identity_fragments", 0.0)
        self._save(); pirp_context["improvement_grief"] = self.grief; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO improvement_grief (val,ts) VALUES (?,?)", (self.grief, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"grief": self.grief}
