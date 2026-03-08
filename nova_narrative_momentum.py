#!/usr/bin/env python3
"""
nova_narrative_momentum.py — Narrative Momentum Engine.
Detects capital rotation between sectors.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class NarrativeMomentum:
    """Tracks narrative momentum and capital rotation."""
    
    # Define narratives with associated tokens
    NARRATIVES = {
        "ai_tokens": {
            "tokens": ["fet", "agix", "render", "rnr", "ocean", "singularity", "numeraire", "cortex", "ai16z", "goat"],
            "weight": 0.3
        },
        "memecoins": {
            "tokens": ["bonk", "wif", "popcat", "pepe", "dogwifhat", "brett", "moodeng", "neiro", "fwog", "act"],
            "weight": 0.25
        },
        "gaming": {
            "tokens": ["imx", "gala", "axs", "sand", "mana", "enjin", "flow", "illuvium", "gmr"],
            "weight": 0.2
        },
        "layer2": {
            "tokens": ["arb", "op", "base", "matic", "avax", "scroll", "starknet", "zk", "blast"],
            "weight": 0.25
        },
        "defi": {
            "tokens": ["uni", "aave", "curve", "sushi", "bal", "comp", "maker", "snx", "pendle"],
            "weight": 0.2
        },
        "solana_ecosystem": {
            "tokens": ["sol", "jup", "bonk", "wif", "jto", "hana", "hnt", "msol", "fsd"],
            "weight": 0.25
        },
        "bitcoin_layer2": {
            "tokens": ["stx", "ordinals", "rune", "kas", "sats", "ordi", "atom"],
            "weight": 0.2
        },
        "rwa": {
            "tokens": ["polymesh", "ondo", "propy", "realio", "cfg", "tru"],
            "weight": 0.15
        },
        "depins": {
            "tokens": ["hnt", "iota", "helium", "render", "filecoin", "arweave", "livepeer"],
            "weight": 0.2
        }
    }
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com"
        self.history = []  # Historical momentum data
    
    async def scan_narratives(self) -> Dict:
        """Scan all narratives for momentum."""
        url = f"{self.dexscreener_url}/token-boosts/top/v1"
        
        # Group volume by narrative
        narrative_volume = defaultdict(lambda: {"volume": 0, "liquidity": 0, "tokens": []})
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tokens = data.get("tokens", [])
                        
                        for token in tokens:
                            symbol = token.get("baseToken", {}).get("symbol", "").lower()
                            volume = token.get("volume", {}).get("h24", 0)
                            liquidity = token.get("liquidity", {}).get("usd", 0)
                            
                            # Match to narratives
                            for narrative, config in self.NARRATIVES.items():
                                for token_sym in config["tokens"]:
                                    if token_sym in symbol:
                                        narrative_volume[narrative]["volume"] += volume
                                        narrative_volume[narrative]["liquidity"] += liquidity
                                        narrative_volume[narrative]["tokens"].append({
                                            "symbol": symbol,
                                            "volume": volume,
                                            "liquidity": liquidity
                                        })
                                        break
        except Exception as e:
            print(f"Narrative scan error: {e}")
        
        # Calculate momentum scores
        momentum = {}
        
        for narrative, data in narrative_volume.items():
            if data["volume"] == 0:
                continue
            
            vol = data["volume"]
            liq = data["liquidity"]
            
            # Momentum score based on volume and liquidity
            score = (vol / 1000000 * 50) + (liq / 1000000 * 30)
            
            momentum[narrative] = {
                "score": round(score, 1),
                "volume": vol,
                "liquidity": liq,
                "token_count": len(data["tokens"]),
                "top_tokens": sorted(data["tokens"], key=lambda x: x["volume"], reverse=True)[:5]
            }
        
        # Sort by score
        sorted_narratives = sorted(momentum.items(), key=lambda x: x[1]["score"], reverse=True)
        
        # Calculate rotation
        rotation = self._calculate_rotation(momentum)
        
        result = {
            "scanned_at": datetime.now().isoformat(),
            "momentum": momentum,
            "ranking": [{"narrative": n, "score": s["score"]} for n, s in sorted_narratives[:5]],
            "rotation": rotation,
            "top_narrative": sorted_narratives[0][0] if sorted_narratives else None
        }
        
        self.history.append(result)
        
        return result
    
    def _calculate_rotation(self, current: Dict) -> Dict:
        """Calculate capital rotation between narratives."""
        if len(self.history) < 2:
            return {"rotation_detected": False}
        
        # Compare with previous scan
        previous = self.history[-1].get("momentum", {})
        
        rotations = []
        
        for narrative in current:
            curr_score = current[narrative].get("score", 0)
            prev_score = previous.get(narrative, {}).get("score", 0)
            
            if prev_score > 0:
                change = ((curr_score - prev_score) / prev_score) * 100
                
                if abs(change) > 20:  # 20% change threshold
                    rotations.append({
                        "narrative": narrative,
                        "change_pct": round(change, 1),
                        "direction": "rising" if change > 0 else "falling"
                    })
        
        # Sort by absolute change
        rotations.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        
        return {
            "rotation_detected": len(rotations) > 0,
            "rotations": rotations[:3]
        }
    
    def get_momentum_signals(self) -> List[Dict]:
        """Get actionable momentum signals."""
        if not self.history:
            return []
        
        latest = self.history[-1]
        momentum = latest.get("momentum", {})
        
        signals = []
        
        for narrative, data in momentum.items():
            score = data.get("score", 0)
            
            if score >= 50:
                signals.append({
                    "narrative": narrative,
                    "signal": "strong_momentum",
                    "score": score,
                    "action": "accumulate"
                })
            elif score >= 30:
                signals.append({
                    "narrative": narrative,
                    "signal": "building",
                    "score": score,
                    "action": "watch"
                })
        
        # Add rotation signals
        rotation = latest.get("rotation", {})
        if rotation.get("rotation_detected"):
            for r in rotation.get("rotations", []):
                if r["direction"] == "rising":
                    signals.append({
                        "narrative": r["narrative"],
                        "signal": "rotation_in",
                        "change_pct": r["change_pct"],
                        "action": "accumulate"
                    })
        
        return signals
    
    def get_status(self) -> Dict:
        """Get engine status."""
        return {
            "narratives_tracked": len(self.NARRATIVES),
            "scans_completed": len(self.history),
            "latest_scan": self.history[-1]["scanned_at"] if self.history else None
        }


# Singleton
_narrative_momentum: Optional[NarrativeMomentum] = None


def get_narrative_momentum() -> NarrativeMomentum:
    """Get narrative momentum singleton."""
    global _narrative_momentum
    if _narrative_momentum is None:
        _narrative_momentum = NarrativeMomentum()
    return _narrative_momentum


if __name__ == "__main__":
    import json
    engine = get_narrative_momentum()
    result = asyncio.run(engine.scan_narratives())
    print(json.dumps(result, indent=2, default=str))
