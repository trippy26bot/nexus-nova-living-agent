"""
Offline Trading Simulator - Nova can trade even without internet
"""

import random
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger("OfflineSimulator")


class OfflineTradingSimulator:
    """Simulates market data and trading when offline"""
    
    def __init__(self, nova_core):
        self.nova = nova_core
        
        # Initial prices (mock)
        self.prices = {
            "BTC": 50000.0,
            "ETH": 3500.0,
            "SOL": 100.0,
            "XRP": 0.55,
            "DOGE": 0.08
        }
        
        # Positions
        self.positions = {coin: 0 for coin in self.prices}
        
        # PnL tracking
        self.pnl_history: List[Dict] = []
        self.initial_balance = 10000.0
        self.current_balance = self.initial_balance
        
        # Volatility settings
        self.volatility = 0.02  # 2% standard deviation
        
        logger.info("OfflineTradingSimulator initialized")
    
    def simulate_market(self) -> Dict[str, float]:
        """Simulate price movement (random walk)"""
        for coin in self.prices:
            # Random walk with mean reversion tendency
            change = random.gauss(0, self.volatility)
            self.prices[coin] *= (1 + change)
            
            # Keep prices reasonable
            self.prices[coin] = max(self.prices[coin] * 0.5, min(self.prices[coin] * 2, self.prices[coin]))
        
        return self.prices.copy()
    
    def execute_signal(self, signal: Dict) -> Dict:
        """Execute a trading signal"""
        coin = signal.get("coin", "BTC")
        action = signal.get("action", "HOLD")
        size = signal.get("size", 0.01)  # % of portfolio
        
        if action == "HOLD" or coin not in self.prices:
            return {"status": "ignored", "reason": "hold or invalid"}
        
        # Calculate position size
        value = self.current_balance * size
        
        if action == "BUY":
            self.positions[coin] += value / self.prices[coin]
            self.current_balance -= value
            result = {"status": "executed", "action": "BUY", "coin": coin, "value": value}
        
        elif action == "SELL":
            if self.positions[coin] > 0:
                sell_value = min(self.positions[coin] * self.prices[coin], value)
                self.positions[coin] -= sell_value / self.prices[coin]
                self.current_balance += sell_value
                result = {"status": "executed", "action": "SELL", "coin": coin, "value": sell_value}
            else:
                result = {"status": "ignored", "reason": "no position"}
        else:
            result = {"status": "ignored", "reason": "unknown action"}
        
        # Track PnL
        self.pnl_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "coin": coin,
            "balance": self.current_balance
        })
        
        return result
    
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        positions_value = sum(
            self.positions[coin] * self.prices[coin] 
            for coin in self.positions
        )
        return self.current_balance + positions_value
    
    def get_status(self) -> Dict:
        """Get simulator status"""
        portfolio_value = self.get_portfolio_value()
        pnl = portfolio_value - self.initial_balance
        pnl_pct = (pnl / self.initial_balance) * 100
        
        return {
            "mode": "OFFLINE",
            "prices": self.prices.copy(),
            "positions": self.positions.copy(),
            "balance": self.current_balance,
            "portfolio_value": portfolio_value,
            "pnl": pnl,
            "pnl_percent": pnl_pct
        }


# Global simulator
_simulator = None

def get_simulator(nova_core=None) -> OfflineTradingSimulator:
    """Get or create simulator"""
    global _simulator
    if _simulator is None and nova_core:
        _simulator = OfflineTradingSimulator(nova_core)
    return _simulator
