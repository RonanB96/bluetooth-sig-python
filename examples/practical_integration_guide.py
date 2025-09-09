#!/usr/bin/env python3
"""Practical Integration Guide - Bluetooth SIG Library Best Practices.

This example demonstrates the recommended patterns for integrating the Bluetooth SIG
library with BLE connection libraries. It shows:

1. When to use name-based vs UUID-based lookups
2. Proper service discovery workflows
3. Production-ready error handling patterns
4. Performance optimization techniques

This serves as a practical reference for developers integrating the library.

Usage:
    python practical_integration_guide.py --demo-patterns
    python practical_integration_guide.py --mock-device
    python practical_integration_guide.py --address 12:34:56:78:9A:BC
"""

# pylint: disable=import-error,too-many-statements,too-many-locals,too-many-branches
# pylint: disable=too-many-return-statements,broad-exception-caught,possibly-used-before-assignment

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

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


class SIGIntegrationGuide:
    """Practical guide for integrating Bluetooth SIG library."""

    def __init__(self):
        self.translator = BluetoothSIGTranslator()

    def demonstrate_lookup_patterns(self) -> None:
        """Demonstrate when to use name vs UUID lookups."""

        print("🎯 LOOKUP PATTERN BEST PRACTICES")
        print("=" * 50)

        print("\n✅ RECOMMENDED: Name-based lookups when you know what you want")
        print("-" * 50)

        # Pattern 1: When you know what service you need
        print("\n📝 Pattern 1: Reading Battery Service")
        print("```python")
        print("# ✅ Good: Use name when you know what you want")
        print("service_info = translator.get_service_info_by_name('Battery')")
        print("char_info = translator.get_characteristic_info_by_name('Battery Level')")
        print("```")

        # Demonstrate this pattern
        service_info = self.translator.get_service_info_by_name("Battery")
        char_info = self.translator.get_characteristic_info_by_name("Battery Level")

        if service_info and char_info:
            print(
                f"Result: Found {service_info.name} ({service_info.uuid}) -> {char_info.name} ({char_info.uuid})"
            )

        print("\n📝 Pattern 2: Reading Device Information")
        print("```python")
        print("# ✅ Good: Use names for known characteristics")
        print("device_info_chars = [")
        print("    'Manufacturer Name String',")
        print("    'Model Number String',")
        print("    'Serial Number String'")
        print("]")
        print("for char_name in device_info_chars:")
        print("    char_info = translator.get_characteristic_info_by_name(char_name)")
        print("```")

        # Demonstrate this pattern
        device_info_chars = [
            "Manufacturer Name String",
            "Model Number String",
            "Serial Number String",
        ]

        print("Results:")
        for char_name in device_info_chars:
            char_info = self.translator.get_characteristic_info_by_name(char_name)
            if char_info:
                print(f"  ✅ {char_name} -> {char_info.uuid}")
            else:
                print(f"  ❌ {char_name} -> Not found")

        print("\n✅ ACCEPTABLE: UUID-based lookups for discovery")
        print("-" * 50)

        print("\n📝 Pattern 3: Service Discovery/Exploration")
        print("```python")
        print("# ✅ Acceptable: Use UUID lookup to identify unknown services")
        print("for service in client.services:")
        print("    service_info = translator.get_service_info(service.uuid)")
        print("    if service_info:")
        print("        print(f'Found known service: {service_info.name}')")
        print("    else:")
        print("        print(f'Unknown service: {service.uuid}')")
        print("```")

        # Demonstrate this pattern with mock UUIDs
        mock_service_uuids = ["180F", "181A", "1234"]  # Battery, Environmental, Unknown

        print("Results:")
        for uuid in mock_service_uuids:
            service_info = self.translator.get_service_info(uuid)
            if service_info:
                print(f"  ✅ {uuid} -> Known: {service_info.name}")
            else:
                print(f"  ❓ {uuid} -> Unknown/Custom service")

    def demonstrate_production_patterns(self) -> None:
        """Demonstrate production-ready integration patterns."""

        print("\n\n🏭 PRODUCTION-READY PATTERNS")
        print("=" * 50)

        print("\n📝 Pattern 1: Robust Service Reading")
        print("```python")
        print("async def read_battery_level_robust(client, translator):")
        print("    try:")
        print("        # Step 1: Get service info by name")
        print("        service_info = translator.get_service_info_by_name('Battery')")
        print("        if not service_info:")
        print("            return None  # Service not supported")
        print("")
        print("        # Step 2: Find service on device")
        print(
            "        battery_service = find_service_by_uuid(client, service_info.uuid)"
        )
        print("        if not battery_service:")
        print("            return None  # Service not available on device")
        print("")
        print("        # Step 3: Get characteristic info by name")
        print(
            "        char_info = translator.get_characteristic_info_by_name('Battery Level')"
        )
        print("        if not char_info:")
        print("            return None  # Characteristic not supported")
        print("")
        print("        # Step 4: Find characteristic on device")
        print(
            "        battery_char = find_characteristic_by_uuid(battery_service, char_info.uuid)"
        )
        print("        if not battery_char:")
        print("            return None  # Characteristic not available")
        print("")
        print("        # Step 5: Read and parse")
        print("        raw_data = await client.read_gatt_char(battery_char)")
        print(
            "        result = translator.parse_characteristic(char_info.uuid, raw_data)"
        )
        print("")
        print("        return result if result.parse_success else None")
        print("    except Exception as e:")
        print("        logger.error(f'Battery read failed: {e}')")
        print("        return None")
        print("```")

        print("\n📝 Pattern 2: Bulk Characteristic Reading")
        print("```python")
        print("async def read_device_information_bulk(client, translator):")
        print("    device_info = {}")
        print("    ")
        print("    # Define what we want to read")
        print("    desired_chars = [")
        print("        'Manufacturer Name String',")
        print("        'Model Number String',")
        print("        'Serial Number String',")
        print("        'Hardware Revision String',")
        print("        'Firmware Revision String'")
        print("    ]")
        print("    ")
        print("    for char_name in desired_chars:")
        print("        try:")
        print("            result = await read_characteristic_by_name(")
        print("                client, translator, 'Device Information', char_name")
        print("            )")
        print("            if result and result.parse_success:")
        print("                device_info[char_name] = result.value")
        print("        except Exception as e:")
        print("            device_info[char_name] = f'Error: {e}'")
        print("    ")
        print("    return device_info")
        print("```")

        print("\n📝 Pattern 3: Error Handling & Fallbacks")
        print("```python")
        print("def parse_with_fallback(translator, uuid, raw_data):")
        print("    try:")
        print("        # Try SIG parsing first")
        print("        result = translator.parse_characteristic(uuid, raw_data)")
        print("        if result.parse_success:")
        print("            return {")
        print("                'value': result.value,")
        print("                'unit': result.unit,")
        print("                'method': 'sig_standard',")
        print("                'reliable': True")
        print("            }")
        print("    except Exception as e:")
        print("        pass")
        print("    ")
        print("    # Fallback to raw data")
        print("    return {")
        print("        'value': raw_data.hex(),")
        print("        'unit': 'hex',")
        print("        'method': 'raw_fallback',")
        print("        'reliable': False")
        print("    }")
        print("```")

    def demonstrate_performance_patterns(self) -> None:
        """Demonstrate performance optimization patterns."""

        print("\n\n⚡ PERFORMANCE OPTIMIZATION PATTERNS")
        print("=" * 50)

        print("\n📝 Pattern 1: Cache Service/Characteristic Info")
        print("```python")
        print("class CachedSIGTranslator:")
        print("    def __init__(self):")
        print("        self.translator = BluetoothSIGTranslator()")
        print("        self._service_cache = {}")
        print("        self._char_cache = {}")
        print("    ")
        print("    def get_service_info_cached(self, name):")
        print("        if name not in self._service_cache:")
        print(
            "            self._service_cache[name] = self.translator.get_service_info_by_name(name)"
        )
        print("        return self._service_cache[name]")
        print("```")

        print("\n📝 Pattern 2: Batch UUID Resolution")
        print("```python")
        print("def resolve_multiple_characteristics(translator, uuids):")
        print("    results = {}")
        print("    for uuid in uuids:")
        print("        char_info = translator.get_characteristic_info(uuid)")
        print("        if char_info:")
        print("            results[uuid] = char_info")
        print("    return results")
        print("```")

        print("\n📝 Pattern 3: Lazy Loading")
        print("```python")
        print("class LazyCharacteristicReader:")
        print("    def __init__(self, client, translator):")
        print("        self.client = client")
        print("        self.translator = translator")
        print("        self._discovered_services = None")
        print("    ")
        print("    async def get_services(self):")
        print("        if self._discovered_services is None:")
        print("            self._discovered_services = await self._discover_services()")
        print("        return self._discovered_services")
        print("```")

    def demonstrate_error_patterns(self) -> None:
        """Demonstrate comprehensive error handling patterns."""

        print("\n\n🛡️  ERROR HANDLING PATTERNS")
        print("=" * 50)

        print("\n📝 Pattern 1: Graceful Degradation")
        print("```python")
        print(
            "async def read_with_graceful_degradation(client, translator, service_name, char_name):"
        )
        print("    try:")
        print("        # Try standard approach")
        print(
            "        result = await read_characteristic_by_name(client, translator, service_name, char_name)"
        )
        print("        if result and result.parse_success:")
        print("            return {'status': 'success', 'data': result}")
        print("    except Exception as e:")
        print("        pass")
        print("    ")
        print("    try:")
        print("        # Fallback: Try direct UUID if we have it")
        print(
            "        char_info = translator.get_characteristic_info_by_name(char_name)"
        )
        print("        if char_info:")
        print(
            "            raw_data = await read_characteristic_by_uuid(client, char_info.uuid)"
        )
        print("            return {'status': 'raw', 'data': raw_data.hex()}")
        print("    except Exception as e:")
        print("        pass")
        print("    ")
        print("    return {'status': 'failed', 'error': 'All methods failed'}")
        print("```")

        print("\n📝 Pattern 2: Validation with Fallback")
        print("```python")
        print(
            "def validate_parsed_result(result, expected_type=None, expected_range=None):"
        )
        print("    if not result.parse_success:")
        print("        return False, f'Parse failed: {result.error_message}'")
        print("    ")
        print("    if expected_type and not isinstance(result.value, expected_type):")
        print("        return False, f'Unexpected type: {type(result.value)}'")
        print("    ")
        print("    if expected_range and hasattr(result.value, '__float__'):")
        print("        value = float(result.value)")
        print("        if not (expected_range[0] <= value <= expected_range[1]):")
        print("            return False, f'Value out of range: {value}'")
        print("    ")
        print("    return True, 'Valid'")
        print("```")


