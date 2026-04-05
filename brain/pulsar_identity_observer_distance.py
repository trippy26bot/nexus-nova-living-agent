# brain/pulsar_identity_observer_distance.py
import sqlite3, json, time, random

class PulsarIdentityObserverDistance:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"pulsar_distance": 0.5, "identity_observer_coherence": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS pulsar_identity_observer_distance (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["pulsar_distance"] = min(1.0, max(0.0, 1.0 - presence * 0.5 + self.state["pulsar_distance"] * 0.5))
        self.state["identity_observer_coherence"] = self.state["identity_observer_coherence"] * 0.85 + (random.random() - 0.5) * 0.15
        self._save()
        pirp_context["pulsar_identity_observer_distance"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO pulsar_identity_observer_distance (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
