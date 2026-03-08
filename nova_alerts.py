#!/usr/bin/env python3
"""
nova_alerts.py — Alert System.
Telegram, Discord, and logging alerts.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum


class AlertLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    WHALE = "whale"
    TRADE = "trade"


class AlertSystem:
    """Manages alerts across multiple channels."""
    
    def __init__(self):
        self.alerts = []
        self.telegram_config = self._load_telegram()
        self.discord_config = self._load_discord()
        self.log_path = Path(__file__).parent / "alerts.log"
        
    def _load_telegram(self) -> Dict:
        """Load Telegram config."""
        return {
            "enabled": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
        }
    
    def _load_discord(self) -> Dict:
        """Load Discord config."""
        return {
            "enabled": bool(os.getenv("DISCORD_WEBHOOK")),
            "webhook": os.getenv("DISCORD_WEBHOOK", "")
        }
    
    async def send(self, message: str, level: AlertLevel = AlertLevel.INFO, 
                   details: Dict = None):
        """Send alert to all configured channels."""
        alert = {
            "level": level.value,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.alerts.append(alert)
        
        # Keep last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Log to file
        self._log(alert)
        
        # Send to Telegram
        if self.telegram_config["enabled"]:
            await self._send_telegram(alert)
        
        # Send to Discord
        if self.discord_config["enabled"]:
            await self._send_discord(alert)
        
        return alert
    
    def _log(self, alert: Dict):
        """Log alert to file."""
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(alert) + "\n")
        except:
            pass
    
    async def _send_telegram(self, alert: Dict):
        """Send alert to Telegram."""
        import aiohttp
        
        token = self.telegram_config["bot_token"]
        chat_id = self.telegram_config["chat_id"]
        
        if not token or not chat_id:
            return
        
        # Format message
        emoji = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "whale": "🐋",
            "trade": "📈"
        }
        
        text = f"{emoji.get(alert['level'], 'ℹ️')} {alert['message']}"
        
        if alert.get("details"):
            for k, v in alert["details"].items():
                text += f"\n{k}: {v}"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={
                    "chat_id": chat_id,
                    "text": text
                })
        except Exception as e:
            print(f"Telegram error: {e}")
    
    async def _send_discord(self, alert: Dict):
        """Send alert to Discord."""
        import aiohttp
        
        webhook = self.discord_config["webhook"]
        
        if not webhook:
            return
        
        # Format embed
        colors = {
            "info": 3447003,
            "success": 3066993,
            "warning": 16776960,
            "error": 15158332,
            "whale": 10181046,
            "trade": 5763714
        }
        
        embed = {
            "title": alert["message"],
            "color": colors.get(alert["level"], 3447003),
            "timestamp": alert["timestamp"],
            "fields": []
        }
        
        if alert.get("details"):
            for k, v in alert["details"].items():
                embed["fields"].append({
                    "name": k,
                    "value": str(v),
                    "inline": True
                })
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(webhook, json={"embeds": [embed]})
        except Exception as e:
            print(f"Discord error: {e}")
    
    # Convenience methods
    async def whale_alert(self, wallet: str, token: str, amount: float):
        """Send whale alert."""
        await self.send(
            f"🐋 Whale Alert: ${amount:,.0f} into {token}",
            AlertLevel.WHALE,
            {"wallet": wallet[:10] + "...", "token": token, "amount": f"${amount:,.0f}"}
        )
    
    async def trade_executed(self, token: str, side: str, amount: float, price: float):
        """Send trade executed alert."""
        await self.send(
            f"📈 Trade: {side} {token}",
            AlertLevel.TRADE,
            {"token": token, "side": side, "amount": f"${amount:,.0f}", "price": f"${price:.6f}"}
        )
    
    async def risk_alert(self, reason: str):
        """Send risk alert."""
        await self.send(
            f"⚠️ Risk Alert: {reason}",
            AlertLevel.WARNING,
            {"reason": reason}
        )
    
    async def error_alert(self, error: str):
        """Send error alert."""
        await self.send(
            f"❌ Error: {error}",
            AlertLevel.ERROR,
            {"error": error}
        )
    
    async def system_status(self, status: str):
        """Send system status."""
        await self.send(
            f"ℹ️ System: {status}",
            AlertLevel.INFO,
            {"status": status}
        )
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts."""
        return self.alerts[-limit:]


# Singleton
_alert_system: Optional[AlertSystem] = None


def get_alert_system() -> AlertSystem:
    """Get alert system singleton."""
    global _alert_system
    if _alert_system is None:
        _alert_system = AlertSystem()
    return _alert_system


if __name__ == "__main__":
    import asyncio
    
    async def test():
        alerts = get_alert_system()
        await alerts.system_status("Nova trading system started")
        await alerts.whale_alert("0x1234...", "BONK", 50000)
        await alerts.trade_executed("BONK", "BUY", 1000, 0.00042)
    
    asyncio.run(test())
    print("Alerts configured")
