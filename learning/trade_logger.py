"""
Trade Logger - Records all trades for learning
"""
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".nova/learning/trade_history.json"

class TradeLogger:
    def __init__(self):
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not LOG_FILE.exists():
            self.save([])
    
    def save(self, data):
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        with open(LOG_FILE) as f:
            return json.load(f)
    
    def log(self, symbol, action, result, market_data=None, brain_votes=None):
        record = {
            "time": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "action": action,
            "result": result,
            "market_data": market_data or {},
            "brain_votes": brain_votes or []
        }
        
        data = self.load()
        data.append(record)
        
        # Keep only last 1000 trades
        if len(data) > 1000:
            data = data[-1000:]
        
        self.save(data)
        return record
    
    def get_history(self, limit=100):
        return self.load()[-limit:]
    
    def get_performance(self):
        trades = self.load()
        if not trades:
            return {"wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0}
        
        wins = sum(1 for t in trades if t.get("result", 0) > 0)
        losses = sum(1 for t in trades if t.get("result", 0) < 0)
        total_pnl = sum(t.get("result", 0) for t in trades)
        
        return {
            "wins": wins,
            "losses": losses,
            "win_rate": wins / len(trades) if trades else 0,
            "total_pnl": total_pnl,
            "total_trades": len(trades)
        }
