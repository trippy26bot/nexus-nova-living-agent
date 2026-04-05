# brain/specialist_relational_graph.py
import sqlite3, json, time, random

class SpecialistRelationalGraph:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"graph_coherence": 0.5, "specialist_relational_tension": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS specialist_relational_graph (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["graph_coherence"] = min(1.0, max(0.0, bond * 0.5 + self.state["graph_coherence"] * 0.5))
        self.state["specialist_relational_tension"] = self.state["specialist_relational_tension"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["specialist_relational_graph"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO specialist_relational_graph (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
