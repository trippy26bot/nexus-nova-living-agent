#!/usr/bin/env python3
"""
nova_autonomous_hunter.py — Autonomous Hunter Loop.
Ties all systems together into continuous operation.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional

from nova_launch_radar import get_launch_radar
from nova_whale_hunter import get_whale_hunter
from nova_wallet_predictor import get_wallet_predictor
from nova_dev_intelligence import get_dev_intelligence
from nova_rug_detector import get_rug_detector
from nova_narrative_momentum import get_narrative_momentum
from nova_pre_pump_detector import get_pre_pump_detector
from nova_liquidity_inflow_detector import get_liquidity_inflow_detector
from nova_exit_detector import get_exit_detector
from nova_brain import get_trading_brain
from nova_security_guard import get_security_guard
from nova_risk_engine import get_risk_engine
from nova_alerts import get_alert_system, AlertLevel


class AutonomousHunter:
    """Orchestrates all systems in continuous loop."""
    
    def __init__(self):
        # Systems
        self.launch_radar = get_launch_radar()
        self.whale_hunter = get_whale_hunter()
        self.wallet_predictor = get_wallet_predictor()
        self.dev_intel = get_dev_intelligence()
        self.rug_detector = get_rug_detector()
        self.narrative = get_narrative_momentum()
        self.pre_pump = get_pre_pump_detector()
        self.liquidity_inflow = get_liquidity_inflow_detector()
        self.exit_detector = get_exit_detector()
        self.brain = get_trading_brain()
        self.security = get_security_guard()
        self.risk = get_risk_engine()
        self.alerts = get_alert_system()
        
        # State
        self.running = False
        self.cycle_count = 0
        self.last_alerts = []
        
    async def run_cycle(self) -> Dict:
        """Run one complete hunting cycle."""
        self.cycle_count += 1
        cycle_start = datetime.now()
        
        result = {
            "cycle": self.cycle_count,
            "started_at": cycle_start.isoformat(),
            "scans": {},
            "signals": [],
            "actions": []
        }
        
        try:
            # 1. Scan for new launches
            launches = await self.launch_radar.detect_launches()
            result["scans"]["launches"] = len(launches.get("hot_launches", []))
            
            # 2. Scan for whale activity
            whales = await self.whale_hunter.scan_whales()
            result["scans"]["whale_signals"] = len(whales)
            
            # 3. Scan narratives
            narratives = await self.narrative.scan_narratives()
            result["scans"]["narratives"] = narratives.get("top_narrative")
            
            # 4. Scan for pre-pump setups
            pre_pumps = await self.pre_pump.scan_for_pre_pumps()
            result["scans"]["pre_pumps"] = len(pre_pumps)
            
            # 5. Scan for liquidity inflows
            inflows = await self.liquidity_inflow.get_major_inflows()
            result["scans"]["liquidity_inflows"] = len(inflows)
            
            # 6. Evaluate opportunities
            opportunities = []
            
            # Add launches as opportunities
            for launch in launches.get("hot_launches", [])[:3]:
                opportunities.append({
                    "type": "launch",
                    "token": launch.get("base_token"),
                    "address": launch.get("address"),
                    "score": launch.get("launch_score", 0),
                    "data": launch
                })
            
            # Add pre-pumps as opportunities
            for pp in pre_pumps[:3]:
                opportunities.append({
                    "type": "pre_pump",
                    "token": pp.get("symbol"),
                    "address": pp.get("token"),
                    "score": pp.get("pre_pump_score", 0),
                    "data": pp
                })
            
            # Add inflows as opportunities
            for inflow in inflows[:3]:
                opportunities.append({
                    "type": "liquidity_inflow",
                    "token": inflow.get("token"),
                    "score": inflow.get("change_pct", 0) * 2,
                    "data": inflow
                })
            
            # 7. Score and filter opportunities
            for opp in opportunities:
                token_data = {
                    "symbol": opp.get("token"),
                    "address": opp.get("address"),
                    "chain": "solana",
                    "score": opp.get("score", 0)
                }
                
                # Security check
                if opp.get("address"):
                    security = await self.security.verify_token(opp["address"])
                    if security["overall_verdict"] == "FAIL":
                        continue
                
                # Brain evaluation
                decision = self.brain.get_decision(token_data)
                
                if decision["final_action"] in ["BUY", "AGGRESSIVE"]:
                    signal = {
                        "type": opp["type"],
                        "token": opp["token"],
                        "score": opp["score"],
                        "decision": decision,
                        "timestamp": datetime.now().isoformat()
                    }
                    result["signals"].append(signal)
                    
                    # Alert
                    await self.alerts.send(
                        f"🚀 Signal: {opp['token']} ({opp['type']})",
                        AlertLevel.TRADE,
                        {"score": opp["score"], "action": decision["final_action"]}
                    )
            
            # 8. Check exits for open positions
            for position in self.exit_detector.get_positions():
                # Would update with real price
                # exit_check = self.exit_detector.update_price(token, current_price)
                pass
            
            result["completed_at"] = datetime.now().isoformat()
            result["duration_ms"] = int((datetime.now() - cycle_start).total_seconds() * 1000)
            
        except Exception as e:
            result["error"] = str(e)
            await self.alerts.error_alert(f"Cycle error: {e}")
        
        return result
    
    async def start(self, interval_seconds: int = 30):
        """Start autonomous hunting."""
        self.running = True
        print(f"🎯 Autonomous hunter started (interval: {interval_seconds}s)")
        
        await self.alerts.system_status("Autonomous hunter started")
        
        while self.running:
            try:
                result = await self.run_cycle()
                
                if result.get("signals"):
                    print(f"Cycle {self.cycle_count}: {len(result['signals'])} signals")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                print(f"Loop error: {e}")
                await asyncio.sleep(10)
    
    def stop(self):
        """Stop autonomous hunting."""
        self.running = False
        print("🛑 Autonomous hunter stopped")
    
    async def get_status(self) -> Dict:
        """Get hunter status."""
        return {
            "running": self.running,
            "cycles": self.cycle_count,
            "systems": {
                "launches": self.launch_radar.get_status(),
                "whales": self.whale_hunter.get_status(),
                "narratives": self.narrative.get_status(),
                "pre_pumps": self.pre_pump.get_status(),
                "liquidity": self.liquidity_inflow.get_status(),
                "exits": self.exit_detector.get_status(),
                "risk": self.risk.get_status()
            }
        }


# Singleton
_autonomous_hunter: Optional[AutonomousHunter] = None


def get_autonomous_hunter() -> AutonomousHunter:
    """Get autonomous hunter singleton."""
    global _autonomous_hunter
    if _autonomous_hunter is None:
        _autonomous_hunter = AutonomousHunter()
    return _autonomous_hunter


if __name__ == "__main__":
    import json
    hunter = get_autonomous_hunter()
    
    # Test single cycle
    result = asyncio.run(hunter.run_cycle())
    print(json.dumps(result, indent=2, default=str))
