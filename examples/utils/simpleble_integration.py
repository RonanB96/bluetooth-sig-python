#!/usr/bin/env python3
"""SimplePyBLE integration utilities for BLE examples.

This module provides SimplePyBLE-specific BLE connection and characteristic reading functions.
"""

from __future__ import annotations

import asyncio
import types
from concurrent.futures import ThreadPoolExecutor
from typing import Any, cast

import simplepyble

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device.connection import ConnectionManagerProtocol


class SimplePyBLEConnectionManager(ConnectionManagerProtocol):
    """Connection manager using SimplePyBLE for BLE communication."""

    def __init__(
        self, address: str, simpleble_module: types.ModuleType, timeout: float = 30.0
    ) -> None:
        self.address = address
        self.timeout = timeout
        self.simpleble_module = simpleble_module
        self.adapter: simplepyble.Adapter | None = None
        self.peripheral: simplepyble.Peripheral | None = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def connect(self) -> None:
        def _connect() -> None:
            adapters = self.simpleble_module.Adapter.get_adapters()
            if not adapters:
                raise RuntimeError("No BLE adapters found")
            self.adapter = adapters[0]
            self.adapter.scan_for(2000)
            peripherals = self.adapter.scan_get_results()
            for p in peripherals:
                if p.address().upper() == self.address.upper():
                    self.peripheral = p
                    break
            if not self.peripheral:
                raise RuntimeError(f"Device {self.address} not found")
            self.peripheral.connect()

        await asyncio.get_event_loop().run_in_executor(self.executor, _connect)

    async def disconnect(self) -> None:
        if self.peripheral:
            await asyncio.get_event_loop().run_in_executor(
                self.executor, self.peripheral.disconnect
            )

    async def read_gatt_char(self, char_uuid: str) -> bytes:
        def _read() -> bytes:
            p = self.peripheral
            assert p is not None
            for service in p.services():
                for char in service.characteristics():
                    if char.uuid().upper() == char_uuid.upper():
                        return char.read()
            raise RuntimeError(f"Characteristic {char_uuid} not found")

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read)

    async def write_gatt_char(self, char_uuid: str, data: bytes) -> None:
        def _write() -> None:
            p = self.peripheral
            assert p is not None
            for service in p.services():
                for char in service.characteristics():
                    if char.uuid().upper() == char_uuid.upper():
                        cast(Any, char).write(data)
                        return
            raise RuntimeError(f"Characteristic {char_uuid} not found")

        await asyncio.get_event_loop().run_in_executor(self.executor, _write)

    async def get_services(self) -> object:
        def _get_services() -> object:
            p = self.peripheral
            assert p is not None
            return p.services()

        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _get_services
        )

    async def start_notify(self, char_uuid: str, callback: Any) -> None:
        # Not implemented: SimplePyBLE notification support
        raise NotImplementedError("Notification not supported in this example")

    async def stop_notify(self, char_uuid: str) -> None:
        # Not implemented: SimplePyBLE notification support
        raise NotImplementedError("Notification not supported in this example")


def comprehensive_device_analysis_simpleble(  # pylint: disable=too-many-locals
    address: str, simpleble_module: types.ModuleType
) -> dict[str, Any]:
    """Analyze a BLE device using SimplePyBLE (synchronous).

    Args:
        address: Device address
        simpleble_module: The imported simplepyble module

    Returns:
        Dict of analysis results
    """
    print("📱 SimplePyBLE Comprehensive Device Analysis...")
    results: dict[str, dict[str, Any]] = {}

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
