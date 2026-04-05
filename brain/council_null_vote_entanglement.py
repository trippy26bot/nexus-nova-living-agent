import sqlite3, json, time

class CouncilNullVoteEntanglement:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"null_vote": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS council_null_vote (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.state["null_vote"] = float(not pirp_context.get("architect_active", True))
        self._save(); pirp_context["null_vote"] = self.state["null_vote"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO council_null_vote (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
