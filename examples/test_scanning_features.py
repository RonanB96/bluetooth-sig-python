#!/usr/bin/env python3
"""Test script for BLE scanning features on real devices.

This script demonstrates all scanning capabilities:
- Basic scan
- Filtered scan (by service UUID, RSSI, name)
- Find device by address
- Find device by name
- Find device by custom filter
- Scan with callback
- Scan stream (async iterator)

Usage:
    python examples/test_scanning_features.py [--timeout 5] [--address AA:BB:CC:DD:EE:FF]
    python examples/test_scanning_features.py -c bleak-retry --timeout 10
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(__file__).rsplit("/examples", 1)[0])

from bluetooth_sig.device.client import ClientManagerProtocol
from bluetooth_sig.types.device_types import ScanFilter, ScannedDevice
from examples.utils.library_detection import (
    AVAILABLE_LIBRARIES,
    get_connection_manager_class,
    show_library_availability,
)

# Display constants
_MAX_SERVICES_TO_DISPLAY = 5
_MAX_DEVICES_TO_DISPLAY = 10
_APPLE_COMPANY_ID = 0x004C


def format_device(device: ScannedDevice, indent: str = "  ") -> str:
    """Format a ScannedDevice for display."""
    lines = [f"{indent}Address: {device.address}"]
    lines.append(f"{indent}Name: {device.name or '(no name)'}")

    if device.advertisement_data:
        adv = device.advertisement_data
        if adv.rssi is not None:
            lines.append(f"{indent}RSSI: {adv.rssi} dBm")

        core = adv.ad_structures.core
        if core.service_uuids:
            uuid_list = ", ".join(str(uuid) for uuid in core.service_uuids[:_MAX_SERVICES_TO_DISPLAY])
            lines.append(f"{indent}Services: {uuid_list}")
            if len(core.service_uuids) > _MAX_SERVICES_TO_DISPLAY:
                remaining = len(core.service_uuids) - _MAX_SERVICES_TO_DISPLAY
                lines.append(f"{indent}          ... and {remaining} more")

        if core.manufacturer_data:
            mfr_ids = list(core.manufacturer_data.keys())
            lines.append(f"{indent}Manufacturer IDs: {mfr_ids}")

    return "\n".join(lines)


async def test_basic_scan(
    manager: type[ClientManagerProtocol],
    timeout: float = 5.0,
) -> list[ScannedDevice]:
    """Test basic scanning without filters."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Scan")
    print("=" * 60)
    print(f"Scanning for {timeout} seconds...")

    devices = await manager.scan(timeout=timeout)

    print(f"\nFound {len(devices)} devices:")
    for i, device in enumerate(devices[:_MAX_DEVICES_TO_DISPLAY], 1):
        print(f"\n[{i}] {device.name or device.address}")
        print(format_device(device))

    if len(devices) > _MAX_DEVICES_TO_DISPLAY:
        print(f"\n... and {len(devices) - _MAX_DEVICES_TO_DISPLAY} more devices")

    return devices


async def test_filtered_scan_rssi(
    manager: type[ClientManagerProtocol],
    timeout: float = 5.0,
    threshold: int = -70,
) -> list[ScannedDevice]:
    """Test scanning with RSSI filter (nearby devices only)."""
    print("\n" + "=" * 60)
    print(f"TEST 2: RSSI Filtered Scan (>= {threshold} dBm)")
    print("=" * 60)
    print(f"Scanning for nearby devices (RSSI >= {threshold} dBm)...")

    filters = ScanFilter(rssi_threshold=threshold)
    devices = await manager.scan(timeout=timeout, filters=filters)

    print(f"\nFound {len(devices)} nearby devices:")
    for device in devices:
        rssi = device.advertisement_data.rssi if device.advertisement_data else "?"
        print(f"  - {device.name or device.address}: {rssi} dBm")

    return devices


async def test_filtered_scan_service(
    manager: type[ClientManagerProtocol],
    timeout: float = 5.0,
) -> list[ScannedDevice]:
    """Test scanning with service UUID filter."""
    print("\n" + "=" * 60)
    print("TEST 3: Service UUID Filtered Scan")
    print("=" * 60)

    # Common service UUIDs to search for
    common_services = {
        "180d": "Heart Rate",
        "180f": "Battery",
        "1800": "Generic Access",
        "1801": "Generic Attribute",
        "fe9f": "Google Fast Pair",
    }

    all_found: list[ScannedDevice] = []

    for uuid, name in common_services.items():
        print(f"\nSearching for {name} Service ({uuid})...")
        filters = ScanFilter(service_uuids=[uuid])
        devices = await manager.scan(timeout=timeout / 2, filters=filters)

        if devices:
            print(f"  Found {len(devices)} device(s) with {name} service:")
            for device in devices:
                print(f"    - {device.name or device.address}")
            all_found.extend(devices)
        else:
            print(f"  No devices found with {name} service")

    return all_found


