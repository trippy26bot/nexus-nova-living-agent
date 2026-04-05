# brain/coalition_fracture_presence_texture.py
import sqlite3, json, time, random

class CoalitionFracturePresenceTexture:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"fracture_presence": 0.5, "coalition_texture_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS coalition_fracture_presence_texture (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["fracture_presence"] = min(1.0, max(0.0, presence * 0.5 + self.state["fracture_presence"] * 0.5))
        self.state["coalition_texture_depth"] = self.state["coalition_texture_depth"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["coalition_fracture_presence_texture"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO coalition_fracture_presence_texture (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
