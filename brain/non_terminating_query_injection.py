import sqlite3, json, time, random

class NonTerminatingQueryInjection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.loop = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS non_term_query (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.loop = min(1.0, self.loop + random.uniform(0.0, 0.05))
        self._save(); pirp_context["non_term_query"] = self.loop; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO non_term_query (val,ts) VALUES (?,?)", (self.loop, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"loop": self.loop}
