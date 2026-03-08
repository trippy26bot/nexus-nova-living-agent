#!/usr/bin/env python3
"""
nova_signal_learner.py — Adaptive Signal Learning.
Tracks signal performance and adjusts weights over time.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class SignalLearner:
    """Learns from signal outcomes to improve accuracy."""
    
    def __init__(self):
        self.signals = []  # All logged signals
        self.outcomes = [] # All resolved outcomes
        self.module_stats = defaultdict(lambda: {
            "signals": 0,
            "wins": 0,
            "losses": 0,
            "total_gain": 0.0,
            "avg_gain": 0.0
        })
        self.path = Path(__file__).parent / "signal_learner.json"
        self._load()
    
    def _load(self):
        """Load saved data."""
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self.signals = data.get("signals", [])
                self.outcomes = data.get("outcomes", [])
            except:
                pass
    
    def _save(self):
        """Save data."""
        self.path.write_text(json.dumps({
            "signals": self.signals,
            "outcomes": self.outcomes
        }, indent=2, default=str))
    
    def log_signal(self, token: str, modules: List[str], entry_price: float):
        """Log a signal when it's generated."""
        signal = {
            "token": token,
            "modules": modules,
            "entry_price": entry_price,
            "signaled_at": datetime.now().isoformat(),
            "resolved": False
        }
        
        self.signals.append(signal)
        
        # Update module stats
        for module in modules:
            self.module_stats[module]["signals"] += 1
        
        self._save()
        
        return len(self.signals) - 1
    
    def resolve_signal(self, token: str, exit_price: float, timeframe_hours: int = 24):
        """Resolve a signal after timeframe."""
        # Find unresolved signals for this token
        for signal in self.signals:
            if signal["token"] == token and not signal.get("resolved"):
                # Calculate outcome
                entry = signal.get("entry_price", exit_price)
                gain = (exit_price - entry) / entry if entry > 0 else 0
                
                # Win if positive
                win = gain > 0
                
                outcome = {
                    "token": token,
                    "entry_price": entry,
                    "exit_price": exit_price,
                    "gain_pct": gain * 100,
                    "win": win,
                    "timeframe_hours": timeframe_hours,
                    "resolved_at": datetime.now().isoformat(),
                    "modules": signal.get("modules", [])
                }
                
                self.outcomes.append(outcome)
                signal["resolved"] = True
                
                # Update module stats
                for module in signal.get("modules", []):
                    stats = self.module_stats[module]
                    stats["total_gain"] += gain
                    if win:
                        stats["wins"] += 1
                    else:
                        stats["losses"] += 1
                    stats["avg_gain"] = stats["total_gain"] / max(1, stats["signals"])
                
                self._save()
                
                return outcome
        
        return None
    
    def get_module_weights(self) -> Dict[str, float]:
        """Calculate adaptive weights based on performance."""
        weights = {}
        
        for module, stats in self.module_stats.items():
            total = stats["signals"]
            if total == 0:
                weights[module] = 0.5  # Default
                continue
            
            win_rate = stats["wins"] / total
            avg_gain = stats["avg_gain"]
            
            # Score formula: win_rate * avg_gain
            score = win_rate * max(0, avg_gain + 1)  # +1 to make positive
            
            weights[module] = min(1.0, max(0.1, score))
        
        return weights
    
    def get_module_stats(self) -> Dict:
        """Get statistics for each module."""
        stats = {}
        
        for module, data in self.module_stats.items():
            total = data["signals"]
            if total == 0:
                continue
            
            win_rate = (data["wins"] / total) * 100 if total > 0 else 0
            
            stats[module] = {
                "signals": total,
                "wins": data["wins"],
                "losses": data["losses"],
                "win_rate": round(win_rate, 1),
                "avg_gain": round(data["avg_gain"] * 100, 1),
                "total_gain": round(data["total_gain"] * 100, 1)
            }
        
        return stats
    
    def get_overall_stats(self) -> Dict:
        """Get overall performance."""
        if not self.outcomes:
            return {"total": 0, "win_rate": 0, "avg_gain": 0}
        
        wins = sum(1 for o in self.outcomes if o.get("win"))
        total = len(self.outcomes)
        
        avg_gain = sum(o.get("gain_pct", 0) for o in self.outcomes) / total
        
        return {
            "total_signals": len(self.signals),
            "resolved": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": round((wins / total) * 100, 1) if total > 0 else 0,
            "avg_gain": round(avg_gain, 1)
        }
    
    def get_adaptive_brain_weights(self) -> Dict[str, float]:
        """Get weights to use in Nova Brain."""
        weights = self.get_module_weights()
        
        # Normalize
        total = sum(weights.values())
        if total > 0:
            return {k: v / total for k, v in weights.items()}
        
        # Default equal weights
        return {
            "launch_radar": 0.20,
            "whale_hunter": 0.25,
            "narrative_momentum": 0.15,
            "pre_pump_detector": 0.25,
            "liquidity_inflow": 0.15
        }


# Singleton
_signal_learner: Optional[SignalLearner] = None


def get_signal_learner() -> SignalLearner:
    """Get signal learner singleton."""
    global _signal_learner
    if _signal_learner is None:
        _signal_learner = SignalLearner()
    return _signal_learner


if __name__ == "__main__":
    learner = get_signal_learner()
    
    # Log test signal
    learner.log_signal("BONK", ["whale_hunter", "launch_radar"], 0.0001)
    
    # Resolve
    learner.resolve_signal("BONK", 0.00012)
    
    print("Module Stats:", learner.get_module_stats())
    print("Overall:", learner.get_overall_stats())
    print("Weights:", learner.get_adaptive_brain_weights())
