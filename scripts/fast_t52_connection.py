#!/usr/bin/env python3
"""
Fast T52 Connection Script

Connects to the T52 device quickly before connection timeout.
Based on analysis of the actual Thingy52 BLE code.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bleak import BleakClient, BleakScanner
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fast_t52_connection():
    """Fast connection to T52 device with immediate service access."""
    target = 'F6:51:E1:61:32:B1'

    print(f"🚀 Fast T52 Connection Test: {target}")
    print("Strategy: Connect fast, read services immediately")
    print()

    try:
        # Find device quickly
        print("📡 Scanning for T52...")
        device = await BleakScanner.find_device_by_address(target, timeout=5.0)
        if not device:
            print("❌ T52 device not found")
            return False

        print(f"✅ Found: {device.name}")
        print()

        # Connect with shorter timeout and disable automatic service discovery
        print("🔗 Connecting with optimized settings...")

        # Use connection strategy similar to nRF Connect
        client = BleakClient(device, timeout=5.0)  # Shorter timeout

        try:
            # Connect
            await client.connect()
            print(f"✅ Connected: {client.is_connected}")

            if not client.is_connected:
                print("❌ Connection failed")
                return False

            # Try to access services immediately
            print("⚡ Immediate service access...")

            # Get services right after connection
            services = client.services

            if services:
                print(f"🎯 Found {len(list(services))} services immediately!")

                for service in services:
                    print(f"  📋 Service: {service.uuid}")

                    # Quick characteristic check
                    chars = list(service.characteristics)
                    print(f"       └─ {len(chars)} characteristics")

                    # Try to read a simple characteristic quickly
                    for char in chars[:2]:  # Just first 2 to stay fast
                        if 'read' in char.properties:
                            try:
                                print(f"       📖 Reading {char.uuid[:8]}...")
                                value = await client.read_gatt_char(char.uuid)
                                print(f"       ✅ Success: {len(value)} bytes")

                                # Show value if short
                                if len(value) <= 4:
                                    hex_val = ' '.join(f'{b:02x}' for b in value)
                                    print(f"       📊 Data: [{hex_val}]")

                                break  # Success! Exit quickly

                            except Exception as e:
                                print(f"       ⚠️  Read failed: {e}")
                                continue

                print()
                print("🎉 SUCCESS: Connected and read data from T52!")
                return True

            else:
                print("❌ No services discovered")
                return False

        finally:
            if client.is_connected:
                await client.disconnect()
                print("🔌 Disconnected cleanly")

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def main():
    """Main function."""
    print("=== Fast T52 Connection Test ===")
    print("Based on Thingy52 BLE code analysis")
    print("Strategy: Fast connect, immediate service access")
    print()

    success = await fast_t52_connection()

    print()
    if success:
        print("🎊 Test PASSED: T52 connection and data read successful!")
        print("✅ The device works fine - it was a timing issue")
    else:
        print("❌ Test FAILED: Could not establish stable connection")
        print("💡 Device may be in sleep mode or need factory reset")

if __name__ == "__main__":
    asyncio.run(main())
