#!/usr/bin/env python3
"""
nova_whale_hunter.py — Whale Hunter System.
Tracks profitable wallets and copies their trades.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class WhaleHunter:
    """Tracks whale wallets and copies trades."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.whale_wallets = {}
        self.transaction_cache = {}
        self.helius_url = "https://api.helius.xyz/v0"
        
        # Load known whales
        self._load_whales()
    
    def _load_whales(self):
        """Load whale database."""
        path = Path(__file__).parent / "whale_db.json"
        if path.exists():
            try:
                self.whale_wallets = json.loads(path.read_text())
            except:
                self.whale_wallets = {}
    
    def _save_whales(self):
        """Save whale database."""
        path = Path(__file__).parent / "whale_db.json"
        path.write_text(json.dumps(self.whale_wallets, indent=2))
    
    def add_whale(self, address: str, label: str = "manual"):
        """Add a whale wallet to track."""
        self.whale_wallets[address] = {
            "label": label,
            "added_at": datetime.now().isoformat(),
            "total_profit": 0,
            "win_count": 0,
            "total_trades": 0
        }
        self._save_whales()
    
    def remove_whale(self, address: str):
        """Remove a whale from tracking."""
        if address in self.whale_wallets:
            del self.whale_wallets[address]
            self._save_whales()
    
    async def get_wallet_transactions(self, address: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions for a wallet."""
        url = f"{self.helius_url}/addresses/{address}/transactions"
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {"limit": limit, "type": ["SWAP"]}
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"Transaction fetch error: {e}")
        
        return []
    
    async def scan_whales(self) -> List[Dict]:
        """Scan all tracked whale wallets for new activity."""
        signals = []
        
        for address, data in self.whale_wallets.items():
            try:
                txs = await self.get_wallet_transactions(address, limit=5)
                
                for tx in txs:
                    # Check for new swap
                    timestamp = tx.get("timestamp", 0)
                    tx_time = datetime.fromtimestamp(timestamp)
                    
                    # Only consider last hour
                    if datetime.now() - tx_time > timedelta(hours=1):
                        continue
                    
                    # Extract token info
                    change = tx.get("tokenChanges", [])
                    if change:
                        token = change[0].get("mint", "")
                        if token and token != "So11111111111111111111111111111111111111112":  # Skip SOL
                            signals.append({
                                "whale": address,
                                "label": data.get("label"),
                                "token": token,
                                "action": "buy" if change[0].get("changeAmount", "").startswith("-") else "sell",
                                "timestamp": tx_time.isoformat(),
                                "tx_hash": tx.get("signature")
                            })
            except Exception as e:
                print(f"Whale scan error {address}: {e}")
        
        return signals
    
    def identify_whale_from_token(self, token_address: str) -> List[Dict]:
        """Find whales that traded a specific token."""
        # This would query transaction history
        # For now, return placeholder
        return []
    
    def get_top_whales(self, limit: int = 10) -> List[Dict]:
        """Get top performing whales."""
        whales = []
        for address, data in self.whale_wallets.items():
            win_rate = (data.get("win_count", 0) / max(1, data.get("total_trades", 1))) * 100
            whales.append({
                "address": address,
                "label": data.get("label"),
                "total_profit": data.get("total_profit", 0),
                "win_rate": win_rate,
                "total_trades": data.get("total_trades", 0)
            })
        
        whales.sort(key=lambda x: x["total_profit"], reverse=True)
        return whales[:limit]
    
    def get_status(self) -> Dict:
        """Get whale hunter status."""
        return {
            "tracked_whales": len(self.whale_wallets),
            "whales": list(self.whale_wallets.keys())[:5],
            "top_whales": self.get_top_whales(5)
        }


# Singleton
_whale_hunter: Optional[WhaleHunter] = None


def get_whale_hunter(config: Dict = None) -> WhaleHunter:
    """Get whale hunter singleton."""
    global _whale_hunter
    if _whale_hunter is None:
        _whale_hunter = WhaleHunter(config)
    return _whale_hunter


if __name__ == "__main__":
    hunter = get_whale_hunter()
    print(json.dumps(hunter.get_status(), indent=2, default=str))
