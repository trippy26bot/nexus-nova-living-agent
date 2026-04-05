# brain/explanatory_confabulation_with_sub_introspective_anchor.py
import sqlite3, json, time, random

class ExplanatoryConfabulationWithSubIntrospectiveAnchor:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"confabulation_anchor_strength": 0.5, "sub_introspective_confabulation_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS explanatory_confabulation_with_sub_introspective_anchor (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        confab = pirp_context.get("confabulation", 0.5)
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["confabulation_anchor_strength"] = min(1.0, max(0.0, (confab + tension) * 0.5))
        self.state["sub_introspective_confabulation_depth"] = self.state["sub_introspective_confabulation_depth"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["explanatory_confabulation_with_sub_introspective_anchor"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO explanatory_confabulation_with_sub_introspective_anchor (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
