#!/usr/bin/env python3
"""Bleak integration example - demonstrates pure SIG parsing with Bleak BLE library.

This example shows how to combine Bleak for BLE connections with bluetooth_sig
for standards-compliant data parsing. The separation of concerns allows you to
use the best tool for each task:
- Bleak: Reliable BLE connection management
- bluetooth_sig: Standards-compliant data interpretation

Requirements:
    pip install bleak

Usage:
    python with_bleak.py --address 12:34:56:78:9A:BC
    python with_bleak.py --scan  # Scan for devices first
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

# Import shared BLE utilities
from ble_utils import (
    BLEAK_AVAILABLE,
    scan_with_bleak,
    read_characteristics_bleak,
    parse_and_display_results,
    get_default_characteristic_uuids,
)

# Also import for notification patterns
try:
    from bleak import BleakClient
except ImportError:
    print("❌ Bleak not available. Install with: pip install bleak")


async def read_and_parse_with_bleak(address: str, characteristic_uuids: list[str] = None) -> dict:
    """Read characteristics from a BLE device and parse with SIG standards.

    Args:
        address: BLE device address (e.g., "12:34:56:78:9A:BC")
        characteristic_uuids: List of UUIDs to read, or None to discover all

    Returns:
        Dictionary of parsed characteristic data
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for connections")
        return {}

    # Use shared utilities for reading
    target_uuids = characteristic_uuids or get_default_characteristic_uuids()
    raw_results = await read_characteristics_bleak(address, target_uuids)

    # Parse and display results
    return await parse_and_display_results(raw_results, "Bleak")


async def handle_notifications(address: str, duration: int = 30) -> None:
    """Monitor BLE notifications with SIG parsing.

    Args:
        address: BLE device address
        duration: Duration to monitor notifications in seconds
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for notifications")
        return

    translator = BluetoothSIGTranslator()
    notification_count = 0

    def notification_handler(sender, data):
        nonlocal notification_count
        notification_count += 1

        # Extract UUID from sender
        char_uuid = sender.uuid[4:8].upper() if len(sender.uuid) > 8 else sender.uuid.upper()

        # Parse with SIG standards
        result = translator.parse_characteristic(char_uuid, data)

        if result.parse_success:
            unit_str = f" {result.unit}" if result.unit else ""
            print(f"🔔 Notification #{notification_count}: {result.name} = {result.value}{unit_str}")
        else:
            print(f"🔔 Notification #{notification_count}: Raw data from {char_uuid}: {data.hex()}")

    print(f"🔔 Starting notification monitoring for {duration}s...")

    try:
        async with BleakClient(address, timeout=10.0) as client:
            print("✅ Connected for notifications")

            # Subscribe to all notifiable characteristics
            subscribed_count = 0
            for service in client.services:
                for char in service.characteristics:
                    if "notify" in char.properties:
                        char_name = char.description or f"Char-{char.uuid[4:8]}"
                        print(f"📡 Subscribing to {char_name} notifications...")
                        await client.start_notify(char.uuid, notification_handler)
                        subscribed_count += 1

            if subscribed_count == 0:
                print("❌ No notifiable characteristics found")
                return

            print(f"📡 Subscribed to {subscribed_count} characteristics")

            # Wait for notifications
            await asyncio.sleep(duration)

            print(f"\n📊 Monitoring complete. Received {notification_count} notifications.")

    except Exception as e:
        print(f"❌ Notification monitoring failed: {e}")


async def demonstrate_bleak_integration_patterns():
    """Demonstrate different integration patterns with Bleak."""
    print("\n🔧 Bleak Integration Patterns")
    print("=" * 50)

    # Show the basic pattern
    print("""
# Pattern 1: Simple characteristic reading
async def read_battery_level(address: str) -> int:
    translator = BluetoothSIGTranslator()

    async with BleakClient(address) as client:
        # Bleak handles connection
        raw_data = await client.read_gatt_char("2A19")

        # bluetooth_sig handles parsing
        result = translator.parse_characteristic("2A19", raw_data)
        return result.value if result.parse_success else None

