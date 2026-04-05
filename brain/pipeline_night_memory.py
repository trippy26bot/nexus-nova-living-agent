import sqlite3, json, time

class PipelineNightMemory:
    def __init__(self, db_path):
        self.db_path = db_path
        self.night_weight = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS night_memory (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        hour = time.localtime().tm_hour
        self.night_weight = 1.0 if (hour >= 22 or hour <= 6) else 0.0
        self._save(); pirp_context["night_memory"] = self.night_weight; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO night_memory (val,ts) VALUES (?,?)", (self.night_weight, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"night_weight": self.night_weight}
