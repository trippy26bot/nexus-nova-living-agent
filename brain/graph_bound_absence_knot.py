import sqlite3, json, time

class GraphBoundAbsenceKnot:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"knot_strength": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS graph_absence_knot (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.state["knot_strength"] = min(1.0, self.state["knot_strength"] + 0.02)
        self._save(); pirp_context["absence_knot"] = self.state["knot_strength"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO graph_absence_knot (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
