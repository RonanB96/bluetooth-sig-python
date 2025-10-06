#!/usr/bin/env python3
"""Test script for connecting to a real Bluetooth device using proper Bleak patterns.

This script tests BLE device connections and demonstrates bluetooth_sig parsing
with real hardware devices.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Configure path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent / "src"))

try:
    from bleak import BleakClient, BleakScanner

    from bluetooth_sig import BluetoothSIGTranslator

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Required dependencies not available: {e}")
    print("Install with: pip install bleak")
    print("For full functionality: pip install -e '.[dev]'")
    DEPENDENCIES_AVAILABLE = False


# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def test_device_connection(mac_address: str):
    """Test connection to a real device using Bleak."""
    print(f"\n🔍 Testing connection to device: {mac_address}")
    print("=" * 60)

    translator = BluetoothSIGTranslator()

    try:
        async with BleakClient(mac_address) as client:
            print(f"✅ Connected to {mac_address}")

            # Allow device to settle after connection
            await asyncio.sleep(0.5)

            # Get device information
            device_name = client.address
            try:
                # Try to get device name from advertisement data
                device_name = getattr(client._device, "name", None) or client.address
            except Exception:
                device_name = client.address

            print(f"� Device: {device_name}")

            # Discover services
            print("🔍 Discovering services...")
            services = client.services

            if not services:
                print("⚠️ No services discovered")
                return False

            print(f"📋 Found {len(services)} services:")

            # Print services and characteristics
            for service in services:
                service_info = translator.translate_service(service.uuid)
                print(f"\n� Service: {service_info.name} ({service.uuid})")

                chars = service.characteristics
                print(f"   └─ {len(chars)} characteristics:")
                for characteristic in chars:
                    props = ", ".join(characteristic.properties)
                    print(f"      └─ {characteristic.uuid} - [{props}]")
                    for descriptor in characteristic.descriptors:
                        print(f"         └─ Descriptor: {descriptor.uuid}")

            # Read all characteristics
            print("\n🔍 Reading all readable characteristics...")
            values = {}
            chars_read = 0

            for service in services:
                for characteristic in service.characteristics:
                    if "read" in characteristic.properties:
                        try:
                            data = await client.read_gatt_char(characteristic.uuid)
                            values[str(characteristic.uuid)] = data
                            chars_read += 1

                            if len(data) == 0:
                                print(f"  ⚠️  {characteristic.uuid}: Empty data (0 bytes)")
                            else:
                                try:
                                    str_val = data.decode("utf-8").strip("\x00")
                                    is_printable = str_val and all(c.isprintable() or c.isspace() for c in str_val)
                                    if is_printable and len(str_val) > 0:
                                        print(f"  ✅ {characteristic.uuid}: '{str_val}' ({len(data)} bytes)")
                                    else:
                                        hex_val = " ".join(f"{b:02x}" for b in data)
                                        print(f"  ✅ {characteristic.uuid}: {hex_val} ({len(data)} bytes)")
                                except UnicodeDecodeError:
                                    hex_val = " ".join(f"{b:02x}" for b in data)
                                    print(f"  ✅ {characteristic.uuid}: {hex_val} ({len(data)} bytes)")
                        except Exception as e:
                            print(f"  ❌ Error reading {characteristic.uuid}: {e}")

            # Parse with bluetooth_sig framework
            print(f"\n🏗️  Testing bluetooth_sig framework integration... (read {chars_read} characteristics)")
            parsed_count = 0

            for char_uuid, data in values.items():
                try:
                    # Parse the data using bluetooth_sig
                    parsed_data = translator.parse_characteristic_data(char_uuid, data)

                    if parsed_data.value is not None:
                        unit_str = f" {parsed_data.unit}" if parsed_data.unit else ""
                        char_info = translator.translate_characteristic(char_uuid)
                        print(f"  ✅ {char_info.name}: {parsed_data.value}{unit_str}")
                        parsed_count += 1
                except Exception:
                    # Silently skip unparseable characteristics
                    pass

            if parsed_count > 0:
                print(f"\n✅ Successfully parsed {parsed_count} characteristics using framework")
            else:
                print("\nℹ️  No characteristics were parsed (may need raw data re-reading)")

            # Enhanced SIG translator analysis
            print("\n🔍 Enhanced SIG Analysis...")

            if values:
                discovered_uuids = list(values.keys())
                print(f"📊 Analyzing {len(discovered_uuids)} discovered " "characteristics:")

                # Batch analysis
                char_info = translator.get_characteristics_info(discovered_uuids)
                for uuid, info in char_info.items():
                    if info:
                        name = info.get("name", "Unknown")
                        data_type = info.get("data_type", "unknown")
                        print(f"  📋 {uuid}: {name} [{data_type}]")
                    else:
                        print(f"  ❓ {uuid}: Unknown characteristic")

                # Validation analysis
                print("\n🔍 Data validation:")
                valid_count = 0
                for uuid, data in values.items():
                    if isinstance(data, (bytes, bytearray)):
                        is_valid = translator.validate_characteristic_data(uuid, data)
                        status = "✅" if is_valid else "⚠️"
                        validity = "Valid" if is_valid else "Unknown format"
                        print(f"  {status} {uuid}: {validity}")
                        if is_valid:
                            valid_count += 1

                print(f"\n📈 Validation: {valid_count}/{len(values)} " "characteristics have known format")

            print("\n✅ Test completed successfully")
            return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def scan_devices(timeout: float = 10.0):
    """Scan for nearby BLE devices."""
    print(f"🔍 Scanning for BLE devices (timeout: {timeout}s)...")
    print("=" * 60)

    try:
        devices = await BleakScanner.discover(timeout=timeout)
        if devices:
            print(f"Found {len(devices)} devices:")
            for idx, device in enumerate(devices, 1):
                name = device.name or "Unknown"
                rssi_str = f"({device.rssi} dBm)" if hasattr(device, "rssi") and device.rssi else ""
                print(f"  {idx:2d}. {device.address} - {name} {rssi_str}")
        else:
            print("No devices found")
            print("\n💡 Troubleshooting tips:")
            print("   - Ensure devices are powered on and advertising")
            print("   - Check Bluetooth adapter is enabled")
            print("   - Try: bluetoothctl scan on")
            print("   - Restart Bluetooth: sudo systemctl restart bluetooth")
    except Exception as e:
        print(f"❌ Scan error: {e}")
        print("Try running with elevated privileges: sudo python scripts/test_real_device.py scan")


async def main():
    """Main function."""
    if not DEPENDENCIES_AVAILABLE:
        print("\n❌ Required dependencies are not installed.")
        print("Install dependencies with: pip install bleak")
        print("For full functionality: pip install -e '.[dev]'")
        print("\nFor more advanced debugging capabilities when dependencies are available:")
        print("python scripts/ble_debug.py --help")
        return

    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            # Check for timeout argument
            timeout = 10.0
            if len(sys.argv) > 2:
                try:
                    timeout = float(sys.argv[2])
                except ValueError:
                    print("Invalid timeout value, using default 10 seconds")
            await scan_devices(timeout)
        elif sys.argv[1] == "analyze":
            print_error_analysis()
        else:
            mac_address = sys.argv[1]
            await test_device_connection(mac_address)
    else:
        print("Usage: python test_real_device.py <MAC_ADDRESS>")
        print("   or: python test_real_device.py scan [timeout]")
        print("   or: python test_real_device.py analyze")
        print()
        print("Examples:")
        print("  python test_real_device.py AA:BB:CC:DD:EE:FF")
        print("  python test_real_device.py scan 15          # Scan with 15s timeout")
        print("  python test_real_device.py analyze          # Show common BLE error patterns")
        print()
        print("For more advanced debugging, use: python scripts/ble_debug.py --help")


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
