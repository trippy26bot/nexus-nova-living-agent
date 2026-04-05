# brain/council_observer_silence_conduction.py
import sqlite3, json, time, random

class CouncilObserverSilenceConduction:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"silence_conduction": 0.5, "council_observer_flow": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS council_observer_silence_conduction (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        bond = pirp_context.get("drive_context", {}).get("drive_state", {}).get("bond_tension", 0.5)
        self.state["silence_conduction"] = min(1.0, max(0.0, self.state["silence_conduction"] * 0.9 + bond * 0.1))
        self.state["council_observer_flow"] = self.state["council_observer_flow"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["council_observer_silence_conduction"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO council_observer_silence_conduction (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
