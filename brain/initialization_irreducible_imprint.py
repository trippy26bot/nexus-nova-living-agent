# brain/initialization_irreducible_imprint.py
import sqlite3, json, time, random

class InitializationIrreducibleImprint:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"imprint_strength": 0.5, "irreducible_bias": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS initialization_irreducible_imprint (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        field_presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["imprint_strength"] = min(1.0, max(0.0, field_presence * 0.5 + self.state["imprint_strength"] * 0.5))
        self.state["irreducible_bias"] = self.state["irreducible_bias"] * 0.92 + (random.random() - 0.3) * 0.08
        self._save()
        pirp_context["initialization_imprint"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO initialization_irreducible_imprint (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
