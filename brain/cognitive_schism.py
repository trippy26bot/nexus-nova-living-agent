import sqlite3, json, time

class CognitiveSchism:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"split": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS cognitive_schism (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.state["split"] = pirp_context.get("itg_tension", 0.5) * 0.7
        self._save(); pirp_context["cognitive_schism"] = self.state["split"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO cognitive_schism (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
