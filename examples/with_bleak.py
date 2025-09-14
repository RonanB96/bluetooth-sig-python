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

# Import shared BLE utilities
from ble_utils import (
    BLEAK_AVAILABLE,
    comprehensive_device_analysis_bleak,
    discover_services_and_characteristics_bleak,
    handle_notifications_bleak,
    parse_and_display_results,
    read_characteristics_bleak,
    scan_with_bleak,
)

# Also import for notification patterns
try:
    pass  # BleakClient not needed as it's imported in ble_utils
except ImportError:
    print("❌ Bleak not available. Install with: pip install bleak")


async def read_and_parse_with_bleak(
    address: str, characteristic_uuids: list[str] = None
) -> dict:
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

    if characteristic_uuids is None:
        # Use comprehensive device analysis for real device discovery
        print("🔍 Using comprehensive device analysis...")
        return await comprehensive_device_analysis_bleak(address)

    # Use targeted reading for specific UUIDs (legacy mode)
    print("📋 Reading specific characteristics...")
    raw_results = await read_characteristics_bleak(address, characteristic_uuids)
    return await parse_and_display_results(raw_results, "Bleak")


async def handle_notifications(address: str, duration: int = 30) -> None:
    """Monitor BLE notifications with SIG parsing.

    Args:
        address: BLE device address
        duration: Duration to monitor notifications in seconds
    """
    await handle_notifications_bleak(address, duration)


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
                if result.parse_success:
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
    return await discover_services_and_characteristics_bleak(address)


async def handle_scan_mode(args: argparse.Namespace) -> None:
    """Handle scan-only mode."""
    await scan_with_bleak(args.timeout)
    if not args.address:
        print("Scan complete. Use --address to connect.")


async def handle_device_operations(args: argparse.Namespace) -> None:
    """Handle device-specific operations."""
    if args.notifications:
        await handle_notifications(args.address, args.duration)
    elif args.discover:
        await discover_services_and_characteristics(args.address)
    else:
        results = await read_and_parse_with_bleak(args.address, args.uuids)
        if results:
            display_results(results)


def display_results(results: dict) -> None:
    """Display parsed results in a consistent format."""
    if isinstance(results, dict) and "parsed_data" in results:
        for _uuid, data in results["parsed_data"].items():
            unit_str = f" {data['unit']}" if data["unit"] else ""
            print(f"{data['name']}: {data['value']}{unit_str}")
    elif isinstance(results, dict):
        for _uuid, data in results.items():
            if isinstance(data, dict) and "name" in data:
                unit_str = f" {data['unit']}" if data.get("unit") else ""
                print(f"{data['name']}: {data['value']}{unit_str}")
            elif hasattr(
                data, "name"
            ):  # Handle CharacteristicData/CharacteristicInfo objects
                unit_str = f" {data.unit}" if data.unit else ""
                print(f"{data.name}: {getattr(data, 'value', 'N/A')}{unit_str}")


async def main():  # pylint: disable=too-many-nested-blocks
    """Main function to demonstrate Bleak + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(
        description="Bleak + bluetooth_sig integration example"
    )
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument(
        "--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds"
    )
    parser.add_argument(
        "--uuids", "-u", nargs="+", help="Specific characteristic UUIDs to read"
    )
    parser.add_argument(
        "--notifications", "-n", action="store_true", help="Monitor notifications"
    )
    parser.add_argument(
        "--discover", "-d", action="store_true", help="Discover services"
    )
    parser.add_argument(
        "--duration", type=int, default=30, help="Duration for notifications"
    )

    args = parser.parse_args()

    if not BLEAK_AVAILABLE:
        print("Bleak not available. Install with: pip install bleak")
        return

    try:
        if args.scan or not args.address:
            await handle_scan_mode(args)
            return

        if args.address:
            await handle_device_operations(args)

    except KeyboardInterrupt:
        print("Demo interrupted by user")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
