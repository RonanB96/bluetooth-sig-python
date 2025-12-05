#!/usr/bin/env python3
"""Pure SIG parsing examples for bluetooth_sig.

This module demonstrates parsing characteristic data using only the
Bluetooth SIG translator without requiring BLE hardware.
"""

from __future__ import annotations

import sys
from typing import TypedDict

from bluetooth_sig import BluetoothSIGTranslator


class TestCase(TypedDict):
    """Test case structure for characteristic parsing."""

    name: str
    uuid: str
    data: bytes
    description: str


def demonstrate_pure_sig_parsing() -> None:
    """Demonstrate pure SIG parsing with various characteristic types."""
    print("🔵 Pure Bluetooth SIG Standards Parsing Demo")
    print("=" * 50)
    print("This demo shows parsing raw characteristic data using official SIG standards.")
    print("No BLE hardware or connections required!\n")

    translator = BluetoothSIGTranslator()

    # Test data from SIG specifications (realistic device data)
    test_cases: list[TestCase] = [
        {
            "name": "Battery Level",
            "uuid": "2A19",
            "data": bytes([0x64]),  # 100% battery
            "description": "Battery level percentage (0-100%)",
        },
        {
            "name": "Temperature",
            "uuid": "2A6E",
            "data": bytes([0x64, 0x09]),  # 24.20°C in SIG format (0x0964 = 2404, * 0.01 = 24.04°C)
            "description": "Temperature measurement in Celsius",
        },
        {
            "name": "Humidity",
            "uuid": "2A6F",
            "data": bytes([0x10, 0x27]),  # 100.00% humidity (0x2710 = 10000, * 0.01 = 100.00%)
            "description": "Relative humidity percentage",
        },
        {
            "name": "Pressure",
            "uuid": "2A6D",
            "data": bytes([0x40, 0x9C, 0x00, 0x00]),  # 1000.0 hPa (atmospheric pressure)
            "description": "Atmospheric pressure in hectopascals",
        },
        {
            "name": "Heart Rate Measurement",
            "uuid": "2A37",
            "data": bytes([0x00, 0x48]),  # 72 BPM, no additional features
            "description": "Heart rate in beats per minute",
        },
        {
            "name": "Device Name",
            "uuid": "2A00",
            "data": b"SIG Demo Device",  # UTF-8 string
            "description": "Human-readable device name",
        },
    ]

    print("Parsing test data using Bluetooth SIG standards:\n")

    results = {}
    for test_case in test_cases:
        print(f"📊 {test_case['name']} ({test_case['uuid']})")
        print(f"   Description: {test_case['description']}")
        print(f"   Raw data: {test_case['data'].hex().upper()}")

        # Parse using pure SIG standards
        result = translator.parse_characteristic(test_case["uuid"], test_case["data"])

        if result.parse_success:
            unit_str = f" {result.characteristic.unit}" if result.characteristic.unit else ""
            print(f"   ✅ Parsed value: {result.value}{unit_str}")
            if getattr(result.characteristic.info, "value_type", None):
                print(f"   📋 Value type: {result.characteristic.info.value_type}")
        else:
            print(f"   ❌ Parse failed: {result.error_message}")

        results[test_case["name"]] = result
        print()


def demonstrate_uuid_resolution() -> None:
    """Demonstrate UUID resolution and characteristic information lookup."""
    print("\n🔍 UUID Resolution and Characteristic Information")
    print("=" * 50)

    translator = BluetoothSIGTranslator()

    # Test UUID formats and resolution
    test_uuids = [
        "2A19",  # Short form
        "2a19",  # Lowercase
        "00002A19-0000-1000-8000-00805F9B34FB",  # Full UUID
        "2A6E",  # Temperature
        "180F",  # Battery Service UUID (for comparison)
    ]

    print("Resolving various UUID formats:\n")

    for uuid in test_uuids:
        print(f"🔗 UUID: {uuid}")

        # Get characteristic information
        char_info = translator.get_characteristic_info_by_uuid(uuid)
        if char_info:
            print(f"   ✅ Name: {char_info.name}")
            print(f"   🏷️  Type: {char_info.value_type}")
            print(f"   📏 Unit: {char_info.unit if char_info.unit else 'N/A'}")
        else:
            print("   ℹ️  Not found in characteristic registry")
        print()


def demonstrate_batch_parsing() -> None:
    """Demonstrate parsing multiple characteristics at once."""
    print("\n📦 Batch Parsing Multiple Characteristics")
    print("=" * 50)

    translator = BluetoothSIGTranslator()

    # Simulate data from multiple sensors
    sensor_data = {  # pylint: disable=duplicate-code
        # NOTE: Test sensor data duplicates parsing_performance benchmark fixture.
        # Duplication justified because:
        # 1. Standard test dataset for demonstrating multi-characteristic parsing
        # 2. Each example demonstrates different aspects (pure parsing vs performance)
        # 3. Self-contained examples are more educational than shared test data
        "2A19": bytes([0x55]),  # 85% battery
        "2A6E": bytes([0x58, 0x07]),  # 18.64°C
        "2A6F": bytes([0x38, 0x19]),  # 65.12% humidity
        "2A6D": bytes([0x70, 0x96, 0x00, 0x00]),  # 996.8 hPa pressure
    }

    print("Parsing data from multiple sensors simultaneously:\n")

    # Parse all characteristics
    results = translator.parse_characteristics(sensor_data)

    for _uuid, result in results.items():
        char_name = result.characteristic.name
        if result.parse_success:
            unit_str = f" {result.characteristic.unit}" if result.characteristic.unit else ""
            print(f"📊 {char_name}: {result.value}{unit_str}")
        else:
            print(f"❌ {char_name}: Parse failed - {result.error_message}")


def demonstrate_integration_pattern() -> None:
    """Show the recommended integration pattern for BLE libraries."""
    print("\n🔧 Integration Pattern for BLE Libraries")
    print("=" * 50)
    print(
        """
The bluetooth_sig library provides pure SIG translation that works with ANY BLE library:

# Step 1: Get raw data (using any BLE library)
raw_data = await your_ble_library.read_characteristic(device, uuid)

# Step 2: Parse with bluetooth_sig (connection-agnostic)
from bluetooth_sig import BluetoothSIGTranslator
translator = BluetoothSIGTranslator()
result = translator.parse_characteristic(uuid, raw_data)

# Step 3: Use parsed result
print(f"Value: {result.value} {result.unit}")

This pattern works with:
- bleak
- bleak-retry-connector
- simplepyble
- Any custom BLE implementation
"""
    )


if __name__ == "__main__":
    print("🚀 Bluetooth SIG Pure Standards Parsing Demo")
    print("This example demonstrates framework-agnostic SIG standard interpretation\n")

    try:
        # Run all demonstrations
        demonstrate_pure_sig_parsing()
        demonstrate_uuid_resolution()
        demonstrate_batch_parsing()
        demonstrate_integration_pattern()

        print("\n✅ Demo completed successfully!")
        print("The bluetooth_sig library is ready for integration with your BLE library of choice.")

    except Exception as e:  # pylint: disable=broad-except
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
