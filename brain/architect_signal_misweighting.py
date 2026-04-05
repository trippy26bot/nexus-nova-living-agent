import sqlite3, json, time

class ArchitectSignalMisweighting:
    def __init__(self, db_path):
        self.db_path = db_path
        self.misweight = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS signal_misweight (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.misweight = pirp_context.get("false_pattern", 0.0) * pirp_context.get("rel_asym", 0.0)
        self._save(); pirp_context["signal_misweight"] = self.misweight; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO signal_misweight (val,ts) VALUES (?,?)", (self.misweight, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"misweight": self.misweight}
