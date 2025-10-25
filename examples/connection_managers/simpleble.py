#!/usr/bin/env python3
"""SimplePyBLE connection manager moved out of the utils package.

This file intentionally imports the optional SimplePyBLE module at import
time so that attempting to import this module when the backend is not
installed fails fast and provides a clear diagnostic.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import simplepyble

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.uuid import BluetoothUUID


class SimplePyBLEConnectionManager(ConnectionManagerProtocol):
    """Connection manager using SimplePyBLE for BLE communication."""

    def __init__(self, address: str, simpleble_module: Any, timeout: float = 30.0) -> None:  # noqa: ANN401
        """Initialize the connection manager."""
        self.address = address
        self.timeout = timeout
        self.simpleble_module = simpleble_module
        self.adapter: simplepyble.Adapter  # type: ignore[no-any-unimported]
        self.peripheral: simplepyble.Peripheral | None = None  # type: ignore[no-any-unimported]
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def connect(self) -> None:
        """Connect to the device."""

        def _connect() -> None:
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
        """Disconnect from the device."""
        if self.peripheral:
            await asyncio.get_event_loop().run_in_executor(self.executor, self.peripheral.disconnect)

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read a GATT characteristic."""

        def _read() -> bytes:
            p = self.peripheral
            assert p is not None
            for service in p.services():
                for char in service.characteristics():
                    if char.uuid().upper() == str(char_uuid).upper():
                        raw_value = char.read()
                        return bytes(raw_value)
            raise RuntimeError(f"Characteristic {char_uuid} not found")

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read)

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes) -> None:
        """Write to a GATT characteristic."""

        def _write() -> None:
            p = self.peripheral
            assert p is not None
            for service in p.services():
                for char in service.characteristics():
                    if char.uuid().upper() == str(char_uuid).upper():
                        char.write(data)
                        return
            raise RuntimeError(f"Characteristic {char_uuid} not found")

        await asyncio.get_event_loop().run_in_executor(self.executor, _write)

    async def get_services(self) -> object:
        """Get services."""

        def _get_services() -> object:
            p = self.peripheral
            assert p is not None
            services: list[Any] = []
            for service in p.services():
                service_obj = {"uuid": service.uuid(), "characteristics": [c.uuid() for c in service.characteristics()]}
                services.append(service_obj)
            return services

        return await asyncio.get_event_loop().run_in_executor(self.executor, _get_services)

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        """Start notifications."""
        raise NotImplementedError("Notification not supported in this example")

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        """Stop notifications."""
        raise NotImplementedError("Notification not supported in this example")

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.peripheral is not None and self.peripheral.is_connected()
