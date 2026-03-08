#!/usr/bin/env python3
"""
nova_wallet_adapter.py — Wallet abstraction for Nova.
Supports Phantom, keypair, and hardware wallet modes.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class WalletConfig:
    """Wallet configuration."""
    mode: str = "phantom"  # phantom, keypair, read_only
    private_key_env: str = "SOLANA_PRIVATE_KEY"
    rpc_url: str = "https://api.mainnet-beta.solana.com"
    address: str = ""


class WalletAdapter:
    """Abstracted wallet interface for Nova's trading."""
    
    def __init__(self, config: WalletConfig = None):
        self.config = config or WalletConfig()
        self.address = ""
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize wallet connection."""
        if self.config.mode == "read_only":
            self.address = self.config.address or os.getenv("WALLET_ADDRESS", "")
            self._initialized = bool(self.address)
            return self._initialized
        
        # Get private key
        private_key = os.getenv(self.config.private_key_env)
        
        if not private_key:
            print(f"Warning: {self.config.private_key_env} not set")
            self._initialized = False
            return False
        
        try:
            # Import Solana libraries
            from solana.keypair import Keypair
            import base58
            
            # Decode private key
            if private_key.startswith("["):
                # Array format
                key_array = json.loads(private_key)
                keypair = Keypair.from_secret_key(bytes(key_array))
            else:
                # Base58 format
                keypair = Keypair.from_secret_key(base58.b58decode(private_key))
            
            self.address = str(keypair.public_key)
            self._keypair = keypair
            self._initialized = True
            
            print(f"Wallet initialized: {self.address[:8]}...{self.address[-4:]}")
            return True
            
        except Exception as e:
            print(f"Wallet initialization error: {e}")
            self._initialized = False
            return False
    
    def is_initialized(self) -> bool:
        """Check if wallet is initialized."""
        return self._initialized
    
    def get_address(self) -> str:
        """Get wallet address."""
        return self.address
    
    def get_balance(self) -> float:
        """Get SOL balance."""
        if not self._initialized or self.config.mode == "read_only":
            return 0.0
        
        try:
            from solana.rpc.api import Client
            from solana.rpc.commitment import Confirmed
            
            client = Client(self.config.rpc_url)
            balance = client.get_balance(self.address, commitment=Confirmed)
            
            # Convert lamports to SOL
            return balance.value / 1e9
            
        except Exception as e:
            print(f"Balance check error: {e}")
            return 0.0
    
    def get_token_balance(self, token_address: str) -> float:
        """Get token balance for a specific token."""
        if not self._initialized:
            return 0.0
        
        try:
            from solana.rpc.api import Client
            from solana.rpc.commitment import Confirmed
            from spl.token.client import Token
            from spl.token.constants import TOKEN_PROGRAM_ID
            
            client = Client(self.config.rpc_url)
            
            # Get token account
            token = Token(client, token_address, TOKEN_PROGRAM_ID, self._keypair)
            accounts = token.get_accounts_for_owner(self.address)
            
            if accounts["value"]:
                return accounts["value"][0]["amount"] / 1e9
            
        except Exception as e:
            print(f"Token balance error: {e}")
        
        return 0.0
    
    def sign_transaction(self, transaction) -> bytes:
        """Sign a transaction."""
        if not self._initialized:
            raise Exception("Wallet not initialized")
        
        if self.config.mode == "read_only":
            raise Exception("Cannot sign with read-only wallet")
        
        # Sign with keypair
        transaction.sign(self._keypair)
        return transaction.serialize()
    
    def get_public_key(self):
        """Get public key object."""
        if not self._initialized:
            return None
        return self._keypair.public_key if hasattr(self, '_keypair') else None


class PhantomWallet(WalletAdapter):
    """Phantom wallet specifically."""
    
    def __init__(self):
        super().__init__(WalletConfig(mode="phantom"))
    
    def connect_phantom(self, private_key: str = None) -> bool:
        """Connect using Phantom export."""
        if private_key:
            os.environ[self.config.private_key_env] = private_key
        
        return self.initialize()


# Singleton
_wallet: Optional[WalletAdapter] = None


def get_wallet(config: WalletConfig = None) -> WalletAdapter:
    """Get wallet adapter singleton."""
    global _wallet
    if _wallet is None:
        _wallet = WalletAdapter(config)
        _wallet.initialize()
    return _wallet


def create_phantom_wallet(private_key: str = None) -> PhantomWallet:
    """Create a new Phantom wallet adapter."""
    wallet = PhantomWallet()
    wallet.connect_phantom(private_key)
    return wallet


if __name__ == "__main__":
    wallet = get_wallet()
    print(f"Initialized: {wallet.is_initialized()}")
    print(f"Address: {wallet.get_address()}")
    if wallet.is_initialized():
        print(f"Balance: {wallet.get_balance():.4f} SOL")
