"""Unified Logger for NOVA"""
import json
from datetime import datetime
from pathlib import Path

class NovaLogger:
    def __init__(self, log_file="~/.nova/logs/nova.log"):
        self.log_file = Path(log_file).expanduser()
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, level, message):
        entry = f"[{datetime.now().isoformat()}] {level}: {message}\n"
        with open(self.log_file, "a") as f:
            f.write(entry)
    
    def info(self, message):
        self.log("INFO", message)
    
    def error(self, message):
        self.log("ERROR", message)
