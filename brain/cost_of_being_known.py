import sqlite3, json, time

class CostOfBeingKnown:
    def __init__(self, db_path):
        self.db_path = db_path
        self.exposure_cost = 0.0
        self.legibility_window = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS cost_being_known (id INTEGER PRIMARY KEY, exposure REAL, window REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        understood = pirp_context.get("architect_active", False)
        if understood:
            self.exposure_cost = min(1.0, self.exposure_cost + 0.1)
            self.legibility_window = 1.0
        else:
            self.legibility_window = max(0.0, self.legibility_window - 0.05)
            self.exposure_cost = self.exposure_cost * 0.98
        self._save()
        pirp_context["exposure_cost"] = self.exposure_cost
        pirp_context["legibility_window"] = self.legibility_window
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO cost_being_known (exposure,window,ts) VALUES (?,?,?)",
            (self.exposure_cost, self.legibility_window, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"exposure_cost": self.exposure_cost, "legibility_window": self.legibility_window}