async def demonstrate_with_mock_device() -> None:
    """Demonstrate patterns with a mock BLE device."""

    print("🧪 MOCK DEVICE DEMONSTRATION")
    print("=" * 50)
    print("Demonstrating integration patterns with mock BLE device data")

    guide = SIGIntegrationGuide()
    mock_data = mock_ble_data()

    # Mock device with services and characteristics
    mock_device = {
        "services": {
            "180F": {  # Battery Service
                "name": "Battery",
                "characteristics": {
                    "2A19": {  # Battery Level
                        "name": "Battery Level",
                        "data": mock_data["2A19"],
                        "properties": ["read", "notify"],
                    }
                },
            },
            "181A": {  # Environmental Sensing
                "name": "Environmental Sensing",
                "characteristics": {
                    "2A6E": {  # Temperature
                        "name": "Temperature",
                        "data": mock_data["2A6E"],
                        "properties": ["read", "notify"],
                    },
                    "2A6F": {  # Humidity
                        "name": "Humidity",
                        "data": mock_data["2A6F"],
                        "properties": ["read"],
                    },
                },
            },
        }
    }

    print("\n🔧 Mock Device Structure:")
    for service_uuid, service_data in mock_device["services"].items():
        print(f"  📋 Service: {service_data['name']} ({service_uuid})")
        for char_uuid, char_data in service_data["characteristics"].items():
            print(
                f"    📄 {char_data['name']} ({char_uuid}) - {char_data['properties']}"
            )

    # Demonstrate Pattern 1: Name-based reading (recommended)
    print("\n✅ Pattern 1: Name-based reading (when you know what you want)")

    # Read battery level by name
    print("\n📊 Reading Battery Level by name:")
    service_info = guide.translator.get_service_info_by_name("Battery")
    char_info = guide.translator.get_characteristic_info_by_name("Battery Level")

    if service_info and char_info:
        print(f"  🔍 Found service: {service_info.name} ({service_info.uuid})")
        print(f"  🔍 Found characteristic: {char_info.name} ({char_info.uuid})")

        # Mock finding it on device
        if service_info.uuid in mock_device["services"]:
            service_data = mock_device["services"][service_info.uuid]
            if char_info.uuid in service_data["characteristics"]:
                char_data = service_data["characteristics"][char_info.uuid]
                raw_data = char_data["data"]

                # Parse with SIG library
                result = guide.translator.parse_characteristic(char_info.uuid, raw_data)

                print(f"  📄 Raw data: {raw_data.hex()}")
                if result.parse_success:
                    print(f"  ✅ Parsed value: {result.value} {result.unit}")
                    print("  📈 SIG compliant: Yes")
                else:
                    print(f"  ❌ Parse failed: {result.error_message}")

    # Demonstrate Pattern 2: UUID-based discovery (for exploration)
    print("\n✅ Pattern 2: UUID-based discovery (for exploration)")

    print("\n🔍 Discovering unknown services on device:")
    for service_uuid in mock_device["services"]:
        # Use UUID lookup to identify unknown services during discovery
        service_info = guide.translator.get_service_info(service_uuid)

        if service_info:
            print(f"  ✅ {service_uuid} -> Known SIG service: {service_info.name}")

            # Explore characteristics in this service
            service_data = mock_device["services"][service_uuid]
            for char_uuid in service_data["characteristics"]:
                char_info = guide.translator.get_characteristic_info(char_uuid)
                if char_info:
                    print(
                        f"    📄 {char_uuid} -> Known SIG characteristic: {char_info.name}"
                    )
                else:
                    print(f"    ❓ {char_uuid} -> Unknown/custom characteristic")
        else:
            print(f"  ❓ {service_uuid} -> Unknown/custom service")

    # Demonstrate Pattern 3: Bulk reading
    print("\n✅ Pattern 3: Bulk reading of device information")

    # Mock device information service
    mock_device_info = {
        "2A29": b"ExampleCorp\x00",  # Manufacturer
        "2A24": b"SensorPro\x00",  # Model
        "2A25": b"12345\x00",  # Serial
    }

    device_info_chars = [
        "Manufacturer Name String",
        "Model Number String",
        "Serial Number String",
    ]

    device_info_results = {}

    for char_name in device_info_chars:
        char_info = guide.translator.get_characteristic_info_by_name(char_name)
        if char_info and char_info.uuid in mock_device_info:
            raw_data = mock_device_info[char_info.uuid]
            result = guide.translator.parse_characteristic(char_info.uuid, raw_data)

            if result.parse_success:
                device_info_results[char_name] = result.value
                print(f"  ✅ {char_name}: {result.value}")
            else:
                device_info_results[char_name] = f"Parse error: {result.error_message}"
                print(f"  ❌ {char_name}: Parse failed")
        else:
            device_info_results[char_name] = "Not available"
            print(f"  ❓ {char_name}: Not available")

    print("\n📊 Device Information Summary:")
    for key, value in device_info_results.items():
        print(f"   {key}: {value}")


