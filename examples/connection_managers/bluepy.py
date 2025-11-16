"""BluePy-based connection manager for BLE devices.

This module provides a connection manager implementation using BluePy,
following the same pattern as Bleak and SimplePyBLE managers.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from bluepy.btle import ADDR_TYPE_RANDOM, UUID, BTLEException, Characteristic, Peripheral, Service

from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.unknown import UnknownCharacteristic
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.types.data_types import CharacteristicInfo
from bluetooth_sig.types.device_types import DeviceService
from bluetooth_sig.types.gatt_enums import GattProperty
from bluetooth_sig.types.uuid import BluetoothUUID


# pylint: disable=too-many-public-methods  # Implements ConnectionManagerProtocol interface
class BluePyConnectionManager(ConnectionManagerProtocol):
    """Connection manager using BluePy for BLE communication.

    Implements ConnectionManagerProtocol to integrate BluePy with
    the bluetooth-sig-python Device class.
    """

    def __init__(self, address: str, addr_type: str = ADDR_TYPE_RANDOM, timeout: float = 20.0) -> None:
        """Initialize the connection manager.

        Args:
            address: BLE MAC address
            addr_type: Address type (ADDR_TYPE_RANDOM or ADDR_TYPE_PUBLIC)
            timeout: Connection timeout in seconds

        """
        super().__init__(address)
        self.addr_type = addr_type
        self.timeout = timeout
        self.periph: Peripheral | None = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._cached_services: list[DeviceService] | None = None

    @staticmethod
    def to_bluepy_uuid(uuid: BluetoothUUID) -> UUID:
        """Convert BluetoothUUID to BluePy UUID.

        Args:
            uuid: BluetoothUUID instance

        Returns:
            Corresponding BluePy UUID instance
        """
        return UUID(str(uuid))

    @staticmethod
    def to_bluetooth_uuid(uuid: UUID) -> BluetoothUUID:
        """Convert BluePy UUID to BluetoothUUID.

        Args:
            uuid: BluePy UUID instance

        Returns:
            Corresponding BluetoothUUID instance
        """
        return BluetoothUUID(str(uuid))

    async def connect(self) -> None:
        """Connect to device."""

        def _connect() -> None:
            try:
                self.periph = Peripheral(self.address, addrType=self.addr_type)
                self._cached_services = None  # Clear cache on new connection
            except BTLEException as e:
                if "Failed to connect to peripheral" in str(e):
                    # First attempt failed, try with public address type
                    try:
                        self.periph = Peripheral(self.address, addrType="public")
                        self._cached_services = None  # Clear cache on new connection
                    except BTLEException as e2:
                        raise RuntimeError(
                            f"Failed to connect to {self.address} with both random and public address types: {e2}"
                        ) from e2
                else:
                    raise RuntimeError(f"Failed to connect to {self.address}: {e}") from e

        await asyncio.get_event_loop().run_in_executor(self.executor, _connect)

    async def disconnect(self) -> None:
        """Disconnect from device."""

        def _disconnect() -> None:
            if self.periph:
                self.periph.disconnect()
                self.periph = None
                self._cached_services = None  # Clear cache on disconnect

        await asyncio.get_event_loop().run_in_executor(self.executor, _disconnect)

    @property
    def is_connected(self) -> bool:
        """Check if connected.

        Returns:
            True if connected
        """
        return self.periph is not None

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read GATT characteristic.

        Args:
            char_uuid: Characteristic UUID

        Returns:
            Raw characteristic bytes

        Raises:
            RuntimeError: If not connected or read fails
        """

        def _read() -> bytes:
            if not self.periph:
                raise RuntimeError("Not connected")

            try:
                characteristics: list[Characteristic] = self.periph.getCharacteristics(
                    uuid=self.to_bluepy_uuid(char_uuid)
                )  # type: ignore[misc]
                if not characteristics:
                    raise RuntimeError(f"Characteristic {char_uuid} not found")

                # First (and typically only) characteristic with this UUID
                char: Characteristic = characteristics[0]
                return char.read()  # type: ignore[no-any-return]
            except BTLEException as e:
                raise RuntimeError(f"BluePy error reading characteristic {char_uuid}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Failed to read characteristic {char_uuid}: {e}") from e

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read)

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
        """Write GATT characteristic.

        Args:
            char_uuid: Characteristic UUID
            data: Data to write
            response: If True, use write-with-response; if False, use write-without-response

        Raises:
            RuntimeError: If not connected or write fails
        """

        def _write() -> None:
            if not self.periph:
                raise RuntimeError("Not connected")

            try:
                characteristics: list[Characteristic] = self.periph.getCharacteristics(
                    uuid=self.to_bluepy_uuid(char_uuid)
                )  # type: ignore[misc]
                if not characteristics:
                    raise RuntimeError(f"Characteristic {char_uuid} not found")

                # First (and typically only) characteristic with this UUID
                char: Characteristic = characteristics[0]
                _ = char.write(data, withResponse=response)  # type: ignore[misc]
                # BluePy write returns a response dict - we don't need to check it specifically
                # as BluePy will raise an exception if the write fails
            except BTLEException as e:
                raise RuntimeError(f"BluePy error writing characteristic {char_uuid}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Failed to write characteristic {char_uuid}: {e}") from e

        await asyncio.get_event_loop().run_in_executor(self.executor, _write)

    async def get_services(self) -> list[DeviceService]:
        """Get services from device.

        Services are cached after first retrieval. BluePy's getServices() performs
        service discovery each call, so caching is important for efficiency.

        Returns:
            List of DeviceService objects converted from BluePy services
        """
        # Return cached services if available
        if self._cached_services is not None:
            return self._cached_services

        def _get_services() -> list[DeviceService]:
            if not self.periph:
                raise RuntimeError("Not connected")

            # BluePy's getServices() performs discovery - cache the result
            bluepy_services: list[Service] = list(self.periph.getServices())  # type: ignore[misc]

            device_services: list[DeviceService] = []
            for bluepy_service in bluepy_services:
                service_uuid = self.to_bluetooth_uuid(bluepy_service.uuid)
                service_class = GattServiceRegistry.get_service_class(service_uuid)

                if service_class:
                    service_instance = service_class()

                    # Populate characteristics with actual class instances
                    characteristics: dict[str, BaseCharacteristic] = {}
                    for char in bluepy_service.getCharacteristics():  # type: ignore[misc]
                        char_uuid = self.to_bluetooth_uuid(char.uuid)

                        # Extract properties from BluePy characteristic
                        properties: list[GattProperty] = []
                        if hasattr(char, "properties") and char.properties:
                            # BluePy stores properties as an integer bitmask
                            prop_flags = char.properties
                            # Bit flags from Bluetooth spec
                            if prop_flags & 0x02:  # Read
                                properties.append(GattProperty.READ)
                            if prop_flags & 0x04:  # Write without response
                                properties.append(GattProperty.WRITE_WITHOUT_RESPONSE)
                            if prop_flags & 0x08:  # Write
                                properties.append(GattProperty.WRITE)
                            if prop_flags & 0x10:  # Notify
                                properties.append(GattProperty.NOTIFY)
                            if prop_flags & 0x20:  # Indicate
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
                    device_services.append(DeviceService(service=service_instance, characteristics=characteristics))  # type: ignore[arg-type]

            return device_services

        result = await asyncio.get_event_loop().run_in_executor(self.executor, _get_services)

        # Cache the result
        self._cached_services = result
        return result

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        """Start notifications (not implemented for this example).

        Args:
            char_uuid: Characteristic UUID
            callback: Notification callback
        """
        raise NotImplementedError("Notifications not implemented in this example")

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        """Stop notifications (not implemented for this example).

        Args:
            char_uuid: Characteristic UUID
        """
        raise NotImplementedError("Notifications not implemented in this example")

    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        """Read GATT descriptor.

        Args:
            desc_uuid: Descriptor UUID

        Returns:
            Raw descriptor bytes

        Raises:
            RuntimeError: If not connected or read fails
        """

        def _read_descriptor() -> bytes:
            if not self.periph:
                raise RuntimeError("Not connected")

            try:
                descriptors = self.periph.getDescriptors()  # type: ignore[misc]
                for desc in descriptors:
                    if str(desc.uuid).lower() == str(desc_uuid).lower():
                        return desc.read()  # type: ignore[no-any-return]
                raise RuntimeError(f"Descriptor {desc_uuid} not found")
            except BTLEException as e:
                raise RuntimeError(f"BluePy error reading descriptor {desc_uuid}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Failed to read descriptor {desc_uuid}: {e}") from e

        return await asyncio.get_event_loop().run_in_executor(self.executor, _read_descriptor)

    async def write_gatt_descriptor(self, desc_uuid: BluetoothUUID, data: bytes) -> None:
        """Write GATT descriptor.

        Args:
            desc_uuid: Descriptor UUID
            data: Data to write

        Raises:
            RuntimeError: If not connected or write fails
        """

        def _write_descriptor() -> None:
            if not self.periph:
                raise RuntimeError("Not connected")

            try:
                descriptors = self.periph.getDescriptors()  # type: ignore[misc]
                for desc in descriptors:
                    if str(desc.uuid).lower() == str(desc_uuid).lower():
                        desc.write(data)  # type: ignore[misc]
                        return
                raise RuntimeError(f"Descriptor {desc_uuid} not found")
            except BTLEException as e:
                raise RuntimeError(f"BluePy error writing descriptor {desc_uuid}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Failed to write descriptor {desc_uuid}: {e}") from e

        await asyncio.get_event_loop().run_in_executor(self.executor, _write_descriptor)

    async def pair(self) -> None:
        """Pair with the device.

        Raises:
            NotImplementedError: BluePy doesn't have explicit pairing API

        """
        raise NotImplementedError("Pairing not supported in BluePy connection manager")

    async def unpair(self) -> None:
        """Unpair from the device.

        Raises:
            NotImplementedError: BluePy doesn't have explicit unpairing API

        """
        raise NotImplementedError("Unpairing not supported in BluePy connection manager")

    async def read_rssi(self) -> int:
        """Read the RSSI (signal strength) of the connection.

        Returns:
            RSSI value in dBm (typically negative, e.g., -50)

        Raises:
            NotImplementedError: BluePy doesn't support reading RSSI from connected devices

        Note:
            BluePy only provides RSSI values during scanning (from advertising packets).
            Once connected, there's no API to read RSSI from an active connection.
            See: https://github.com/IanHarvey/bluepy/issues/394

        """
        raise NotImplementedError("RSSI reading from connected devices not supported in BluePy")

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to be called when the device disconnects.

        Args:
            callback: Function to call when device disconnects

        Raises:
            NotImplementedError: BluePy doesn't provide disconnection callbacks
        """
        raise NotImplementedError("Disconnection callbacks not supported in BluePy connection manager")

    @property
    def mtu_size(self) -> int:
        """Get the current MTU (Maximum Transmission Unit) size.

        Returns:
            MTU size in bytes (typically 23-512)

        Raises:
            NotImplementedError: BluePy doesn't expose MTU information
        """
        raise NotImplementedError("MTU size not supported in BluePy connection manager")

    @property
    def address(self) -> str:
        """Get the device's Bluetooth address.

        Returns:
            Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        """
        if self.periph:
            return self.periph.addr  # type: ignore[no-any-return]
        return self._address  # Fall back to stored address if not connected

    @property
    def name(self) -> str:
        """Get the device name.

        Returns:
            Device name or "Unknown" if not available

        Note:
            BluePy doesn't provide a direct name property. Reading the GAP
            Device Name characteristic (0x2A00) would require service discovery.
            This returns "Unknown" for simplicity.

        """
        return "Unknown"
