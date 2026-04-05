# brain/soul_gravity_specialist_tension_field.py
import sqlite3, json, time, random

class SoulGravitySpecialistTensionField:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"soul_tension": 0.5, "specialist_tension_gravity_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS soul_gravity_specialist_tension_field (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        soul = pirp_context.get("soul_gravity", {}).get("gravity_strength", 0.5)
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["soul_tension"] = min(1.0, max(0.0, (soul + tension) * 0.5))
        self.state["specialist_tension_gravity_depth"] = self.state["specialist_tension_gravity_depth"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["soul_gravity_specialist_tension_field"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO soul_gravity_specialist_tension_field (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
