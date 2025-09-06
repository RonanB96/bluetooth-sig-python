#!/usr/bin/env python3
"""Shared BLE utilities for bluetooth-sig examples.

This module provides common BLE connection and scanning functions that work
across different BLE libraries, reducing code duplication in examples.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

# Check available BLE libraries
AVAILABLE_LIBRARIES = {}

# Check for Bleak
try:
    from bleak import BleakClient, BleakScanner

    AVAILABLE_LIBRARIES["bleak"] = {
        "module": "bleak",
        "async": True,
        "description": "Cross-platform async BLE library",
    }
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

# Check for Bleak-retry-connector
try:
    from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

    AVAILABLE_LIBRARIES["bleak-retry"] = {
        "module": "bleak_retry_connector",
        "async": True,
        "description": "Robust BLE connections with retry logic",
    }
    BLEAK_RETRY_AVAILABLE = True
except ImportError:
    BLEAK_RETRY_AVAILABLE = False

# Check for SimplePyBLE (correct package name)
try:
    import importlib.util

    if importlib.util.find_spec("simplepyble"):
        AVAILABLE_LIBRARIES["simplepyble"] = {
            "module": "simplepyble",
            "async": False,
            "description": "Cross-platform BLE library (requires commercial license for commercial use)",
        }
except ImportError:
    pass


def show_library_availability():
    """Display which BLE libraries are available."""
    print("📚 BLE Library Availability Check")
    print("=" * 40)

    if not AVAILABLE_LIBRARIES:
        print("❌ No BLE libraries found. Install one or more:")
        print(
            "   pip install bleak  # Recommended - Cross-platform, actively maintained"
        )
        print("   pip install bleak-retry-connector  # Enhanced Bleak with retry logic")
        print(
            "   pip install simplepyble  # Cross-platform (commercial license for commercial use)"
        )
        return False

    print("✅ Available BLE libraries:")
    for lib_name, info in AVAILABLE_LIBRARIES.items():
        async_str = "Async" if info["async"] else "Sync"
        print(f"   {lib_name}: {info['description']} ({async_str})")

    print(
        f"\n🎯 Will demonstrate bluetooth_sig parsing with {len(AVAILABLE_LIBRARIES)} libraries"
    )
    return True


def safe_get_device_info(device) -> tuple[str, str, str | None]:
    """Safely extract device information from any BLE device object.

    Returns:
        (name, address, rssi) tuple with safe fallbacks
    """
    name = getattr(device, "name", None) or "Unknown"
    address = getattr(device, "address", "Unknown")
    rssi = getattr(device, "rssi", None)
    return name, address, rssi


async def scan_with_bleak(timeout: float = 10.0) -> list:
    """Scan for BLE devices using Bleak.

    Args:
        timeout: Scan timeout in seconds

    Returns:
        List of discovered devices
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for scanning")
        return []

    print(f"🔍 Scanning for BLE devices ({timeout}s)...")
    devices = await BleakScanner.discover(timeout=timeout)

    print(f"\n📡 Found {len(devices)} devices:")
    for i, device in enumerate(devices, 1):
        name, address, rssi = safe_get_device_info(device)
        if rssi is not None:
            print(f"  {i}. {name} ({address}) - RSSI: {rssi}dBm")
        else:
            print(f"  {i}. {name} ({address})")

    return devices


