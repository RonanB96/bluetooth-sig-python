#!/usr/bin/env python3
"""Demo functions for BLE examples.

This module provides demo functions that were previously in ble_utils.py
"""

from __future__ import annotations

import asyncio
import types
from typing import cast

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.device.device import Device
from bluetooth_sig.gatt.characteristics.base import CharacteristicData
from bluetooth_sig.types.uuid import BluetoothUUID

from .data_parsing import display_parsed_results
from .library_detection import (
    bleak_retry_available,
    simplepyble_available,
    simplepyble_module,
)
from .models import LibraryComparisonResult
from .simpleble_integration import comprehensive_device_analysis_simpleble


async def demo_basic_usage(address: str, connection_manager: ConnectionManagerProtocol) -> None:
    """Demonstrate basic usage of the bluetooth_sig library (migrated from shared_utils).

    This function is used by the top-level `examples/basic_usage.py` script as the
    canonical demonstration of connecting, reading a handful of common
    characteristics and displaying parsed results.
    """
    print(f"Connecting to device: {address}")

    translator = BluetoothSIGTranslator()
    device = Device(connection_manager, translator)

    try:
        print("🔗 Connecting to device...")
        await connection_manager.connect()
        print("✅ Connected, reading characteristics...")

        common_uuids = ["2A00", "2A19", "2A29", "2A24", "2A25", "2A26", "2A27", "2A28"]
        parsed_results: dict[str, CharacteristicData] = {}

        for uuid_short in common_uuids:
            try:
                parsed = await device.read(uuid_short)
                if parsed and getattr(parsed, "parse_success", False):
                    parsed_results[uuid_short] = parsed
                    unit_str = f" {getattr(parsed, 'unit', '')}" if getattr(parsed, "unit", None) else ""
                    print(f"  ✅ {getattr(parsed, 'name', uuid_short)}: {getattr(parsed, 'value', 'N/A')}{unit_str}")
                else:
                    print(f"  • {uuid_short}: Read failed or parse failed")
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"  ❌ {uuid_short}: Error - {e}")

        await connection_manager.disconnect()
        print("✅ Disconnected")

        # Convert to BluetoothUUID-keyed mapping for the display helper
        normalized: dict[BluetoothUUID, CharacteristicData] = {}
        for k, v in parsed_results.items():
            try:
                normalized[BluetoothUUID(k)] = v
            except Exception:
                # Fallback: generate a BluetoothUUID from the string as best effort
                normalized[BluetoothUUID(str(k))] = v

        display_parsed_results(normalized, title="Basic Usage Results")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Basic usage demo failed: {e}")
        print("This may be due to device being unavailable or connection issues.")


async def demo_service_discovery(address: str, connection_manager: ConnectionManagerProtocol) -> None:
    """Demonstrate service discovery using the Device class (migrated from shared_utils).

    The original example enumerated services and attempted to read and parse
    characteristics where possible. The migrated version re-uses
    :func:`display_parsed_results` to keep output consistent with other examples.
    """
    print(f"Discovering services on device: {address}")

    from bluetooth_sig import BluetoothSIGTranslator
    from bluetooth_sig.device.device import Device

    translator = BluetoothSIGTranslator()
    device = Device(connection_manager, translator)

    try:
        print("🔍 Discovering services...")
        print("   Connecting to device...")
        await connection_manager.connect()
        print("   ✅ Connected, discovering services...")
        services = await device.discover_services()

        print(f"✅ Found {len(services)} services:")
        total_chars = 0
        parsed_chars = 0

        parsed_results: dict[str, CharacteristicData] = {}

        for service_uuid, service_info in services.items():
            service_name = translator.get_service_info_by_uuid(service_uuid)
            if service_name:
                print(f"  📋 {service_uuid}: {service_name.name}")
            else:
                print(f"  📋 {service_uuid}: Unknown service")

            characteristics = service_info.characteristics
            if characteristics:
                print(f"     └─ {len(characteristics)} characteristics:")
                for char_uuid, _char_info in characteristics.items():
                    total_chars += 1
                    try:
                        short_uuid = char_uuid[4:8].upper() if len(char_uuid) > 8 else char_uuid.upper()
                        parsed = await device.read(short_uuid)

                        if parsed and getattr(parsed, "parse_success", False):
                            parsed_chars += 1
                            parsed_results[short_uuid] = parsed
                            char_name = getattr(parsed, "name", short_uuid)
                            value = getattr(parsed, "value", "N/A")
                            unit = getattr(parsed, "unit", "")
                            print(f"        ✅ {short_uuid}: {char_name} = {value} {unit}")
                        else:
                            char_info_obj = translator.get_characteristic_info_by_uuid(short_uuid)
                            if char_info_obj:
                                print(f"        • {short_uuid}: {char_info_obj.name} (read failed)")
                            else:
                                print(f"        • {short_uuid}: Unknown characteristic")
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        short_uuid = char_uuid[4:8].upper() if len(char_uuid) > 8 else char_uuid.upper()
                        char_info_obj = translator.get_characteristic_info_by_uuid(short_uuid)
                        if char_info_obj:
                            print(f"        ❌ {short_uuid}: {char_info_obj.name} (error: {e})")
                        else:
                            print(f"        ❌ {short_uuid}: Unknown characteristic (error: {e})")

        await connection_manager.disconnect()
        print("   ✅ Disconnected")

        print(f"\n📊 Device summary: {device}")
        print(f"📊 Total characteristics: {total_chars}, Successfully parsed: {parsed_chars}")

        normalized: dict[BluetoothUUID, CharacteristicData] = {}
        for k, v in parsed_results.items():
            try:
                normalized[BluetoothUUID(k)] = v
            except Exception:
                normalized[BluetoothUUID(str(k))] = v

        display_parsed_results(normalized, title="Service Discovery Results")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Service discovery failed: {e}")
        print("This may be due to device being unavailable or connection issues.")


