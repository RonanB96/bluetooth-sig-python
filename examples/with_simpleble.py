#!/usr/bin/env python3
from __future__ import annotations

# Set up paths for imports
import sys
from pathlib import Path

# Add src directory for bluetooth_sig imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add parent directory for examples package imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add examples directory for utils imports
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import time
from typing import Any

import simplepyble as simplepyble_module

from bluetooth_sig import BluetoothSIGTranslator
from examples.utils.library_detection import simplepyble_available
from examples.utils.simpleble_integration import comprehensive_device_analysis_simpleble

"""SimplePyBLE integration example

This example demonstrates using SimplePyBLE as an alternative BLE library combined
with bluetooth_sig for standards-compliant data parsing. SimplePyBLE offers a
different API design compared to Bleak.

Benefits:
- Cross-platform BLE library (Windows, macOS, Linux)
- Synchronous API alternative to async libraries
- Pure SIG standards parsing
- Demonstrates framework-agnostic design

Requirements:
    pip install simplepyble  # Cross-platform (requires commercial license for commercial use)

Note: SimplePyBLE requires a commercial license for commercial use since January 2025.
Free for non-commercial use.

Usage:
    python with_simpleble.py --scan
    python with_simpleble.py --address 12:34:56:78:9A:BC
"""


def scan_for_devices_simpleble(timeout: float = 10.0) -> list[dict[str, Any]]:  # type: ignore
    """Scan for BLE devices using SimpleBLE.

    Args:
        timeout: Scan duration in seconds

    Returns:
        List of device dictionaries with address, name, and RSSI
    """
    # mypy doesn't understand optional imports, so ignore type checking for this function
    if not simplepyble_available:  # type: ignore[possibly-unbound]
        print("❌ SimplePyBLE not available")
        return []

    # At this point we know simplepyble is available
    assert simplepyble_module is not None

    print(f"🔍 Scanning for BLE devices ({timeout}s)...")

    # Get available adapters
    adapters: Any
    if hasattr(simplepyble_module, "Adapter") and hasattr(
        simplepyble_module.Adapter, "get_adapters"
    ):
        adapters = simplepyble_module.Adapter.get_adapters()  # type: ignore[attr-defined]
    elif hasattr(simplepyble_module, "get_adapters"):
        adapters = simplepyble_module.get_adapters()  # type: ignore[attr-defined]
    else:
        print("❌ SimplePyBLE API for adapter discovery not found")
        return []
    if not adapters:
        print("❌ No BLE adapters found")
        return []
    adapter: Any = adapters[0]  # type: ignore[index]
    if not adapters:
        print("❌ No BLE adapters found")
        return []

    adapter = adapters[0]  # Use first adapter
    print(f"📡 Using adapter: {adapter.identifier()}")

    # Start scanning
    adapter.scan_start()
    time.sleep(timeout)
    adapter.scan_stop()

    # Get scan results
    scan_results = adapter.scan_get_results()

    devices: list[dict[str, Any]] = []
    print(f"\n📡 Found {len(scan_results)} devices:")
    for i, peripheral in enumerate(scan_results, 1):
        try:
            name = peripheral.identifier() or "Unknown"
            address = (
                peripheral.address() if hasattr(peripheral, "address") else "Unknown"
            )
            rssi = peripheral.rssi() if hasattr(peripheral, "rssi") else "N/A"

            device_info = {
                "name": name,
                "address": address,
                "rssi": rssi,
                "peripheral": peripheral,
            }
            devices.append(device_info)

            print(f"  {i}. {name} ({address}) - RSSI: {rssi}dBm")

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"  {i}. Error reading device info: {e}")

    return devices


