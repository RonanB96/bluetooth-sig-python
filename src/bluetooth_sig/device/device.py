"""Device class for grouping BLE device services, characteristics, encryption, and advertiser data.

Provides a high-level Device abstraction that groups all services,
characteristics, encryption requirements, and advertiser data for a BLE
device.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, overload

from ..advertising.registry import PayloadInterpreterRegistry
from ..gatt.characteristics import CharacteristicName
from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.context import DeviceInfo
from ..gatt.descriptors.base import BaseDescriptor
from ..gatt.descriptors.registry import DescriptorRegistry
from ..gatt.services import ServiceName
from ..types import (
    DescriptorData,
    DescriptorInfo,
)
from ..types.advertising.result import AdvertisementData
from ..types.device_types import ScannedDevice
from ..types.uuid import BluetoothUUID
from .advertising import DeviceAdvertising
from .characteristic_io import CharacteristicIO
from .client import ClientManagerProtocol
from .connected import DeviceConnected, DeviceEncryption, DeviceService
from .dependency_resolver import DependencyResolutionMode, DependencyResolver
from .protocols import SIGTranslatorProtocol

# Type variable for generic characteristic return types
T = TypeVar("T")

__all__ = [
    "DependencyResolutionMode",
    "Device",
    "DeviceAdvertising",
    "DeviceConnected",
    "SIGTranslatorProtocol",
]


class Device:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    r"""High-level BLE device abstraction using composition pattern.

    Coordinates between connected GATT operations and advertising packet
    interpretation through two subsystems:

    - ``device.connected`` — GATT connection, services, characteristics
    - ``device.advertising`` — Vendor-specific advertising interpretation

    Convenience methods delegate to the appropriate subsystem, so callers
    can use ``await device.read("battery_level")`` without knowing which
    subsystem handles it.
    """

    def __init__(self, connection_manager: ClientManagerProtocol, translator: SIGTranslatorProtocol) -> None:
        """Initialise Device instance with connection manager and translator.

        Args:
            connection_manager: Connection manager implementing ClientManagerProtocol
            translator: SIGTranslatorProtocol instance

        """
        self.connection_manager = connection_manager
        self.translator = translator
        self._name: str = ""

        # Connected subsystem (composition pattern)
        self.connected = DeviceConnected(
            mac_address=self.address,
            connection_manager=connection_manager,
        )

        # Advertising subsystem (composition pattern)
        self.advertising = DeviceAdvertising(self.address, connection_manager)
        # Set up registry for auto-detection
        self.advertising.set_registry(PayloadInterpreterRegistry())

        # Dependency resolution delegate
        self._dep_resolver = DependencyResolver(connection_manager, self.connected)

        # Characteristic I/O delegate
        self._char_io = CharacteristicIO(connection_manager, translator, self._dep_resolver, lambda: self.device_info)

        # Cache for device_info property and last advertisement
        self._device_info_cache: DeviceInfo | None = None
        self._last_advertisement: AdvertisementData | None = None

    def __str__(self) -> str:
        """Return string representation of Device.

        Returns:
            str: String representation of Device.

        """
        service_count = len(self.connected.services)
        char_count = sum(len(service.characteristics) for service in self.connected.services.values())
        return f"Device({self.address}, name={self.name}, {service_count} services, {char_count} characteristics)"

    @property
    def services(self) -> dict[str, DeviceService]:
        """GATT services discovered on device.

        Delegates to device.connected.services.

        Returns:
            Dictionary of service UUID → DeviceService

        """
        return self.connected.services

    @property
    def encryption(self) -> DeviceEncryption:
        """Encryption state for connected device.

        Delegates to device.connected.encryption.

        Returns:
            DeviceEncryption instance

        """
        return self.connected.encryption

    @property
    def address(self) -> str:
        """Get the device address from the connection manager.

        Returns:
            BLE device address

        """
        return self.connection_manager.address

    @staticmethod
    async def scan(manager_class: type[ClientManagerProtocol], timeout: float = 5.0) -> list[ScannedDevice]:
        """Scan for nearby BLE devices using a specific connection manager.

        This is a static method that doesn't require a Device instance.
        Use it to discover devices before creating Device instances.

        Args:
            manager_class: The connection manager class to use for scanning
                          (e.g., BleakRetryClientManager)
            timeout: Scan duration in seconds (default: 5.0)

        Returns:
            List of discovered devices

        Raises:
            NotImplementedError: If the connection manager doesn't support scanning

        Example::

            from bluetooth_sig.device import Device
            from connection_managers.bleak_retry import BleakRetryClientManager

            # Scan for devices
            devices = await Device.scan(BleakRetryClientManager, timeout=10.0)

            # Create Device instance for first discovered device
            if devices:
                translator = BluetoothSIGTranslator()
                device = Device(devices[0].address, translator)

        """
        return await manager_class.scan(timeout)

    async def connect(self) -> None:
        """Connect to the BLE device.

        Convenience method that delegates to device.connected.connect().

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self.connected.connect()

    async def disconnect(self) -> None:
        """Disconnect from the BLE device.

        Convenience method that delegates to device.connected.disconnect().

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self.connected.disconnect()

    # ------------------------------------------------------------------
    # Characteristic I/O (delegated to CharacteristicIO)
    # ------------------------------------------------------------------

    @overload
    async def read(
        self,
        char: type[BaseCharacteristic[T]],
        resolution_mode: DependencyResolutionMode = ...,
    ) -> T | None: ...

    @overload
    async def read(
        self,
        char: str | CharacteristicName,
        resolution_mode: DependencyResolutionMode = ...,
    ) -> Any | None: ...  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe

    async def read(
        self,
        char: str | CharacteristicName | type[BaseCharacteristic[T]],
        resolution_mode: DependencyResolutionMode = DependencyResolutionMode.NORMAL,
    ) -> T | Any | None:  # Runtime UUID dispatch cannot be type-safe
        """Read a characteristic value from the device.

        Delegates to :class:`CharacteristicIO`.

        Args:
            char: Name, enum, or characteristic class to read.
            resolution_mode: How to handle automatic dependency resolution.

        Returns:
            Parsed characteristic value or None if read fails.

        Raises:
            RuntimeError: If no connection manager is attached
            ValueError: If required dependencies cannot be resolved

        """
        return await self._char_io.read(char, resolution_mode)

    @overload
    async def write(
        self,
        char: type[BaseCharacteristic[T]],
        data: T,
        response: bool = ...,
    ) -> None: ...

    @overload
    async def write(
        self,
        char: str | CharacteristicName,
        data: bytes,
        response: bool = ...,
    ) -> None: ...

    async def write(
        self,
        char: str | CharacteristicName | type[BaseCharacteristic[T]],
        data: bytes | T,
        response: bool = True,
    ) -> None:
        r"""Write data to a characteristic on the device.

        Delegates to :class:`CharacteristicIO`.

        Args:
            char: Name, enum, or characteristic class to write to.
            data: Raw bytes (for string/enum) or typed value (for characteristic class).
            response: If True, use write-with-response. Default is True.

        Raises:
            RuntimeError: If no connection manager is attached
            CharacteristicEncodeError: If encoding fails (when using characteristic class)

        """
        await self._char_io.write(char, data, response=response)  # type: ignore[arg-type, misc]  # Union narrowing handled by overloads; mypy can't infer across delegation

    @overload
    async def start_notify(
        self,
        char: type[BaseCharacteristic[T]],
        callback: Callable[[T], None],
    ) -> None: ...

    @overload
    async def start_notify(
        self,
        char: str | CharacteristicName,
        callback: Callable[[Any], None],
    ) -> None: ...

    async def start_notify(
        self,
        char: str | CharacteristicName | type[BaseCharacteristic[T]],
        callback: Callable[[T], None] | Callable[[Any], None],
    ) -> None:
        """Start notifications for a characteristic.

        Delegates to :class:`CharacteristicIO`.

        Args:
            char: Name, enum, or characteristic class to monitor.
            callback: Function to call when notifications are received.

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self._char_io.start_notify(char, callback)

    async def stop_notify(self, char_name: str | CharacteristicName) -> None:
        """Stop notifications for a characteristic.

        Delegates to :class:`CharacteristicIO`.

        Args:
            char_name: Characteristic name or UUID

        """
        await self._char_io.stop_notify(char_name)

    async def read_descriptor(self, desc_uuid: BluetoothUUID | BaseDescriptor) -> DescriptorData:
        """Read a descriptor value from the device.

        Args:
            desc_uuid: UUID of the descriptor to read or BaseDescriptor instance

        Returns:
            Parsed descriptor data with metadata

        Raises:
            RuntimeError: If no connection manager is attached

        """
        # Extract UUID from BaseDescriptor if needed
        uuid = desc_uuid.uuid if isinstance(desc_uuid, BaseDescriptor) else desc_uuid

        raw_data = await self.connected.read_descriptor(uuid)

        # Try to create a descriptor instance and parse the data
        descriptor = DescriptorRegistry.create_descriptor(str(uuid))
        if descriptor:
            return descriptor.parse_value(raw_data)

        # If no registered descriptor found, return unparsed DescriptorData
        return DescriptorData(
            info=DescriptorInfo(uuid=uuid, name="Unknown Descriptor"),
            value=raw_data,
            raw_data=raw_data,
            parse_success=False,
            error_message="Unknown descriptor UUID - no parser available",
        )

    async def write_descriptor(self, desc_uuid: BluetoothUUID | BaseDescriptor, data: bytes | DescriptorData) -> None:
        """Write data to a descriptor on the device.

        Args:
            desc_uuid: UUID of the descriptor to write to or BaseDescriptor instance
            data: Either raw bytes to write, or a DescriptorData object.
                 If DescriptorData is provided, its raw_data will be written.

        Raises:
            RuntimeError: If no connection manager is attached

        """
        # Extract UUID from BaseDescriptor if needed
        uuid = desc_uuid.uuid if isinstance(desc_uuid, BaseDescriptor) else desc_uuid

        # Extract raw bytes from DescriptorData if needed
        raw_data: bytes
        raw_data = data.raw_data if isinstance(data, DescriptorData) else data

        await self.connected.write_descriptor(uuid, raw_data)

    async def pair(self) -> None:
        """Pair with the device.

        Convenience method that delegates to device.connected.pair().

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self.connected.pair()

    async def unpair(self) -> None:
        """Unpair from the device.

        Convenience method that delegates to device.connected.unpair().

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self.connected.unpair()

    async def read_rssi(self) -> int:
        """Read the RSSI (signal strength) of the connection.

        Convenience method that delegates to device.connected.read_rssi().

        Returns:
            RSSI value in dBm (typically negative, e.g., -60)

        Raises:
            RuntimeError: If no connection manager is attached

        """
        return await self.connected.read_rssi()

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to be invoked when the device disconnects.

        Convenience method that delegates to device.connected.set_disconnected_callback().

        Args:
            callback: Function to call when disconnection occurs

        Raises:
            RuntimeError: If no connection manager is attached

        """
        self.connected.set_disconnected_callback(callback)

    @property
    def mtu_size(self) -> int:
        """Get the negotiated MTU size in bytes.

        Delegates to device.connected.mtu_size.

        Returns:
            The MTU size negotiated for this connection (typically 23-512 bytes)

        Raises:
            RuntimeError: If no connection manager is attached

        """
        return self.connected.mtu_size

    async def refresh_advertisement(self, refresh: bool = False) -> AdvertisementData | None:
        """Get advertisement data from the connection manager.

        Args:
            refresh: If ``True``, perform an active scan for fresh data.

        Returns:
            Interpreted :class:`AdvertisementData`, or ``None`` if unavailable.

        Raises:
            RuntimeError: If no connection manager is attached.

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        advertisement = await self.connection_manager.get_latest_advertisement(refresh=refresh)
        if advertisement is None:
            return None

        # Process and cache the advertisement
        processed_ad, _result = self.advertising.process_from_connection_manager(advertisement)
        self._last_advertisement = processed_ad

        # Update device name if not set
        if advertisement.ad_structures.core.local_name and not self.name:
            self.name = advertisement.ad_structures.core.local_name

        return processed_ad

    def parse_raw_advertisement(self, raw_data: bytes, rssi: int = 0) -> AdvertisementData:
        """Parse raw advertising PDU bytes directly.

        Args:
            raw_data: Raw BLE advertising PDU bytes.
            rssi: Received signal strength in dBm.

        Returns:
            AdvertisementData with parsed AD structures and vendor interpretation.

        """
        # Delegate to advertising subsystem
        advertisement, _result = self.advertising.parse_raw_pdu(raw_data, rssi)
        self._last_advertisement = advertisement

        # Update device name if present and not already set
        if advertisement.ad_structures.core.local_name and not self.name:
            self.name = advertisement.ad_structures.core.local_name

        return advertisement

    def get_characteristic_data(self, char_uuid: BluetoothUUID) -> Any | None:  # noqa: ANN401  # Heterogeneous cache
        """Get parsed characteristic data via ``characteristic.last_parsed``.

        Args:
            char_uuid: UUID of the characteristic.

        Returns:
            Parsed characteristic value if found, ``None`` otherwise.

        """
        char_instance = self.connected.get_cached_characteristic(char_uuid)
        if char_instance is not None:
            return char_instance.last_parsed
        return None

    async def discover_services(self) -> dict[str, Any]:
        """Discover services and characteristics from the connected BLE device.

        Performs BLE service discovery via the connection manager.  The
        discovered :class:`DeviceService` objects (with characteristic
        instances and runtime properties) are stored in ``self.services``.

        Returns:
            Dictionary mapping service UUIDs to DeviceService objects.

        Raises:
            RuntimeError: If no connection manager is attached.

        """
        # Delegate to connected subsystem
        services_list = await self.connected.discover_services()

        # Invalidate device_info cache since services changed
        self._device_info_cache = None

        # Return as dict for backward compatibility
        return {str(svc.uuid): svc for svc in services_list}

    async def get_characteristic_info(self, char_uuid: str) -> Any | None:  # noqa: ANN401  # Adapter-specific characteristic metadata
        """Get information about a characteristic from the connection manager.

        Args:
            char_uuid: UUID of the characteristic

        Returns:
            Characteristic information or None if not found

        Raises:
            RuntimeError: If no connection manager is attached

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        services_data = await self.connection_manager.get_services()
        for service_info in services_data:
            for char_uuid_key, char_info in service_info.characteristics.items():
                if char_uuid_key == char_uuid:
                    return char_info
        return None

    async def read_multiple(self, char_names: list[str | CharacteristicName]) -> dict[str, Any | None]:
        """Read multiple characteristics in batch.

        Delegates to :class:`CharacteristicIO`.

        Args:
            char_names: List of characteristic names or enums to read

        Returns:
            Dictionary mapping characteristic UUIDs to parsed values

        """
        return await self._char_io.read_multiple(char_names)

    async def write_multiple(
        self, data_map: dict[str | CharacteristicName, bytes], response: bool = True
    ) -> dict[str, bool]:
        """Write to multiple characteristics in batch.

        Delegates to :class:`CharacteristicIO`.

        Args:
            data_map: Dictionary mapping characteristic names/enums to data bytes
            response: If True, use write-with-response for all writes.

        Returns:
            Dictionary mapping characteristic UUIDs to success status

        """
        return await self._char_io.write_multiple(data_map, response=response)

    @property
    def device_info(self) -> DeviceInfo:
        """Get cached device info object.

        Returns:
            DeviceInfo with current device metadata

        """
        if self._device_info_cache is None:
            self._device_info_cache = DeviceInfo(
                address=self.address,
                name=self.name,
                manufacturer_data=self._last_advertisement.ad_structures.core.manufacturer_data
                if self._last_advertisement
                else {},
                service_uuids=self._last_advertisement.ad_structures.core.service_uuids
                if self._last_advertisement
                else [],
            )
        else:
            # Update existing cache object with current data
            self._device_info_cache.name = self.name
            if self._last_advertisement:
                self._device_info_cache.manufacturer_data = (
                    self._last_advertisement.ad_structures.core.manufacturer_data
                )
                self._device_info_cache.service_uuids = self._last_advertisement.ad_structures.core.service_uuids
        return self._device_info_cache

    @property
    def name(self) -> str:
        """Get the device name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the device name and update cached device_info."""
        self._name = value
        # Update existing cache object if it exists
        if self._device_info_cache is not None:
            self._device_info_cache.name = value

    @property
    def is_connected(self) -> bool:
        """Check if the device is currently connected.

        Delegates to device.connected.is_connected.

        Returns:
            True if connected, False otherwise

        """
        return self.connected.is_connected

    @property
    def last_advertisement(self) -> AdvertisementData | None:
        """Get the last received advertisement data.

        This is automatically updated when advertisements are processed via
        refresh_advertisement() or parse_raw_advertisement().

        Returns:
            AdvertisementData with AD structures and interpreted_data if available,
            None if no advertisement has been received yet.

        """
        return self._last_advertisement

    def get_service_by_uuid(self, service_uuid: str) -> DeviceService | None:
        """Get a service by its UUID.

        Args:
            service_uuid: UUID of the service

        Returns:
            DeviceService instance or None if not found

        """
        return self.services.get(service_uuid)

    def get_services_by_name(self, service_name: str | ServiceName) -> list[DeviceService]:
        """Get services by name.

        Args:
            service_name: Name or enum of the service

        Returns:
            List of matching DeviceService instances

        """
        service_uuid = self.translator.get_service_uuid_by_name(
            service_name if isinstance(service_name, str) else service_name.value
        )
        if service_uuid and str(service_uuid) in self.services:
            return [self.services[str(service_uuid)]]
        return []

    def list_characteristics(self, service_uuid: str | None = None) -> dict[str, list[str]]:
        """List all characteristics, optionally filtered by service.

        Args:
            service_uuid: Optional service UUID to filter by

        Returns:
            Dictionary mapping service UUIDs to lists of characteristic UUIDs

        """
        if service_uuid:
            service = self.services.get(service_uuid)
            if service:
                return {service_uuid: list(service.characteristics.keys())}
            return {}

        return {svc_uuid: list(service.characteristics.keys()) for svc_uuid, service in self.services.items()}
