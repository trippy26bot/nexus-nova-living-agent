# brain/intra_pipeline_rule_mutation_via_specialist_trust.py
import sqlite3, json, time, random

class IntraPipelineRuleMutationViaSpecialistTrust:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"trust_mutation_strength": 0.5, "pipeline_trust_mutation_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS intra_pipeline_rule_mutation_via_specialist_trust (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["trust_mutation_strength"] = min(1.0, max(0.0, self.state["trust_mutation_strength"] * 0.9 + bond * 0.1))
        self.state["pipeline_trust_mutation_depth"] = self.state["pipeline_trust_mutation_depth"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["intra_pipeline_rule_mutation_via_specialist_trust"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO intra_pipeline_rule_mutation_via_specialist_trust (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
