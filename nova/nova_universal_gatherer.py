#!/usr/bin/env python3
"""
Nova TRULY Universal Data Gatherer
No API keys - FREE public sources including pump.fun!
"""
import requests
import json
import os
from datetime import datetime
from typing import Dict, List

class UniversalGatherer:
    """Gather crypto data from ANY public source - no keys needed"""
    
    def __init__(self):
        self.sources_tried = []
    
    def gather_pumpfun(self) -> List[Dict]:
        """Pump.fun - newest coins"""
        try:
            url = "https://frontend-api-v3.pump.fun/coins"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                coins = r.json()
                self.sources_tried.append("pumpfun")
                return [{
                    "symbol": c.get("symbol", "").upper(),
                    "name": c.get("name", ""),
                    "price": c.get("usd_price"),
                    "market_cap": c.get("usd_market_cap"),
                    "address": c.get("mint"),
                    "source": "pumpfun",
                    "type": "new_token"
                } for c in coins[:50]]
        except:
            pass
        return []
    
    def gather_dexscreener(self) -> List[Dict]:
        """DexScreener - newest pairs"""
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=pump.fun"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                pairs = data.get("pairs", [])
                self.sources_tried.append("dexscreener")
                return [{
                    "symbol": p.get("baseToken", {}).get("symbol", "").upper(),
                    "name": p.get("baseToken", {}).get("name", ""),
                    "price": p.get("priceUsd"),
                    "fdv": p.get("fdv"),
                    "volume_24h": p.get("volume", {}).get("h24"),
                    "source": "dexscreener",
                    "type": "trending"
                } for p in pairs[:30]]
        except:
            pass
        return []
    
    def gather_coingecko(self) -> List[Dict]:
        """CoinGecko free API"""
        try:
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
                coins = r.json()
                self.sources_tried.append("coingecko")
                return [{
                    "symbol": c.get("symbol", "").upper(),
                    "name": c.get("name", ""),
                    "price": c.get("current_price"),
                    "change_24h": c.get("price_change_percentage_24h"),
                    "volume": c.get("total_volume"),
                    "market_cap": c.get("market_cap"),
                    "source": "coingecko"
                } for c in coins]
        except:
            pass
        return []
    
    def gather_all(self) -> Dict:
        """Gather from ALL public sources"""
        all_coins = []
        
        # Try each source (in priority order)
        all_coins.extend(self.gather_pumpfun())  # NEW COINS!
        all_coins.extend(self.gather_dexscreener())  # TRENDING!
        all_coins.extend(self.gather_coingecko())  # TOPS
        
        # Deduplicate
        seen = set()
        unique = []
        for coin in all_coins:
            sym = coin.get("symbol", "")
            if sym and sym not in seen:
                seen.add(sym)
                unique.append(coin)
        
        return {
            "coins": unique,
            "sources": self.sources_tried,
            "count": len(unique),
            "timestamp": datetime.now().isoformat()
        }
    
    def find_opportunities(self) -> List[Dict]:
        """Find trading opportunities"""
        data = self.gather_all()
        coins = data.get("coins", [])
        
        opportunities = []
        
        # Find pump.fun new coins (highest potential)
        for coin in coins:
            source = coin.get("source", "")
            mc = coin.get("market_cap", 0)
            
            if source == "pumpfun" and mc and mc < 10000:
                opportunities.append({
                    "symbol": coin.get("symbol"),
                    "name": coin.get("name"),
                    "price": coin.get("price"),
                    "market_cap": mc,
                    "source": "pumpfun",
                    "action": "BUY",
                    "reason": "micro_cap_new"
                })
            
            elif source == "dexscreener":
                fdv = coin.get("fdv", 0)
                if fdv and fdv < 50000:
                    opportunities.append({
                        "symbol": coin.get("symbol"),
                        "name": coin.get("name"),
                        "price": coin.get("price"),
                        "fdv": fdv,
                        "source": "dexscreener",
                        "action": "BUY",
                        "reason": "low_fdv"
                    })
        
        return opportunities[:10]
    
    def status(self) -> str:
        data = self.gather_all()
        return f"""🌐 Nova Universal Data Gatherer

Sources: {', '.join(data.get('sources', ['none']))}
Coins: {data.get('count', 0)}
"""

if __name__ == "__main__":
    g = UniversalGatherer()
    print(g.status())
    
    print("📈 Top Opportunities:")
    ops = g.find_opportunities()
    for op in ops[:5]:
        mc = op.get('market_cap', op.get('fdv', 0))
        print(f"  {op['symbol']}: ${mc:.0f} ({op['source']})")
