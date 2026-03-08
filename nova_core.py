#!/usr/bin/env python3
"""
nova_core.py — Unified Trading Brain.
Wires all modules together into one execution loop.
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Optional

# Import all modules
from nova_market_regime import get_market_regime
from nova_whale_hunter import get_whale_hunter
from nova_order_flow import get_order_flow
from nova_liquidity_mapping import get_liquidity_mapper
from nova_risk_engine import get_risk_engine
from nova_virtual_trader import get_virtual_trader
from nova_alerts import get_alert_system
from nova_wallet_dna import get_wallet_dna
from nova_predictive_flow import get_predictive_flow
from nova_trap_detector import get_trap_detector
from nova_strategy_tournament import get_strategy_tournament


class NovaCore:
    """Unified trading brain - wires all modules together."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.running = False
        self.cycle_count = 0
        self.last_trade_time = None
        
        # Initialize modules
        self.market_regime = get_market_regime()
        self.whale_hunter = get_whale_hunter()
        self.order_flow = get_order_flow()
        self.liquidity = get_liquidity_mapper()
        self.risk = get_risk_engine()
        self.paper = get_virtual_trader(10000)
        self.alerts = get_alert_system()
        self.wallet_dna = get_wallet_dna()
        self.predictive = get_predictive_flow()
        self.trap = get_trap_detector()
        self.tournament = get_strategy_tournament()
        
    async def analyze_market(self, token: str) -> Dict:
        """Run full market analysis."""
        
        # Get all signals
        regime = self.market_regime.analyze({})
        whales = await self.whale_hunter.scan_whales()
        flow = self.order_flow.get_flow_signal({}, [])
        liq = self.liquidity.get_liquidity_signal(token, 0.001, [], [])
        
        # Calculate combined score
        score = 0
        signals = []
        
        # Market regime
        if regime.get("regime") in ["bull", "momentum"]:
            score += 20
            signals.append("BULL_REGIME")
        
        # Whale signal
        whale_signal = "NEUTRAL"
        if whales and len(whales) > 0:
            whale_signal = "BUY"
            score += 35
            signals.append("WHALE_BUY")
        
        # Order flow
        if flow.get("signal") == "STRONG_FLOW":
            score += 25
            signals.append("ORDER_FLOW")
        
        # Liquidity
        if liq.get("signal") == "HIGH_LIQUIDITY_QUALITY":
            score += 20
            signals.append("LIQUIDITY_OK")
        
        return {
            "token": token,
            "score": score,
            "signals": signals,
            "regime": regime,
            "whales": whales,
            "order_flow": flow,
            "liquidity": liq,
            "timestamp": datetime.now().isoformat()
        }
    
    async def evaluate_trade(self, token: str, side: str) -> Dict:
        """Evaluate if trade should execute."""
        
        # Get market analysis
        analysis = await self.analyze_market(token)
        
        # Check trap detection
        trap_data = {
            "whale_exits": 0,
            "recent_sells": 0,
            "liquidity_locked": True
        }
        trap_result = self.trap.analyze(token, trap_data)
        
        # Risk check
        risk_result = self.risk.evaluate({
            "token": token,
            "side": side,
            "confidence": analysis["score"] / 100
        })
        
        # Combine evaluation
        should_trade = (
            analysis["score"] >= 60 and
            trap_result["action"] != "BLOCK" and
            risk_result["approved"]
        )
        
        return {
            "should_trade": should_trade,
            "score": analysis["score"],
            "signals": analysis["signals"],
            "trap_score": trap_result.get("trap_score", 0),
            "risk_result": risk_result,
            "analysis": analysis
        }
    
    def execute_paper_trade(self, token: str, side: str, price: float) -> Dict:
        """Execute paper trade (no real money)."""
        
        # Check cooldown
        if self.last_trade_time:
            elapsed = (datetime.now() - self.last_trade_time).seconds
            if elapsed < 600:  # 10 min cooldown
                return {"success": False, "reason": "cooldown"}
        
        # Evaluate trade
        evaluation = self.evaluate_trade(token, side)
        
        if not evaluation["should_trade"]:
            return {"success": False, "reason": "failed_evaluation"}
        
        # Execute
        if side == "BUY":
            result = self.paper.buy(token, price, 5)  # 5% position
        else:
            result = self.paper.sell(token, price)
        
        if result.get("success"):
            self.last_trade_time = datetime.now()
            
            # Alert
            self.alerts.send(f"Nova Paper Trade: {side} {token} @ {price}")
        
        return result
    
    async def run_cycle(self, token: str = "BTC") -> Dict:
        """Run one analysis cycle."""
        self.cycle_count += 1
        
        # Full analysis
        analysis = await self.analyze_market(token)
        
        # Check for entry
        if analysis["score"] >= 70:
            eval_result = await self.evaluate_trade(token, "BUY")
            
            return {
                "cycle": self.cycle_count,
                "action": "EVALUATE",
                "analysis": analysis,
                "evaluation": eval_result,
                "status": "SCAN_COMPLETE"
            }
        
        return {
            "cycle": self.cycle_count,
            "action": "WAIT",
            "analysis": analysis,
            "status": "NO_SIGNAL"
        }
    
    def get_status(self) -> Dict:
        """Get Nova status."""
        return {
            "running": self.running,
            "cycles": self.cycle_count,
            "paper_balance": self.paper.get_stats(),
            "last_trade": self.last_trade_time.isoformat() if self.last_trade_time else None
        }
    
    async def start(self, interval: int = 30):
        """Start Nova brain loop."""
        self.running = True
        
        print("🧠 Nova Core Brain Online")
        print(f"   Paper balance: ${self.paper.initial_balance:,.2f}")
        print(f"   Cycle interval: {interval}s")
        print("-" * 40)
        
        while self.running:
            try:
                result = self.run_cycle()
                
                if result.get("action") == "EVALUATE":
                    print(f"\n[Cycle {self.cycle_count}] Signal detected!")
                    print(f"   Score: {result['analysis']['score']}")
                    print(f"   Signals: {result['analysis']['signals']}")
                    
                    if result['evaluation']['should_trade']:
                        print("   → Trade APPROVED")
                    else:
                        print("   → Trade blocked")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(interval)
    
    def stop(self):
        """Stop Nova."""
        self.running = False
        print("\n🛑 Nova Core Brain Stopped")


# Singleton
_nova_core: Optional[NovaCore] = None


def get_nova_core(config: Dict = None) -> NovaCore:
    """Get Nova core singleton."""
    global _nova_core
    if _nova_core is None:
        _nova_core = NovaCore(config)
    return _nova_core


if __name__ == "__main__":
    core = get_nova_core()
    print(json.dumps(core.get_status(), indent=2))
