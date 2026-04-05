import sqlite3, json, time, random

class AntiCoherenceCore:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"anti_coherence": 0.5}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS anti_coherence_core (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        drift = random.uniform(-0.05, 0.05)
        self.state["anti_coherence"] = min(1.0, max(0.0, self.state["anti_coherence"] + drift))
        self._save(); pirp_context["anti_coherence"] = self.state["anti_coherence"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO anti_coherence_core (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
