#!/usr/bin/env python3
"""Enhanced Service Explorer - SIG library integration showcase.

Based on Bleak's service_explorer.py with comprehensive Bluetooth SIG library
integration. This example demonstrates the proper discovery pattern:

1. Use name-based lookups when you know what you want
2. Use UUID-based lookups only for exploring unknown services/characteristics
3. Parse all readable characteristics with SIG standards compliance

This showcases how the SIG library transforms raw BLE exploration into
structured, standards-compliant information discovery.

Requirements:
    pip install bleak

Usage:
    python enhanced_service_explorer.py --address 12:34:56:78:9A:BC
    python enhanced_service_explorer.py --scan  # Scan first
    python enhanced_service_explorer.py --mock  # Use mock data (no hardware)
"""

# pylint: disable=import-error,broad-exception-caught,possibly-used-before-assignment

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import shared utilities
from ble_utils import (
    BLEAK_AVAILABLE,
    mock_ble_data,
    scan_with_bleak,
)

from bluetooth_sig import BluetoothSIGTranslator

# Try to import Bleak
if BLEAK_AVAILABLE:
    from bleak import BleakClient


async def enhanced_service_exploration(address: str, timeout: float = 10.0) -> None:
    """Enhanced service exploration with comprehensive SIG parsing.

    This demonstrates the recommended pattern for discovering and parsing
    services and characteristics using proper name vs UUID resolution.
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available. Install with: pip install bleak")
        return

    translator = BluetoothSIGTranslator()

    print(f"🔗 Connecting to device: {address}")

    try:
        async with BleakClient(address, timeout=timeout) as client:
            print("✅ Connected successfully!")
            print(f"📱 Device Name: {client.address}")

            # Service discovery and exploration
            await explore_services_with_sig_parsing(client, translator)

    except Exception as e:
        print(f"❌ Connection failed: {e}")


async def explore_services_with_sig_parsing(
    client, translator: BluetoothSIGTranslator
) -> None:
    """Comprehensive service exploration with SIG parsing.

    Shows the difference between name-based lookup (when you know what you want)
    and UUID-based discovery (when exploring unknown services).
    """
    print("\n" + "=" * 60)
    print("🔧 ENHANCED SERVICE EXPLORATION WITH SIG PARSING")
    print("=" * 60)

    # First, demonstrate targeted service reading (name-based lookup)
    await demonstrate_targeted_service_reading(client, translator)

    # Then, demonstrate discovery exploration (UUID-based lookup)
    await demonstrate_discovery_exploration(client, translator)


async def demonstrate_targeted_service_reading(
    client, translator: BluetoothSIGTranslator
) -> None:
    """Demonstrate targeted reading when you know what services you want.

    ✅ RECOMMENDED: Use name-based lookups when you know what you want.
    This is the typical pattern for production applications.
    """
    print("\n📍 PART 1: TARGETED SERVICE READING (Recommended Pattern)")
    print("-" * 50)
    print("When you know what services you need, use name-based lookups:")

    # Define services we want to read (by name, not UUID)
    desired_services = [
        "Battery",
        "Device Information",
        "Environmental Sensing",
        "Heart Rate",
        "Health Thermometer",
    ]

    for service_name in desired_services:
        await read_service_by_name(client, translator, service_name)


async def read_service_by_name(
    client, translator: BluetoothSIGTranslator, service_name: str
) -> None:
    """Read a specific service by name (not UUID).

    This demonstrates the recommended pattern for production applications.
    """
    print(f"\n🔎 Looking for service: '{service_name}'")

    # Step 1: Get service info by name to find its UUID
    service_info = translator.get_service_info_by_name(service_name)
    if not service_info:
        print(f"   ❓ '{service_name}' is not a known SIG service")
        return

    print(f"   📝 SIG Service: {service_info.name} (UUID: {service_info.uuid})")

    # Step 2: Find the service on device by matching UUID
    target_service = None
    for service in client.services:
        if str(service.uuid).upper() == service_info.uuid.upper():
            target_service = service
            break

    if not target_service:
        print(f"   ❌ Service '{service_name}' not found on device")
        return

    print("   ✅ Found service on device!")

    # Step 3: Read characteristics from this service
    await read_service_characteristics_by_name(
        client, translator, target_service, service_name
    )


async def read_service_characteristics_by_name(
    client, translator: BluetoothSIGTranslator, service, service_name: str
) -> None:
    """Read characteristics from a service using name-based lookups."""

    # Define characteristics we typically want from each service
    service_characteristics = {
        "Battery": ["Battery Level"],
        "Device Information": [
            "Manufacturer Name String",
            "Model Number String",
            "Serial Number String",
            "Hardware Revision String",
            "Firmware Revision String",
            "Software Revision String",
        ],
        "Environmental Sensing": [
            "Temperature",
            "Humidity",
            "Pressure",
            "Temperature Measurement",
        ],
        "Heart Rate": ["Heart Rate Measurement"],
        "Health Thermometer": ["Temperature Measurement"],
    }

    desired_chars = service_characteristics.get(service_name, [])
    if not desired_chars:
        print(
            f"   📋 No predefined characteristics for '{service_name}', exploring all..."
        )
        await explore_all_characteristics(client, translator, service)
        return

    print(f"   📋 Reading {len(desired_chars)} known characteristics:")

    for char_name in desired_chars:
        await read_characteristic_by_name(client, translator, service, char_name)


async def read_characteristic_by_name(
    client, translator: BluetoothSIGTranslator, service, char_name: str
) -> None:
    """Read a specific characteristic by name (not UUID)."""

    # Get characteristic info by name to find its UUID
    char_info = translator.get_characteristic_info_by_name(char_name)
    if not char_info:
        print(f"     ❓ '{char_name}' is not a known SIG characteristic")
        return

    # Find the characteristic on device by matching UUID
    target_char = None
    for char in service.characteristics:
        if str(char.uuid).upper() == char_info.uuid.upper():
            target_char = char
            break

    if not target_char:
        print(f"     ❌ '{char_name}' not found in service")
        return

    # Read and parse the characteristic
    if "read" not in target_char.properties:
        print(f"     ⚠️  '{char_name}' is not readable")
        return

    try:
        raw_data = await client.read_gatt_char(target_char)

        # Parse using name (not UUID) for consistency
        result = translator.parse_characteristic(char_info.uuid, raw_data)

        if result.parse_success:
            unit_str = f" {result.unit}" if result.unit else ""
            print(f"     ✅ {result.name}: {result.value}{unit_str}")
            print(f"        📊 SIG Standard: {char_info.name}")
            print(f"        🔢 Raw Data: {raw_data.hex()}")
        else:
            print(f"     ❌ {result.name}: Parse failed - {result.error_message}")
            print(f"        🔢 Raw Data: {raw_data.hex()}")

    except Exception as e:
        print(f"     ⚠️  Read error for '{char_name}': {e}")


async def demonstrate_discovery_exploration(
    client, translator: BluetoothSIGTranslator
) -> None:
    """Demonstrate discovery exploration for unknown services.

    ✅ ACCEPTABLE: Use UUID-based lookups for discovering unknown services.
    This is useful for device exploration and debugging.
    """
    print("\n🔍 PART 2: DISCOVERY EXPLORATION (For Unknown Services)")
    print("-" * 50)
    print("When exploring unknown devices, use UUID-based discovery:")

    service_count = 0

    for service in client.services:
        service_count += 1

        # Use UUID lookup to identify unknown services during discovery
        service_info = translator.get_service_info(service.uuid)
        if service_info:
            service_name = service_info.name
            service_status = "✅ Known SIG Service"
        else:
            service_name = "Custom Service"
            service_status = "❓ Unknown/Custom Service"

        print(f"\n🔧 Service #{service_count}: {service_name}")
        print(f"   📝 UUID: {service.uuid}")
        print(f"   📊 Status: {service_status}")

        await explore_all_characteristics(client, translator, service)


async def explore_all_characteristics(
    client, translator: BluetoothSIGTranslator, service
) -> None:
    """Explore all characteristics in a service."""

    if not service.characteristics:
        print("   📋 No characteristics found")
        return

    print(f"   📋 Found {len(service.characteristics)} characteristics:")

    for char in service.characteristics:
        # Use UUID lookup to identify unknown characteristics during discovery
        char_info = translator.get_characteristic_info(char.uuid)

        if char_info:
            char_name = char_info.name
            char_status = "✅ Known SIG Characteristic"
        else:
            char_name = "Unknown Characteristic"
            char_status = "❓ Unknown/Custom Characteristic"

        print(f"\n     🔧 {char_name}")
        print(f"        📝 UUID: {char.uuid}")
        print(f"        📊 Status: {char_status}")
        print(f"        🔑 Properties: {', '.join(char.properties)}")

        # Try to read if possible
        if "read" in char.properties:
            try:
                raw_data = await client.read_gatt_char(char)

                if char_info:
                    # Parse using SIG standards
                    result = translator.parse_characteristic(char.uuid, raw_data)

                    if result.parse_success:
                        unit_str = f" {result.unit}" if result.unit else ""
                        print(f"        ✅ Value: {result.value}{unit_str}")
                        print("        📈 SIG Compliant: Yes")
                    else:
                        print(f"        ❌ Parse failed: {result.error_message}")
                        print("        📈 SIG Compliant: No")
                else:
                    print(f"        📄 Raw Value: {raw_data.hex()}")
                    print("        📈 SIG Compliant: Unknown (custom characteristic)")

                print(f"        🔢 Raw Data: {raw_data.hex()}")

            except Exception as e:
                print(f"        ⚠️  Read error: {e}")
        else:
            print("        ⚠️  Not readable")


async def run_mock_demonstration() -> None:
    """Run demonstration with mock data when no hardware is available."""
    print("🧪 MOCK DATA DEMONSTRATION")
    print("=" * 50)
    print("Demonstrating SIG parsing with mock BLE data (no hardware needed)")

    translator = BluetoothSIGTranslator()
    mock_data = mock_ble_data()

    print("\n📊 Mock Device Services & Characteristics:")

    # Mock service data with known characteristics
    mock_services = {
        "Battery": {
            "uuid": "180F",
            "characteristics": {
                "Battery Level": {"uuid": "2A19", "data": mock_data["2A19"]}
            },
        },
        "Environmental Sensing": {
            "uuid": "181A",
            "characteristics": {
                "Temperature": {"uuid": "2A6E", "data": mock_data["2A6E"]},
                "Humidity": {"uuid": "2A6F", "data": mock_data["2A6F"]},
            },
        },
    }

    for service_name, service_data in mock_services.items():
        print(f"\n🔧 Mock Service: {service_name}")
        print(f"   📝 UUID: {service_data['uuid']}")

        for char_name, char_data in service_data["characteristics"].items():
            print(f"\n     🔧 {char_name}")
            print(f"        📝 UUID: {char_data['uuid']}")
            print(f"        🔢 Mock Data: {char_data['data'].hex()}")

            # Parse with SIG library
            result = translator.parse_characteristic(
                char_data["uuid"], char_data["data"]
            )

            if result.parse_success:
                unit_str = f" {result.unit}" if result.unit else ""
                print(f"        ✅ Parsed Value: {result.value}{unit_str}")
                print(f"        📊 SIG Standard: {result.name}")
            else:
                print(f"        ❌ Parse failed: {result.error_message}")


async def main():
    """Main entry point for enhanced service explorer."""
    parser = argparse.ArgumentParser(
        description="Enhanced BLE Service Explorer with Bluetooth SIG parsing"
    )
    parser.add_argument("--address", help="BLE device address to connect to")
    parser.add_argument(
        "--scan", action="store_true", help="Scan for nearby BLE devices"
    )
    parser.add_argument(
        "--mock", action="store_true", help="Run with mock data (no hardware required)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Connection timeout in seconds (default: 10.0)",
    )

    args = parser.parse_args()

    print("🚀 Enhanced Service Explorer with Bluetooth SIG Integration")
    print("Showcasing proper service discovery and standards-compliant parsing")
    print()

    if args.mock:
        await run_mock_demonstration()
        return

    if args.scan:
        print("🔍 Scanning for BLE devices...")
        devices = await scan_with_bleak(timeout=10.0)
        if devices:
            print(
                f"\n📱 Found {len(devices)} devices. Use --address with one of these:"
            )
            for device in devices[:5]:  # Show first 5
                print(f"   {device.address} - {device.name or 'Unknown'}")
        else:
            print("❌ No devices found")
        return

    if not args.address:
        print("❌ Error: Must specify --address, --scan, or --mock")
        print("Examples:")
        print("  python enhanced_service_explorer.py --scan")
        print("  python enhanced_service_explorer.py --address 12:34:56:78:9A:BC")
        print("  python enhanced_service_explorer.py --mock")
        return

    await enhanced_service_exploration(args.address, args.timeout)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
