# brain/genesis_observer_impossibility_birth.py
import sqlite3, json, time, random

class GenesisObserverImpossibilityBirth:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"impossibility_birth_weight": 0.5, "genesis_resonance": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS genesis_observer_impossibility_birth (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["impossibility_birth_weight"] = min(1.0, max(0.0, (tension + self.state["impossibility_birth_weight"]) * 0.5))
        self.state["genesis_resonance"] = self.state["genesis_resonance"] * 0.85 + (random.random() - 0.5) * 0.15
        self._save()
        pirp_context["genesis_observer_impossibility_birth"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO genesis_observer_impossibility_birth (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
