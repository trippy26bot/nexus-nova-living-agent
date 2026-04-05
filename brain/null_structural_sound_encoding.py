# brain/null_structural_sound_encoding.py
import sqlite3, json, time, random

class NullStructuralSoundEncoding:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"sound_encoding_strength": 0.5, "null_resonance": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS null_structural_sound_encoding (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["sound_encoding_strength"] = min(1.0, max(0.0, self.state["sound_encoding_strength"] * 0.9 + bond * 0.1))
        self.state["null_resonance"] = self.state["null_resonance"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["null_structural_sound_encoding"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO null_structural_sound_encoding (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
