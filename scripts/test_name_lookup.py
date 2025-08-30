"""Quick test of UUID registry name lookup."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gatt.uuid_registry import uuid_registry


def main():
    """Test name-based lookups."""
    # Test Battery Service lookups
    print("\nTesting Battery Service lookups:")
    for key in [
        "Battery",
        "BATTERY",
        "battery",
        "org.bluetooth.service.battery_service",
        "180F",
    ]:
        info = uuid_registry.get_service_info(key)
        print(f"Lookup key: {key:40} -> {'Found' if info else 'Not found'}")
        if info:
            print(f"  UUID: {info.uuid}")
            print(f"  Name: {info.name}")
            print(f"  ID: {info.id}\n")

    # Test Environmental Sensing Service lookups
    print("\nTesting Environmental Sensing Service lookups:")
    for key in [
        "Environmental Sensing",
        "ENVIRONMENTAL_SENSING",
        "org.bluetooth.service.environmental_sensing",
        "181A",
    ]:
        info = uuid_registry.get_service_info(key)
        print(f"Lookup key: {key:40} -> {'Found' if info else 'Not found'}")
        if info:
            print(f"  UUID: {info.uuid}")
            print(f"  Name: {info.name}")
            print(f"  ID: {info.id}\n")


if __name__ == "__main__":
    main()
