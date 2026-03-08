#!/usr/bin/env python3
"""
nova_narrative_detector.py — Narrative Detection Engine.
Detects which crypto narratives are heating up.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class NarrativeDetector:
    """Detects market narratives before they go mainstream."""
    
    # Narrative keywords and associated tokens
    NARRATIVES = {
        "ai_tokens": {
            "keywords": ["ai", "artificial intelligence", "machine learning", "neural", "gpt", "agi", "agi", "claude", "chatgpt"],
            "tokens": ["fet", "agix", "render", "rnr", "ocean", "singularity", "numeraire", "cortex"],
            "weight": 0.4
        },
        "memecoins": {
            "keywords": ["meme", "dog", "pepe", "shiba", "bonk", "wif", "bob", "mog"],
            "tokens": ["bonk", "wif", "popcat", "pepe", "dogwifhat", "brett", "moodeng"],
            "weight": 0.3
        },
        "gaming": {
            "keywords": ["game", "gaming", "play to earn", "nft game", "metaverse", "gamer"],
            "tokens": ["imx", "gala", "axs", "sand", "mana", "enjin", "flow"],
            "weight": 0.2
        },
        "layer2": {
            "keywords": ["layer2", "l2", "rollup", "arbitrum", "optimism", "base", "zk"],
            "tokens": ["arb", "op", "base", "matic", "avax", "scroll", "starknet"],
            "weight": 0.3
        },
        "defi": {
            "keywords": ["defi", "decentralized exchange", "swap", "yield", "staking", "liquidity"],
            "tokens": ["uni", "aave", "curve", "sushi", "bal", "comp", "maker"],
            "weight": 0.2
        },
        "rwa": {
            "keywords": ["rwa", "real world assets", "tokenized", "real estate", "bonds"],
            "tokens": ["polymesh", "ondo", "propy", "realio"],
            "weight": 0.2
        },
        "depins": {
            "keywords": ["depin", "decentralized physical", "infrastructure", "wireless", "hotspot"],
            "tokens": ["hnt", "iota", "helium", "drone", "render"],
            "weight": 0.2
        },
        "solana_ecosystem": {
            "keywords": ["solana", "sol", "solanad", "jupiter", "raydium", "orca"],
            "tokens": ["sol", "jup", "bonk", "wif", "jto", "hana"],
            "weight": 0.25
        },
        "bitcoin_layer2": {
            "keywords": ["ordinals", "bitcoin l2", "stacks", "lightning", "runes", "brc-20"],
            "tokens": ["stx", "ordinals", "rune", "kas", "sats"],
            "weight": 0.25
        },
        "privacy": {
            "keywords": ["privacy", "anonymous", "zksync", "tornado", "monero", "zec"],
            "tokens": ["zec", "xmr", "zrx", "penumbra"],
            "weight": 0.15
        }
    }
    
    def __init__(self):
        self.narrative_scores = {}
        self.history = []
    
    async def scan_dexscreener(self) -> Dict:
        """Scan Dexscreener for narrative signals."""
        url = "https://api.dexscreener.com/token-boosts/top/v1"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("tokens", [])
        except Exception as e:
            print(f"Dexscreener scan error: {e}")
        
        return []
    
    def analyze_tokens(self, tokens: List[Dict]) -> Dict:
        """Analyze tokens for narrative patterns."""
        narrative_counts = defaultdict(lambda: {"count": 0, "volume": 0, "liquidity": 0, "tokens": []})
        
        for token in tokens:
            symbol = token.get("baseToken", {}).get("symbol", "").lower()
            name = token.get("baseToken", {}).get("name", "").lower()
            volume = token.get("volume", {}).get("h24", 0)
            liquidity = token.get("liquidity", {}).get("usd", 0)
            
            for narrative, config in self.NARRATIVES.items():
                # Check tokens
                for token_symbol in config["tokens"]:
                    if token_symbol in symbol or token_symbol in name:
                        narrative_counts[narrative]["count"] += 1
                        narrative_counts[narrative]["volume"] += volume
                        narrative_counts[narrative]["liquidity"] += liquidity
                        narrative_counts[narrative]["tokens"].append({
                            "symbol": symbol,
                            "volume": volume,
                            "liquidity": liquidity
                        })
                        break
                
                # Check keywords
                text = f"{symbol} {name}"
                for keyword in config["keywords"]:
                    if keyword in text:
                        narrative_counts[narrative]["count"] += 1
                        break
        
        # Calculate scores
        scores = {}
        for narrative, data in narrative_counts.items():
            if data["count"] == 0:
                continue
            
            weight = self.NARRATIVES[narrative]["weight"]
            
            # Score formula
            score = (
                data["count"] * 10 * weight +
                min(data["volume"] / 100000, 30) * weight +
                min(data["liquidity"] / 500000, 30) * weight
            )
            
            scores[narrative] = {
                "score": round(score, 1),
                "token_count": data["count"],
                "total_volume": data["volume"],
                "total_liquidity": data["liquidity"],
                "top_tokens": sorted(data["tokens"], key=lambda x: x.get("volume", 0), reverse=True)[:5],
                "weight": weight
            }
        
        return scores
    
    async def detect_narratives(self) -> Dict:
        """Run full narrative detection."""
        tokens = await self.scan_dexscreener()
        
        scores = self.analyze_tokens(tokens)
        
        # Sort by score
        sorted_narratives = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        # Get top narrative
        top_narrative = None
        if sorted_narratives:
            top_narrative = sorted_narratives[0][0]
        
        result = {
            "detected_at": datetime.now().isoformat(),
            "tokens_analyzed": len(tokens),
            "narratives": scores,
            "top_narrative": top_narrative,
            "ranking": [{"narrative": n, "score": s["score"]} for n, s in sorted_narratives[:5]]
        }
        
        self.history.append(result)
        
        return result
    
    def get_hot_narratives(self, threshold: float = 30) -> List[str]:
        """Get narratives above threshold."""
        if not self.history:
            return []
        
        latest = self.history[-1]
        hot = [
            n for n, s in latest["narratives"].items()
            if s["score"] >= threshold
        ]
        
        return sorted(hot, key=lambda x: latest["narratives"][x]["score"], reverse=True)
    
    def get_trending_tokens(self, narrative: str) -> List[Dict]:
        """Get trending tokens for a specific narrative."""
        if not self.history:
            return []
        
        latest = self.history[-1]
        
        if narrative in latest["narratives"]:
            return latest["narratives"][narrative].get("top_tokens", [])
        
        return []
    
    def get_status(self) -> Dict:
        """Get detector status."""
        return {
            "narratives_tracked": len(self.NARRATIVES),
            "scans_completed": len(self.history),
            "latest_scan": self.history[-1]["detected_at"] if self.history else None
        }


# Singleton
_narrative_detector: Optional[NarrativeDetector] = None


def get_narrative_detector() -> NarrativeDetector:
    """Get narrative detector singleton."""
    global _narrative_detector
    if _narrative_detector is None:
        _narrative_detector = NarrativeDetector()
    return _narrative_detector


if __name__ == "__main__":
    import json
    detector = get_narrative_detector()
    result = asyncio.run(detector.detect_narratives())
    print(json.dumps(result, indent=2, default=str))
