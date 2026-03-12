#!/usr/bin/env python3
"""
Telegram Bot Setup for Nova Proactive Messaging

To set up Telegram messaging:

1. Create a bot via @BotFather on Telegram:
   - Open Telegram, search for @BotFather
   - Send /newbot
   - Follow prompts to name your bot
   - You'll get a bot token (like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)

2. Get your chat ID:
   - Search for @userinfobot on Telegram
   - Send /start
   - It'll show your user ID (that's your chat_id)

3. Edit this file with your credentials:
   ~/.nova/proactive_config.json

Or run: python nova_telegram_setup.py
"""

import json
import os

CONFIG_FILE = os.path.expanduser("~/.nova/proactive_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def setup():
    config = load_config()
    
    print("=== Nova Telegram Setup ===\n")
    print("You'll need:")
    print("1. Bot token from @BotFather")
    print("2. Your chat ID from @userinfobot\n")
    
    bot_token = input("Enter bot token (or press Enter to skip): ").strip()
    chat_id = input("Enter your chat ID (or press Enter to skip): ").strip()
    
    if "telegram" not in config:
        config["telegram"] = {}
    
    if bot_token:
        config["telegram"]["bot_token"] = bot_token
    if chat_id:
        config["telegram"]["chat_id"] = chat_id
    
    save_config(config)
    
    if bot_token and chat_id:
        print("\n✅ Config saved! Testing connection...")
        test_send(bot_token, chat_id)
    else:
        print("\n⚠️ Config saved but incomplete. Fill in the blanks to enable.")

def test_send(token, chat_id):
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": "👑 Nova proactive messaging is now configured!"
        }
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200:
            print("✅ Test message sent successfully!")
        else:
            print(f"❌ Failed: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup()
