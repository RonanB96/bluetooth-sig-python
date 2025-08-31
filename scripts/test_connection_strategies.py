#!/usr/bin/env python3
"""Test script with multiple connection strategies for problematic devices."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# pylint: disable=wrong-import-position
from bleak import BleakClient, BleakScanner


async def test_connection_strategies(mac_address: str):
    """Try multiple connection strategies."""
    print(f"🔍 Testing Multiple Connection Strategies: {mac_address}")
    print("=" * 60)

    # First, find the device
    device = await BleakScanner.find_device_by_address(mac_address)
    if not device:
        print("❌ Device not found")
        return False

    print(f"✅ Device found: {device.name or 'Unknown'}")

    strategies = [
        ("Short timeout", {"timeout": 10.0}),
        ("Long timeout", {"timeout": 60.0}),
        ("No services filter", {"timeout": 30.0, "services": None}),
    ]

    for strategy_name, kwargs in strategies:
        print(f"\n🔄 Strategy: {strategy_name}")
        print(f"   Parameters: {kwargs}")

        try:
            async with BleakClient(device, **kwargs) as client:
                print(f"   ✅ Connected successfully!")
                print(f"   Services available: {len(list(client.services))}")

                # Try to read one simple characteristic
                for service in client.services:
                    for char in service.characteristics:
                        if "read" in char.properties:
                            try:
                                value = await client.read_gatt_char(char)
                                print(f"   ✅ Read test successful: {len(value)} bytes")
                                return True
                            except Exception as e:
                                print(f"   ⚠️  Read test failed: {e}")
                                continue

                print(f"   ⚠️  No readable characteristics found")
                return True  # Connection successful even without reads

        except asyncio.TimeoutError:
            print(f"   ❌ Timeout error")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Try manual connection without context manager
    print(f"\n🔄 Strategy: Manual connection")
    client = None
    try:
        client = BleakClient(device)
        print("   Connecting manually...")
        await client.connect()
        print("   ✅ Manual connection successful!")

        # Force service discovery
        print("   Discovering services...")
        await asyncio.sleep(2.0)  # Give time for discovery

        services = list(client.services)
        print(f"   ✅ Found {len(services)} services")

        return True

    except Exception as e:
        print(f"   ❌ Manual connection failed: {e}")
    finally:
        if client and client.is_connected:
            await client.disconnect()

    return False


async def test_simple_connection(mac_address: str):
    """Test a very simple connection."""
    print(f"\n🔧 Simple Connection Test: {mac_address}")
    print("-" * 40)

    try:
        # Most basic connection possible
        async with BleakClient(mac_address, timeout=45.0) as client:
            print("✅ Simple connection successful!")
            return True
    except Exception as e:
        print(f"❌ Simple connection failed: {e}")
        return False


async def test_bluetoothctl_style(mac_address: str):
    """Test connection similar to bluetoothctl."""
    print(f"\n🔧 Bluetoothctl-style Test: {mac_address}")
    print("-" * 40)

    # Discover device fresh each time
    print("Discovering device...")
    devices = await BleakScanner.discover(timeout=5.0)
    target_device = None

    for device in devices:
        if device.address.upper() == mac_address.upper():
            target_device = device
            break

    if not target_device:
        print("❌ Device not found in fresh scan")
        return False

    print(f"✅ Fresh device found: {target_device.name}")

    # Try connection immediately after discovery
    try:
        client = BleakClient(target_device)
        await client.connect()
        print("✅ Connected!")

        # Minimal service check
        await asyncio.sleep(1.0)
        service_count = len(list(client.services))
        print(f"✅ Services: {service_count}")

        await client.disconnect()
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python test_connection_strategies.py <MAC_ADDRESS>")
        return

    mac_address = sys.argv[1].upper()

    # Try all strategies
    strategies = [
        test_simple_connection,
        test_bluetoothctl_style,
        test_connection_strategies,
    ]

    for strategy_func in strategies:
        success = await strategy_func(mac_address)
        if success:
            print(f"\n🎉 SUCCESS with {strategy_func.__name__}!")
            break
        else:
            print(f"\n❌ {strategy_func.__name__} failed")
    else:
        print(f"\n💡 All strategies failed. Try:")
        print(f"   1. sudo systemctl restart bluetooth")
        print(f"   2. bluetoothctl scan on")
        print(f"   3. bluetoothctl connect {mac_address}")
        print(f"   4. Check if device requires pairing")


if __name__ == "__main__":
    asyncio.run(main())
