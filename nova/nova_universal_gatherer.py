#!/usr/bin/env python3
"""
Nova TRULY Universal Data Gatherer
No API keys - only public free sources
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
        self.data = {}
    
    def gather_coingecko(self) -> List[Dict]:
        """CoinGecko free API"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "volume_desc",
                "per_page": 50,
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
        except Exception as e:
            pass
        return []
    
    def gather_cryptocompare(self) -> List[Dict]:
        """CryptoCompare free API"""
        try:
            url = "https://min-api.cryptocompare.com/data/top/totalvol?limit=50"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("Data"):
                    self.sources_tried.append("cryptocompare")
                    return [{
                        "symbol": d.get("CoinInfo", {}).get("Symbol", "").upper(),
                        "name": d.get("CoinInfo", {}).get("FullName", ""),
                        "price": d.get("RAW", {}).get("USD", {}).get("PRICE"),
                        "change_24h": d.get("RAW", {}).get("USD", {}).get("CHANGEPCT24HOUR"),
                        "volume": d.get("RAW", {}).get("USD", {}).get("VOLUME24HOUR"),
                        "source": "cryptocompare"
                    } for d in data["Data"]]
        except Exception as e:
            pass
        return []
    
    def gather_all(self) -> Dict:
        """Gather from ALL public sources"""
        all_coins = []
        
        # Try each source
        all_coins.extend(self.gather_coingecko())
        all_coins.extend(self.gather_cryptocompare())
        
        # Deduplicate by symbol
        seen = set()
        unique = []
        for coin in all_coins:
            sym = coin.get("symbol", "")
            if sym and sym not in seen:
                seen.add(sym)
                unique.append(coin)
        
        # Sort by volume
        unique.sort(key=lambda x: x.get("volume", 0), reverse=True)
        
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
        
        for coin in coins[:30]:  # Top 30
            change = coin.get("change_24h", 0) or 0
            volume = coin.get("volume", 0) or 0
            
            # High volume + big move = opportunity
            if volume > 10_000_000:  # $10M+
                if change < -5:  # Dip
                    opportunities.append({
                        "symbol": coin.get("symbol"),
                        "action": "BUY",
                        "price": coin.get("price"),
                        "change": change,
                        "volume": volume,
                        "reason": "dip_buy"
                    })
                elif change > 5:  # Pump
                    opportunities.append({
                        "symbol": coin.get("symbol"),
                        "action": "SELL",
                        "price": coin.get("price"),
                        "change": change,
                        "volume": volume,
                        "reason": "profit_take"
                    })
        
        return opportunities[:10]
    
    def status(self) -> str:
        """Get status"""
        data = self.gather_all()
        return f"""🌐 Nova Universal Data Gatherer

Sources Active: {', '.join(data.get('sources', ['none']))}
Coins Mapped: {data.get('count', 0)}
Last Update: {data.get('timestamp', 'Never')}"""

if __name__ == "__main__":
    g = UniversalGatherer()
    print(g.status())
    
    print("\n📈 Top Opportunities:")
    ops = g.find_opportunities()
    for op in ops[:5]:
        print(f"  {op['symbol']}: {op['change']:+.1f}% (${op.get('volume', 0)/1e6:.1f}M)")
