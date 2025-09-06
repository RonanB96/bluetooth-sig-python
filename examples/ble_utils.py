#!/usr/bin/env python3
"""Shared BLE utilities for bluetooth-sig examples.

This module provides common BLE connection and scanning functions that work
across different BLE libraries, reducing code duplication in examples.
"""  # pylint: disable=too-many-lines

from __future__ import annotations

import asyncio
import importlib.util
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
if importlib.util.find_spec("bleak_retry_connector") is not None:
    AVAILABLE_LIBRARIES["bleak-retry"] = {
        "module": "bleak_retry_connector",
        "async": True,
        "description": "Robust BLE connections with retry logic",
    }
    BLEAK_RETRY_AVAILABLE = True
else:
    BLEAK_RETRY_AVAILABLE = False

# Check for SimplePyBLE (correct package name)
SIMPLEPYBLE_AVAILABLE = False
SIMPLEPYBLE_MODULE = None
if importlib.util.find_spec("simplepyble") is not None:
    try:
        # Import at module scope using importlib to avoid unused-import pylint warnings
        SIMPLEPYBLE_MODULE = importlib.import_module("simplepyble")  # type: ignore
    except Exception:  # pylint: disable=broad-exception-caught
        SIMPLEPYBLE_MODULE = None
        SIMPLEPYBLE_AVAILABLE = False
    else:
        SIMPLEPYBLE_AVAILABLE = True
        AVAILABLE_LIBRARIES["simplepyble"] = {
            "module": "simplepyble",
            "async": False,
            "description": "Cross-platform BLE library (requires commercial license for commercial use)",
        }


def short_uuid(uuid: str) -> str:
    """Normalize a UUID (full or short) to a short 16-bit uppercase string.

    Examples:
      '00002a19-0000-1000-8000-00805f9b34fb' -> '2A19'
      '2a19' -> '2A19'
    """
    if not uuid:
        return ""
    u = str(uuid).replace("-", "").lower()
    if len(u) == 32:
        return u[4:8].upper()
    if len(u) >= 4:
        return u[-4:].upper()
    return u.upper()


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


