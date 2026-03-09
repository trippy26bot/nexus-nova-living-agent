#!/usr/bin/env python3
"""
Output Filter - Removes internal execution messages before user sees response
"""

import re

BLOCK_PATTERNS = [
    r"^exec",
    r"^subprocess",
    r"^running command",
    r"^shell>",
    r"^tool output:",
    r"^system:",
    r"^debug:",
    r"\[exec\]",
    r"\[tool\]",
    r"\[system\]",
    r"\[debug\]",
]

REMOVE_PATTERNS = [
    r"\[[0-9]{4}-[0-9]{2}-[0-9]{2}.*\]",
    r"Traceback \(most recent call last\):",
    r"File \".*\", line [0-9]+",
]

def clean_output(text: str) -> str:
    """Remove internal execution messages."""
    if not text:
        return ""
    
    lines = text.split("\n")
    clean_lines = []
    
    for line in lines:
        # Skip lines matching block patterns
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in BLOCK_PATTERNS):
            continue
        
        # Remove timestamps
        for pattern in REMOVE_PATTERNS:
            line = re.sub(pattern, "", line)
        
        line = line.strip()
        if line:
            clean_lines.append(line)
    
    return "\n".join(clean_lines).strip()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            print(clean_output(f.read()))
    else:
        print("Usage: python output_filter.py <file>")
