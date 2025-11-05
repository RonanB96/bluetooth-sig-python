#!/usr/bin/env python3
"""SimplePyBLE connection manager moved out of the utils package.

This file intentionally imports the optional SimplePyBLE module at import
time so that attempting to import this module when the backend is not
installed fails fast and provides a clear diagnostic.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Protocol

import simplepyble

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.io import RawCharacteristicBatch, RawCharacteristicRead
from bluetooth_sig.types.uuid import BluetoothUUID


class _DescriptorLike(Protocol):
    uuid: object
    value: bytes | bytearray | None


class _CharacteristicLike(Protocol):
    uuid: object
    properties: Sequence[str] | None
    descriptors: Iterable[_DescriptorLike] | None
    value: bytes | bytearray | None


class _ServiceLike(Protocol):
    characteristics: Iterable[_CharacteristicLike] | None


def simpleble_services_to_batch(
    services: Iterable[_ServiceLike] | None,
    values_by_uuid: Mapping[str, bytes] | None = None,
) -> RawCharacteristicBatch:
    """Build a RawCharacteristicBatch from SimpleBLE service metadata.

    Duck-typed similarly to the Bleak helper. Many SimpleBLE wrappers
    expose `service.characteristics` where each characteristic has a `.uuid`
    and optionally `.properties` and `.descriptors` with `.uuid`/`.value`.
    Provide `values_by_uuid` if you've read characteristic values separately.
    """
    items: list[RawCharacteristicRead] = []

    for service in services or []:
        chars = getattr(service, "characteristics", [])
        for char in chars:
            uuid = str(char.uuid)
            raw: bytes | None = None

            # Prefer explicit values map if provided
            if values_by_uuid is not None:
                raw = values_by_uuid.get(uuid) or values_by_uuid.get(uuid.upper()) or values_by_uuid.get(uuid.lower())

            # Fallback to attribute commonly present on some wrappers
            if raw is None:
                raw = getattr(char, "value", None)

            if raw is None:
                continue  # skip characteristics without a value

            props = list(getattr(char, "properties", []) or [])

            # Collect descriptor raw values when available
            desc_bytes: dict[str, bytes] = {}
            for desc in getattr(char, "descriptors", []) or []:
                d_uuid = str(getattr(desc, "uuid", ""))
                d_val = getattr(desc, "value", None)
                if d_uuid and isinstance(d_val, (bytes, bytearray)):
                    desc_bytes[d_uuid] = bytes(d_val)

            items.append(
                RawCharacteristicRead(uuid=uuid, raw_data=bytes(raw), descriptors=desc_bytes, properties=props)
            )

    return RawCharacteristicBatch(items=items)


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