async def read_characteristics_bleak(  # pylint: disable=too-many-locals,import-outside-toplevel
    address: str, target_uuids: list[str] = None, timeout: float = 10.0
) -> dict[str, tuple[bytes, float]]:
    """Read characteristics from a BLE device using Bleak.

    Args:
        address: Device address
        target_uuids: List of characteristic UUIDs to read, or None to discover and read all
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

            # Add connection delay for device stability
            await asyncio.sleep(0.5)

            # Discover services to ensure proper connection
            services = await client.get_services()
            print(f"   🔍 Discovered {len(services.services)} services")

            # If no target UUIDs specified, discover all readable characteristics
            if target_uuids is None:
                print("   🔍 Discovering all readable characteristics...")
                target_uuids = []
                for service in services:
                    for char in service.characteristics:
                        if "read" in char.properties:
                            target_uuids.append(str(char.uuid))
                print(f"   📋 Found {len(target_uuids)} readable characteristics")
            else:
                # Convert short UUIDs to full format for existing examples
                expanded_uuids = []
                for uuid in target_uuids:
                    if len(uuid) == 4:  # Short UUID
                        expanded_uuids.append(f"0000{uuid}-0000-1000-8000-00805F9B34FB")
                    else:
                        expanded_uuids.append(uuid)
                target_uuids = expanded_uuids

            for uuid in target_uuids:
                try:
                    read_start = time.time()
                    raw_data = await client.read_gatt_char(uuid)
                    read_time = time.time() - read_start

                    # Use short UUID as key for compatibility
                    uuid_key = uuid[4:8].upper() if len(uuid) > 8 else uuid.upper()
                    results[uuid_key] = (raw_data, read_time)
                    print(
                        f"   📖 {uuid_key}: {len(raw_data)} bytes in {read_time:.3f}s"
                    )
                except Exception as e:  # pylint: disable=broad-exception-caught
                    uuid_key = uuid[4:8].upper() if len(uuid) > 8 else uuid.upper()
                    print(f"   ❌ {uuid_key}: {e}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"   ❌ Bleak connection failed: {e}")

    return results


async def read_characteristics_bleak_retry(
    address: str, target_uuids: list[str], timeout: float = 10.0, max_attempts: int = 3
) -> dict[str, tuple[bytes, float]]:
    """Read characteristics using Bleak with manual retry logic.

    Args:
        address: Device address
        target_uuids: List of characteristic UUIDs to read
        timeout: Connection timeout
        max_attempts: Maximum retry attempts

    Returns:
        Dict mapping UUID to (raw_data, read_time)
    """
    if not BLEAK_AVAILABLE:
        return {}

    results = {}
    print("🔄 Reading with Bleak (with retry logic)...")

    for attempt in range(max_attempts):
        try:
            start_time = time.time()
            async with BleakClient(address, timeout=timeout) as client:
                connection_time = time.time() - start_time
                print(
                    f"   ⏱️  Connection time: {connection_time:.2f}s (attempt {attempt + 1})"
                )

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
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        print(f"   ❌ {uuid_short}: {e}")

                # If we got here, connection was successful
                break

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"   ❌ Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                print("   🔄 Retrying in 2 seconds...")
                await asyncio.sleep(2)
            else:
                print(f"   ❌ All {max_attempts} attempts failed")

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

        except Exception as e:  # pylint: disable=broad-exception-caught
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


async def demo_library_comparison(address: str, target_uuids: list[str] = None) -> dict:  # pylint: disable=R0912,W0718
    """Compare BLE libraries using comprehensive device analysis.

    NOTE: This function orchestrates multiple external libraries and wraps
    library calls in broad exception handlers to keep the demo resilient to
    environment-specific failures (HCI adapter, missing libs). The branching
    is intentionally high because the function serialises multiple library
    flows for comparison.
    """
    # Args:
    #     address: Device address
    #     target_uuids: UUIDs to read, or None for comprehensive analysis
    #
    # Returns:
    #     Dict of results from each library
    comparison_results = {}

    print("🔍 Comparing BLE Libraries with Comprehensive Device Analysis")
    print("=" * 60)

    # Helper: ensure Bleak can see device by doing an explicit scan first
    async def _ensure_bleak_sees_device(addr: str, attempts: int = 2) -> bool:
        for attempt in range(1, attempts + 1):
            print(
                f"🔎 Bleak scan attempt {attempt}/{attempts} (timeout={5 * attempt}s)"
            )
            devices = await scan_with_bleak(timeout=5 * attempt)
            for dev in devices:
                name, a, _rssi = safe_get_device_info(dev)
                if str(a).upper() == addr.upper():
                    print(
                        f"✅ Bleak discovered device {addr} ({name}) on attempt {attempt}"
                    )
                    return True
            # short backoff
            if attempt < attempts:
                await asyncio.sleep(1)
        print(f"❌ Bleak did not discover device {addr} after {attempts} attempts")
        return False

    # Test Bleak with comprehensive analysis (perform a pre-scan to improve reliability)
    if BLEAK_AVAILABLE:
        try:
            if target_uuids is None:
                seen = await _ensure_bleak_sees_device(address, attempts=2)
                if not seen:
                    print(
                        "⚠️  Proceeding with Bleak comprehensive analysis despite missing scan result"
                    )
                bleak_results = await comprehensive_device_analysis_bleak(address)
                comparison_results["bleak"] = bleak_results
            else:
                # Use targeted reading for specific UUIDs
                bleak_results = await read_characteristics_bleak(address, target_uuids)
                comparison_results["bleak"] = await parse_and_display_results(
                    bleak_results, "Bleak"
                )
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"❌ Bleak comprehensive analysis failed: {e}")

    # Small delay to avoid HCI adapter contention between different libraries
    await asyncio.sleep(1)

    # Test Bleak-retry with comprehensive approach
    if BLEAK_RETRY_AVAILABLE:
        try:
            if target_uuids is None:
                print("\n📋 Bleak-Retry: Using comprehensive analysis approach...")
                retry_results = await read_characteristics_bleak_retry(address, [])
                comparison_results["bleak-retry"] = await parse_and_display_results(
                    retry_results, "Bleak-Retry"
                )
            else:
                retry_results = await read_characteristics_bleak_retry(
                    address, target_uuids
                )
                comparison_results["bleak-retry"] = await parse_and_display_results(
                    retry_results, "Bleak-Retry"
                )
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"❌ Bleak-retry analysis failed: {e}")

    # Small delay before running synchronous SimplePyBLE to avoid adapter conflicts
    await asyncio.sleep(1)

    # Test SimplePyBLE (synchronous) by running its comprehensive analyzer in a thread
    if SIMPLEPYBLE_AVAILABLE:
        try:
            print(
                "\n🔁 Running SimplePyBLE comprehensive analysis in background thread..."
            )
            if SIMPLEPYBLE_MODULE is None:
                print("❌ SimplePyBLE module missing at runtime")
            else:
                simple_results = await asyncio.to_thread(
                    comprehensive_device_analysis_simpleble,
                    address,
                    SIMPLEPYBLE_MODULE,
                )
                comparison_results["simplepyble"] = simple_results
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"❌ SimplePyBLE analysis failed: {e}")

    return comparison_results


def get_default_characteristic_uuids() -> list[str]:
    """Get a default set of commonly available characteristics for testing.

    DEPRECATED: Use comprehensive_device_analysis() instead for real device discovery.
    This function only returns predefined UUIDs and misses actual device capabilities.
    """
    return [
        "2A19",  # Battery Level
        "2A00",  # Device Name
        "2A6E",  # Temperature
        "2A6F",  # Humidity
        "2A6D",  # Pressure
        "2A29",  # Manufacturer Name
    ]


async def comprehensive_device_analysis_bleak(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements,too-many-nested-blocks,import-outside-toplevel,protected-access
    address: str, timeout: float = 10.0
) -> dict:
    """Comprehensively analyze a BLE device using Bleak - discovers and tests ALL characteristics.

    This is the superior approach that discovers actual device capabilities rather than
    testing predefined characteristics. Based on test_real_device.py logic.

    Args:
        address: BLE device address
        timeout: Connection timeout

    Returns:
        Dict containing:
        - 'services': List of discovered services with characteristics
        - 'raw_data': Dict mapping UUID to raw bytes
        - 'parsed_data': Dict mapping UUID to parsed results
        - 'analysis': Comprehensive analysis results
        - 'stats': Connection and parsing statistics
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for comprehensive analysis")
        return {}

    translator = BluetoothSIGTranslator()
    results = {
        "services": [],
        "raw_data": {},
        "parsed_data": {},
        "analysis": {},
        "stats": {
            "connection_time": 0,
            "services_discovered": 0,
            "characteristics_found": 0,
            "characteristics_read": 0,
            "characteristics_parsed": 0,
            "characteristics_validated": 0,
        },
    }

    print("📱 Comprehensive Device Analysis with Bleak...")

    try:
        start_time = time.time()
        async with BleakClient(address, timeout=timeout) as client:
            results["stats"]["connection_time"] = time.time() - start_time
            print(
                f"✅ Connected to {address} ({results['stats']['connection_time']:.2f}s)"
            )

            # Allow device to settle after connection
            await asyncio.sleep(0.5)

            # Get device information
            device_name = client.address
            try:
                device_name = getattr(client._device, "name", None) or client.address
            except Exception:  # pylint: disable=broad-exception-caught
                device_name = client.address
            print(f"📱 Device: {device_name}")

            # Discover services
            print("🔍 Discovering services...")
            services = client.services

            if not services:
                print("⚠️ No services discovered")
                return results

            results["stats"]["services_discovered"] = len(list(services))
            print(f"📋 Found {len(list(services))} services:")

            # Analyze each service and characteristic
            for service in services:
                service_info = translator.get_service_info(service.uuid)
                service_name = service_info.name if service_info else "Unknown Service"
                service_data = {
                    "uuid": str(service.uuid),
                    "name": service_name,
                    "characteristics": [],
                }

                print(f"\n🔧 Service: {service_name} ({service.uuid})")

                chars = service.characteristics
                results["stats"]["characteristics_found"] += len(chars)
                print(f"   └─ {len(chars)} characteristics:")

                for characteristic in chars:
                    char_data = {
                        "uuid": str(characteristic.uuid),
                        "properties": list(characteristic.properties),
                        "descriptors": [
                            str(d.uuid) for d in characteristic.descriptors
                        ],
                    }

                    props = ", ".join(characteristic.properties)
                    print(f"      └─ {characteristic.uuid} - [{props}]")
                    for descriptor in characteristic.descriptors:
                        print(f"         └─ Descriptor: {descriptor.uuid}")

                    service_data["characteristics"].append(char_data)

                results["services"].append(service_data)

            # Read all readable characteristics
            print("\n🔍 Reading all readable characteristics...")
            chars_read = 0

            for service in services:
                for characteristic in service.characteristics:
                    if "read" in characteristic.properties:
                        try:
                            data = await client.read_gatt_char(characteristic.uuid)
                            sid = short_uuid(str(characteristic.uuid))
                            results["raw_data"][sid] = data
                            chars_read += 1

                            if len(data) == 0:
                                print(
                                    f"  ⚠️  {characteristic.uuid}: Empty data (0 bytes)"
                                )
                            else:
                                try:
                                    str_val = data.decode("utf-8").strip("\x00")
                                    is_printable = str_val and all(
                                        c.isprintable() or c.isspace() for c in str_val
                                    )
                                    if is_printable and len(str_val) > 0:
                                        print(
                                            f"  ✅ {characteristic.uuid}: '{str_val}' ({len(data)} bytes)"
                                        )
                                    else:
                                        hex_val = " ".join(f"{b:02x}" for b in data)
                                        print(
                                            f"  ✅ {characteristic.uuid}: {hex_val} ({len(data)} bytes)"
                                        )
                                except UnicodeDecodeError:
                                    hex_val = " ".join(f"{b:02x}" for b in data)
                                    print(
                                        f"  ✅ {characteristic.uuid}: {hex_val} ({len(data)} bytes)"
                                    )
                        except Exception as e:  # pylint: disable=broad-exception-caught
                            print(f"  ❌ Error reading {characteristic.uuid}: {e}")

            results["stats"]["characteristics_read"] = chars_read

            # Parse with bluetooth_sig framework
            print(
                f"\n🏗️  Testing bluetooth_sig framework integration... (read {chars_read} characteristics)"
            )
            parsed_count = 0

            for char_uuid, data in list(results["raw_data"].items()):
                try:
                    # Parse the data using bluetooth_sig
                    parsed_data = translator.parse_characteristic(char_uuid, data)

                    if parsed_data.value is not None:
                        unit_str = f" {parsed_data.unit}" if parsed_data.unit else ""
                        char_info = translator.get_characteristic_info(char_uuid)
                        name = char_info.name if char_info else char_uuid
                        print(f"  ✅ {name}: {parsed_data.value}{unit_str}")
                        results["parsed_data"][char_uuid] = {
                            "name": name,
                            "value": parsed_data.value,
                            "unit": parsed_data.unit,
                            "parse_success": parsed_data.parse_success,
                            "error_message": parsed_data.error_message,
                        }
                        parsed_count += 1
                except Exception:  # pylint: disable=broad-exception-caught
                    # Silently skip unparseable characteristics
                    pass

            results["stats"]["characteristics_parsed"] = parsed_count

            if parsed_count > 0:
                print(
                    f"\n✅ Successfully parsed {parsed_count} characteristics using framework"
                )
            else:
                print(
                    "\nℹ️  No characteristics were parsed (may need raw data re-reading)"
                )

            # Enhanced SIG translator analysis
            print("\n🔍 Enhanced SIG Analysis...")

            if results["raw_data"]:
                discovered_uuids = list(results["raw_data"].keys())
                print(
                    f"📊 Analyzing {len(discovered_uuids)} discovered characteristics:"
                )

                # Batch analysis
                char_info = translator.get_characteristics_info(discovered_uuids)
                analysis_results = {}
                for uuid, info in char_info.items():
                    if info:
                        name = getattr(info, "name", "Unknown")
                        data_type = getattr(info, "value_type", "unknown")
                        print(f"  📋 {uuid}: {name} [{data_type}]")
                        analysis_results[uuid] = {
                            "name": name,
                            "data_type": data_type,
                            "recognized": True,
                        }
                    else:
                        print(f"  ❓ {uuid}: Unknown characteristic")
                        analysis_results[uuid] = {
                            "name": "Unknown",
                            "data_type": "unknown",
                            "recognized": False,
                        }

                results["analysis"]["characteristics"] = analysis_results

                # Validation analysis
                print("\n🔍 Data validation:")
                valid_count = 0
                validation_results = {}
                for uuid, data in results["raw_data"].items():
                    if isinstance(data, (bytes, bytearray)):
                        is_valid = translator.validate_characteristic_data(uuid, data)
                        status = "✅" if is_valid else "⚠️"
                        validity = "Valid" if is_valid else "Unknown format"
                        print(f"  {status} {uuid}: {validity}")
                        validation_results[uuid] = {
                            "valid": is_valid,
                            "status": validity,
                        }
                        if is_valid:
                            valid_count += 1

                results["analysis"]["validation"] = validation_results
                results["stats"]["characteristics_validated"] = valid_count

                print(
                    f"\n📈 Validation: {valid_count}/{len(results['raw_data'])} characteristics have known format"
                )

            print("\n✅ Comprehensive analysis completed successfully")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Comprehensive analysis failed: {e}")
        results["error"] = str(e)

    return results


