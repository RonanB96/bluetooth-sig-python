#!/usr/bin/env python3
"""SimplePyBLE integration utilities for BLE examples.

This module provides SimplePyBLE-specific BLE connection and
characteristic reading functions.
"""

from __future__ import annotations

import asyncio
import types
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import simplepyble

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.data_types import CharacteristicData
from bluetooth_sig.types.uuid import BluetoothUUID


def scan_devices_simpleble(  # pylint: disable=duplicate-code
    simpleble_module: types.ModuleType, timeout: float = 10.0
) -> list[dict[str, Any]]:
    # NOTE: Device listing pattern duplicates bleak_retry_integration scan display logic.
    # Duplication justified because:
    # 1. SimplePyBLE API differs from Bleak (different method names, synchronous)
    # 2. Example code prioritizes readability over DRY for learning purposes
    # 3. Consolidation would require abstract device wrapper, over-engineering for examples
    """Scan for BLE devices using SimplePyBLE utilities."""
    # NOTE: SimplePyBLE exposes dynamic attributes; stubs provide type safety
    adapters = simpleble_module.Adapter.get_adapters()  # pylint: disable=no-member
    if not adapters:
        return []

    adapter = adapters[0]
    adapter.scan_for(int(timeout * 1000))

    devices: list[dict[str, Any]] = []
    for peripheral in adapter.scan_get_results():
        info: dict[str, Any] = {
            "peripheral": peripheral,
            "name": peripheral.identifier(),
            "address": peripheral.address(),
            "rssi": peripheral.rssi(),
        }
        devices.append(info)

    return devices


class SimpleCharacteristic:
    """Simple characteristic object compatible with Device class
    expectations."""

    def __init__(self, uuid: str, properties: list[str] | None = None):
        self.uuid = uuid
        self.properties = properties or []


class SimpleService:
    """Simple service object compatible with Device class expectations."""

    def __init__(self, uuid: str, characteristics: list[SimpleCharacteristic] | None = None):
        self.uuid = uuid
        self.characteristics = characteristics or []


class SimplePyBLEConnectionManager(ConnectionManagerProtocol):
    """Connection manager using SimplePyBLE for BLE communication."""

    def __init__(self, address: str, simpleble_module: types.ModuleType, timeout: float = 30.0) -> None:
        self.address = address
        self.timeout = timeout
        self.simpleble_module = simpleble_module
        self.adapter: simplepyble.Adapter
        self.peripheral: simplepyble.Peripheral | None = None  # type: ignore[no-any-unimported]
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def connect(self) -> None:
        def _connect() -> None:
            # NOTE: SimplePyBLE exposes dynamic attributes; stubs provide type safety
            adapters = self.simpleble_module.Adapter.get_adapters()  # pylint: disable=no-member
            if not adapters:
                raise RuntimeError("No BLE adapters found")
            self.adapter = adapters[0]

            self.adapter.scan_for(2000)
            for peripheral in self.adapter.scan_get_results():
                if peripheral.address().upper() == self.address.upper():
                    self.peripheral = peripheral
                    break
            if not self.peripheral:
                raise RuntimeError(f"Device {self.address} not found")
            self.peripheral.connect()

        await asyncio.get_event_loop().run_in_executor(self.executor, _connect)

    async def disconnect(self) -> None:
        if self.peripheral:
            await asyncio.get_event_loop().run_in_executor(self.executor, self.peripheral.disconnect)

    async def read_gatt_char(self, char_uuid: str) -> bytes:
        def _read() -> bytes:
            p = self.peripheral
            assert p is not None
            for service in p.services():
                for char in service.characteristics():
                    if char.uuid().upper() == char_uuid.upper():
                        raw_value = char.read()
                        return bytes(raw_value)
            raise RuntimeError(f"Characteristic {char_uuid} not found")

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read)

    async def write_gatt_char(self, char_uuid: str, data: bytes) -> None:
        def _write() -> None:
            p = self.peripheral
            assert p is not None
            for service in p.services():
                for char in service.characteristics():
                    if char.uuid().upper() == char_uuid.upper():
                        char.write(data)
                        return
            raise RuntimeError(f"Characteristic {char_uuid} not found")

        await asyncio.get_event_loop().run_in_executor(self.executor, _write)

    async def get_services(self) -> object:
        def _get_services() -> object:
            p = self.peripheral
            assert p is not None
            # Convert SimplePyBLE services to the format expected by Device class
            services: list[SimpleService] = []
            for service in p.services():
                service_obj = SimpleService(service.uuid())

                for char in service.characteristics():
                    char_obj = SimpleCharacteristic(char.uuid())
                    service_obj.characteristics.append(char_obj)

                services.append(service_obj)

            return services

        return await asyncio.get_event_loop().run_in_executor(self.executor, _get_services)

    async def start_notify(self, char_uuid: str, callback: Any) -> None:
        # Not implemented: SimplePyBLE notification support
        raise NotImplementedError("Notification not supported in this example")

    async def stop_notify(self, char_uuid: str) -> None:
        # Not implemented: SimplePyBLE notification support
        raise NotImplementedError("Notification not supported in this example")

    @property
    def is_connected(self) -> bool:
        """Check if the connection is currently active."""
        return self.peripheral is not None and self.peripheral.is_connected()


def comprehensive_device_analysis_simpleble(  # pylint: disable=too-many-locals,duplicate-code
    address: str,
    simpleble_module: types.ModuleType,
) -> dict[str, CharacteristicData]:
    # NOTE: Result parsing pattern duplicates shared_utils and data_parsing display logic.
    # Duplication justified because:
    # 1. SimplePyBLE is synchronous, shared utils are async (different execution models)
    # 2. This returns CharacteristicData objects, shared utils return dicts (different types)
    # 3. Example code prioritizes clarity over abstraction for educational purposes
    """Analyze a BLE device using SimplePyBLE (synchronous).

    Args:
        address: Device address
        simpleble_module: The imported simplepyble module

    Returns:
        Mapping of short UUIDs to characteristic parse data
    """
    print("📱 SimplePyBLE Comprehensive Device Analysis...")
    results: dict[str, CharacteristicData] = {}

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
                    char_uuid_short = BluetoothUUID(char_uuid)
                    parse_outcome = translator.parse_characteristic(char_uuid_short, raw_data)
                    results[char_uuid_short] = parse_outcome
                    if parse_outcome.parse_success:
                        unit_str = f" {parse_outcome.unit}" if parse_outcome.unit else ""
                        print(f"   ✅ {parse_outcome.name}: {parse_outcome.value}{unit_str}")
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
