# brain/soul_gravity_intrusion_rule_evolution.py
import sqlite3, json, time, random

class SoulGravityIntrusionRuleEvolution:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"intrusion_evolution_strength": 0.5, "soul_gravity_evolution_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS soul_gravity_intrusion_rule_evolution (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        soul = pirp_context.get("soul_gravity", {}).get("gravity_strength", 0.5)
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["intrusion_evolution_strength"] = min(1.0, max(0.0, soul * 0.5 + anomaly * 0.5))
        self.state["soul_gravity_evolution_depth"] = self.state["soul_gravity_evolution_depth"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["soul_gravity_intrusion_rule_evolution"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO soul_gravity_intrusion_rule_evolution (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