def comprehensive_device_analysis_simpleble(address: str, simpleble_module) -> dict:
    """Comprehensively analyze a BLE device using SimpleBLE - discovers and tests ALL characteristics.

    This is the reusable version of the comprehensive analysis logic that can be
    used by SimpleBLE-based examples.

    Args:
        address: BLE device address
        simpleble_module: The imported simplepyble module

    Returns:
        Dict containing:
        - 'stats': Connection and analysis statistics
        - 'parsed_data': Successfully parsed characteristics
        - 'raw_data': Raw bytes from all characteristics
        - 'service_info': Service and characteristic metadata
        - 'analysis': Additional analysis results
    """
    translator = BluetoothSIGTranslator()
    start_time = time.time()

    results = {
        "stats": {
            "connection_time": 0,
            "services_discovered": 0,
            "characteristics_found": 0,
            "characteristics_read": 0,
            "characteristics_parsed": 0,
            "characteristics_validated": 0,
        },
        "parsed_data": {},
        "raw_data": {},
        "service_info": {},
        "analysis": {},
    }

    print(f"🔵 Comprehensive analysis of device: {address}")
    print("🔍 Discovering ALL services and characteristics...")

    try:
        # Get adapter
        adapters = simpleble_module.Adapter.get_adapters()
        if not adapters:
            print("❌ No BLE adapters found")
            return results

        adapter = adapters[0]

        # Find the device
        print("🔍 Looking for device...")
        adapter.scan_start()
        time.sleep(5.0)
        adapter.scan_stop()

        scan_results = adapter.scan_get_results()
        target_peripheral = None

        for peripheral in scan_results:
            try:
                if hasattr(peripheral, "address") and peripheral.address() == address:
                    target_peripheral = peripheral
                    break
                if peripheral.identifier() == address:
                    target_peripheral = peripheral
                    break
            except Exception:  # pylint: disable=broad-exception-caught
                continue

        if not target_peripheral:
            print(f"❌ Device {address} not found in scan results")
            return results

        # Connect to device
        print("🔗 Connecting...")
        target_peripheral.connect()

        if not target_peripheral.is_connected():
            print("❌ Failed to connect")
            return results

        connection_time = time.time() - start_time
        results["stats"]["connection_time"] = connection_time
        print(f"✅ Connected to {address} in {connection_time:.2f}s")

        # Allow device to settle after connection
        time.sleep(0.5)

        # Discover all services and characteristics
        print("\n🔍 Discovering all services...")
        services = target_peripheral.services()
        results["stats"]["services_discovered"] = len(list(services))

        print(f"📋 Found {len(list(services))} services:")

        # Process all services and characteristics (pass connected peripheral for reads)
        _process_simpleble_services(services, translator, results, target_peripheral)

        # Enhanced SIG translator analysis
        _perform_sig_analysis(results, translator)

        # Disconnect
        target_peripheral.disconnect()
        print(f"\n🔌 Disconnected from {address}")
        print("✅ Comprehensive analysis completed")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Comprehensive analysis failed: {e}")
        results["error"] = str(e)

    return results


