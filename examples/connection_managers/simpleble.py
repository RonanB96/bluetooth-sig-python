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
from typing import Protocol

import simplepyble

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.unknown import UnknownCharacteristic
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.gatt.services.unknown import UnknownService
from bluetooth_sig.types.data_types import CharacteristicInfo
from bluetooth_sig.types.device_types import DeviceService
from bluetooth_sig.types.gatt_enums import GattProperty
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

    def __init__(
        self,
        address: str,
        timeout: float = 10.0,
        disconnected_callback: Callable[[], None] | None = None,
    ) -> None:
        """Initialize the connection manager.

        Args:
            address: Bluetooth device address
            timeout: Connection timeout in seconds
            disconnected_callback: Optional callback when device disconnects

        """
        super().__init__(address)
        self.timeout = timeout
        self._user_callback = disconnected_callback
        self.adapter: simplepyble.Adapter | None = None
        self.peripheral: simplepyble.Peripheral | None = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._cached_services: list[DeviceService] | None = None

    async def connect(self) -> None:
        """Connect to the device."""

        def _connect() -> None:
            # pylint: disable=no-member  # Stub exists but pylint doesn't recognize it
            adapters = simplepyble.Adapter.get_adapters()
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

            # Set up disconnection callback if provided
            if self._user_callback:
                self.peripheral.set_callback_on_disconnected(self._user_callback)  # type: ignore[misc]

            self.peripheral.connect()
            self._cached_services = None  # Clear cache on new connection

        await asyncio.get_event_loop().run_in_executor(self.executor, _connect)

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self.peripheral:
            self._cached_services = None  # Clear cache on disconnect
            await asyncio.get_event_loop().run_in_executor(self.executor, self.peripheral.disconnect)

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read a GATT characteristic."""

        def _read() -> bytes:
            p = self.peripheral
            assert p is not None
            for service in p.services():
                service_uuid = service.uuid()
                for char in service.characteristics():
                    if char.uuid().upper() == str(char_uuid).upper():
                        # Read using peripheral.read(service_uuid, char_uuid)
                        raw_value = p.read(service_uuid, char.uuid())
                        return bytes(raw_value)
            raise RuntimeError(f"Characteristic {char_uuid} not found")

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read)

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
        """Write to a GATT characteristic.

        Args:
            char_uuid: UUID of the characteristic to write to
            data: Data to write
            response: If True, use write-with-response (write_request);
                     if False, use write-without-response (write_command)

        """

        def _write() -> None:
            p = self.peripheral
            assert p is not None
            for service in p.services():
                service_uuid = service.uuid()
                for char in service.characteristics():
                    if char.uuid().upper() == str(char_uuid).upper():
                        if response:
                            p.write_request(service_uuid, char.uuid(), data)
                        else:
                            p.write_command(service_uuid, char.uuid(), data)
                        return
            raise RuntimeError(f"Characteristic {char_uuid} not found")

        await asyncio.get_event_loop().run_in_executor(self.executor, _write)

    async def get_services(self) -> list[DeviceService]:
        """Get services from SimplePyBLE, converted to DeviceService objects.

        Services are cached after first retrieval. SimplePyBLE's services() method
        may perform discovery each call, so caching is important for efficiency.

        Returns:
            List of DeviceService instances

        """
        # Return cached services if available
        if self._cached_services is not None:
            return self._cached_services

        device_services: list[DeviceService] = []

        p = self.peripheral
        if not p:
            return device_services

        def _get_services() -> list[DeviceService]:
            services: list[DeviceService] = []
            # SimplePyBLE's services() may not be cached internally
            for simpleble_service in p.services():
                # Convert SimplePyBLE service UUID to BluetoothUUID
                service_uuid = BluetoothUUID(simpleble_service.uuid())

                # Try to get the service class from registry
                service_class = GattServiceRegistry.get_service_class(service_uuid)

                if service_class:
                    # Create service instance
                    service_instance = service_class()
                else:
                    # Create UnknownService for unrecognized services
                    service_instance = UnknownService(
                        uuid=service_uuid,
                        name=f"Unknown Service ({service_uuid.short_form}...)",
                    )

                # Populate characteristics with actual class instances
                characteristics: dict[str, BaseCharacteristic] = {}
                for char in simpleble_service.characteristics():
                    char_uuid = BluetoothUUID(char.uuid())

                    # Extract properties from SimplePyBLE characteristic
                    properties: list[GattProperty] = []
                    if char.can_read():
                        properties.append(GattProperty.READ)
                    if char.can_write_request():
                        properties.append(GattProperty.WRITE)
                    if char.can_write_command():
                        properties.append(GattProperty.WRITE_WITHOUT_RESPONSE)
                    if char.can_notify():
                        properties.append(GattProperty.NOTIFY)
                    if char.can_indicate():
                        properties.append(GattProperty.INDICATE)

                    # Try to get the characteristic class from registry
                    char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(char_uuid)

                    if char_class:
                        # Create characteristic instance with runtime properties from device
                        char_instance = char_class(properties=properties)
                        characteristics[str(char_uuid)] = char_instance
                    else:
                        # Fallback: Create UnknownCharacteristic for unrecognized UUIDs
                        char_info = CharacteristicInfo(
                            uuid=char_uuid,
                            name=f"Unknown Characteristic ({char_uuid.short_form}...)",
                            description="",
                        )
                        char_instance = UnknownCharacteristic(info=char_info, properties=properties)
                        characteristics[str(char_uuid)] = char_instance

                # Type ignore needed due to dict invariance with union types
                services.append(DeviceService(service=service_instance, characteristics=characteristics))  # type: ignore[arg-type]

            return services

        result = await asyncio.get_event_loop().run_in_executor(self.executor, _get_services)

        # Cache the result
        self._cached_services = result
        return result

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        """Start notifications for a characteristic.

        Args:
            char_uuid: UUID of the characteristic to subscribe to
            callback: Callback function(uuid: str, data: bytes) to call when notification arrives

        """

        def _start_notify() -> None:
            p = self.peripheral
            assert p is not None

            # Find the characteristic's service and UUID
            for service in p.services():
                for char in service.characteristics():
                    if char.uuid().upper() == str(char_uuid).upper():
                        # SimplePyBLE notify takes (service_uuid, char_uuid, callback)
                        # Callback receives bytes, we need to adapt to include UUID
                        def adapted_callback(data: bytes) -> None:
                            callback(str(char_uuid), data)

                        p.notify(service.uuid(), char.uuid(), adapted_callback)
                        return

            raise RuntimeError(f"Characteristic {char_uuid} not found")

        await asyncio.get_event_loop().run_in_executor(self.executor, _start_notify)

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        """Stop notifications for a characteristic.

        Args:
            char_uuid: UUID of the characteristic to unsubscribe from

        """

        def _stop_notify() -> None:
            p = self.peripheral
            assert p is not None

            # Find the characteristic's service and UUID
            for service in p.services():
                for char in service.characteristics():
                    if char.uuid().upper() == str(char_uuid).upper():
                        p.unsubscribe(service.uuid(), char.uuid())
                        return

            raise RuntimeError(f"Characteristic {char_uuid} not found")

        await asyncio.get_event_loop().run_in_executor(self.executor, _stop_notify)

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.peripheral is not None and self.peripheral.is_connected()

    @property
    def name(self) -> str:
        """Get the device name.

        Returns:
            Device name

        """
        if self.peripheral is not None:
            return str(self.peripheral.identifier())
        return "Unknown"

    @property
    def address(self) -> str:
        """Get the device address.

        Returns:
            Bluetooth MAC address

        """
        if self.peripheral is not None:
            addr = self.peripheral.address()
            return str(addr) if addr else self._address
        return super().address  # Fallback to address from parent class

    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        """Read a GATT descriptor.

        Args:
            desc_uuid: UUID of the descriptor to read

        Returns:
            Raw descriptor data as bytes

        Raises:
            RuntimeError: If descriptor not found or peripheral not connected

        """

        def _read() -> bytes:
            p = self.peripheral
            assert p is not None
            # SimplePyBLE requires service_uuid, char_uuid, desc_uuid
            # We need to find which service/char contains this descriptor
            for service in p.services():
                for char in service.characteristics():
                    for desc in char.descriptors():
                        if desc.uuid().upper() == str(desc_uuid).upper():
                            return p.descriptor_read(service.uuid(), char.uuid(), desc.uuid())  # type: ignore[call-arg, no-any-return]
            raise RuntimeError(f"Descriptor {desc_uuid} not found")

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read)

    async def write_gatt_descriptor(self, desc_uuid: BluetoothUUID, data: bytes) -> None:
        """Write to a GATT descriptor.

        Args:
            desc_uuid: UUID of the descriptor to write to
            data: Data to write

        Raises:
            RuntimeError: If descriptor not found or peripheral not connected

        """

        def _write() -> None:
            p = self.peripheral
            assert p is not None
            # SimplePyBLE requires service_uuid, char_uuid, desc_uuid
            # We need to find which service/char contains this descriptor
            for service in p.services():
                for char in service.characteristics():
                    for desc in char.descriptors():
                        if desc.uuid().upper() == str(desc_uuid).upper():
                            p.descriptor_write(service.uuid(), char.uuid(), desc.uuid(), data)  # type: ignore[call-arg]
                            return
            raise RuntimeError(f"Descriptor {desc_uuid} not found")

        await asyncio.get_event_loop().run_in_executor(self.executor, _write)

    async def pair(self) -> None:
        """Pair with the device.

        Raises:
            NotImplementedError: SimplePyBLE doesn't have explicit pairing API

        """
        raise NotImplementedError("Pairing not supported in SimplePyBLE connection manager")

    async def unpair(self) -> None:
        """Unpair from the device.

        Uses SimplePyBLE's unpair() method to remove pairing with the peripheral.

        """

        def _unpair() -> None:
            p = self.peripheral
            assert p is not None
            p.unpair()

        await asyncio.get_event_loop().run_in_executor(self.executor, _unpair)

    async def read_rssi(self) -> int:
        """Read the RSSI (signal strength) of the connection.

        Returns:
            RSSI value in dBm (typically negative, e.g., -50)

        Raises:
            RuntimeError: If peripheral not connected

        """

        def _read_rssi() -> int:
            p = self.peripheral
            assert p is not None
            return p.rssi()  # type: ignore[no-any-return]

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read_rssi)

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to be called when the device disconnects.

        Args:
            callback: Function to call when device disconnects

        """
        self._user_callback = callback
        # If already connected, update the callback on the peripheral
        if self.peripheral is not None and self.is_connected:
            self.peripheral.set_callback_on_disconnected(self._user_callback)

    @property
    def mtu_size(self) -> int:
        """Get the current MTU (Maximum Transmission Unit) size.

        Returns:
            MTU size in bytes (typically 23-512)

        Raises:
            RuntimeError: If peripheral not connected

        """
        p = self.peripheral
        assert p is not None
        return p.mtu()  # type: ignore[no-any-return]