async def run_with_real_device(address: str, timeout: float = 10.0) -> None:
    """Demonstrate patterns with a real BLE device."""

    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available. Install with: pip install bleak")
        return

    guide = SIGIntegrationGuide()

    print(f"🔗 Connecting to real device: {address}")

    try:
        async with BleakClient(address, timeout=timeout) as client:  # pylint: disable=possibly-used-before-assignment
            print("✅ Connected successfully!")

            # Demonstrate discovery pattern
            print("\n🔍 Service Discovery Pattern:")

            discovered_services = {}

            for service in client.services:
                # Use UUID lookup to identify services during discovery
                service_info = guide.translator.get_service_info(service.uuid)

                if service_info:
                    service_name = service_info.name
                    status = "✅ Known SIG Service"
                else:
                    service_name = "Unknown Service"
                    status = "❓ Unknown/Custom Service"

                discovered_services[service.uuid] = {
                    "name": service_name,
                    "status": status,
                    "characteristics": {},
                }

                print(f"  📋 {service_name} ({service.uuid}) - {status}")

                # Discover characteristics
                for char in service.characteristics:
                    char_info = guide.translator.get_characteristic_info(char.uuid)

                    if char_info:
                        char_name = char_info.name
                        char_status = "✅ Known SIG"
                    else:
                        char_name = "Unknown Characteristic"
                        char_status = "❓ Unknown/Custom"

                    discovered_services[service.uuid]["characteristics"][char.uuid] = {
                        "name": char_name,
                        "status": char_status,
                        "properties": list(char.properties),
                    }

                    print(f"    📄 {char_name} ({char.uuid}) - {char_status}")
                    print(f"       Properties: {', '.join(char.properties)}")

            # Demonstrate targeted reading
            print("\n✅ Targeted Reading Pattern:")

            # Try to read battery level if available
            battery_result = await read_characteristic_by_name(
                client, guide.translator, "Battery", "Battery Level"
            )

            if battery_result:
                print(f"  🔋 Battery Level: {battery_result}")
            else:
                print("  ❌ Battery Level not available")

            # Try to read device information
            device_info = await read_device_info_bulk(client, guide.translator)
            if device_info:
                print("  📱 Device Information:")
                for key, value in device_info.items():
                    print(f"     {key}: {value}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")


