#!/usr/bin/env python3
"""Test script for connecting to a real Bluetooth device using proper Bleak patterns."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path before importing our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from ble_gatt_device.core import BLEGATTDevice


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def test_device_connection(mac_address: str):
    """Test connecting to a real BLE device and reading characteristics using the backend abstraction."""
    print(f"Testing connection to device: {mac_address}")
    print("=" * 60)
    device = BLEGATTDevice(mac_address)
    connected = await device.connect()
    if not connected:
        print(f"❌ Could not connect to device {mac_address}")
        if hasattr(device._impl, '_scan_rssi') and device._impl._scan_rssi is not None:
            print(f"📶 Scan RSSI: {device._impl._scan_rssi} dBm ({device._impl._scan_rssi_quality})")
        else:
            print("Device not found during scan or out of range.")
        return False
    print(f"✅ Successfully connected to {mac_address}")
    if hasattr(device._impl, '_scan_rssi') and device._impl._scan_rssi is not None:
        print(f"📶 Scan RSSI: {device._impl._scan_rssi} dBm ({device._impl._scan_rssi_quality})")
    if hasattr(device._impl, '_connection_rssi') and device._impl._connection_rssi is not None:
        print(f"📶 Connection RSSI: {device._impl._connection_rssi} dBm ({device._impl._connection_rssi_quality})")

    # Print discovered services and characteristics
    info = await device.get_device_info()
    if not info.get("connected"):
        print("❌ Not connected after info check.")
        return False
    services = info.get("services", {})
    print(f"✅ Found {len(services)} services:")
    for service_uuid, service in services.items():
        print(f"\n📋 Service: {service_uuid}")
        chars = service.get("characteristics", {})
        print(f"   └─ {len(chars)} characteristics:")
        for char_uuid, char in chars.items():
            props = ", ".join(char.get("properties", []))
            print(f"      └─ {char_uuid} - [{props}]")
            for desc in char.get("descriptors", []):
                print(f"         └─ Descriptor: {desc}")

    # Read all characteristics
    print("\n🔍 Reading all readable characteristics...")
    values = await device.read_characteristics()
    for uuid, value in values.items():
        if isinstance(value, (bytes, bytearray)):
            if len(value) == 0:
                print(f"  ⚠️  {uuid}: Empty data (0 bytes)")
            else:
                try:
                    str_val = value.decode("utf-8").strip("\x00")
                    is_printable = str_val and all(c.isprintable() or c.isspace() for c in str_val)
                    if is_printable and len(str_val) > 0:
                        print(f"  ✅ {uuid}: '{str_val}' ({len(value)} bytes)")
                    else:
                        hex_val = " ".join(f"{b:02x}" for b in value)
                        print(f"  ✅ {uuid}: {hex_val} ({len(value)} bytes)")
                except UnicodeDecodeError:
                    hex_val = " ".join(f"{b:02x}" for b in value)
                    print(f"  ✅ {uuid}: {hex_val} ({len(value)} bytes)")
        else:
            print(f"  ✅ {uuid}: {value}")

    # Parse with GATT framework
    print("\n🏗️  Testing GATT framework integration...")
    parsed = await device.read_parsed_characteristics()
    chars = parsed.get("characteristics", {})
    if chars:
        for uuid, entry in chars.items():
            char_name = entry.get("characteristic", "?")
            value = entry.get("value")
            unit = entry.get("unit", "")
            unit_str = f" {unit}" if unit else ""
            print(f"  ✅ {char_name}: {value}{unit_str}")
        print(f"\n✅ Successfully parsed {len(chars)} characteristics using framework")
    else:
        print("\nℹ️  No characteristics were parsed (may need raw data re-reading)")

    await device.disconnect()
    print("\n✅ Test completed successfully")
    return True


async def scan_devices():
    """Scan for nearby BLE devices."""
    print("Scanning for BLE devices is not implemented in the backend abstraction yet.")
    print("Please use a dedicated scan script or extend the backend to support scanning.")


async def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            await scan_devices()
        elif sys.argv[1] == "analyze":
            print_error_analysis()
        else:
            mac_address = sys.argv[1]
            await test_device_connection(mac_address)
    else:
        print("Usage: python test_real_device.py <MAC_ADDRESS>")
        print("   or: python test_real_device.py scan")
        print("   or: python test_real_device.py analyze")
        print()
        print("Examples:")
        print("  python test_real_device.py AA:BB:CC:DD:EE:FF")
        print("  python test_real_device.py scan")
        print("  python test_real_device.py analyze  # Show common BLE error patterns")


def print_error_analysis():
    """Print analysis of common BLE connection errors and solutions."""
    print("🔍 Common BLE Error Analysis & Solutions")
    print("=" * 60)

    print("\n📱 Service Discovery Errors:")
    print("❌ 'Service Discovery has not been performed yet'")
    print("   → Solution: Enhanced connection with explicit discovery retry")
    print("   → Often affects: Apple devices, complex devices")

    print("\n🔐 Authentication Errors:")
    print("❌ 'ATT error: 0x0e (Unlikely Error)'")
    print("   → Meaning: Characteristic requires authentication/encryption")
    print("   → Solution: Device needs to be paired first")
    print("   → Command: bluetoothctl pair <MAC_ADDRESS>")

    print("\n⏱️  Connection Timeouts:")
    print("❌ Connection timeout or 'Device not found'")
    print("   → Causes: Device sleeping, out of range, already connected")
    print("   → Solutions:")
    print("     • bluetoothctl disconnect <MAC_ADDRESS>")
    print("     • Ensure device is in advertising mode")
    print("     • Check device power/battery")

    print("\n📦 Empty Characteristic Data:")
    print("❌ Characteristics return 0 bytes")
    print("   → Causes: Requires write-first, authentication, timing")
    print("   → Solutions:")
    print("     • Some characteristics need activation via write")
    print("     • May require notifications to be enabled")
    print("     • Check characteristic properties")

    print("\n🚫 Framework Recognition:")
    print("ℹ️  'No services recognized by GATT framework'")
    print("   → Expected for proprietary devices")
    print("   → Our framework targets standard Bluetooth SIG services")
    print("   → Focus on Environmental Sensing Service (181A) devices")

    print("\n🎯 Recommended Test Devices:")
    print("✅ Environmental sensors with ESS service")
    print("✅ Fitness trackers with standard services")
    print("✅ Nordic nRF52 development boards")
    print("✅ Thingy:52 (when properly advertising)")


if __name__ == "__main__":
    asyncio.run(main())
