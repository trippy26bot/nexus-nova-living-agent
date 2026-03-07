---
name: file-system
version: 1.0.0
description: Allow safe interaction with the local filesystem.
tags: [filesystem, file, read, write, directory]
triggers: [read file, write file, list directory, create folder]
---

# File System Skill

## Purpose

Allow safe interaction with the local filesystem.

## Capabilities

- `read_file(path)` — Read file contents
- `write_file(path, content)` — Write content to file
- `list_directory(path)` — List directory contents
- `create_directory(path)` — Create a directory

## Invariants

1. **Never access system-critical directories** — Block `/etc`, `/usr`, `/bin`, `/sbin`, `~/.ssh`, `~/.aws`, `/root`
2. **Always validate file paths** — No path traversal (`../`), no absolute paths outside workspace
3. **Read-only by default unless explicitly writing**

## Usage

```python
# Read a file
content = read_file("/workspace/notes.txt")

# Write to a file
write_file("/workspace/output.txt", "Hello world")

# List directory
files = list_directory("/workspace")

# Create directory
create_directory("/workspace/new_folder")
```

## Safety

- Path validation before every operation
- Block list for system directories
- Audit log all file operations

## Trust Level

**restricted** — Requires approval for write operations
