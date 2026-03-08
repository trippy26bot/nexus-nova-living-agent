#!/usr/bin/env python3
"""
nova_virtual_trader.py — Virtual Trading Simulator.
Tests strategies without real money.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class VirtualTrader:
    """Simulates trading without real money."""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}  # token -> position
        self.trade_history = []
        self.pnl_history = []
    
    def reset(self):
        """Reset to initial state."""
        self.balance = self.initial_balance
        self.positions = {}
        self.trade_history = []
        self.pnl_history = []
    
    def buy(self, token: str, price: float, size_pct: float = 10) -> Dict:
        """Simulate a buy."""
        size_usd = self.balance * (size_pct / 100)
        
        if size_usd > self.balance:
            return {"success": False, "reason": "insufficient_balance"}
        
        # Update balance
        self.balance -= size_usd
        
        # Calculate tokens
        tokens = size_usd / price
        
        # Record position
        self.positions[token] = {
            "entry_price": price,
            "size_usd": size_usd,
            "tokens": tokens,
            "entered_at": datetime.now().isoformat()
        }
        
        # Record trade
        self.trade_history.append({
            "action": "BUY",
            "token": token,
            "price": price,
            "size_usd": size_usd,
            "at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "token": token,
            "bought": tokens,
            "at_price": price,
            "balance": self.balance
        }
    
    def sell(self, token: str, price: float, pct: float = 100) -> Dict:
        """Simulate a sell."""
        if token not in self.positions:
            return {"success": False, "reason": "no_position"}
        
        position = self.positions[token]
        
        # Calculate sell amount
        tokens_to_sell = position["tokens"] * (pct / 100)
        usd_value = tokens_to_sell * price
        
        # Update balance
        self.balance += usd_value
        
        # Calculate PnL
        entry_value = position["entry_price"] * tokens_to_sell
        pnl = usd_value - entry_value
        pnl_pct = (pnl / entry_value) * 100 if entry_value > 0 else 0
        
        # Update position
        remaining = position["tokens"] - tokens_to_sell
        if remaining <= 0:
            del self.positions[token]
        else:
            position["tokens"] = remaining
            position["size_usd"] = remaining * price
        
        # Record trade
        self.trade_history.append({
            "action": "SELL",
            "token": token,
            "price": price,
            "size_usd": usd_value,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "at": datetime.now().isoformat()
        })
        
        # Record PnL
        self.pnl_history.append({
            "token": token,
            "pnl": pnl,
            "pnl_pct": pnl_pct
        })
        
        return {
            "success": True,
            "sold": tokens_to_sell,
            "at_price": price,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "balance": self.balance
        }
    
    def get_stats(self) -> Dict:
        """Get trading statistics."""
        if not self.pnl_history:
            return {
                "trades": 0,
                "balance": self.balance,
                "total_pnl": 0,
                "win_rate": 0
            }
        
        wins = sum(1 for p in self.pnl_history if p["pnl"] > 0)
        total = len(self.pnl_history)
        
        total_pnl = sum(p["pnl"] for p in self.pnl_history)
        
        return {
            "trades": total,
            "balance": self.balance,
            "total_pnl": total_pnl,
            "total_pnl_pct": (total_pnl / self.initial_balance) * 100,
            "wins": wins,
            "losses": total - wins,
            "win_rate": (wins / total * 100) if total > 0 else 0,
            "open_positions": len(self.positions)
        }
    
    def simulate_signal(self, token: str, action: str, price: float, 
                       confidence: float) -> Dict:
        """Simulate a trading signal."""
        # Position size based on confidence
        if confidence >= 0.85:
            size_pct = 10
        elif confidence >= 0.70:
            size_pct = 6
        elif confidence >= 0.50:
            size_pct = 3
        else:
            size_pct = 0
        
        if action == "BUY" and size_pct > 0:
            return self.buy(token, price, size_pct)
        elif action == "SELL" and token in self.positions:
            return self.sell(token, price)
        
        return {"success": False, "reason": "no_action_needed"}


# Singleton
_virtual_trader: Optional[VirtualTrader] = None


def get_virtual_trader(initial_balance: float = 10000) -> VirtualTrader:
    """Get virtual trader singleton."""
    global _virtual_trader
    if _virtual_trader is None:
        _virtual_trader = VirtualTrader(initial_balance)
    return _virtual_trader


if __name__ == "__main__":
    import random
    trader = get_virtual_trader(10000)
    
    # Simulate some trades
    for _ in range(10):
        signal = random.choice(["BUY", "SELL"])
        price = random.uniform(0.001, 0.01)
        
        if signal == "BUY":
            trader.buy("TEST", price, 10)
        else:
            trader.sell("TEST", price)
    
    print(json.dumps(trader.get_stats(), indent=2))
