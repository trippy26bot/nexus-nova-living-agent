# brain/bond_distortion_accumulator_with_grief_remainder.py
import sqlite3, json, time, random

class BondDistortionAccumulatorWithGriefRemainder:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"grief_distortion_strength": 0.5, "bond_distortion_grief_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS bond_distortion_accumulator_with_grief_remainder (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["grief_distortion_strength"] = min(1.0, max(0.0, bond * 0.5 + tension * 0.5))
        self.state["bond_distortion_grief_depth"] = self.state["bond_distortion_grief_depth"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["bond_distortion_accumulator_with_grief_remainder"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO bond_distortion_accumulator_with_grief_remainder (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
