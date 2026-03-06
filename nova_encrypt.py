#!/usr/bin/env python3
"""
NOVA ENCRYPT — Vault Encryption for Identity and Memory
Your data stays yours. Encrypts IDENTITY.md and memory files.

Uses AES encryption with a user-provided passphrase.
"""

import os
import sys
import base64
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

# Try to import cryptography, fall back to simpler methods if not available
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Configuration
NOVA_DIR = Path.home() / ".nova"
IDENTITY_FILE = NOVA_DIR / "IDENTITY.md"
MEMORY_DIR = NOVA_DIR / "memory"
ENCRYPTED_DIR = NOVA_DIR / "encrypted"
VAULT_CONFIG = NOVA_DIR / "vault.json"


def derive_key(passphrase: str) -> bytes:
    """Derive an encryption key from passphrase."""
    if CRYPTO_AVAILABLE:
        salt = b'nova_vault_salt_v1'  # Fixed salt for simplicity
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    else:
        # Fallback: simple hash (NOT SECURE - for testing only)
        return hashlib.sha256(passphrase.encode()).digest()


def encrypt_data(data: str, key: bytes) -> str:
    """Encrypt string data."""
    if CRYPTO_AVAILABLE:
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    else:
        # Fallback encoding (NOT SECURE)
        return base64.b64encode(data.encode()).decode()


def decrypt_data(encrypted: str, key: bytes) -> str:
    """Decrypt string data."""
    if CRYPTO_AVAILABLE:
        f = Fernet(key)
        return f.decrypt(encrypted.encode()).decode()
    else:
        # Fallback decoding
        return base64.b64decode(encrypted.encode()).decode()


def get_vault_config() -> dict:
    """Get vault configuration."""
    if VAULT_CONFIG.exists():
        with open(VAULT_CONFIG) as f:
            return json.load(f)
    return {}


def save_vault_config(config: dict):
    """Save vault configuration."""
    with open(VAULT_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)


def encrypt_file(file_path: Path, key: bytes) -> Path:
    """Encrypt a single file."""
    if not file_path.exists():
        return None
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    encrypted = encrypt_data(content, key)
    
    # Save to encrypted directory
    encrypted_path = ENCRYPTED_DIR / f"{file_path.name}.enc"
    with open(encrypted_path, 'w') as f:
        f.write(encrypted)
    
    return encrypted_path


def decrypt_file(encrypted_path: Path, key: bytes) -> str:
    """Decrypt a file."""
    if not encrypted_path.exists():
        return None
    
    with open(encrypted_path, 'r') as f:
        encrypted = f.read()
    
    return decrypt_data(encrypted, key)


def encrypt_vault(passphrase: str = None):
    """Encrypt identity and memory files."""
    
    if passphrase is None:
        passphrase = input("Enter vault passphrase: ")
    
    if not passphrase:
        print("Error: Passphrase required")
        return False
    
    # Create encrypted directory
    ENCRYPTED_DIR.mkdir(exist_ok=True)
    
    key = derive_key(passphrase)
    
    files_encrypted = []
    
    # Encrypt IDENTITY.md
    if IDENTITY_FILE.exists():
        encrypted_path = encrypt_file(IDENTITY_FILE, key)
        if encrypted_path:
            files_encrypted.append(str(IDENTITY_FILE))
            # Remove original
            IDENTITY_FILE.unlink()
            print(f"✓ Encrypted: {IDENTITY_FILE}")
    
    # Encrypt memory files
    if MEMORY_DIR.exists():
        for mem_file in MEMORY_DIR.glob("*.md"):
            encrypted_path = encrypt_file(mem_file, key)
            if encrypted_path:
                files_encrypted.append(str(mem_file))
                # Remove original
                mem_file.unlink()
                print(f"✓ Encrypted: {mem_file}")
    
    # Encrypt database
    nova_db = NOVA_DIR / "nova.db"
    if nova_db.exists():
        with open(nova_db, 'rb') as f:
            content = f.read()
        
        encrypted = encrypt_data(content.decode('utf-8', errors='ignore'), key)
        encrypted_path = ENCRYPTED_DIR / "nova.db.enc"
        with open(encrypted_path, 'w') as f:
            f.write(encrypted)
        
        files_encrypted.append(str(nova_db))
        nova_db.unlink()
        print(f"✓ Encrypted: {nova_db}")
    
    # Save vault config
    config = {
        'encrypted': True,
        'files': files_encrypted,
        'encrypted_at': datetime.now().isoformat()
    }
    save_vault_config(config)
    
    print(f"\n✓ Vault locked. {len(files_encrypted)} files encrypted.")
    print("Keep your passphrase safe. Without it, your data cannot be recovered.")
    
    return True


def decrypt_vault(passphrase: str = None):
    """Decrypt vault files."""
    
    config = get_vault_config()
    
    if not config.get('encrypted'):
        print("Vault is not locked.")
        return False
    
    if passphrase is None:
        passphrase = input("Enter vault passphrase: ")
    
    if not passphrase:
        print("Error: Passphrase required")
        return False
    
    key = derive_key(passphrase)
    
    # Try to decrypt config to verify passphrase
    try:
        test_encrypted = ENCRYPTED_DIR / "IDENTITY.md.enc"
        if test_encrypted.exists():
            decrypt_file(test_encrypted, key)
    except Exception as e:
        print(f"Error: Wrong passphrase")
        return False
    
    files_decrypted = []
    
    # Decrypt all encrypted files
    for enc_file in ENCRYPTED_DIR.glob("*.enc"):
        decrypted_content = decrypt_file(enc_file, key)
        
        # Determine original path
        original_name = enc_file.stem  # Remove .enc
        if original_name == "nova.db":
            original_path = NOVA_DIR / "nova.db"
        else:
            original_path = NOVA_DIR / original_name
        
        # Write decrypted content
        if original_name == "nova.db":
            with open(original_path, 'wb') as f:
                f.write(decrypted_content.encode('utf-8'))
        else:
            with open(original_path, 'w') as f:
                f.write(decrypted_content)
        
        files_decrypted.append(str(original_path))
        print(f"✓ Decrypted: {original_path}")
    
    # Update config
    config['encrypted'] = False
    save_vault_config(config)
    
    print(f"\n✓ Vault unlocked. {len(files_decrypted)} files decrypted.")
    
    return True


def is_vault_locked() -> bool:
    """Check if vault is currently locked."""
    config = get_vault_config()
    return config.get('encrypted', False)


# CLI
if __name__ == '__main__':
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Nova Vault Encryption")
    subparsers = parser.add_subparsers(dest='command')
    
    subparsers.add_parser('lock', help='Lock the vault')
    subparsers.add_parser('unlock', help='Unlock the vault')
    subparsers.add_parser('status', help='Check vault status')
    
    args = parser.parse_args()
    
    if args.command == 'lock':
        encrypt_vault()
    elif args.command == 'unlock':
        decrypt_vault()
    elif args.command == 'status':
        if is_vault_locked():
            print("🔒 Vault is locked")
        else:
            print("🔓 Vault is unlocked")
    else:
        parser.print_help()
