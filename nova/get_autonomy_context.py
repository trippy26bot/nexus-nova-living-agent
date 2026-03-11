#!/usr/bin/env python3
"""Quick context fetch for OpenClaw"""
import sys
sys.path.insert(0, "/Users/dr.claw/.openclaw/workspace")

from nova.autonomy_bridge import get_full_wakeup_context

print(get_full_wakeup_context())
