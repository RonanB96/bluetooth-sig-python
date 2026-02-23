#!/usr/bin/env python3
"""Pure SIG parsing examples for bluetooth_sig.

This module demonstrates parsing characteristic data without requiring BLE hardware.
Two approaches are shown:

1. **Type-safe** (recommended): Use characteristic classes directly for full IDE inference
2. **Dynamic**: Use Translator with UUID strings for scanning unknown devices
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


def demonstrate_type_safe_parsing() -> None:
    """Demonstrate type-safe parsing with characteristic classes (recommended).

    Use this approach when you know the characteristic type at compile time.
    The IDE infers return types automatically.
    """
    print("Type-Safe Parsing (Recommended for Known Devices)")
    print("=" * 55)
    print("Use characteristic classes directly for full IDE type inference.\n")

    from bluetooth_sig.gatt.characteristics import (
        BatteryLevelCharacteristic,
        HeartRateMeasurementCharacteristic,
        HumidityCharacteristic,
        TemperatureCharacteristic,
    )

    # Simple characteristics: return primitive types
    battery = BatteryLevelCharacteristic()
    level = battery.parse_value(bytearray([85]))  # IDE knows: int
    print(f"Battery Level: {level}% (type: {type(level).__name__})")

    temp = TemperatureCharacteristic()
    temp_value = temp.parse_value(bytearray([0x64, 0x09]))  # IDE knows: float
    print(f"Temperature: {temp_value}°C (type: {type(temp_value).__name__})")

    humidity = HumidityCharacteristic()
    humidity_value = humidity.parse_value(bytearray([0x3A, 0x13]))  # IDE knows: float
    print(f"Humidity: {humidity_value}% (type: {type(humidity_value).__name__})")

    # Complex characteristics: return structured dataclasses
    heart_rate = HeartRateMeasurementCharacteristic()
    hr_data = heart_rate.parse_value(bytearray([0x00, 72]))  # IDE knows: HeartRateData
    print(f"Heart Rate: {hr_data.heart_rate} bpm (type: {type(hr_data).__name__})")
    print(f"   Sensor contact: {hr_data.sensor_contact}")

    # Encoding: build_value converts back to bytes
    encoded = battery.build_value(85)
    print(f"\nEncode 85% battery → {encoded.hex()}")

    encoded_hr = heart_rate.build_value(hr_data)
    print(f"Encode heart rate data → {encoded_hr.hex()}")
    print()


def demonstrate_dynamic_parsing() -> None:
    """Demonstrate dynamic parsing with UUID strings (for device scanning).

    Use this approach when scanning unknown devices or building generic BLE explorers.
    Return type is Any since the characteristic type is determined at runtime.
    """
    print("Dynamic Parsing (For Scanning Unknown Devices)")
    print("=" * 55)
    print("Use Translator with UUID strings when characteristic type is unknown.\n")

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
        print(f"{test_case['name']} ({test_case['uuid']})")
        print(f"   Description: {test_case['description']}")
        print(f"   Raw data: {test_case['data'].hex().upper()}")

        # Parse using pure SIG standards
        try:
            result = translator.parse_characteristic(test_case["uuid"], test_case["data"])
            info = translator.get_characteristic_info_by_uuid(test_case["uuid"])
            unit_str = f" {info.unit}" if info and info.unit else ""
            print(f"   Parsed value: {result}{unit_str}")
            if info and info.python_type:
                print(f"   Python type: {info.python_type}")
            results[test_case["name"]] = result
        except Exception as e:
            print(f"   Parse failed: {e}")
            results[test_case["name"]] = None

        print()


def demonstrate_uuid_resolution() -> None:
    """Demonstrate UUID resolution and characteristic information lookup."""
    print("\nUUID Resolution and Characteristic Information")
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
        print(f"UUID: {uuid}")

        # Get characteristic information
        char_info = translator.get_characteristic_info_by_uuid(uuid)
        if char_info:
            print(f"   Name: {char_info.name}")
            print(f"   Type: {char_info.python_type}")
            print(f"   Unit: {char_info.unit if char_info.unit else 'N/A'}")
        else:
            print("   Not found in characteristic registry")
        print()


def demonstrate_batch_parsing() -> None:
    """Demonstrate parsing multiple characteristics at once."""
    print("\nBatch Parsing Multiple Characteristics")
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

    for uuid, result in results.items():
        info = translator.get_characteristic_info_by_uuid(uuid)
        char_name = info.name if info else uuid
        unit_str = f" {info.unit}" if info and info.unit else ""
        print(f"{char_name}: {result}{unit_str}")


def demonstrate_integration_pattern() -> None:
    """Show the recommended integration patterns for BLE libraries."""
    print("\nIntegration Patterns for BLE Libraries")
    print("=" * 55)
    print(
        """
Choose your approach based on your use case:

# TYPE-SAFE (recommended for known devices):
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

battery = BatteryLevelCharacteristic()
raw_data = await your_ble_library.read_characteristic(device, "2A19")
level = battery.parse_value(raw_data)  # IDE knows: int
encoded = battery.build_value(85)      # Encode back to bytes

# DYNAMIC (for scanning unknown devices):
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
for uuid in discovered_uuids:
    if translator.supports(uuid):
        result = translator.parse_characteristic(uuid, raw_data)
        print(f"{result.info.name}: {result.value}")  # Returns Any

Both patterns work with bleak, simplepyble, or any BLE library.
"""
    )


if __name__ == "__main__":
    print("Bluetooth SIG Pure Standards Parsing Demo")
    print("Demonstrates type-safe and dynamic parsing approaches\n")

    try:
        # Run all demonstrations
        demonstrate_type_safe_parsing()
        demonstrate_dynamic_parsing()
        demonstrate_uuid_resolution()
        demonstrate_batch_parsing()
        demonstrate_integration_pattern()

        print("\nDemo completed successfully!")
        print("Use characteristic classes for known devices, Translator for scanning.")

    except Exception as e:  # pylint: disable=broad-except
        print(f"\nDemo failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
