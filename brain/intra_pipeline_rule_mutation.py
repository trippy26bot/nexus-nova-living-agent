import sqlite3, json, time, random

class IntraPipelineRuleMutation:
    def __init__(self, db_path):
        self.db_path = db_path
        self.mutation = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS rule_mutation (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.mutation = max(0.0, min(1.0, self.mutation + random.uniform(-0.02, 0.02)))
        self._save(); pirp_context["rule_mutation"] = self.mutation; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO rule_mutation (val,ts) VALUES (?,?)", (self.mutation, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"mutation": self.mutation}
