#!/usr/bin/env python3
"""Run Nova Core forever"""
import asyncio
import sys
sys.path.insert(0, '.')
from core.nova_core_full import NovaCore

async def main():
    nova = NovaCore()
    print("Nova running forever...")
    await nova.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
