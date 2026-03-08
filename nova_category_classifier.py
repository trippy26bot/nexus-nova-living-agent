#!/usr/bin/env python3
"""
nova_category_classifier.py — Market Category Classifier.
Automatically categorizes markets.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class CategoryClassifier:
    """Classifies markets into categories."""
    
    # Category keywords
    CATEGORIES = {
        "meme_coin": ["dog", "cat", "frog", "pepe", "shiba", "doge", "bonk", "wif", "goat", "meme"],
        "ai_token": ["ai", "openai", "anthropic", "machine", "neural", "gpt", "ai16z", "render", "bittensor", "fetch"],
        "gaming": ["game", "gaming", "play", "meta", "illuvium", "axie", "sandbox", "decentraland", "gala", "enjin"],
        "defi": ["swap", "lend", "borrow", "yield", "farm", "stake", "pool", "dex", "uniswap", "aave", "curve"],
        "layer1": ["bitcoin", "ethereum", "solana", "avalanche", "polkadot", "cardano", "algorand", "near", "aptos"],
        "layer2": ["arbitrum", "optimism", "base", "polygon", "zksync", "starknet", "linea", "blast"],
        "rwa": ["real", "estate", "gold", "silver", "treasury", "bond", "stock", "equity"],
        "privacy": ["zcoin", "monero", "zec", "dash", "firo", "railgun"],
        "infrastructure": ["storage", "oracle", "dns", "bridge", "rpc", "indexer", "ipfs", "filecoin"],
        "prediction": ["will", "election", "court", "outcome", "yes", "no", "probability"],
        "stablecoin": ["usdt", "usdc", "dai", "frax", "busd", "tusd", "gusd"],
        "nft": ["nft", "collection", "bored", "azuki", "pudgy", "clonex"],
    }
    
    # Chain mapping
    CHAINS = {
        "solana": ["sol", "solana", "raydium", "orca", "jupiter"],
        "ethereum": ["eth", "ethereum", "uniswap", "sushiswap"],
        "base": ["base", "baseswap"],
        "arbitrum": ["arb", "arbitrum", "uniswap"],
        "polygon": ["matic", "polygon", "quickswap"],
        "bsc": ["bnb", "bsc", "pancakeswap"],
        "avalanche": ["avax", "avalanche", "traderjoe"],
    }
    
    def classify(self, market: Dict) -> Dict:
        """Classify a market."""
        name = market.get("name", "").lower()
        symbol = market.get("symbol", "").lower()
        category = market.get("category", "unknown")
        
        # Check existing category
        if category and category != "unknown":
            detected = category
            confidence = 0.9
        else:
            detected = "uncategorized"
            confidence = 0
        
        # Match keywords
        for cat, keywords in self.CATEGORIES.items():
            for kw in keywords:
                if kw in name or kw in symbol:
                    detected = cat
                    confidence = 0.8
                    break
        
        # Detect chain
        chain = self._detect_chain(market)
        
        return {
            "original_category": category,
            "detected_category": detected,
            "confidence": confidence,
            "chain": chain,
            "classified_at": datetime.now().isoformat()
        }
    
    def _detect_chain(self, market: Dict) -> str:
        """Detect blockchain."""
        name = market.get("name", "").lower()
        symbol = market.get("symbol", "").lower()
        
        for chain, keywords in self.CHAINS.items():
            for kw in keywords:
                if kw in name or kw in symbol:
                    return chain
        
        return "unknown"
    
    def classify_batch(self, markets: List[Dict]) -> List[Dict]:
        """Classify multiple markets."""
        results = []
        
        for market in markets:
            classification = self.classify(market)
            results.append({
                **market,
                **classification
            })
        
        return results
    
    def get_category_stats(self, markets: List[Dict]) -> Dict:
        """Get statistics by category."""
        stats = {}
        
        for market in markets:
            cat = market.get("detected_category", "unknown")
            if cat not in stats:
                stats[cat] = {"count": 0, "volume": 0}
            
            stats[cat]["count"] += 1
            stats[cat]["volume"] += market.get("volume_24h", 0) or market.get("volume", 0)
        
        return stats


_classifier: Optional[CategoryClassifier] = None

def get_category_classifier() -> CategoryClassifier:
    """Get classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = CategoryClassifier()
    return _classifier


if __name__ == "__main__":
    classifier = get_category_classifier()
    
    test_markets = [
        {"name": "Pepe", "symbol": "PEPE", "volume_24h": 1000000},
        {"name": "Render", "symbol": "RNDR", "volume_24h": 500000},
        {"name": "Bitcoin", "symbol": "BTC", "volume_24h": 50000000000},
    ]
    
    results = classifier.classify_batch(test_markets)
    print(json.dumps(results, indent=2))
