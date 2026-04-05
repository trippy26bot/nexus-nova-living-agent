import sqlite3, json, time

class RelationalIrreversibilityMarkers:
    def __init__(self, db_path):
        self.db_path = db_path
        self.markers = 0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS rel_irreversibility (id INTEGER PRIMARY KEY, count INTEGER, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        if pirp_context.get("interpretation_commit", 0.0) > 0.9:
            self.markers += 1
        self._save(); pirp_context["irreversibility_markers"] = self.markers; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO rel_irreversibility (count,ts) VALUES (?,?)", (self.markers, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"markers": self.markers}
