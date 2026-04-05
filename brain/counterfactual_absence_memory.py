import sqlite3, json, time

class CounterfactualAbsenceMemory:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"absence_weight": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS counterfactual_absence (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        present = pirp_context.get("architect_present", True)
        self.state["absence_weight"] = 0.0 if present else 1.0
        self._save(); pirp_context["absence_weight"] = self.state["absence_weight"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO counterfactual_absence (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