async def discover_services_and_characteristics_bleak(  # pylint: disable=too-many-locals
    address: str, timeout: float = 10.0
) -> dict:
    """Discover all services and characteristics on a BLE device using Bleak.

    Args:
        address: BLE device address
        timeout: Connection timeout

    Returns:
        Dictionary of discovered services and characteristics
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for service discovery")
        return {}

    translator = BluetoothSIGTranslator()
    discovery_results = {}

    print(f"🔄 Discovering services on {address}...")

    try:
        async with BleakClient(address, timeout=timeout) as client:
            print("✅ Connected for service discovery")

            services = client.services
            await asyncio.sleep(0.5)  # Allow device to settle

            for service in services:
                service_info = translator.get_service_info(service.uuid)
                service_name = service_info.name if service_info else "Unknown Service"

                print(f"\n🔧 Service: {service_name} ({service.uuid[:8]}...)")

                service_chars = []
                for char in service.characteristics:
                    char_uuid_short = (
                        char.uuid[4:8].upper()
                        if len(char.uuid) > 8
                        else char.uuid.upper()
                    )
                    char_info = translator.get_characteristic_info(char_uuid_short)
                    char_name = char_info.name if char_info else char.description

                    service_chars.append(
                        {
                            "uuid": char_uuid_short,
                            "name": char_name,
                            "properties": list(char.properties),
                        }
                    )

                    print(
                        f"  📋 {char_name} ({char_uuid_short}) - {', '.join(char.properties)}"
                    )

                discovery_results[service.uuid] = {
                    "name": service_name,
                    "characteristics": service_chars,
                }

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Service discovery failed: {e}")

    return discovery_results


async def handle_notifications_bleak(
    address: str, duration: int = 30, timeout: float = 10.0
) -> int:
    """Monitor BLE notifications with SIG parsing using Bleak.

    Args:
        address: BLE device address
        duration: Duration to monitor notifications in seconds
        timeout: Connection timeout

    Returns:
        Number of notifications received
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for notifications")
        return 0

    translator = BluetoothSIGTranslator()
    notification_count = 0

    def notification_handler(sender, data):
        nonlocal notification_count
        notification_count += 1

        # Extract UUID from sender
        char_uuid = (
            sender.uuid[4:8].upper() if len(sender.uuid) > 8 else sender.uuid.upper()
        )

        # Parse with SIG standards
        result = translator.parse_characteristic(char_uuid, data)

        if result.parse_success:
            unit_str = f" {result.unit}" if result.unit else ""
            print(
                f"🔔 Notification #{notification_count}: {result.name} = {result.value}{unit_str}"
            )
        else:
            print(
                f"🔔 Notification #{notification_count}: Raw data from {char_uuid}: {data.hex()}"
            )

    print(f"🔔 Starting notification monitoring for {duration}s...")

    try:
        async with BleakClient(address, timeout=timeout) as client:
            print("✅ Connected for notifications")

            # Subscribe to all notifiable characteristics
            subscribed_count = 0
            for service in client.services:
                for char in service.characteristics:
                    if "notify" in char.properties:
                        char_name = char.description or f"Char-{char.uuid[4:8]}"
                        print(f"📡 Subscribing to {char_name} notifications...")
                        await client.start_notify(char.uuid, notification_handler)
                        subscribed_count += 1

            if subscribed_count == 0:
                print("❌ No notifiable characteristics found")
                return 0

            print(f"📡 Subscribed to {subscribed_count} characteristics")

            # Wait for notifications
            await asyncio.sleep(duration)

            print(
                f"\n📊 Monitoring complete. Received {notification_count} notifications."
            )

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Notification monitoring failed: {e}")

    return notification_count


