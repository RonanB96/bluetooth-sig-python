#!/usr/bin/env python3
"""Bleak-retry-connector integration example - robust BLE connections with SIG parsing.

This example demonstrates using bleak-retry-connector for reliable BLE connections
combined with bluetooth_sig for standards-compliant data parsing. This is the
recommended pattern for production applications.

Benefits:
- Automatic retry logic for unreliable BLE connections
- Connection recovery and error handling
- Pure SIG standards parsing
- Production-ready robustness

Requirements:
    pip install bleak-retry-connector bleak

Usage:
    python with_bleak_retry.py --address 12:34:56:78:9A:BC
    python with_bleak_retry.py --scan
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import shared BLE utilities
from ble_utils import (
    BLEAK_RETRY_AVAILABLE,
    get_default_characteristic_uuids,
    parse_and_display_results,
    read_characteristics_bleak_retry,
    scan_with_bleak,
)

from bluetooth_sig import BluetoothSIGTranslator

# Also import for robust patterns
try:
    from bleak import BleakClient
    from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
except ImportError:
    print("❌ Bleak-retry-connector not available. Install with:")
    print("    pip install bleak-retry-connector bleak")


async def robust_device_reading(address: str, retries: int = 3) -> dict:
    """Robust device reading with automatic retry and error recovery.

    Args:
        address: BLE device address
        retries: Number of connection retry attempts

    Returns:
        Dictionary of parsed characteristic data
    """
    if not BLEAK_RETRY_AVAILABLE:
        print("❌ Bleak-retry-connector not available")
        return {}

    # Use shared utilities for robust reading
    target_uuids = get_default_characteristic_uuids()
    raw_results = await read_characteristics_bleak_retry(
        address, target_uuids, max_attempts=retries
    )

    # Parse and display results
    return await parse_and_display_results(raw_results, "Bleak-Retry-Connector")


async def robust_service_discovery(address: str) -> dict:
    """Discover all services and characteristics with robust connection.

    Args:
        address: BLE device address

    Returns:
        Dictionary of discovered services and characteristics
    """
    if not BLEAK_RETRY_AVAILABLE:
        print("❌ Bleak-retry-connector not available")
        return {}

    translator = BluetoothSIGTranslator()
    discovery_results = {}

    print(f"🔄 Discovering services on {address} with robust connection...")

    try:
        async with establish_connection(
            BleakClientWithServiceCache, address, timeout=10.0, max_attempts=3
        ) as client:
            print("✅ Connected for service discovery")

            services = client.services

            for service in services:
                service_info = translator.get_service_info(service.uuid)
                service_name = service_info.name if service_info else "Unknown Service"

                print(f"\n🔧 Service: {service_name} ({service.uuid[:8]}...)")

                service_chars = []
                for char in service.characteristics:
                    char_uuid_short = (
                        char.uuid[4:8].upper()
                        if len(char.uuid) > 8
                        else char.uuid.upper()
                    )
                    char_info = translator.get_characteristic_info(char_uuid_short)
                    char_name = char_info.name if char_info else char.description

                    service_chars.append(
                        {
                            "uuid": char_uuid_short,
                            "name": char_name,
                            "properties": list(char.properties),
                        }
                    )

                    print(
                        f"  📋 {char_name} ({char_uuid_short}) - {', '.join(char.properties)}"
                    )

                discovery_results[service.uuid] = {
                    "name": service_name,
                    "characteristics": service_chars,
                }

    except Exception as e:
        print(f"❌ Service discovery failed: {e}")

    return discovery_results


async def continuous_monitoring(address: str, duration: int = 60) -> None:
    """Continuously monitor a device with automatic reconnection.

    Args:
        address: BLE device address
        duration: Monitoring duration in seconds
    """
    if not BLEAK_RETRY_AVAILABLE:
        print("❌ Bleak-retry-connector not available")
        return

    print(f"📊 Starting continuous monitoring of {address} for {duration}s...")
    print("🔄 Auto-reconnection enabled")

    translator = BluetoothSIGTranslator()
    target_uuids = ["2A19", "2A6E", "2A6F"]  # Battery, Temperature, Humidity

    import time

    start_time = time.time()
    reading_count = 0

    try:
        while time.time() - start_time < duration:
            try:
                # Use robust connection with retry
                raw_results = await read_characteristics_bleak_retry(
                    address, target_uuids, max_attempts=3
                )

                if raw_results:
                    reading_count += 1
                    print(
                        f"\n📊 Reading #{reading_count} at {time.strftime('%H:%M:%S')}:"
                    )

                    for uuid_short, (raw_data, _) in raw_results.items():
                        result = translator.parse_characteristic(uuid_short, raw_data)
                        if result.parse_success:
                            unit_str = f" {result.unit}" if result.unit else ""
                            print(f"   {result.name}: {result.value}{unit_str}")

                # Wait between readings
                await asyncio.sleep(5)

            except Exception as e:
                print(f"⚠️  Reading failed, retrying in 5s: {e}")
                await asyncio.sleep(5)

    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped by user after {reading_count} readings")


async def notification_monitoring(address: str, duration: int = 60) -> None:
    """Monitor device notifications with robust connection.

    Args:
        address: BLE device address
        duration: Monitoring duration in seconds
    """
    if not BLEAK_RETRY_AVAILABLE:
        print("❌ Bleak-retry-connector not available")
        return

    translator = BluetoothSIGTranslator()
    notification_count = 0

    def notification_handler(sender, data):
        nonlocal notification_count
        notification_count += 1

        # Extract UUID from sender
        char_uuid = (
            sender.uuid[4:8].upper() if len(sender.uuid) > 8 else sender.uuid.upper()
        )

        # Parse with SIG standards
        result = translator.parse_characteristic(char_uuid, data)

        if result.parse_success:
            unit_str = f" {result.unit}" if result.unit else ""
            print(
                f"🔔 Notification #{notification_count}: {result.name} = {result.value}{unit_str}"
            )
        else:
            print(
                f"🔔 Notification #{notification_count}: Raw data from {char_uuid}: {data.hex()}"
            )

    print(f"🔔 Starting notification monitoring for {duration}s...")

    try:
        async with establish_connection(
            BleakClientWithServiceCache, address, timeout=10.0
        ) as client:
            print("✅ Connected for notifications")

            # Subscribe to all notifiable characteristics
            for service in client.services:
                for char in service.characteristics:
                    if "notify" in char.properties:
                        char_name = char.description or f"Char-{char.uuid[4:8]}"
                        print(f"📡 Subscribing to {char_name} notifications...")
                        await client.start_notify(char.uuid, notification_handler)

            # Wait for notifications
            await asyncio.sleep(duration)

            print(
                f"\n📊 Monitoring complete. Received {notification_count} notifications."
            )

    except Exception as e:
        print(f"❌ Notification monitoring failed: {e}")


async def main():
    """Main function demonstrating robust BLE patterns."""
    parser = argparse.ArgumentParser(
        description="Robust BLE with bleak-retry-connector + SIG parsing"
    )
    parser.add_argument("--address", "-a", help="BLE device address")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument(
        "--monitor", "-m", action="store_true", help="Continuous monitoring"
    )
    parser.add_argument(
        "--notifications", "-n", action="store_true", help="Monitor notifications"
    )
    parser.add_argument(
        "--discover", "-d", action="store_true", help="Service discovery"
    )
    parser.add_argument(
        "--duration", "-t", type=int, default=60, help="Duration for monitoring"
    )

    args = parser.parse_args()

    print("🚀 Bleak-Retry-Connector + Bluetooth SIG Integration Demo")
    print("=" * 65)

    if not BLEAK_RETRY_AVAILABLE:
        print("❌ This example requires bleak-retry-connector. Install with:")
        print("    pip install bleak-retry-connector bleak")
        return

    try:
        if args.scan:
            await scan_with_bleak()

            if not args.address:
                print("\n💡 Use --address with one of the discovered addresses")
                return

        if args.address:
            if args.monitor:
                await continuous_monitoring(args.address, args.duration)
            elif args.notifications:
                await notification_monitoring(args.address, args.duration)
            elif args.discover:
                await robust_service_discovery(args.address)
            else:
                await robust_device_reading(args.address)
        else:
            print("❌ No device address provided. Use --scan to discover devices.")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")


if __name__ == "__main__":
    asyncio.run(main())
