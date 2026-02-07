#!/usr/bin/env python3
"""SimplePyBLE integration example.

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

from __future__ import annotations

import argparse
import asyncio
from typing import Any

import simplepyble

from bluetooth_sig.types.uuid import BluetoothUUID
from examples.utils.models import DeviceInfo, ReadResult


def parse_results(raw_results: dict[str, ReadResult]) -> dict[str, ReadResult]:
    """Typed wrapper around canonical parsing helper in examples.utils."""
    from examples.utils.data_parsing import parse_and_display_results_sync

    # Use the synchronous helper because SimplePyBLE integration is
    # synchronous at the call site.
    return parse_and_display_results_sync(raw_results, library_name="SimplePyBLE")


def scan_for_devices_simpleble(timeout: float = 10.0) -> list[DeviceInfo]:
    """Scan for BLE devices using SimpleBLE.

    Args:
        timeout: Scan duration in seconds

    Returns:
        List of device dictionaries with address, name, and RSSI

    """
    from .utils.simpleble_integration import scan_devices_simpleble

    print(f"🔍 Scanning for BLE devices ({timeout}s)...")
    devices = scan_devices_simpleble(simplepyble, timeout)

    if not devices:
        print("❌ No BLE adapters found or scan failed")
        return []

    print(f"\n📡 Found {len(devices)} devices:")
    for index, device in enumerate(devices, 1):
        name = device.name or "Unknown"
        address = device.address
        rssi = device.rssi if device.rssi is not None else "N/A"
        print(f"  {index}. {name} ({address}) - RSSI: {rssi}dBm")

    return devices


def read_and_parse_with_simpleble(
    address: str, target_uuids: list[str] | None = None
) -> dict[str, ReadResult] | dict[str, Any]:
    """Read characteristics from a BLE device using SimpleBLE and parse with SIG standards."""
    from examples.connection_managers.simpleble import SimplePyBLEClientManager

    from .utils.simpleble_integration import comprehensive_device_analysis_simpleble

    if target_uuids is None:
        # Use comprehensive device analysis for real device discovery
        print("🔍 Using comprehensive device analysis...")
        return comprehensive_device_analysis_simpleble(address, simplepyble)

    async def _collect() -> dict[str, ReadResult]:
        manager = SimplePyBLEClientManager(address, timeout=10.0)
        from examples.utils.connection_helpers import read_characteristics_with_manager

        return await read_characteristics_with_manager(manager, target_uuids)

    raw_results: dict[str, ReadResult] = asyncio.run(_collect())
    parsed_results: dict[str, ReadResult] = parse_results(raw_results)

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


def display_simpleble_results(
    results: dict[str, ReadResult] | dict[str, Any] | dict[BluetoothUUID, Any],
) -> None:
    """Display SimpleBLE results in a consistent format.

    Accepts either a mapping of short UUID strings to :class:`ReadResult`
    or to parsed values produced by the translator.
    """
    if not results:
        print("No results to display")
        return

    # Normalise BluetoothUUID keys to short strings if needed.
    normalized: dict[str, ReadResult | dict[str, Any] | Any] = {}
    for k, v in results.items():
        key_str = str(k)
        normalized[key_str] = v

    for uuid_short, value in normalized.items():
        # ReadResult from connection helpers
        if isinstance(value, ReadResult):
            if value.parsed is not None:
                print(f"{uuid_short}: {value.parsed}")
            elif value.error:
                print(f"{uuid_short}: Error - {value.error}")
            else:
                print(f"{uuid_short}: Raw {len(value.raw_data)} bytes (read_time={value.read_time:.3f}s)")

        # Loose dict fallback (legacy forms)
        elif isinstance(value, dict):
            mapping = value
            if mapping.get("parse_success"):
                unit_val = mapping.get("unit", "")
                unit_str = f" {unit_val}" if unit_val else ""
                name_value = mapping.get("name", "Unknown")
                value_value = mapping.get("value", "N/A")
                print(f"{name_value}: {value_value}{unit_str}")
            elif mapping.get("error"):
                print(f"{uuid_short}: Error - {mapping.get('error')}")
            else:
                print(f"{uuid_short}: Unknown legacy dict format")

        else:
            # Direct parsed value
            print(f"{uuid_short}: {value}")


def main() -> None:  # pylint: disable=too-many-nested-blocks
    """Main function demonstrating SimpleBLE + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(description="SimpleBLE + bluetooth_sig integration example")
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds")
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific characteristic UUIDs to read")

    args = parser.parse_args()

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