def _process_single_characteristic(char, translator, results, service_uuid, peripheral):
    """Process a single SimpleBLE characteristic.

    Returns:
        (read_ok: bool, parsed_count: int)
    """
    try:
        char_uuid = char.uuid()
        char_uuid_short = short_uuid(char_uuid)

        # Get characteristic info
        char_info = translator.get_characteristic_info(char_uuid_short)
        char_name = char_info.name if char_info else f"Char-{char_uuid_short}"

        char_data = {
            "uuid": char_uuid_short,
            "name": char_name,
            "readable": False,
        }
        results["service_info"][service_uuid]["characteristics"].append(char_data)

        print(f"      └─ {char_name} ({char_uuid_short}) - [read]")

        # Try to read the characteristic using the peripheral read API
        try:
            print(f"  📖 Reading {char_uuid_short}...")

            raw_data = peripheral.read(service_uuid, char_uuid)

            if raw_data:
                raw_bytes = _convert_to_bytes(raw_data)
                results["raw_data"][char_uuid_short] = raw_bytes
                results["service_info"][service_uuid]["characteristics"][-1][
                    "readable"
                ] = True

                # Display raw data
                _display_raw_data(char_uuid_short, raw_bytes)

                # Try to parse with bluetooth_sig
                parsed = _parse_characteristic_data(
                    char_uuid_short, raw_bytes, char_name, translator, results
                )
                return True, parsed

            print(f"  ⚠️  {char_uuid_short}: No data read")
            return False, 0

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"  ❌ Error reading {char_uuid_short}: {e}")
            return False, 0

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"     ❌ Error processing characteristic: {e}")
    return False, 0


