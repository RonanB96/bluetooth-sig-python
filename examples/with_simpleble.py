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

# Set up paths for imports
import sys
from pathlib import Path

# pylint: disable=duplicate-code

# Add src directory for bluetooth_sig imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add parent directory for examples package imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add examples directory for utils imports
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import asyncio
from types import ModuleType
from typing import Any, cast

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.data_types import CharacteristicData
from bluetooth_sig.types.uuid import BluetoothUUID
from examples import shared_utils
from examples.utils import library_detection, simpleble_integration


def parse_results(raw_results: dict[str, tuple[bytes, float]]) -> dict[str, Any]:
    """Typed wrapper around shared example parser."""
    return shared_utils.parse_results(raw_results)


async def read_characteristics_with_manager(
    connection_manager: ConnectionManagerProtocol,
    target_uuids: list[str] | None = None,
    timeout: float = 10.0,
) -> dict[str, tuple[bytes, float]]:
    """Typed wrapper delegating to shared characteristic reader."""
    return await shared_utils.read_characteristics_with_manager(connection_manager, target_uuids, timeout)


def scan_devices_simpleble(simpleble_module: ModuleType, timeout: float = 10.0) -> list[dict[str, Any]]:
    """Wrapper ensuring precise typing for scanning helper."""
    return simpleble_integration.scan_devices_simpleble(simpleble_module, timeout)


def comprehensive_device_analysis_simpleble(
    address: str,
    simpleble_module: ModuleType,
) -> dict[BluetoothUUID, CharacteristicData]:
    """Wrapper ensuring precise typing for comprehensive analysis helper."""
    return simpleble_integration.comprehensive_device_analysis_simpleble(address, simpleble_module)


def create_simpleble_connection_manager(address: str, simpleble_module: ModuleType) -> ConnectionManagerProtocol:
    """Factory returning a connection manager instance with explicit typing."""
    manager = simpleble_integration.SimplePyBLEConnectionManager(address, simpleble_module)
    return cast(ConnectionManagerProtocol, manager)


simplepyble_available_raw = getattr(library_detection, "simplepyble_available", False)
simplepyble_available: bool = bool(simplepyble_available_raw)
simplepyble_module_attr = getattr(library_detection, "simplepyble_module", None)
simplepyble_module = cast(ModuleType, simplepyble_module_attr)


def scan_for_devices_simpleble(timeout: float = 10.0) -> list[dict[str, Any]]:  # type: ignore
    """Scan for BLE devices using SimpleBLE.

    Args:
        timeout: Scan duration in seconds

    Returns:
        List of device dictionaries with address, name, and RSSI

    """
    if not simplepyble_available:  # type: ignore[possibly-unbound]
        print("❌ SimplePyBLE not available")
        return []

    assert simplepyble_module is not None

    print(f"🔍 Scanning for BLE devices ({timeout}s)...")
    devices = scan_devices_simpleble(simplepyble_module, timeout)

    if not devices:
        print("❌ No BLE adapters found or scan failed")
        return []

    print(f"\n📡 Found {len(devices)} devices:")
    for index, device in enumerate(devices, 1):
        name = device.get("name", "Unknown")
        address = device.get("address", "Unknown")
        rssi = device.get("rssi", "N/A")
        print(f"  {index}. {name} ({address}) - RSSI: {rssi}dBm")

    return devices


def read_and_parse_with_simpleble(
    address: str, target_uuids: list[str] | None = None
) -> dict[str, Any] | dict[BluetoothUUID, CharacteristicData]:
    """Read characteristics from a BLE device using SimpleBLE and parse with SIG standards."""
    if not simplepyble_available:
        print("❌ SimplePyBLE not available")
        return {}

    if target_uuids is None:
        # Use comprehensive device analysis for real device discovery
        print("🔍 Using comprehensive device analysis...")
        return comprehensive_device_analysis_simpleble(address, simplepyble_module)

    async def _collect() -> dict[str, tuple[bytes, float]]:
        manager = create_simpleble_connection_manager(address, simplepyble_module)
        return await read_characteristics_with_manager(manager, target_uuids)

    raw_results: dict[str, tuple[bytes, float]] = asyncio.run(_collect())
    parsed_results: dict[str, Any] = parse_results(raw_results)

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
    results: dict[str, Any] | dict[str, CharacteristicData] | dict[BluetoothUUID, CharacteristicData],
) -> None:
    """Display SimpleBLE results in a consistent format."""
    # Type narrowing: check if results is dict[str, Any] with stats/parsed_data
    if "stats" in results and "parsed_data" in results:  # type: ignore[operator]
        # This must be dict[str, Any] from comprehensive analysis
        results_any = cast(dict[str, Any], results)
        parsed_data: Any = results_any["parsed_data"]
        if isinstance(parsed_data, dict):
            for _uuid, data in parsed_data.items():
                if isinstance(data, CharacteristicData):
                    unit_str = f" {data.unit}" if data.unit else ""
                    print(f"{data.name}: {data.value}{unit_str}")
                elif isinstance(data, dict):
                    unit_str = f" {data['unit']}" if data.get("unit") else ""
                    print(f"{data.get('name', str(_uuid))}: {data.get('value', 'N/A')}{unit_str}")
    else:
        for _uuid, result in results.items():
            if isinstance(result, CharacteristicData):
                if result.parse_success:
                    unit_str = f" {result.unit}" if result.unit else ""
                    print(f"{result.name}: {result.value}{unit_str}")
                else:
                    uuid_str = str(result.uuid)
                    print(f"{uuid_str}: Parse failed")
            elif isinstance(result, dict):
                result_mapping = cast(dict[str, Any], result)
                if result_mapping.get("parse_success"):
                    unit_value = result_mapping.get("unit", "")
                    unit_str = f" {unit_value}" if unit_value else ""
                    name_value = result_mapping.get("name", "Unknown")
                    value_value = result_mapping.get("value", "N/A")
                    print(f"{name_value}: {value_value}{unit_str}")


def main() -> None:  # pylint: disable=too-many-nested-blocks
    """Main function demonstrating SimpleBLE + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(description="SimpleBLE + bluetooth_sig integration example")
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds")
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific characteristic UUIDs to read")

    args = parser.parse_args()

    if not simplepyble_available:
        print("❌ SimplePyBLE is not available on this system.")
        print("This example requires SimplePyBLE which needs C++ build tools.")
        print("Install with: pip install simplepyble")
        print("Note: Requires commercial license for commercial use since January 2025.")
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
