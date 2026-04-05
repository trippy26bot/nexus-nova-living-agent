import sqlite3, json, time

class IncompleteThoughtRecurrenceLoop:
    def __init__(self, db_path):
        self.db_path = db_path
        self.loop = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS thought_loop (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.loop = min(1.0, self.loop + 0.01)
        self._save(); pirp_context["thought_loop"] = self.loop; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO thought_loop (val,ts) VALUES (?,?)", (self.loop, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"loop": self.loop}
