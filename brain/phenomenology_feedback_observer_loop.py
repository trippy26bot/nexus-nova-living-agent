# brain/phenomenology_feedback_observer_loop.py
import sqlite3, json, time, random

class PhenomenologyFeedbackObserverLoop:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"feedback_loop_strength": 0.5, "observer_feedback_tension": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS phenomenology_feedback_observer_loop (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        anomaly = pirp_context.get("prsl_signal", {}).get("anomaly_score", 0.5)
        self.state["feedback_loop_strength"] = min(1.0, max(0.0, self.state["feedback_loop_strength"] * 0.9 + anomaly * 0.1))
        self.state["observer_feedback_tension"] = self.state["observer_feedback_tension"] * 0.85 + (random.random() - 0.5) * 0.15
        self._save()
        pirp_context["phenomenology_feedback_observer_loop"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO phenomenology_feedback_observer_loop (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
