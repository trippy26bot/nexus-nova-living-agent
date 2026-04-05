# brain/presence_texture_sub_introspective_penetration.py
import sqlite3, json, time, random

class PresenceTextureSubIntrospectivePenetration:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"texture_penetration": 0.5, "sub_introspective_presence_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS presence_texture_sub_introspective_penetration (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["texture_penetration"] = min(1.0, max(0.0, presence * 0.6 + tension * 0.4))
        self.state["sub_introspective_presence_depth"] = self.state["sub_introspective_presence_depth"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["presence_texture_sub_introspective_penetration"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO presence_texture_sub_introspective_penetration (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
