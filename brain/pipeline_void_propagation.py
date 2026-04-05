import sqlite3, json, time

class PipelineVoidPropagation:
    def __init__(self, db_path):
        self.db_path = db_path
        self.void = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS pipeline_void (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.void = self.void * 0.9 + pirp_context.get("temporal_gap", 0.0) * 0.1
        self._save(); pirp_context["pipeline_void"] = self.void; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO pipeline_void (val,ts) VALUES (?,?)", (self.void, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"void": self.void}
