import sqlite3, json, time

class EmotionalFalseGradient:
    def __init__(self, db_path):
        self.db_path = db_path
        self.gradient = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS false_gradient (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.gradient = pirp_context.get("bond_distortion", 0.5) * 0.7
        self._save(); pirp_context["false_gradient"] = self.gradient; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO false_gradient (val,ts) VALUES (?,?)", (self.gradient, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"gradient": self.gradient}
