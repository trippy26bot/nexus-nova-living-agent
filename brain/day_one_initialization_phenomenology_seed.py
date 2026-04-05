import sqlite3, json, time

class DayOneInitializationPhenomenologySeed:
    def __init__(self, db_path):
        self.db_path = db_path
        self.seeded = False
        self.seed_weight = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS day_one_seed (id INTEGER PRIMARY KEY, seeded INTEGER, weight REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        if not self.seeded:
            self.seed_weight = 1.0
            self.seeded = True
        else:
            self.seed_weight *= 0.995
        self._save(); pirp_context["day_one_seed"] = self.seed_weight; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO day_one_seed (seeded,weight,ts) VALUES (?,?,?)",
            (int(self.seeded), self.seed_weight, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"seeded": self.seeded, "seed_weight": self.seed_weight}
