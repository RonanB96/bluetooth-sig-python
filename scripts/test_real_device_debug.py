#!/usr/bin/env python3
"""Enhanced test script for connecting to a real Bluetooth device with detailed debugging."""

import asyncio
import logging
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# pylint: disable=wrong-import-position
from bleak import BleakClient, BleakScanner
from ble_gatt_device.gatt.gatt_manager import gatt_hierarchy

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def test_device_connection_debug(mac_address: str):
    """Test connecting to a real BLE device with enhanced debugging.

    Args:
        mac_address: The MAC address of the BLE device (e.g., "AA:BB:CC:DD:EE:FF")
    """
    print(f"🔍 Enhanced Device Connection Test: {mac_address}")
    print("=" * 70)

    # Step 1: Device Discovery with detailed information
    print("📡 Step 1: Device Discovery & Verification")
    print("-" * 40)

    device = None
    try:
        print(f"Searching for device {mac_address}...")
        device = await BleakScanner.find_device_by_address(mac_address)

        if device:
            print("✅ Device found!")
            print(f"   Name: {device.name or 'Unknown'}")
            print(f"   Address: {device.address}")
            # RSSI might not be available from find_device_by_address
            if hasattr(device, "rssi") and device.rssi is not None:
                print(f"   RSSI: {device.rssi} dBm")
            else:
                print("   RSSI: Not available from address lookup")
            if hasattr(device, "details"):
                print(f"   Details: {device.details}")
            if hasattr(device, "metadata"):
                print(f"   Metadata: {device.metadata}")
        else:
            print(f"❌ Device {mac_address} not found via address lookup")
            print("🔄 Performing full scan to locate device...")

            devices = await BleakScanner.discover(timeout=15.0)
            print(f"Found {len(devices)} total devices:")

            for idx, scanned_device in enumerate(devices):
                status = (
                    "🎯"
                    if scanned_device.address.upper() == mac_address.upper()
                    else "  "
                )
                print(
                    f"{status} {idx+1:2d}. {scanned_device.address} - {scanned_device.name or 'Unknown'} ({scanned_device.rssi} dBm)"
                )

                if scanned_device.address.upper() == mac_address.upper():
                    device = scanned_device
                    print(f"✅ Target device found in scan!")

            if not device:
                print(f"❌ Device {mac_address} not discoverable")
                print("\n💡 Troubleshooting tips:")
                print(
                    "   - Ensure device is powered on and in pairing/advertising mode"
                )
                print("   - Check MAC address format (should be XX:XX:XX:XX:XX:XX)")
                print("   - Move closer to the device")
                print("   - Restart Bluetooth: sudo systemctl restart bluetooth")
                return False

    except Exception as e:
        print(f"❌ Error during device discovery: {e}")
        traceback.print_exc()
        return False

    # Step 2: Connection attempt with detailed error handling
    print(f"\n🔗 Step 2: Connection Attempt")
    print("-" * 40)

    try:
        print(f"Creating BleakClient for {device.address}...")
        print("Connection parameters:")
        print("   - Timeout: 30 seconds")
        print("   - Device object: Using discovered device")

        # Try connection with extended timeout
        async with BleakClient(device, timeout=30.0) as client:
            print(f"✅ Connection established!")
            print(f"   Address: {client.address}")
            print(f"   Connected: {client.is_connected}")

            # Check MTU
            try:
                mtu = client.mtu_size
                print(f"   MTU Size: {mtu} bytes")
            except Exception as e:
                print(f"   MTU Size: Unable to determine ({e})")

            # Step 3: Service Discovery
            print(f"\n📋 Step 3: Service Discovery")
            print("-" * 40)

            # Wait a moment for service discovery to complete
            await asyncio.sleep(1.0)

            if not client.services:
                print("❌ No services discovered")
                print("   This might indicate:")
                print("   - Device requires pairing")
                print("   - Device has connection issues")
                print("   - Service discovery timeout")
                return False

            services_list = list(client.services)
            print(f"✅ Discovered {len(services_list)} services")

            readable_chars = []
            total_chars = 0

            # Detailed service enumeration
            for service_idx, service in enumerate(client.services, 1):
                print(f"\n📋 Service {service_idx}: {service.uuid}")
                print(f"   Description: {service.description}")
                print(f"   Handle range: {getattr(service, 'handle', 'N/A')}")

                if not service.characteristics:
                    print("   └─ No characteristics")
                    continue

                char_list = list(service.characteristics)
                total_chars += len(char_list)
                print(f"   └─ {len(char_list)} characteristics:")

                for char_idx, char in enumerate(service.characteristics, 1):
                    properties = ", ".join(char.properties)
                    print(f"      {char_idx}. {char.uuid}")
                    print(f"         Description: {char.description}")
                    print(f"         Properties: [{properties}]")
                    print(f"         Handle: {getattr(char, 'handle', 'N/A')}")

                    # Collect readable characteristics
                    if "read" in char.properties:
                        readable_chars.append(char)
                        print(f"         ✅ Readable")

                    # Show descriptors
                    if char.descriptors:
                        print(f"         Descriptors:")
                        for desc_idx, desc in enumerate(char.descriptors, 1):
                            print(
                                f"           {desc_idx}. {desc.uuid} - {desc.description}"
                            )

            print(
                f"\n📊 Summary: {total_chars} total characteristics, {len(readable_chars)} readable"
            )

            # Step 4: Characteristic Reading Test
            if readable_chars:
                print(f"\n🔍 Step 4: Reading Characteristics")
                print("-" * 40)

                characteristic_data = {}
                successful_reads = 0

                for idx, char in enumerate(readable_chars, 1):
                    try:
                        print(f"Reading {idx}/{len(readable_chars)}: {char.uuid}...")
                        value = await client.read_gatt_char(char)
                        characteristic_data[str(char.uuid)] = value
                        successful_reads += 1

                        # Display value
                        if isinstance(value, (bytes, bytearray)):
                            if len(value) == 0:
                                print(f"   ✅ Empty value")
                            elif all(32 <= b <= 126 for b in value):  # Printable ASCII
                                try:
                                    str_val = value.decode("utf-8").strip("\x00")
                                    print(f"   ✅ '{str_val}' (string)")
                                except UnicodeDecodeError:
                                    hex_val = " ".join(f"{b:02x}" for b in value)
                                    print(f"   ✅ {hex_val} (hex)")
                            else:
                                hex_val = " ".join(f"{b:02x}" for b in value)
                                print(f"   ✅ {hex_val} (hex)")
                        else:
                            print(f"   ✅ {value}")

                    except Exception as e:
                        print(f"   ❌ Error: {e}")

                print(
                    f"\n📊 Read Summary: {successful_reads}/{len(readable_chars)} successful"
                )

            # Step 5: Framework Integration Test
            print(f"\n🏗️  Step 5: GATT Framework Integration")
            print("-" * 40)

            try:
                # Convert services
                services_dict = {}
                for service in client.services:
                    service_uuid = str(service.uuid).upper()
                    if len(service_uuid) == 36 and service_uuid.endswith(
                        "-0000-1000-8000-00805F9B34FB"
                    ):
                        service_uuid = service_uuid[4:8]

                    characteristics = {}
                    for char in service.characteristics:
                        char_uuid = str(char.uuid)
                        characteristics[char_uuid] = {"properties": char.properties}

                    services_dict[service_uuid] = {"characteristics": characteristics}

                # Process with framework
                gatt_hierarchy._services = {}
                gatt_hierarchy.process_services(services_dict)

                if gatt_hierarchy.discovered_services:
                    print(
                        f"✅ Framework recognized {len(gatt_hierarchy.discovered_services)} services:"
                    )
                    for service in gatt_hierarchy.discovered_services:
                        print(
                            f"   └─ {service.__class__.__name__}: {service.SERVICE_UUID}"
                        )
                        print(f"      Characteristics: {len(service.characteristics)}")
                else:
                    print("ℹ️  No services recognized by framework")

            except Exception as e:
                print(f"❌ Framework error: {e}")
                traceback.print_exc()

            print(f"\n🎉 All tests completed successfully!")
            return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Exception type: {type(e).__name__}")

        # Detailed error analysis
        error_msg = str(e).lower()
        print(f"\n🔍 Error Analysis:")

        if "timeout" in error_msg:
            print("   • Timeout Error:")
            print("     - Device may be sleeping or unresponsive")
            print("     - Try putting device in pairing mode")
            print("     - Check for interference from other devices")
            print("     - Try: bluetoothctl scan on, then connect from command line")

        elif "permission denied" in error_msg or "access" in error_msg:
            print("   • Permission Error:")
            print("     - Try: sudo python scripts/test_real_device_debug.py <address>")
            print("     - Add to bluetooth group: sudo usermod -a -G bluetooth $USER")
            print("     - Check: groups $USER")

        elif "device not found" in error_msg:
            print("   • Device Not Found:")
            print("     - Device moved out of range")
            print("     - Device turned off")
            print("     - MAC address changed (randomization)")

        elif "already connected" in error_msg or "busy" in error_msg:
            print("   • Device Busy:")
            print("     - Disconnect from phone/other apps")
            print("     - Wait 10 seconds and retry")
            print("     - Reset Bluetooth: sudo systemctl restart bluetooth")

        elif "invalid" in error_msg:
            print("   • Invalid Address:")
            print("     - Check format: XX:XX:XX:XX:XX:XX")
            print("     - Case doesn't matter")

        else:
            print(f"   • Unknown error: {e}")

        print(f"\n📋 Full traceback:")
        traceback.print_exc()

        return False


async def main():
    """Main function with enhanced argument handling."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            print("🔍 Scanning for BLE devices...")
            try:
                devices = await BleakScanner.discover(timeout=10.0)
                if devices:
                    print(f"Found {len(devices)} devices:")
                    for idx, device in enumerate(devices, 1):
                        name = device.name or "Unknown"
                        print(
                            f"  {idx:2d}. {device.address} - {name} ({device.rssi} dBm)"
                        )
                else:
                    print("No devices found")
            except Exception as e:
                print(f"Scan error: {e}")
        else:
            mac_address = sys.argv[1].upper()  # Normalize to uppercase
            await test_device_connection_debug(mac_address)
    else:
        print("Usage: python test_real_device_debug.py <MAC_ADDRESS>")
        print("   or: python test_real_device_debug.py scan")
        print()
        print("Examples:")
        print("  python test_real_device_debug.py AA:BB:CC:DD:EE:FF")
        print("  python test_real_device_debug.py scan")


if __name__ == "__main__":
    asyncio.run(main())
