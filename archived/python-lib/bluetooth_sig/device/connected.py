"""Connection-related functionality for Device.

Manages GATT connection operations for a BLE device using
the composition pattern. This class is accessed via `device.connected`.

Based on patterns from bleak (BLEDevice + BleakClient) and real-world
implementations.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import msgspec

from bluetooth_sig.device.client import ClientManagerProtocol
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.services.base import BaseGattService
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


class DeviceEncryption(msgspec.Struct, kw_only=True, frozen=False):
    """Encryption state for connected device.

    Attributes:
        paired: Whether the device is paired.
        bonded: Whether the device is bonded (persistent pairing).
        encrypted: Whether the current connection is encrypted.

    """

    paired: bool = False
    bonded: bool = False
    encrypted: bool = False


class DeviceService(msgspec.Struct, kw_only=True, frozen=False):
    """Wrapper for a discovered GATT service.

    Attributes:
        uuid: Service UUID.
        service_class: The GATT service class, or None if unknown.
        characteristics: Discovered characteristics by UUID string.

    """

    uuid: BluetoothUUID
    service_class: type[BaseGattService] | None = None
    characteristics: dict[str, BaseCharacteristic[Any]] = msgspec.field(default_factory=dict)


class DeviceConnected:
    """Manages GATT connection operations for a device.

    Accessed via `device.connected`.

    Attributes:
        services: Discovered GATT services by UUID string.
        encryption: Current encryption state.

    Example::
        device = Device(mac_address="AA:BB:CC:DD:EE:FF", translator=translator)

        # Connect and discover services
        await device.connected.connect()
        services = await device.connected.discover_services()

        # Read a characteristic
        battery = await device.connected.read(BluetoothUUID("00002a19-0000-1000-8000-00805f9b34fb"))


        # Subscribe to notifications
        async def on_heart_rate(value):
            print(f"Heart rate: {value}")


        await device.connected.subscribe(
            BluetoothUUID("00002a37-0000-1000-8000-00805f9b34fb"),
            on_heart_rate,
        )

        await device.connected.disconnect()

    """

    def __init__(
        self,
        mac_address: str,
        connection_manager: ClientManagerProtocol | None = None,
    ) -> None:
        """Initialise connection subsystem.

        Args:
            mac_address: Device MAC address.
            connection_manager: Optional connection manager (can be set later).

        """
        self._mac_address = mac_address
        self._connection_manager = connection_manager
        self.services: dict[str, DeviceService] = {}
        self.encryption = DeviceEncryption()
        self._is_connected = False
        self._subscriptions: dict[str, list[Callable[[Any], None]]] = {}

    @property
    def mac_address(self) -> str:
        """Device MAC address."""
        return self._mac_address

    @property
    def connection_manager(self) -> ClientManagerProtocol | None:
        """Current connection manager."""
        return self._connection_manager

    @connection_manager.setter
    def connection_manager(self, value: ClientManagerProtocol | None) -> None:
        """Set connection manager."""
        self._connection_manager = value

    @property
    def is_connected(self) -> bool:
        """Whether currently connected."""
        return self._is_connected

    async def connect(self, *, timeout: float = 10.0) -> None:
        """Establish GATT connection.

        Args:
            timeout: Connection timeout in seconds.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        await self._connection_manager.connect(timeout=timeout)
        self._is_connected = True

    async def disconnect(self) -> None:
        """Disconnect from device.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        await self._connection_manager.disconnect()
        self._is_connected = False
        self._subscriptions.clear()

    async def discover_services(self) -> list[DeviceService]:
        """Discover and cache GATT services.

        Returns:
            List of discovered services.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        # Get raw services from connection manager
        raw_services = await self._connection_manager.get_services()

        self.services.clear()
        for raw_svc in raw_services:
            uuid_str = str(raw_svc.service.uuid)
            service_class = GattServiceRegistry.get_service_class_by_uuid(raw_svc.service.uuid)

            device_service = DeviceService(
                uuid=raw_svc.service.uuid,
                service_class=service_class,
            )

            # Discover characteristics for this service
            for char_uuid_str, char_instance in raw_svc.characteristics.items():
                device_service.characteristics[char_uuid_str] = char_instance

            self.services[uuid_str] = device_service

        return list(self.services.values())

    async def read(self, characteristic_uuid: BluetoothUUID | str) -> Any:  # noqa: ANN401
        """Read a characteristic value.

        Args:
            characteristic_uuid: UUID of the characteristic to read.

        Returns:
            Parsed characteristic value.

        Raises:
            RuntimeError: If no connection manager is set.
            ValueError: If characteristic is unknown.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        if isinstance(characteristic_uuid, str):
            characteristic_uuid = BluetoothUUID(characteristic_uuid)

        raw_data = await self._connection_manager.read_gatt_char(characteristic_uuid)

        # Try to parse with registered characteristic class
        char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(characteristic_uuid)
        if char_class is not None:
            char_instance = char_class()
            return char_instance.parse_value(raw_data)

        # Return raw bytes if no parser available
        return raw_data

    async def write(
        self,
        characteristic_uuid: BluetoothUUID | str,
        value: Any,  # noqa: ANN401
        *,
        response: bool = True,
    ) -> None:
        """Write a value to a characteristic.

        Args:
            characteristic_uuid: UUID of the characteristic to write.
            value: Value to write (will be encoded if characteristic is known).
            response: Whether to wait for write response.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        if isinstance(characteristic_uuid, str):
            characteristic_uuid = BluetoothUUID(characteristic_uuid)

        # Try to encode with registered characteristic class
        data: bytes | bytearray
        char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(characteristic_uuid)
        if char_class is not None and hasattr(char_class, "build_value"):
            char_instance = char_class()
            data = char_instance.build_value(value)
        elif isinstance(value, (bytes, bytearray)):
            data = value
        else:
            raise ValueError(f"Cannot write value of type {type(value).__name__} to unknown characteristic")

        await self._connection_manager.write_gatt_char(
            characteristic_uuid,
            bytes(data),
            response=response,
        )

    async def subscribe(
        self,
        characteristic_uuid: BluetoothUUID | str,
        callback: Callable[[Any], None],
    ) -> None:
        """Subscribe to characteristic notifications.

        Args:
            characteristic_uuid: UUID of the characteristic to subscribe to.
            callback: Function called with parsed value on each notification.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        if isinstance(characteristic_uuid, str):
            characteristic_uuid = BluetoothUUID(characteristic_uuid)

        uuid_str = str(characteristic_uuid)

        # Get characteristic class for parsing
        char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(characteristic_uuid)

        def notification_handler(_sender: str, data: bytes) -> None:
            """Parse notification data and dispatch to callbacks."""
            parsed_value: Any
            if char_class is not None:
                char_instance = char_class()
                parsed_value = char_instance.parse_value(data)
            else:
                parsed_value = data

            for cb in self._subscriptions.get(uuid_str, []):
                cb(parsed_value)

        # Start notifications via connection manager
        await self._connection_manager.start_notify(characteristic_uuid, notification_handler)

        # Track subscription
        if uuid_str not in self._subscriptions:
            self._subscriptions[uuid_str] = []
        self._subscriptions[uuid_str].append(callback)

    async def unsubscribe(self, characteristic_uuid: BluetoothUUID | str) -> None:
        """Unsubscribe from characteristic notifications.

        Args:
            characteristic_uuid: UUID of the characteristic to unsubscribe from.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        if isinstance(characteristic_uuid, str):
            characteristic_uuid = BluetoothUUID(characteristic_uuid)

        uuid_str = str(characteristic_uuid)

        await self._connection_manager.stop_notify(characteristic_uuid)
        self._subscriptions.pop(uuid_str, None)

    async def read_descriptor(self, descriptor_uuid: BluetoothUUID | str) -> bytes:
        """Read a descriptor value.

        Args:
            descriptor_uuid: UUID of the descriptor to read.

        Returns:
            Raw descriptor bytes.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        if isinstance(descriptor_uuid, str):
            descriptor_uuid = BluetoothUUID(descriptor_uuid)

        return await self._connection_manager.read_gatt_descriptor(descriptor_uuid)

    async def write_descriptor(self, descriptor_uuid: BluetoothUUID | str, data: bytes) -> None:
        """Write data to a descriptor.

        Args:
            descriptor_uuid: UUID of the descriptor to write.
            data: Raw bytes to write.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        if isinstance(descriptor_uuid, str):
            descriptor_uuid = BluetoothUUID(descriptor_uuid)

        await self._connection_manager.write_gatt_descriptor(descriptor_uuid, data)

    async def pair(self) -> None:
        """Pair with the device.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        await self._connection_manager.pair()

    async def unpair(self) -> None:
        """Unpair from the device.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        await self._connection_manager.unpair()

    async def read_rssi(self) -> int:
        """Read the RSSI (signal strength) of the connection.

        Returns:
            RSSI value in dBm.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        return await self._connection_manager.read_rssi()

    @property
    def mtu_size(self) -> int:
        """Get the MTU size of the connection.

        Returns:
            MTU size in bytes.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        return self._connection_manager.mtu_size

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to be invoked when the device disconnects.

        Args:
            callback: Function to call when disconnection occurs.

        Raises:
            RuntimeError: If no connection manager is set.

        """
        if self._connection_manager is None:
            raise RuntimeError("No connection manager set")

        self._connection_manager.set_disconnected_callback(callback)

    def get_cached_characteristic(self, char_uuid: BluetoothUUID) -> BaseCharacteristic[Any] | None:
        """Get cached characteristic instance from services.

        Args:
            char_uuid: UUID of the characteristic to find.

        Returns:
            BaseCharacteristic instance if found, None otherwise.

        """
        char_uuid_str = str(char_uuid)
        for service in self.services.values():
            if char_uuid_str in service.characteristics:
                return service.characteristics[char_uuid_str]
        return None

    def cache_characteristic(self, char_uuid: BluetoothUUID, char_instance: BaseCharacteristic[Any]) -> None:
        """Store characteristic instance in services cache.

        Args:
            char_uuid: UUID of the characteristic.
            char_instance: BaseCharacteristic instance to cache.

        """
        char_uuid_str = str(char_uuid)
        for service in self.services.values():
            if char_uuid_str in service.characteristics:
                service.characteristics[char_uuid_str] = char_instance
                return
        logger.warning(
            "Cannot cache characteristic %s - not found in any discovered service. Run discover_services() first.",
            char_uuid_str,
        )
