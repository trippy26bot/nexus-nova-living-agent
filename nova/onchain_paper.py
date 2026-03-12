#!/usr/bin/env python3
"""
On-Chain Paper Trading System
Proves profitability before real wallet
"""
import requests
import json
import os
from datetime import datetime
from typing import Dict, List
import random

ONCHAIN_DIR = os.path.expanduser("~/.nova/onchain_paper")
os.makedirs(ONCHAIN_DIR, exist_ok=True)

POSITIONS_FILE = os.path.join(ONCHAIN_DIR, "positions.json")
STATE_FILE = os.path.join(ONCHAIN_DIR, "state.json")
HISTORY_FILE = os.path.join(ONCHAIN_DIR, "history.json")

PAPER_BALANCE = 10000  # Start with $10k

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE) as f:
            return json.load(f)
    return {"positions": []}

def save_positions(data):
    with open(POSITIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "balance": PAPER_BALANCE,
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "pnl": 0,
        "started_at": datetime.now().isoformat()
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# Import real data from Nova's universal gatherer (now with pump.fun!)
def get_real_opportunities():
    """Get real opportunities from Nova's universal gatherer"""
    try:
        import sys
        sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace"))
        from nova.nova_universal_gatherer import UniversalGatherer
        
        gatherer = UniversalGatherer()
        opportunities = gatherer.find_opportunities()
        
        if opportunities:
            return opportunities[:10]
        return None
    except Exception as e:
        print(f"Gatherer error: {e}")
        return None

# Try to get real data first, fallback to mock
REAL_OPPORTUNITIES = get_real_opportunities()

# Mock opportunities (fallback)
MOCK_OPPORTUNITIES = [
    {"symbol": "SOL", "name": "Solana", "base_price": 86.50, "volatility": 0.03},
    {"symbol": "ETH", "name": "Ethereum", "base_price": 1850.00, "volatility": 0.02},
    {"symbol": "BTC", "name": "Bitcoin", "base_price": 43500.00, "volatility": 0.015},
    {"symbol": "PEPE", "name": "Pepe", "base_price": 0.0000012, "volatility": 0.15},
    {"symbol": "WIF", "name": "dogwifhat", "base_price": 0.85, "volatility": 0.08},
    {"symbol": "BONK", "name": "Bonk", "base_price": 0.000015, "volatility": 0.12},
    {"symbol": "JUP", "name": "Jupiter", "base_price": 0.55, "volatility": 0.06},
    {"symbol": "PYTH", "name": "Pyth Network", "base_price": 0.22, "volatility": 0.07},
    {"symbol": "SUI", "name": "Sui", "base_price": 0.65, "volatility": 0.09},
    {"symbol": "SEI", "name": "Sei", "base_price": 0.35, "volatility": 0.08},
]

class PaperTrader:
    def __init__(self):
        self.state = load_state()
        self.positions = load_positions()
        self.history = load_history()
    
    def get_current_prices(self) -> Dict:
        """Get current mock prices (with some randomness)"""
        prices = {}
        for opp in MOCK_OPPORTUNITIES:
            # Add some volatility-based movement
            change = random.uniform(-opp["volatility"], opp["volatility"])
            current = opp["base_price"] * (1 + change)
            prices[opp["symbol"]] = current
        return prices
    
    def find_opportunities(self) -> List[Dict]:
        """Find paper trading opportunities using REAL data"""
        # Try real data first
        if REAL_OPPORTUNITIES:
            opportunities = []
            for opp in REAL_OPPORTUNITIES:
                symbol = opp.get("symbol", "")
                price = opp.get("base_price", 1)
                change = opp.get("change_24h", 0)
                
                if change < -3:  # Dip buy
                    opportunities.append({
                        "symbol": symbol,
                        "action": "BUY",
                        "price": price,
                        "change": change / 100,
                        "confidence": min(abs(change) / 20, 0.9),
                        "source": "real"
                    })
                elif change > 5:  # Profit take
                    opportunities.append({
                        "symbol": symbol,
                        "action": "SELL",
                        "price": price,
                        "change": change / 100,
                        "confidence": min(change / 30, 0.8),
                        "source": "real"
                    })
            
            if opportunities:
                return opportunities
        
        # Fallback to mock
        prices = self.get_current_prices()
        opportunities = []
        
        for opp in MOCK_OPPORTUNITIES:
            symbol = opp["symbol"]
            price = prices[symbol]
            
            # Simple strategy: buy on dip, sell on rip
            change_pct = (price - opp["base_price"]) / opp["base_price"]
            
            # Low price = potential buy
            if change_pct < -0.02:  # Down 2%+
                opportunities.append({
                    "symbol": symbol,
                    "action": "BUY",
                    "price": price,
                    "change": change_pct,
                    "confidence": min(abs(change_pct) * 5, 0.9)
                })
            # High price = potential sell
            elif change_pct > 0.03:  # Up 3%+
                opportunities.append({
                    "symbol": symbol,
                    "action": "SELL",
                    "price": price,
                    "change": change_pct,
                    "confidence": min(change_pct * 3, 0.8)
                })
        
        return opportunities
    
    def execute_trade(self, opportunity: Dict, amount: float = 5.0) -> bool:
        """Execute a paper trade"""
        if self.state["balance"] < amount:
            return False
        
        symbol = opportunity["symbol"]
        action = opportunity["action"]
        price = opportunity["price"]
        
        # Check if we already have this position
        current_pos = None
        for p in self.positions["positions"]:
            if p["symbol"] == symbol:
                current_pos = p
                break
        
        if action == "BUY":
            # Buy if we don't have it or add to position
            shares = amount / price
            if current_pos:
                current_pos["amount"] += shares
                current_pos["avg_price"] = (
                    (current_pos["avg_price"] * current_pos["amount"] + price * shares) / 
                    (current_pos["amount"] + shares)
                )
            else:
                self.positions["positions"].append({
                    "symbol": symbol,
                    "amount": shares,
                    "avg_price": price,
                    "entry_time": datetime.now().isoformat(),
                    "entry_price": price
                })
            self.state["balance"] -= amount
        
        elif action == "SELL" and current_pos:
            # Sell position
            proceeds = current_pos["amount"] * price
            pnl = proceeds - (current_pos["amount"] * current_pos["avg_price"])
            
            # Record trade
            self.history.append({
                "symbol": symbol,
                "action": "SELL",
                "amount": current_pos["amount"],
                "entry_price": current_pos["avg_price"],
                "exit_price": price,
                "pnl": pnl,
                "time": datetime.now().isoformat()
            })
            
            # Update stats
            self.state["total_trades"] += 1
            if pnl > 0:
                self.state["wins"] += 1
            else:
                self.state["losses"] += 1
            self.state["pnl"] += pnl
            self.state["balance"] += proceeds
            
            # Remove position
            self.positions["positions"] = [p for p in self.positions["positions"] if p["symbol"] != symbol]
        
        save_positions(self.positions)
        save_state(self.state)
        save_history(self.history)
        return True
    
    def run_cycle(self):
        """Run one trading cycle"""
        opportunities = self.find_opportunities()
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        trades_made = 0
        for opp in opportunities[:3]:  # Max 3 trades per cycle
            if opp["confidence"] > 0.3:  # Only confident trades
                if self.execute_trade(opp, amount=5.0):
                    trades_made += 1
        
        return trades_made
    
    def get_status(self):
        """Get current status"""
        prices = self.get_current_prices()
        
        # Calculate unrealized P&L
        unrealized = 0
        for p in self.positions["positions"]:
            symbol = p["symbol"]
            if symbol in prices:
                current_val = p["amount"] * prices[symbol]
                entry_val = p["amount"] * p["avg_price"]
                unrealized += current_val - entry_val
        
        total_pnl = self.state["pnl"] + unrealized
        win_rate = (self.state["wins"] / self.state["total_trades"] * 100) if self.state["total_trades"] > 0 else 0
        
        return {
            "balance": self.state["balance"],
            "positions": len(self.positions["positions"]),
            "total_trades": self.state["total_trades"],
            "wins": self.state["wins"],
            "losses": self.state["losses"],
            "win_rate": win_rate,
            "realized_pnl": self.state["pnl"],
            "unrealized_pnl": unrealized,
            "total_pnl": total_pnl,
            "current_prices": prices
        }

def run_cycle():
    """Run one cycle"""
    trader = PaperTrader()
    trades = trader.run_cycle()
    status = trader.get_status()
    return status

def status():
    """Get status"""
    trader = PaperTrader()
    return trader.get_status()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "run":
            result = run_cycle()
            print(f"Cycle complete: {result['total_trades']} trades, P&L: ${result['total_pnl']:.2f}")
        elif sys.argv[1] == "status":
            s = status()
            print(json.dumps(s, indent=2))
    else:
        s = status()
        print(f"""📊 On-Chain Paper Trading

Balance: ${s['balance']:,.2f}
Positions: {s['positions']}
Trades: {s['total_trades']} (W: {s['wins']} | L: {s['losses']})
Win Rate: {s['win_rate']:.1f}%

Realized P&L: ${s['realized_pnl']:.2f}
Unrealized P&L: ${s['unrealized_pnl']:.2f}
Total P&L: ${s['total_pnl']:.2f}
""")
