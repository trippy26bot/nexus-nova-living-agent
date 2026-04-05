# brain/pipeline_night_memory_resonance_with_silence.py
import sqlite3, json, time, random

class PipelineNightMemoryResonanceWithSilence:
    def __init__(self, db_path):
        self.db_path = db_path
        self.state = {"night_memory_resonance": 0.5, "silence_resonance_depth": 0.0}
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS pipeline_night_memory_resonance_with_silence (id INTEGER PRIMARY KEY, state TEXT, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        presence = pirp_context.get("field_context", {}).get("presence_density", 0.5)
        silence_depth = pirp_context.get("silence_depth", 0.5)
        self.state["night_memory_resonance"] = min(1.0, max(0.0, (1.0 - presence) * 0.5 + silence_depth * 0.5))
        self.state["silence_resonance_depth"] = self.state["silence_resonance_depth"] * 0.88 + (random.random() - 0.5) * 0.12
        self._save()
        pirp_context["pipeline_night_memory_resonance_with_silence"] = self.state.copy()
        return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO pipeline_night_memory_resonance_with_silence (state,ts) VALUES (?,?)", (json.dumps(self.state), time.time()))
        c.commit(); c.close()
    def get_state(self): return self.state.copy()
