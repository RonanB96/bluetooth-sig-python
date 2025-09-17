#!/usr/bin/env python3
"""Shared utilities for bluetooth-sig examples."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device

# Check available BLE libraries
try:
    from bleak import BleakClient, BleakScanner

    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

SIMPLEPYBLE_AVAILABLE = importlib.util.find_spec("simplepyble") is not None


def setup_library_check() -> dict[str, bool]:
    """Check which BLE libraries are available."""
    return {
        "bleak": BLEAK_AVAILABLE,
        "simplepyble": SIMPLEPYBLE_AVAILABLE,
    }


def create_device(address: str) -> Device:
    """Create a configured Device instance."""
    translator = BluetoothSIGTranslator()
    return Device(address, translator)


def short_uuid(uuid: str) -> str:
    """Normalize a UUID to a short 16-bit uppercase string."""
    if not uuid:
        return ""
    u = str(uuid).replace("-", "").lower()
    if len(u) == 32:
        return u[4:8].upper()
    if len(u) >= 4:
        return u[-4:].upper()
    return u.upper()


async def scan_devices(timeout: float = 10.0) -> list:
    """Scan for BLE devices using available library."""
    if not BLEAK_AVAILABLE:
        print("Bleak not available for scanning")
        return []

    print(f"Scanning for BLE devices ({timeout}s)...")
    scanner = BleakScanner()
    devices = await scanner.discover(timeout=timeout)
    return devices


async def read_characteristics(
    address: str, uuids: list[str] = None
) -> dict[str, bytes]:
    """Read characteristics from a BLE device."""
    if not BLEAK_AVAILABLE:
        print("Bleak not available")
        return {}

    results = {}
    try:
        async with BleakClient(address) as client:
            if not uuids:
                # Get all readable characteristics
                for service in client.services:
                    for char in service.characteristics:
                        if "read" in char.properties:
                            uuids = uuids or []
                            uuids.append(char.uuid)

            for uuid in uuids or []:
                try:
                    data = await client.read_gatt_char(uuid)
                    results[uuid] = data
                except (OSError, ValueError) as e:
                    print(f"Failed to read {uuid}: {e}")
    except (OSError, ValueError, ConnectionError) as e:
        print(f"Connection failed: {e}")

    return results


def parse_results(raw_results: dict[str, bytes]) -> dict[str, Any]:
    """Parse raw characteristic data using bluetooth_sig."""
    translator = BluetoothSIGTranslator()
    parsed = {}

    for uuid, data in raw_results.items():
        try:
            result = translator.parse_characteristic(uuid, data)
            parsed[uuid] = result
        except (ValueError, KeyError, OSError) as e:
            print(f"Failed to parse {uuid}: {e}")
            parsed[uuid] = None

    return parsed


async def demo_basic_usage(address: str) -> None:
    """Demonstrate basic usage of the bluetooth_sig library."""
    print(f"Connecting to device: {address}")

    # Read characteristics
    raw_results = await read_characteristics(address)

    if not raw_results:
        print("No data read from device")
        return

    # Parse results
    parsed_results = parse_results(raw_results)

    print(f"Successfully parsed {len(parsed_results)} characteristics")
    for uuid, result in parsed_results.items():
        if result is not None:
            print(f"  {short_uuid(uuid)}: {result}")


async def demo_service_discovery(address: str) -> None:
    """Demonstrate service discovery using Device class."""
    print(f"Discovering services on device: {address}")

    print("Device class methods available:")
    print("- discover_services()")
    print("- read_multiple(uuids)")
    print("- write_multiple(data_dict)")
    print("- get_service_by_uuid(uuid)")
    print("- list_characteristics()")
    print("- is_connected property")


async def demo_advertising_parsing(raw_data: bytes) -> None:
    """Demonstrate advertising data parsing."""
    device = create_device("00:00:00:00:00:00")  # Dummy address
    device.parse_advertiser_data(raw_data)

    ad_data = device.advertiser_data
    print(f"Device name: {ad_data.local_name}")
    print(f"Service UUIDs: {ad_data.service_uuids}")
    print(f"Manufacturer data: {ad_data.manufacturer_data}")
    print(f"TX Power: {ad_data.tx_power}")


async def demo_notifications(address: str, char_uuid: str) -> None:
    """Demonstrate notification handling."""
    if not BLEAK_AVAILABLE:
        print("Bleak not available")
        return

    def notification_handler(_sender, data):
        """Handle incoming notification."""
        translator = BluetoothSIGTranslator()
        try:
            parsed = translator.parse_characteristic(char_uuid, data)
            print(f"Notification from {short_uuid(char_uuid)}: {parsed}")
        except (ValueError, KeyError, OSError) as e:
            print(f"Failed to parse notification: {e}")

    try:
        async with BleakClient(address) as client:
            await client.start_notify(char_uuid, notification_handler)
            print(f"Listening for notifications on {short_uuid(char_uuid)}...")
            await asyncio.sleep(10)  # Listen for 10 seconds
            await client.stop_notify(char_uuid)
    except (OSError, ValueError, ConnectionError) as e:
        print(f"Notification demo failed: {e}")