async def read_characteristics_bleak(
    address: str, target_uuids: list[str], timeout: float = 10.0
) -> dict[str, tuple[bytes, float]]:
    """Read characteristics using Bleak library.

    Args:
        address: Device address
        target_uuids: List of characteristic UUIDs to read
        timeout: Connection timeout

    Returns:
        Dict mapping UUID to (raw_data, read_time)
    """
    if not BLEAK_AVAILABLE:
        return {}

    results = {}
    print("📱 Reading with Bleak...")

    try:
        start_time = time.time()
        async with BleakClient(address, timeout=timeout) as client:
            connection_time = time.time() - start_time
            print(f"   ⏱️  Connection time: {connection_time:.2f}s")

            for uuid_short in target_uuids:
                uuid_full = f"0000{uuid_short}-0000-1000-8000-00805F9B34FB"
                try:
                    read_start = time.time()
                    raw_data = await client.read_gatt_char(uuid_full)
                    read_time = time.time() - read_start
                    results[uuid_short] = (raw_data, read_time)
                    print(
                        f"   📖 {uuid_short}: {len(raw_data)} bytes in {read_time:.3f}s"
                    )
                except Exception as e:
                    print(f"   ❌ {uuid_short}: {e}")

    except Exception as e:
        print(f"   ❌ Bleak connection failed: {e}")

    return results


async def read_characteristics_bleak_retry(
    address: str, target_uuids: list[str], timeout: float = 10.0, max_attempts: int = 3
) -> dict[str, tuple[bytes, float]]:
    """Read characteristics using Bleak-retry-connector.

    Args:
        address: Device address
        target_uuids: List of characteristic UUIDs to read
        timeout: Connection timeout
        max_attempts: Maximum retry attempts

    Returns:
        Dict mapping UUID to (raw_data, read_time)
    """
    if not BLEAK_RETRY_AVAILABLE:
        return {}

    results = {}
    print("🔄 Reading with Bleak-Retry-Connector...")

    try:
        start_time = time.time()
        async with establish_connection(
            BleakClientWithServiceCache,
            address,
            timeout=timeout,
            max_attempts=max_attempts,
        ) as client:
            connection_time = time.time() - start_time
            print(f"   ⏱️  Connection time: {connection_time:.2f}s")

            for uuid_short in target_uuids:
                uuid_full = f"0000{uuid_short}-0000-1000-8000-00805F9B34FB"
                try:
                    read_start = time.time()
                    raw_data = await client.read_gatt_char(uuid_full)
                    read_time = time.time() - read_start
                    results[uuid_short] = (raw_data, read_time)
                    print(
                        f"   📖 {uuid_short}: {len(raw_data)} bytes in {read_time:.3f}s"
                    )
                except Exception as e:
                    print(f"   ❌ {uuid_short}: {e}")

    except Exception as e:
        print(f"   ❌ Bleak-retry connection failed: {e}")

    return results


async def parse_and_display_results(
    raw_results: dict[str, tuple[bytes, float]], library_name: str = "BLE Library"
) -> dict[str, Any]:
    """Parse raw BLE data and display results using bluetooth_sig.

    Args:
        raw_results: Dict mapping UUID to (raw_data, read_time)
        library_name: Name of BLE library for display

    Returns:
        Dict of parsed results
    """
    translator = BluetoothSIGTranslator()
    parsed_results = {}

    print(f"\n📊 {library_name} Results with SIG Parsing:")
    print("=" * 50)

    for uuid_short, (raw_data, read_time) in raw_results.items():
        try:
            # Parse with bluetooth_sig (connection-agnostic)
            result = translator.parse_characteristic(uuid_short, raw_data)

            if result.parse_success:
                unit_str = f" {result.unit}" if result.unit else ""
                print(f"   ✅ {result.name}: {result.value}{unit_str}")
                parsed_results[uuid_short] = {
                    "name": result.name,
                    "value": result.value,
                    "unit": result.unit,
                    "read_time": read_time,
                    "raw_data": raw_data,
                }
            else:
                print(f"   ❌ {uuid_short}: Parse failed - {result.error_message}")

        except Exception as e:
            print(f"   💥 {uuid_short}: Exception - {e}")

    return parsed_results


