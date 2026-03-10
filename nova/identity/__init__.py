#!/usr/bin/env python3
"""
Nova Identity Module
"""

from nova.identity.identity_seed import IdentitySeed, get_identity_seed
from nova.identity.identity_lock import IdentityLock, CloneProtection, get_identity_lock

__all__ = [
    'IdentitySeed',
    'get_identity_seed',
    'IdentityLock',
    'CloneProtection',
    'get_identity_lock'
]