# Pattern 2: Service-based reading
async def read_environmental_sensors(address: str) -> dict:
    translator = BluetoothSIGTranslator()
    results = {}

    async with BleakClient(address) as client:
        # Read multiple environmental characteristics
        for uuid in ["2A6E", "2A6F", "2A6D"]:  # Temperature, Humidity, Pressure
            try:
                raw_data = await client.read_gatt_char(uuid)
                result = translator.parse_characteristic(uuid, raw_data)
                results[uuid] = result.value
            except Exception:
                pass  # Handle missing characteristics gracefully

    return results

# Pattern 3: Notification handling
async def handle_notifications(address: str):
    translator = BluetoothSIGTranslator()

    def notification_handler(sender, data):
        # Parse notifications using SIG standards
        uuid = sender.uuid[4:8]  # Extract short UUID
        result = translator.parse_characteristic(uuid, data)
        print(f"📨 {result.name}: {result.value} {result.unit}")

    async with BleakClient(address) as client:
        await client.start_notify("2A37", notification_handler)  # Heart rate
        await asyncio.sleep(30)  # Listen for 30 seconds
        await client.stop_notify("2A37")
    """)


async def discover_services_and_characteristics(address: str) -> dict:
    """Discover all services and characteristics on a device.

    Args:
        address: BLE device address

    Returns:
        Dictionary of discovered services and characteristics
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for service discovery")
        return {}

    translator = BluetoothSIGTranslator()
    discovery_results = {}

    print(f"🔄 Discovering services on {address}...")

    try:
        async with BleakClient(address, timeout=10.0) as client:
            print("✅ Connected for service discovery")

            services = client.services

            for service in services:
                service_info = translator.get_service_info(service.uuid)
                service_name = service_info.name if service_info else "Unknown Service"

                print(f"\n🔧 Service: {service_name} ({service.uuid[:8]}...)")

                service_chars = []
                for char in service.characteristics:
                    char_uuid_short = char.uuid[4:8].upper() if len(char.uuid) > 8 else char.uuid.upper()
                    char_info = translator.get_characteristic_info(char_uuid_short)
                    char_name = char_info.name if char_info else char.description

                    service_chars.append({
                        'uuid': char_uuid_short,
                        'name': char_name,
                        'properties': list(char.properties)
                    })

                    print(f"  📋 {char_name} ({char_uuid_short}) - {', '.join(char.properties)}")

                discovery_results[service.uuid] = {
                    'name': service_name,
                    'characteristics': service_chars
                }

    except Exception as e:
        print(f"❌ Service discovery failed: {e}")

    return discovery_results


async def main():
    """Main function to demonstrate Bleak + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(description="Bleak + bluetooth_sig integration example")
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds")
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific characteristic UUIDs to read")
    parser.add_argument("--notifications", "-n", action="store_true", help="Monitor notifications")
    parser.add_argument("--discover", "-d", action="store_true", help="Discover services")
    parser.add_argument("--duration", type=int, default=30, help="Duration for notifications")

    args = parser.parse_args()

    print("🚀 Bleak + Bluetooth SIG Integration Demo")
    print("=" * 50)

    if not BLEAK_AVAILABLE:
        print("\n❌ This example requires Bleak. Install with:")
        print("    pip install bleak")
        return

    try:
        if args.scan or not args.address:
            # Scan for devices
            await scan_with_bleak(args.timeout)

            if not args.address:
                print("\n💡 Use --address with one of the discovered addresses to connect")
                return

        if args.address:
            if args.notifications:
                await handle_notifications(args.address, args.duration)
            elif args.discover:
                await discover_services_and_characteristics(args.address)
            else:
                # Connect and read characteristics
                print(f"\n🔗 Connecting to {args.address}...")
                results = await read_and_parse_with_bleak(args.address, args.uuids)

                if results:
                    print(f"\n📋 Summary of parsed data:")
                    for uuid, result in results.items():
                        if result.parse_success:
                            unit_str = f" {result.unit}" if result.unit else ""
                            print(f"  {result.name}: {result.value}{unit_str}")

        # Show integration patterns
        await demonstrate_bleak_integration_patterns()

        print("\n✅ Demo completed!")
        print("This example shows how bluetooth_sig provides pure SIG parsing")
        print("while Bleak handles all BLE connection complexity.")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
