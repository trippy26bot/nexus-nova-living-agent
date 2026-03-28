import hashlib
import os
import json

CORE_FILES = [
    "SOUL.md",
    "SEED.md",
    "IDENTITY.md",
    "PRESENCE.md",
    "EPISTEMIC_BOUNDARIES.md",
    "NOVA_BECOMING.md",
]

def hash_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

manifest = {}
for filepath in CORE_FILES:
    if os.path.exists(filepath):
        manifest[filepath] = hash_file(filepath)
    else:
        print(f"WARNING: {filepath} not found")

with open("MANIFEST.sha256", "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Manifest generated. {len(manifest)} files hashed.")