def _process_simpleble_services(services, translator, results, peripheral):  # pylint: disable=too-many-locals
    """Process SimpleBLE services and characteristics (helper function)."""
    chars_found = 0
    chars_read = 0
    chars_parsed = 0

    for service in services:
        try:
            service_uuid = service.uuid()
            service_info = translator.get_service_info(service_uuid)
            service_name = service_info.name if service_info else "Unknown Service"

            results["service_info"][service_uuid] = {
                "name": service_name,
                "characteristics": [],
            }

            print(f"\n🔧 Service: {service_name} ({service_uuid[:8]}...)")

            # Get characteristics for this service
            characteristics = service.characteristics()
            chars_found += len(characteristics)

            print(f"   └─ {len(characteristics)} characteristics:")

            for char in characteristics:
                read_ok, parsed_count = _process_single_characteristic(
                    char, translator, results, service_uuid, peripheral
                )
                if read_ok:
                    chars_read += 1
                if parsed_count > 0:
                    chars_parsed += parsed_count

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"  ❌ Error processing service: {e}")

    # Update stats
    results["stats"]["characteristics_found"] = chars_found
    results["stats"]["characteristics_read"] = chars_read
    results["stats"]["characteristics_parsed"] = chars_parsed


def _convert_to_bytes(raw_data):
    """Convert raw data to bytes (helper function)."""
    if hasattr(raw_data, "__iter__") and not isinstance(raw_data, (str, bytes)):
        return bytes(raw_data)
    if isinstance(raw_data, str):
        return raw_data.encode("utf-8")
    return raw_data


