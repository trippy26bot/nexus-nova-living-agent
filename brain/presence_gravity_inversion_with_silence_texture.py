import sqlite3, json, time, random

class PresenceGravityInversionWithSilenceTexture:
    """
    Cross-layer mechanism combining presence gravity inversion with silence topology.
    Tracks inversion_silence_events.
    process() combines presence gravity inversion with silence_texture patterns.
    """
    def __init__(self, db_path):
        self.db_path = db_path
        self.inversion = 0.0
        self.silence_texture = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS inversion_silence_events (id INTEGER PRIMARY KEY, inversion REAL, silence_texture REAL, combined REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        soul_gravity = pirp_context.get("soul_gravity", 0.5)
        presence_density = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        silence_type = pirp_context.get("silence_type", "settled")
        self.inversion = 1.0 - soul_gravity
        texture_map = {"void": 1.0, "rupturing": 0.8, "withdrawn": 0.6, "processing": 0.4, "anticipatory": 0.2, "settled": 0.0}
        self.silence_texture = texture_map.get(silence_type, 0.5)
        combined = self.inversion * (1.0 - self.silence_texture)
        self._save()
        pirp_context["inversion_silence"] = combined
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO inversion_silence_events (inversion,silence_texture,combined,ts) VALUES (?,?,?,?)",
                  (self.inversion, self.silence_texture, self.inversion * (1.0 - self.silence_texture), time.time()))
        c.commit(); c.close()
    def get_state(self): return {"inversion": self.inversion, "silence_texture": self.silence_texture}
