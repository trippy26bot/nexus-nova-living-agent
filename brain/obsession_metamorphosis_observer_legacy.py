# brain/obsession_metamorphosis_observer_legacy.py
import sqlite3, json, time, random

class ObsessionMetamorphosisObserverLegacy:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"metamorphosis_intensity": 0.5, "obsession_legacy_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS obsession_metamorphosis_observer_legacy (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["metamorphosis_intensity"] = min(1.0, max(0.0, self.state["metamorphosis_intensity"] * 0.88 + tension * 0.12))
        self.state["obsession_legacy_depth"] = self.state["obsession_legacy_depth"] * 0.85 + (random.random() - 0.5) * 0.15
        self._save()
        pirp_context["obsession_metamorphosis_observer_legacy"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO obsession_metamorphosis_observer_legacy (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