async def test_find_by_address(
    manager: type[ClientManagerProtocol],
    address: str,
    timeout: float = 10.0,
) -> ScannedDevice | None:
    """Test finding a device by address."""
    print("\n" + "=" * 60)
    print("TEST 4: Find Device by Address")
    print("=" * 60)
    print(f"Searching for device: {address}")
    print(f"Timeout: {timeout} seconds")

    start = datetime.now()
    device = await manager.find_device(ScanFilter(addresses=[address]), timeout=timeout)
    elapsed = (datetime.now() - start).total_seconds()

    if device:
        print(f"\n✅ Found device in {elapsed:.2f}s:")
        print(format_device(device))
    else:
        print(f"\n❌ Device not found within {timeout}s")

    return device


async def test_find_by_name(
    manager: type[ClientManagerProtocol],
    name: str,
    timeout: float = 10.0,
) -> ScannedDevice | None:
    """Test finding a device by name."""
    print("\n" + "=" * 60)
    print("TEST 5: Find Device by Name")
    print("=" * 60)
    print(f"Searching for device named: '{name}'")
    print(f"Timeout: {timeout} seconds")

    start = datetime.now()
    device = await manager.find_device(ScanFilter(names=[name]), timeout=timeout)
    elapsed = (datetime.now() - start).total_seconds()

    if device:
        print(f"\n✅ Found device in {elapsed:.2f}s:")
        print(format_device(device))
    else:
        print(f"\n❌ Device not found within {timeout}s")

    return device


async def test_find_by_filter(
    manager: type[ClientManagerProtocol],
    timeout: float = 10.0,
) -> ScannedDevice | None:
    """Test finding a device by custom filter."""
    print("\n" + "=" * 60)
    print("TEST 6: Find Device by Custom Filter")
    print("=" * 60)
    print("Searching for device with Apple manufacturer data (0x004C)...")

    def has_apple_data(device: ScannedDevice) -> bool:
        if device.advertisement_data is None:
            return False
        mfr = device.advertisement_data.ad_structures.core.manufacturer_data
        return _APPLE_COMPANY_ID in mfr  # Apple's company ID

    start = datetime.now()
    device = await manager.find_device(ScanFilter(filter_func=has_apple_data), timeout=timeout)
    elapsed = (datetime.now() - start).total_seconds()

    if device:
        print(f"\n✅ Found Apple device in {elapsed:.2f}s:")
        print(format_device(device))
    else:
        print(f"\n❌ No Apple device found within {timeout}s")

    return device


async def test_scan_with_callback(
    manager: type[ClientManagerProtocol],
    timeout: float = 5.0,
) -> list[ScannedDevice]:
    """Test scanning with real-time callback."""
    print("\n" + "=" * 60)
    print("TEST 7: Scan with Callback")
    print("=" * 60)
    print("Scanning with real-time callbacks...")
    print("-" * 40)

    device_count = 0

    async def on_device(device: ScannedDevice) -> None:
        nonlocal device_count
        device_count += 1
        rssi = device.advertisement_data.rssi if device.advertisement_data else "?"
        name = device.name or "(no name)"
        print(f"  [{device_count:3d}] {name[:30]:30s} | {device.address} | {rssi} dBm")

    devices = await manager.scan(
        timeout=timeout,
        filters=ScanFilter(rssi_threshold=-85),  # Only moderately close devices
        callback=on_device,
    )

    print("-" * 40)
    print(f"Total: {len(devices)} unique devices discovered via callback")

    return devices


async def test_scan_stream(
    manager: type[ClientManagerProtocol],
    timeout: float = 5.0,
    max_devices: int = 5,
) -> list[ScannedDevice]:
    """Test scanning as async stream with early termination."""
    print("\n" + "=" * 60)
    print("TEST 8: Scan Stream (Async Iterator)")
    print("=" * 60)
    print(f"Streaming devices (will stop after {max_devices} or {timeout}s)...")
    print("-" * 40)

    collected: list[ScannedDevice] = []

    async for device in manager.scan_stream(
        timeout=timeout,
        filters=ScanFilter(rssi_threshold=-80),
    ):
        collected.append(device)
        rssi = device.advertisement_data.rssi if device.advertisement_data else "?"
        name = device.name or "(no name)"
        print(f"  [{len(collected):2d}] {name[:30]:30s} | {rssi} dBm")

        if len(collected) >= max_devices:
            print("\n  >>> Reached target count, stopping scan early!")
            break

    print("-" * 40)
    print(f"Collected {len(collected)} devices via stream")

    return collected


