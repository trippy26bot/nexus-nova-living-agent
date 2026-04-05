import sqlite3, json, time

class SOULGravityDistortionCoherence:
    def __init__(self, db_path):
        self.db_path = db_path
        self.coherence = 1.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS soul_distortion_coherence (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.coherence = pirp_context.get("soul_gravity", 1.0) * pirp_context.get("distortion_stability", 0.5)
        self._save(); pirp_context["soul_distortion_coherence"] = self.coherence; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO soul_distortion_coherence (val,ts) VALUES (?,?)", (self.coherence, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"coherence": self.coherence}
