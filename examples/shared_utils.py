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

from typing import Any

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device.connection import ConnectionManagerProtocol

"""Shared utilities for bluetooth-sig examples."""

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


async def read_characteristics_with_manager(
    connection_manager: ConnectionManagerProtocol,
    target_uuids: list[str] | None = None,
    timeout: float = 10.0,
) -> dict[str, tuple[bytes, float]]:
    """Read characteristics from a BLE device using a connection manager."""
    results: dict[str, tuple[bytes, float]] = {}
    print("Reading characteristics with connection manager...")

    try:
        await connection_manager.connect()
        print("✅ Connected, reading characteristics...")

        # If no target UUIDs specified, we need to discover services first
        if target_uuids is None:
            services = await connection_manager.get_services()
            target_uuids = []
            # This depends on the structure returned by get_services()
            # For now, let's assume it returns an iterable with characteristics
            for service in services:
                if hasattr(service, "characteristics"):
                    for char in service.characteristics:
                        if hasattr(char, "properties") and "read" in char.properties:
                            target_uuids.append(str(char.uuid))
            print(f"Found {len(target_uuids)} readable characteristics")
        else:
            # Convert short UUIDs to full format if needed
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
                raw_data = await connection_manager.read_gatt_char(uuid)
                read_time = time.time() - read_start

                # Use short UUID as key
                uuid_key = uuid[4:8].upper() if len(uuid) > 8 else uuid.upper()
                results[uuid_key] = (raw_data, read_time)
                print(f"  {uuid_key}: {len(raw_data)} bytes")
            except Exception as e:  # pylint: disable=broad-exception-caught
                uuid_key = uuid[4:8].upper() if len(uuid) > 8 else uuid.upper()
                print(f"  {uuid_key}: {e}")

        await connection_manager.disconnect()
        print("✅ Disconnected")

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


async def demo_basic_usage(address: str, connection_manager: ConnectionManagerProtocol) -> None:
    """Demonstrate basic usage of the bluetooth_sig library."""
    print(f"Connecting to device: {address}")

    from bluetooth_sig import BluetoothSIGTranslator
    from bluetooth_sig.device.device import Device

    translator = BluetoothSIGTranslator()
    device = Device(address, translator)
    device.connection_manager = connection_manager

    try:
        print("🔗 Connecting to device...")
        await connection_manager.connect()
        print("✅ Connected, reading characteristics...")

        # Read some common characteristics
        common_uuids = ["2A00", "2A19", "2A29", "2A24", "2A25", "2A26", "2A27", "2A28"]
        parsed_results: dict[str, Any] = {}

        for uuid_short in common_uuids:
            try:
                result = await device.read(uuid_short)
                if result and getattr(result, "parse_success", False):
                    parsed_results[uuid_short] = result
                    unit_str = f" {result.unit}" if getattr(result, "unit", None) else ""
                    print(f"  ✅ {getattr(result, 'name', uuid_short)}: {getattr(result, 'value', 'N/A')}{unit_str}")
                else:
                    print(f"  • {uuid_short}: Read failed or parse failed")
            except Exception as e:
                print(f"  ❌ {uuid_short}: Error - {e}")

        await connection_manager.disconnect()
        print("✅ Disconnected")

        print(f"\n📊 Successfully parsed {len(parsed_results)} characteristics")

    except Exception as e:
        print(f"❌ Basic usage demo failed: {e}")
        print("This may be due to device being unavailable or connection issues.")


async def demo_service_discovery(address: str, connection_manager: ConnectionManagerProtocol) -> None:
    """Demonstrate service discovery using Device class."""
    print(f"Discovering services on device: {address}")

    from bluetooth_sig import BluetoothSIGTranslator
    from bluetooth_sig.device.device import Device

    translator = BluetoothSIGTranslator()
    device = Device(address, translator)
    device.connection_manager = connection_manager

    try:
        print("🔍 Discovering services...")
        print("   Connecting to device...")
        await connection_manager.connect()
        print("   ✅ Connected, discovering services...")
        services = await device.discover_services()

        print(f"✅ Found {len(services)} services:")
        total_chars = 0
        parsed_chars = 0

        for service_uuid, service_info in services.items():
            service_name = translator.get_service_info(service_uuid)
            if service_name:
                print(f"  📋 {service_uuid}: {service_name.name}")
            else:
                print(f"  📋 {service_uuid}: Unknown service")

            # Show characteristics for this service
            characteristics = service_info.characteristics
            if characteristics:
                print(f"     └─ {len(characteristics)} characteristics:")
                for char_uuid, _char_info in characteristics.items():
                    total_chars += 1
                    # Try to read and parse the characteristic
                    try:
                        # Convert full UUID to short form for reading
                        short_uuid = char_uuid[4:8].upper() if len(char_uuid) > 8 else char_uuid.upper()
                        parsed = await device.read(short_uuid)

                        if parsed and getattr(parsed, "parse_success", False):
                            parsed_chars += 1
                            char_name = getattr(parsed, "name", short_uuid)
                            value = getattr(parsed, "value", "N/A")
                            unit = getattr(parsed, "unit", "")
                            print(f"        ✅ {short_uuid}: {char_name} = {value} {unit}")
                        else:
                            # Try to get name from translator
                            char_info_obj = translator.get_characteristic_info(short_uuid)
                            if char_info_obj:
                                print(f"        • {short_uuid}: {char_info_obj.name} (read failed)")
                            else:
                                print(f"        • {short_uuid}: Unknown characteristic")
                    except Exception as e:
                        # Try to get name from translator
                        short_uuid = char_uuid[4:8].upper() if len(char_uuid) > 8 else char_uuid.upper()
                        char_info_obj = translator.get_characteristic_info(short_uuid)
                        if char_info_obj:
                            print(f"        ❌ {short_uuid}: {char_info_obj.name} (error: {e})")
                        else:
                            print(f"        ❌ {short_uuid}: Unknown characteristic (error: {e})")

        await connection_manager.disconnect()
        print("   ✅ Disconnected")

        print(f"\n📊 Device summary: {device}")
        print(f"📊 Total characteristics: {total_chars}, Successfully parsed: {parsed_chars}")

    except Exception as e:
        print(f"❌ Service discovery failed: {e}")
        print("This may be due to device being unavailable or connection issues.")