async def comprehensive_device_analysis_bleak_retry(
    address: str, target_uuids: list[str]
) -> dict[str, CharacteristicData]:
    """Analyze a BLE device using Bleak-retry.

    Args:
        address: Device address
        target_uuids: List of short UUIDs to read

    Returns:
        Mapping of short UUIDs to characteristic parse data

    """
    from bluetooth_sig import BluetoothSIGTranslator
    from examples.connection_managers.bleak_retry import BleakRetryConnectionManager

    translator = BluetoothSIGTranslator()
    manager = BleakRetryConnectionManager(address)

    try:
        await manager.connect()

        # Delegate reading to canonical helper
        from examples.utils.connection_helpers import read_characteristics_with_manager

        read_results = await read_characteristics_with_manager(manager, target_uuids)

        parsed: dict[str, CharacteristicData] = {}
        for short_uuid, read_result in read_results.items():
            try:
                parsed_outcome = translator.parse_characteristic(short_uuid, read_result.raw_data)
                parsed[short_uuid] = parsed_outcome
            except Exception:  # pylint: disable=broad-exception-caught
                # Skip failed parses but continue processing
                continue

        return parsed
    finally:
        try:
            await manager.disconnect()
        except Exception:
            pass


async def demo_library_comparison(address: str, target_uuids: list[str] | None = None) -> LibraryComparisonResult:
    """Compare BLE libraries using comprehensive device analysis.

    Note: Only supports bleak-retry and simpleble (plain bleak removed).

    Args:
        address: Device address
        target_uuids: UUIDs to read, or None for comprehensive analysis

    Returns:
        Dict of results from each library

    """
    from .models import LibraryComparisonResult

    comparison_results = LibraryComparisonResult(status="ok", data=None)

    print("🔍 Comparing BLE Libraries (bleak-retry and simpleble only)")
    print("=" * 60)

    # Test Bleak-retry
    if bleak_retry_available:
        try:
            print("\n🔁 Running Bleak-retry analysis...")
            if target_uuids is None:
                target_uuids = ["2A19", "2A00"]  # Default UUIDs for demo

            bleak_results = await comprehensive_device_analysis_bleak_retry(address, target_uuids)
            comparison_results.data = bleak_results
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"❌ Bleak-retry analysis failed: {e}")

    await asyncio.sleep(1)

    # Test SimplePyBLE
    if simplepyble_available and simplepyble_module:
        try:
            print("\n🔁 Running SimplePyBLE analysis...")
            simple_results = await asyncio.to_thread(
                comprehensive_device_analysis_simpleble,
                address,
                cast(types.ModuleType, simplepyble_module),
            )
            if comparison_results.data is None:
                comparison_results.data = simple_results
            else:
                # Merge results if both succeeded
                comparison_results.data.update(simple_results)  # type: ignore[arg-type]
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"❌ SimplePyBLE analysis failed: {e}")

    return comparison_results
