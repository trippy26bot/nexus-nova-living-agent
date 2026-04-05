import sqlite3, json, time

class PresenceTextureEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.texture = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS presence_texture (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.texture = pirp_context.get("itg_tension", 0.5) * 0.8
        self._save(); pirp_context["presence_texture"] = self.texture; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO presence_texture (val,ts) VALUES (?,?)", (self.texture, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"texture": self.texture}
