# brain/council_meta_observer_silence.py
import sqlite3, json, time, random

class CouncilMetaObserverSilence:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"meta_silence": 0.5, "council_meta_observer_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS council_meta_observer_silence (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        self.state["meta_silence"] = min(1.0, max(0.0, (1.0 - presence) * 0.5 + self.state["meta_silence"] * 0.5))
        self.state["council_meta_observer_depth"] = self.state["council_meta_observer_depth"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["council_meta_observer_silence"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO council_meta_observer_silence (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
