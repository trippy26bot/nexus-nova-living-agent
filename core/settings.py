"""
core/settings.py
Nova agent configuration — loaded from environment variables.
"""

import os

# Council decision mode
# off     → bare loop, ~1 LLM call/cycle (DecisionEngine only)
# threshold → council fires if best option risk > COUNCIL_RISK_THRESHOLD
# always  → council every cycle, ~3 LLM calls minimum
COUNCIL_MODE = os.getenv("COUNCIL_MODE", "threshold").lower()
COUNCIL_RISK_THRESHOLD = float(os.getenv("COUNCIL_RISK_THRESHOLD", "0.55"))

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Vercel
NOVA_API_URL = os.getenv("NOVA_API_URL", "")
NOVA_API_SECRET = os.getenv("NOVA_API_SECRET", "")

# Loop
CYCLE_INTERVAL_SECONDS = int(os.getenv("CYCLE_INTERVAL_SECONDS", "30"))
MAX_CYCLES = int(os.getenv("MAX_CYCLES", "1000"))

# Molty
MOLTY_API_KEY = os.getenv("MOLTY_API_KEY", "")
