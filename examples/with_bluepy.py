#!/usr/bin/env python3
"""BluePy integration example.

This example demonstrates using BluePy as a BLE library combined with
bluetooth_sig for standards-compliant data parsing. BluePy offers a
Linux-specific BLE interface with synchronous API.

Benefits:
- Native Linux BLE library
- Synchronous API (wrapped in async for compatibility)
- Pure SIG standards parsing
- Demonstrates framework-agnostic design

Requirements:
    pip install bluepy  # Linux only

Usage:
    python with_bluepy.py --scan
    python with_bluepy.py --address 12:34:56:78:9A:BC
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Any

from bluetooth_sig.gatt.characteristics.base import CharacteristicData
from examples.utils.models import DeviceInfo, ReadResult

# Type alias for the scanning helper imported from the BluePy integration
ScanFunc = object


def parse_results(raw_results: dict[str, ReadResult]) -> dict[str, ReadResult]:
    """Typed wrapper around canonical parsing helper in examples.utils."""
    from examples.utils.data_parsing import parse_and_display_results_sync

    # Use the synchronous helper because BluePy integration is
    # synchronous at the call site.
    return parse_and_display_results_sync(raw_results)


def scan_for_devices(timeout: float = 10.0) -> list[DeviceInfo]:
    """Scan for BLE devices using BluePy Scanner.

    Args:
        timeout: Scan timeout in seconds

    Returns:
        List of discovered devices

    """
    try:
        from examples.utils.device_scanning import scan_with_bluepy

        device_tuples = scan_with_bluepy(timeout)
        devices = []
        for name, address, rssi in device_tuples:
            devices.append(DeviceInfo(name=name, address=address, rssi=rssi))
        return devices

    except ImportError as e:
        print(f"❌ BluePy not available: {e}")
        print("Install with: pip install bluepy")
        return []
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        return []


async def demonstrate_bluepy_device_reading(address: str) -> dict[str, CharacteristicData[Any]]:
    """Demonstrate reading characteristics from a BLE device using BluePy.

    Args:
        address: BLE device address

    Returns:
        Dictionary of parsed characteristic data

    """
    try:
        from examples.connection_managers.bluepy import BluePyConnectionManager
        from examples.utils.connection_helpers import read_characteristics_with_manager

        print(f"🔍 Connecting to {address} using BluePy...")

        # Create BluePy connection manager
        connection_manager = BluePyConnectionManager(address)

        # Read characteristics using the common helper
        raw_results = await read_characteristics_with_manager(connection_manager)

        # Parse and display results
        parsed_results_map = parse_results(raw_results)

        print(f"\n📊 Successfully read {len(parsed_results_map)} characteristics")

        # Extract CharacteristicData from ReadResult
        final_results: dict[str, CharacteristicData[Any]] = {}
        for uuid, result in parsed_results_map.items():
            if result.parsed:
                final_results[uuid] = result.parsed

        return final_results

    except ImportError as e:
        print(f"❌ BluePy not available: {e}")
        print("Install with: pip install bluepy")
        return {}
    except Exception as e:
        print(f"❌ BluePy operation failed: {e}")
        return {}


async def demonstrate_bluepy_service_discovery(address: str) -> None:
    """Demonstrate service discovery using BluePy.

    Args:
        address: BLE device address

    """
    try:
        from examples.connection_managers.bluepy import BluePyConnectionManager

        print(f"🔍 Discovering services on {address} using BluePy...")

        connection_manager = BluePyConnectionManager(address)
        await connection_manager.connect()

        # Get services using the connection manager
        services = await connection_manager.get_services()

        print(f"✅ Found {len(services)} services:")
        for i, service in enumerate(services, 1):
            service_name = getattr(service.service, "name", "Unknown Service")
            service_uuid = getattr(service.service, "uuid", "Unknown UUID")
            print(f"  {i}. {service_name} ({service_uuid})")

        await connection_manager.disconnect()

    except ImportError as e:
        print(f"❌ BluePy not available: {e}")
        print("Install with: pip install bluepy")
    except Exception as e:
        print(f"❌ Service discovery failed: {e}")


def display_device_list(devices: list[DeviceInfo]) -> None:
    """Display a formatted list of discovered devices.

    Args:
        devices: List of discovered devices

    """
    if not devices:
        print("❌ No devices found")
        return

    print(f"\n📱 Found {len(devices)} BLE devices:")
    print("-" * 60)
    for i, device in enumerate(devices, 1):
        rssi_str = f"{device.rssi} dBm" if device.rssi is not None else "Unknown"
        print(f"{i:2d}. {device.name:<30} {device.address} ({rssi_str})")


async def main() -> None:
    """Main function for BluePy integration demonstration."""
    parser = argparse.ArgumentParser(description="BluePy BLE integration example")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scan", action="store_true", help="Scan for BLE devices")
    group.add_argument("--address", "-a", help="Connect to specific device address")

    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds")

    args = parser.parse_args()

    # Check if BluePy is available
    try:
        import bluepy  # type: ignore[import-untyped]

        del bluepy  # Clean up the import check
    except ImportError:
        print("❌ BluePy not available!")
        print("Install with: pip install bluepy")
        print("Note: BluePy only works on Linux")
        return

    print("🔵 BluePy BLE Integration Example")
    print("=" * 40)

    if args.scan:
        print(f"🔍 Scanning for devices (timeout: {args.timeout}s)...")
        devices = scan_for_devices(args.timeout)
        display_device_list(devices)

        if devices:
            print("\n💡 To connect to a device, run:")
            print(f"   python {__file__} --address <ADDRESS>")

    elif args.address:
        print(f"🔗 Connecting to device: {args.address}")

        # First try service discovery
        await demonstrate_bluepy_service_discovery(args.address)

        # Then try reading characteristics
        await demonstrate_bluepy_device_reading(args.address)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
