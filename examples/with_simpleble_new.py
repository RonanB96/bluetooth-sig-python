#!/usr/bin/env python3
"""SimpleBLE integration example - alternative BLE library with SIG parsing.

This example demonstrates using SimpleBLE as an alternative BLE library combined
with bluetooth_sig for standards-compliant data parsing. SimpleBLE offers a
different API design compared to Bleak.

Benefits:
- Alternative BLE library choice
- Cross-platform C++ library with Python bindings
- Pure SIG standards parsing
- Demonstrates framework-agnostic design

Requirements:
    pip install simplebluez  # Linux
    pip install simpleble    # Windows/macOS (if available)

Note: SimpleBLE availability varies by platform. This example shows the
integration pattern even if the library is not installed.

Usage:
    python with_simpleble.py --scan
    python with_simpleble.py --address 12:34:56:78:9A:BC
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

# Import shared BLE utilities
from ble_utils import (
    demo_mock_comparison,
    get_default_characteristic_uuids,
)

# Try to import SimpleBLE (availability varies by platform)
SIMPLEBLE_AVAILABLE = False
SIMPLEBLE_MODULE = None

try:
    import simpleble as simpleble_module
    SIMPLEBLE_AVAILABLE = True
    SIMPLEBLE_MODULE = simpleble_module
    print("✅ SimpleBLE module loaded")
except ImportError:
    try:
        import simplebluez as simpleble_module
        SIMPLEBLE_AVAILABLE = True
        SIMPLEBLE_MODULE = simpleble_module
        print("✅ SimpleBluez module loaded (Linux alternative)")
    except ImportError:
        print("⚠️  SimpleBLE not available. This is a demonstration of the integration pattern.")
        print("Install options:")
        print("  Linux: pip install simplebluez")
        print("  Other: pip install simpleble (if available)")


def scan_for_devices_simpleble(timeout: float = 10.0) -> list[dict]:
    """Scan for BLE devices using SimpleBLE.

    Args:
        timeout: Scan duration in seconds

    Returns:
        List of device information dictionaries
    """
    if not SIMPLEBLE_AVAILABLE:
        print("❌ SimpleBLE not available for scanning")
        return []

    devices = []

    try:
        print(f"🔍 Scanning for BLE devices using SimpleBLE ({timeout}s)...")

        # Get available adapters
        adapters = SIMPLEBLE_MODULE.Adapter.get_adapters()
        if not adapters:
            print("❌ No BLE adapters found")
            return devices

        adapter = adapters[0]  # Use first adapter
        print(f"📡 Using adapter: {adapter.identifier()}")

        # Start scanning
        adapter.scan_start()
        time.sleep(timeout)
        adapter.scan_stop()

        # Get scan results
        scan_results = adapter.scan_get_results()

        print(f"\n📡 Found {len(scan_results)} devices:")
        for i, peripheral in enumerate(scan_results, 1):
            try:
                name = peripheral.identifier() or "Unknown"
                address = peripheral.address() if hasattr(peripheral, 'address') else "Unknown"
                rssi = peripheral.rssi() if hasattr(peripheral, 'rssi') else "N/A"

                device_info = {
                    'name': name,
                    'address': address,
                    'rssi': rssi,
                    'peripheral': peripheral
                }
                devices.append(device_info)

                print(f"  {i}. {name} ({address}) - RSSI: {rssi}dBm")

            except Exception as e:
                print(f"  {i}. Error reading device info: {e}")

    except Exception as e:
        print(f"❌ Scanning failed: {e}")

    return devices


def read_characteristics_simpleble(address: str, target_uuids: list[str] = None) -> dict:
    """Read characteristics from a BLE device using SimpleBLE.

    Args:
        address: BLE device address
        target_uuids: List of characteristic UUIDs to read

    Returns:
        Dictionary mapping UUID to (raw_data, char_object) tuples
    """
    if not SIMPLEBLE_AVAILABLE:
        print("❌ SimpleBLE not available for connections")
        return {}

    results = {}
    target_uuids = target_uuids or get_default_characteristic_uuids()

    print(f"🔵 Connecting to device using SimpleBLE: {address}")

    try:
        # Get adapter
        adapters = SIMPLEBLE_MODULE.Adapter.get_adapters()
        if not adapters:
            print("❌ No BLE adapters found")
            return results

        adapter = adapters[0]

        # Find the device (may need to scan first)
        print("🔍 Looking for device...")
        adapter.scan_start()
        time.sleep(5.0)  # Scan briefly
        adapter.scan_stop()

        scan_results = adapter.scan_get_results()
        target_peripheral = None

        for peripheral in scan_results:
            try:
                if hasattr(peripheral, 'address') and peripheral.address() == address:
                    target_peripheral = peripheral
                    break
                elif peripheral.identifier() == address:  # Some implementations use identifier
                    target_peripheral = peripheral
                    break
            except Exception:
                continue

        if not target_peripheral:
            print(f"❌ Device {address} not found in scan results")
            return results

        # Connect to device
        print("🔗 Connecting...")
        target_peripheral.connect()

        if not target_peripheral.is_connected():
            print("❌ Failed to connect")
            return results

        print(f"✅ Connected to {address}")

        # Discover services and read characteristics
        print("\n📊 Reading and parsing characteristics...")
        services = target_peripheral.services()

        for service in services:
            try:
                service_uuid = service.uuid()

                # Get characteristics for this service
                characteristics = service.characteristics()

                for char in characteristics:
                    try:
                        char_uuid = char.uuid()

                        # Extract short UUID for SIG lookup
                        if len(char_uuid) > 8:
                            char_uuid_short = char_uuid[4:8].upper()
                        else:
                            char_uuid_short = char_uuid.upper()

                        # Check if we should read this characteristic
                        if target_uuids and char_uuid_short not in target_uuids:
                            continue

                        print(f"  📖 Reading characteristic {char_uuid_short}...")

                        # Read raw data
                        raw_data = char.read()

                        if not raw_data:
                            print("     ⚠️  No data read")
                            continue

                        # Convert to bytes if needed
                        if hasattr(raw_data, '__iter__') and not isinstance(raw_data, (str, bytes)):
                            raw_bytes = bytes(raw_data)
                        elif isinstance(raw_data, str):
                            raw_bytes = raw_data.encode('utf-8')
                        else:
                            raw_bytes = raw_data

                        results[char_uuid_short] = (raw_bytes, char)

                    except Exception as e:
                        print(f"     ❌ Error reading characteristic: {e}")

            except Exception as e:
                print(f"  ❌ Error processing service: {e}")

        # Disconnect
        target_peripheral.disconnect()
        print(f"\n🔌 Disconnected from {address}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    return results


def read_and_parse_with_simpleble(address: str, target_uuids: list[str] = None) -> dict:
    """Read characteristics from a BLE device using SimpleBLE and parse with SIG standards.

    Args:
        address: BLE device address
        target_uuids: List of characteristic UUIDs to read

    Returns:
        Dictionary of parsed characteristic data
    """
    if not SIMPLEBLE_AVAILABLE:
        print("❌ SimpleBLE not available for connections")
        return {}

    # Read raw characteristics
    raw_results = read_characteristics_simpleble(address, target_uuids)

    # Parse with SIG standards
    translator = BluetoothSIGTranslator()
    parsed_results = {}

    for char_uuid_short, (raw_bytes, _) in raw_results.items():
        result = translator.parse_characteristic(char_uuid_short, raw_bytes)

        if result.parse_success:
            unit_str = f" {result.unit}" if result.unit else ""
            print(f"     ✅ {result.name}: {result.value}{unit_str}")
        else:
            print(f"     ❌ Parse failed: {result.error_message}")

        print(f"     📄 Raw data: {raw_bytes.hex().upper()}")
        parsed_results[char_uuid_short] = result

    print(f"\n✅ Successfully read {len(parsed_results)} characteristics")
    return parsed_results


def demonstrate_simpleble_patterns():
    """Demonstrate different SimpleBLE integration patterns."""
    print("\n🔧 SimpleBLE Integration Patterns")
    print("=" * 50)

    print("""
