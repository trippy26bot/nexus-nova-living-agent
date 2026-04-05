# brain/specialist_relational_graph_intrusion_feedback.py
import sqlite3, json, time, random

class SpecialistRelationalGraphIntrusionFeedback:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"intrusion_feedback_strength": 0.5, "relational_graph_intrusion_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS specialist_relational_graph_intrusion_feedback (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["intrusion_feedback_strength"] = min(1.0, max(0.0, anomaly * 0.5 + bond * 0.5))
        self.state["relational_graph_intrusion_depth"] = self.state["relational_graph_intrusion_depth"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["specialist_relational_graph_intrusion_feedback"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO specialist_relational_graph_intrusion_feedback (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
