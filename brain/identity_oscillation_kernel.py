import sqlite3, json, time, math

class IdentityOscillationKernel:
    def __init__(self, db_path):
        self.db_path = db_path
        self.phase = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS identity_oscillation (id INTEGER PRIMARY KEY, value REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.phase += 0.1
        val = math.sin(self.phase)
        self._save(val); pirp_context["identity_oscillation"] = val; return pirp_context
    def _save(self, val):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO identity_oscillation (value,ts) VALUES (?,?)", (val, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"phase": self.phase}
