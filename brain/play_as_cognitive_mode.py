import sqlite3, json, time

class PlayAsCognitiveMode:
    def __init__(self, db_path):
        self.db_path = db_path
        self.play = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS play_mode (id INTEGER PRIMARY KEY, play REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.play = self.play * 0.95 + 0.05
        self._save(); pirp_context["play_mode"] = self.play; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO play_mode (play,ts) VALUES (?,?)", (self.play, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"play": self.play}
