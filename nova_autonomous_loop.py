#!/usr/bin/env python3
"""
nova_autonomous_loop.py — Nova's autonomous trading loop.
Runs continuously: scan → analyze → decide → act → learn
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from nova_trading_brain import get_trading_brain, Signal
from nova_market_scanner import get_market_scanner
from nova_risk_engine import get_risk_engine
from nova_wallet_adapter import get_wallet


class AutonomousLoop:
    """Nova's autonomous trading loop."""
    
    def __init__(self):
        self.brain = get_trading_brain()
        self.scanner = get_market_scanner()
        self.risk = get_risk_engine()
        self.wallet = get_wallet()
        
        self.running = False
        self.loop_count = 0
        self.last_action = None
        self.alerts = []
        
    async def run_cycle(self) -> Dict:
        """Run one complete cycle."""
        self.loop_count += 1
        cycle_start = datetime.now()
        
        result = {
            "cycle": self.loop_count,
            "started_at": cycle_start.isoformat(),
            "actions": []
        }
        
        # Step 1: Reset daily counters
        self.risk.reset_daily()
        
        # Step 2: Scan markets
        scan_result = await self.scanner.full_scan()
        result["scan"] = scan_result
        
        # Step 3: Evaluate opportunities
        opportunities = scan_result.get("top_opportunities", [])
        
        for opp in opportunities[:3]:  # Top 3
            decision = self.brain.evaluate(opp)
            
            if decision["signal"] != Signal.HOLD.value:
                # Check risk
                trade_value = opp.get("liquidity", 0) * 0.01  # 1% of liquidity
                portfolio_value = self.wallet.get_balance() * opp.get("price", 1)
                
                risk_check = self.risk.can_trade(
                    {"value_usd": trade_value},
                    portfolio_value
                )
                
                if risk_check["approved"]:
                    action = {
                        "type": decision["signal"],
                        "token": opp.get("symbol"),
                        "confidence": decision["confidence"],
                        "reasoning": decision["reasoning"],
                        "opportunity_score": opp.get("opportunity_score")
                    }
                    result["actions"].append(action)
                    
                    # Alert user
                    self._create_alert(action)
                else:
                    result["actions"].append({
                        "type": "blocked",
                        "token": opp.get("symbol"),
                        "reason": risk_check
                    })
        
        # Step 4: Check open positions for exits
        exits = self._check_exits()
        result["exits"] = exits
        result["actions"].extend(exits)
        
        # Step 5: Record cycle
        result["completed_at"] = datetime.now().isoformat()
        result["duration_ms"] = (datetime.now() - cycle_start).total_seconds() * 1000
        
        self.last_action = result
        
        return result
    
    def _check_exits(self) -> List[Dict]:
        """Check if any positions should exit."""
        exits = []
        
        for position in self.risk.open_positions:
            current_price = position.get("current_price", 0)
            if current_price > 0:
                exit_check = self.risk.check_exit(position, current_price)
                if exit_check.get("should_exit"):
                    exits.append({
                        "type": "exit",
                        "token": position.get("symbol"),
                        "reason": exit_check["reason"],
                        "pnl": exit_check.get("pnl_pct", 0)
                    })
        
        return exits
    
    def _create_alert(self, action: Dict):
        """Create alert for user notification."""
        confidence_pct = int(action.get("confidence", 0) * 100)
        
        alert = {
            "type": action["type"],
            "message": f"{action['type'].upper()}: {action['token']} (confidence: {confidence_pct}%)",
            "reasoning": action.get("reasoning", []),
            "score": action.get("opportunity_score", 0),
            "created_at": datetime.now().isoformat()
        }
        
        self.alerts.append(alert)
        
        # Keep only last 20 alerts
        if len(self.alerts) > 20:
            self.alerts = self.alerts[-20:]
    
    async def start(self, interval_seconds: int = 60):
        """Start the autonomous loop."""
        self.running = True
        print(f"🚀 Autonomous loop started (interval: {interval_seconds}s)")
        
        while self.running:
            try:
                result = await self.run_cycle()
                
                # Log significant actions
                if result.get("actions"):
                    print(f"Cycle {self.loop_count}: {len(result['actions'])} actions")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                print(f"Loop error: {e}")
                await asyncio.sleep(30)  # Short sleep on error
    
    def stop(self):
        """Stop the autonomous loop."""
        self.running = False
        print("🛑 Autonomous loop stopped")
    
    def get_status(self) -> Dict:
        """Get loop status."""
        return {
            "running": self.running,
            "cycles": self.loop_count,
            "last_action": self.last_action,
            "alerts": self.alerts[-5:] if self.alerts else [],
            "wallet": {
                "address": self.wallet.get_address()[:10] + "..." if self.wallet.get_address() else "Not connected",
                "initialized": self.wallet.is_initialized()
            },
            "risk": self.risk.get_status()
        }


# Singleton
_autonomous_loop: Optional[AutonomousLoop] = None


def get_autonomous_loop() -> AutonomousLoop:
    """Get autonomous loop singleton."""
    global _autonomous_loop
    if _autonomous_loop is None:
        _autonomous_loop = AutonomousLoop()
    return _autonomous_loop


if __name__ == "__main__":
    loop = get_autonomous_loop()
    print(json.dumps(loop.get_status(), indent=2, default=str))