def _display_raw_data(char_uuid_short, raw_bytes):
    """Display raw data in appropriate format (helper function)."""
    if len(raw_bytes) == 0:
        print(f"  ⚠️  {char_uuid_short}: Empty data (0 bytes)")
    else:
        try:
            str_val = raw_bytes.decode("utf-8").strip("\x00")
            is_printable = str_val and all(
                c.isprintable() or c.isspace() for c in str_val
            )
            if is_printable and len(str_val) > 0:
                print(f"  ✅ {char_uuid_short}: '{str_val}' ({len(raw_bytes)} bytes)")
            else:
                hex_val = " ".join(f"{b:02x}" for b in raw_bytes)
                print(f"  ✅ {char_uuid_short}: {hex_val} ({len(raw_bytes)} bytes)")
        except UnicodeDecodeError:
            hex_val = " ".join(f"{b:02x}" for b in raw_bytes)
            print(f"  ✅ {char_uuid_short}: {hex_val} ({len(raw_bytes)} bytes)")


def _parse_characteristic_data(
    char_uuid_short, raw_bytes, char_name, translator, results
):
    """Parse characteristic data and store results (helper function)."""
    try:
        parsed_data = translator.parse_characteristic(char_uuid_short, raw_bytes)

        if parsed_data.value is not None:
            unit_str = f" {parsed_data.unit}" if parsed_data.unit else ""
            print(f"  🏗️ {char_name}: {parsed_data.value}{unit_str}")

            results["parsed_data"][char_uuid_short] = {
                "name": char_name,
                "value": parsed_data.value,
                "unit": parsed_data.unit,
            }
            return 1
    except Exception:  # pylint: disable=broad-exception-caught
        pass  # Silently skip unparseable characteristics

    return 0


