#!/usr/bin/env python3
"""
nova_blacklist_db.py — Threat Intelligence Database.
Persistent storage for malicious entities.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set


class BlacklistDB:
    """Database of known malicious entities."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.db_path = self.base_path / "threat_blacklist.json"
        self._load()
    
    def _load(self):
        """Load blacklist database."""
        if self.db_path.exists():
            try:
                data = json.loads(self.db_path.read_text())
                self.scam_wallets = set(data.get("scam_wallets", []))
                self.rug_devs = set(data.get("rug_devs", []))
                self.honeypot_contracts = set(data.get("honeypot_contracts", []))
                self.malicious_tokens = set(data.get("malicious_tokens", []))
                self.suspicious_clusters = data.get("suspicious_clusters", [])
            except:
                self._init_empty()
        else:
            self._init_empty()
    
    def _init_empty(self):
        """Initialize empty database."""
        self.scam_wallets = set()
        self.rug_devs = set()
        self.honeypot_contracts = set()
        self.malicious_tokens = set()
        self.suspicious_clusters = []
    
    def _save(self):
        """Save blacklist database."""
        data = {
            "scam_wallets": list(self.scam_wallets),
            "rug_devs": list(self.rug_devs),
            "honeypot_contracts": list(self.honeypot_contracts),
            "malicious_tokens": list(self.malicious_tokens),
            "suspicious_clusters": self.suspicious_clusters,
            "updated": datetime.now().isoformat()
        }
        self.db_path.write_text(json.dumps(data, indent=2))
    
    def add_scam_wallet(self, address: str, reason: str = ""):
        """Add wallet to scam list."""
        self.scam_wallets.add(address)
        self._save()
    
    def add_rug_dev(self, address: str, rug_count: int = 1):
        """Add rug developer."""
        self.rug_devs.add(address)
        self._save()
    
    def add_honeypot(self, contract: str):
        """Add honeypot contract."""
        self.honeypot_contracts.add(contract)
        self._save()
    
    def add_malicious_token(self, token: str):
        """Add malicious token."""
        self.malicious_tokens.add(token)
        self._save()
    
    def add_suspicious_cluster(self, wallets: List[str], reason: str):
        """Add suspicious cluster."""
        self.suspicious_clusters.append({
            "wallets": wallets,
            "reason": reason,
            "added_at": datetime.now().isoformat()
        })
        self._save()
    
    def is_scam_wallet(self, address: str) -> bool:
        """Check if wallet is known scam."""
        return address in self.scam_wallets
    
    def is_rug_dev(self, address: str) -> bool:
        """Check if developer is known rug."""
        return address in self.rug_devs
    
    def is_honeypot(self, contract: str) -> bool:
        """Check if contract is honeypot."""
        return contract in self.honeypot_contracts
    
    def is_malicious_token(self, token: str) -> bool:
        """Check if token is malicious."""
        return token in self.malicious_tokens
    
    def is_in_cluster(self, wallet: str) -> bool:
        """Check if wallet is in suspicious cluster."""
        for cluster in self.suspicious_clusters:
            if wallet in cluster.get("wallets", []):
                return True
        return False
    
    def check_entity(self, address: str, token: str = "", contract: str = "") -> Dict:
        """Check all threat databases."""
        return {
            "scam_wallet": self.is_scam_wallet(address),
            "rug_dev": self.is_rug_dev(address),
            "honeypot": self.is_honeypot(contract),
            "malicious_token": self.is_malicious_token(token),
            "suspicious_cluster": self.is_in_cluster(address)
        }
    
    def get_status(self) -> Dict:
        """Get database status."""
        return {
            "scam_wallets": len(self.scam_wallets),
            "rug_devs": len(self.rug_devs),
            "honeypot_contracts": len(self.honeypot_contracts),
            "malicious_tokens": len(self.malicious_tokens),
            "suspicious_clusters": len(self.suspicious_clusters)
        }


# Singleton
_blacklist_db: Optional[BlacklistDB] = None


def get_blacklist_db() -> BlacklistDB:
    """Get blacklist database singleton."""
    global _blacklist_db
    if _blacklist_db is None:
        _blacklist_db = BlacklistDB()
    return _blacklist_db


if __name__ == "__main__":
    db = get_blacklist_db()
    print(json.dumps(db.get_status(), indent=2))
