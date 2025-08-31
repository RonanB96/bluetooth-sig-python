#!/usr/bin/env python3
"""Test script for data parsing functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# pylint: disable=wrong-import-position
from ble_gatt_device.gatt.gatt_manager import gatt_hierarchy


def test_data_parsing():
    """Test parsing of simulated real device data."""
    print("Testing GATT Framework Data Parsing")
    print("=" * 50)

    # Simulate the services we found on the real Nordic Thingy:52 device
    services_dict = {
        "180F": {  # Battery Service
            "characteristics": {
                "00002a19-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read", "notify"]
                }
            }
        },
        "181A": {  # Environmental Sensing Service
            "characteristics": {
                "00002a6e-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read", "notify"]
                },  # Temperature
                "00002a6f-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read", "notify"]
                },  # Humidity
                "00002a6d-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read", "notify"]
                },  # Pressure
                "00002afb-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read", "notify"]
                },  # Illuminance
                "00002b28-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read", "notify"]
                },  # Sound Pressure Level
            }
        },
        "180A": {  # Device Information Service
            "characteristics": {
                "00002a24-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read"]
                },  # Model Number
                "00002a29-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read"]
                },  # Manufacturer Name
                "00002a25-0000-1000-8000-00805f9b34fb": {
                    "properties": ["read"]
                },  # Serial Number
            }
        },
    }

    # Simulate the raw data we read from the device
    characteristic_data = {
        # Battery Level: 77 (0x4D, which was 'M' in ASCII)
        "00002a19-0000-1000-8000-00805f9b34fb": bytearray([0x4D]),
        # Temperature: simulated as sint16 = 2300 (23.00°C)
        "00002a6e-0000-1000-8000-00805f9b34fb": bytearray(
            [0xFC, 0x08]
        ),  # 2300 little endian
        # Humidity: simulated as uint16 = 6100 (61.00%)
        "00002a6f-0000-1000-8000-00805f9b34fb": bytearray(
            [0xD4, 0x17]
        ),  # 6100 little endian
        # Pressure: simulated as uint32 = 101325 Pa (sea level)
        "00002a6d-0000-1000-8000-00805f9b34fb": bytearray(
            [0xE2, 0x7F, 0x01, 0x00]
        ),  # little endian
        # Illuminance: simulated as uint24 = 50000 (500.00 lux)
        "00002afb-0000-1000-8000-00805f9b34fb": bytearray(
            [0x50, 0xC3, 0x00]
        ),  # 50000 little endian
        # Sound Pressure Level: simulated as uint8 = 65 dBA
        "00002b28-0000-1000-8000-00805f9b34fb": bytearray([0x41]),  # 65 dBA
        # Device strings
        "00002a24-0000-1000-8000-00805f9b34fb": bytearray(b"Thingy:52"),
        "00002a29-0000-1000-8000-00805f9b34fb": bytearray(b"Nordic Semiconductor"),
        "00002a25-0000-1000-8000-00805f9b34fb": bytearray(b"ENV001"),
    }

    # Process through our GATT hierarchy
    gatt_hierarchy._services = {}  # Reset discovered services
    gatt_hierarchy.process_services(services_dict)

    if gatt_hierarchy.discovered_services:
        service_count = len(gatt_hierarchy.discovered_services)
        print(f"✅ GATT framework recognized {service_count} services:")
        for service in gatt_hierarchy.discovered_services:
            service_name = service.__class__.__name__
            service_uuid = service.SERVICE_UUID
            print(f"   └─ {service_name}: {service_uuid}")

        print("\n🔍 Parsing simulated data...")
        parsed_count = 0

        for service in gatt_hierarchy.discovered_services:
            print(f"\n📋 {service.__class__.__name__}:")
            print(f"   Service has {len(service.characteristics)} characteristics")
            for char_uuid, characteristic in service.characteristics.items():
                print(f"   Stored UUID: {char_uuid}")

            for char_uuid, characteristic in service.characteristics.items():
                # Try both original UUID and stored UUID format
                original_uuid = char_uuid
                full_uuid = None

                # Find the corresponding full UUID in our data
                for data_uuid in characteristic_data.keys():
                    if data_uuid.replace("-", "").upper() == char_uuid:
                        full_uuid = data_uuid
                        break

                if full_uuid and full_uuid in characteristic_data:
                    try:
                        raw_data = characteristic_data[full_uuid]
                        parsed_value = characteristic.parse_value(raw_data)
                        unit = getattr(characteristic, "unit", "")
                        unit_str = f" {unit}" if unit else ""

                        char_name = characteristic.__class__.__name__
                        print(f"  ✅ {char_name}: {parsed_value}{unit_str}")
                        parsed_count += 1

                    except Exception as e:  # pylint: disable=broad-exception-caught
                        char_name = characteristic.__class__.__name__
                        print(f"  ❌ {char_name}: Parse error - {e}")
                else:
                    char_name = characteristic.__class__.__name__
                    print(f"  ⚠️  {char_name}: No data available (UUID: {char_uuid})")

        print(f"\n✅ Successfully parsed {parsed_count} characteristics!")

    else:
        print("❌ No services recognized by GATT framework")
        return False

    return True


if __name__ == "__main__":
    success = test_data_parsing()
    sys.exit(0 if success else 1)
