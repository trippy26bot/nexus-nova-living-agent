#!/usr/bin/env python3
"""
core/safe_write.py
Nova Loop — Safe Write Utilities

Unified integrity-check pattern for both text and JSON files.
All writes use atomic rename to prevent partial-file corruption.
"""

import os
import json
import tempfile


# Minimum content threshold — refuse empty or near-empty writes
MIN_CONTENT_LENGTH = 10


def validate_content(content):
    """
    Validate content is non-empty and not just whitespace.
    Returns the stripped content if valid.
    Raises ValueError if too short.
    """
    if content is None:
        raise ValueError("Content is None")
    stripped = content.strip()
    if len(stripped) < MIN_CONTENT_LENGTH:
        raise ValueError(
            f"Content too short ({len(stripped)} chars). "
            f"Minimum is {MIN_CONTENT_LENGTH}. Refusing to write."
        )
    return stripped


def safe_write(path, content):
    """
    Safely write text/markdown content to a file.

    - Validates non-empty before touching the file
    - Uses atomic rename (temp file + os.replace) to prevent corruption
    - Fails if content is empty or whitespace-only
    """
    validated = validate_content(content)

    dir_name = os.path.dirname(os.path.abspath(path))
    os.makedirs(dir_name, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        'w', dir=dir_name, delete=False, suffix='.tmp'
    ) as f:
        f.write(validated)
        tmp_path = f.name

    os.replace(tmp_path, path)  # Atomic on POSIX


def safe_write_json(path, data, validator=None):
    """
    Safely write JSON to a file.

    - Validates data is not None
    - Validates JSON-serializable
    - Optional validator callable — receives deserialized data, returns bool
    - Uses atomic rename to prevent partial-write corruption
    """
    if data is None:
        raise ValueError(f"Refusing to write None to {path}")

    # Validate serializable
    try:
        serialized = json.dumps(data, indent=2)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Data not JSON-serializable for {path}: {e}")

    # Optional schema validation
    if validator is not None:
        try:
            parsed = json.loads(serialized)
        except Exception:
            raise ValueError(f"Cannot re-parse JSON for validation at {path}")
        if not validator(parsed):
            raise ValueError(f"Data failed schema validation for {path}")

    dir_name = os.path.dirname(os.path.abspath(path))
    os.makedirs(dir_name, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        'w', dir=dir_name, delete=False, suffix='.tmp'
    ) as f:
        f.write(serialized)
        tmp_path = f.name

    os.replace(tmp_path, path)  # Atomic on POSIX


def load_json(path):
    """Load and parse a JSON file. Returns None if missing or invalid."""
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def read_file(path):
    """Read and return file contents. Returns None if missing."""
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return f.read()
    except IOError:
        return None
