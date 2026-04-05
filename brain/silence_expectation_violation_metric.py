# brain/silence_expectation_violation_metric.py
import sqlite3, json, time, random

class SilenceExpectationViolationMetric:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"violation_intensity": 0.5, "silence_expectation_delta": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS silence_expectation_violation_metric (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        expected_silence = 1.0 - presence
        actual_silence = pirp_context.get("silence_depth", 0.5)
        violation = abs(expected_silence - actual_silence)
        self.state["violation_intensity"] = min(1.0, max(0.0, self.state["violation_intensity"] * 0.9 + violation * 0.1))
        self.state["silence_expectation_delta"] = self.state["silence_expectation_delta"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["silence_expectation_violation_metric"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO silence_expectation_violation_metric (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