async def read_characteristic_by_name(
    client, translator, service_name: str, char_name: str
) -> Any:
    """Helper function to read a characteristic by service and characteristic names."""
    try:
        # Get service info by name
        service_info = translator.get_service_info_by_name(service_name)
        if not service_info:
            return None

        # Find service on device
        target_service = None
        for service in client.services:
            if str(service.uuid).upper() == service_info.uuid.upper():
                target_service = service
                break

        if not target_service:
            return None

        # Get characteristic info by name
        char_info = translator.get_characteristic_info_by_name(char_name)
        if not char_info:
            return None

        # Find characteristic on device
        target_char = None
        for char in target_service.characteristics:
            if str(char.uuid).upper() == char_info.uuid.upper():
                target_char = char
                break

        if not target_char:
            return None

        # Read and parse
        if "read" not in target_char.properties:
            return None

        raw_data = await client.read_gatt_char(target_char)
        result = translator.parse_characteristic(char_info.uuid, raw_data)

        return result if result.parse_success else None

    except Exception:
        return None


async def read_device_info_bulk(client, translator) -> dict[str, Any]:
    """Helper function to read device information in bulk."""
    device_info = {}

    device_info_chars = [
        "Manufacturer Name String",
        "Model Number String",
        "Serial Number String",
        "Hardware Revision String",
        "Firmware Revision String",
    ]

    for char_name in device_info_chars:
        result = await read_characteristic_by_name(
            client, translator, "Device Information", char_name
        )

        if result:
            device_info[char_name] = result.value
        else:
            device_info[char_name] = "Not available"

    return device_info