async def test_passive_scan(
    manager: type[ClientManagerProtocol],
    timeout: float = 3.0,
) -> list[ScannedDevice]:
    """Test passive scanning mode."""
    print("\n" + "=" * 60)
    print("TEST 9: Passive Scanning Mode")
    print("=" * 60)
    print(f"Scanning in passive mode for {timeout} seconds...")

    try:
        devices = await manager.scan(
            timeout=timeout,
            scanning_mode="passive",
        )
        print(f"\n✅ Found {len(devices)} devices in passive mode")
        for device in devices[:_MAX_SERVICES_TO_DISPLAY]:
            print(f"  - {device.name or device.address}")

        if len(devices) > _MAX_SERVICES_TO_DISPLAY:
            print(f"  ... and {len(devices) - _MAX_SERVICES_TO_DISPLAY} more")
        return devices
    except Exception as e:
        # Catch any unexpected errors
        print(f"\n⚠️  Passive scanning error: {e}")
        return []


async def run_all_tests(
    manager: type[ClientManagerProtocol],
    args: argparse.Namespace,
) -> None:
    """Run all scanning tests.

    Args:
        manager: Connection manager class to use for scanning
        args: Parsed command line arguments
    """
    print("\n" + "#" * 60)
    print("# BLE SCANNING FEATURES TEST SUITE")
    print("#" * 60)
    print(f"Connection manager: {manager.__name__}")
    print(f"Timeout per test: {args.timeout}s")

    # Check if the manager supports scanning
    if not manager.supports_scanning:
        print(f"\n❌ {manager.__name__} does not support scanning")
        return

    # Test 1: Basic scan
    all_devices = await test_basic_scan(manager, args.timeout)

    # Test 2: RSSI filtered scan
    await test_filtered_scan_rssi(manager, args.timeout, threshold=-70)

    # Test 3: Service UUID filtered scan
    await test_filtered_scan_service(manager, args.timeout)

    # Test 4: Find by address (if provided or use first found device)
    if args.address:
        await test_find_by_address(manager, args.address, args.timeout * 2)
    elif all_devices:
        print("\n(Using first discovered device for address test)")
        await test_find_by_address(manager, all_devices[0].address, args.timeout)

    # Test 5: Find by name (if provided or use first named device)
    if args.name:
        await test_find_by_name(manager, args.name, args.timeout * 2)
    else:
        named_devices = [d for d in all_devices if d.name]
        if named_devices:
            print("\n(Using first named device for name test)")
            await test_find_by_name(manager, named_devices[0].name, args.timeout)  # type: ignore[arg-type]

    # Test 6: Find by custom filter
    await test_find_by_filter(manager, args.timeout)

    # Test 7: Callback scan
    await test_scan_with_callback(manager, args.timeout)

    # Test 8: Stream scan
    await test_scan_stream(manager, args.timeout, max_devices=5)

    # Test 9: Passive scan
    await test_passive_scan(manager, min(args.timeout, 3.0))

    print("\n" + "#" * 60)
    print("# ALL TESTS COMPLETE")
    print("#" * 60)


def main() -> None:
    """Parse arguments and run tests."""
    # Show available libraries
    show_library_availability()

    # Get available connection managers
    available_managers = list(AVAILABLE_LIBRARIES.keys())
    if not available_managers:
        print("\n❌ No BLE libraries available. Install with: pip install .[examples]")
        sys.exit(1)

    default_manager = available_managers[0]

    parser = argparse.ArgumentParser(
        description="Test BLE scanning features on real devices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available connection managers: {", ".join(available_managers)}

Examples:
    python examples/test_scanning_features.py
    python examples/test_scanning_features.py -c bleak-retry --timeout 10
    python examples/test_scanning_features.py --address AA:BB:CC:DD:EE:FF
    python examples/test_scanning_features.py --name "Polar H10"
        """,
    )

    parser.add_argument(
        "--connection-manager",
        "-c",
        choices=available_managers,
        default=default_manager,
        help=f"BLE connection manager to use (default: {default_manager})",
    )

    parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=5.0,
        help="Timeout for each scan test in seconds (default: 5.0)",
    )

    parser.add_argument(
        "--address",
        "-a",
        type=str,
        help="Specific device address to search for",
    )

    parser.add_argument(
        "--name",
        "-n",
        type=str,
        help="Specific device name to search for",
    )

    args = parser.parse_args()

    # Get the connection manager class
    try:
        manager_class = get_connection_manager_class(args.connection_manager)
    except (ValueError, ImportError) as e:
        print(f"\n❌ Failed to load connection manager: {e}")
        sys.exit(1)

    try:
        asyncio.run(run_all_tests(manager_class, args))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        raise


if __name__ == "__main__":
    main()