def read_characteristics_simpleble(  # type: ignore # pylint: disable=too-many-locals,too-many-branches,too-many-statements,too-many-nested-blocks
    address: str, target_uuids: list[str] | None = None
) -> dict[str, Any]:
    """Read characteristics from a BLE device using SimpleBLE.

    Args:
        address: BLE device address
        target_uuids: List of characteristic UUIDs to read (if None, reads ALL readable characteristics)

    Returns:
        Dictionary mapping UUID to (raw_data, char_object) tuples
    """
    if not simplepyble_available or simplepyble_module is None:
        print("❌ SimplePyBLE not available")
        return {}

    results: dict[str, Any] = {}

    print(f"🔵 Connecting to device using SimpleBLE: {address}")

    try:
        # Get adapter
        adapters = simplepyble_module.Adapter.get_adapters()  # noqa: F821 # pylint: disable=undefined-variable,no-member
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
                if hasattr(peripheral, "address") and peripheral.address() == address:
                    target_peripheral = peripheral
                    break
                if peripheral.identifier() == address:
                    target_peripheral = peripheral
                    break
            except Exception:  # pylint: disable=broad-exception-caught
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
        if target_uuids:
            print(f"\n📊 Reading {len(target_uuids)} specific characteristics...")
        else:
            print("\n📊 Reading ALL readable characteristics...")

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

                        # Use peripheral.read(service_uuid, char_uuid)
                        raw_data = target_peripheral.read(service_uuid, char_uuid)

                        if not raw_data:
                            print("     ⚠️  No data read")
                            continue

                        # Convert to bytes if needed. Cast to Any to avoid example-only mypy errors
                        from typing import Any as _Any

                        raw_any: _Any = raw_data

                        if isinstance(raw_any, str):
                            raw_bytes = raw_any.encode("utf-8")
                        elif hasattr(raw_any, "__iter__") and not isinstance(
                            raw_any, bytes
                        ):
                            # raw_any is an iterable of ints (e.g., array-like), convert to bytes
                            raw_bytes = bytes(raw_any)  # type: ignore[arg-type]
                        else:
                            raw_bytes = raw_any

                        results[char_uuid_short] = (raw_bytes, char)

                    except Exception as e:  # pylint: disable=broad-exception-caught
                        print(f"     ❌ Error reading characteristic: {e}")

            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"  ❌ Error processing service: {e}")

        # Disconnect
        target_peripheral.disconnect()
        print(f"\n🔌 Disconnected from {address}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Connection failed: {e}")

    return results


def read_and_parse_with_simpleble(
    address: str, target_uuids: list[str] | None = None
) -> dict[str, Any]:
    """Read characteristics from a BLE device using SimpleBLE and parse with SIG standards.

    Args:
        address: BLE device address
        target_uuids: List of characteristic UUIDs to read (if None, performs comprehensive analysis)

    Returns:
        Dictionary of parsed characteristic data or comprehensive analysis results
    """
    if not simplepyble_available or simplepyble_module is None:
        print("❌ SimplePyBLE not available")
        return {}

    if target_uuids is None:
        # Use comprehensive device analysis for real device discovery
        print("🔍 Using comprehensive device analysis...")
        return comprehensive_device_analysis_simpleble(address, simplepyble_module)  # type: ignore[arg-type] # noqa: F821 # pylint: disable=undefined-variable

    # Use targeted reading for specific UUIDs (legacy mode)
    print("📋 Reading specific characteristics...")

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


def handle_scan_mode_simpleble(args: argparse.Namespace) -> None:
    """Handle scan-only mode for SimpleBLE."""
    devices = scan_for_devices_simpleble(args.timeout)
    if not devices:
        print("No devices found")
    if not args.address:
        print("Scan complete. Use --address to connect.")


def handle_device_operations_simpleble(args: argparse.Namespace) -> None:
    """Handle device-specific operations for SimpleBLE."""
    results = read_and_parse_with_simpleble(args.address, args.uuids)
    if results:
        display_simpleble_results(results)


def display_simpleble_results(results: dict[str, Any]) -> None:
    """Display SimpleBLE results in a consistent format."""
    if "stats" in results:
        if results["parsed_data"]:
            for _uuid, data in results["parsed_data"].items():
                unit_str = f" {data['unit']}" if data["unit"] else ""
                print(f"{data['name']}: {data['value']}{unit_str}")
    else:
        for _uuid, result in results.items():
            if isinstance(result, dict) and result.get("parse_success"):
                unit_str = f" {result.get('unit', '')}" if result.get("unit") else ""
                print(
                    f"{result.get('name', 'Unknown')}: {result.get('value', 'N/A')}{unit_str}"
                )


def main() -> None:  # pylint: disable=too-many-nested-blocks
    """Main function demonstrating SimpleBLE + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(
        description="SimpleBLE + bluetooth_sig integration example"
    )
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument(
        "--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds"
    )
    parser.add_argument(
        "--uuids", "-u", nargs="+", help="Specific characteristic UUIDs to read"
    )

    args = parser.parse_args()

    if not simplepyble_available:
        print("❌ SimplePyBLE is not available on this system.")
        print("This example requires SimplePyBLE which needs C++ build tools.")
        print("Install with: pip install simplepyble")
        print(
            "Note: Requires commercial license for commercial use since January 2025."
        )
        return

    try:
        if args.scan or not args.address:
            handle_scan_mode_simpleble(args)
            return

        if args.address:
            handle_device_operations_simpleble(args)

    except KeyboardInterrupt:
        print("Demo interrupted by user")
    except (OSError, RuntimeError, ValueError) as e:
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    main()
