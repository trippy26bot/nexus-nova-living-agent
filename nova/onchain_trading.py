#!/usr/bin/env python3
"""
Nova On-Chain Trading System
Multi-chain scanning and trading
"""
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Storage
ONCHAIN_DIR = os.path.expanduser("~/.nova/onchain")
os.makedirs(ONCHAIN_DIR, exist_ok=True)

POSITIONS_FILE = os.path.join(ONCHAIN_DIR, "positions.json")
STATE_FILE = os.path.join(ONCHAIN_DIR, "state.json")
CONFIG_FILE = os.path.join(ONCHAIN_DIR, "config.json")

# Chains to scan
CHAINS = {
    "solana": {
        "rpc": "https://api.mainnet-beta.solana.com",
        "explorer": "https://solscan.io"
    },
    "base": {
        "rpc": "https://mainnet.base.org",
        "explorer": "https://basescan.org"
    },
    "ethereum": {
        "rpc": "https://eth.llamarpc.com",
        "explorer": "https://etherscan.io"
    }
}

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE) as f:
            return json.load(f)
    return {"positions": []}

def save_positions(data):
    with open(POSITIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "balance": 10000,
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "pnl": 0,
        "started_at": datetime.now().isoformat()
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

class OnChainScanner:
    """Scan multiple chains for opportunities"""
    
    def __init__(self):
        self.helius_key = self._get_helius_key()
    
    def _get_helius_key(self):
        keys_file = os.path.expanduser("~/.nova/keys.json")
        if os.path.exists(keys_file):
            with open(keys_file) as f:
                keys = json.load(f)
                return keys.get("helius", {}).get("api_key", "")
        return ""
    
    def scan_solana(self) -> List[Dict]:
        """Scan Solana for opportunities"""
        opportunities = []
        
        # Use Helius for token list
        if self.helius_key:
            try:
                # Get recent token mints
                url = f"https://api.helius.xyz/v0/tokens?api-key={self.helius_key}"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    tokens = r.json()
                    # Look for new mints with volume
                    for token in tokens[:50]:  # Top 50
                        if token.get("volume24h", 0) > 10000:
                            opportunities.append({
                                "chain": "solana",
                                "symbol": token.get("symbol", "UNKNOWN"),
                                "address": token.get("address", ""),
                                "volume": token.get("volume24h", 0),
                                "price_change": token.get("priceChange24h", 0),
                                "liquidity": token.get("liquidity", 0),
                                "type": "new_token"
                            })
            except Exception as e:
                print(f"Helius scan error: {e}")
        
        return opportunities
    
    def scan_base(self) -> List[Dict]:
        """Scan Base chain"""
        opportunities = []
        # Could add Base scanning here
        return opportunities
    
    def scan_ethereum(self) -> List[Dict]:
        """Scan Ethereum"""
        opportunities = []
        # Could add ETH scanning here
        return opportunities
    
    def scan_all(self) -> List[Dict]:
        """Scan all chains"""
        all_ops = []
        all_ops.extend(self.scan_solana())
        all_ops.extend(self.scan_base())
        all_ops.extend(self.scan_ethereum())
        return all_ops

class TradingEngine:
    """Execute trades"""
    
    def __init__(self):
        self.phantom_wallet = None  # Set when provided
    
    def set_wallet(self, address: str):
        """Set Phantom wallet address"""
        self.phantom_wallet = address
        config = {"wallet_address": address, "set_at": datetime.now().isoformat()}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    
    def get_wallet(self) -> Optional[str]:
        """Get current wallet"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                return config.get("wallet_address")
        return self.phantom_wallet
    
    def can_trade(self) -> bool:
        """Check if ready to trade"""
        return self.get_wallet() is not None
    
    def place_trade(self, opportunity: Dict, amount: float = 5.0) -> Dict:
        """Place a trade (placeholder - needs wallet)"""
        if not self.can_trade():
            return {"success": False, "error": "No wallet configured"}
        
        # This would integrate with Phantom/Solana
        # For now, log the intent
        return {
            "success": True,
            "chain": opportunity.get("chain"),
            "symbol": opportunity.get("symbol"),
            "amount": amount,
            "wallet": self.get_wallet(),
            "note": "Trade logged - needs Phantom SDK integration"
        }

def status():
    """Get on-chain status"""
    scanner = OnChainScanner()
    engine = TradingEngine()
    
    positions = load_positions()
    state = load_state()
    
    # Get current prices for P&L
    current_prices = {}
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum,base&vs_currencies=usd", timeout=5)
        if r.status_code == 200:
            current_prices = r.json()
    except:
        pass
    
    # Calculate current P&L
    total_pnl = state.get("pnl", 0)
    for pos in positions.get("positions", []):
        symbol = pos.get("symbol", "").lower()
        if symbol in current_prices:
            current_price = current_prices[symbol]["usd"]
            entry = pos.get("entry_price", 0)
            if entry > 0:
                pnl = (current_price - entry) * pos.get("amount", 0)
                total_pnl += pnl
    
    return f"""📊 On-Chain Trading Status

Wallet: {engine.get_wallet() or 'Not configured'}
Chain: Solana, Base, Ethereum

Positions: {len(positions.get('positions', []))}
Total Trades: {state.get('total_trades', 0)}
P&L: ${total_pnl:,.2f}

Chains Active: Solana (scanning)"""

def scan():
    """Scan for opportunities"""
    scanner = OnChainScanner()
    opportunities = scanner.scan_all()
    return f"""🔍 On-Chain Scan Results

Found {len(opportunities)} opportunities"""

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            print(status())
        elif sys.argv[1] == "scan":
            print(scan())
    else:
        print(status())
