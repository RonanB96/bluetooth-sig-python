"""Test script to debug UUID registry."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ble_gatt_device.gatt.uuid_registry import UuidRegistry

# Create registry
registry = UuidRegistry()

# Print all service names
print("Available service lookups:")
print("-" * 50)
for key, info in registry._services.items():
    if info.uuid == "180F":  # Battery Service
        print(f"Key: {key!r}")
        print(f"  UUID: {info.uuid}")
        print(f"  Name: {info.name}")
        print(f"  ID: {info.id}")
        print()
