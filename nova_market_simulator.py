#!/usr/bin/env python3
"""
nova_market_simulator.py — Market Simulation Engine.
Simulates price outcomes before trading.
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class MarketSimulator:
    """Simulates market outcomes for trading decisions."""
    
    def __init__(self):
        self.scenarios_run = 0
        self.paths_per_scenario = 500
        
    def simulate(self, token: str, signal_data: Dict) -> Dict:
        """Run market simulation for a token."""
        
        # Input parameters
        cluster_size = signal_data.get("cluster_size", 0)
        liquidity = signal_data.get("liquidity", 0)
        volume = signal_data.get("volume_24h", 0)
        whale_buys = signal_data.get("whale_buys", [])
        stealth_mode = signal_data.get("stealth_detected", False)
        
        # Generate price paths
        price_paths = self._generate_paths(
            cluster_size=cluster_size,
            liquidity=liquidity,
            volume=volume,
            whale_buys=whale_buys,
            stealth_mode=stealth_mode
        )
        
        # Analyze outcomes
        analysis = self._analyze_paths(price_paths)
        
        # Calculate expected value
        expected_value = self._calculate_expected_value(price_paths)
        
        # Determine trade decision
        decision = self._make_decision(analysis, expected_value)
        
        self.scenarios_run += 1
        
        return {
            "token": token,
            "scenarios": self.paths_per_scenario,
            "analysis": analysis,
            "expected_value": expected_value,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_paths(self, cluster_size: int, liquidity: float, 
                      volume: float, whale_buys: List, stealth_mode: bool) -> List[Dict]:
        """Generate simulated price paths."""
        paths = []
        
        # Base probability factors
        base_bull = 0.3  # 30% base pump probability
        
        # Cluster strength bonus
        cluster_bonus = min(0.4, cluster_size * 0.08)
        
        # Liquidity bonus (liquidity = easier to pump)
        if liquidity > 200000:
            liq_bonus = 0.15
        elif liquidity > 100000:
            liq_bonus = 0.10
        elif liquidity > 50000:
            liq_bonus = 0.05
        else:
            liq_bonus = -0.10
        
        # Volume activity bonus
        vol_ratio = volume / max(liquidity, 1)
        if vol_ratio > 2:
            vol_bonus = 0.15
        elif vol_ratio > 1:
            vol_bonus = 0.10
        else:
            vol_bonus = 0.0
        
        # Stealth bonus (insiders know something)
        stealth_bonus = 0.20 if stealth_mode else 0.0
        
        # Whale count bonus
        whale_bonus = min(0.25, len(whale_buys) * 0.08)
        
        # Calculate pump probability
        pump_prob = base_bull + cluster_bonus + liq_bonus + vol_bonus + stealth_bonus + whale_bonus
        pump_prob = max(0.1, min(0.9, pump_prob))
        
        # Generate paths
        for _ in range(self.paths_per_scenario):
            # Determine if pump happens
            if random.random() < pump_prob:
                # Pump scenario
                pump_magnitude = random.expovariate(0.02)  # Mean 50% pump
                pump_magnitude = min(pump_magnitude, 5.0)  # Cap at 500%
                
                # Time to peak (minutes)
                time_to_peak = random.expovariate(0.03)  # Mean ~33 min
                time_to_peak = min(time_to_peak, 180)
                
                # Decline after peak
                decline = random.uniform(0.1, 0.6)
                
                # Generate path points
                path = {
                    "outcome": "pump",
                    "peak_change": pump_magnitude * 100,
                    "final_change": pump_magnitude * (1 - decline) * 100,
                    "time_to_peak": time_to_peak,
                    "scenario": self._classify_scenario(pump_magnitude, decline)
                }
            else:
                # Dump or sideways
                decline = random.uniform(-0.8, 0.2)
                
                path = {
                    "outcome": "dump" if decline < -0.1 else "sideways",
                    "peak_change": 0,
                    "final_change": decline * 100,
                    "time_to_peak": 0,
                    "scenario": "dump" if decline < -0.1 else "sideways"
                }
            
            paths.append(path)
        
        return paths
    
    def _classify_scenario(self, pump_magnitude: float, decline: float) -> str:
        """Classify the pump scenario."""
        if pump_magnitude > 3:
            return "mega_pump"
        elif pump_magnitude > 1.5:
            return "big_pump"
        elif pump_magnitude > 0.5:
            return "moderate_pump"
        else:
            return "small_pump"
    
    def _analyze_paths(self, paths: List[Dict]) -> Dict:
        """Analyze simulated paths."""
        
        # Count outcomes
        outcomes = defaultdict(int)
        for path in paths:
            outcomes[path["outcome"]] += 1
        
        # Calculate average changes by outcome
        pump_paths = [p for p in paths if p["outcome"] == "pump"]
        dump_paths = [p for p in paths if p["outcome"] == "dump"]
        
        avg_pump = sum(p["final_change"] for p in pump_paths) / max(1, len(pump_paths))
        avg_dump = sum(p["final_change"] for p in dump_paths) / max(1, len(dump_paths))
        
        # Calculate probability of each outcome
        total = len(paths)
        
        return {
            "total_scenarios": total,
            "pump_probability": (outcomes["pump"] / total) * 100,
            "dump_probability": (outcomes["dump"] / total) * 100,
            "sideways_probability": (outcomes["sideways"] / total) * 100,
            "avg_pump_return": avg_pump,
            "avg_dump_return": avg_dump,
            "pump_count": outcomes["pump"],
            "dump_count": outcomes["dump"]
        }
    
    def _calculate_expected_value(self, paths: List[Dict]) -> float:
        """Calculate expected value of trade."""
        total = len(paths)
        
        if total == 0:
            return 0
        
        # Weight by probability
        ev = 0
        for path in paths:
            ev += path["final_change"]
        
        return ev / total
    
    def _make_decision(self, analysis: Dict, expected_value: float) -> Dict:
        """Make trading decision based on simulation."""
        
        pump_prob = analysis["pump_probability"]
        ev = expected_value
        
        # Decision logic
        if pump_prob >= 70 and ev >= 50:
            action = "AGGRESSIVE"
            size = "4-5%"
        elif pump_prob >= 50 and ev >= 30:
            action = "BUY"
            size = "2-3%"
        elif pump_prob >= 35 and ev >= 10:
            action = "WATCH"
            size = "1%"
        else:
            action = "AVOID"
            size = "0%"
        
        return {
            "action": action,
            "position_size": size,
            "reason": f"pump_prob={pump_prob:.0f}%, ev={ev:.1f}%"
        }
    
    def run_scenario_analysis(self, signal_data: Dict) -> Dict:
        """Run detailed scenario analysis."""
        
        # Run multiple simulations
        results = []
        for _ in range(10):
            result = self.simulate(signal_data.get("token", "UNKNOWN"), signal_data)
            results.append(result["analysis"]["pump_probability"])
        
        # Average results
        avg_pump_prob = sum(results) / len(results)
        
        return {
            "simulations": len(results),
            "avg_pump_probability": round(avg_pump_prob, 1),
            "confidence": "high" if abs(avg_pump_prob - results[0]) < 5 else "medium"
        }
    
    def get_status(self) -> Dict:
        """Get simulator status."""
        return {
            "scenarios_run": self.scenarios_run,
            "paths_per_scenario": self.paths_per_scenario,
            "total_simulations": self.scenarios_run * self.paths_per_scenario
        }


# Singleton
_market_simulator: Optional[MarketSimulator] = None


def get_market_simulator() -> MarketSimulator:
    """Get market simulator singleton."""
    global _market_simulator
    if _market_simulator is None:
        _market_simulator = MarketSimulator()
    return _market_simulator


if __name__ == "__main__":
    sim = get_market_simulator()
    
    test_signal = {
        "token": "TEST",
        "cluster_size": 4,
        "liquidity": 150000,
        "volume_24h": 80000,
        "whale_buys": ["w1", "w2", "w3"],
        "stealth_detected": True
    }
    
    result = sim.simulate("TEST", test_signal)
    print(json.dumps(result, indent=2))
