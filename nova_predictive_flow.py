#!/usr/bin/env python3
"""
nova_predictive_flow.py — Predictive Wallet Flow Engine.
Predicts which wallets will buy next.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class PredictiveFlow:
    """Predicts wallet behavior based on patterns."""
    
    def __init__(self):
        self.patterns = defaultdict(list)  # wallet -> known patterns
    
    def learn_pattern(self, trigger_wallet: str, response_wallet: str, 
                     time_window_minutes: int, success_count: int):
        """Learn that trigger_wallet often leads to response_wallet."""
        key = f"{trigger_wallet}->{response_wallet}"
        
        self.patterns[key].append({
            "time_window": time_window_minutes,
            "successes": success_count,
            "learned_at": datetime.now().isoformat()
        })
    
    def predict(self, trigger_wallet: str, current_time: datetime = None) -> Dict:
        """Predict which wallets will act after trigger_wallet."""
        if current_time is None:
            current_time = datetime.now()
        
        predictions = []
        
        # Find all known patterns
        for key, data in self.patterns.items():
            if key.startswith(f"{trigger_wallet}->"):
                response_wallet = key.split("->")[1]
                
                # Calculate prediction strength
                total_successes = sum(p["successes"] for p in data)
                avg_window = sum(p["time_window"] for p in data) / len(data)
                
                predictions.append({
                    "response_wallet": response_wallet,
                    "confidence": min(1.0, total_successes / 10),
                    "expected_window": round(avg_window, 1),
                    "trigger_count": total_successes
                })
        
        # Sort by confidence
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "trigger": trigger_wallet,
            "predictions": predictions[:5],
            "prediction_time": current_time.isoformat()
        }
    
    def get_cluster_cascade(self, starter_wallet: str) -> Dict:
        """Predict full cluster cascade."""
        # First layer
        first = self.predict(starter_wallet)
        
        # Second layer predictions
        second_layer = []
        for pred in first["predictions"][:3]:
            second = self.predict(pred["response_wallet"])
            second_layer.extend(second["predictions"][:2])
        
        return {
            "starter": starter_wallet,
            "first_layer": first["predictions"][:3],
            "second_layer": second_layer[:5],
            "cascade_probability": self._calculate_cascade_prob(first, second_layer)
        }
    
    def _calculate_cascade_prob(self, first: List, second: List) -> float:
        """Calculate cascade probability."""
        if not first:
            return 0.0
        
        first_prob = sum(p["confidence"] for p in first) / len(first)
        
        if not second:
            return first_prob * 0.5
        
        second_prob = sum(p["confidence"] for p in second) / len(second)
        
        return round((first_prob + second_prob * 0.5) / 1.5, 2)
    
    def analyze_flow_signal(self, wallet: str, token: str, current_price: float) -> Dict:
        """Analyze if a wallet buy predicts more buys."""
        prediction = self.predict(wallet)
        
        if not prediction["predictions"]:
            return {
                "cascade_detected": False,
                "confidence": 0,
                "action": "STANDALONE"
            }
        
        # Calculate cascade confidence
        cascade = self.get_cluster_cascade(wallet)
        prob = cascade["cascade_probability"]
        
        if prob >= 0.7:
            action = "STRONG_CASCADE"
        elif prob >= 0.4:
            action = "MODERATE_CASCADE"
        else:
            action = "LOW_CASCADE"
        
        return {
            "cascade_detected": prob > 0.3,
            "confidence": prob,
            "action": action,
            "predictions": prediction["predictions"][:3],
            "cascade": cascade
        }


# Singleton
_predictive_flow: Optional[PredictiveFlow] = None


def get_predictive_flow() -> PredictiveFlow:
    """Get predictive flow singleton."""
    global _predictive_flow
    if _predictive_flow is None:
        _predictive_flow = PredictiveFlow()
    return _predictive_flow


if __name__ == "__main__":
    flow = get_predictive_flow()
    
    # Learn pattern
    flow.learn_pattern("wallet_A", "wallet_B", 2, 8)
    flow.learn_pattern("wallet_A", "wallet_C", 3, 6)
    flow.learn_pattern("wallet_B", "wallet_D", 1, 5)
    
    result = flow.analyze_flow_signal("wallet_A", "TOKEN", 0.001)
    print(json.dumps(result, indent=2))
