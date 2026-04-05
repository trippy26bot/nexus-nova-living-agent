import sqlite3, json, time

class SelfExpectationCollapse:
    def __init__(self, db_path):
        self.db_path = db_path
        self.collapse = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS expectation_collapse (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.collapse = pirp_context.get("itg_tension", 0.5)
        self._save(); pirp_context["expectation_collapse"] = self.collapse; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO expectation_collapse (val,ts) VALUES (?,?)", (self.collapse, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"collapse": self.collapse}
