#!/usr/bin/env python3
"""Bleak-retry-connector integration example.

Demonstrates robust BLE connections with retry logic combined with the
bluetooth_sig translator for production-ready parsing patterns.
"""

from __future__ import annotations

import argparse
import asyncio
import time
from typing import Any

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.gatt.characteristics.base import CharacteristicData


async def robust_device_reading(
    address: str, backend: str = "bleak-retry", retries: int = 3
) -> dict[str, CharacteristicData[Any]]:
    """Robust device reading with automatic retry and error recovery.

    Args:
        address: BLE device address
        backend: BLE backend to use (only "bleak-retry" supported)
        retries: Number of connection retry attempts

    Returns:
        Dictionary of parsed characteristic data

    """
    if backend != "bleak-retry":
        print(f"❌ Only bleak-retry backend is supported in this example. Got: {backend}")
        return {}

    from examples.connection_managers.bleak_retry import BleakRetryConnectionManager  # type: ignore

    from .utils.mock_data import get_default_characteristic_uuids  # type: ignore

    target_uuids = get_default_characteristic_uuids()
    translator = BluetoothSIGTranslator()

    manager = BleakRetryConnectionManager(address, max_attempts=retries)
    device = Device(manager, translator)
    await device.connect()

    # First discover what characteristics are actually available
    print("🔍 Discovering available characteristics...")
    try:
        services = await device.discover_services()
        available_uuids = []
        for _service_uuid, service_info in services.items():
            for char_uuid in service_info.characteristics.keys():
                # Convert full UUID to short form for comparison
                short_uuid = char_uuid[4:8].upper() if len(char_uuid) > 8 else char_uuid.upper()
                available_uuids.append(short_uuid)
        print(f"✅ Found {len(available_uuids)} readable characteristics")

        # Filter target UUIDs to only those available on this device
        target_uuids = [uuid for uuid in target_uuids if uuid.upper() in available_uuids]
        print(f"📋 Will read {len(target_uuids)} matching characteristics: {target_uuids}")
    except Exception as e:
        print(f"⚠️ Service discovery failed, trying predefined characteristics: {e}")

    results: dict[str, CharacteristicData[Any]] = {}
    for uuid in target_uuids:
        try:
            parsed = await device.read(uuid)
            if parsed and getattr(parsed, "parse_success", False):
                results[uuid] = parsed
                unit_str = f" {parsed.unit}" if parsed.unit else ""
                print(f"✅ {uuid}: {parsed.name}: {parsed.value}{unit_str}")
            else:
                print(f"⚠️ {uuid}: Parse failed or no data")
        except Exception as e:
            print(f"❌ {uuid}: Read failed - {e}")

    await device.disconnect()
    print(f"📊 Device results: {results}")
    return results


async def robust_service_discovery(address: str) -> dict[str, CharacteristicData[Any]]:
    """Discover all services and characteristics with robust connection.

    Args:
        address: BLE device address

    Returns:
        Dictionary of discovered services and characteristics

    """
    print(f"🔍 Service discovery with {address} - Feature not yet implemented")
    return {}


async def perform_single_reading(address: str, translator: BluetoothSIGTranslator, target_uuids: list[str]) -> bool:
    """Perform a single reading cycle and return success status."""
    try:
        # Use robust connection with retry (import at runtime)
        from examples.connection_managers.bleak_retry import BleakRetryConnectionManager  # type: ignore
        from examples.utils.connection_helpers import read_characteristics_with_manager  # type: ignore

        manager = BleakRetryConnectionManager(address)
        raw_results = await read_characteristics_with_manager(manager, target_uuids)

        if raw_results:
            print(f"📊 Reading at {time.strftime('%H:%M:%S')}:")
            for uuid_short, read_result in raw_results.items():
                result = translator.parse_characteristic(uuid_short, read_result.raw_data)
                if result.parse_success:
                    unit_str = f" {result.unit}" if result.unit else ""
                    print(f"   {result.name}: {result.value}{unit_str}")
            return True

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"⚠️  Reading failed: {e}")

    return False


async def continuous_monitoring(address: str, duration: int = 60) -> None:  # pylint: disable=too-many-nested-blocks
    """Continuously monitor a device with automatic reconnection.

    Args:
        address: BLE device address
        duration: Monitoring duration in seconds

    """
    print(f"📊 Starting continuous monitoring of {address} for {duration}s...")
    print("🔄 Auto-reconnection enabled")

    translator = BluetoothSIGTranslator()
    target_uuids = ["2A19", "2A6E", "2A6F"]  # Battery, Temperature, Humidity

    start_time = time.time()
    reading_count = 0

    try:
        while time.time() - start_time < duration:
            if await perform_single_reading(address, translator, target_uuids):
                reading_count += 1

            # Wait between readings
            await asyncio.sleep(5)

    except KeyboardInterrupt:
        print(f"🛑 Monitoring stopped by user after {reading_count} readings")


async def notification_monitoring(address: str, duration: int = 60) -> None:
    """Monitor device notifications with robust connection.

    Args:
        address: BLE device address
        duration: Monitoring duration in seconds

    """
    print(f"🔔 Notification monitoring with {address} for {duration}s - Feature not yet implemented")


async def main() -> None:
    """Main function demonstrating robust BLE patterns."""
    parser = argparse.ArgumentParser(description="Robust BLE with bleak-retry-connector + SIG parsing")
    parser.add_argument("--address", "-a", help="BLE device address")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--monitor", "-m", action="store_true", help="Continuous monitoring")
    parser.add_argument("--notifications", "-n", action="store_true", help="Monitor notifications")
    parser.add_argument("--discover", "-d", action="store_true", help="Service discovery")
    parser.add_argument("--duration", "-t", type=int, default=60, help="Duration for monitoring")

    args = parser.parse_args()

    from examples.connection_managers.bleak_utils import scan_with_bleak_retry  # type: ignore

    from .utils.library_detection import bleak_retry_available  # type: ignore

    if not bleak_retry_available:
        print("Bleak-retry not available. Install with: pip install bleak-retry-connector")
        return

    try:
        if args.scan:
            await scan_with_bleak_retry()
            if not args.address:
                print("Scan complete. Use --address to connect.")
                return

        if args.address:
            if args.monitor:
                await continuous_monitoring(args.address, args.duration)
            elif args.notifications:
                await notification_monitoring(args.address, args.duration)
            elif args.discover:
                await robust_service_discovery(args.address)
            else:
                await robust_device_reading(args.address)
        else:
            print("No device address provided. Use --scan to discover devices.")
    except KeyboardInterrupt:
        print("Demo interrupted by user")


if __name__ == "__main__":
    asyncio.run(main())
