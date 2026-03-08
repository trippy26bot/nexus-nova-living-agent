#!/usr/bin/env python3
"""
nova_dashboard.py — Nova Mission Control Dashboard.
Live monitoring for the trading system.
"""

import streamlit as st
import psutil
import datetime
import json
import asyncio
from pathlib import Path

st.set_page_config(
    page_title="Nova Mission Control",
    page_icon="🚀",
    layout="wide"
)

# Page title
st.title("🚀 NOVA MISSION CONTROL")
st.markdown("**Crypto Intelligence Dashboard**")

# System Status
st.header("🖥️ System Status")

col1, col2, col3, col4 = st.columns(4)

cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage('/').percent

try:
    import subprocess
    result = subprocess.run(['uptime'], capture_output=True, text=True)
    uptime = result.stdout.strip()
except:
    uptime = "Unknown"

col1.metric("CPU", f"{cpu}%", delta_color="inverse")
col2.metric("RAM", f"{ram}%", delta_color="inverse")
col3.metric("Disk", f"{disk}%")
col4.metric("Uptime", uptime.split(",")[0] if "," in uptime else uptime[:15])

# Module Status
st.header("⚙️ Trading Engine Modules")

base_path = Path(__file__).parent

modules = [
    ("Autonomous Hunter", "nova_autonomous_hunter.py"),
    ("Alpha Brain", "nova_brain.py"),
    ("Launch Radar", "nova_launch_radar.py"),
    ("Whale Hunter", "nova_whale_hunter.py"),
    ("Wallet Predictor", "nova_wallet_predictor.py"),
    ("Wallet Clusterer", "nova_wallet_clusterer.py"),
    ("Dev Intelligence", "nova_dev_intelligence.py"),
    ("Narrative Momentum", "nova_narrative_momentum.py"),
    ("Pre-Pump Detector", "nova_pre_pump_detector.py"),
    ("Exit Detector", "nova_exit_detector.py"),
    ("Risk Engine", "nova_risk_engine.py"),
    ("Security Guard", "nova_security_guard.py"),
    ("Alert System", "nova_alerts.py"),
    ("Liquidity Inflow", "nova_liquidity_inflow_detector.py"),
]

cols = st.columns(4)

for i, (name, filename) in enumerate(modules):
    col = cols[i % 4]
    module_path = base_path / filename
    
    if module_path.exists():
        col.success(f"✅ {name}")
    else:
        col.error(f"❌ {name}")

# API Status
st.header("🌐 API Status")

apis = [
    ("DexScreener", "https://api.dexscreener.com"),
    ("Helius RPC", "https://api.mainnet-beta.solana.com"),
]

api_cols = st.columns(3)

for i, (name, url) in enumerate(apis):
    col = api_cols[i % 3]
    try:
        import requests
        start = datetime.datetime.now()
        r = requests.get(url, timeout=2)
        latency = (datetime.datetime.now() - start).total_seconds() * 1000
        col.success(f"✅ {name} ({int(latency)}ms)")
    except Exception as e:
        col.error(f"❌ {name}")

# Signal Feed
st.header("📡 Signal Feed")

# Try to load recent signals
signals_path = base_path / "signals.json"
if signals_path.exists():
    try:
        signals = json.loads(signals_path.read_text())
        for sig in signals[-5:]:
            st.write(f"🔔 {sig.get('time', 'N/A')}: {sig.get('signal', 'Unknown')}")
    except:
        st.info("No signals recorded yet")
else:
    st.info("Awaiting signals...")

# Wallet Tracking
st.header("🐋 Wallet Tracking")

whale_path = base_path / "whale_db.json"
smart_path = base_path / "smart_money.json"

c1, c2 = st.columns(2)

if whale_path.exists():
    try:
        whales = json.loads(whale_path.read_text())
        c1.metric("Tracked Whales", len(whales))
    except:
        c1.metric("Tracked Whales", 0)
else:
    c1.metric("Tracked Whales", 0)

if smart_path.exists():
    try:
        smart = json.loads(smart_path.read_text())
        c2.metric("Smart Wallets", len(smart.get("wallets", {})))
    except:
        c2.metric("Smart Wallets", 0)
else:
    c2.metric("Smart Wallets", 0)

# Risk Status
st.header("🛡️ Risk Status")

risk_cols = st.columns(4)
risk_cols[0].metric("Max Position", "10%")
risk_cols[1].metric("Max Daily Loss", "5%")
risk_cols[2].metric("Stop Loss", "15%")
risk_cols[3].metric("Take Profit", "40%")

# Narrative Heatmap
st.header("🔥 Narrative Heatmap")

narratives = ["AI Tokens", "Memecoins", "Gaming", "Layer2", "DeFi", "Solana"]
narrative_cols = st.columns(6)

for i, n in enumerate(narratives):
    # Placeholder - would connect to real data
    score = 50  # Would be dynamic
    if score > 70:
        narrative_cols[i].success(f"{n}: {score}")
    elif score > 40:
        narrative_cols[i].warning(f"{n}: {score}")
    else:
        narrative_cols[i].info(f"{n}: {score}")

# Recent Alerts
st.header("🔔 Recent Alerts")

alerts_path = base_path / "alerts.log"
if alerts_path.exists():
    try:
        lines = alerts_path.read_text().strip().split("\n")[-5:]
        for line in lines:
            if line:
                try:
                    alert = json.loads(line)
                    st.write(f"{alert.get('level', 'info').upper()}: {alert.get('message', '')}")
                except:
                    st.write(line[:100])
    except:
        st.info("No alerts yet")
else:
    st.info("No alerts logged yet")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh
if st.button("🔄 Refresh Now"):
    st.rerun()

# Auto-refresh every 30 seconds
import time
st.markdown(f"""
<script>
    setInterval(function() {{
        window.location.reload();
    }}, 30000);
</script>
""", unsafe_allow_html=True)
