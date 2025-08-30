"""Test script to verify dynamic UUID loading from YAML files."""

import sys
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gatt.services.battery_service import BatteryService
from gatt.services.environmental_sensing import EnvironmentalSensingService
from gatt.uuid_registry import uuid_registry


def test_service_uuid_lookup():
    """Test that service UUIDs are correctly loaded from YAML."""
    print("Testing Service UUID Lookup:")
    print("-" * 50)

    # Test Battery Service
    battery = BatteryService()
    print(f"Battery Service:")
    print(f"  UUID: {battery.SERVICE_UUID}")
    print(f"  Name: {battery.name}")
    print(f"  Summary: {battery.summary}\n")

    # Test Environmental Sensing Service
    env = EnvironmentalSensingService()
    print(f"Environmental Sensing Service:")
    print(f"  UUID: {env.SERVICE_UUID}")
    print(f"  Name: {env.name}")
    print(f"  Summary: {env.summary}\n")

    # Verify UUIDs match expected values
    assert battery.SERVICE_UUID == "180F", "Battery Service UUID mismatch"
    assert env.SERVICE_UUID == "181A", "Environmental Service UUID mismatch"


def test_characteristic_lookup():
    """Test that characteristic UUIDs are correctly loaded."""
    print("Testing Characteristic UUID Lookup:")
    print("-" * 50)

    # Test mock device data
    mock_device_data = {
        "180F": {  # Battery Service
            "characteristics": {
                "00002A19-0000-1000-8000-00805F9B34FB": {  # Battery Level
                    "properties": ["read", "notify"]
                }
            }
        },
        "181A": {  # Environmental Sensing
            "characteristics": {
                "00002A6E-0000-1000-8000-00805F9B34FB": {  # Temperature
                    "properties": ["read", "notify"]
                },
                "00002A6F-0000-1000-8000-00805F9B34FB": {  # Humidity
                    "properties": ["read", "notify"]
                },
            }
        },
    }

    # Test Battery Service characteristic discovery
    battery = BatteryService()
    battery.process_characteristics(mock_device_data["180F"]["characteristics"])
    print("Battery Service Characteristics:")
    for uuid, char in battery.characteristics.items():
        print(f"  {char.name}:")
        print(f"    UUID: {uuid}")
        print(f"    Properties: {char.properties}")

    # Test Environmental Service characteristic discovery
    env = EnvironmentalSensingService()
    env.process_characteristics(mock_device_data["181A"]["characteristics"])
    print("\nEnvironmental Sensing Characteristics:")
    for uuid, char in env.characteristics.items():
        print(f"  {char.name}:")
        print(f"    UUID: {uuid}")
        print(f"    Properties: {char.properties}")

    # Verify characteristic counts
    assert len(battery.characteristics) == 1, "Wrong number of battery characteristics"
    assert (
        len(env.characteristics) == 2
    ), "Wrong number of environmental characteristics"


def main():
    """Run all tests."""
    try:
        test_service_uuid_lookup()
        test_characteristic_lookup()
        print("\nAll tests passed successfully! ✅")
    except AssertionError as e:
        print(f"\nTest failed: {e} ❌")
    except Exception as e:
        print(f"\nUnexpected error: {e} ❌")


if __name__ == "__main__":
    main()
