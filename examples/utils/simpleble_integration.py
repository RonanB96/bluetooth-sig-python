#!/usr/bin/env python3
"""SimplePyBLE integration utilities for BLE examples.

This module provides SimplePyBLE-specific BLE connection and characteristic reading functions.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator


def comprehensive_device_analysis_simpleble(  # pylint: disable=too-many-locals
    address: str, simpleble_module
) -> dict[str, Any]:
    """Analyze a BLE device using SimplePyBLE (synchronous).

    Args:
        address: Device address
        simpleble_module: The imported simplepyble module

    Returns:
        Dict of analysis results
    """
    print("📱 SimplePyBLE Comprehensive Device Analysis...")
    results = {}

    try:
        # Initialize SimplePyBLE adapter
        adapters = simpleble_module.Adapter.get_adapters()
        if not adapters:
            print("   ❌ No BLE adapters found")
            return {}

        adapter = adapters[0]
        print(f"   📡 Using adapter: {adapter.address()}")

        # Scan for device
        adapter.scan_for(2000)  # 2 seconds scan
        peripherals = adapter.scan_get_results()

        target_peripheral = None
        for peripheral in peripherals:
            if peripheral.address().upper() == address.upper():
                target_peripheral = peripheral
                break

        if not target_peripheral:
            print(f"   ❌ Device {address} not found in scan")
            return {}

        print(f"   🎯 Found target device: {target_peripheral.identifier()}")

        # Connect to device
        target_peripheral.connect()
        print("   ✅ Connected successfully")

        # Get services
        services = target_peripheral.services()
        print(f"   🔍 Found {len(services)} services")

        # Process characteristics
        translator = BluetoothSIGTranslator()
        for service in services:
            characteristics = service.characteristics()

            for characteristic in characteristics:
                char_uuid = characteristic.uuid()

                try:
                    # Try to read characteristic
                    raw_data = characteristic.read()
                    char_uuid_short = (
                        char_uuid[4:8].upper()
                        if len(char_uuid) > 8
                        else char_uuid.upper()
                    )

                    # Parse with bluetooth_sig
                    result = translator.parse_characteristic(char_uuid_short, raw_data)

                    if result.parse_success:
                        results[char_uuid_short] = {
                            "name": result.name,
                            "value": result.value,
                            "unit": result.unit,
                            "raw_data": raw_data,
                        }
                        unit_str = f" {result.unit}" if result.unit else ""
                        print(f"   ✅ {result.name}: {result.value}{unit_str}")
                    else:
                        print(f"   ❌ {char_uuid_short}: Parse failed")

                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"   ⚠️  {char_uuid}: {e}")

        # Disconnect
        target_peripheral.disconnect()
        print("   🔌 Disconnected")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"   ❌ SimplePyBLE analysis failed: {e}")

    return results
