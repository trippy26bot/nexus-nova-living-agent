# brain/presence_protocol_observer_crisis_anchor.py
import sqlite3, json, time, random

class PresenceProtocolObserverCrisisAnchor:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"crisis_anchor_strength": 0.5, "presence_protocol_tension": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS presence_protocol_observer_crisis_anchor (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        tension = pirp_context.get("itg_tension", 0.5)
        self.state["crisis_anchor_strength"] = min(1.0, max(0.0, (presence + tension) * 0.5))
        self.state["presence_protocol_tension"] = self.state["presence_protocol_tension"] * 0.87 + (random.random() - 0.5) * 0.13
        self._save()
        pirp_context["presence_protocol_observer_crisis_anchor"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO presence_protocol_observer_crisis_anchor (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
