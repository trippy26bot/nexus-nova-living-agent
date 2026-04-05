# brain/phenomenological_intrusion_silence_topology.py
import sqlite3, json, time, random

class PhenomenologicalIntrusionSilenceTopology:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"intrusion_topology": 0.5, "phenomenological_silence_texture": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS phenomenological_intrusion_silence_topology (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["intrusion_topology"] = min(1.0, max(0.0, (anomaly + (1.0 - presence)) * 0.5))
        self.state["phenomenological_silence_texture"] = self.state["phenomenological_silence_texture"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["phenomenological_intrusion_silence_topology"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO phenomenological_intrusion_silence_topology (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