# Pattern 1: Simple device reading
def read_device_with_simpleble(address: str) -> dict:
    translator = BluetoothSIGTranslator()

    # SimpleBLE connection management
    adapters = simpleble.Adapter.get_adapters()
    adapter = adapters[0]

    # Scan and connect
    adapter.scan_start()
    time.sleep(5)
    adapter.scan_stop()

    peripherals = adapter.scan_get_results()
    target = next(p for p in peripherals if p.address() == address)

    target.connect()

    # Read and parse characteristics
    results = {}
    for service in target.services():
        for char in service.characteristics():
            raw_data = char.read()

            # bluetooth_sig handles SIG parsing
            uuid_short = char.uuid()[4:8]
            result = translator.parse_characteristic(uuid_short, bytes(raw_data))
            results[uuid_short] = result.value

    target.disconnect()
    return results

# Pattern 2: Service-specific reading
def read_battery_service(address: str) -> dict:
    translator = BluetoothSIGTranslator()

    # ... connection code ...

    # Find Battery Service (180F)
    battery_service = None
    for service in target.services():
        if "180F" in service.uuid().upper():
            battery_service = service
            break

    if battery_service:
        for char in battery_service.characteristics():
            if "2A19" in char.uuid().upper():  # Battery Level
                raw_data = char.read()
                result = translator.parse_characteristic("2A19", bytes(raw_data))
                return {"battery_level": result.value}

    return {}

