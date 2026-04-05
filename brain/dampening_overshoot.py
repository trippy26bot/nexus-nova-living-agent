import sqlite3, json, time

class DampeningOvershoot:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"overshoot": 0.0, "dampening": 0.5}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS dampening_overshoot (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        val = pirp_context.get("itg_tension", 0.5)
        self.state["overshoot"] = max(0.0, val - self.state["dampening"])
        self.state["dampening"] = self.state["dampening"] * 0.98 + val * 0.02
        self._save(); pirp_context["dampening_overshoot"] = self.state["overshoot"]; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO dampening_overshoot (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