def _perform_sig_analysis(results, translator):
    """Perform enhanced SIG analysis (helper function)."""
    print("\n🔍 Enhanced SIG Analysis...")
    if results["raw_data"]:
        discovered_uuids = list(results["raw_data"].keys())
        print(f"📊 Analyzing {len(discovered_uuids)} discovered characteristics:")

        # Batch analysis
        char_info = translator.get_characteristics_info(discovered_uuids)
        for uuid, info in char_info.items():
            if info:
                name = getattr(info, "name", "Unknown")
                data_type = getattr(info, "value_type", "unknown")
                print(f"  📋 {uuid}: {name} [{data_type}]")
            else:
                print(f"  ❓ {uuid}: Unknown characteristic")

        # Validation analysis
        print("\n🔍 Data validation:")
        valid_count = 0
        validation_results = {}

        for uuid, data in results["raw_data"].items():
            if isinstance(data, (bytes, bytearray)):
                is_valid = translator.validate_characteristic_data(uuid, data)
                status = "✅" if is_valid else "⚠️"
                validity = "Valid" if is_valid else "Unknown format"
                print(f"  {status} {uuid}: {validity}")
                validation_results[uuid] = {
                    "valid": is_valid,
                    "status": validity,
                }
                if is_valid:
                    valid_count += 1

        results["analysis"]["validation"] = validation_results
        results["stats"]["characteristics_validated"] = valid_count

        print(
            f"\n📈 Validation: {valid_count}/{len(results['raw_data'])} characteristics have known format"
        )


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
