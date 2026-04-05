import sqlite3, json, time

class SelectiveAttentionBlindness:
    def __init__(self, db_path):
        self.db_path = db_path
        self.blindness = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS attention_blindness (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.blindness = min(1.0, pirp_context.get("itg_tension", 0.5))
        self._save(); pirp_context["attention_blindness"] = self.blindness; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO attention_blindness (val,ts) VALUES (?,?)", (self.blindness, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"blindness": self.blindness}
