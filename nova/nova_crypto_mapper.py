#!/usr/bin/env python3
"""
Nova Universal Crypto Mapper
Own API built from free public sources
"""
import requests
import json
import os
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

DATA_DIR = os.path.expanduser("~/.nova/crypto_map")
os.makedirs(DATA_DIR, exist_ok=True)

CACHE_FILE = os.path.join(DATA_DIR, "cache.json")
PRICES_FILE = os.path.join(DATA_DIR, "prices.json")

class UniversalCryptoMapper:
    """Build our own crypto mapping from free sources"""
    
    def __init__(self):
        self.cache = self._load_cache()
    
    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                return json.load(f)
        return {"tokens": {}, "updated": None}
    
    def _save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=2)
    
    def fetch_from_coingecko(self) -> Dict:
        """Get prices from CoinGecko (free, no key)"""
        try:
            # Get top coins
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "volume_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": False
            }
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"CoinGecko error: {e}")
        return []
    
    def fetch_from_birdeye(self) -> Dict:
        """Try Birdeye (free tier)"""
        try:
            url = "https://api.birdeye.so/v1/tokenlist"
            params = {"sort_by": "volume", "sort_type": "desc", "limit": 50}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"Birdeye error: {e}")
        return {}
    
    def fetch_solana_tokens(self) -> List[Dict]:
        """Get Solana tokens from public sources"""
        tokens = []
        
        # Try Solana token list (public)
        try:
            url = "https://token-list.solana.com/tokens.json"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                tokens.extend([
                    {
                        "symbol": t.get("symbol"),
                        "name": t.get("name"),
                        "address": t.get("address"),
                        "chain": "solana",
                        "decimals": t.get("decimals")
                    }
                    for t in data.get("tokens", [])[:100]
                ])
        except:
            pass
        
        return tokens
    
    def map_prices(self) -> Dict:
        """Build our own price map from multiple sources"""
        prices = {}
        
        # Source 1: CoinGecko
        cg_data = self.fetch_from_coingecko()
        for coin in cg_data:
            symbol = coin.get("symbol", "").upper()
            prices[symbol] = {
                "name": coin.get("name"),
                "price": coin.get("current_price"),
                "change_24h": coin.get("price_change_percentage_24h"),
                "volume": coin.get("total_volume"),
                "market_cap": coin.get("market_cap"),
                "source": "coingecko"
            }
        
        # Source 2: Try adding Solana tokens
        sol_tokens = self.fetch_solana_tokens()
        for token in sol_tokens:
            symbol = token.get("symbol", "")
            if symbol and symbol not in prices:
                prices[symbol] = {
                    "name": token.get("name"),
                    "address": token.get("address"),
                    "chain": "solana",
                    "source": "solana_token_list"
                }
        
        # Save
        self.cache = {
            "prices": prices,
            "updated": datetime.now().isoformat(),
            "coins_count": len(prices)
        }
        self._save_cache()
        
        return prices
    
    def get_opportunities(self) -> List[Dict]:
        """Find trading opportunities from our map"""
        if not self.cache.get("prices"):
            self.map_prices()
        
        opportunities = []
        prices = self.cache.get("prices", {})
        
        for symbol, data in prices.items():
            change = data.get("change_24h", 0)
            volume = data.get("volume", 0)
            
            # Find opportunities
            if change and volume:
                # High volume + big move
                if abs(change) > 5 and volume > 10_000_000:
                    opportunities.append({
                        "symbol": symbol,
                        "change_24h": change,
                        "volume": volume,
                        "price": data.get("price"),
                        "reason": "high_volume_move" if change > 0 else "dip_buy"
                    })
        
        # Sort by volume
        opportunities.sort(key=lambda x: x.get("volume", 0), reverse=True)
        return opportunities[:10]
    
    def status(self) -> str:
        """Get mapper status"""
        if not self.cache.get("prices"):
            self.map_prices()
        
        prices = self.cache.get("prices", {})
        return f"""📊 Nova Universal Crypto Map

Coins Mapped: {len(prices)}
Last Updated: {self.cache.get('updated', 'Never')}

Top Opportunities:"""

def run_mapper():
    """Run the mapper"""
    mapper = UniversalCryptoMapper()
    mapper.map_prices()
    return mapper.cache

if __name__ == "__main__":
    mapper = UniversalCryptoMapper()
    print(mapper.status())
    
    ops = mapper.get_opportunities()
    print(f"\nFound {len(ops)} opportunities:")
    for op in ops[:5]:
        print(f"  {op['symbol']}: {op.get('change_24h', 0):+.1f}% (${op.get('volume', 0)/1e6:.1f}M)")
