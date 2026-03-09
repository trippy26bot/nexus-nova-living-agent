#!/usr/bin/env python3
"""
File Integrity Scanner - Track file hashes to detect modifications
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

INTEGRITY_DB = ".nova_integrity.json"

def hash_file(path: str) -> str:
    """Calculate SHA256 hash of a file"""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def scan_directory(root: str, extensions=None) -> dict:
    """Scan directory and calculate file hashes"""
    if extensions is None:
        extensions = [".py", ".md", ".json"]
    
    records = {}
    root_path = Path(root)
    
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix in extensions:
            rel_path = str(path.relative_to(root_path))
            file_hash = hash_file(str(path))
            records[rel_path] = {
                "hash": file_hash,
                "size": path.stat().st_size,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
    
    return records

def save_integrity_db(records: dict, path: str = INTEGRITY_DB):
    """Save integrity database"""
    with open(path, "w") as f:
        json.dump(records, f, indent=2)

def load_integrity_db(path: str = INTEGRITY_DB) -> dict:
    """Load integrity database"""
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def check_integrity(root: str, db_path: str = INTEGRITY_DB) -> dict:
    """Check files against integrity database"""
    current = scan_directory(root)
    stored = load_integrity_db(db_path)
    
    results = {
        "new_files": [],
        "modified_files": [],
        "deleted_files": [],
        "unchanged": []
    }
    
    # Check for new and modified
    for path, data in current.items():
        if path not in stored:
            results["new_files"].append(path)
        elif stored[path]["hash"] != data["hash"]:
            results["modified_files"].append(path)
        else:
            results["unchanged"].append(path)
    
    # Check for deleted
    for path in stored:
        if path not in current:
            results["deleted_files"].append(path)
    
    return results

def print_integrity_report(results: dict):
    """Print integrity check results"""
    print("=" * 50)
    print("FILE INTEGRITY CHECK")
    print("=" * 50)
    
    print(f"🆕 New files: {len(results['new_files'])}")
    print(f"📝 Modified: {len(results['modified_files'])}")
    print(f"🗑️ Deleted: {len(results['deleted_files'])}")
    print(f"✅ Unchanged: {len(results['unchanged'])}")
    
    if results["modified_files"]:
        print("\n⚠️ Modified files:")
        for f in results["modified_files"]:
            print(f"  - {f}")
    
    if results["deleted_files"]:
        print("\n⚠️ Deleted files:")
        for f in results["deleted_files"]:
            print(f"  - {f}")
    
    print("=" * 50)
    
    return len(results["modified_files"]) == 0 and len(results["deleted_files"]) == 0


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "nova"
    results = check_integrity(root)
    success = print_integrity_report(results)
    sys.exit(0 if success else 1)
