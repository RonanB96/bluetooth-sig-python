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
from types import ModuleType
from typing import Any, Callable, cast

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.data_types import CharacteristicData
from bluetooth_sig.types.uuid import BluetoothUUID
from examples.utils.models import DeviceInfo, ReadResult

# Avoid importing examples.shared_utils at module import time to keep this
# module side-effect free and avoid confusing type checkers that may not
# include the examples/ path in their search paths.

# Type alias for the scanning helper imported from the SimplePyBLE integration
ScanFunc = Callable[[ModuleType, float], list[DeviceInfo]]


def parse_results(raw_results: dict[str, ReadResult]) -> dict[str, ReadResult]:
    """Typed wrapper around canonical parsing helper in examples.utils."""
    from examples.utils.data_parsing import parse_and_display_results_sync

    # Use the synchronous helper because SimplePyBLE integration is
    # synchronous at the call site.
    return parse_and_display_results_sync(raw_results, library_name="SimplePyBLE")


def scan_devices_simpleble(simpleble_module: ModuleType, timeout: float = 10.0) -> list[DeviceInfo]:
    """Wrapper ensuring precise typing for scanning helper."""
    from .utils.simpleble_integration import scan_devices_simpleble as _scan

    _scan_fn = cast(ScanFunc, _scan)
    return _scan_fn(simpleble_module, timeout)


def comprehensive_device_analysis_simpleble(
    address: str,
    simpleble_module: ModuleType,
) -> dict[str, CharacteristicData]:
    """Wrapper ensuring precise typing for comprehensive analysis helper."""
    from .utils.simpleble_integration import comprehensive_device_analysis_simpleble as _analysis

    AnalysisFunc = Callable[[str, ModuleType], dict[str, CharacteristicData]]
    analysis_fn = cast(AnalysisFunc, _analysis)
    return analysis_fn(address, simpleble_module)


def create_simpleble_connection_manager(address: str, simpleble_module: ModuleType) -> ConnectionManagerProtocol:
    """Factory returning a connection manager instance with explicit typing."""
    from examples.connection_managers.simpleble import SimplePyBLEConnectionManager

    manager = SimplePyBLEConnectionManager(address, simpleble_module)
    return cast(ConnectionManagerProtocol, manager)


def scan_for_devices_simpleble(timeout: float = 10.0) -> list[DeviceInfo]:  # type: ignore
    """Scan for BLE devices using SimpleBLE.

    Args:
        timeout: Scan duration in seconds

    Returns:
        List of device dictionaries with address, name, and RSSI

    """
    # Determine backend availability at runtime to avoid import-time errors
    from .utils import library_detection

    simplepyble_available = getattr(library_detection, "simplepyble_available", False)
    simplepyble_module = getattr(library_detection, "simplepyble_module", None)

    if not simplepyble_available:  # type: ignore[possibly-unbound]
        print("❌ SimplePyBLE not available")
        return []

    assert simplepyble_module is not None

    print(f"🔍 Scanning for BLE devices ({timeout}s)...")
    from .utils.simpleble_integration import scan_devices_simpleble as _scan

    scan_func = cast(ScanFunc, _scan)

    devices = scan_func(simplepyble_module, timeout)

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
) -> dict[str, ReadResult] | dict[str, CharacteristicData]:
    """Read characteristics from a BLE device using SimpleBLE and parse with SIG standards."""
    from .utils import library_detection

    if not getattr(library_detection, "simplepyble_available", False):
        print("❌ SimplePyBLE not available")
        return {}

    simplepyble_module = getattr(library_detection, "simplepyble_module", None)

    if target_uuids is None:
        # Use comprehensive device analysis for real device discovery
        print("🔍 Using comprehensive device analysis...")
        if simplepyble_module is None:
            print("❌ SimplePyBLE module not available for analysis")
            return {}
        return comprehensive_device_analysis_simpleble(address, simplepyble_module)

    # At this point simplepyble_module may be None; ensure it's a ModuleType for downstream calls
    if simplepyble_module is None:
        print("❌ SimplePyBLE module not available for reading")
        return {}

    module = cast(ModuleType, simplepyble_module)

    async def _collect() -> dict[str, ReadResult]:
        manager = create_simpleble_connection_manager(address, module)
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
    results: dict[str, ReadResult] | dict[str, CharacteristicData] | dict[BluetoothUUID, CharacteristicData],
) -> None:
    """Display SimpleBLE results in a consistent format.

    Accepts either a mapping of short UUID strings to :class:`ReadResult`
    or to :class:`CharacteristicData` objects produced by the translator.
    """
    if not results:
        print("No results to display")
        return

    # Normalise BluetoothUUID keys to short strings if needed. Use a
    # precise union type for values so the type checker can narrow
    # correctly on runtime type checks.
    normalized: dict[str, ReadResult | CharacteristicData | dict[str, Any]] = {}
    for k, v in results.items():
        key_str = str(k)
        normalized[key_str] = v  # type: ignore[assignment]

    for uuid_short, value in normalized.items():
        # ReadResult from connection helpers
        if isinstance(value, ReadResult):
            if value.parsed and getattr(value.parsed, "parse_success", False):
                unit_str = f" {value.parsed.unit}" if getattr(value.parsed, "unit", None) else ""
                print(f"{value.parsed.name}: {value.parsed.value}{unit_str}")
            elif value.error:
                print(f"{uuid_short}: Error - {value.error}")
            else:
                print(f"{uuid_short}: Raw {len(value.raw_data)} bytes (read_time={value.read_time:.3f}s)")

        # CharacteristicData objects
        elif isinstance(value, CharacteristicData):
            if value.parse_success:
                unit_str = f" {value.unit}" if value.unit else ""
                print(f"{value.name}: {value.value}{unit_str}")
            else:
                print(f"{str(value.uuid)}: Parse failed")

        # Loose dict fallback (legacy forms)
        elif isinstance(value, dict):
            mapping = value  # type: ignore[assignment]
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
            print(f"{uuid_short}: Unsupported result type: {type(value)!r}")  # type: ignore[unreachable]


def main() -> None:  # pylint: disable=too-many-nested-blocks
    """Main function demonstrating SimpleBLE + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(description="SimpleBLE + bluetooth_sig integration example")
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds")
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific characteristic UUIDs to read")

    args = parser.parse_args()

    from .utils import library_detection

    simplepyble_available = getattr(library_detection, "simplepyble_available", False)

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
