#!/usr/bin/env python3
"""Bleak-retry-connector integration example - robust BLE connections with SIG parsing.

This example demonstrates using bleak-retry-connector for reliable BLE connections
combined with bluetooth_sig for standards-compliant data parsing. This is the
recommended pattern for production applications.

Benefits:
- Automatic retry logic for unreliable BLE connections
- Connection recovery and error handling
- Pure SIG standards parsing
- Production-ready robustness

Requirements:
    pip install bleak-retry-connector bleak

Usage:
    python with_bleak_retry.py --address 12:34:56:78:9A:BC
    python with_bleak_retry.py --scan
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import shared BLE utilities
from ble_utils import (
    BLEAK_AVAILABLE,
    discover_services_and_characteristics_bleak,
    get_default_characteristic_uuids,
    handle_notifications_bleak,
    parse_and_display_results,
    read_characteristics_bleak_retry,
    scan_with_bleak,
)

from bluetooth_sig import BluetoothSIGTranslator

# Note: bleak_retry_connector has compatibility issues on this system
# Using Bleak with manual retry logic instead


async def robust_device_reading(address: str, retries: int = 3) -> dict:
    """Robust device reading with automatic retry and error recovery.

    Args:
        address: BLE device address
        retries: Number of connection retry attempts

    Returns:
        Dictionary of parsed characteristic data
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available")
        return {}

    # Use shared utilities for robust reading
    target_uuids = get_default_characteristic_uuids()
    raw_results = await read_characteristics_bleak_retry(
        address, target_uuids, max_attempts=retries
    )

    # Parse and display results
    return await parse_and_display_results(raw_results, "Bleak-Retry")


async def robust_service_discovery(address: str) -> dict:
    """Discover all services and characteristics with robust connection.

    Args:
        address: BLE device address

    Returns:
        Dictionary of discovered services and characteristics
    """
    return await discover_services_and_characteristics_bleak(address)


async def perform_single_reading(
    address: str, translator: BluetoothSIGTranslator, target_uuids: list[str]
) -> bool:
    """Perform a single reading cycle and return success status."""
    try:
        # Use robust connection with retry
        raw_results = await read_characteristics_bleak_retry(
            address, target_uuids, max_attempts=3
        )

        if raw_results:
            print(f"📊 Reading at {time.strftime('%H:%M:%S')}:")

            for uuid_short, (raw_data, _) in raw_results.items():
                result = translator.parse_characteristic(uuid_short, raw_data)
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
    await handle_notifications_bleak(address, duration)


async def main():
    """Main function demonstrating robust BLE patterns."""
    parser = argparse.ArgumentParser(
        description="Robust BLE with bleak-retry-connector + SIG parsing"
    )
    parser.add_argument("--address", "-a", help="BLE device address")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument(
        "--monitor", "-m", action="store_true", help="Continuous monitoring"
    )
    parser.add_argument(
        "--notifications", "-n", action="store_true", help="Monitor notifications"
    )
    parser.add_argument(
        "--discover", "-d", action="store_true", help="Service discovery"
    )
    parser.add_argument(
        "--duration", "-t", type=int, default=60, help="Duration for monitoring"
    )

    args = parser.parse_args()

    if not BLEAK_AVAILABLE:
        print("Bleak not available. Install with: pip install bleak")
        return

    try:
        if args.scan:
            await scan_with_bleak()
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