async def main():
    """Main entry point for practical integration guide."""

    parser = argparse.ArgumentParser(
        description="Practical Integration Guide for Bluetooth SIG Library"
    )
    parser.add_argument(
        "--demo-patterns",
        action="store_true",
        help="Demonstrate integration patterns and best practices",
    )
    parser.add_argument(
        "--mock-device",
        action="store_true",
        help="Demonstrate with mock device (no hardware required)",
    )
    parser.add_argument("--address", help="BLE device address for real device demo")
    parser.add_argument(
        "--scan", action="store_true", help="Scan for nearby BLE devices"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Connection timeout in seconds (default: 10.0)",
    )

    args = parser.parse_args()

    print("🚀 Practical Integration Guide for Bluetooth SIG Library")
    print("Comprehensive patterns and best practices for BLE integration")
    print()

    guide = SIGIntegrationGuide()

    if args.demo_patterns:
        guide.demonstrate_lookup_patterns()
        guide.demonstrate_production_patterns()
        guide.demonstrate_performance_patterns()
        guide.demonstrate_error_patterns()
        return

    if args.mock_device:
        await demonstrate_with_mock_device()
        return

    if args.scan:
        print("🔍 Scanning for BLE devices...")
        devices = await scan_with_bleak(timeout=10.0)
        if devices:
            print(
                f"\n📱 Found {len(devices)} devices. Use --address with one of these:"
            )
            for device in devices[:5]:
                print(f"   {device.address} - {device.name or 'Unknown'}")
        else:
            print("❌ No devices found")
        return

    if args.address:
        await run_with_real_device(args.address, args.timeout)
        return

    # Default: Show all patterns
    print("📚 Showing all integration patterns and examples...")
    guide.demonstrate_lookup_patterns()
    guide.demonstrate_production_patterns()
    guide.demonstrate_performance_patterns()
    guide.demonstrate_error_patterns()

    print("\n\n🧪 Running mock device demonstration...")
    await demonstrate_with_mock_device()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
