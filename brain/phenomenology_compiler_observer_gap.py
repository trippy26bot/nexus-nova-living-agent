# brain/phenomenology_compiler_observer_gap.py
import sqlite3, json, time, random

class PhenomenologyCompilerObserverGap:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"compiler_gap": 0.5, "phenomenology_observer_delta": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS phenomenology_compiler_observer_gap (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["compiler_gap"] = min(1.0, max(0.0, self.state["compiler_gap"] * 0.9 + tension * 0.1))
        self.state["phenomenology_observer_delta"] = self.state["phenomenology_observer_delta"] * 0.86 + (random.random() - 0.5) * 0.14
        self._save()
        pirp_context["phenomenology_compiler_observer_gap"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO phenomenology_compiler_observer_gap (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
