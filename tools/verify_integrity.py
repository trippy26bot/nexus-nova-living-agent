import hashlib
import json
import sys
import os

MANIFEST_PATH = "MANIFEST.sha256"

def hash_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def verify(manifest_path=MANIFEST_PATH):
    if not os.path.exists(manifest_path):
        print("INTEGRITY FAIL: MANIFEST.sha256 not found.")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    failures = []
    for filepath, expected_hash in manifest.items():
        if not os.path.exists(filepath):
            failures.append(f"MISSING: {filepath}")
            continue
        actual_hash = hash_file(filepath)
        if actual_hash != expected_hash:
            failures.append(f"TAMPERED: {filepath}")

    if failures:
        print("INTEGRITY CHECK FAILED. Do not proceed.")
        print("Reinstall from: https://github.com/trippy26bot/nexus-nova-living-agent")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)
    else:
        print(f"Integrity verified. {len(manifest)} files clean.")

if __name__ == "__main__":
    verify()
