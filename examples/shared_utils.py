#!/usr/bin/env python3
"""Shared utilities for bluetooth-sig examples."""

from __future__ import annotations

from typing import Any

from bluetooth_sig import BluetoothSIGTranslator

# Import Device class for advertising data parsing
# from bluetooth_sig.device import Device

# Check available BLE libraries
try:
    import importlib.util

    bleak_available = importlib.util.find_spec("bleak") is not None
except ImportError:
    bleak_available = False

try:
    import simplepyble  # type: ignore[import-untyped]  # noqa: F401 # pylint: disable=unused-import

    simplepyble_available = True
except ImportError:
    simplepyble_available = False


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


async def scan_devices(timeout: float = 10.0) -> list[Any]:
    """Scan for BLE devices using available library."""
    if not bleak_available:
        print("Bleak not available for scanning")
        return []

    from bleak import BleakScanner  # type: ignore[import-untyped]

    print(f"Scanning for BLE devices ({timeout}s)...")
    devices = await BleakScanner.discover(timeout=timeout)

    print(f"Found {len(devices)} devices:")
    for i, device in enumerate(devices, 1):
        name = getattr(device, "name", None) or "Unknown"
        address = getattr(device, "address", "Unknown")
        rssi = getattr(device, "rssi", None)
        if rssi is not None:
            print(f"  {i}. {name} ({address}) - RSSI: {rssi}dBm")
        else:
            print(f"  {i}. {name} ({address})")

    return devices


async def read_characteristics(  # pylint: disable=too-many-locals
    address: str, target_uuids: list[str] | None = None, timeout: float = 10.0
) -> dict[str, tuple[bytes, float]]:
    """Read characteristics from a BLE device."""
    if not bleak_available:
        return {}

    from bleak import BleakClient  # type: ignore[import-untyped]

    results: dict[str, tuple[bytes, float]] = {}
    print("Reading characteristics...")

    try:
        async with BleakClient(address, timeout=timeout) as client:
            # Discover services
            services = client.services
            print(f"Discovered {len(services.services)} services")

            # If no target UUIDs specified, discover all readable characteristics
            if target_uuids is None:
                target_uuids = []
                for service in services:
                    for char in service.characteristics:
                        if "read" in char.properties:
                            target_uuids.append(str(char.uuid))
                print(f"Found {len(target_uuids)} readable characteristics")
            else:
                # Convert short UUIDs to full format
                expanded_uuids: list[str] = []
                for uuid in target_uuids:
                    if len(uuid) == 4:  # Short UUID
                        expanded_uuids.append(f"0000{uuid}-0000-1000-8000-00805F9B34FB")
                    else:
                        expanded_uuids.append(uuid)
                target_uuids = expanded_uuids

            for uuid in target_uuids:
                try:
                    import time  # pylint: disable=import-outside-toplevel

                    read_start = time.time()
                    raw_data = await client.read_gatt_char(uuid)
                    read_time = time.time() - read_start

                    # Convert bytearray to bytes
                    raw_data_bytes: bytes = bytes(raw_data)

                    # Use short UUID as key
                    uuid_key = uuid[4:8].upper() if len(uuid) > 8 else uuid.upper()
                    results[uuid_key] = (raw_data_bytes, read_time)
                    print(f"  {uuid_key}: {len(raw_data)} bytes")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    uuid_key = uuid[4:8].upper() if len(uuid) > 8 else uuid.upper()
                    print(f"  {uuid_key}: {e}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Connection failed: {e}")

    return results


def parse_results(raw_results: dict[str, tuple[bytes, float]]) -> dict[str, Any]:
    """Parse raw BLE data using bluetooth_sig."""
    translator = BluetoothSIGTranslator()
    parsed_results: dict[str, Any] = {}

    print("Parsing results with SIG library:")

    for uuid_short, (raw_data, read_time) in raw_results.items():
        try:
            result = translator.parse_characteristic(uuid_short, raw_data)

            if result.parse_success:
                unit_str = f" {result.unit}" if result.unit else ""
                print(f"  {result.name}: {result.value}{unit_str}")
                parsed_results[uuid_short] = {
                    "name": result.name,
                    "value": result.value,
                    "unit": result.unit,
                    "read_time": read_time,
                    "raw_data": raw_data,
                }
            else:
                print(f"  {uuid_short}: Parse failed - {result.error_message}")
                parsed_results[uuid_short] = {
                    "error": result.error_message,
                    "raw_data": raw_data,
                }
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"  {uuid_short}: Exception - {e}")
            parsed_results[uuid_short] = {
                "error": str(e),
                "raw_data": raw_data,
            }

    return parsed_results


def mock_ble_data() -> dict[str, bytes]:
    """Generate mock BLE data for testing."""
    return {
        "2A19": b"\x64",  # Battery Level: 100%
        "2A29": b"HelloWorld Inc.",  # Manufacturer Name
        "2A24": b"TestModel",  # Model Number
        "2A25": b"123456789",  # Serial Number
        "2A6E": b"\x0a\x00",  # Temperature: 10.00°C
        "2A6F": b"\x64\x00",  # Humidity: 100.00%
    }


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

    print(f"\nSuccessfully parsed {len(parsed_results)} characteristics")


async def demo_service_discovery(address: str) -> None:
    """Demonstrate service discovery using Device class."""
    print(f"Discovering services on device: {address}")

    # translator = BluetoothSIGTranslator()  # Would need connection manager

    # This would require a connection manager in a real implementation
    # For demo purposes, we'll show the API
    print("Device class methods available:")
    print("- discover_services()")
    print("- read_multiple(uuids)")
    print("- write_multiple(data_dict)")
    print("- get_service_by_uuid(uuid)")
    print("- list_characteristics()")
    print("- is_connected property")
