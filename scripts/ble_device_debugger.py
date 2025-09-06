#!/usr/bin/env python3
"""
BLE Device Debugger Script

Comprehensive tool for debugging BLE GATT devices including:
- Service discovery
- Characteristic enumeration
- Property analysis
- Value reading with hex and text display
- Connection status validation

Usage:
    python scripts/ble_device_debugger.py <MAC_ADDRESS>

Example:
    python scripts/ble_device_debugger.py 50:FD:D5:58:21:79
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bleak import BleakClient, BleakScanner


async def debug_ble_device(target_address: str) -> None:
    """
    Debug a BLE device by discovering services and characteristics.

    Args:
        target_address: MAC address of the BLE device to debug
    """
    print(f"=== BLE Device Debugger ===")
    print(f"Target: {target_address}")
    print()

    try:
        # Find the device
        print("Scanning for device...")
        device = await BleakScanner.find_device_by_address(target_address)
        if not device:
            print("❌ Device not found")
            print("Make sure the device is powered on and in range")
            return

        print(f"✅ Device found: {device.name or 'Unknown'} ({device.address})")
        print()

        # Connect with timeout
        print("Attempting connection with 10s timeout...")
        async with BleakClient(device, timeout=10.0) as client:
            print("✅ Connection established")

            # Get MTU information
            try:
                mtu = client.mtu_size
                print(f"MTU: {mtu} bytes")
            except Exception:
                print("MTU: Unable to determine")

            print(f"Connected: {client.is_connected}")
            print()

            # Discover and analyze services
            print("=== Service Discovery ===")
            services = list(client.services)
            print(f"Found {len(services)} services:")
            print()

            for i, service in enumerate(services, 1):
                print(f"Service {i}: {service.uuid}")
                print(f"  Description: {service.description}")
                print(f"  Handle: 0x{service.handle:04x}")

                characteristics = list(service.characteristics)
                print(f"  Characteristics ({len(characteristics)}):")

                for j, char in enumerate(characteristics, 1):
                    print(f"    {j}. {char.uuid}")
                    print(f"       Description: {char.description}")
                    print(f"       Handle: 0x{char.handle:04x}")

                    # Analyze properties
                    props = []
                    if "read" in char.properties:
                        props.append("READ")
                    if "write" in char.properties:
                        props.append("WRITE")
                    if "write-without-response" in char.properties:
                        props.append("WRITE_NO_RESP")
                    if "notify" in char.properties:
                        props.append("NOTIFY")
                    if "indicate" in char.properties:
                        props.append("INDICATE")

                    print(f"       Properties: {' | '.join(props) if props else 'None'}")

                    # Try to read if readable
                    if "read" in char.properties:
                        try:
                            value = await client.read_gatt_char(char.uuid)
                            hex_val = " ".join(f"{b:02x}" for b in value)
                            print(f"       Value: [{hex_val}] ({len(value)} bytes)")

                            # Try to decode as string if printable
                            if value:
                                try:
                                    decoded = value.decode("utf-8")
                                    if decoded.isprintable():
                                        print(f'       Text: "{decoded}"')
                                except UnicodeDecodeError:
                                    pass

                                # Show as integer if small
                                if len(value) <= 4:
                                    try:
                                        if len(value) == 1:
                                            int_val = value[0]
                                        elif len(value) == 2:
                                            int_val = int.from_bytes(value, byteorder="little")
                                        elif len(value) == 4:
                                            int_val = int.from_bytes(value, byteorder="little")
                                        else:
                                            int_val = None

                                        if int_val is not None:
                                            print(f"       Integer: {int_val}")
                                    except Exception:
                                        pass

                        except Exception as e:
                            print(f"       Read failed: {e}")

                    print()

                print()

    except Exception as e:
        print(f"❌ Connection error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point for the debugger."""
    if len(sys.argv) != 2:
        print("Usage: python ble_device_debugger.py <MAC_ADDRESS>")
        print("Example: python ble_device_debugger.py 50:FD:D5:58:21:79")
        sys.exit(1)

    target_address = sys.argv[1]

    # Validate MAC address format
    if len(target_address) != 17 or target_address.count(":") != 5:
        print("❌ Invalid MAC address format")
        print("Expected format: AA:BB:CC:DD:EE:FF")
        sys.exit(1)

    try:
        asyncio.run(debug_ble_device(target_address))
    except KeyboardInterrupt:
        print("\n🛑 Debugging interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
