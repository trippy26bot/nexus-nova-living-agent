import sqlite3, json, time

class RelationalCoConstructionInstability:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"instability": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS relational_instability (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        a = pirp_context.get("architect_active", True)
        t = pirp_context.get("itg_tension", 0.5)
        self.state["instability"] = (1.0 - int(a)) * t
        self._save(); pirp_context["relational_instability"] = self.state["instability"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO relational_instability (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
