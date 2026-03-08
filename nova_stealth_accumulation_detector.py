#!/usr/bin/env python3
"""
nova_stealth_accumulation_detector.py — Stealth Accumulation Detector.
Detects insiders loading slowly to avoid detection.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class StealthAccumulationDetector:
    """Detects stealth accumulation patterns."""
    
    def __init__(self):
        self.accumulations = defaultdict(list)  # token -> accumulation events
        self.window_minutes = 60  # Time window for stealth detection
        self.min_transactions = 3  # Minimum buys to qualify
        self.path = Path(__file__).parent
    
    def record_buy(self, wallet: str, token: str, amount: float, timestamp: datetime = None):
        """Record a buy transaction."""
        if timestamp is None:
            timestamp = datetime.now()
        
        event = {
            "wallet": wallet,
            "token": token,
            "amount": amount,
            "timestamp": timestamp.isoformat()
        }
        
        self.accumulations[token].append(event)
        
        # Clean old events
        self._clean_old_events(token)
    
    def _clean_old_events(self, token: str):
        """Remove events outside the window."""
        cutoff = datetime.now() - timedelta(minutes=self.window_minutes)
        
        self.accumulations[token] = [
            e for e in self.accumulations[token]
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
    
    def detect_stealth(self, token: str) -> Dict:
        """Detect stealth accumulation pattern."""
        events = self.accumulations.get(token, [])
        
        if len(events) < self.min_transactions:
            return {"detected": False, "reason": "insufficient_transactions"}
        
        # Group by wallet
        wallet_events = defaultdict(list)
        for event in events:
            wallet_events[event["wallet"]].append(event)
        
        # Calculate metrics
        unique_wallets = len(wallet_events)
        total_volume = sum(e["amount"] for e in events)
        
        # Check time distribution (stealth = spread out)
        timestamps = [datetime.fromisoformat(e["timestamp"]) for e in events]
        if timestamps:
            time_span = (max(timestamps) - min(timestamps)).total_seconds() / 60
            avg_interval = time_span / max(1, len(events) - 1)
        else:
            time_span = 0
            avg_interval = 0
        
        # Detect if coordinated (same cluster buying over time)
        # Stealth pattern: buys spread over time, not all at once
        is_stealth = (
            unique_wallets >= 2 and
            time_span > 10 and  # At least 10 min apart
            avg_interval > 3    # Average 3+ min between buys
        )
        
        # Calculate stealth score
        stealth_score = 0
        
        # More wallets = higher score
        if unique_wallets >= 5:
            stealth_score += 40
        elif unique_wallets >= 3:
            stealth_score += 30
        elif unique_wallets >= 2:
            stealth_score += 20
        
        # Spread out timing = higher score
        if time_span > 30:
            stealth_score += 30
        elif time_span > 15:
            stealth_score += 20
        elif time_span > 5:
            stealth_score += 10
        
        # Volume consistency (not one huge buy)
        if events:
            amounts = [e["amount"] for e in events]
            avg_amount = sum(amounts) / len(amounts)
            max_amount = max(amounts)
            
            # Stealth = similar sized buys, not one whale
            if max_amount < avg_amount * 3:
                stealth_score += 20
        
        # Determine if detected
        if stealth_score >= 50:
            detection = "strong_stealth"
            action = "aggressive"
        elif stealth_score >= 35:
            detection = "moderate_stealth"
            action = "normal"
        else:
            detection = "none"
            action = "watch"
        
        return {
            "detected": detection != "none",
            "pattern": detection,
            "stealth_score": round(stealth_score, 1),
            "action": action,
            "unique_wallets": unique_wallets,
            "total_transactions": len(events),
            "total_volume": round(total_volume, 2),
            "time_span_minutes": round(time_span, 1),
            "avg_interval_minutes": round(avg_interval, 1),
            "wallets": list(wallet_events.keys()),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_accumulation_wallets(self, token: str) -> List[str]:
        """Get wallets involved in accumulation."""
        events = self.accumulations.get(token, [])
        return list(set(e["wallet"] for e in events))
    
    def calculate_cluster_accumulation(self, token: str, cluster_members: List[str]) -> Dict:
        """Calculate accumulation specific to a cluster."""
        events = self.accumulations.get(token, [])
        
        cluster_events = [e for e in events if e["wallet"] in cluster_members]
        
        if not cluster_events:
            return {"detected": False, "reason": "no_cluster_activity"}
        
        # Calculate cluster metrics
        total_volume = sum(e["amount"] for e in cluster_events)
        unique_wallets = len(set(e["wallet"] for e in cluster_events))
        
        return {
            "detected": unique_wallets >= 2,
            "cluster_size": len(cluster_members),
            "active_in_cluster": unique_wallets,
            "cluster_volume": round(total_volume, 2),
            "cluster_buys": len(cluster_events)
        }
    
    def get_status(self) -> Dict:
        """Get detector status."""
        return {
            "tracked_tokens": len(self.accumulations),
            "window_minutes": self.window_minutes,
            "min_transactions": self.min_transactions
        }


# Singleton
_stealth_detector: Optional[StealthAccumulationDetector] = None


def get_stealth_detector() -> StealthAccumulationDetector:
    """Get stealth accumulation detector singleton."""
    global _stealth_detector
    if _stealth_detector is None:
        _stealth_detector = StealthAccumulationDetector()
    return _stealth_detector


if __name__ == "__main__":
    detector = get_stealth_detector()
    
    # Test
    now = datetime.now()
    detector.record_buy("wallet_A", "TOKEN_X", 100, now)
    detector.record_buy("wallet_B", "TOKEN_X", 150, now + timedelta(minutes=5))
    detector.record_buy("wallet_C", "TOKEN_X", 80, now + timedelta(minutes=12))
    
    result = detector.detect_stealth("TOKEN_X")
    print(json.dumps(result, indent=2))