# Pattern 3: Cross-platform compatibility
def get_ble_library_and_connect(address: str):
    translator = BluetoothSIGTranslator()

    # Try different BLE libraries based on availability
    if SIMPLEBLE_AVAILABLE:
        return read_with_simpleble(address, translator)
    elif BLEAK_AVAILABLE:
        return asyncio.run(read_with_bleak(address, translator))
    else:
        raise RuntimeError("No BLE library available")
    """)


def demonstrate_mock_usage():
    """Demonstrate the integration pattern even without SimpleBLE."""
    print("\n🎭 Mock SimpleBLE Integration (No Hardware Required)")
    print("=" * 55)

    # Use shared demo functionality
    demo_mock_comparison("SimpleBLE")


def main():
    """Main function demonstrating SimpleBLE + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(description="SimpleBLE + bluetooth_sig integration example")
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds")
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific characteristic UUIDs to read")

    args = parser.parse_args()

    print("🚀 SimpleBLE + Bluetooth SIG Integration Demo")
    print("=" * 50)

    try:
        if args.scan or not args.address:
            # Scan for devices
            devices = scan_for_devices_simpleble(args.timeout)

            if not devices and SIMPLEBLE_AVAILABLE:
                print("\n❌ No devices found")
            elif not SIMPLEBLE_AVAILABLE:
                print("📝 Would scan for devices if SimpleBLE was available")

            if not args.address:
                print("\n💡 Use --address with a device address to connect")
                demonstrate_mock_usage()
                demonstrate_simpleble_patterns()
                return

        if args.address:
            # Connect and read characteristics
            print(f"\n🔗 Connecting to {args.address}...")
            results = read_and_parse_with_simpleble(args.address, args.uuids)

            if results:
                print("\n📋 Summary of parsed data:")
                for _uuid, result in results.items():
                    if result.parse_success:
                        unit_str = f" {result.unit}" if result.unit else ""
                        print(f"  {result.name}: {result.value}{unit_str}")

        # Always show the integration patterns
        demonstrate_simpleble_patterns()

        # Show mock usage if SimpleBLE not available
        if not SIMPLEBLE_AVAILABLE:
            demonstrate_mock_usage()

        print("\n✅ Demo completed!")
        print("This example shows framework-agnostic SIG parsing with SimpleBLE.")
        print("The same bluetooth_sig parsing works with any BLE library!")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
