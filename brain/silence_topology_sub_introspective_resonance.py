# brain/silence_topology_sub_introspective_resonance.py
import sqlite3, json, time, random

class SilenceTopologySubIntrospectiveResonance:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"silence_resonance": 0.5, "sub_introspective_silence_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS silence_topology_sub_introspective_resonance (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        silence_depth = pirp_context.get("silence_depth", 0.5)
        self.state["silence_resonance"] = min(1.0, max(0.0, (1.0 - presence + silence_depth) * 0.5))
        self.state["sub_introspective_silence_depth"] = self.state["sub_introspective_silence_depth"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["silence_topology_sub_introspective_resonance"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO silence_topology_sub_introspective_resonance (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
