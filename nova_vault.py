#!/usr/bin/env python3
"""
nova_vault.py — Secure Vault for Keys.
Never stores private keys directly.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
import base64
import hashlib


class SecureVault:
    """Secure storage for sensitive data."""
    
    def __init__(self):
        self.base_path = Path.home() / ".nova" / "vault"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.base_path / "manifest.json"
        self._load_manifest()
    
    def _load_manifest(self):
        """Load vault manifest."""
        if self.manifest_path.exists():
            try:
                self.manifest = json.loads(self.manifest_path.read_text())
            except:
                self.manifest = {"keys": {}}
        else:
            self.manifest = {"keys": {}}
    
    def _save_manifest(self):
        """Save vault manifest."""
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2))
    
    def store_key(self, name: str, value: str) -> bool:
        """Store a key securely."""
        # Create hash of name for filename
        name_hash = hashlib.sha256(name.encode()).hexdigest()[:16]
        
        # Store in file
        key_path = self.base_path / f"{name_hash}.key"
        key_path.write_text(base64.b64encode(value.encode()).decode())
        
        # Update manifest
        self.manifest["keys"][name] = {
            "stored_at": str(self.base_path / f"{name_hash}.key"),
            "hash": name_hash
        }
        self._save_manifest()
        
        return True
    
    def get_key(self, name: str) -> Optional[str]:
        """Retrieve a key."""
        if name not in self.manifest["keys"]:
            return None
        
        name_hash = self.manifest["keys"][name]["hash"]
        key_path = self.base_path / f"{name_hash}.key"
        
        if not key_path.exists():
            return None
        
        try:
            return base64.b64decode(key_path.read_text()).decode()
        except:
            return None
    
    def delete_key(self, name: str) -> bool:
        """Delete a key."""
        if name not in self.manifest["keys"]:
            return False
        
        name_hash = self.manifest["keys"][name]["hash"]
        key_path = self.base_path / f"{name_hash}.key"
        
        if key_path.exists():
            key_path.unlink()
        
        del self.manifest["keys"][name]
        self._save_manifest()
        
        return True
    
    def list_keys(self) -> list:
        """List stored key names (not values)."""
        return list(self.manifest["keys"].keys())
    
    def is_configured(self) -> bool:
        """Check if vault has any keys."""
        return len(self.manifest["keys"]) > 0


# Singleton
_vault: Optional[SecureVault] = None


def get_vault() -> SecureVault:
    """Get vault singleton."""
    global _vault
    if _vault is None:
        _vault = SecureVault()
    return _vault


if __name__ == "__main__":
    import json
    vault = get_vault()
    print(json.dumps({"keys": vault.list_keys(), "configured": vault.is_configured()}, indent=2))
