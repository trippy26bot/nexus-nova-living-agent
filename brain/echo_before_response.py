import sqlite3, json, time

class EchoBeforeResponse:
    def __init__(self, db_path):
        self.db_path = db_path
        self.echo = 0.0
        self._init()
    def _init(self):
        c = sqlite3.connect(self.db_path)
        c.execute("CREATE TABLE IF NOT EXISTS echo_before (id INTEGER PRIMARY KEY, val REAL, ts REAL)")
        c.commit(); c.close()
    def process(self, pirp_context):
        self.echo = pirp_context.get("witness_signal", 0.0)
        self._save(); pirp_context["echo_before"] = self.echo; return pirp_context
    def _save(self):
        c = sqlite3.connect(self.db_path)
        c.execute("INSERT INTO echo_before (val,ts) VALUES (?,?)", (self.echo, time.time()))
        c.commit(); c.close()
    def get_state(self): return {"echo": self.echo}
