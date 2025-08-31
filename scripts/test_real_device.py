#!/usr/bin/env python3
"""Test script for connecting to a real Bluetooth device using proper Bleak patterns."""

import asyncio
import logging
import sys
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


async def test_device_connection(mac_address: str):
    """Test connecting to a real BLE device and reading characteristics.

    Args:
        mac_address: The MAC address of the BLE device (e.g., "AA:BB:CC:DD:EE:FF")
    """
    print(f"Testing connection to device: {mac_address}")
    print("=" * 60)

    try:
        # Use proper async context manager for connection with optimal timeout
        print("Attempting to connect...")
        async with BleakClient(mac_address, timeout=10.0) as client:
            print(f"✅ Successfully connected to {client.address}")

            # Service discovery happens automatically during connection
            print("\n📋 Discovering services and characteristics...")

            if not client.services:
                print("❌ No services discovered")
                return False

            services_list = list(client.services)
            print(f"✅ Found {len(services_list)} services:")

            readable_chars = []

            # Iterate through all services and characteristics
            for service in client.services:
                print(f"\n📋 Service: {service.uuid} ({service.description})")

                if not service.characteristics:
                    print("   └─ No characteristics found")
                    continue

                characteristics_list = list(service.characteristics)
                print(f"   └─ {len(characteristics_list)} characteristics:")

                for char in service.characteristics:
                    properties = ", ".join(char.properties)
                    print(f"      └─ {char.uuid} ({char.description}) - [{properties}]")

                    # Collect readable characteristics
                    if "read" in char.properties:
                        readable_chars.append(char)

                    # Show descriptors if any
                    if char.descriptors:
                        for desc in char.descriptors:
                            desc_info = f"{desc.uuid} ({desc.description})"
                            print(f"         └─ Descriptor: {desc_info}")

            # Test reading characteristics
            if readable_chars:
                print(f"\n🔍 Reading {len(readable_chars)} readable characteristics...")

                # Store raw data for later parsing
                characteristic_data = {}

                for char in readable_chars:
                    try:
                        value = await client.read_gatt_char(char)
                        characteristic_data[str(char.uuid)] = value

                        # Try to display value in a readable format
                        if isinstance(value, (bytes, bytearray)):
                            try:
                                # Try as UTF-8 string first
                                str_val = value.decode("utf-8").strip("\x00")
                                is_printable = str_val and all(
                                    c.isprintable() or c.isspace() for c in str_val
                                )
                                if is_printable:
                                    print(f"  ✅ {char.uuid}: '{str_val}'")
                                else:
                                    # Show as hex if not printable
                                    hex_val = " ".join(f"{b:02x}" for b in value)
                                    print(f"  ✅ {char.uuid}: {hex_val} (hex)")
                            except UnicodeDecodeError:
                                hex_val = " ".join(f"{b:02x}" for b in value)
                                print(f"  ✅ {char.uuid}: {hex_val} (hex)")
                        else:
                            print(f"  ✅ {char.uuid}: {value}")

                    except Exception as e:  # pylint: disable=broad-exception-caught
                        print(f"  ❌ {char.uuid}: Error reading - {e}")
            else:
                print("\nℹ️  No readable characteristics found")
                characteristic_data = {}  # Empty dict for parsing section

            # Test our GATT framework integration
            print("\n🏗️  Testing GATT framework integration...")

            try:
                # Convert Bleak services to our expected format
                services_dict = {}
                for service in client.services:
                    service_uuid = str(service.uuid).upper()
                    # Convert to short form if it's a standard Bluetooth UUID
                    standard_suffix = "-0000-1000-8000-00805F9B34FB"
                    if len(service_uuid) == 36 and service_uuid.endswith(
                        standard_suffix
                    ):
                        service_uuid = service_uuid[4:8]

                    characteristics = {}
                    for char in service.characteristics:
                        char_uuid = str(char.uuid)
                        characteristics[char_uuid] = {"properties": char.properties}

                    services_dict[service_uuid] = {"characteristics": characteristics}

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

                    # Parse data using our framework
                    print("\n🔍 Parsing data with GATT framework...")
                    parsed_count = 0

                    for service in gatt_hierarchy.discovered_services:
                        for (
                            char_uuid,
                            characteristic,
                        ) in service.characteristics.items():  # noqa: E501
                            # Find the corresponding full UUID in our data
                            full_uuid = None
                            for data_uuid in characteristic_data.keys():
                                if data_uuid.replace("-", "").upper() == char_uuid:
                                    full_uuid = data_uuid
                                    break

                            if full_uuid and full_uuid in characteristic_data:
                                try:
                                    # Parse using characteristic's parse method
                                    raw_data = characteristic_data[full_uuid]
                                    parsed_value = characteristic.parse_value(raw_data)
                                    unit = getattr(characteristic, "unit", "")
                                    unit_str = f" {unit}" if unit else ""

                                    char_name = characteristic.__class__.__name__
                                    print(f"  ✅ {char_name}: {parsed_value}{unit_str}")
                                    parsed_count += 1

                                except (
                                    Exception
                                ) as e:  # pylint: disable=broad-exception-caught  # noqa: E501
                                    char_name = characteristic.__class__.__name__
                                    print(f"  ❌ {char_name}: Parse error - {e}")

                    if parsed_count > 0:
                        framework_msg = (
                            f"\n✅ Successfully parsed {parsed_count} "
                            "characteristics using framework"
                        )
                        print(framework_msg)
                    else:
                        no_parse_msg = (
                            "\nℹ️  No characteristics were parsed "
                            "(may need raw data re-reading)"
                        )
                        print(no_parse_msg)

                else:
                    print("ℹ️  No services recognized by GATT framework")

            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"❌ GATT framework error: {e}")

            print("\n✅ Test completed successfully")
            return True

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("  - Device is not in range or not discoverable")
        print("  - MAC address is incorrect")
        print("  - Bluetooth permissions issue")
        print("  - Device is already connected to another client")
        return False


async def scan_devices():
    """Scan for nearby BLE devices."""
    try:
        print("Scanning for BLE devices...")
        print("=" * 60)

        devices = await BleakScanner.discover()

        if not devices:
            print("No BLE devices found")
            return

        print(f"Found {len(devices)} devices:")
        for device in devices:
            name = device.name or "Unknown"
            print(f"  {device.address} - {name}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error scanning devices: {e}")


async def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            await scan_devices()
        else:
            mac_address = sys.argv[1]
            await test_device_connection(mac_address)
    else:
        print("Usage: python test_real_device.py <MAC_ADDRESS>")
        print("   or: python test_real_device.py scan")
        print()
        print("Examples:")
        print("  python test_real_device.py AA:BB:CC:DD:EE:FF")
        print("  python test_real_device.py scan")


if __name__ == "__main__":
    asyncio.run(main())
