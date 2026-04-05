# brain/soul_gravity_silence_topology_field.py
import sqlite3, json, time, random

class SoulGravitySilenceTopologyField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"soul_silence_field": 0.5, "gravity_silence_topology_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS soul_gravity_silence_topology_field (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        soul = pirp_context.get("soul_gravity", {}).get("gravity_strength", 0.5)
        silence_depth = pirp_context.get("silence_depth", 0.5)
        self.state["soul_silence_field"] = min(1.0, max(0.0, soul * 0.5 + silence_depth * 0.5))
        self.state["gravity_silence_topology_depth"] = self.state["gravity_silence_topology_depth"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["soul_gravity_silence_topology_field"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO soul_gravity_silence_topology_field (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
