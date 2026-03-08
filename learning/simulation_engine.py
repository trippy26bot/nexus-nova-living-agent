"""
Simulation Engine - Test strategies before real trading
"""
import random

class SimulationEngine:
    def __init__(self):
        self.name = "simulation"
    
    def run(self, strategy_func, historical_data, initial_balance=10000):
        """
        Backtest a strategy function against historical data.
        strategy_func takes (price_data) and returns "BUY", "SELL", or "HOLD"
        """
        balance = initial_balance
        position = 0
        trades = 0
        wins = 0
        losses = 0
        
        for i, candle in enumerate(historical_data):
            decision = strategy_func(candle)
            
            if decision == "BUY" and position == 0:
                # Buy with 10% of balance
                shares = (balance * 0.1) / candle.get("close", 1)
                position = shares
                balance -= shares * candle.get("close", 0)
                trades += 1
            
            elif decision == "SELL" and position > 0:
                # Sell position
                proceeds = position * candle.get("close", 0)
                pnl = proceeds - (position * candle.get("open", 0))
                
                if pnl > 0:
                    wins += 1
                else:
                    losses += 1
                
                balance += proceeds
                position = 0
                trades += 1
        
        # Close any remaining position
        if position > 0 and historical_data:
            final_price = historical_data[-1].get("close", 0)
            balance += position * final_price
        
        final_pnl = balance - initial_balance
        
        return {
            "initial_balance": initial_balance,
            "final_balance": balance,
            "pnl": final_pnl,
            "pnl_percent": (final_pnl / initial_balance) * 100,
            "trades": trades,
            "wins": wins,
            "losses": losses,
            "win_rate": wins / trades if trades > 0 else 0
        }
    
    def quick_test(self, market_data, decision):
        """
        Quick sanity check before executing a trade.
        Returns: (should_execute, reason)
        """
        # Check basic risk factors
        risk_level = market_data.get("risk_level", 0)
        volatility = market_data.get("volatility", 0)
        
        if risk_level > 0.8:
            return False, "risk too high"
        
        if volatility > 3:
            return False, "volatility too high"
        
        if decision == "HOLD":
            return False, "brain said hold"
        
        return True, "passed checks"
    
    def monte_carlo(self, strategy_func, historical_data, iterations=100):
        """
        Run multiple simulations with random variations
        """
        results = []
        
        for _ in range(iterations):
            # Add small random variations
            varied_data = []
            for candle in historical_data:
                varied = candle.copy()
                if "close" in varied:
                    varied["close"] *= random.uniform(0.98, 1.02)
                varied_data.append(varied)
            
            result = self.run(strategy_func, varied_data)
            results.append(result["pnl_percent"])
        
        return {
            "mean_pnl": sum(results) / len(results),
            "min_pnl": min(results),
            "max_pnl": max(results),
            "std_dev": self._std(results)
        }
    
    def _std(self, values):
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