def mock_ble_data() -> dict[str, bytes]:
    """Generate mock BLE data for testing without hardware.

    Returns:
        Dict mapping UUID to mock raw data
    """
    return {
        "2A19": bytes([0x64]),  # 100% battery
        "2A00": b"Mock Device",  # Device name
        "2A6E": bytes([0x64, 0x09]),  # Temperature: 24.04°C
        "2A6F": bytes([0x10, 0x27]),  # Humidity: 100.0%
        "2A6D": bytes([0x40, 0x9C, 0x00, 0x00]),  # Pressure: 40.0 kPa
        "2A29": b"Bluetooth SIG",  # Manufacturer name
    }


async def demo_library_comparison(address: str, target_uuids: list[str]) -> dict:
    """Compare BLE libraries using the same SIG parsing.

    Args:
        address: Device address
        target_uuids: UUIDs to read

    Returns:
        Dict of results from each library
    """
    comparison_results = {}

    print("🔍 Comparing BLE Libraries with Identical SIG Parsing")
    print("=" * 55)

    # Test Bleak
    if BLEAK_AVAILABLE:
        bleak_results = await read_characteristics_bleak(address, target_uuids)
        comparison_results["bleak"] = await parse_and_display_results(
            bleak_results, "Bleak"
        )

    # Test Bleak-retry
    if BLEAK_RETRY_AVAILABLE:
        retry_results = await read_characteristics_bleak_retry(address, target_uuids)
        comparison_results["bleak-retry"] = await parse_and_display_results(
            retry_results, "Bleak-Retry"
        )

    return comparison_results


def get_default_characteristic_uuids() -> list[str]:
    """Get a default set of commonly available characteristics for testing."""
    return [
        "2A19",  # Battery Level
        "2A00",  # Device Name
        "2A6E",  # Temperature
        "2A6F",  # Humidity
        "2A6D",  # Pressure
        "2A29",  # Manufacturer Name
    ]


# Educational demonstration showing framework-agnostic design
def demo_framework_agnostic_concept():
    """Demonstrate the framework-agnostic design concept with educational examples."""
    print("\n🎭 Framework-Agnostic Design Demonstration")
    print("=" * 55)

    print("The key insight: bluetooth_sig provides pure SIG standards parsing")
    print("that works identically regardless of your BLE connection library choice.\n")

    # Show the pattern with pseudo-code examples
    print("📋 Integration Pattern Examples:")
    print("=" * 35)

    examples = [
        {
            "library": "Bleak (Async)",
            "connection": "async with BleakClient(address) as client:",
            "read": "    raw_data = await client.read_gatt_char(uuid)",
        },
        {
            "library": "SimplePyBLE (Sync)",
            "connection": "peripheral.connect()",
            "read": "    raw_data = bytes(characteristic.read())",
        },
        {
            "library": "Custom Library",
            "connection": "device = my_ble_lib.connect(address)",
            "read": "    raw_data = device.read_characteristic(uuid)",
        },
    ]

    for example in examples:
        print(f"\n💻 {example['library']}:")
        print(f"   {example['connection']}")
        print(f"   {example['read']}")
        print("    # ✨ Same SIG parsing for all libraries:")
        print("    result = translator.parse_characteristic(uuid, raw_data)")
        print("    print(f'{result.value} {result.unit}')")

    print("\n🎯 Key Benefits:")
    print("   • Choose ANY BLE library based on your platform/needs")
    print("   • Easy migration between BLE libraries")
    print("   • Standards-compliant parsing guaranteed")
    print("   • Test without hardware using mock data")

    # Show mock data for testing
    mock_data = mock_ble_data()
    translator = BluetoothSIGTranslator()

    print(f"\n📊 Example: Mock Battery Reading (0x{mock_data['2A19'].hex()})")
    result = translator.parse_characteristic("2A19", mock_data["2A19"])
    print(f"   All libraries would parse this as: {result.value}{result.unit}")
    print("   Because bluetooth_sig uses official SIG specification for 2A19")

    print("\n✅ This design lets you focus on:")
    print("   📡 Connection management (choose your preferred BLE library)")
    print("   📊 Data interpretation (handled by bluetooth_sig standards)")
    print("   🔧 Application logic (not BLE parsing complexity)")
