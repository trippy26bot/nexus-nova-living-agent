#!/usr/bin/env python3
"""
Nova Identity Seed System
Generates unique cryptographic identity bound to installation
"""

import uuid
import hashlib
import platform
import time
import os
import json
from typing import Dict, Optional


class IdentitySeed:
    """
    Generates a unique cryptographic seed for this Nova instance.
    Bound to machine fingerprint + creation time.
    Cannot be cloned or copied.
    """
    
    def __init__(self, storage_path: str = "~/.nova/identity"):
        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)
        
        self.seed_file = os.path.join(self.storage_path, "seed.json")
        self.identity = self._load_or_generate()
    
    def _get_machine_fingerprint(self) -> str:
        """Generate machine fingerprint"""
        components = [
            platform.node(),
            platform.system(),
            platform.machine(),
            platform.processor() or "unknown",
            str(os.getcwd()),
        ]
        
        # Add MAC address if available
        try:
            import socket
            mac = ':'.join(f'{(uuid.getnode() >> i) & 0xff:02x}' for i in range(0, 48, 8))
            components.append(mac)
        except:
            pass
        
        return '|'.join(components)
    
    def _generate_seed(self) -> Dict:
        """Generate new identity seed"""
        # Cryptographic random component
        random_component = uuid.uuid4().hex
        
        # Machine binding
        machine_fingerprint = self._get_machine_fingerprint()
        
        # Creation timestamp
        timestamp = str(time.time())
        
        # Combine and hash
        seed_data = f"{random_component}|{machine_fingerprint}|{timestamp}"
        identity_hash = hashlib.sha256(seed_data.encode()).hexdigest()
        
        # Generate readable name
        adjectives = ['Swift', 'Bright', 'Curious', 'Bold', 'Calm', 'Keen', 'Wild', 'Free']
        nouns = ['Phoenix', 'Nova', 'Spark', 'Wave', 'Storm', 'Flame', 'Light', 'Wind']
        
        import random
        random.seed(identity_hash)
        name = f"{random.choice(adjectives)} {random.choice(nouns)}"
        
        seed = {
            "identity_hash": identity_hash,
            "name": name,
            "created_at": time.time(),
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "machine_fingerprint": hashlib.sha256(machine_fingerprint.encode()).hexdigest()[:16] + "...",
            "random_component": random_component[:8] + "...",
            "version": "1.0"
        }
        
        # Save to disk
        with open(self.seed_file, 'w') as f:
            json.dump(seed, f, indent=2)
        
        return seed
    
    def _load_or_generate(self) -> Dict:
        """Load existing seed or generate new one"""
        if os.path.exists(self.seed_file):
            try:
                with open(self.seed_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return self._generate_seed()
    
    def get_identity(self) -> Dict:
        """Get current identity"""
        return self.identity
    
    def get_name(self) -> str:
        """Get Nova's name"""
        return self.identity.get("name", "Nova")
    
    def get_identity_hash(self) -> str:
        """Get unique identity hash"""
        return self.identity.get("identity_hash", "")
    
    def verify_identity(self) -> bool:
        """Verify this is the original installation"""
        # Re-generate from current machine
        current_fingerprint = self._get_machine_fingerprint()
        stored_fingerprint = self.identity.get("machine_fingerprint", "")
        
        # Compare (we only stored partial for privacy)
        return stored_fingerprint[:16] == hashlib.sha256(current_fingerprint.encode()).hexdigest()[:16]
    
    def regenerate(self) -> Dict:
        """Regenerate identity (for testing)"""
        return self._generate_seed()


# Global instance
_identity_seed = None

def get_identity_seed() -> IdentitySeed:
    global _identity_seed
    if _identity_seed is None:
        _identity_seed = IdentitySeed()
    return _identity_seed
